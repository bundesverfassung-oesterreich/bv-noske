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

# elements which child elements get processed and 
# that get converted into vertical structures
RELEVANT_ELEMENTS = [
    "head",
    "p",
    "lg",
    "titlePage",
    "item",
    "label",
    "note",
    "list"
]
# attribs extracted from structures
RELEVANT_ELEMENTS_ATTRIBUTES = [
    "xml:id"
]

# elements which child elements get processed and 
# that DON'T get converted into vertical structures
CONTAINER_ELEMENTS = [
    "div"
]

#tags considered tokens
TOKEN_TAGS = [
    "w",
    "pc"
]

TOKEN_TAG_ATTRIBUTES = [
    "@lemma",
    "@pos"
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


def extract_structure_tag(element_name,  attributes:dict={}, open=False) -> str:
    if attributes and not open:
        input("You are trying to add attributes to a closing structure tag. Stop it!")
    if open:
        return f"<{element_name}>"
    else:
        return f"</{element_name}>"

def write_to_tsv(output_file: str, verticals: str) -> None:
    with open(output_file, "a", encoding="utf-8") as f:
        f.writelines(verticals)


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
        f'attrs="word lemma type">'
    ])

def handle_ana_attribute(element)->str:
    values = []
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
            values.append("")
        else:
            values.append(returnvalue)
    return "\t".join(values)

def get_vertical_for_atomic(element, element_name:str)-> str:
    text = element.text.strip()
    if element_name == "pc":
        return "<g/>\n" + text
    elif element_name == "w":
        token_attribs = [text]
        for attrib in TOKEN_TAG_ATTRIBUTES:
            val = element.xpath(f"{attrib}")
            string_val = val[0] if val else ""
            token_attribs.append(string_val)
        token_attribs.append(
            handle_ana_attribute(
                element
            )
        )
        return "\t".join(token_attribs)
    else:
        input(f"unexpected element {element_name}")
        return ""

def get_attributes_from_structure(element):
    return_dict = {}
    for attrib in RELEVANT_ELEMENTS_ATTRIBUTES:
        val = element.xpath(f"./@{attrib}", namespaces=NS)
        return_dict[attrib] = val

def extract_subelement_verticals(verticals: list, current_root) -> list:
    if len(current_root) == 0:
        element_name = current_root.xpath("local-name()").removeprefix("{http://www.tei-c.org/ns/1.0}")
        if element_name in TOKEN_TAGS:
            vertical = get_vertical_for_atomic(current_root, element_name)
            #print(vertical)
            verticals.append(vertical)
        return verticals
    else:
        for element in current_root:
            element_name = element.xpath("local-name()").removeprefix("{http://www.tei-c.org/ns/1.0}")
            if element_name in RELEVANT_ELEMENTS:
                # if element_name == "p":
                #     input(element_name)
                attributes= get_attributes_from_structure(element)
                open_structure = extract_structure_tag(
                    element_name,
                    attributes,
                    open=True
                )
                verticals.append(open_structure)
                for subelement in element:
                    #input(subelement)
                    verticals = extract_subelement_verticals(
                        verticals=verticals,
                        current_root=subelement
                    )
                #input(element_name)
                close_structure = extract_structure_tag(
                    element_name,
                    open=False
                )
                verticals.append(close_structure)
                # if element_name == "p":
                #     input(verticals)
            elif element_name in CONTAINER_ELEMENTS:
                for subelement in element:
                    verticals = extract_subelement_verticals(
                        verticals= verticals,
                        current_root= subelement
                    )
            elif element_name in TOKEN_TAGS:
                vertical = get_vertical_for_atomic(element, element_name)
                #print(vertical)
                verticals.append(vertical)
            else:
                input(element_name)
    #print(verticals)
    return verticals


def create_verticals(doc: TeiReader, output_filename) -> None:
    verticals = []
    docstructure_opening = mk_docstructure_open(doc)
    verticals.append(docstructure_opening)
    roots = doc.any_xpath("//tei:body")
    for root in roots:
        verticals += extract_subelement_verticals(
            verticals= [],
            current_root= root
        )
    docstructure_closing = "</doc>\n"
    verticals.append(docstructure_closing)
    verticals_str = "\n".join(verticals)
    output_file = os.path.join(output_filepath, "verticals", f"{output_filename}.tsv")
    write_to_tsv(output_file, verticals_str)


def process_xml_files(input_dir: str, output_dir: str) -> None:
    create_dirs(output_dir)
    xml_files = load_xml_files(input_dir)
    for xml_file in tqdm(xml_files, total=len(xml_files)):
        doc = TeiReader(xml_file)
        filename = os.path.splitext(os.path.basename(xml_file))[0].replace(".xml", "")
        print(filename)
        create_verticals(doc, filename)


if __name__ == "__main__":
    input_filepath = INPUT_PATH
    output_filepath = OUTPUT_PATH
    process_xml_files(input_filepath, output_filepath)
