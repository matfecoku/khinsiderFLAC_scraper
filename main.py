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


FLAC_ID = 6
FLAC_DOWNLOAD_ID = 4
DELAY = -1  # in seconds, increase in case of rate limiting


def get_page(url, stream):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    }
    return requests.get(url, headers=headers)


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
    main_page_content = get_page(SONG_PAGE_URL, False).text
    print("Loaded main page!")
    print("Parsing main page...")
    parser = get_parser(main_page_content)
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

    temp_num = 0
    for p in page_content.find_all("p"):
        if temp_num == FLAC_DOWNLOAD_ID:
            return p.find("a").get("href")
        temp_num += 1


def handle_subpage(url, id):
    subpage_print("Loading subpage...", id)
    subpage_content = get_page(BASE_URL + url, False).text
    parser = get_parser(subpage_content)
    subpage_print("Loaded subpage!", id)
    return parse_subpage(parser, id)


def handle_subpages(subpage_links):
    subpage_id = 0
    temp_delay = 0
    for subpage in subpage_links:
        subpage_id += 1
        subpage_data = handle_subpage(subpage, subpage_id)
        subpage_print("Downloading song...", subpage_id)
        download_file(subpage_data)
        subpage_print("Downloaded song!", subpage_id)
        if temp_delay == DELAY and temp_delay != -1:
            sleep(3)
            temp_delay = 0
        temp_delay += 1


def get_album_name():
    path = urlparse(SONG_PAGE_URL).path
    album_name = unquote(path.split("/")[-1])
    formatted_name = album_name.replace("-", " ").title()
    return formatted_name


def construct_file_path(url):
    filename = unquote(url.split("/")[-1])
    path = "downloads/"
    path += str(date.today())
    path += "/"
    path += get_album_name()
    path += "/"
    path += filename
    return path


def check_download_directory(path):
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)


def download_file(url):
    resp = get_page(url, True)
    download_path = construct_file_path(url)
    check_download_directory(download_path)
    with open(str(download_path), "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)


def handle_download_links(download_links):
    for link in download_links:
        download_file(link)


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
