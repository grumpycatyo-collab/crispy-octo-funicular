# Enhanced consumer with retry logic
import pika
import json
import requests
from time import sleep

class ProductConsumer:
    def __init__(self, max_retries=3, retry_delay=5):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection = None
        self.channel = None

    def connect(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost')
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='products_queue')
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")
            raise

    def post_to_server(self, product, attempt=1):
        try:
            response = requests.post(
                'http://localhost:8000/products/',
                json=product
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            if attempt < self.max_retries:
                print(f"Attempt {attempt} failed, retrying in {self.retry_delay} seconds...")
                sleep(self.retry_delay)
                return self.post_to_server(product, attempt + 1)
            else:
                print(f"Failed to post product after {self.max_retries} attempts: {e}")
                return False

    def callback(self, ch, method, properties, body):
        try:
            product = json.loads(body)
            print(product)
            success = self.post_to_server(product)

            if success:
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        except Exception as e:
            print(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        try:
            self.connect()
            self.channel.basic_consume(
                queue='products_queue',
                on_message_callback=self.callback
            )
            print('Starting to consume messages...')
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("Shutting down consumer...")
            if self.connection:
                self.connection.close()
        except Exception as e:
            print(f"Unexpected error: {e}")
            if self.connection:
                self.connection.close()

def run_consumer():
    consumer = ProductConsumer()
    consumer.start()