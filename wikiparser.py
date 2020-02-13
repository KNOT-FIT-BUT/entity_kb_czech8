import re

from utils import readlines
import xml.etree.ElementTree as ET
from pprint import pprint
import dateparser
from datetime import datetime

heading = re.compile(r"=+[^=]+=+")
wikilink = re.compile(r"\[\[([^\[\]:]+)\:([^\[\]:]+)\]\]")
comment = re.compile(r"<!--[^-<>!]*-->")
flagicon = re.compile(r"{{[^{}\|]+\|[^{}\|]+}}")


def get_cs_date(text):
    return dateparser.parse(text, languages=["cs"])


def get_val(line):
    return line.split("=")[1].strip()


def clean(line):
    line = line.replace("[", "")
    line = line.replace("]", "")
    line = line.replace(";", " ")
    line = line.replace("&nbsp", "")
    return line


# Infobox attrbiutes

def location(infobox):
    for line in infobox.split('\n'):
        line = clean(line)

        if "sídlo" in line.lower():
            location = get_val(line)
            return location


def place(infobox):
    for line in infobox.split('\n'):
        line = clean(line)

        if "místo" in line.lower():
            places = get_val(line).split(',')
            return [p.strip() for p in places]


def duration(infobox):
    for line in infobox.split('\n'):
        line = clean(line)

        if "trvání" in line.lower():
            duration = get_val(line)
            start, end = duration.split("–")
            return {
                "start": get_cs_date(start),
                "end": get_cs_date(end)
            }
        elif "datum" in line.lower():
            line = clean(line)

def start_date(infobox):
    return duration(infobox)["start"]

def end_date(infobox):
    return duration(infobox)["end"]


def founded(infobox):
    for line in infobox.split('\n'):
        line = clean(line)

        if "vznik" in line.lower() or "založen" in line.lower():
            founded = get_val(line)
            return get_cs_date(founded)


def cancelled(infobox):
    for line in infobox.split('\n'):
        line = clean(line)

        if "rozpušt" in line.lower() or "zrušen" in line.lower() or "zánik" in line.lower():
            return get_cs_date(get_val(line))


EXTRACTORS = {
    "LOCATION": location,
    "PLACE": place,
    "START_DATE": start_date,
    "END_DATE": end_date,
    "FOUNDED": founded,
    "CANCELLED": cancelled
}


# Article type matchers

def is_event(attrs):
    return attrs.get("start") and attrs.get("end") and attrs.get("place")


def is_organization(attrs):
    return attrs.get("founded") and attrs.get("location")


filtered = ("Wikipedie:", "Kategorie:", "Nápověda:", "(rozcestník)", "Seznam",
            "MediaWiki:", "Šablona", "Portál:", "Soubor:", "Rejstřík:")

def filtered_title(title):
    for f in filtered:
        if f in title:
            return True
    return False


class SchemaMatcher:
    def __init__(self, prefix, schema, output_dir):
        self._prefix = prefix
        schema = schema.replace("{m}", "")
        schema = schema.replace("{e}", "")
        schema = schema.split(" ")
        name = schema.pop(0)
        name = name.replace("<", "")
        self._name, first_attr = name.split(">")
        attrs = schema + [first_attr]
        self._attrs = list(filter(bool, attrs))
    
        self._extractors = {}
        for attr in self._attrs:
            self._extractors[attr] = EXTRACTORS.get(attr, lambda infobox: None)

        self._output_file = open(output_dir+self._name+".tsv", "w")

    def format_row(self, values):
        row = ""
        values["TYPE"] = self._prefix

        for attr in self._attrs:
            val = values[attr]
            if isinstance(val, datetime):
                val = val.strftime("%Y-%m-%d")
            elif val is None:
                val = "?"
            row += f"{val}\t"
        
        row += "\n"

        return row

    def create_row(self, page):
        infobox = page.infobox
        values = {}
        for attr_name, extractor in self._extractors.items():
            try:
                val = extractor(infobox)
                values[attr_name] = val
            except Exception:
                values[attr_name] = None
        
        if any(values.values()):
            # input(values)
            # input(self.format_row(values))
            self._output_file.write(self.format_row(values))

class Page:
    def __init__(self, article_text):
        self._xml = ET.fromstring(article_text)
        self.page_id = int(self._xml.find(".//id").text)
        self.title = self._xml.find(".//title").text
        self.invalid = filtered_title(self.title)
        if self.invalid:
            return
        self._text = self._xml.find(".//text").text
        if not self._text:
            self._text = ""
        self._text = self._text.replace("<br />", "\n")
        self._sections = None
        self._infobox = self.get_infobox()
        self._infobox = flagicon.sub("", self._infobox)

    @property
    def infobox(self):
        return self._infobox

    def get_infobox(self):
        infobox = ""

        in_infobox = False
        for line in self._text.split('\n'):
            t = self.line_type(line)
            if t == "infobox_start":
                in_infobox = True
                continue
            elif t == "infobox_end":
                in_infobox = False

            if in_infobox:
                infobox += line + '\n'

        return infobox
    
    def line_type(self, line):
        line = line.strip()

        if line.startswith("*"):
            return "bullet"
        elif line.startswith("="):
            return "heading"
        elif line.startswith("<"):
            return "html"
        elif line.startswith("{{Infobox"):
            return "infobox_start"
        elif line.startswith("}}"):
            return "infobox_end"

    def __str__(self):
        return f"<{self.title}>"


def read_pages(filename):
    article = ""

    for line in readlines(filename):
        if "<page>" in line:
            article = ""

        article += line

        if "</page>" in line:
            yield article

        if not line:
            break
