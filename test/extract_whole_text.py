import requests







# Function to extract text from a document using an API
def extract_text(document_id, total_pages, api_key, token=None):
    # Base URL for the API endpoint, where document ID and page number are inserted dynamically
    base_url = "https://cli.agiledd.ai/api/documents/{}/pages/{}/text"
    
    # Headers for authentication, including API key and optional token
    headers = {"Authorization": f"Bearer {api_key}"}
    if token:
        headers["Token"] = token  # Add token if provided
    
    extracted_text = []  # List to store extracted text from each page
    
    # Loop through each page to fetch text one by one
    for page in range(1, total_pages + 1):
        url = base_url.format(document_id, page)  # Construct the request URL
        response = requests.get(url, headers=headers)  # Send GET request to API
        
        if response.status_code == 200:
            extracted_text.append(response.text)  # Append extracted text to the list
        else:
            print(f"Failed to fetch page {page}: {response.status_code}")  # Print error message if request fails
            
    return "\n".join(extracted_text)  # Combine all page texts into a single string with line breaks

# Function to save extracted text to a .txt file
def save_text_to_file(text, filename):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)  # Write extracted text to the specified file

# Example usage

document_id = 913  # Unique identifier for the document
total_pages = 7  # Total number of pages in the document to be processed
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Imp1YW5pc2l2b0BnbWFpbC5jb20iLCJleHAiOjE3NDQ1ODg4MDAsImlhdCI6MTc0MTk0NTgzMSwiYXVkIjoiYWdpbGVkZC1wZXJzb25hbC1hY2Nlc3MtdG9rZW4iLCJqdGkiOiIxOCJ9.D4ZTKbRspIQOpsqgKIx8Sre_P_2OA-bwp1SNkcfh6qA"  # API key for authentication
token = "your_token"  # Optional authentication token

# Extract text from the document
document_text = extract_text(document_id, total_pages, api_key)

# Save the extracted text to a file
save_text_to_file(document_text, "extracted_text.txt")

print("Text saved to extracted_text.txt")  # Print confirmation message
