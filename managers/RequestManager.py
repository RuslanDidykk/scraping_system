import requests
from managers.UseragentManager import UseagentManager
import time
from selenium import webdriver



class RequestManager():
    REQUEST_HEADER = {
        'Accept' : 'application/json',
        'Content-Type' : 'application/json',
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "en-US,en;q=0.8",
        "User-Agent": "some user-agent"
    }

    def __init__(self):
        self.useragent = UseagentManager()

    def get_driver(self, driver_name):
        if driver_name == 'chrome':
            driver = webdriver.Chrome('/usr/local/bin/chromedriver')
        elif driver_name == 'phantom':
            driver = webdriver.PhantomJS()
        else:
            raise
        driver.set_window_size(1120, 550)
        return driver

    def take_js_request(self, url, driver, control_class=None, control_amount=None):
        struct_data = {'source_code': '',
                       'status_code': '',
                       'timeout': False,
                       'redirect': False,
                       'redirect_error': False,
                       'error': True,
                       'error_description': '',
                       'proxy': False
                       }
        driver.get(url)

        if control_class is None:
            struct_data['source_code'] = driver.page_source
            return struct_data

        while True:
            time.sleep(1)
            if self.__page_is_loaded(control_class, driver, control_amount):
                break
            else:
                continue
        struct_data['source_code'] = driver.page_source

        return struct_data

    def __page_is_loaded(self, control_class, driver, control_amount):
        try:
            elements = driver.find_elements_by_class_name(control_class)
            if control_amount > len(elements):
                return False
            return True
        except Exception as exc:
            print exc
            return False

    def take_get_request(self, url, proxy_using=False, timeout=100):
        struct_data = {'source_code': '',
                       'status_code': '',
                       'timeout': False,
                       'redirect': False,
                       'redirect_error': False,
                       'error': True,
                       'error_description': '',
                       'proxy': proxy_using
                       }
        headers = self.__generate_headers()
        url = self.convert_to_standart_format(url)
        try:
            if proxy_using:
                proxie = {'https': '52.70.148.50:3128'}
                response = requests.get(url=url,
                                        proxies=proxie,
                                        headers=headers,
                                        timeout=timeout,
                                        )
                struct_data['proxy'] = str(proxie)
            else:
                headers = {'Accept': '*/*',

                            'Accept-Encoding': 'gzip, deflate',

'User-Agent': 'runscope/0.1'}
                response = requests.get(url=url,
                                        headers=headers,
                                        timeout=timeout)
            if self.is_redirect(source_url=url, returned_url=response.url):
                struct_data['redirect'] = True
            print response.history

            struct_data['status_code'] = response.status_code
            struct_data['source_code'] = response.text
            struct_data['error'] = False
            struct_data['url'] = response.url
        except requests.Timeout:
            struct_data['timeout'] = True
        except requests.ConnectionError as exc:
            struct_data['error_description'] = str(exc)
        except requests.TooManyRedirects as exc:
            struct_data['redirect_error'] = True
            struct_data['error_description'] = str(exc)
        except Exception as exc:
            struct_data['error_description'] = str(exc)

        return struct_data

    def __generate_headers(self):
        self.REQUEST_HEADER['User-Agent'] = self.useragent.get_random_useragent()

    def convert_to_standart_format(self, url):
        if 'http://' in url:
            return url
        elif 'https://' in url:
            return url
        else:
            return 'http://' + url

    def is_redirect(self, source_url, returned_url):
        if source_url == returned_url:
            return False
        else:
            return True


if __name__ == '__main__':
    requestManager = RequestManager()
    url = 'https://search.yahoo.com/local/s;_ylt=AwrBT7lFbAVas10AsRVXNyoA;_ylu=X3oDMTEzZDcyNzk0BGNvbG8DYmYxBHBvcwMxBHZ0aWQDREZENl8xBHNlYwNwaXZz;_ylc=X1MDMTM1MTE5NTExOARfcgMyBGdwcmlkAwRuX3N1Z2cDMARvcmlnaW4Dc2VhcmNoLnlhaG9vLmNvbQRwb3MDMARwcXN0cgMEcHFzdHJsAwRxc3RybAMxMARxdWVyeQM5MTc3NTQ1Nzc3BHRfc3RtcAMxNTEwMzA1MTg1?fr2=sb-top-search&p=9177545777&fr=yfp-t-'
    print requestManager.take_get_request(url=url)
