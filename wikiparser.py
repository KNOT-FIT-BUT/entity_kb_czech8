from utils import readlines
import xml.etree.ElementTree as ET
from pprint import pprint
import dateparser
from datetime import datetime
from bs4 import BeautifulSoup


def get_cs_date(text):
    return dateparser.parse(text, languages=["cs"])



def get_attr(infobox, item):
    for val in infobox.params:
        if item in val.name.lower().strip():
            return val


# Infobox attrbiutes

def location(infobox):
    locations = []
    for item in ["místo"]:
        item = get_attr(infobox, item)

        for val in item.value.ifilter_text():
            if val.strip() not in ' \n\t,':
                input(locations)
                locations.append(val)
    
    return locations


def place(infobox):
    for item in ["sídlo"]:
        item = get_attr(infobox, item)

        for val in item.value.ifilter_text():
            if val.strip() not in ' \n\t,':
                return val


def duration(infobox):
    for item in ["trvání"]:
        if not infobox.has(item):
            continue

        text = infobox.get(item).value
        start, end = text.strip().split("–")
        start = get_cs_date(start)
        end = get_cs_date(end)
        return {"start": start, "end": end}


def start_date(infobox):
    return duration(infobox)["start"]


def end_date(infobox):
    return duration(infobox)["end"]


def founded(infobox):
    for item in ["datum založení", "vznik"]:
        item = get_attr(infobox, item)

        founded = item.value.filter_text()
        founded = "".join(map(str, founded))
        return get_cs_date(founded)


def cancelled(infobox):
        for item in ["datum rozpuštění", "zánik"]:
            item = get_attr(infobox, item)

            founded = item.value.filter_text()
            founded = "".join(map(str, founded))
            return get_cs_date(founded)


EXTRACTORS = {
    "LOCATION": location,
    "PLACE": place,
    "START_DATE": start_date,
    "END_DATE": end_date,
    "FOUNDED": founded,
    "CANCELLED": cancelled
}


# Article type matchers

filtered = ("Wikipedie:", "Kategorie:", "Nápověda:", "(rozcestník)", "Seznam",
            "MediaWiki:", "Šablona", "Portál:", "Soubor:", "Rejstřík:")

def filtered_title(title):
    for f in filtered:
        if f in title:
            return True
    return False


import mwparserfromhell as mw
import html


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
        values["ID"] = self._prefix

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
        if not infobox:
            return

        values = {}
        for attr_name, extractor in self._extractors.items():
            try:
                val = extractor(infobox)
                values[attr_name] = val
            except Exception:
                values[attr_name] = None
        
        if any(values.values()):
            print(page.title)
            print(self.format_row(values))
            # self._output_file.write(self.format_row(values))


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
        self._text = html.unescape(self._text)
        self._text = BeautifulSoup(self._text, features="html.parser").get_text()

        self._infobox = None

        try:
            parsed_source = mw.parse(self._text, skip_style_tags=True)
            for template in parsed_source.ifilter_templates():
                if "Infobox" in template.name:
                    self._infobox = template
                    break
        except IndexError:
            pass

    @property
    def infobox(self):
        return self._infobox

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
