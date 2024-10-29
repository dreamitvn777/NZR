import requests
from bs4 import BeautifulSoup

# Hàm để lấy nội dung từ trang web
def scrape_toucan_docs():
    url = "https://docs.toucan.earth/"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching data from {url}: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    # Lấy tiêu đề và nội dung
    title = soup.title.string
    content = ""
    
    # Giả định rằng nội dung chính nằm trong thẻ <main>
    main_content = soup.find("main")
    if main_content:
        content = main_content.get_text(separator="\n", strip=True)

    return title, content

# Hàm để gửi nội dung lên GitBook
def upload_to_gitbook(title, content):
    url = "https://api.gitbook.com/v1/spaces/YOUR_SPACE_ID/contents"
    headers = {
        "Authorization": "Bearer gb_api_oAvtSIG5tdvlmK7qrQEQQ8nrawdAf16BuNJ9TVZ9",
        "Content-Type": "application/json"
    }

    data = {
        "title": title,
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
