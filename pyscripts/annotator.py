# needs: python -m spacy download de_dep_news_trf
import de_dep_news_trf
import glob
import lxml.etree as ET
import lxml.builder as builder
from acdh_tei_pyutils.tei import TeiReader

nsmap = {
    "tei" : "http://www.tei-c.org/ns/1.0"
}
teiMaker = builder.ElementMaker(
    namespace = "http://www.tei-c.org/ns/1.0",
    nsmap = nsmap
)
nl_processor = de_dep_news_trf.load()

# iterate over docs
data_dir = "./data"
editions_dir = f"{data_dir}/editions"
output_dir = f"{data_dir}/tokenized_xml"

for docpath in glob.glob(f"{editions_dir}/*.xml"):
    # load doc
    print(f"processing {docpath}")
    xml_doc = TeiReader(docpath)
    # identifiy text to annotate: source elements (p, head, item)
    for source_element in xml_doc.any_xpath("//tei:body//tei:p|//tei:body//tei:head|//tei:body//tei:item"):
        if source_element.text is not None:
            tokens = nl_processor(source_element.text)
            source_element.text = "\n"
            for token in tokens:
                subel_name = "w" if token.pos_ != "PUNCT" else "pc"
                subel = teiMaker(
                    subel_name,
                    token.text,
                    pos=token.pos_,
                    lemma=token.lemma_
                )
                source_element.append(subel)
    docname = docpath.split("/")[-1].removesuffix(".xml") + "_pos.xml"
    new_docpath = f"{output_dir}/{docname}"
    print(f"writing {new_docpath}")
    xml_doc.tree_to_file(
        new_docpath
    )