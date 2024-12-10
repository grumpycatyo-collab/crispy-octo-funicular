from ftplib import FTP
import json
import os
from scraper.scraper import scrape_cactus_phones, mock_scrape_cactus_phones
from scraper.processor import process_products
import time

def process_and_upload_to_ftp(products):
    processed_products = process_products(products, min_price_eur=200, max_price_eur=1000)

    filename = 'processed_products.json'
    with open(filename, 'w') as f:
        json.dump(processed_products, f)

    try:
        ftp = FTP()
        ftp.connect('localhost', 21)
        ftp.login('testuser', 'testpass')

        with open(filename, 'rb') as f:
            ftp.storbinary(f'STOR {filename}', f)

        ftp.quit()
        print("File uploaded successfully to FTP")

    except Exception as e:
        print(f"FTP upload error: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

def scrape_and_process():
    products = mock_scrape_cactus_phones()
    process_and_upload_to_ftp(products)

def feed_ftp():
    while True:
        scrape_and_process()
        print("Sleeping for 60 seconds...")
        time.sleep(60)