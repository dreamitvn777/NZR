from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Các phạm vi yêu cầu
SCOPES = ['https://www.googleapis.com/auth/documents']

# Xác thực và tạo dịch vụ
flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json', SCOPES)  # Thay thế bằng đường dẫn đến tệp JSON của bạn
creds = flow.run_console()  # Sử dụng phương thức này để lấy mã xác thực qua console

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
