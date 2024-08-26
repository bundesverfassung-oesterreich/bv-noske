#!/bin/bash
# # def vars
temp_path="./tmp_tmp/"
zip_file="${temp_path}main.zip"
fetched_editions_path="${temp_path}bv-data-main/data/editions/"
target_editions_path="./data/editions/"
# # prepare folder structure
rm -rf $temp_path
mkdir $temp_path
# # fetch data from repo, unzip, and move to destination
wget https://github.com/bundesverfassung-oesterreich/bv-data/archive/refs/heads/main.zip -O $zip_file
unzip $zip_file -d $temp_path
# # check for target dir
if [ ! -d "$target_editions_path" ]; then mkdir "$target_editions_path"; fi
find $fetched_editions_path -name "*.xml" -exec cp "{}" "$target_editions_path" \;
# # remove temp folder
rm -rf $temp_path