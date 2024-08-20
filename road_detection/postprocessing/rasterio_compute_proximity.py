import os

import rasterio
from scipy import ndimage

target ="temp"

#data = ['201606','201612','201706','201712','201806','201812','201906','201912','202006','202009','202010','202011','202012','202101','202102','202103','202104','202105','202106','202107','202108','202109','202110','202111','202112','202201','202202','202203','202204','202205','202206','202207','202208','202209']
data = ['202105','202106','202107','202108']

#inputfilename = "merge_keypoints_" + target + "_over30_road_cumulation_error_removed.tif"
inputfilename =  "merge_keypoints_" + target + "_over30_road_cumulation.tif"

outputfilename = "merge_keypoints_" + target + "_proximity_value_over30.tif"

inputpath ="./outputs_"+target+ "_merge_utm_value_over30_cumulation_roads/"
outputpath ="./outputs_"+target+ "_proximity_value/"

cellsize = 4.777314267160000405

for i in data:
    input_tiff = inputpath + i + inputfilename
    output_tiff = outputpath + i + outputfilename

    img = rasterio.open(input_tiff)
    input_meta = img.meta

    input_meta.update(dtype=rasterio.uint32,compress='lzw')


    input_img = img.read(1)
    output = (ndimage.distance_transform_edt(input_img!=1) * cellsize).astype('int32')

    with rasterio.open(output_tiff,'w', **input_meta) as outdata:
        outdata.write_band(1,output.astype(rasterio.int32))

    print(i ," finished!")