import shutil
import requests
from bs4 import BeautifulSoup
import json
import os
import logging
import tempfile

url="https://upcar.up.gov.in/en/page/advisory"

def download_pdf(url, temp_dir):
    print("f1")
    url="https://upcar.up.gov.in/"+url
    print("url>>", url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=".pdf")
            with open(temp_file.name, 'wb') as f:
                f.write(response.content)
            return temp_file.name
        else:
            logging.error(f"Failed to download PDF from {url}")
            return None
    except Exception as e:
        logging.error(f"Error downloading PDF: {e}")
        return None
    
def scraper():
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        download_link = soup.find('a', class_='btn btn-success btn-xs external')['href']
        uploading_date = soup.find('span', class_='pdf-details').find_all('strong')[-1].next_sibling.strip()
        data={
            "download_url":download_link,
            "date":uploading_date
        }

        return data

    except Exception as e:
        print(str(e))
        return {}

def move_json_to_history():
    dest_dir="history"
    os.makedirs(dest_dir, exist_ok=True)

    filename="latest.json"
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
        date = data.get('date')
        history_filename = f"{date}.json"
        dest_path = os.path.join(dest_dir, history_filename)
        shutil.move(filename, dest_path)
        print(f"Moved {filename} to {dest_path}")

if __name__ == "__main__":
    move_json_to_history()
