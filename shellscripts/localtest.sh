#!/bin/bash
read -p "Going to install python dependencies. Do you want to?" -n 1 -r user_input_value_1
echo
if [[ ! $user_input_value_1 =~ ^[YyJj]$ ]]
then
    pip install -r ./pyscripts/requirements.txt
fi
read -p "Going to install spacys de_dep_news_trf model (see: https://spacy.io/models/de/#de_dep_news_trf). This might take some time. Do you want to install it now?" -n 1 -r user_input_value_2
echo
if [[ ! $user_input_value_2 =~ ^[YyJj]$ ]]
then
    python -m spacy download de_dep_news_trf
fi
./shellscripts/fetch_editions.sh
./shellscripts/dl_saxon.sh 
ant
python pyscripts/annotator.py
python pyscripts/mk_verticals.py
./shellscripts/build_container.sh
echo "check the interface at http://localhost:8080/crystal/"
./shellscripts/run_image.sh 