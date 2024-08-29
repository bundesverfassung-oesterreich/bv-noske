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
for docpath in glob.glob("./data/tokenized_xml/*.xml"):
    # load doc
    print(f"processing {docpath}")
    xml_doc = TeiReader(docpath)
    # identifiy text to annotate: source elements (p, head, item)
    for source_element in xml_doc.any_xpath("//tei:body//tei:p|//tei:body//tei:head|//tei:body//tei:item"):
        if source_element.text is not None:
            tokens = nl_processor(source_element.text)
            source_element.text = "\n"
            for token in tokens:
                subel_name = "word" if token.pos_ != "PUNCT" else "pc"
                subel = teiMaker(
                    subel_name,
                    token.text,
                    pos=token.pos_,
                    lemma=token.lemma_
                )
                source_element.append(subel)
    print(f"writing {docpath}")
    xml_doc.tree_to_file(
        docpath.removesuffix(".xml") + "_pos.xml"
    )