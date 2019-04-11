import argparse

import time

from database.DatabaseManager import DatabaseManager
from DubizzleLinksExtractor import LinksExtractor as DubizzleLinksExtractor
from DubicarsLinksExtractor import LinksExtractor as DubicarsLinksExtractor
from managers.DealQualityManager import DealQualityManager
from multiprocess import Pool

import RabbitMQ.RabbitMQManager


class Runner():
    TEMPLATE_DUBIZZLE = 'https://uae.dubizzle.com/motors/used-cars/?page={}&seller_type=OW&is_search=1&is_basic_search_widget=0&places__id__in=--&ot=desc&o=2'
    TEMPLATE_DUBICARS = 'https://www.dubicars.com/search?ajax=true&view=&o=&l=&ma=&mo=0&c=new-and-used&pf=&pt=&yf=&yt=&kf=10000&kt=&b=&co=&ci=&s=&gi=&page={}'


    DUBIZZLE_DOMAIN = 'dubai.dubizzle.com'
    DUBICARS_DOMAIN = 'dubicars.com'

    def __init__(self):
        # self.pool = Pool(5)

        self.db = DatabaseManager()
        # self.rmq_extract = RabbitMQ.RabbitMQManager.RabbitMQManager('uae_extract_urls')
        # self.rmq_update = RabbitMQ.RabbitMQManager.RabbitMQManager('uae_update_urls')

        # ======== Dubizzle =======
        #self.dubizzle_data_extractor = DubizzleDataExtractor()
        # self.dubizzle_links_extractor = DubizzleLinksExtractor()

        # ======== Dubicars =======
        #self.dubicars_data_extractor = DubicarsDataExtractor()
        # self.dubicars_links_extractor = DubicarsLinksExtractor()



        self.deal_quality = DealQualityManager()

    def main(self, update_mode=False, deal_update=False, extract_data=False):

        # if update_mode:
        #     self.update_db()
        #     self.deal_quality.main(self.db.get_grouped_listings())
        #     print "Updated!"
        #     self.db.reset_updates()
        #     return
        # if deal_update:
        #     self.deal_quality.main(self.db.get_grouped_listings())
        #     return
        # if extract_data: # Not work
        #     new_urls = self.db.get_urls(source=None)
        #     print len(new_urls)
        #     self.pool.map(self.dubizzle_data_extractor.extract_data, new_urls)
        #     return



        self.deal_quality.main(self.db.get_grouped_listings())

    def extract_data_dubizzle(self):
        # ======== Dubizzle =======
        # self.dubizzle_links_extractor.extract_urls()
        # print self.DUBIZZLE_DOMAIN

        new_urls = self.db.get_urls(source=self.DUBIZZLE_DOMAIN)  # Dubizzle
        print len(new_urls)
        self.rmq_extract.load_urls(self.generate_urls_to_queue(activity='extract',
                                                               source='dubizzle',
                                                               urls=new_urls))

    def extract_data_dubicars(self):
        # ======== Dubicars =======
        self.dubicars_links_extractor.main(self.TEMPLATE_DUBICARS)

        new_urls = self.db.get_urls(source=self.DUBICARS_DOMAIN)  # Dubcars
        print len(new_urls)
        self.rmq_extract.load_urls(self.generate_urls_to_queue(activity='extract',
                                                               source='dubicars',
                                                               urls=new_urls))

    def update_db(self):

        # ======== Dubizzle =======
        dubizzle_urls_data = self.db.get_all_urls(source=self.DUBIZZLE_DOMAIN)
        urls_to_queue = self.generate_urls_to_queue(source='dubizzle', activity='update', urls=dubizzle_urls_data)
        self.rmq_update.load_urls(urls=urls_to_queue)

        # ======== Dubicars =======
        dubicars_urls_data = self.db.get_all_urls(source=self.DUBICARS_DOMAIN)
        urls_to_queue = self.generate_urls_to_queue(source='dubicars', activity='update', urls=dubicars_urls_data)
        self.rmq_update.load_urls(urls=urls_to_queue)

    def generate_urls_to_queue(self, source, activity, urls):

        for url in urls:
            url['activity'] = activity
            url['source'] = source

        return urls

    def deal_quality_func(self):
        self.deal_quality.main(self.db.get_grouped_listings())







if __name__ == '__main__':
    print Runner().main()

#
#     parser = argparse.ArgumentParser()
#
#     parser.add_argument("-u", "--update", action="store_true",
#                         help="update")
#     parser.add_argument("-e", "--extract", action="store_true",
#                         help="extract data")
#
#     args = parser.parse_args()
#     if args.update:
#         RabbitMQ.RabbitMQManager.multiprocess(project_id='uae_update_urls')
#     elif args.extract:
#         RabbitMQ.RabbitMQManager.multiprocess(project_id='uae_extract_urls')
# #
#     #Runner().extract_data_dubicars()
#     #
#     # parser = argparse.ArgumentParser()
#     #
#     # parser.add_argument("-u", "--update", action="store_true",
#     #                     help="update")
#     # parser.add_argument("-d", "--deal", action="store_true",
#     #                     help="deal")
#     # parser.add_argument("-e", "--extract", action="store_true",
#     #                     help="extract data")
#     #
#     #
#     #
#     # args = parser.parse_args()
#     # if args.update:
#     #     Runner().main(update_mode=True)
#     # elif args.deal:
#     #     Runner().main(deal_update=True)
#     # elif args.extract:
#     #     Runner().main(extract_data=True)
#     # else:
#     #     Runner().main()
#
#
#
