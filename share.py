from googleapiclient.discovery import build
from google.oauth2 import service_account

# Thay đổi đường dẫn tới tệp JSON của bạn
SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

# Xác thực
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Tạo dịch vụ Drive
service = build('drive', 'v3', credentials=creds)

# ID tài liệu bạn đã tạo
document_id = '1kgD7wKB-jSaHAyaOnFV-FqGUNBhpFKoYlYH88tAf3sg'

# Chia sẻ tài liệu
permission = {
    'type': 'user',
    'role': 'writer',  # Bạn có thể thay đổi thành 'reader' nếu chỉ muốn đọc
    'emailAddress': 'bdpjournal@gmail.com'  # Thay đổi thành email gốc của bạn
}

service.permissions().create(
    fileId=document_id,
    body=permission,
    fields='id'
).execute()
