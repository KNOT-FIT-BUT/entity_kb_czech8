from utils import *

from wikiparser import read_pages, Page
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
dataset = ""


def dump_page(title):
    for page in read_pages(dataset):
        if Page(page).title == title:
            with open("samples/" + title.replace(" ", "_") + ".xml", "w") as file:
                file.write(page)


def load_page(title):
    with open(f'samples/{title.replace(" ", "_")}.xml', "r") as file:
        return Page(file.read())


for page in read_pages(dataset):
    p = Page(page)

    if p.invalid:
        continue

    if ":" in p.title:
        input(p)

    try:
        at = p.get_attributes(all_attributes)
    except Exception:
        pass
        # print(p)

    if is_event(at):
        print(f"Event - {p}")
    elif is_organization(at):
        print(f"Organization - {p}")
    else:
        pass
        # input(f"{yellow(str(p))}")
