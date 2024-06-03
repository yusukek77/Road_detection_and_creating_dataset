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

#input
target_date = sys.argv[1]
number = sys.argv[2]
ID_num = sys.argv[3]
API_key = sys.argv[4]

#start target ID
#YYYYMMNN0000
#e.g. 2022-09 Altamira 03
#202209030000
c = int(number)*1000000 + int(ID_num)

poly_name ="polygon_data/"+ str(c) + "_polygon.json"

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

for name_cfg in sys.argv[5:]:
	dataset_cfg_ = json.load(open(name_cfg, "r"))
	
	for item in dataset_cfg_:
		dataset_cfg.append(item)
		ilat = item["lat_n"]
		ilon = item["lon_n"]

		total_regions += ilat * ilon 
                
print("total regions", total_regions)

Popen("mkdir -p tmp", shell=True).wait()
dataset_folder = "nicfi_dataset"
folder_nicfi_cache = "nicfi_cache"+ str(c) +"/"
polygon_data = "polygon_data"

Popen("mkdir -p %s" % dataset_folder, shell=True).wait()
Popen("mkdir -p %s" % folder_nicfi_cache, shell=True).wait()

Popen("mkdir -p %s" % polygon_data, shell=True).wait()

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
			c = c + 1

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
			polygon_merge.to_file(poly_name,driver='GeoJSON')
			
			# Image downloading part 
			img, _ = md2.GetMapInRect(lat_st, lon_st, lat_ed, lon_ed, start_lat = lat_st, start_lon = lon_st, zoom=zoom, folder = folder_nicfi_cache,target_date=target_date,API_key=API_key)
			print(np.shape(img))

			#output number
			print("C= ",c)

			img = img.astype(np.uint8)
			img=cv2.resize(img, dsize=(2048, 2048), interpolation=cv2.INTER_CUBIC)
			Image.fromarray(img).save(dataset_folder+"/region_%d_sat.png" % c)
