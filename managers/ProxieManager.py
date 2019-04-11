from database.DatabaseManager import DatabaseManager

class ProxieManager():

    def __init__(self):
        self.db = DatabaseManager()

    def check_existing_proxie(self):
        proxie_list = self.db.get_proxies()
        for proxie_data in proxie_list:
            proxie = self.__generate_proxie(proxie_data)


    def __check_proxie(self, proxie):
        pass

    @staticmethod
    def __generate_proxie(proxie_data):
        protocol = proxie_data['protocol']
        host = proxie_data['host']
        port = proxie_data['port']
        proxie = protocol + "://" + host + ":" + port
        return proxie

