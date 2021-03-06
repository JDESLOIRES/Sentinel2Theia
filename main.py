import os
import pandas as pd
import numpy as np
import Sentinel2Theia.unzip_data as unzip_data
import Sentinel2Theia.stack_data as stack_data
import Sentinel2Theia.GapFilling as GapFilling
import Sentinel2Theia.GFSuperImpose as GFSuperImpose
import Sentinel2Theia.VegetationIndices as VegetationIndices
import Sentinel2Theia.training_set as training_set

###Input files (see readme)
#Orfeo Toolbox
path = '/media/DATA/johann/PUL/TileHG/'
os.chdir(path)
otb_path = '/home/johann/OTB-7.2.0-Linux64/bin'
os.path.exists(otb_path)
##Theia folder pulled
folder_theia = './Sentinel2/theia_download'
os.path.exists(folder_theia)
#Folder to save images preprocessed
path_output = './Sentinel2/GEOTIFFS'
os.path.exists(path_output)
#Input vector for training process
vector_path = './FinalDBPreprocessed/DATABASE_SAMPLED/DATABASE_SAMPLED.shp'
os.path.exists(vector_path)
#Polygon of the Area of Interest
mask_data = './FinalDBPreprocessed/HG_TILE_INTERSECTION/INTERSECTION_TILE_DEPARTMENT/intersection_hg_tile.shp'
os.path.exists(mask_data)
mask_feature = 'DN'

band_names = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12']

##################################################################################
#Download Sentinel-2 images
download = unzip_data.TheiaDownload(folder_theia,
                                    tile_name="T31TCJ",
                                    start_date="2018-11-20",
                                    end_date="2018-12-01")

download.download_data()
download.unzip_data()

##################################################################################
#Rasterize labels using a reference file from Sentinel-2 folders
reference_file = stack_data.GetRandomTheiaFile(folder_theia, band_name='B2')

rasterize_labels = stack_data.RasterLabels(vector_path=vector_path,
                                           reference_file=reference_file,
                                           extent_vector=mask_data,
                                           saving_path=path_output,
                                           ObjectID='Class_ID',
                                           LabelID='Label_Code')

rasterize_labels.rasterize_labels()

#GEOTIFFS concatenation cropped according to the AOI
concatenate_images = stack_data.StackFoldersSentinel2(extent_vector=mask_data,
                                                      bands=band_names,
                                                      res_bands=[10, 10, 10, 20, 20, 20, 10, 20, 20, 20],
                                                      saving_path=path_output,
                                                      folder_theia=folder_theia,
                                                      name_mask_feature='DN')

concatenate_images.ExtractImagesFolder()
concatenate_images.CropImages()

###############################################################################################################
#Cloud masking interpolation
GapFilling.GapFill(otb_path,
                   path_output,
                   bands=['B2', 'B3', 'B4', 'B8'],
                   res=10)

GapFilling.GapFill(otb_path,
                   path_output,
                   bands=['B5', 'B6', 'B7', 'B8A', 'B11', 'B12'],
                   res=20)

#Put 20 meters images into 10 meters
GFSuperImpose.GFSuperImpose(otb_path,
                            path_output,
                            bands_20=['B5', 'B6', 'B7', 'B8A', 'B11', 'B12'])

##################################################################################################################
#Compute NDVI, GNDVI and NDWI
vis = VegetationIndices.VegetationIndices(saving_path=path_output,
                                          band_names=['B2', 'B4', 'B8', 'B11'])

vis.compute_VIs()

##################################################################################################################
#CSubset time series

GapFilling.subset_time_series(path_output,band_names,'2019')

GapFilling.subset_time_series(path_output,['NDVI','GNDVI','NDWI'],'2019')


##################################################################################################################
#Built the training set for given features
features = ['B2', 'B3', 'B4', 'NDVI', 'GNDVI', 'NDWI']
#this file has been automatically create during StackFoldersSentinel2()
dates = pd.read_csv(os.path.join(path_output, 'dates.csv'))
#Path to save the output training set
path_ts = '/home/johanndesloires/Documents/Sentinel2/FinalDB'
#Random geotiff file created from the steps above that will be used as geo reference
reference_file = os.path.join(path_output, 'GFstack_B2_crop.tif')

output_files = training_set.TrainingSet(path_images=path_output,
                                        band_names=features,
                                        dates=dates,
                                        saving_path=path_ts,
                                        reference_file=reference_file,
                                        ObjectID=os.path.join(path_output, 'Class_ID_crop.tif'),
                                        LabelID=os.path.join(path_output, 'Label_Code_crop.tif'))

output_files.prepare_training_set()
