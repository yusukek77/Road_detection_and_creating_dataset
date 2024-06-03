import geopandas as gpd
import pandas as pd
import rasterio

inputpath="./outputs_Porto_Velho_10000_proximity_value/"
mesh_centroid = "./Porto_Velho_1km_mesh_centroid_WGS84_UTM20S.json"
outputpath ="./mesh_centroid_point_road_distance_value/"
data = ['201606','201612','201706','201712','201806','201812','201906','201912','202006','202009','202011','202101','202104','202105','202106','202107','202108','202109','202110','202111','202205','202206','202207','202208','202209']


gdf_points  = gpd.read_file(mesh_centroid)
gdf_points['id'] = gdf_points['id'].astype(int)
df_points_merge = pd.DataFrame(gdf_points).drop(columns='geometry')

coord_list = [(x, y) for x, y in zip(gdf_points["geometry"].x, gdf_points["geometry"].y)]
output_csv = outputpath + "Porto_Velho_centroid_point_value.csv"

for i in data:
    input_tiff = inputpath + i + "_Porto_Velho_proximity_value_over30.tif"
    
    src = rasterio.open(input_tiff)

    gdf_points['value1'] = [x for x in src.sample(coord_list)]
    df_points = pd.DataFrame(gdf_points).drop(columns='geometry')
    df_points_merge[i] = df_points['value1'].astype(int)

    print(i ," finished!")

df_points_merge.to_csv(output_csv,index=False)
