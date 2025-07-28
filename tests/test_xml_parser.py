import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from scraper.xml_parser import XMLContentParser


def test_search_xml_content_case_insensitive():
    parser = XMLContentParser()
    xml_content = "<root><item>Alpha Beta</item></root>"
    terms = ["alpha", "BETA", "Gamma"]
    assert parser.search_xml_content(xml_content, terms) == ["alpha", "BETA"]
