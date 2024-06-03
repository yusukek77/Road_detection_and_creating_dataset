import math 
import numpy as np 
import os 
import scipy.ndimage
from PIL import Image 
from subprocess import Popen 
from time import time, sleep 
import imageio

def lonlat2mapboxTile(lonlat, zoom):
	n = np.exp2(zoom)
	x = int((lonlat[0] + 180)/360*n)
	y = int((1 - math.log(math.tan(lonlat[1] * math.pi / 180) + (1 / math.cos(lonlat[1] * math.pi / 180))) / math.pi) / 2 * n)

	return [x,y]

def lonlat2TilePos(lonlat, zoom):
	n = np.exp2(zoom)
	ix = int((lonlat[0] + 180)/360*n)
	iy = int((1 - math.log(math.tan(lonlat[1] * math.pi / 180) + (1 / math.cos(lonlat[1] * math.pi / 180))) / math.pi) / 2 * n)

	x = ((lonlat[0] + 180)/360*n)
	y = ((1 - math.log(math.tan(lonlat[1] * math.pi / 180) + (1 / math.cos(lonlat[1] * math.pi / 180))) / math.pi) / 2 * n)

	x = int((x - ix) * 256)
	y = int((y - iy) * 256)

	return x,y

def downloadMapBox(zoom, p, outputname,target_date,API_key):
	url = "'https://tiles.planet.com/basemaps/v1/planet-tiles/planet_medres_normalized_analytic_%s_mosaic/gmap/%d/%d/%d.png?api_key=%s&proc=cir'" %(target_date,zoom, p[0], p[1],API_key)
	filename = "%d.png?api_key=%s&proc=cir" %(p[1],API_key)


	Succ = False

	print(outputname)
	retry_timeout = 10

	while Succ != True :
		Popen("timeout 30s wget "+url, shell = True).wait()
		Succ = os.path.isfile(filename) 
		Popen("mv \""+filename+"\" "+outputname, shell=True).wait()
		if Succ != True:
			sleep(retry_timeout)
			retry_timeout += 10
			if retry_timeout > 60:
				retry_timeout = 60

			print("Retry, timeout is ", retry_timeout)

	return Succ



def GetMapInRect(min_lat,min_lon, max_lat, max_lon , folder = "nicfi_cache/", start_lat = 42.1634, start_lon = -71.36, resolution = 1024, padding = 128, zoom = 19, scale = 2,target_date="2022-09",API_key="1"):
	mapbox1 = lonlat2mapboxTile([min_lon, min_lat], zoom)
	mapbox2 = lonlat2mapboxTile([max_lon, max_lat], zoom)

	ok = True

	print(mapbox1, mapbox2)

	print((mapbox2[0] - mapbox1[0])*(mapbox1[1] - mapbox2[1]))

	dimx = (mapbox2[0] - mapbox1[0]+1) * 256 # lon
	dimy = (mapbox1[1] - mapbox2[1]+1) * 256 # lat 

	img = np.zeros((dimy, dimx, 3), dtype = np.uint8)

	for i in range(mapbox2[0] - mapbox1[0]+1):
		if ok == False:
			break 

		for j in range(mapbox1[1] - mapbox2[1]+1):
			filename = folder + "/%d_%d_%d.png" % (zoom, i+mapbox1[0], j+mapbox2[1])
			Succ = os.path.isfile(filename)

			if Succ == True:
				try:
					subimg = imageio.imread(filename).astype(np.uint8)
				except:
					print("image file is damaged, try to redownload it", filename)
					Succ = False

			if Succ == False:
				Succ = downloadMapBox(zoom, [i+mapbox1[0],j+mapbox2[1]], filename,target_date,API_key)

			if Succ:
				subimg = imageio.imread(filename).astype(np.uint8)
				img[j*256:(j+1)*256, i*256:(i+1)*256,:] = subimg[:,:,0:3]


			else:
				ok = False
				break


	x1,y1 = lonlat2TilePos([min_lon, max_lat], zoom)
	x2,y2 = lonlat2TilePos([max_lon, min_lat], zoom)

	x2 = x2 + dimx-256
	y2 = y2 + dimy-256

	img = img[y1:y2,x1:x2]

	return img, ok 
