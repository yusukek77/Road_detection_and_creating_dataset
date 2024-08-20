import numpy as np
import geopandas as gpd
import rasterio
from rasterio import features

target ='temp'

#Create polygon
remove_area_path = "./temp_error.json"
#remove_area_path = "./filename_error.json"


#data = ['201606','201612','201706','201712','201806','201812','201906','201912','202006','202009','202010','202011','202012','202101','202102','202103','202104','202105','202106','202107','202108','202109','202110','202111','202112','202201','202202','202203','202204','202205','202206','202207','202208','202209']
data = ['202105','202106','202107','202108']

inputpath ="./outputs_"+target+ "_merge_utm_value_over30_cumulation_roads/"
outputpath ="./outputs_"+target+ "_merge_utm_value_over30_cumulation_roads_error_removed/"

remove_area = gpd.read_file(remove_area_path)

# Get list of geometries for all features in vector file
geom = [shapes for shapes in remove_area.geometry]

for i in data:
    input_tiff = inputpath +i+ "merge_keypoints_" + target + "_over30_road_cumulation.tif"
    output_tiff = outputpath + i + "merge_keypoints_" + target + "_over30_road_cumulation_error_removed.tif"

    img1 = rasterio.open(input_tiff)
    input_meta = img1.meta
    input_meta.update(dtype=rasterio.int8,compress='lzw')
    input_img = img1.read(1)

    remove_area_rasterized = features.rasterize(geom,
                                out_shape = img1.shape,
                                #fill = 0,
                                out = None,
                                transform = img1.transform,
                                all_touched = False,
                                default_value = 1,
                                dtype = None)

    output = np.where(remove_area_rasterized == 1,0,input_img)

    with rasterio.open(output_tiff, "w", **input_meta) as dataset:
        dataset.write(output,indexes = 1)