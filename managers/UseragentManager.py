from database.DatabaseManager import DatabaseManager
class UseagentManager():
    def __init__(self):
        self.db = DatabaseManager()
        pass

    def get_random_useragent(self):
        useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        return useragent