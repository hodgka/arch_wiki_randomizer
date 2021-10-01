'''
A program that grabs a random page from the arch wiki. The script will try to 
'''
import argparse
import os
from typing import Any, List, Dict, Optional
import webbrowser

from bs4 import BeautifulSoup
import requests

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--languages', '-l', '--lang', nargs='*', default=['en'], help='Languages to look for an article in. If multiple languages are available, defaults to the first language')
    args = parser.parse_args()
    args.default_language = args.languages[0]
    args.base_path = 'https://wiki.archlinux.org/'
    return args


headers: Dict[str, str] = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

def get_index(base_path: str) -> Any:
    main_page: str = os.path.join(base_path, 'title/Main_page')
    req: requests.Response = requests.get(main_page, headers)
    return BeautifulSoup(req.content, 'html.parser')

def get_random_link(html: Any) -> str:
    for link in html('a'):
        href: str = link.get('href')
        if href and 'Special:Random' in href:
            return href
    raise Exception("No get random article link on page.")

def get_random_page(url: str, base_path: str) -> str:
    rand_url: str = os.path.join(base_path, url.lstrip('/'))
    req: requests.Response = requests.get(rand_url)
    url = req.url
    return url 

def get_translated_url(random_url: str, languages: List[str]) -> str:
    req: requests.Response = requests.get(random_url, headers)
    new_soup: Any = BeautifulSoup(req.content, 'html.parser')

    langs: Dict[str, str] = {}
    # get current_language
    page_lang: str = new_soup.find('div', {"id": 'mw-content-text'}).get("lang")
    langs[page_lang] = random_url
    
    # get other languages
    language_links: List[BeautifulSoup] = new_soup.find_all("li", {'class': 'interlanguage-link'})
    for li_link in language_links:
        language: str = li_link.a.get('lang')
        langs[language] = li_link.a.get('href')
    
    for lang in languages:
        link: Optional[str] = langs.get(lang)
        if link:
            return link
    raise ValueError(f"Could not find an acceptable language for the page: {random_url}.")

def main() -> None:
    args: argparse.Namespace = parse_args()
    
    html: Any = get_index(args.base_path)
    random_link: str = get_random_link(html)
    random_page: str = get_random_page(random_link, args.base_path)
    url: str = get_translated_url(random_page, args.languages)
    print(f'URL: {url}')
    webbrowser.open_new_tab(url)

if __name__ == '__main__':
    main()