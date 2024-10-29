from googleapiclient.discovery import build
from google.oauth2 import service_account

# Đường dẫn tới tệp JSON của tài khoản dịch vụ
SERVICE_ACCOUNT_FILE = 'NZR/credentials.json'
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

# Cập nhật tài liệu với nội dung
service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
print(f"Tài liệu đã được tạo với ID: {document_id}")
