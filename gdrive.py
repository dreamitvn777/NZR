import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Hàm để lấy nội dung từ trang web
def scrape_toucan_docs():
    url = "https://docs.toucan.earth/"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching data from {url}: {response.status_code}")
        return None

    content = response.text
    return content
    
# Đường dẫn tới tệp JSON của tài khoản dịch vụ
SERVICE_ACCOUNT_FILE = 'credentials.json'  # Thay thế bằng đường dẫn đến tệp JSON của bạn
SCOPES = ['https://www.googleapis.com/auth/documents']

# Xác thực với tài khoản dịch vụ
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Tạo dịch vụ Google Docs
service = build('docs', 'v1', credentials=credentials)

# Tạo tài liệu mới
document = {
    'title': 'Nội dung từ Toucan Docs'
}
doc = service.documents().create(body=document).execute()
document_id = doc.get('documentId')

# Thêm nội dung vào tài liệu
content = 'Nội dung bạn đã sao chép từ Toucan Docs'  # Thay thế bằng nội dung thực tế
requests = [
    {'insertText': {'location': {'index': 1}, 'text': content}}
]

service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
print(f"Tài liệu đã được tạo với ID: {document_id}")

if __name__ == "__main__":
    # Lấy nội dung từ trang web
    content = scrape_toucan_docs()
