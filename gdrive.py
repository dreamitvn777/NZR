import os.path
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

# Các phạm vi cần thiết
SCOPES = ['https://www.googleapis.com/auth/documents']

# Kiểm tra xem có tệp token.pickle không
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
else:
    # Nếu không có, yêu cầu xác thực
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)  # Sử dụng phương thức này để mở URL xác thực

    # Lưu thông tin xác thực để sử dụng sau này
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

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
