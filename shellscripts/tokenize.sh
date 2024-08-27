xml_files="data/editions/bv_doc_id__*.xml"
xsl_script="xslt/tokenize.xslt"
for file in $xml_files; do
    new_filename=`printf '%s\n' "${file%.xml}_tokenized.xml"`
    echo "creating tokens in $file"
    java -jar ./saxon/saxon9he.jar -o:$new_filename -s:$file $xsl_script
    if [ $? != 0 ]; then
        echo "error while creating navigation anchor in $file"
        exit 1
    fi
done
