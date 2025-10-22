import requests
from bs4 import BeautifulSoup
from time import sleep
from urllib.parse import unquote, urlparse
from datetime import date
import os

BASE_URL = "https://downloads.khinsider.com"
SONG_PAGE_URL = (
    ""  # format: https://downloads.khinsider.com/game-soundtracks/album/album-name
)

DELAY = -1  # in seconds, increase in case of rate limiting
RETRIES = 3  # number of retries for network requests
RETRY_DELAY = 3  # seconds to wait before retrying

FLAC_ID = 6
FLAC_DOWNLOAD_ID = 4


def get_page(url, stream=False):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    }

    for attempt in range(RETRIES):
        try:
            response = requests.get(url, headers=headers, stream=stream, timeout=15)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"Failed to get {url} ({attempt + 1}/{RETRIES}: {e}.)")
            sleep(RETRY_DELAY)

    print(f"Could not fetch {url}.")
    return None


def get_parser(site_content):
    return BeautifulSoup(site_content, "html.parser")


def parse_main_page(parser):
    subpage_links = []
    song_list = parser.select_one("#songlist")

    for row in song_list.select("tr"):
        temp_num = 0
        for cell in row.find_all("td"):
            if temp_num == FLAC_ID:
                link = cell.find("a")
                if link and link.get("href"):
                    subpage_links.append(link.get("href"))
            temp_num += 1

    return subpage_links


def handle_main_page():
    print("Loading main page...")
    response = get_page(SONG_PAGE_URL)
    if not response:
        print("Failed to load main page. Exiting.")
        exit()
    print("Loaded main page!")
    print("Parsing main page...")
    parser = get_parser(response.text)
    print("Parsed main page!")
    print("Loading subpage links...")
    subpage_links = parse_main_page(parser)
    print("Loaded subpage links!")
    print("Found " + str(len(subpage_links)) + " links.")
    return subpage_links


def subpage_print(string, id):
    print("[" + str(id) + "] " + str(string))


def parse_subpage(parser, id):
    page_content = parser.select_one("#pageContent")
    if not page_content:
        return None

    temp_num = 0
    for p in page_content.find_all("p"):
        if temp_num == FLAC_DOWNLOAD_ID:
            link = p.find("a")
            if link and link.get("href"):
                return link.get("href")
        temp_num += 1
    return None


def handle_subpage(url, id):
    subpage_print("Loading subpage...", id)
    response = get_page(BASE_URL + url)
    if not response:
        subpage_print("Failed to load subpage!", id)
        return None
    parser = get_parser(response.text)
    subpage_print("Loaded subpage!", id)
    return parse_subpage(parser, id)


def handle_subpages(subpage_links):
    subpage_id = 0
    failed_downloads = []

    for subpage in subpage_links:
        subpage_id += 1
        try:
            subpage_data = handle_subpage(subpage, subpage_id)
            if not subpage_data:
                subpage_print("No download link found.", subpage_id)
                failed_downloads.append(subpage)
                continue

            subpage_print("Downloading song...", subpage_id)
            download_file(subpage_data)
            subpage_print("Downloaded song!", subpage_id)
        except Exception as e:
            subpage_print(f"Failed to download song: {e}", subpage_id)
            failed_downloads.append(subpage)

        if DELAY != -1:
            sleep(DELAY)

        if failed_downloads:
            print("Failed downloads:")
            for failed in failed_downloads:
                print(failed)


def get_album_name():
    path = urlparse(SONG_PAGE_URL).path
    album_name = unquote(path.split("/")[-1])
    formatted_name = album_name.replace("-", " ").title()
    return formatted_name


def construct_file_path(url):
    filename = unquote(url.split("/")[-1])
    path = os.path.join("downloads", str(date.today()), get_album_name(), filename)
    return path


def check_download_directory(path):
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)


def download_file(url):
    resp = get_page(url, True)

    if not resp:
        raise Exception("Failed to fetch file from URL")

    download_path = construct_file_path(url)
    check_download_directory(download_path)

    with open(str(download_path), "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)


def main():
    if SONG_PAGE_URL == "":
        print(
            f'WARNING: SONG_PAGE_URL variable must be set. Open "{BASE_URL}", find an album and paste its link into the variable.'
        )
        exit()
    subpage_links = handle_main_page()
    handle_subpages(subpage_links)
    print("Complete!")


if __name__ == "__main__":
    main()
