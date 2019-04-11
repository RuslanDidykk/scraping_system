import hashlib

from datetime import datetime
import time

import os


class Generator:

    def generate_controll_summ(self, string):
        hash_object = hashlib.sha256(string)
        hex_dig = hash_object.hexdigest()
        return hex_dig

    @staticmethod
    def generate_timestamp(format="%Y.%m.%d:%H:%M:%S"):
        timestamp = datetime.strftime(datetime.now(), format)
        return timestamp

    def generate_url_string(self, url):
        timestamp = self.generate_timestamp(format="%Y.%m.%d")
        url_string = url + '_' + timestamp
        hash = self.generate_controll_summ(url_string)
        return {'url_string': url_string,
                'hash': hash}

    def generate_urls_data(self, urls_list, proxy):
        urls_data_list = []
        for url in urls_list:
            url_data = self.generate_url_string(url)
            url_data['proxy'] = proxy
            url_data['url'] = url
            urls_data_list.append(url_data)
        return urls_data_list

    def generate_session_name(self, project_id):
        timestamp = self.generate_timestamp(format="%Y.%m.%d")
        session_name = str(timestamp) + '_' + str(project_id)
        return session_name

    def generate_data_to_database(self, data_from_page, url_id, proxy):
        result = {}
        result['data'] = data_from_page
        result['url_id'] = url_id
        result['proxy'] = proxy
        return result

    def generate_filename(self, project_title, project_id, date, format):
        return project_title + '_'+ str(project_id) + '_' + str(date) + '.' + format

    def generate_path_to_project(self):
        return os.path.dirname(os.path.abspath(__file__)).split('managers')[0]

    def create_folder(self, folder_name):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)



if __name__ == '__main__':
    generator = Generator()
    print generator.generate_path_to_project()
    ts_1 = generator.generate_timestamp()
    time.sleep(5)
    ts_2 = generator.generate_timestamp()
    time_dif = datetime.strptime(ts_2, "%Y.%m.%d:%H:%M:%S") - datetime.strptime(ts_1,"%Y.%m.%d:%H:%M:%S")
    print time_dif.days