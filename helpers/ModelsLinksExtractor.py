# coding=utf-8

from database.DatabaseManager import DatabaseManager
from managers.RequestManager import RequestManager
from managers.SourceCodeManager import SourceCodeManager
from managers.Generator import Generator

from helpers.hash_generator import generate_controll_summ

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class ModelsLinksExtractor:

    DOMAIN = 'carsguide.com.au'
    # PROJECT_ID = 13

    def __init__(self):
        self.request_manager = RequestManager()
        self.source_code_manager = SourceCodeManager()
        self.generator = Generator()
        self.db = DatabaseManager()
        self.hash_generator = generate_controll_summ

    def getAllMarks(self, parse_code):
        main_div = parse_code.find('div',{'class': 'panel-body'})
        links_marks = main_div.findAll('a')

        to_return_links = []
        for link in links_marks:
            to_return_links.append('https://www.carsguide.com.au'+link['href'])

        return to_return_links

    def getAllModels(self, parse_code):
        try:
            ul = parse_code.find('ul', {'class': 'cg-model-model-list clearfix'})
            list_li = ul.findAll('li', {'class': 'col-lg-2 col-sm-3 col-md-3 col-xs-6'})

            for li in list_li:
                self.list_models_links.append('https://www.carsguide.com.au'+li.find('a')['href'])
        except:
            pass

        try:
            ul = parse_code.find('ul', {'class': 'cg-model-other-model-list clearfix'})
            list_teg_a = ul.findAll('a')

            for teg_a in list_teg_a:
                links = 'https://www.carsguide.com.au'+teg_a['href']
                if links not in self.list_models_links:
                    self.list_models_links.append(links)
        except:
            pass

    def getPricingGuide(self, parse_code, url):
        try:
            div = parse_code.find('div', {'class': 'makeModelYear--text'})
            price_guide = div.find('a', {'data-gtm-category': 'pricing and spec'})['href']
            print 'https://www.carsguide.com.au'+price_guide
            return 'https://www.carsguide.com.au'+price_guide
        except Exception as exc:
            print exc
            print url+'/price'
            return url+'/price'

    def getAllYearList(self, parse_code, url):
        table = parse_code.find('table', {'id': 'pricingSpecsTable'})
        try:
            list_rows = table.findAll('tr', {'class': 'cgNativeTable--row'})

            print len(list_rows)
            for row in list_rows:
                try:
                    link = url+'/'+row['data-year']
                    if link not in self.list_year_links:
                        self.list_year_links.append(link)
                except Exception as exc:
                    print exc
                    continue
        except Exception as exc:
            print exc
            return None


    def getAllTrims(self, parse_code, url):
        def readTeg(teg):
            try:
                return teg.text.strip()
            except:
                return ''

        splited_url = url.split('/')
        marka = splited_url[3]
        model = splited_url[4]
        year  = splited_url[6]

        main_div = parse_code.find('div', {'id': 'pricingspecstablelist'})

        list_types = main_div.findAll('h3', {'class': 'cgNativeTable--title'})
        list_tables = main_div.findAll('table', {'class': 'cgNativeTable'})

        i = 0
        list_data_car = []
        for table in list_tables:
            list_rows = table.findAll('tr', {'class': 'cgNativeTable--row'})
            try:
                type = list_types[i].text.strip()
            except:
                type = ''

            for row in list_rows:
                listed_row = row.findAll('td')
                try:
                    trim = readTeg(listed_row[0])
                except:
                    trim = ''

                try:
                    listed_spec = listed_row[1].findAll('span', {'class': 'cgNativeTable--subItem'})
                except:
                    listed_spec = []
                try:
                    engine_volume = readTeg(listed_spec[0])
                except:
                    engine_volume = ''
                try:
                    short_spec = readTeg(listed_spec[1].find('span', {'class': 'hidden-xs'}))
                except:
                    short_spec = ''
                try:
                    specs = readTeg(listed_spec[1].find('span', {'class': 'visible-xs-inline'}))
                except:
                    specs = ''
                try:
                    short_transmission = readTeg(listed_spec[2].find('span', {'class': 'hidden-xs'}))
                except:
                    short_transmission = ''
                try:
                    transmission = readTeg(listed_spec[2].find('span', {'class': 'visible-xs-inline'}))
                except:
                    transmission = ''

                price_range = readTeg(listed_row[2].find('span'))
                price_range = price_range.encode('utf8')
                price_range = price_range.split('\xe2\x80\x93')

                try:
                    min_price = price_range[0]\
                        .replace('$','')\
                        .replace(',','')\
                        .replace('.','').strip()
                except:
                    min_price = ''

                try:
                    max_price = price_range[1] \
                        .replace('$', '') \
                        .replace(',', '') \
                        .replace('.', '').strip()
                except:
                    max_price = ''

                car_string = str(marka)+str(model)+str(year)+str(trim)+\
                             str(engine_volume)+str(specs)+str(transmission)+\
                             str(min_price)+str(max_price)+str(type)

                hash_code = self.hash_generator(car_string)

                data_car = {
                    'marka': marka,
                    'model': model,
                    'year': year,
                    'trim':trim,
                    'engine_volume':engine_volume,
                    'short_specs':short_spec,
                    'specs':specs,
                    'short_transmission':short_transmission,
                    'transmission':transmission,
                    'min_price':min_price,
                    'max_price':max_price,
                    'type': type,
                    'hash_code': hash_code
                }
                print data_car
                self.db.insert_trim(data_car)

            i +=1

        return list_data_car


    def main(self):
        url = 'https://www.carsguide.com.au/mlp/makes'
        response = self.request_manager.take_get_request(url)['source_code']
        parse_code = self.source_code_manager.parse_code(response)
        marka_links = self.getAllMarks(parse_code)

        self.list_models_links = []
        #1 toyota
        #1 - 3 ford, holden final
        #46 не запускать
        for link_mark in marka_links[54:]:
            print link_mark
            response = self.request_manager.take_get_request(link_mark)['source_code']
            parse_code = self.source_code_manager.parse_code(response)
            self.getAllModels(parse_code)

        list_price_guide = []
        for model_link in self.list_models_links:
            print model_link, '   priceeeeee'
            response = self.request_manager.take_get_request(model_link)['source_code']
            parse_code = self.source_code_manager.parse_code(response)
            list_price_guide.append(self.getPricingGuide(parse_code, model_link))

        self.list_year_links = []
        for link_model in list_price_guide:
            print link_model,'    modellll'
            response = self.request_manager.take_get_request(link_model)['source_code']
            parse_code = self.source_code_manager.parse_code(response)
            self.getAllYearList(parse_code, url=link_model)


        list_data_car = []
        for year_link in self.list_year_links:
            print year_link,'     yearrrrrrrr'
            response = self.request_manager.take_get_request(year_link)['source_code']
            parse_code = self.source_code_manager.parse_code(response)
            list_data_car.append(self.getAllTrims(parse_code=parse_code,url=year_link))



if __name__ == '__main__':
    ModelsLinksExtractor().main()

