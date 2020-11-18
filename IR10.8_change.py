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

my_files1 = glob.glob(diri+'/decompressed/*'+date+time+'*') # use glob.glob and wildcard to identify all HRIT files for the given date and time
my_files2 = glob.glob(diri+'/decompressed/*'+date_last+time_last+'*')

# Load the satellite data using satpy and select pan African subdomain

global_scene1 = Scene(filenames=my_files1, reader='seviri_l1b_hrit') # use satpy to read in HRIT files
global_scene1.load(['IR_108'], calibration='brightness_temperature') # load the specific scene that is required. In this case 10.8 micrometer BT
IR108_1 = (global_scene1["IR_108"].values-273.15) # export values from satpy scene to np array and subsample to pan Africa region (also convert to deg C)

global_scene2 = Scene(filenames=my_files2, reader='seviri_l1b_hrit') # use satpy to read in HRIT files
global_scene2.load(['IR_108'], calibration='brightness_temperature') # load the specific scene that is required. In this case 10.8 micrometer BT
IR108_2 = (global_scene2["IR_108"].values-273.15) # export values from satpy scene to np array and subsample to pan Africa region (also convert to deg C)

diff = IR108_1 - IR108_2

BT_thresh = np.where(IR108_1 <= -40.0, 1, 0)

#BT_thresh = ndi.binary_erosion(BT_thresh,structure=disc(2))
#BT_thresh = ndi.binary_dilation(BT_thresh,structure=disc(5))

diff = np.ma.masked_array(diff, BT_thresh!=1)

DPI=77.0

plt.clf()
plt.axis([0,3712, 0, 3712])
plt.figure(figsize=(3712.0/float(DPI), 3712.0/float(DPI)))
ax = plt.axes(projection=ccrs.Geostationary(central_longitude=0.0,satellite_height=35785831))
plt.imshow(IR108_1, cmap="Greys")
plt.imshow(diff, cmap="jet")
plt.clim(-10.0, 10.0)

ax.set_axis_off()

plt.savefig(diri+"/images/IR108_change_"+date+"_"+time+".png",  transparent=True, bbox_inches="tight", pad_inches=0)

