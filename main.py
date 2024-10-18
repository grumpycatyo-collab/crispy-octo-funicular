import requests
from bs4 import BeautifulSoup
import re


def scrape_cactus_phones():
    url = "https://www.cactus.md/ro/catalogue/electronice/telefone/mobilnye-telefony/"

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching page: Status code {response.status_code}")
        return
    soup = BeautifulSoup(response.content, 'html.parser')
    products = soup.find_all('div', class_='catalog__pill')

    scraped_products = []

    for product in products:
        name = product.find('span', class_='catalog__pill__text__title').text.strip()

        price = product.find('div', class_='catalog__pill__controls__price').text.strip()

        number_parts = re.findall(r'\d+', price)
        number_str = ''.join(number_parts)
        price = int(number_str)

        link = product.find('a')['href']
        full_link = f"https://www.cactus.md{link}"

        product_response = requests.get(full_link)
        product_soup = BeautifulSoup(product_response.content, 'html.parser')

        screen_size = extract_screen_size(product_soup)
        if not name or not price:
            print(f"Missing required data for product: {name}")
            continue

        if not type(price)==int:
            print(f"Invalid price format for product: {name}")
            continue

        # Store scraped data
        product_data = {
            'name': name,
            'price': int(price),
            'link': full_link,
            'screen_size': screen_size
        }

        scraped_products.append(product_data)

    return scraped_products

def extract_screen_size(soup):
    params = soup.find('div', id='itemParams')
    if params:
        for li in params.find_all('li'):
            h2 = li.find('h2', class_='catalog__characteristic__title')
            if h2 and "Diagonală display:" in h2.get_text():

                span = h2.find('span', class_='catalog__characteristic__unit')
                if span:
                    return span.get_text(strip=True)
    return "N/A"


products = scrape_cactus_phones()


for product in products:
    print(f"Name: {product['name']}")
    print(f"Price: {product['price']} lei")
    print(f"Link: {product['link']}")
    print(f"Screen Size: {product['screen_size']}")
    print("---")