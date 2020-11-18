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

cold_lim = -100.0
warm_lim = -60.0
grad_thresh = 3.0

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

my_files = glob.glob(diri+'/decompressed/*'+date+time+'*') # use glob.glob and wildcard to identify all HRIT files for the given date and time

global_scene = Scene(filenames=my_files, reader='seviri_l1b_hrit') # use satpy to read in HRIT files
global_scene.load(['IR_108'], calibration='brightness_temperature') # load the specific scene that is required. In this case 10.8 micrometer BT
#IR108 = (global_scene["IR_108"].values-273.15)[650:3200,360:2600][::-1,::-1] # export values from satpy scene to np array and subsample to pan Africa region (also convert to deg C)
IR108 = (global_scene["IR_108"].values-273.15)

IR108_mask = IR108
Tost = np.zeros_like(IR108)
OST = np.zeros_like(IR108)

thresh_warm = IR108_mask<=warm_lim
thresh_warm = ndi.binary_erosion(thresh_warm, structure=disc(5))
thresh_warm = ndi.binary_dilation(thresh_warm, structure=disc(7))
thresh_warm = np.where((thresh_warm) & (IR108_mask<=warm_lim) == True, 1, 0)

cells, number_of_cells = ndi.label(thresh_warm)

for i in range(1,number_of_cells+1, 1):
   mask = cells==i
   Tost = np.where(cells == i, np.mean(IR108[mask])-0.0, Tost)
   OST = np.where((cells == i) & (IR108-Tost <= 0.0) == True, IR108, OST)
   
Tost = np.where(Tost == 0, np.nan, Tost)
OST = np.where(OST == 0, np.nan, OST)

dx, dy = np.gradient(OST)

OST_grad = np.sqrt((dx**2.0)+(dy**2.0))
OST_grad_thresh = np.where(OST_grad>=grad_thresh, 1, 0)
OST_grad_thresh = ndi.binary_dilation(OST_grad_thresh, structure=disc(7))

OST = np.where(OST_grad_thresh == 1, IR108, np.nan)

DPI=77.0

plt.clf()
plt.axis([0,3712, 0, 3712])
plt.figure(figsize=(3712.0/float(DPI), 3712.0/float(DPI)))
ax = plt.axes(projection=ccrs.Geostationary(central_longitude=0.0,satellite_height=35785831))
plt.imshow(IR108, cmap="Greys")
plt.imshow(OST, cmap="jet_r")
ax.set_axis_off()
plt.clim(-90.0, -40.0)

plt.savefig(diri+"/images/ot_varthresh_"+date+"_"+time+".png",  transparent=True, bbox_inches="tight", pad_inches=0)

