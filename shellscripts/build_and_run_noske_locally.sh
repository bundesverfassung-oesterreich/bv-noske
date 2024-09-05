#!/bin/bash
# this script fetches new data, runs pos and morph tagging and then builds a container and runs it locally.
# you will need docker, a virtenv and some modules (they can be installed while running the script)
# good luck
#
# pulling some dependencies
#
read -p "Going to install python dependencies. Do you want to?" -n 1 -r user_input_value_1
echo
if [[ $user_input_value_1 =~ ^[YyJj]$ ]]
then
    pip install -r ./pyscripts/requirements.txt
fi
read -p "Going to install spacys de_dep_news_trf model (see: https://spacy.io/models/de/#de_dep_news_trf). This might take some time. Do you want to install it now?" -n 1 -r user_input_value_2
echo
if [[ $user_input_value_2 =~ ^[YyJj]$ ]]
then
    python -m spacy download de_dep_news_trf
fi
if [ ! -d "saxon" ]
then
    ./shellscripts/dl_saxon.sh
fi
echo -e "\nstarting the data part\n\n"
echo -e "\npulling the editions from the bv-data-github\n\n"
./shellscripts/fetch_editions.sh
echo -e "\nrun ant to apply some xslt to the xmls\n\n"
ant
echo -e "\nannotating the xmls\n\n"
python pyscripts/annotator.py
echo -e "\nconvert them to verticals\n\n"
python pyscripts/extract_verticals.py
echo -e "\nbuild the docker container\n\n"
./shellscripts/build_container.sh
echo -e "\nthe interface should be running at http://localhost:8080/crystal/\n\n"
./shellscripts/run_image.sh 