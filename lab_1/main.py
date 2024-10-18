from scraper import scrape_cactus_phones
from processor import process_products
from serializer import manual_json_serialize, manual_xml_serialize, CustomSerializer
from docker_client import send_to_docker_server

def save_serialized_data(processed_data):
    json_data = manual_json_serialize(processed_data)
    with open('files/data.json', 'w', encoding='utf-8') as f:
        f.write(json_data)

    xml_data = manual_xml_serialize(processed_data)
    with open('files/data.xml', 'w', encoding='utf-8') as f:
        f.write(xml_data)

    custom_data = CustomSerializer.serialize(processed_data)
    with open('files/data.custom', 'w', encoding='utf-8') as f:
        f.write(custom_data)

    return json_data, xml_data, custom_data

def main():
    print("Scraping products...")
    products = scrape_cactus_phones()

    print("\nProcessing products...")
    processed_data = process_products(products, min_price_eur=200, max_price_eur=1000)

    print("\nSerializing data...")
    json_data = manual_json_serialize(processed_data)
    xml_data = manual_xml_serialize(processed_data)
    custom_data = CustomSerializer.serialize(processed_data)
    save_serialized_data(processed_data)

    print("\nJSON:", json_data)
    print("\nXML:", xml_data)
    print("\nCustom:", custom_data)

    print("\nSending to Docker server...")
    try:
        json_response = send_to_docker_server(json_data, 'application/json')
        print("\nJSON Response:", json_response)

        xml_response = send_to_docker_server(xml_data, 'application/xml')
        print("\nXML Response:", xml_response)
    except Exception as e:
        print(f"Error sending to Docker server: {e}")


if __name__ == "__main__":
    main()