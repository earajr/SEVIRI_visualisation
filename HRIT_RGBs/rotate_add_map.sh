#!/bin/bash

MSG_dir=$MSGsat
img_dir="$MSG_dir/HRIT_RGBs/images"
dest_img_dir="$MSG_dir/HRIT_RGBs/Senegal_20200905_images"
map_overlay="$MSG_dir/HRIT_RGBs/map_overlay.png"


if [ ! -d ${dest_img_dir} ]
then
   mkdir ${dest_img_dir}
fi

for fil in ${img_dir}/*.png
do
   fil_name=$( basename ${fil} )
   convert ${fil} -rotate 180 ${dest_img_dir}/${fil_name}
   composite ${map_overlay} ${dest_img_dir}/${fil_name} ${dest_img_dir}/${fil_name}
   convert ${dest_img_dir}/${fil_name} -crop 500x500+1100+1100 ${dest_img_dir}/${fil_name}
   rm ${fil}
done
