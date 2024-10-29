import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaInMemoryUpload
from googleapiclient.errors import HttpError

def scrape_toucan_docs(drive_service):
    base_url = "https://docs.toucan.earth/"
    content_list = []

    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Error fetching data from {base_url}: {response.status_code}")
        return None

    main_soup = BeautifulSoup(response.text, 'html.parser')
    links = main_soup.find_all('a', href=True)
    for link in links:
        if link['href'].startswith('/'):
            page_url = base_url + link['href'][1:]
            page_content = scrape_page_content(page_url, drive_service)
            if page_content:
                content_list.append(page_content)

    return "\n".join(content_list)

def scrape_page_content(page_url, drive_service):
    response = requests.get(page_url)
    if response.status_code != 200:
        print(f"Error fetching data from {page_url}: {response.status_code}")
        return None

    page_soup = BeautifulSoup(response.text, 'html.parser')
    page_content = []

    # Bỏ qua nội dung có class cụ thể
    for el in page_soup.find_all(class_="flex-1 text-sm text-dark/6 dark:text-light/5"):
        el.extract()

    # Bỏ qua nội dung có class cụ thể
    for el in page_soup.find_all(class_="group/headerlogo flex-1 flex flex-row items-center shrink-0"):
        el.extract()

    # Xử lý hình ảnh
    images = page_soup.find_all('img')
    for img in images:
        img_url = img['src']
        if not img_url.startswith('http'):
            img_url = 'https:' + img_url
        
        img_response = requests.get(img_url)
        if img_response.status_code == 200:
            file_metadata = {
                'name': img_url.split('/')[-1],
                'mimeType': 'image/jpeg'
            }
            media = MediaInMemoryUpload(img_response.content, mimetype='image/jpeg')
            img_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            image_id = img_file.get('id')
            page_content.append({
                'insertInlineImage': {
                    'location': {'index': len(page_content)},
                    'uri': f'https://drive.google.com/uc?id={image_id}',
                    'objectSize': {
                        'height': {'magnitude': 100, 'unit': 'PT'},
                        'width': {'magnitude': 100, 'unit': 'PT'},
                    }
                }
            })

    # Xử lý Headings
    headers = page_soup.find_all(['h1', 'h2', 'h3'])
    for header in headers:
        header_level = header.name[1]
        header_text = header.get_text(strip=True)
        page_content.append({'insertText': {'location': {'index': len(page_content)}, 'text': f"{'#' * int(header_level)} {header_text}\n"}})

    # Xử lý văn bản
    paragraphs = page_soup.find_all('p')
    for para in paragraphs:
        para_text = para.get_text(strip=True)
        if para_text:
            page_content.append({'insertText': {'location': {'index': len(page_content)}, 'text': f"{para_text}\n"}})

    return page_content

def main():
    SERVICE_ACCOUNT_FILE = 'credentials.json'
    SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    docs_service = build('docs', 'v1', credentials=credentials)
    drive_service = build('drive', 'v3', credentials=credentials)

    document = {
        'title': 'Nội dung từ Toucan Docs'
    }
    doc = docs_service.documents().create(body=document).execute()
    document_id = doc.get('documentId')

    content = scrape_toucan_docs(drive_service)
    
    requests = []
    if content:
        requests.extend(content)

    try:
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
        print(f"Tài liệu đã được tạo với ID: {document_id}")

        permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': 'bdpjournal@gmail.com'  
        }
        drive_service.permissions().create(fileId=document_id, body=permission).execute()
        print(f"Tài liệu đã được chia sẻ với email: {permission['emailAddress']}")

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
