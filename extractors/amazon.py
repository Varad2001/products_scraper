import logging
logging.basicConfig(filename='scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")


def get_titles_urls_on_page(page):
    print("Getting titles and urls of the sample items...")
    tags =  page.find_all('a', attrs={'class' : 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
    results = []
    for tag in tags:
        try :
            url = "https://www.amazon.com" + tag.get('href')
            title = tag.span.text
            results.append({'url' : url, 'title' : title})
        except Exception as e:
            print(e)
            continue
    print(f"{len(results)} sample items found on this page...")
    return results
