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
kb_schema = []
with open("HEAD-KB", "r") as file:
    kb_schema = file.read().split("\n")

event_matcher = SchemaMatcher("e", kb_schema[-2], "output/")
org_matcher = SchemaMatcher("o", kb_schema[-1], "output/")


def dump_page(title):
    for page in read_pages(dataset):
        if Page(page).title == title:
            with open("samples/" + title.replace(" ", "_") + ".xml", "w") as file:
                file.write(page)


def load_page(title):
    with open(f'samples/{title.replace(" ", "_")}.xml', "r") as file:
        return file.read()
        return Page(file.read())

# dump_page("Národně socialistická německá dělnická strana")
# page = load_page("Národně socialistická německá dělnická strana")
# p = Page(page)
# event_matcher.create_row(p)



for page in read_pages(dataset):
    p = Page(page)

    if p.invalid:
        continue

    event_matcher.create_row(p)
    org_matcher.create_row(p)
    continue

    if is_event(at):
        print(f"Event - {p}")
    elif is_organization(at):
        pass
        # print(f"Organization - {p}")
    else:
        pass
        # input(f"{yellow(str(p))}")
