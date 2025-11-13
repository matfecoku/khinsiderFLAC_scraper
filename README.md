# Khinsider FLAC Album Downloader

Downloads **FLAC albums** from [Khinsider](https://downloads.khinsider.com/) by parsing the album page and automatically downloading each song.

## Features

- Scrapes the Khinsider album page for all **FLAC download links**
- Automatially downloads all songs in an **organized folder structure**
- Creates folders by **album name** and **date** for easy organization

## Requirements
- Python 3.10 or higher
- Dependencies listed in "requirements.txt"

## Usage
1. Clone the repository and navigate to the project folder.
2. Open "main.py" and set the SONG_PAGE_URL variable to the desired album
  Optional:
  Set the DELAY variable (in seconds) to avoid rate limiting
3. Run "main.py"

## How it works
- Fetches the main album page using **HTTP requests**.
- Parses the page with **BeautifulSoup** to extract song subpage links.
- Visits each subpage to obtain the **direct FLAC download URL**.
- Downloads each song while maintaining a **clean folder hierarchy**.
- Uses a **User-Agent header** to mimic a browser request and avoid blocks.

## Notes
- Adjust the **DELAY** variable to control pauses between downloads.
