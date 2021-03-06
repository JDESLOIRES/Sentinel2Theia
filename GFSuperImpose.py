import os
import numpy as np
import subprocess


def GFSuperImpose(otb_path, path_root, bands_20=['B5', 'B6', 'B7', 'B8A', 'B11', 'B12']):
    '''

    Args:
        path_root (str) : folder that contains GEOTIFFS file obtained from stack_data.py
        otb_path (str) : folder where OTB is installed
        bands_20 (list) : name of the bands in 20m that will be superimposed into 10 meters
    '''
    tif_10_meters = []
    tif_20_meters = []

    for k in os.listdir(path_root):
        if np.any([x in k for x in ['GF']]):
            if np.any([x in k for x in ['B5', 'B6', 'B7', 'B8A', 'B11', 'B12']]):
                tif_20_meters.append(k)
            elif np.any([x in k for x in ['B2', 'B3', 'B4', 'B8']]):
                tif_10_meters.append(k)

    for band in bands_20:
        file = os.path.join(path_root, 'GFstack_' + band + '_crop.tif')
        reference = os.path.join(path_root, tif_10_meters[0])
        out = os.path.join(path_root, 'GFstack_SI_' + band + '_crop.tif')

        cmd = [os.path.join(otb_path, "otbcli_Superimpose"),
               "-inr", "%s" % reference,
               "-inm", "%s" % file,
               "-out", "%s" % out,
               "uint16",
               "-ram", "10000"]


        shell = False
        subprocess.call(cmd, shell=shell)
        os.remove(file)
