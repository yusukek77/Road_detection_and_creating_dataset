import geopandas as gpd
import pandas as pd
import rasterio
import warnings
warnings.simplefilter('ignore')

##########
# config #
##########
#input ID
#"Porto Velho" is 1, "Humaita" is 2, "Altamira" is 3, "Vista Alegre do Abuna" is 4, "Novo Progresso" is 5,
#"Sao_Felix_do_Xingu" is 6, "S6W57" is 7,and "S7W57" is 8. If adding other area, please put the number in order from 9.
ID = 10

target ="temp"

#data = ['201606','201612','201706','201712','201806','201812','201906','201912','202006','202009','202011','202101','202104','202105','202106','202107','202108','202109','202110','202111','202205','202206','202207','202208','202209']
data = ['202105','202106','202107','202108']

##########
#  main  #
##########

folder =os.getcwd()
polygon_folder_dir = os.path.join(folder, 'polygon')

inputpath ="outputs_"+target+ "_proximity_value/"
gdf_mesh =  gpd.read_file(os.path.join(polygon_folder_dir, str(ID), "1km_mesh_with_centroid.geojson"))

gdf_points = gdf_mesh[['ID', 'centroid_x', 'centroid_y']]



output_csv =os.path.join("outputs_mesh_centroid_point_road_distance_value", target + "_centroid_point_value.csv")

df_points_merge = pd.DataFrame(gdf_points).drop(columns=['centroid_x', 'centroid_y'])

coord_list = [(x, y) for x, y in zip(gdf_points["centroid_x"], gdf_points["centroid_y"])]

for i in data:
    input_tiff = inputpath + i +  "merge_keypoints_" + target + "_proximity_value_over30.tif"

    src = rasterio.open(input_tiff)

    gdf_points['value1'] = [x for x in src.sample(coord_list)]
    df_points = pd.DataFrame(gdf_points).filter(items=['value1'])
    df_points_merge[i] = df_points['value1'].astype(int)

    print(i ," finished!")

df_points_merge.to_csv(output_csv,index=False)