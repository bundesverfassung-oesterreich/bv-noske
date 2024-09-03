import de_dep_news_trf
import glob
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


data_dir = "./data"
editions_dir = f"{data_dir}/editions"
output_dir = f"{data_dir}/tokenized_xml"
source_elements_xpath = "//tei:body//tei:p|//tei:body//tei:head|//tei:body//tei:item"

def write_new_doc(xml_doc: TeiReader, docpath):
    docname = docpath.split("/")[-1].removesuffix(".xml") + "_pos.xml"
    new_docpath = f"{output_dir}/{docname}"
    print(f"writing {new_docpath}")
    xml_doc.tree_to_file(
        new_docpath
    )

def tag_doc(docpath: str, source_elements_xpath: str):
    # load doc
    print(f"processing {docpath}")
    xml_doc = TeiReader(docpath)
    # identifiy text to annotate: source elements
    source_elements = xml_doc.any_xpath(
        source_elements_xpath
    )
    for source_element in source_elements:
        if source_element.text is not None:
            tokens = nl_processor(source_element.text)
            source_element.text = "\n"
            for token in tokens:
                if token.pos_ == "PUNCT":
                    subel = teiMaker.pc(
                        token.text,
                        pos=token.pos_
                    )
                else:
                    subel = teiMaker.w(
                        token.text,
                        pos=token.pos_,
                        lemma=token.lemma_.strip(),
                        # keys are so far (from testing) 
                        # ['Case', 'Definite', 'Degree', 'Foreign', 'Gender', 'Mood', 'Number', 'Person', 'Poss', 'PronType', 'Reflex', 'Tense', 'VerbForm']
                        # could I extract the attrib in mk_verticals 
                        ana=token.morph.__str__()
                    )
                source_element.append(subel)
    write_new_doc(xml_doc, docpath)

if __name__ == "__main__":
    for docpath in glob.glob(f"{editions_dir}/*.xml"):
        tag_doc(docpath, source_elements_xpath)