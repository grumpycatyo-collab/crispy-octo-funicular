from datetime import datetime

def mdl_to_eur(price_mdl):
    return round(price_mdl / 19.5, 2)

def eur_to_mdl(price_eur):
    return round(price_eur * 19.5, 2)

def process_products(products, min_price_eur, max_price_eur):
    mapped_products = []
    for product in products:
        new_product = product.copy()
        if new_product['currency'] == 'MDL':
            new_product['price'] = mdl_to_eur(new_product['price'])
            new_product['currency'] = 'EUR'
        else:
            new_product['price'] = eur_to_mdl(new_product['price'])
            new_product['currency'] = 'MDL'
        mapped_products.append(new_product)

    filtered_products = list(filter(
        lambda x: min_price_eur <= x['price'] <= max_price_eur if x['currency'] == 'EUR'
        else min_price_eur <= mdl_to_eur(x['price']) <= max_price_eur,
        mapped_products
    ))

    total_price = sum(p['price'] for p in filtered_products)

    result = {
        'timestamp': datetime.utcnow().isoformat(),
        'products': filtered_products,
        'total_price': total_price
    }
    return result