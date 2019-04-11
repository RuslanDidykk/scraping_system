import os

from datetime import datetime
import textract

from Logger import Logger
from database.DatabaseManager import DatabaseManager
from managers.RequestManager import RequestManager
from managers.SourceCodeManager import SourceCodeManager
from managers.Generator import Generator
import binascii as ba

from helpers.timestamp_generator import generate_timestamp


class DataExtractor:
    DOMAIN = 'dubicars.com'
    PROJECT_ID = 13

    PATH = 'phones/'

    def __init__(self):
        print self.DOMAIN
        self.logger = Logger(name='dubicars_data_log')
        self.err_logger = Logger(name='err_dubicars_data_log')
        self.request_manager = RequestManager()
        self.source_code_manager = SourceCodeManager()
        self.generator = Generator()
        self.db = DatabaseManager()
        self.trim_list = self.db.get_trim_list()


    def extract_data(self, url_data):
        print url_data
        url_id = url_data['id']
        url = url_data['url']
        listing_id = url_data['listing_id']

        data = {}

        response = self.request_manager.take_get_request(url)
        source_code = response['source_code']
        parsed_code = self.source_code_manager.parse_code(source_code)

        expired = parsed_code.find('img', {'class': 'sold'})
        if expired is not None:
            self.db.set_url_inactive(url_id)
            self.err_logger.error("EXPIRED " + str(url_data))

            return
        elif response['status_code'] == 404:
            self.db.set_url_inactive(url_id)
            self.err_logger.error("404 " + str(url_data))

            return

        try:
            marka = self.__find_make(parsed_code)

            year = self.__find_year(parsed_code)
            kilometres = self.__find_km(parsed_code)
            color = self.__find_color(parsed_code)
            specs = self.__find_specs(parsed_code)
            price = self.__find_price(parsed_code)
            model = self.__find_model(parsed_code, make=marka)
            trim = self.__find_trim(parsed_code, marka=marka, model=model)
            if trim == 'Other':
                self.db.set_url_processed(url_id)
                self.db.set_url_inactive(url_id)
                return
            phone = self.__find_phone(parsed_code)
        except Exception as exc:
            self.err_logger.error(str(exc) + str(url_data))

            self.db.set_url_processed(url_id)
            return
        try:
            data['year'] = int(year)
            data['price'] = int(price)
            data['kilometres'] = int(kilometres)
            data['color'] = color
            data['specs'] = specs
            data['trim'] = trim
            data['model'] = model
            data['make'] = marka
            data['phone'] = phone
            print data
        except Exception as exc:
            self.err_logger.error(str(exc) + url_data)

            self.db.set_url_processed(url_id)
            self.db.set_url_inactive(url_id)

            return

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
        expired = parsed_code.find('img', {'class': 'sold'})
        if expired is not None:
            self.db.set_sold_status(listing_id=listing_id, days_for_selling=time_dif)
            #self.db.remove_listing(listing_id)
            self.db.set_url_inactive(url_id)
            return

        elif response['status_code'] == 404:
            print 404, listing_id
            self.db.set_sold_status(listing_id=listing_id, days_for_selling=time_dif)
            #self.db.remove_listing(listing_id)
            self.db.set_url_inactive(url_id)
            return

        try:
            price = self.__find_price(parsed_code)
        except:
            price = 0

        # days = self.__calc_days_on_market(listing_id)

        self.db.update_listing(listing_id=listing_id, price=int(price), days_on_market=time_dif)
        self.db.set_updated(listing_id=listing_id)


    def __find_make(self, code):
        try:
            make = self.__find_tag_by_text(code, text='Make:')
            return make
        except:
            return ''

    def __find_year(self, code):
        try:
            year = self.__find_tag_by_text(code, text='Year:')
            year_list = year.split()
            for year in year_list:
                try:
                    year = int(year)
                    return year
                except:
                    continue
        except:
            return ''

    def __find_km(self, code):
        try:
            km = self.__find_tag_by_text(code, text='Kilometers:')
            km = km.replace(",", "").replace(".", "").replace(" ","")
            return int(km)
        except:
            return 0

    def __find_color(self, code):
        try:
            color = self.__find_tag_by_text(code, text='Color:')
            return color.strip()
        except:
            return ''

    def __find_specs(self, code):
        try:
            specs = self.__find_tag_by_text(code, text='Specs:')
            return specs.strip()
        except:
            return ''

    # ============= TRIM ===============
    # =====
    def __generateEditedTrims(self, marka, trim):
        for example_trim in self.trim_list:
            try:
                if len(example_trim['trim']) <= 3:
                    continue
            except:
                continue

            if '-' in example_trim['trim']:
                if example_trim['make'] == marka:

                    edited_example_trim = example_trim['trim'].replace('-', ' ')
                    if edited_example_trim in trim:
                        print example_trim['trim']
                        return example_trim['trim']

                    edited_example_trim = example_trim['trim'].replace('-', ' ').title()
                    if edited_example_trim in trim:
                        print example_trim['trim']
                        return example_trim['trim']
        return ''

    def __find_trim(self, code, marka, model):
        try:
            to_return_trim = ''
            not_edited_trim = self.__find_tag_by_text(code, text='Model:').strip()
            trim = not_edited_trim.replace(model, '').strip()

            if len(trim.split()) == 0:
                print not_edited_trim, 'there is no Trim!!!!'
                return not_edited_trim.strip()

            for example_trim in self.trim_list:
                if example_trim['make'] == marka:
                    if example_trim['trim'] in trim:

                        if len(example_trim['trim']) <= 2:
                            if ' '+example_trim['trim']+' ' in ' '+trim+' ':
                                if len(example_trim['trim']) > len(to_return_trim):
                                    print example_trim['trim']
                                    to_return_trim = example_trim['trim']
                            continue

                        if len(example_trim['trim']) > len(to_return_trim):
                            print example_trim['trim']
                            to_return_trim = example_trim['trim']

            edited_trim = self.__generateEditedTrims(marka=marka, trim=trim)
            if len(edited_trim) > len(to_return_trim):
                return edited_trim
            elif to_return_trim == '':
                if len(trim.split()) <= 2 and len(trim.split()) > 0:
                    return trim
            else:
                return to_return_trim
        except:
            return ''
    # =====
    # ============= TRIM ===============

    def __find_model(self, code, make):
        try:
            breadcrumbs = code.findAll('span', {'typeof': 'v:Breadcrumb'})
            name = breadcrumbs[-1].text
            len_make = len(make.split())
            trim = name.split()[len_make:]
            trim = ' '.join(trim)
            return trim.strip()
        except Exception as exc:
            print exc
            return ''

    def __find_phone(self, code):
        try:
            phone = code.find('p', {'id':'contact-buttons'}).find('a')['data-reveal']
            phone = phone.replace('"', "").replace(" ", "").replace("[", "").replace("]", "")
            return phone.strip()
        except Exception as exc:
            print exc
            return ''

    def __find_price(self, code):
        try:
            price = code.find('strong', {'class': 'money'}).text
            price = price.replace('AED', "").replace(" ", "").\
                replace(",", "").\
                replace(".", "").\
                replace("-", "")
            return int(price)
        except:
            try:
                price = code.find('strong', {'class': 'money reduced'}).text
                price = price.replace('AED', "").replace(" ", ""). \
                    replace(",", ""). \
                    replace(".", ""). \
                    replace("-", "")
                return int(price)
            except:
                return 0

    def __find_tag_by_text(self, code, text):

        tag_with_text = code.find(text=text)
        needed_tag = tag_with_text.parent.find_next_sibling()
        return needed_tag.text


if __name__ == '__main__':
    extractor = DataExtractor()
    db = DatabaseManager()

    # print extractor.extract_data(db.get_all_urls(extractor.DOMAIN))
    # list = db.get_all_urls(extractor.DOMAIN)[200:250]
    # for url in list:
    #     extractor.extract_data(url)

    extractor.extract_data({'url': 'https://www.dubicars.com/2006-toyota-land-cruiser-vxr-v8-152617.html', 'listing_id': '152617', 'id': 221717L})


