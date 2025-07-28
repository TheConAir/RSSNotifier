from urllib.request import urlopen
from lxml import etree
from loguru import logger


class XMLContentParser:
    def __init__(self):
        pass

    def fetch_and_parse_xml(self, xml_url):
        """Fetch XML content from URL and return as string"""
        try:
            with urlopen(xml_url) as resp:
                tree = etree.parse(resp)
            root = tree.getroot()
            return etree.tostring(root, encoding="unicode")
        except Exception as e:
            logger.error(f"Failed to parse XML from {xml_url}: {e}")
            return ""

    def search_xml_content(self, xml_content, search_terms):
        """Search for terms in XML content and return found terms."""
        xml_low = (xml_content or "").lower()
        found_terms = []
        for term in search_terms:
            if term.lower() in xml_low:
                found_terms.append(term)
        return found_terms