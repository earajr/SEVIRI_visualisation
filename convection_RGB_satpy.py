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

import glob
import sys
from satpy import Scene
import dask
import numpy as np
from astropy.visualization import make_lupton_rgb
import matplotlib.pyplot as plt
import satpy
print(satpy.__file__)

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

#create filelists for the current timestep

my_files1 = glob.glob(diri+'/decompressed/*'+date+time+'*') # use glob.glob and wildcard to identify all HRIT files for the given date and time

# Load the satellite data using satpy and select pan African subdomain
# HRV IR_108 IR_120 VIS006 WV_062 IR_039 IR_134 IR_097 IR_087 VIS008 IR_016 WV_073
# HRV   9      10     1      5       4     11     8       7     2      3      6

global_scene1 = Scene(filenames=my_files1, reader='seviri_l1b_hrit') # use satpy to read in HRIT files

composite = 'convection'

global_scene1.load([composite])

global_scene1.save_dataset(composite, diri+"/images/convection_satpy_"+date+"_"+time+".png")
#global_scene1.save_dataset(composite, "convection_satpy_"+date+"_"+time+".png")
