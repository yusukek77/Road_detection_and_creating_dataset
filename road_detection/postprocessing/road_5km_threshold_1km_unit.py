import pandas as pd
import math

target_area_list = ["Altamira","Porto_Velho","Humaita","Novo_Progresso","Vista_Alegre_do_Abuna","Sao_Felix_do_Xingu","S6W57","S7W57"]

main_dir = "/path/to/"
data = ['201606','201607','201608','201609','201610','201611','201612','201701','201702','201703','201704','201705','201706','201707','201708','201709','201710','201711','201712','201801','201802','201803','201804','201805','201806','201807','201808','201809','201810','201811','201812','201901','201902','201903','201904','201905','201906','201907','201908','201909','201910','201911','201912','202001','202002','202003','202004','202005','202006','202007','202008','202009','202010','202011','202012','202101','202102','202103','202104','202105','202106','202107','202108','202109','202110','202111','202112','202201','202202','202203','202204','202205','202206','202207','202208','202209']

for target in target_area_list:

    road_path = main_dir + "road_1km_mesh_"+target +".csv"
    export_path_5km = main_dir + "road_5km_"+target +".csv"
    export_path_1km_unit = main_dir + "road_1km_unit_"+target +".csv"


    df_road =  pd.read_csv(road_path,index_col=0, header=0)

    df_road_1km_unit = df_road.copy()

    for i in data:
        print(i)
        df_road[i] = df_road[i].apply(lambda x : 1 if x <= 5000 else 0)
        df_road_1km_unit[i] = df_road_1km_unit[i].apply(lambda x : math.ceil(x/1000))    
    
    df_road.to_csv(export_path_5km, header=True, index=True)  

    df_road_1km_unit.to_csv(export_path_1km_unit, header=True, index=True)

