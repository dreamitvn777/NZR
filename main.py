import requests
from bs4 import BeautifulSoup

# Hàm để lấy nội dung từ trang web
def scrape_toucan_docs():
    url = "https://docs.toucan.earth/"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching data from {url}: {response.status_code}")
        return None, None

    soup = BeautifulSoup(response.content, "html.parser")

    # Lấy tiêu đề và nội dung
    title = soup.title.string if soup.title else "No title found"
    content = ""
    
    # Giả định rằng nội dung chính nằm trong thẻ <main>
    main_content = soup.find("main")
    if main_content:
        content = main_content.get_text(separator="\n", strip=True)
    else:
        print("No main content found")

    return title, content

# Hàm để gửi nội dung lên GitBook
def upload_to_gitbook(title, content):
    url = "https://api.gitbook.com/v1/spaces/fIM6QujbfhsNUfWQsQYG/contents"  # Thay YOUR_SPACE_ID bằng ID không gian của bạn
    headers = {
        "Authorization": "Bearer gb_api_5ZoA46F2gJqESyzB99U7hZXxcGm0oLSeihpTdu7K",  # Đảm bảo token hợp lệ
        "Content-Type": "application/json"
    }

    # Cấu trúc dữ liệu đúng với API GitBook
    data = {
        "title": title,
        "type": "page",  # Đảm bảo rằng loại nội dung đúng
        "content": content
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        print("Successfully uploaded to GitBook!")
    else:
        print(f"Failed to upload to GitBook: {response.status_code}, {response.text}")

if __name__ == "__main__":
    title, content = scrape_toucan_docs()
    if title and content:
        upload_to_gitbook(title, content)
    else:
        print("Failed to retrieve title or content.")
