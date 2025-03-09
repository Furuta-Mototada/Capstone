import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json


def fetch_bills(url):
    # Download the page
    response = requests.get(url)
    response.encoding = response.apparent_encoding  # Ensure correct encoding
    html = response.text

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Define the captions we are interested in.
    table_captions = [
        "衆法の一覧",
        "参法の一覧",
        "閣法の一覧",
        "予算の一覧",
        "条約の一覧",
        "承認の一覧",
        "承諾の一覧",
        "決算その他",
    ]

    results = {}

    # Find all tables and filter by caption text.
    tables = soup.find_all("table")
    for table in tables:
        caption_tag = table.find("caption")
        if caption_tag:
            caption_text = caption_tag.get_text(strip=True)
            if caption_text in table_captions:
                results[caption_text] = []
                # Process each row, skipping header rows if they contain <th>
                rows = table.find_all("tr")
                for row in rows:
                    if row.find("th"):
                        continue  # skip header row
                    cols = row.find_all("td")
                    if len(cols) < 5:
                        continue  # not enough columns to contain all fields

                    bill = {}
                    bill["提出回次"] = cols[0].get_text(strip=True)
                    bill["番号"] = cols[1].get_text(strip=True)
                    bill["議案件名"] = cols[2].get_text(strip=True)
                    bill["審議状況"] = cols[3].get_text(strip=True)

                    # Extract 経過情報 and link if available.
                    keika_info_tag = cols[4]
                    bill["経過情報"] = keika_info_tag.get_text(strip=True)
                    link = keika_info_tag.find("a")
                    if link and link.has_attr("href"):
                        bill["経過情報リンク"] = urljoin(url, link["href"])

                    # Optional 本文情報 if a 6th column exists.
                    if len(cols) > 5:
                        honbun_info_tag = cols[5]
                        bill["本文情報"] = honbun_info_tag.get_text(strip=True)
                        link = honbun_info_tag.find("a")
                        if link and link.has_attr("href"):
                            bill["本文情報リンク"] = urljoin(url, link["href"])

                    results[caption_text].append(bill)
    return results


if __name__ == "__main__":
    url = "https://www.shugiin.go.jp/internet/itdb_gian.nsf/html/gian/menu.htm"
    bills_data = fetch_bills(url)

    # For demonstration, we pretty-print the results as JSON.
    print(json.dumps(bills_data, ensure_ascii=False, indent=2))
