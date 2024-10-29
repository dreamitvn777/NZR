import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

# Hàm để lấy nội dung từ trang web
def scrape_toucan_docs():
    url = "https://docs.toucan.earth/"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching data from {url}: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    content = "\n".join([p.get_text() for p in paragraphs])  
    return content

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

# Lấy nội dung từ trang web
content = scrape_toucan_docs()

if content:
    # Thêm nội dung vào tài liệu
    requests = [
        {'insertText': {'location': {'index': 1}, 'text': content}}
    ]
    docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    print(f"Tài liệu đã được tạo với ID: {document_id}")

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
    print(f"Tài liệu đã được chia sẻ với email: {permission['emailAddress']}")
else:
    print("Không có nội dung để thêm vào tài liệu.")
