import sys  
import json 
from subprocess import Popen  
import mapdriver as md 
import nicfi as md2
import graph_ops as graphlib 
import math 
import numpy as np 
import scipy.misc 
from PIL import Image 
import pickle
import cv2 

from shapely.geometry import Polygon
import geopandas as gpd
import pandas as pd
from fiona.crs import from_epsg

import warnings
warnings.simplefilter('ignore', FutureWarning)

#input cell size (NICFI:4.777314267160000405)
cellsize = 4.777314267160000405

dataset_cfg = []
total_regions = 0 

tid = 0
tn = 1

#prepare for creating polygon
polygondata = gpd.GeoDataFrame()
polygon_merge = gpd.GeoDataFrame()

poly_num = 0

#input
target_date = sys.argv[1]
API_key = sys.argv[2]

for name_cfg in sys.argv[3:]:
	dataset_cfg_ = json.load(open(name_cfg, "r"))

	
	for item in dataset_cfg_:
		dataset_cfg.append(item)
		ilat = item["lat_n"]
		ilon = item["lon_n"]

		total_regions += ilat * ilon 


print("total regions", total_regions)

Popen("mkdir -p tmp", shell=True).wait()

dataset_folder = "amazon_dataset"
folder_nicfi_cache = "nicfi_cache/"
polygon_data = "polygon_data"

Popen("mkdir -p %s" % dataset_folder, shell=True).wait()
Popen("mkdir -p %s" % folder_nicfi_cache, shell=True).wait()

Popen("mkdir -p %s" % polygon_data, shell=True).wait()

# download imagery and osm maps 

c = 0
tiles_needed = 0

for item in dataset_cfg:
	ilat = item["lat_n"]
	ilon = item["lon_n"]
	lat = item["lat"]
	lon = item["lon"]
	print(ilat,ilon,lat,lon)
	for i in range(ilat):
		for j in range(ilon):
			print(c, total_regions)

			if c % tn == tid:
				pass
			else:
				c = c + 1
				continue


			lat = item["lat"]
			lon = item["lon"]
			print(lat,lon)


			lat_st = lat + 2048/111111.0 * cellsize * i 
			lon_st = lon + 2048/111111.0 * cellsize * j / math.cos(math.radians(lat))
			lat_ed = lat + 2048/111111.0 * cellsize * (i+1)
			lon_ed = lon + 2048/111111.0 * cellsize * (j+1) / math.cos(math.radians(lat))


			zoom = 15
			print(lat_st, lon_st, lat_ed, lon_ed)


			# create polygon			
			polygon1 = Polygon([(lon_st,lat_st), (lon_st, lat_ed), (lon_ed, lat_ed), (lon_ed, lat_st)])
			polygondata.loc[0, 'geometry'] = polygon1
			polygondata.crs = from_epsg(4326)
			polygondata['lat_st'] = lat_st
			polygondata['lon_st'] = lon_st
			polygondata['lat_ed'] = lat_ed
			polygondata['lon_ed'] = lon_ed
			polygondata['ID'] = c
			polygon_merge = pd.concat([polygon_merge,polygondata])
			polygon_merge.to_file("polygon_data/polygon.json",driver='GeoJSON')
			
			#the image downloading part 
			img, _ = md2.GetMapInRect(lat_st, lon_st, lat_ed, lon_ed, start_lat = lat_st, start_lon = lon_st, zoom=zoom, folder = folder_nicfi_cache,target_date=target_date,API_key=API_key)
			print(np.shape(img))

			img = img.astype(np.uint8)
			img=cv2.resize(img, dsize=(2048, 2048), interpolation=cv2.INTER_CUBIC)
			Image.fromarray(img).save(dataset_folder+"/region_%d_sat.png" % c)


			# download openstreetmap 
			OSMMap = md.OSMLoader([lat_st,lon_st,lat_ed,lon_ed], False, includeServiceRoad = False)

			node_neighbor = {} # continuous

			for node_id, node_info in OSMMap.nodedict.items():
				lat = node_info["lat"]
				lon = node_info["lon"]

				n1key = (lat,lon)

				neighbors = []

				info_to = node_info["to"].items()
				info_from = node_info["from"].items()

				list_info_to1 = list(info_to)
				list_info_to2 = [r[0] for r in list_info_to1]

				list_info_from1 = list(info_from)
				list_info_from2 = [r[0] for r in list_info_from1]

				for nid in list_info_to2 + list_info_from2 :
					if nid not in neighbors:
						neighbors.append(nid)


				for nid in neighbors:
					n2key = (OSMMap.nodedict[nid]["lat"],OSMMap.nodedict[nid]["lon"])

					node_neighbor = graphlib.graphInsert(node_neighbor, n1key, n2key)

			node_neighbor = graphlib.graphDensify(node_neighbor)
			node_neighbor_region = graphlib.graph2RegionCoordinate(node_neighbor, [lat_st,lon_st,lat_ed,lon_ed])
			prop_graph = dataset_folder+"/region_%d_graph_gt.pickle" % c
			pickle.dump(node_neighbor_region, open(prop_graph, "wb"))

			graphlib.graphVis2048Segmentation(node_neighbor, [lat_st,lon_st,lat_ed,lon_ed], dataset_folder+"/region_%d_" % c + "gt.png")

			node_neighbor_refine, sample_points = graphlib.graphGroundTruthPreProcess(node_neighbor_region)

			refine_graph = dataset_folder+"/region_%d_" % c + "refine_gt_graph.p"
			pickle.dump(node_neighbor_refine, open(refine_graph, "wb"))
			json.dump(sample_points, open(dataset_folder+"/region_%d_" % c + "refine_gt_graph_samplepoints.json", "w"), indent=2)

			c+=1

# create polygon(geojson)
polygon_merge.to_file("polygon_data/polygon.json",driver='GeoJSON')
