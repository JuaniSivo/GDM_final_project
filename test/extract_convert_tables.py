import os
import json
import xml.etree.ElementTree as ET
import requests
import zipfile
import csv
from io import BytesIO

def download_zip(document_id, output_dir, api_key):
    url = f"https://cli.agiledd.ai/api/documents/{document_id}/tables?return_combined_excel=false"
    
    # Headers for authentication, including API key and optional token
    headers = {"Authorization": f"Bearer {api_key}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        zip_path = os.path.join(output_dir, f"{document_id}.zip")
        with open(zip_path, "wb") as f:
            f.write(response.content)
        return zip_path
    else:
        raise Exception(f"Failed to download ZIP: {response.status_code}")

def extract_zip(zip_path, extract_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

def csv_to_json(csv_path, json_path):
    with open(csv_path, newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        data = list(reader)
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)

def dict_to_xml(data, root_name="root"):
    root = ET.Element(root_name)
    for row in data:
        item = ET.SubElement(root, "row")
        for key, value in row.items():
            child = ET.SubElement(item, key)
            child.text = value
    return ET.ElementTree(root)

def csv_to_xml(csv_path, xml_path):
    with open(csv_path, newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        data = list(reader)
    tree = dict_to_xml(data)
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)

def main(document_id, api_key):
    base_dir = os.path.join("output", document_id)
    json_dir = os.path.join(base_dir, "JSON_table")
    xml_dir = os.path.join(base_dir, "XML_table")
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(xml_dir, exist_ok=True)
    
    zip_path = download_zip(document_id, base_dir, api_key=api_key)
    extract_dir = os.path.join(base_dir, "extracted")
    os.makedirs(extract_dir, exist_ok=True)
    extract_zip(zip_path, extract_dir)
    
    for file in os.listdir(extract_dir):
        if file.endswith(".csv"):
            csv_path = os.path.join(extract_dir, file)
            json_path = os.path.join(json_dir, file.replace(".csv", ".json"))
            xml_path = os.path.join(xml_dir, file.replace(".csv", ".xml"))
            
            csv_to_json(csv_path, json_path)
            csv_to_xml(csv_path, xml_path)
    
    print(f"Processing completed. Files saved in {base_dir}")

if __name__ == "__main__":
    document_id = '269'  # Replace with actual document ID
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Imp1YW5pc2l2b0BnbWFpbC5jb20iLCJleHAiOjE3NDQ1ODg4MDAsImlhdCI6MTc0MTk0NTgzMSwiYXVkIjoiYWdpbGVkZC1wZXJzb25hbC1hY2Nlc3MtdG9rZW4iLCJqdGkiOiIxOCJ9.D4ZTKbRspIQOpsqgKIx8Sre_P_2OA-bwp1SNkcfh6qA"  # API key for authentication
    main(document_id, api_key)
