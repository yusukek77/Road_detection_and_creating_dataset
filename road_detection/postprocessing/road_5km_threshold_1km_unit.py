import pandas as pd
import math
import os

target_area_list = ["temp"]

main_dir =os.path.join(os.getcwd(), "outputs_mesh_centroid_point_road_distance_value")
#main_dir = "/path/to/"

for target in target_area_list:

    road_path = os.path.join(main_dir, "road_1km_mesh_"+target +".csv")
    export_path_5km = os.path.join(main_dir, "road_5km_"+target +".csv")
    export_path_1km_unit = os.path.join(main_dir, "road_1km_unit_"+target +".csv")

    df_road =  pd.read_csv(road_path,index_col=0, header=0)
    data = df_road.columns.values

    df_road_1km_unit = df_road.copy()

    for i in data:
        print(i)
        df_road[i] = df_road[i].apply(lambda x : 1 if x <= 5000 else 0)
        df_road_1km_unit[i] = df_road_1km_unit[i].apply(lambda x : math.ceil(x/1000))

    df_road.to_csv(export_path_5km, header=True, index=True)

    df_road_1km_unit.to_csv(export_path_1km_unit, header=True, index=True)