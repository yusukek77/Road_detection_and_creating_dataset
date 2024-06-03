import pandas as pd

target_area_list = ["Altamira","Porto_Velho","Humaita","Novo_Progresso","Vista_Alegre_do_Abuna","Sao_Felix_do_Xingu","S6W57","S7W57"]

main_dir = "/path/to/"
startyear = 2016
startmonth = 6
endyear = 2022
endmonth = 9

for target in target_area_list:

    #import csv
    df_data =pd.read_csv(main_dir + target +"_centroid_point_value.csv")

    df_result = df_data[["id"]]


    flag0 = 0
    year_month_name = 0


    for i in range(endyear - startyear + 1):
        year = startyear + i
        print(year)
        for month in range(1,13):
        
            if year == startyear and month < startmonth:
                    pass

            #after 2022-10-08, break
            elif year == endyear and month == endmonth:
                break

            else:
                date1 = str(year) + str(month).zfill(2)
                if date1 in df_data:
                    df_date_data = df_data[[date1]]
                    df_result = pd.concat([df_result,df_date_data], axis=1)
                    year_month_name = date1

                else:
                  df_date_data = df_date_data.rename(columns={year_month_name: date1})
                  year_month_name = date1

                df_result = pd.concat([df_result,df_date_data], axis=1)            

    df_result.to_csv(main_dir +"road_1km_mesh_"+target +".csv", index=False)
