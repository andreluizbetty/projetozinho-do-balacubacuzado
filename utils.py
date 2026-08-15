import openpyxl
import logging
import xml.etree.ElementTree as ET
import io


def xml_to_dict(element):
    """
    Converte um ElementTree em um dicionário preservando a hierarquia.
    """

    children = list(element)

    # nó folha
    if not children:
        return (element.text or "").strip()

    result = {}

    for child in children:
        value = xml_to_dict(child)

        # caso existam várias tags iguais (ex.: vários <item>)
        chield_tag = limpar_tag_xml(child.tag)

        if chield_tag in result:

            if not isinstance(result[chield_tag], list):
                result[chield_tag] = [result[chield_tag]]

            result[chield_tag].append(value)
        else:
            result[chield_tag] = value

    return result

def limpar_tag_xml(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag

def leitor_xml(file: str | io.BytesIO, filename=False):
    if isinstance(file, str):
        with open(file, "rb") as f:
            buffer = io.BytesIO(f.read())
    else:
        buffer = file

    try:
        tree = ET.parse(buffer)
        root = tree.getroot()
    except ET.ParseError as e:
        logger.error(f"XML malformado em {filename}: {e}")

    return {limpar_tag_xml(root.tag): xml_to_dict(root)}

def format_style(data_frame):
    openpyxl.load_workbook(data_frame)

def get_metadata_gmail_msg(msg):
    headers = msg["payload"]["headers"]

    metadata = {}

    for header in headers:
        metadata[header["name"]] = header["value"]
    return metadata

def get_logger(title):
    # 1. Configure the logging system
    logging.basicConfig(
        level=logging.INFO, # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),          # Print to console
            logging.FileHandler("report.log")    # Write to a file
        ])

    logging.getLogger("googleapiclient.discovery_cache").disabled = True

    # 2. Instantiate and use the logger
    log = logging.getLogger(title)
    return log

def verify_info_in_db(info):
    ...


if __name__ == '__main__':
    logger = get_logger("gmail_extractor")
    logger.info('oi')