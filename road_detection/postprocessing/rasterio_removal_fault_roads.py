import rasterio
import numpy as np
import shutil



inputpath ="./outputs_Porto_Velho_10000_merge_wgs84_utm20s_value_over30/"
outputpath ="./outputs_Porto_Velho_10000_over30_removal_fault_roads/"

filename ="merge_keypoints_Porto_Velho_value_wgs84_utm20s_over30.tif"
target ="Porto_Velho"

data = ['201606','201612','201706','201712','201806','201812','201906','201912','202006','202009','202010','202011','202012','202101','202102','202103','202104','202105','202106','202107','202108','202109','202110','202111','202112','202201','202202','202203','202204','202205','202206','202207','202208','202209']

j = 0
for j in range(len(data)-2):
    print(data[j])
    print(data[j+1])
    print(data[j+2])
    print("")

    input_tiff = inputpath + data[j] + filename
    input_tiff1 = inputpath + data[j+1] + filename
    input_tiff2 = inputpath + data[j+2] + filename

    output_tiff = outputpath + data[j] + "merge_keypoints_" + target + "_over30_removal_fault_roads.tif"
    img = rasterio.open(input_tiff)
    input_meta = img.meta
    input_img = img.read(1)

    img1 = rasterio.open(input_tiff1)
    input1_meta = img1.meta
    input1_img = img1.read(1)

    img2 = rasterio.open(input_tiff2)
    input2_meta = img2.meta
    input2_img = img2.read(1)

    calc1 = np.where(input1_img+input2_img>=1,1,0)
    result = input_img * calc1
    
    input_meta.update(dtype=rasterio.int8,compress='lzw')
    
    with rasterio.open(output_tiff,'w', **input_meta) as outdata:
        outdata.write_band(1,result.astype(rasterio.int8))    
    
    print(data[j] ," finished!")    

output_tiff1 = outputpath + data[j+1] + "merge_keypoints_" + target + "_over30_removal_fault_roads.tif"
output_tiff2 = outputpath + data[j+2] + "merge_keypoints_" + target + "_over30_removal_fault_roads.tif"

shutil.copy2(input_tiff1,output_tiff1)
shutil.copy2(input_tiff2,output_tiff2)
