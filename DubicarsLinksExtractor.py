import json

from database.DatabaseManager import DatabaseManager
from managers.RequestManager import RequestManager
from managers.SourceCodeManager import SourceCodeManager
from managers.Generator import Generator

class LinksExtractor:

    DOMAIN = 'dubicars.com'
    PROJECT_ID = 13

    def __init__(self):
        self.request_manager = RequestManager()
        self.source_code_manager = SourceCodeManager()
        self.generator = Generator()
        self.db = DatabaseManager()


    def __createUrl(self, templateUrl, page):
        #url = templateUrl[:-1] + str(page)
        url = templateUrl.format(page)
        return url

    def findLinks(self, sourceCode):
        links = []
        status = True
        sourceCode = sourceCode.find('section', {'data-item-hash': "search"})
        listOfTags = sourceCode.findAll('li')
        for block in listOfTags:
            try:
                data = block['data-sp-item']
            except:
                continue
            data = json.loads(data)
            listing_id = data['id']
            try:
                km = int(data['km'])
            except:
                km = 101

            if km < 100:
                continue

            tag_a = block.find('a')
            href = tag_a['href']
            links.append({'url':href,
                          'listing_id':listing_id})
        return {'links':links, 'status': status}


    def main(self, sourceUrl):
        page = 1
        while True:
            url = self.__createUrl(sourceUrl, page)
            print url
            try:
                response = self.request_manager.take_get_request(url, proxy_using=False)
            except Exception as exc:
                print exc
                break
            parseSourceCode = self.source_code_manager.parse_code(response['source_code'])

            links_data = self.findLinks(parseSourceCode)
            links = links_data['links']


            self.db.insert_urls(urls_list=links, source=self.DOMAIN)

            if self.isLastPage(parseSourceCode):
                print "last"
                break
            page += 1

    def find_last_page(self, code):
        pagination = code.find('div', {'class':'paging '})
        pages = pagination.findAll('a')
        last_page = int(pages[-2].text)
        print last_page
        return last_page

    def isLastPage(self, code):
        next_page = code.find('a', {'class':'next'})
        if next_page is None:
            return True
        else:
            return False


# if __name__ == '__main__':
#
#     TEMPL_URL = 'https://uae.dubizzle.com/motors/used-cars/?page={}&seller_type=OW&is_search=1&is_basic_search_widget=0&places__id__in=--&ot=desc&o=2'
#     LinksExtractor().main(TEMPL_URL, ['13740106'])

if __name__ == '__main__':
    url = 'https://www.dubicars.com/search?ajax=true&view=&o=&l=&ma=&mo=0&c=new-and-used&pf=&pt=&yf=&yt=&kf=10000&kt=&b=&co=&ci=&s=&gi=&page={}'
    LinksExtractor().main(url)


