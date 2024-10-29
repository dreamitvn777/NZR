import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import io
import base64

# Hàm để lấy tất cả các link từ trang chính
def scrape_toucan_docs():
    base_url = "https://docs.toucan.earth/"
    response = requests.get(base_url)

    if response.status_code != 200:
        print(f"Error fetching data from {base_url}: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Tìm tất cả các link trên trang
    links = [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)]

    # Lưu nội dung của tất cả các link
    all_content = []
    for link in links:
        try:
            page_response = requests.get(link)
            if page_response.status_code == 200:
                page_soup = BeautifulSoup(page_response.text, 'html.parser')

                # Xóa phần "Last updated" và thời gian
                for element in page_soup.find_all(text=re.compile(r'Last updated')):
                    element.extract()

                # Tạo cấu trúc với Headings
                page_content = []
                page_content.append(f"\n\n\n# {page_soup.title.string.strip()}\n")  # Thêm tiêu đề của trang
                headers = page_soup.find_all(['h1', 'h2', 'h3'])
                for header in headers:
                    header_level = header.name[1]  # Lấy cấp độ từ tên thẻ (h1, h2, h3)
                    header_text = header.get_text(strip=True)
                    page_content.append(f"{'#' * int(header_level)} {header_text}\n")  # Thêm Heading
                
                # Thêm nội dung từ các đoạn văn
                paragraphs = page_soup.find_all('p')
                for p in paragraphs:
                    paragraph_text = p.get_text(strip=True)
                    page_content.append(paragraph_text + "\n")

                # Thêm hình ảnh và lưu vào danh sách
                images = page_soup.find_all('img')
                image_urls = []
                for img in images:
                    img_url = urljoin(base_url, img['src'])
                    image_urls.append(img_url)
                    page_content.append(f"![Image]({img_url})\n")  # Thêm ảnh

                all_content.append(''.join(page_content))  # Tích lũy nội dung của từng trang

                # Chèn ảnh vào tài liệu
                for img_url in image_urls:
                    insert_image_to_doc(img_url, doc, page_content)  # Chèn ảnh vào doc
            else:
                print(f"Failed to retrieve {link}: {page_response.status_code}")
        except Exception as e:
            print(f"Error fetching data from {link}: {e}")

    return '\n'.join(all_content)

# Hàm chèn hình ảnh vào tài liệu Google Docs
def insert_image_to_doc(image_url, document_id, page_content):
    try:
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            # Chuyển đổi hình ảnh thành base64
            base64_image = base64.b64encode(image_response.content).decode('utf-8')
            image_index = page_content.index(f"![Image]({image_url})")  # Tìm vị trí chèn
            requests = [
                {
                    'insertInlineImage': {
                        'location': {'index': image_index},
                        'uri': f'data:image/jpeg;base64,{base64_image}',
                        'objectSize': {'height': {'magnitude': 100, 'unit': 'PT'}, 'width': {'magnitude': 100, 'unit': 'PT'}}
                    }
                }
            ]
            docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
        else:
            print(f"Failed to retrieve image from {image_url}: {image_response.status_code}")
    except Exception as e:
        print(f"Error inserting image {image_url}: {e}")

# Đường dẫn tới tệp JSON của tài khoản dịch vụ
SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

# Xác thực với tài khoản dịch vụ
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Tạo dịch vụ Google Docs và Google Drive
docs_service = build('docs', 'v1', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)

# Tạo tài liệu mới
document = {
    'title': 'Nội dung từ Toucan Docs'
}
doc = docs_service.documents().create(body=document).execute()
document_id = doc.get('documentId')

# Lấy nội dung từ tất cả các link
content = scrape_toucan_docs()

if content:
    # Thêm nội dung vào tài liệu
    requests = [{'insertText': {'location': {'index': 1}, 'text': content}}]
    docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

    # Chia sẻ tài liệu với email gốc
    permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': 'bdpjournal@gmail.com'
    }

    drive_service.permissions().create(
        fileId=document_id,
        body=permission,
        fields='id'
    ).execute()
    print(f"Tài liệu đã được tạo với ID: {document_id} và đã được chia sẻ với email: {permission['emailAddress']}")

else:
    print("Không có nội dung để thêm vào tài liệu.")
