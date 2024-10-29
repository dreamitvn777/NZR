import requests
import time
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Thiết lập logging
logging.basicConfig(level=logging.INFO)

# Hàm để lấy tất cả các link từ trang chính
def scrape_toucan_docs():
    base_url = "https://docs.toucan.earth/"
    response = requests.get(base_url)

    if response.status_code != 200:
        logging.error(f"Error fetching data from {base_url}: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Tìm tất cả các link trên trang
    links = [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)]

    # Lưu nội dung của tất cả các link với cấu trúc
    content_requests = []
    for link in links:
        try:
            page_response = requests.get(link)
            if page_response.status_code == 200:
                page_soup = BeautifulSoup(page_response.text, 'html.parser')
                
                # Lấy nội dung từ phần div theo yêu cầu
                main_content = page_soup.select_one('body > div:nth-of-type(1) > div > div > div > main')
                
                if main_content:
                    for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
                        # Xác định cấp độ Heading dựa vào thẻ HTML
                        if element.name.startswith('h') and element.name[1].isdigit():
                            heading_level = int(element.name[1])  # Lấy cấp độ heading từ thẻ
                            if 1 <= heading_level <= 6:
                                # Thêm phần nội dung dưới dạng Heading tương ứng
                                content_requests.append({
                                    'insertText': {
                                        'location': {'index': 1},
                                        'text': element.get_text() + "\n\n"
                                    }
                                })
                                content_requests.append({
                                    'updateParagraphStyle': {
                                        'range': {
                                            'startIndex': 1,
                                            'endIndex': 1 + len(element.get_text()) + 2
                                        },
                                        'paragraphStyle': {
                                            'namedStyleType': f'HEADING_{heading_level}'
                                        },
                                        'fields': 'namedStyleType'
                                    }
                                })
                        elif element.name == 'p':
                            # Thêm đoạn văn bản bình thường
                            content_requests.append({
                                'insertText': {
                                    'location': {'index': 1},
                                    'text': element.get_text() + "\n\n"
                                }
                            })
                else:
                    logging.warning(f"No main content found in {link}")

            else:
                logging.warning(f"Failed to fetch {link}: {page_response.status_code}")
            time.sleep(1)  # Tạm dừng 1 giây giữa các yêu cầu
        except Exception as e:
            logging.error(f"Error fetching data from {link}: {e}")

    return content_requests

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
content_requests = scrape_toucan_docs()

if content_requests:
    # Thêm nội dung vào tài liệu với các định dạng
    docs_service.documents().batchUpdate(documentId=document_id, body={'requests': content_requests}).execute()
    logging.info(f"Tài liệu đã được tạo với ID: {document_id}")

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
    logging.info(f"Tài liệu đã được chia sẻ với email: {permission['emailAddress']}")
else:
    logging.warning("Không có nội dung để thêm vào tài liệu.")
