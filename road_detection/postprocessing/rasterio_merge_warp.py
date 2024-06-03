import rasterio
import glob
import sys
from rasterio.merge import merge
from rasterio.warp import reproject, Resampling, calculate_default_transform

#input target list
target_list =['Porto_Velho_10000','Humaita_20000','Altamira_30000','Vista_Alegre_do_Abuna_40000','Novo_Progresso_50000','Sao_Felix_do_Xingu_60000','S6W57_70000','S7W57_80000']

data = ['201606','201612','201706','201712','201806','201812','201906','201912','202006','202009','202010','202011','202012','202101','202102','202103','202104','202105','202106','202107','202108','202109','202110','202111','202112','202201','202202','202203','202204','202205','202206','202207','202208','202209']

for target in target_list:
  inputpath ="./outputs_"+target + "/"
  outputpath1="./outputs_"+target + "_merge/"
  outputpath2="./outputs_"+target + "_merge_utm/"
  
  if target == 'Vista_Alegre_do_Abuna_40000':
    dst_crs = 'EPSG:32719'
  elif target == 'Porto_Velho_10000' or target == 'Humaita_20000':
    dst_crs = 'EPSG:32720'      
  elif target == 'Novo_Progresso_50000' or target == 'S6W57_70000' or target == 'S7W57_80000':
    dst_crs = 'EPSG:32721' 
  elif target == 'Porto_Velho_10000' or target == 'Altamira_30000' or target == 'Sao_Felix_do_Xingu_60000':
    dst_crs = 'EPSG:32722'    
  else:
    print(target + " is projection error!")
    sys.exit()

  for i in data:   
    sat_path = glob.glob(inputpath + i +'*_sat.tif')
    key_path = glob.glob(inputpath + i + '*_output_keypoints.tif')
    sat_dest, sat_output = merge(sat_path)

    with rasterio.open(sat_path[0]) as src:
        out_meta = src.meta.copy()    
    out_meta.update({"driver": "GTiff",
                 "height": sat_dest.shape[1],
                 "width": sat_dest.shape[2],
                 "transform": sat_output})
    out_meta.update(compress='lzw')
    
    with rasterio.open(outputpath1 + i + "merge_sat.tif", "w", **out_meta) as sat_out:
        sat_out.write(sat_dest)

    key_dest, key_output = merge(key_path)

    with rasterio.open(key_path[0]) as src2:
        out_meta2 = src2.meta.copy()    
    out_meta2.update({"driver": "GTiff",
                 "height": key_dest.shape[1],
                 "width": key_dest.shape[2],
                 "transform": key_output})
    out_meta2.update(compress='lzw')
    
    with rasterio.open(outputpath1 + i + "merge_keypoints.tif", "w", **out_meta2) as key_out:
        key_out.write(key_dest)

        transform, width, height = calculate_default_transform(
        key_out.crs, dst_crs, key_out.width, key_out.height, *key_out.bounds)
        kwargs = out_meta2.copy()    
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })
        kwargs.update(dtype=rasterio.int8,compress='lzw')

        with rasterio.open(outputpath2+ i + "merge_keypoints_"+ target + "_utm.tif" , 'w', **kwargs) as dst:
            for j in range(1, key_out.count + 1):
                reproject(
                    source=rasterio.band(key_out, j),
                    destination=rasterio.band(dst, j),
                    src_transform=key_out.transform,
                    src_crs=key_out.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)        
   
    print(i + " is finished!")
