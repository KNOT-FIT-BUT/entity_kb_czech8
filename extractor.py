from utils import *

from wikiparser import *

#  EVENT (prefix: e)
#  ==========================================
#  + START DATE
#  + END DATE
#  + LOCATIONS (MULTIPLE VALUES)
#  + EVENT TYPE

#  ORGANIZATION (prefix: o)
#  ==========================================
#  + FOUNDED
#  + CANCELLED
#  + LOCATION
#  + ORGANIZATION TYPE
dataset = "../cswiki-latest-pages-articles.xml"


def dump_page(title):
    with open("samples/" + title.replace(" ", "_") + ".xml", "w") as file:
        page = list(get_pages_by_title(dataset, title))[0]
        file.write(page)


def load_page(title):
    with open(f'samples/{title.replace(" ", "_")}.xml', "r") as file:
        return Page(file.read())


for page in get_pages_by_title(dataset, ["Praha"]):
    print(page)
    input(page.link)
