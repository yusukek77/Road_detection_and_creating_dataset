import os

import numpy as np
import rasterio
import glob
import sys


threshold = 30

target_list =['Porto_Velho_10000','Humaita_20000','Altamira_30000','Vista_Alegre_do_Abuna_40000','Novo_Progresso_50000','Sao_Felix_do_Xingu_60000','S6W57_70000','S7W57_80000']

for target in target_list:
    inputpath = "./outputs_"+target + "_merge_utm/"
    outputpath = "./outputs_"+target+ "_merge_utm_value_over30/"

    data_path = glob.glob(inputpath + '*.tif')

    for filepath in data_path:
        basename = os.path.basename(filepath)
        date = basename[:6]
        output_tiff = outputpath + date + "merge_keypoints_"+ target + "_value_utm_over30.tif"
        img1 = rasterio.open(filepath)
        input_meta = img1.meta
        input_meta.update(dtype=rasterio.int8,compress='lzw')
       
        input_img = img1.read(1)
    
        output_img = np.where(input_img <= threshold, 0 ,1)
    
        with rasterio.open(output_tiff,'w', **input_meta) as outdata:
            outdata.write_band(1,output_img.astype(rasterio.int8))

        print(date ," finished!")
