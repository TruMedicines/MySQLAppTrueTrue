import configparser
from webapp import db

class config():
    def __init__(self):
        self.device_id = 0
        self.user_id = 0

    def initialize(self):
        config = configparser.ConfigParser()
        config.read('webapp/conf.ini')

        self.device_id = config['DEFAULT']['device']

        cur = db.connection.cursor()        
        cur.execute('''SELECT user_id FROM Devices WHERE device_id = '''+self.device_id)
        results = cur.fetchall()
        self.user_id=results[0]['user_id']
        print("Device is ", self.device_id, "User is ", self.user_id)
