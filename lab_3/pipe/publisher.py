import pika
import json
from scraper.scraper import scrape_cactus_phones

def publish_products():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    channel = connection.channel()

    channel.queue_declare(queue='products_queue')

    products = scrape_cactus_phones()

    for product in products:
        channel.basic_publish(
            exchange='',
            routing_key='products_queue',
            body=json.dumps(product)
        )
        print(f"Published product: {product['name']}")

    connection.close()

def run_publisher():
    publish_products()