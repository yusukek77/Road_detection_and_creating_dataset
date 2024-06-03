import numpy as np
import os
import shutil
import rasterio

inputpath ="./outputs_Porto_Velho_10000_over30_removal_fault_roads_eliminated/"
outputpath ="./outputs_Porto_Velho_10000_over30_cumulation_roads/"

target ="Porto_Velho"

data = ['201606','201612','201706','201712','201806','201812','201906','201912','202006','202009','202010','202011','202012','202101','202102','202103','202104','202105','202106','202107','202108','202109','202110','202111','202112','202201','202202','202203','202204','202205','202206','202207','202208','202209']


inputfilename =  "merge_keypoints_" + target + "_over30_removal_fault_roads_eliminated.tif"
outputfilename = "merge_keypoints_" + target + "_over30_road_cumulation.tif"

j = 0
for j in range(len(data)-1):
    print(data[j+1])
    print("")

    input_tiff1 = inputpath + data[j+1] + inputfilename
    output_tiff = outputpath + data[j+1] + outputfilename

    if j == 0:

       input_tiff = inputpath + data[j] + inputfilename
       #copy first file
       output1 = outputpath + data[j] + outputfilename
       shutil.copy2(input_tiff,output1)

       img = rasterio.open(input_tiff)
       input_meta = img.meta
       input_meta.update(dtype=rasterio.int8,compress='lzw')
       input_img = img.read(1) 

    else:
       input_tiff = outputpath + data[j] + outputfilename
       img = rasterio.open(input_tiff)
       input_img = img.read(1) 

    img1 = rasterio.open(input_tiff1)
    input1_img = img1.read(1)

    result = np.where(input_img+input1_img>=1,1,0)
    
    with rasterio.open(output_tiff,'w', **input_meta) as outdata:
        outdata.write_band(1,result.astype(rasterio.int8))     

    print(data[j] ," finished!")
    input_img = np.zeros(input_img.shape)
    input_img = np.copy(input1_img)
