import socket
from bs4 import BeautifulSoup
import re
import ssl


def make_https_request(host, path):
    context = ssl.create_default_context()

    with socket.create_connection((host, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            ssock.send(request.encode())

            response = b""
            while True:
                data = ssock.recv(4096)
                if not data:
                    break
                response += data

    response = response.decode('utf-8')
    try:
        headers, body = response.split('\r\n\r\n', 1)
    except ValueError:
        print("Failed to split response")
        return None

    return body


def extract_screen_size(soup):
    params = soup.find('div', id='itemParams')
    if params:
        for li in params.find_all('li'):
            h2 = li.find('h2', class_='catalog__characteristic__title')
            if h2 and "Diagonală display:" in h2.get_text():
                span = h2.find('span', class_='catalog__characteristic__unit')
                if span:
                    screen_size = span.get_text(strip=True)
                    screen_size = screen_size.replace('"', '').strip()
                    return screen_size
    return "N/A"


def scrape_cactus_phones():
    host = "www.cactus.md"
    path = "/ro/catalogue/electronice/telefone/mobilnye-telefony/"
    body = make_https_request(host, path)
    soup = BeautifulSoup(body, 'html.parser')
    products = soup.find_all('div', class_='catalog__pill')
    scraped_products = []
    print("Started scraping products")
    for product in products:
        try:
            name = product.find('span', class_='catalog__pill__text__title').text.strip()
            price = product.find('div', class_='catalog__pill__controls__price').text.strip()

            number_parts = re.findall(r'\d+', price)
            number_str = ''.join(number_parts)
            price = int(number_str)

            link = product.find('a')['href']
            full_link = f"https://www.cactus.md{link}"

            product_body = make_https_request(host, link)
            product_soup = BeautifulSoup(product_body, 'html.parser')
            screen_size = extract_screen_size(product_soup)

            product_data = {
                'name': name,
                'price': price,
                'currency': 'MDL',
                'link': full_link,
                'screen_size': screen_size
            }

            scraped_products.append(product_data)
        except Exception as e:
            print(f"Error scraping product: {e}")
            continue
    print("Finished the scraping")
    return scraped_products


def mock_scrape_cactus_phones():
    """
    Mock version of scrape_cactus_phones() that returns test data
    without making actual HTTP requests
    """
    mock_products = [
        {
            'name': 'iPhone 14 Pro Max',
            'price': 25999,
            'currency': 'MDL',
            'link': 'https://www.cactus.md/ro/catalogue/iphone-14-pro-max',
            'screen_size': '6.7'
        },
        {
            'name': 'Samsung Galaxy S23 Ultra',
            'price': 23499,
            'currency': 'MDL',
            'link': 'https://www.cactus.md/ro/catalogue/samsung-s23-ultra',
            'screen_size': '6.8'
        },
        {
            'name': 'Xiaomi Redmi Note 12',
            'price': 4299,
            'currency': 'MDL',
            'link': 'https://www.cactus.md/ro/catalogue/xiaomi-redmi-note-12',
            'screen_size': '6.67'
        },
        {
            'name': 'Nothing Phone (2)',
            'price': 15999,
            'currency': 'MDL',
            'link': 'https://www.cactus.md/ro/catalogue/nothing-phone-2',
            'screen_size': '6.7'
        },
        {
            'name': 'Google Pixel 7 Pro',
            'price': 19999,
            'currency': 'MDL',
            'link': 'https://www.cactus.md/ro/catalogue/google-pixel-7-pro',
            'screen_size': '6.7'
        }
    ]

    print("Started mock scraping products")
    import time
    time.sleep(1)
    print("Finished the mock scraping")

    return mock_products