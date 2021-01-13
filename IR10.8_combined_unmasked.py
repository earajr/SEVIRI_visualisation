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

# Calculate the date and time of the previous timestep

dt_last = datetime.datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]), int(time[0:2]), int(time[2:4]))-datetime.timedelta(minutes=15)
date_last = (dt_last.strftime('%Y%m%d'))
time_last = (dt_last.strftime('%H%M'))

#create filelists for the current and previous timestep

my_files = glob.glob(diri+'/decompressed/*'+date+time+'*') # use glob.glob and wildcard to identify all HRIT files for the given date and time
my_files2 = glob.glob(diri+'/decompressed/*'+date_last+time_last+'*')


# Load the satellite data using satpy and select pan African subdomain

global_scene = Scene(filenames=my_files, reader='seviri_l1b_hrit') # use satpy to read in HRIT files
global_scene.load(['IR_108'], calibration='brightness_temperature') # load the specific scene that is required. In this case 10.8 micrometer BT
IR108 = (global_scene["IR_108"].values-273.15) # export values from satpy scene to np array and subsample to pan Africa region (also convert to deg C)

global_scene2 = Scene(filenames=my_files2, reader='seviri_l1b_hrit') # use satpy to read in HRIT files
global_scene2.load(['IR_108'], calibration='brightness_temperature') # load the specific scene that is required. In this case 10.8 micrometer BT
IR108_2 = (global_scene2["IR_108"].values-273.15) # export values from satpy scene to np array and subsample to pan Africa region (also convert to deg C)

BT_diff = IR108 - IR108_2

dx, dy = np.gradient(IR108)
BT_grad = np.sqrt((dx**2.0)+(dy**2.0))

#BT_thresh = np.where(IR108 <= -40.0, 1, 0)
#BT_thresh = ndi.binary_erosion(BT_thresh,structure=disc(3))
#BT_grad_thresh = np.where(BT_grad <= 10.0, 1, 0)
#BT_grad_thresh = ndi.binary_erosion(BT_grad_thresh,structure=disc(1))


#BT = np.ma.masked_array(IR108, BT_thresh!=1)
BT = IR108
BT = ((((BT*-1.0)-40.0)/5.0)/10.0)
#BT_grad = np.ma.masked_array(BT_grad, BT_thresh!=1)
BT_grad = np.where(BT_grad > 7.0, 7.0, BT_grad)
BT_grad = ((BT_grad*(10.0/7.0))/10.0)**0.5
#BT_diff = np.ma.masked_array(BT_diff, BT_thresh!=1)
BT_diff = np.where(BT_diff > 0.0, 0.0, BT_diff)
BT_diff = np.where(BT_diff < -10.0, -10, BT_diff)
BT_diff = ((BT_diff/10.0)*(-1.0))**0.5

#RGBA

BT_combined = [BT_grad, BT, BT_diff]

#
#
##diff_grad = np.ma.masked_array(diff_grad, diff_grad_thresh!=1)
#
#'''
##BT_thresh = ndi.binary_erosion(BT_thresh,structure=disc(2))
##BT_thresh = ndi.binary_dilation(BT_thresh,structure=disc(5))
#
#diff = np.ma.masked_array(diff, BT_thresh!=1)
#
#dx, dy = np.gradient(diff)
#
#diff_grad = np.sqrt((dx**2.0)+(dy**2.0))
#diff_grad_thresh = np.where(diff_grad <= 5.0, 1, 0)
#
#diff_grad = np.ma.masked_array(diff_grad, diff_grad_thresh!=1)
#diff_grad = ndi.gaussian_filter(diff_grad, sigma=1)
#
#diff = np.ma.masked_array(diff, BT_thresh!=1)
#'''
#
DPI=77.0

plt.clf()
plt.axis([0,3712, 0, 3712])
plt.figure(figsize=(3712.0/float(DPI), 3712.0/float(DPI)))
ax = plt.axes(projection=ccrs.Geostationary(central_longitude=0.0,satellite_height=35785831))
#plt.imshow(IR108, cmap="Greys")
plt.imshow(np.dstack(BT_combined), interpolation="none")

ax.set_axis_off()

plt.savefig(diri+"/images/IR108_combined_unmasked_"+date+"_"+time+".png",  transparent=True, bbox_inches="tight", pad_inches=0)

