import argparse
import json
import multiprocessing
import threading
import rabbitpy
from datetime import datetime

from RabbitMQConnector import RabbitMQConnector
from DubizzleDataExtractor import DataExtractor as dubizzle_DE
from DubicarsDataExtractor import DataExtractor as dubicars_DE


class RabbitMQManager():
    EXCHANGE = 'input'

    def __init__(self, queue_name):
        self.connector = RabbitMQConnector()
        self.connection = self.connector.connect()
        self.kwargs = {'connection': self.connection}
        self.publishChannel = self.connection.channel()

        self.ROUTING_KEY = str(queue_name)
        self.QUEUE = str(queue_name)

        self.dubizzle_de = dubizzle_DE()
        self.dubicars_de = dubicars_DE()

        self.queue_declare()

    def startConsuming(self):
        with self.connection.channel() as channel:
            print "Channel"
            channel.prefetch_count(1)
            for message in rabbitpy.Queue(channel, self.QUEUE):
                try:
                    bodyMessage = message.body
                    bodyMessage = json.loads(bodyMessage)
                    print (" [x] %r received %r" % (threading.currentThread(), bodyMessage))
                    result = self.processMessage(bodyMessage)
                    if result is False:
                        self.load_urls([bodyMessage])
                    message.ack()
                except Exception as exc:
                    print exc
                    message.ack()

    def load_urls(self, urls):
        with self.connection.channel() as channel:
            for url in urls:
                message = rabbitpy.Message(channel=channel,
                                               body_value=url,
                                               properties={
                                                           "delivery_mode": 2},
                                               )
                message.publish(self.EXCHANGE, self.ROUTING_KEY)


    def processMessage(self, message):
        try:
            source = message['source']
            activity = message['activity']
            try:
                message['timestamp'] = datetime.strptime(message['timestamp'], "%Y-%m-%d %H:%M:%S")
            except:
                pass
            if source == 'dubicars':
                if activity == 'extract':
                    self.dubicars_de.extract_data(message)
                elif activity == 'update':
                    self.dubicars_de.update_data(message)
            elif source == 'dubizzle':
                if activity == 'extract':
                    self.dubizzle_de.extract_data(message)
                elif activity == 'update':
                    self.dubizzle_de.update_data(message)
            return True
        except Exception as exc:
            print exc
            return False

    def queue_declare(self):
        with self.connection.channel() as channel:
            queue = rabbitpy.Queue(channel, self.QUEUE)
            queue.durable = True
            queue.declare()
            queue.bind(source=self.EXCHANGE, routing_key=self.ROUTING_KEY)



def multiprocess(project_id):
    rabbit = RabbitMQManager(project_id)
    rabbit.startConsuming()




if __name__ == "__main__":
    multiprocess('uae_extract_urls')
#     parser = argparse.ArgumentParser()
#
#     parser.add_argument("-u", "--update", action="store_true",
#                         help="update")
#     parser.add_argument("-e", "--extract", action="store_true",
#                         help="extract data")
#
#     args = parser.parse_args()
#     if args.update:
#         multiprocess(project_id='uae_update_urls')
#     elif args.extract:
#         multiprocess(project_id='uae_extract_urls')