import rabbitpy
from config import rabbit_port
from config import rabbit_host
from config import rabbit_user
from config import rabbit_pass
from config import rabbit_vhost


class RabbitMQConnector():
    def connect(self):
        connection = rabbitpy.Connection("amqp://{}:{}@{}:{}/{}".format(rabbit_user,
                                                                        rabbit_pass,
                                                                        rabbit_host,
                                                                        rabbit_port,
                                                                        rabbit_vhost
                                                                        ))
        print "Connected"
        return connection
