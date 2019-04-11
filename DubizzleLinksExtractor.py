
from database.DatabaseManager import DatabaseManager
from managers.RequestManager import RequestManager
from managers.SourceCodeManager import SourceCodeManager
from managers.Generator import Generator

class LinksExtractor:

    DOMAIN = 'dubai.dubizzle.com'
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
        listOfTags = sourceCode.findAll('div', {'class': 'listing-item'})
        for block in listOfTags:
            listing_id = block['data-id']
            km = self.__find_km(block)
            exist = self.__check_url(listing_id)

            # if exist:
            #     status = False
            #     break
            if km < 100:
                continue

            tag_a = block.find('a')
            href = tag_a['href']
            links.append({'url':href,
                          'listing_id':listing_id})
        return {'links':links, 'status': status}

    def __find_km(self, code):
        try:
            km = code.find(text='Kilometers: ').parent.text.replace('Kilometers: ', '')
            km = km.replace(',', '')
            km = int(km)
        except AttributeError:
            km = 0
        return km

    def __check_url(self, listing_id):

        if listing_id in self.existing_urls:
            return True
        else:
            return False

    def main(self, sourceUrl, existing_urls):
        self.existing_urls = existing_urls
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
            status = links_data['status']


            self.db.insert_urls(urls_list=links, source=self.DOMAIN)
            if not status:
                print "Exist"
                break
            if self.isLastPage(parseSourceCode):
                print "last"
                break
            page += 1

    def find_last_page(self, code):
        pagination = code.find('div', {'class':'paging '})
        pages = pagination.findAll('a')
        last_page = int(pages[-2].text)
        print  last_page
        return last_page

    def isLastPage(self, code):
        next_page = code.find('a', {'id':'next_page'})
        if next_page is None:
            return True
        else:
            return False

    def generate_search_urls(self):
        TEMPLATE_URL = 'https://uae.dubizzle.com/motors/used-cars/?page={0}&price__gte={1}&price__lte={2}&year__gte={3}&year__lte={4}&kilometers__gte=&kilometers__lte=&seller_type=&keywords=&is_basic_search_widget=0&is_search=1&added__gte=&auto_agent='

        list_links = []
        list_links.append(
            'https://uae.dubizzle.com/motors/used-cars/?page={}&price__gte=&price__lte=&year__gte=&year__lte=2001&kilometers__gte=&kilometers__lte=&seller_type=&keywords=&is_basic_search_widget=0&is_search=1&added__gte=&auto_agent=')
        for year in range(2002, 2007, 2):
            for price in range(0, 45001, 15000):
                max_price = price + 15000
                if price == 45000:
                    max_price = 10000000
                list_links.append(TEMPLATE_URL.format('{}', price, max_price, year, year + 1))
        for year in range(2008, 2019):
            for price in range(0, 160001, 10000):
                max_price = price + 10000
                if price == 160000:
                    max_price = 10000000
                list_links.append(TEMPLATE_URL.format('{}', price, max_price, year, year))
        return list_links

    def extract_urls(self):
        urls = self.generate_search_urls()
        for url in urls:
            self.main(url, [])


# if __name__ == '__main__':
#
#     TEMPL_URL = 'https://uae.dubizzle.com/motors/used-cars/?page={}&seller_type=OW&is_search=1&is_basic_search_widget=0&places__id__in=--&ot=desc&o=2'
#     LinksExtractor().main(TEMPL_URL, ['13740106'])

if __name__ == '__main__':
    LinksExtractor().extract_urls()


