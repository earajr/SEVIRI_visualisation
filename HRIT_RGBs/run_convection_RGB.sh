#!/bin/bash

source /home/earajr/anaconda3/etc/profile.d/conda.sh

conda activate new_products

dates=("20200906")
MSG_dir=$MSGsat
data_dir="${MSG_dir}/HRIT_RGBs"
cd ${data_dir}

for date in ${dates}
do
   for hour in "00" "01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12" "13" "14" "15" "16" "17" "18" "19" "20" "21" "22" "23"
   do
      for min in "00" "15" "30" "45"
      do
        python ${MSG_dir}/convection_RGB_satpy.py ${data_dir} ${date} ${hour}${min}
      done
   done
done
