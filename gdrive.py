from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

# Các phạm vi cần thiết
SCOPES = ['https://www.googleapis.com/auth/documents']

# Lấy thông tin xác thực
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)

# Sử dụng phương thức console để xác thực
creds = flow.run_console()

# Tạo dịch vụ Google Docs
service = build('docs', 'v1', credentials=creds)

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
