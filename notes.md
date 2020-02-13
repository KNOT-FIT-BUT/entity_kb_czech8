# Wikipedia dumps
 * XML/TSV dumps of wikipedia
 * /mnt/minerva1/nlp/corpora/monolingual/czech/wikipedia/

# Wikipedia API - getting wikidata metadata about article using article name
 * Api request: `https://cs.wikipedia.org/w/api.php?action=query&prop=pageprops&ppprop=wikibase_item&redirects=1&titles=ARTICLE_NAME`

## Response format
 * Get the data in pure json format `https://cs.wikipedia.org/w/api.php?action=query&prop=pageprops&ppprop=wikibase_item&format=json&redirects=1&titles=UNESCO` 
 * This seems to work for all language types of wikipedia (e.g. `cs` and `en`, ...)

```json
{
    "batchcomplete": "",
    "query": {
        "pages": {
            "21786641": {
                "pageid": 21786641,
                "ns": 0,
                "title": "UNESCO",
                "pageprops": {
                    "wikibase_item": "Q7809"
                }
            }
        }
    }
}
```
 * We are interested in `data["query"]["pages"][id]["pageprops"]["wikibase_item"]`

# APIs
 * action=query - query data
 * prop=pageprops
 * titles=...  - Imporant! Article title to get data for
 * format=json - Easy to parse for python
 * You can make "claims" to wikipedia to get any data we need (for example "P569" is date of birth)

## Wikidata API
 * https://www.wikidata.org/w/api.php
 * Get data about entity: `https://www.wikidata.org/wiki/Special:EntityData/Q42.json`

## Wikipedia API
 * https://en.wikipedia.org/w/api.php
