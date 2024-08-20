import rasterio
import numpy as np
import pandas as pd
from scipy.ndimage import label, generate_binary_structure

target ='temp'

#data = ['201606','201612','201706','201712','201806','201812','201906','201912','202006','202009','202010','202011','202012','202101','202102','202103','202104','202105','202106','202107','202108','202109','202110','202111','202112','202201','202202','202203','202204','202205','202206','202207','202208','202209']
data = ['202105','202106','202107','202108']

th = 150

#inputpath ="./outputs_Porto_Velho_10000_over30_removal_fault_roads/"
#outputpath ="./outputs_Porto_Velho_10000_over30_removal_fault_roads_eliminated/"

inputpath ="./outputs_"+target+ "_merge_utm_value_over30_removal_fault_roads/"
outputpath ="./outputs_"+target+ "_merge_utm_value_over30_removal_fault_roads_eliminated/"

s = generate_binary_structure(2,2)

for i in data:
    input_tiff = inputpath +i+ "merge_keypoints_" + target + "_over30_removal_fault_roads.tif"
    output_tiff = outputpath + i + "merge_keypoints_" + target + "_over30_removal_fault_roads_eliminated.tif"

    with rasterio.open(input_tiff) as img1:
        img = img1.read(1)
        img_meta = img1.meta
        img_meta.update(
        dtype=rasterio.uint8,
        #count=1,
        compress='lzw')

    labeled_img, num_features = label(img, structure=s)
    labeled_img2 = np.where(img==0,0,labeled_img)
    np_count = np.array(np.unique(labeled_img2, return_counts=True)).T

    col = ['id','count']
    df_count = pd.DataFrame(np_count)
    df_count2 = df_count.set_axis(['id','count'],axis=1).drop(df_count.index[0])
    df_count_valid = df_count2[df_count2['count'] >= th]
    df_count_valid_id = df_count_valid['id']

    np_count_valid_id = df_count_valid_id.values
    lines = np_count_valid_id.shape[0]
    for i in range(lines):
        labeled_img2  = np.where(labeled_img2  == np_count_valid_id[i],-1,labeled_img2)

    img_out = np.where(labeled_img2 >= 0,0,1)
    with rasterio.open(output_tiff, "w", **img_meta) as dataset2:
        dataset2.write(img_out,1)
