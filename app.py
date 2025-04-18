import streamlit as st
import requests
import zipfile
import io
import pandas as pd
import json
import xml.etree.ElementTree as ET

def get_page_count(json_data):
    return len(json_data.get("pages", []))

def fetch_document_data(document_id, api_key):
    url = f"https://cli.agiledd.ai/api/documents/{document_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def download_text(document_id, num_pages, api_key):
    base_url = "https://cli.agiledd.ai/api/documents/{}/pages/{}/text"    # Base URL for the API endpoint, where document ID and page number are inserted dynamically
    headers = {"Authorization": f"Bearer {api_key}"}    # Headers for authentication, including API key and optional token
    extracted_text = []  # List to store extracted text from each page
    
    # Loop through each page to fetch text one by one
    for page in range(1, num_pages + 1):
        url = base_url.format(document_id, page)  # Construct the request URL
        response = requests.get(url, headers=headers)  # Send GET request to API
        
        if response.status_code == 200:
            extracted_text.append(response.text)  # Append extracted text to the list
        else:
            print(f"Failed to fetch page {page}: {response.status_code}")  # Print error message if request fails
            
    return "\n".join(extracted_text)  # Combine all page texts into a single string with line breaks

def download_csv_zip(document_id, api_key):
    url = f"https://cli.agiledd.ai/api/documents/{document_id}/tables?return_combined_excel=false"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return io.BytesIO(response.content)
    else:
        st.error("Failed to retrieve CSV zip.")
        return None

def extract_zip(zip_file):
    with zipfile.ZipFile(zip_file) as zip_ref:
        return {name: zip_ref.read(name).decode('utf-8') for name in zip_ref.namelist()}

def convert_csv_to_json_and_xml(csv_files):
    json_data = {}
    xml_data = {}
    
    for csv_file, content in csv_files.items():
        df = pd.read_csv(io.StringIO(content))
        json_data[csv_file.replace('.csv', '')] = df.to_json(orient='records', lines=True, force_ascii=False)

        root = ET.Element("root")
        for _, row in df.iterrows():
            item = ET.SubElement(root, "item")
            for col in df.columns:
                child = ET.SubElement(item, col)
                child.text = str(row[col])
        xml_data[csv_file.replace('.csv', '')] = ET.tostring(root, encoding='unicode')

    return json_data, xml_data

def create_final_zip(text, json_data, xml_data):
    final_zip = io.BytesIO()
    with zipfile.ZipFile(final_zip, 'w') as final_zip_file:
        final_zip_file.writestr('extracted_text.txt', text)
        for json_filename, json_content in json_data.items():
            final_zip_file.writestr(f'{json_filename}.json', json_content)
        for xml_filename, xml_content in xml_data.items():
            final_zip_file.writestr(f'{xml_filename}.xml', xml_content)
    final_zip.seek(0)
    return final_zip

def main():
    st.title("Document Processing App")

    api_key = st.text_input("Enter API key:")
    document_id = st.text_input("Enter Document ID:", value=500)
    if api_key:
        document_data = fetch_document_data(document_id, api_key)
        num_pages = get_page_count(document_data)
        st.write(num_pages)

    if st.button("Process Document"):
        text = download_text(document_id, num_pages, api_key)
        if text:
            zip_file = download_csv_zip(document_id, api_key)
            if zip_file:
                csv_files = extract_zip(zip_file)
                json_data, xml_data = convert_csv_to_json_and_xml(csv_files)
                final_zip = create_final_zip(text, json_data, xml_data)

                st.download_button("Download Processed Files", final_zip, file_name='processed_files.zip')

            st.success("Processing complete!")

if __name__ == "__main__":
    main()