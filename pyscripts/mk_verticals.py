# creates verticals from xml to import data to NoSketch engine

import os
import glob
import shutil
import datetime
from tqdm import tqdm
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import extract_fulltext
from typing import Generator, Any
from collections import deque

morph_keys = [
    'Case', 
    'Definite', 
    'Degree', 
    'Foreign', 
    'Gender', 
    'Mood', 
    'Number', 
    'Person', 
    'Poss', 
    'PronType', 
    'Reflex', 
    'Tense', 
    'VerbForm'
]

INPUT_PATH = "./data/tokenized_xml"
OUTPUT_PATH = "./data"

NS = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace"
}

STRUCTURES = [
    "tei:head",
    "tei:p",
    "tei:lg",
    "tei:titlePage",
    "tei:item",
    "tei:label",
    "tei:div"
]

STRUCUTRE_ATTRIBUTES = [
    "@xml:id"
]

TAGS = [
    "tei:w",
    "tei:pc"
]

TAG_ATTRIBUTES = [
    "@lemma",
    "@pos"
]

BLACKLIST = [
    "{http://www.tei-c.org/ns/1.0}orig",
    "{http://www.tei-c.org/ns/1.0}del"
]


def yearToDecade(year) -> int:
    year = int(year)
    return year - year % 10


def weekdayToString(weekday) -> str:
    if weekday == 0:
        return "Monday"
    elif weekday == 1:
        return "Tuesday"
    elif weekday == 2:
        return "Wednesday"
    elif weekday == 3:
        return "Thursday"
    elif weekday == 4:
        return "Friday"
    elif weekday == 5:
        return "Saturday"
    elif weekday == 6:
        return "Sunday"


def dateToWeekday(year, month, day) -> int:
    return datetime.date(int(year), int(month), int(day)).weekday()


def punctuation_normalized(input_glob):
    for file in glob.glob(input_glob):
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
            text = text.replace("\\.", "<g/>\n\\.")
            text = text.replace(",", "<g/>\n,")
            text = text.replace(";", "<g/>\n;")
            text = text.replace(":", "<g/>\n:")
            text = text.replace("!", "<g/>\n!")
            text = text.replace("?", "<g/>\n?")
            text = text.replace("(", "<g/>\n(")
            text = text.replace(")", "<g/>\n)")
            text = text.replace("[", "<g/>\n[")
            text = text.replace("]", "<g/>\n]")
            text = text.replace("=", "<g/>\n=")
        with open(file, "w", encoding="utf-8") as f:
            f.write(text)


def create_dirs(output_dir: str) -> None:
    output_dir = os.path.join(output_dir, "verticals")
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=True)


def load_xml_files(input_dir: str) -> list:
    return glob.glob(os.path.join(input_dir, "*.xml"))


def list_to_xpaths(items: list) -> str:
    xpath = ""
    for item in items:
        xpath += f".//{item}|"
    return xpath[:-1]


def extract_structure(doc: TeiReader, structures: list) -> list:
    return doc.any_xpath(list_to_xpaths(structures))


def extract_tags_from_structures(doc_structures: list, tags: list) -> Generator[Any, Any, Any]:
    for structure in doc_structures:
        tag_nodes = structure.xpath(list_to_xpaths(tags), namespaces=NS)
        yield tag_nodes

def rehandle_ana_attributes(element):
    returned_values = []
    ana = element.xpath("@ana[normalize-space()!='']")
    existing_values = {}
    if ana:
        ana = ana[0]
        for key_val in ana.split("|"):
            key, val = key_val.split("=")
            existing_values[key.strip()] = val.strip()
    for morph_key in morph_keys:
        returnvalue = existing_values.get(morph_key)
        if returnvalue is None:
            returned_values.append("")
        else:
            returned_values.append(returnvalue)
    return returned_values


def extract_tag_attributes(doc_tags: list, tag_attributes: list) -> Generator[Any, Any, Any]:
    for tag in doc_tags:
        if isinstance(tag, list):
            for subtag in tag:
                match subtag.tag:
                    case "{http://www.tei-c.org/ns/1.0}pc":
                        yield [""]
                    case _:
                        tag_attributes_text = subtag.xpath(list_to_xpaths(tag_attributes), namespaces=NS)
                        tag_attributes_text += rehandle_ana_attributes(subtag)
                        yield tag_attributes_text
        else:
            match tag.tag:
                case "{http://www.tei-c.org/ns/1.0}pc":
                    yield [""]
                case _:
                    tag_attributes_text = tag.xpath(list_to_xpaths(tag_attributes), namespaces=NS)
                    tag_attributes_text += rehandle_ana_attributes(subtag)
                    yield tag_attributes_text


def extract_text_from_tags(doc_tags: list, blacklist: list) -> Generator[Any, Any, Any]:
    for tag in doc_tags:
        if isinstance(tag, list):
            for subtag in tag:
                text = extract_fulltext(subtag, blacklist)
                match subtag.tag:
                    case "{http://www.tei-c.org/ns/1.0}pc":
                        yield "<g/>\n" + text
                    case _:
                        yield text
        else:
            text = extract_fulltext(subtag, blacklist)
            match tag.tag:
                case "{http://www.tei-c.org/ns/1.0}pc":
                    yield "<g/>\n" + text
                case _:
                    yield text


def exhaust(generator) -> list:
    return deque(generator)


def write_to_tsv(output_file: str, data_text: list, data_attributes: list, doc_structure_open: str) -> None:
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(doc_structure_open)
        for idx, text in enumerate(data_text) if data_text else []:
            f.write(text + "\t" + "\t".join(data_attributes[idx]) + "\n")
        f.write("</doc>\n")


def mk_docstructure_open(doc: TeiReader) -> str:
    not_before = doc.any_xpath("//tei:msDesc/tei:history/tei:origin/@notBefore-iso")[0].strip()
    not_after = doc.any_xpath("//tei:msDesc/tei:history/tei:origin/@notAfter-iso")[0].strip()
    doc_year = not_before.split("-")[0].strip()
    doc_title = doc.any_xpath("//tei:titleStmt/tei:title/text()")[0].strip()
    doc_id = doc.any_xpath("//tei:TEI/@xml:id")[0].strip()
    xml_status = doc.any_xpath("//tei:revisionDesc/@status")[0].strip()
    doc_type = doc.any_xpath("//tei:physDesc/tei:objectDesc/@form")[0].strip()
    doc_text_type = doc.any_xpath("//tei:text/@type")[0].strip()
    dataset = doc.any_xpath("//tei:idno[@type='bv_data_set']/text()")[0].strip()
    if dataset == "Datenset A":
        dataset = "Gesetzestexte & Entwürfe"
    elif dataset == "Datenset B":
        dataset = "Sitzungsprotokolle"
    else:
        dataset = "sonstige"
    return " ".join([
        f'<doc id="{doc_id}"',
        f'document_title="{doc_title}"',
        f'created_not_before="{not_before}"',
        f'created_not_after="{not_after}"',
        f'creation_year="{doc_year}"', 
        f'state_of_correction="{xml_status}"',
        f'document_type="{doc_type}"',
        f'text_type="{doc_text_type}"',
        f'dataset="{dataset}"',
        f'attrs="word lemma type">\n'
    ])


def create_verticals(doc: TeiReader, output_filename) -> None:
    doc_structures = extract_structure(doc, STRUCTURES)
    docstructure_open = mk_docstructure_open(doc)
    doc_tags = exhaust(extract_tags_from_structures(doc_structures, TAGS))
    doc_tag_attributes = exhaust(extract_tag_attributes(doc_tags, TAG_ATTRIBUTES))
    doc_text = exhaust(extract_text_from_tags(doc_tags, BLACKLIST))
    output_file = os.path.join(output_filepath, "verticals", f"{output_filename}.tsv")
    write_to_tsv(output_file, doc_text, doc_tag_attributes, docstructure_open)


def process_xml_files(input_dir: str, output_dir: str) -> None:
    create_dirs(output_dir)
    xml_files = load_xml_files(input_dir)
    for xml_file in tqdm(xml_files, total=len(xml_files)):
        doc = TeiReader(xml_file)
        filename = os.path.splitext(os.path.basename(xml_file))[0].replace(".xml", "")
        create_verticals(doc, filename)


if __name__ == "__main__":
    input_filepath = INPUT_PATH
    output_filepath = OUTPUT_PATH
    process_xml_files(input_filepath, output_filepath)
