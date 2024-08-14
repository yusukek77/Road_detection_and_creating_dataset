import geopandas as gpd
import pandas as pd
import glob
import os

outputname = "merge.json"

folder =os.getcwd()

gdf_merge = gpd.GeoDataFrame()
files = glob.glob(os.path.join(folder ,'*.json'))
for f in files:
    gdf_file1 = gpd.read_file(f)
    gdf_merge = gpd.GeoDataFrame(pd.concat([gdf_merge ,gdf_file1]))

gdf_merge.to_file(driver='GeoJSON', filename=os.path.join(folder,outputname))
