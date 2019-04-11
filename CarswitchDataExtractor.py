# coding=utf-8
import json
import urllib2

from datetime import datetime
from helpers.timestamp_generator import generate_timestamp

from database.DatabaseManager import DatabaseManager
from managers.RequestManager import RequestManager
from managers.SourceCodeManager import SourceCodeManager
from managers.Generator import Generator

class DataExtractor:

    DOMAIN = 'carswitch.com'
    PROJECT_ID = 15

    def __init__(self):
        self.request_manager = RequestManager()
        self.source_code_manager = SourceCodeManager()
        self.generator = Generator()
        self.db = DatabaseManager()

    def update_data(self, db_list_listings):
        list_cars = self.take_js_request()
        if len(list_cars) == 0:
            print 'Error Carswitch, len of list cars is 0'
            return

        list_expired_listing_id = []
        list_active_cars = []

        for listing in db_list_listings:
            checker = False
            for car in list_cars:
                active_car = car['inspectionID']
                if str(listing) == str(active_car):
                    list_active_cars.append({
                        'listing_id':active_car,
                        'price': car['salePrice']
                    })
                    checker = True
                    break

            if checker is False:
                list_expired_listing_id.append(listing)


        if len(list_expired_listing_id) > 0:
            for expired_id in list_expired_listing_id:
                self.db.set_sold_status(listing_id=expired_id, days_for_selling=0)
                print expired_id, 'Not Active'

        if len(list_active_cars) > 0:
            for active_car in list_active_cars:
                timestamp = self.get_info_about_car(active_car['listing_id']).timestamp
                days_on_market = self.calculate_days_on_market(first_timestamp=timestamp)
                self.db.update_listing(listing_id=active_car['listing_id'], price=active_car['price'], days_on_market=days_on_market)
                print active_car, 'Active'


    def take_js_request(self):
        data = '{"requests": [{"indexName": "All_Carswitch_Cars","params": "query=&' \
               'numericFilters=%2CinspectionStatus!%3D9%2Cpromoted!%3D1%2C(new!%3D1)&facetFilters=&page=&hitsPerPage=1200"}]}'

        url = 'http://ih3kc909gb-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20AngularJS%203.15.1&x-algolia-application-id=IH3KC909GB&x-algolia-api-key=0a4fcd3b57535f88c86172d5646d6787'

        try:
            response = urllib2.urlopen(
                url,
                data=data)
            data = json.loads(response.read())
            return data['results'][0]['hits']
        except Exception as e:
            print('Error: ' + str(e))
            return []

    def indicate_specs(self, specs_index):
        if specs_index == 0:
            return 'American'
        elif specs_index == 1:
            return 'GCC'
        elif specs_index == 2:
            return 'European'
        elif specs_index == 3:
            return 'Japanese'
        elif specs_index == 4:
            return 'Canadian'

    def extract_data(self, db_list_listings):
        list_cars = self.take_js_request()

        if len(list_cars) == 0:
            print 'Error Carswitch, len of list cars is 0'
            return

        print len(list_cars)

        for car in list_cars:
            data = {}

            listing_id = car['inspectionID']
            inspectionID = car['carID']

            if str(listing_id) in db_list_listings:
                print listing_id, 'Exist!'
                continue

            data['make'] = car['make']
            data['model'] = car['model']
            data['trim'] = car['displayTrim']
            data['year'] = car['year']
            data['kilometres'] = car['mileage']
            data['color'] = car['_highlightResult']['colorPaint']['value']
            data['specs'] = self.indicate_specs(car['GCCspecs'])
            data['price'] = car['salePrice']



            url = 'http://carswitch.com/uae/used-car/{0}/{1}/{2}/{3}-{4}'\
                .format(data['make'],data['model'],data['year'],listing_id,inspectionID)

            data['phone'] = ''

            print data

            self.db.insert_data(data=data, listing_id=listing_id, url=url, source=self.DOMAIN)


    def get_info_about_car(self, listing_id):
        car_obj = self.db.get_car_data(listing_id=listing_id)
        return car_obj


    def calculate_days_on_market(self, first_timestamp):
        timestamp = generate_timestamp()
        time_dif = first_timestamp - datetime.strptime(timestamp,
                                                       "%Y.%m.%d:%H:%M:%S")
        time_dif = time_dif.days

        return time_dif

    def main(self):
        list_listings = self.db.get_all_cars_listings(self.DOMAIN)
        self.extract_data(list_listings)
        self.update_data(list_listings)


if __name__ == '__main__':
    extractor = DataExtractor()
    # #extractor.get_info_about_car(19956)
    # db = DatabaseManager()
    # list = db.get_all_urls(extractor.DOMAIN)
    # extractor.update_data(list)
    extractor.main()



