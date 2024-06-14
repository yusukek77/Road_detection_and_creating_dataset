from shapely.geometry import Polygon
import geopandas as gpd
import pandas as pd
import numpy as np
import sys
import math
import os

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

##########
# config #
##########
#input ID
#"Porto Velho" is 1, "Humaita" is 2, "Altamira" is 3, "Vista Alegre do Abuna" is 4, "Novo Progresso" is 5, 
#"Sao_Felix_do_Xingu" is 6, "S6W57" is 7,and "S7W57" is 8. If adding other area, please put the number in order from 9.
ID = 1

#Input latitude of north and south, and longitude of east and west of the target area.
west = -63
east = -62
north = -8
south = -9

'''
#e.g. 
#Porto Velho (ID:1)
west = -63
east = -62
north = -8
south = -9

#Humaita (ID:2)
west = -62
east = -61
north = -7
south = -8

#Altamira (ID:3)
west = -52
east = -51
north = -2
south = -3

#Vista Alegre do Abuna (ID:4)
west = -67
east = -66
north = -9
south = -10

#Novo Progresso (ID:5)
west = -56
east = -55
north = -7
south = -8 

#Sao_Felix_do_Xingu (ID:6)
west = -54
east = -53
north = -6
south = -7

#S6W57 (ID:7)
west = -57
east = -56
north = -6
south = -7

#S7W57 (ID:8)
west = -57
east = -56
north = -7
south = -8
'''

#set main directory
#main_dir = "/path/to/directory"
main_dir = os.getcwd()

# new folders
polygon_folder_dir = os.path.join(main_dir, 'polygon')
data_folder_dir = os.path.join(main_dir, 'data')

#mesh size(m)(default:1000)
resolution = 1000

##########
#  main  #
##########
# if west >= east or south >= north, then exit.
if  west >= east:
    print("ERROR! East must be greater than west.")
    sys.exit()
if south >= north:
    print("ERROR! North must be greater than south.")
    sys.exit()

#create target polygon area
gdf_polygon_area = gpd.GeoDataFrame({'target': ['1'], 'geometry':[Polygon([(west, south), (west, north),(east, north), (east, south)])]},crs="EPSG:4326")

average = (west + east) /2
#define Universal Transverse Mercator(UTM) coordinate system using (west + east)/2
if  average >= -78 and average <= -72:
    #UTM 18S
    crs = "EPSG:32718"
elif average >= -72 and average <= -66:
    #UTM 19S
    crs = "EPSG:32719"
elif average >= -66 and average <= -60:
    #UTM 20S
    crs = "EPSG:32720"
elif average >= -60 and average <= -54:
    #UTM 21S
    crs = "EPSG:32721"
elif average >= -54 and average <= -48:
    #UTM 22S
    crs = "EPSG:32722"
elif average >= -48 and average <= -42:
      #UTM 23S
    crs = "EPSG:32723"
elif average >= -42 and average <= -36:
      #UTM 24S
    crs = "EPSG:32724"
elif average >= -36 and average <= -30:
      #UTM 25sS
    crs = "EPSG:32725"
else:
    print("ERROR! out of range or cross the boundary")
    sys.exit()   

#set UTM coordinate system
gdf_polygon_area_UTM = gdf_polygon_area.to_crs(crs)  

#calculate minx,miny, maxx and maxy
gdf_polygon_area_UTM_bounds = gdf_polygon_area_UTM.bounds
minx = math.ceil(gdf_polygon_area_UTM_bounds.loc[0, "minx"] / resolution) * resolution
miny = math.ceil(gdf_polygon_area_UTM_bounds.loc[0, "miny"] / resolution) * resolution
maxx = math.floor(gdf_polygon_area_UTM_bounds.loc[0, "maxx"] / resolution) * resolution
maxy = math.floor(gdf_polygon_area_UTM_bounds.loc[0, "maxy"] / resolution) * resolution

#create the list of the cols and rows
cols = list(np.arange(minx, maxx + resolution, resolution))
rows = list(np.arange(miny, maxy + resolution, resolution))

#create empty geodatabase
gdf_grid_polygon = gpd.GeoDataFrame()

#create grid polygon
for x in cols[:-1]:
    for y in rows[:-1]:
        cell = gpd.GeoDataFrame([Polygon([(x,y), (x + resolution, y), (x + resolution, y + resolution), (x, y + resolution)])])
        cell["left"] = x
        cell["top"] = y + resolution
        cell["right"] = x + resolution
        cell["bottom"] = y
        gdf_grid_polygon = gpd.GeoDataFrame(pd.concat([gdf_grid_polygon,cell], ignore_index=True))

gdf_grid_polygon = gdf_grid_polygon.set_geometry(0)
gdf_grid_polygon = gdf_grid_polygon.set_crs(crs)

#extract grid polygon within the target area
gdf_grid_polygon_target_area = gdf_grid_polygon.sjoin(gdf_polygon_area_UTM, how="inner", predicate="within").drop(['index_right', 'target'], axis=1)

#set ID
gdf_grid_polygon_target_area['ID'] = range(ID*1000000 + 1, ID*1000000 + len(gdf_grid_polygon_target_area.index) + 1)

#create directory
os.makedirs(os.path.join(polygon_folder_dir, str(ID)), exist_ok=True)

#export target polygon geojson file to main directry
#gdf_polygon_area_UTM.to_file(driver='GeoJSON', filename=main_dir  + "/polygon/" + str(ID) +"_target.geojson")
#export grid polygon geojson file to main directry
gdf_grid_polygon_target_area.to_file(driver='GeoJSON', filename=os.path.join(polygon_folder_dir, str(ID), "1km_mesh.geojson"))

#read DETER polygon
gdf_deter_polygon = gpd.read_file(os.path.join(main_dir, "deter-amz-deter-public.shp"), encoding='UTF-8').explode(ignore_index=True)

#convert CRS
gdf_target_polygon = gdf_polygon_area_UTM.to_crs("EPSG:4674")

#extract deforestation polygon
gdf_deforestation_polygon = gdf_deter_polygon.query('CLASSNAME == ["DESMATAMENTO_CR", "DESMATAMENTO_VEG","MINERACAO"]')

#clip deforestation polygon
gdf_deforestation_clip = gpd.clip(gdf_deforestation_polygon, gdf_target_polygon)

#set CRS
gdf_deforestation_clip.crs = "EPSG:4674"  

#extract polygon (remove line)
gdf_deforestation_clip = gdf_deforestation_clip[gdf_deforestation_clip.geometry.type == 'Polygon']

#set view data
gdf_deforestation_clip['VIEW_DATE']= pd.to_datetime(gdf_deforestation_clip['VIEW_DATE'])

#get start year, month and end year, month
startyear = gdf_deforestation_clip['VIEW_DATE'].min().year
startmonth = gdf_deforestation_clip['VIEW_DATE'].min().month
endyear = gdf_deforestation_clip['VIEW_DATE'].max().year
endmonth = gdf_deforestation_clip['VIEW_DATE'].max().month
year_range = endyear - startyear + 1

#set UTM coordinate system
gdf_deforestation_clip = gdf_deforestation_clip.to_crs(crs)
gdf_deforestation_clip['geometry'] = gdf_deforestation_clip['geometry'].buffer(0)
gdf_grid_polygon = gdf_grid_polygon_target_area.set_index('ID').reset_index()

#create directory
os.makedirs(os.path.join(data_folder_dir, "feature", str(ID)), exist_ok=True)
flag0 = 0

for i in range(year_range):
    year = startyear + i
    for month in range(1,13):
         if year == startyear and month < startmonth:
           continue
         else:        
            if year == endyear and month == endmonth + 1:
                break
            #print(year,month)

            if flag0 == 0:
                gdf_result_output = gdf_grid_polygon.copy()
       
            #extract deforestation polygon in target month
            gdf_polygon_extract1 = gdf_deforestation_clip[(gdf_deforestation_clip['VIEW_DATE'].dt.year == year) & (gdf_deforestation_clip['VIEW_DATE'].dt.month  == month)]

            #if nodata then 0
            if len(gdf_polygon_extract1.index) == 0:
                area_date = str(year) + str(month).zfill(2)
                gdf_result_output[area_date] = 0
            else:
                #dissolve polygon
                gdf_polygon_extract2 = gdf_polygon_extract1.dissolve(as_index=False).explode()

                if flag0 == 0:
                    gdf_polygon_extract = gdf_polygon_extract2.copy()
                    flag0 = 1
                else:
                    #extract previous deforestation polygon
                    gdf_polygon_before1 = gdf_deforestation_clip[(gdf_deforestation_clip['VIEW_DATE'].dt.year < year) | ((gdf_deforestation_clip['VIEW_DATE'].dt.year == year) & (gdf_deforestation_clip['VIEW_DATE'].dt.month  < month))]
                    
                    #dissolve polygon
                    gdf_polygon_before = gdf_polygon_before1.dissolve(as_index=False).explode()
                    gdf_polygon_extract = gpd.overlay(gdf_polygon_extract2, gdf_polygon_before, how='difference', keep_geom_type=False).explode()

                    #extract polygon (remove line)
                    gdf_polygon_extract = gdf_polygon_extract[gdf_polygon_extract.geometry.type == 'Polygon']
                       
                #intersection mesh and polygon_extract
                gdf_intersect = gpd.overlay(gdf_grid_polygon,gdf_polygon_extract, how='intersection', keep_geom_type=False).reset_index() 

                #calculate area
                gdf_intersect['area'] = gdf_intersect['geometry'].area

                #extract column ID and area
                gdf_intersect_area = gdf_intersect[["ID", "area"]]

                #sum by mesh id
                df_intersect_area_sum = gdf_intersect_area.groupby("ID").sum().reset_index()

                #merge mesh polygon and sum area
                gdf_result = pd.merge(gdf_grid_polygon,df_intersect_area_sum, how='left', on='ID')

                #NoData to 0
                gdf_result['area'] = gdf_result['area'].fillna(0) 
                area_date = str(year) + str(month).zfill(2)
                gdf_result_output[area_date] = gdf_result['area']
 
#export geojson for check
gdf_result_output.to_file(driver='GeoJSON', filename=os.path.join(polygon_folder_dir, str(ID), "1km_mesh_deforestation_area.geojson"))

#export csv file
df_result_output = pd.DataFrame(gdf_result_output.drop(columns=[0,'left','top','right','bottom']))
df_result_output.to_csv(os.path.join(data_folder_dir, "feature", str(ID), "deforestation_area.csv"), index=False)

df_result_output2 = df_result_output.set_index('ID')
df_result_output2.where(df_result_output2 == 0,1,inplace=True)
df_result_output2.to_csv(os.path.join(data_folder_dir, "feature", str(ID), "deforestation.csv"), index=True)

print("finished!")