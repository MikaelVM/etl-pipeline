from utils import DATA_DIR
import wget
from bs4 import BeautifulSoup
import requests

class FileDownloader:

    def download_files_with_suffix(self, *, file_urls: list[str], suffix: str, output_path: str) -> None:
        # Download files that end with the specified suffix
        for url in file_urls:
            if url.endswith(suffix):
                self.download_file(url, output_path)

    @staticmethod
    def find_files(url: str) -> list[str]:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        print(response.status_code)
        print(response.headers.get("Content-Type"))
        print(response.text[:1000])

        # Parse the HTML content using BeautifulSoup
        print(f"Parsing HTML content from {url} with the following content:")
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all links in the page
        links = soup.find_all('a')
        print(f"Found {len(links)} links in the HTML content.")

        # Extract the href attribute from each link
        file_urls = [link.get('href') for link in links if link.get('href')]

        return file_urls

    @staticmethod
    def download_file(url, output_path):
        # Download the file from the URL and save it to the specified output path
        try:
            print(f"Downloading file from {url} to {output_path}...")
            wget.download(url, out=output_path)
            print(f"File downloaded successfully to {output_path}.")
        except Exception as e:
            print(f"Error downloading file from {url}: {e}")


if __name__ == "__main__":
    url_main = "http://aisdata.ais.dk"
    output_path = DATA_DIR / "raw" / "ais"
    file_downloader = FileDownloader()

    print("Finding files to download...")
    file_urls = file_downloader.find_files(url_main)
    print(f"Found {len(file_urls)} files to download.")



