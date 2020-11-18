#########################################################
#                 rapid_cooling.py                      #
#                                                       #
#     Read in decompressed HRIT files (currently only   #
#     10.8 micron BT) and output netcdf of cells and    #
#     a text file with id information.                  #
#                                                       #
#     Written by Alexander Roberts                      #
#     June 2019                                         #
#     NCAS, ICAS, University of Leeds                   #
#                                                       #
# python rapid_cooling.py.py $MSGsat YYYYMMDD HHMM      #
#########################################################

import os
import glob
import sys
from satpy import Scene
import cartopy.crs as ccrs
import cartopy
import matplotlib.pyplot as plt
import matplotlib
import scipy.ndimage as ndi
import numpy as np
from netCDF4 import Dataset
import datetime
from pathlib import Path
from skimage import segmentation
from skimage.feature import peak_local_max
from skimage import morphology

###################################################################################################

# Define binary erosion and dilation structure

def disc(n):
    struct = np.zeros((2 * n + 1, 2 * n + 1))
    x, y = np.indices((2 * n + 1, 2 * n + 1))
    mask = (x - n)**2 + (y - n)**2 <= n**2
    struct[mask] = 1

    return struct.astype(np.bool)

###################################################################################################

# Use arguments to input the $MSGsat directory, the date and the time

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

# Calculate Brightness temperature difference between current and previous timestep

BT_diff = IR108_1-IR108_2

# Create mask based on BT difference between current and previous timestep and threshold cooling in BT of 20.0 deg C 

BT_diff_thresh = np.where(BT_diff <= -5.0, 1, 0)

# Apply eriosion using small disk structure followed by dilation using larger disk structure

BT_diff_thresh = ndi.binary_erosion(BT_diff_thresh,structure=disc(2))
BT_diff_thresh = ndi.binary_dilation(BT_diff_thresh,structure=disc(5))

cool = np.ma.masked_array(BT_diff, BT_diff_thresh!=1)

# Plot image 

DPI=77.0

plt.clf()
plt.axis([0,3712, 0, 3712])
plt.figure(figsize=(3712.0/float(DPI), 3712.0/float(DPI)))
ax = plt.axes(projection=ccrs.Geostationary(central_longitude=0.0,satellite_height=35785831))
plt.imshow(IR108_1, cmap="Greys")
plt.imshow(cool, cmap="jet_r")
ax.set_axis_off()
plt.clim(-80.0, -0.0)

plt.savefig(diri+"/images/cool_"+date+"_"+time+".png",  transparent=True, bbox_inches="tight", pad_inches=0)

#
#fig, ax = plt.subplots(figsize=(15,15))
#
#plt.imshow(IR108_1[::,::], cmap="Greys")
#ax.set_axis_off()
#
#rapid_cool = np.ma.masked_array(BT_diff, BT_diff_thresh!=1)
#
#plt.imshow(rapid_cool[::,::], cmap="jet_r")
#plt.colorbar()
#plt.clim(-80.0, 30.0)
#
#plt.savefig("rapid_cooling_"+date+"_"+time+".png")
