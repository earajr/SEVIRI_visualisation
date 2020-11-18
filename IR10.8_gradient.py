import os
import glob
import sys
from satpy import Scene
import cartopy.crs as ccrs
import cartopy
import numpy as np
import scipy.ndimage as ndi
import matplotlib.pyplot as plt
import matplotlib
import datetime

###################################################################################################

# Define binary erosion and dilation structure

def disc(n):
    struct = np.zeros((2 * n + 1, 2 * n + 1))
    x, y = np.indices((2 * n + 1, 2 * n + 1))
    mask = (x - n)**2 + (y - n)**2 <= n**2
    struct[mask] = 1

    return struct.astype(np.bool)

###################################################################################################

diri = sys.argv[1] # input directory of decompressed HRIT files
date = sys.argv[2] # date in form 20180601
time = sys.argv[3] # time in form 1200

#create filelists for the current and previous timestep

my_files = glob.glob(diri+'/decompressed/*'+date+time+'*') # use glob.glob and wildcard to identify all HRIT files for the given date and time

# Load the satellite data using satpy and select pan African subdomain

global_scene = Scene(filenames=my_files, reader='seviri_l1b_hrit') # use satpy to read in HRIT files
global_scene.load(['IR_108'], calibration='brightness_temperature') # load the specific scene that is required. In this case 10.8 micrometer BT
IR108 = (global_scene["IR_108"].values-273.15) # export values from satpy scene to np array and subsample to pan Africa region (also convert to deg C)

dx, dy = np.gradient(IR108)
BT_grad = np.sqrt((dx**2.0)+(dy**2.0))

BT_thresh = np.where(IR108 <= -40.0, 1, 0)
BT_thresh = ndi.binary_erosion(BT_thresh,structure=disc(3))
BT_grad_thresh = np.where(BT_grad <= 10.0, 1, 0)
BT_grad_thresh = ndi.binary_erosion(BT_grad_thresh,structure=disc(1))

#BT_grad = np.where(BT_grad_thresh!=1, 0.0, BT_grad)
#BT_grad = ndi.gaussian_filter(BT_grad, sigma=1)

BT_grad = np.ma.masked_array(BT_grad, BT_thresh!=1)

#diff_grad = np.ma.masked_array(diff_grad, diff_grad_thresh!=1)

'''
#BT_thresh = ndi.binary_erosion(BT_thresh,structure=disc(2))
#BT_thresh = ndi.binary_dilation(BT_thresh,structure=disc(5))

diff = np.ma.masked_array(diff, BT_thresh!=1)

dx, dy = np.gradient(diff)

diff_grad = np.sqrt((dx**2.0)+(dy**2.0))
diff_grad_thresh = np.where(diff_grad <= 5.0, 1, 0)

diff_grad = np.ma.masked_array(diff_grad, diff_grad_thresh!=1)
diff_grad = ndi.gaussian_filter(diff_grad, sigma=1)

diff = np.ma.masked_array(diff, BT_thresh!=1)
'''

DPI=77.0

plt.clf()
plt.axis([0,3712, 0, 3712])
plt.figure(figsize=(3712.0/float(DPI), 3712.0/float(DPI)))
ax = plt.axes(projection=ccrs.Geostationary(central_longitude=0.0,satellite_height=35785831))
plt.imshow(IR108, cmap="Greys")
plt.imshow(BT_grad, cmap="jet")
plt.clim(0.0, 7.0)

ax.set_axis_off()

plt.savefig(diri+"/images/IR108_grad_"+date+"_"+time+".png",  transparent=True, bbox_inches="tight", pad_inches=0)

