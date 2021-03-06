from utils import readlines
import xml.etree.ElementTree as ET
from pprint import pprint
import dateparser
from datetime import datetime
from bs4 import BeautifulSoup


def get_cs_date(text):
    return dateparser.parse(text, languages=["cs"])


# Infobox attrbiutes

def location(infobox):
    pass


def place(infobox):
    pass


def duration(infobox):
    pass


def start_date(infobox):
    pass


def end_date(infobox):
    pass


def founded(infobox):
    pass


def cancelled(infobox):
    pass


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
            "MediaWiki:", "Šablona", "Portál:", "Soubor:", "Rejstřík:", "Hlavní strana")


def filter_titles(filtered):
    def wrapper(page_generator):
        def arg_wrapper(*args, **kwargs):
            for page in page_generator(*args, **kwargs):
                if not filtered_title(page.title):
                    yield page
        return arg_wrapper
    return wrapper


def filtered_title(title):
    for f in filtered:
        if f in title:
            return True
    return False


import mwparserfromhell as mw
import html
import re

comment = re.compile(r"<!--[^<>]*-->|")
br = re.compile(f"<br ?\/>")
small = re.compile(f"<\/?small>")


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
        if not page.infobox:
            return
        infobox = page.infobox
        print(page.title)
        for param in infobox.params:
            name = param.name.strip()
            val = param.value.strip()
            val = br.sub("\n", val)
            val = small.sub("", val)
            input(f"<{name}> <{val}>")
        # self._text = tags.sub(self._text, "")
        input()
        return

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


class Infobox:
    def __init__(self, infobox):
        self._infobox = infobox

        self._attrs = {}
        for param in self._infobox.params:
            name = str(param.name).strip()
            value = str(param.value).strip()
            value = comment.sub(value, "")
            self._attrs[name] = value
    
    @property
    def attrs(self):
        return self._attrs


class Page:
    def __init__(self, article_text):
        self._raw_text = article_text
        self._xml = ET.fromstring(article_text)
        self.page_id = int(self._xml.find(".//id").text)
        self.title = self._xml.find(".//title").text
        self.link = f"https://cs.wikipedia.org/wiki/{self.title}"
        self._text = self._xml.find(".//text").text
        if not self._text:
            self._text = ""
        self._text = html.unescape(self._text)

        self._infobox = None

        try:
            parsed_source = mw.parse(self._text, skip_style_tags=True)
            for template in parsed_source.ifilter_templates():
                if "Infobox" in template.name:
                    self._infobox = Infobox(template)
                    break
        except IndexError:
            pass

    @property
    def raw(self):
        return self._raw_text
        
    @property
    def infobox(self):
        return self._infobox

    def __str__(self):
        return f"<{self.title}>"


def get_pages_title_regex(filename, pattern):
    for page in get_pages(filename):
        if re.match(pattern, page.title):
            print(page)
            yield page


def get_pages_by_index(filename, indexes):
    if isinstance(indexes, range):
        indexes = list(indexes)

    for index, page in enumerate(get_pages(filename)):
        if not indexes:
            break

        if index in indexes:
            indexes.pop(indexes.index(index))
            yield page


def get_pages_by_title(filename, page_titles):
    for page in get_pages(filename):
        if not page_titles:
            break

        if page.title in page_titles:
            page_titles.pop(page_titles.index(page.title))
            yield page


@filter_titles(filtered)
def get_pages(filename):
    for page in iter_pages(filename):
        yield Page(page)


def iter_pages(filename):
    article = ""

    for line in readlines(filename):
        if "<page>" in line:
            article = ""

        article += line

        if "</page>" in line:
            yield article

        if not line:
            break
