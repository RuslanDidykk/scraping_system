import os

from datetime import datetime
import textract

from database.DatabaseManager import DatabaseManager
from managers.RequestManager import RequestManager
from managers.SourceCodeManager import SourceCodeManager
from managers.Generator import Generator
from Logger import Logger
import binascii as ba

from helpers.timestamp_generator import generate_timestamp


class DataExtractor:
    DOMAIN = 'dubai.dubizzle.com'
    PROJECT_ID = 13

    PATH = 'phones/'

    def __init__(self):
        print self.DOMAIN
        self.logger = Logger(name='dubizzle_data_log')
        self.err_logger = Logger(name='err_dubizzle_data_log')
        self.request_manager = RequestManager()
        self.source_code_manager = SourceCodeManager()
        self.generator = Generator()
        self.db = DatabaseManager()

    def extract_data(self, url_data):
        print url_data
        url_id = url_data['id']
        url = url_data['url']
        listing_id = url_data['listing_id']

        data = {}

        response = self.request_manager.take_get_request(url)
        source_code = response['source_code']
        parsed_code = self.source_code_manager.parse_code(source_code)

        expired = parsed_code.find('div', {'id': 'expired-ad-message'})
        if expired is not None:
            #self.db.remove_listing(listing_id)
            self.db.set_url_inactive(url_id)
            self.err_logger.error("EXPIRED " + str(url_data))

            return
        elif response['status_code'] == 404:
            #self.db.remove_listing(listing_id)
            self.err_logger.error("404 " + str(url_data))

            self.db.set_url_inactive(url_id)

            return

        bread = parsed_code.find('span', {'id': 'browse_in_breadcrumb'})
        items = bread.findAll('div')
        try:
            year = parsed_code.find('img', attrs={'alt': 'Year'}).parent.text.replace('Year', '').strip()

            kilometres = parsed_code.find('img', attrs={'alt': 'Kilometers'}).parent.text.replace('Kilometers',
                                                                                                  '').strip().replace(
                ',', '').replace('.', '')
            color = parsed_code.find('img', attrs={'alt': 'Color'}).parent.text.replace('Color', '').strip()
            specs = parsed_code.find('img', attrs={'alt': 'Specs'}).parent.text.replace('Specs', '').strip()
            trim = parsed_code.find('img', attrs={'alt': 'Trim'}).parent.parent.text.replace('Trim', '').strip()
            if trim == 'Other':
                self.db.set_url_processed(url_id)
                return
            price = parsed_code.find('span', {'id': 'actualprice'}).text.replace(',', '').replace('.', '')
            model = items[-1].find('a').text.strip()
            marka = items[-2].find('a').text.strip()
            phone = self.extract_phone(parsed_code, id=url_id)
        except Exception as exc:
            self.err_logger.error(str(exc) + str(url_data))
            self.db.set_url_processed(url_id)

            return

        data['year'] = int(year)
        data['price'] = int(price)
        data['kilometres'] = int(kilometres)
        data['color'] = color
        data['specs'] = specs
        data['trim'] = trim
        data['model'] = model
        data['make'] = marka
        data['phone'] = phone

        self.db.insert_data(data=data, listing_id=listing_id, url=url, source=self.DOMAIN)
        self.db.set_url_processed(url_id)


    def update_data(self, url_data):
        timestamp = generate_timestamp()
        url_id = url_data['id']
        listing_id = url_data['listing_id']
        print listing_id
        url = url_data['url']
        first_timestamp = url_data['timestamp']
        time_dif = first_timestamp - datetime.strptime(timestamp,
                                                       "%Y.%m.%d:%H:%M:%S")
        time_dif = time_dif.days


        response = self.request_manager.take_get_request(url)
        source_code = response['source_code']
        parsed_code = self.source_code_manager.parse_code(source_code)
        expired = parsed_code.find('div', {'id': 'expired-ad-message'})
        if expired is not None:
            self.db.set_sold_status(listing_id=listing_id, days_for_selling=time_dif)
            #self.db.remove_listing(listing_id)
            self.db.set_url_inactive(url_id)
            print "updated"

            return

        elif response['status_code'] == 404:
            print 404, listing_id
            self.db.set_sold_status(listing_id=listing_id, days_for_selling=time_dif)
            #self.db.remove_listing(listing_id)
            self.db.set_url_inactive(url_id)
            print "updated"

            return

        try:
            price = parsed_code.find('span', {'id': 'actualprice'}).text.replace(',', '').replace('.', '')
        except:
            price = 0

        # days = self.__calc_days_on_market(listing_id)

        self.db.update_listing(listing_id=listing_id, price=int(price), days_on_market=time_dif)
        self.db.set_updated(listing_id=listing_id)
        print "updated"


    # def __calc_days_on_market(self, listing_id):
    #     days_on_market = self.db.get_car_data(listing_id).days_on_market
    #     if days_on_market is None:
    #         return 0
    #     days_on_market += 1
    #     return days_on_market



    def extract_phone(self, code, id):
        img = code.find('img', {'class': 'phone-num-img'})['src']

        ext = img.partition('data:image/')[2].split(';')[0]
        with open(self.PATH + str(id) + '.' + ext, 'wb') as f:
            f.write(ba.a2b_base64(img.partition('base64,')[2]))

        text = textract.process(self.PATH + str(id) + '.' + ext).replace(' ', '')

        if '+971' in text:
            pass
        else:
            text = '+971' + text

        os.remove(self.PATH + str(id) + '.' + ext)
        return text.strip()


if __name__ == '__main__':
    extractor = DataExtractor()
    db = DatabaseManager()

    #print extractor.update_data(db.get_one_url(listing_id=13728733))
