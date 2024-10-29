from googleapiclient.discovery import build

# Sử dụng API Key của bạn
API_KEY = 'AIzaSyBLU7xeTK_rrIywatvDGuEFCgeBWnBm23A'  # Thay thế bằng API Key của bạn
service = build('docs', 'v1', developerKey=API_KEY)

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
