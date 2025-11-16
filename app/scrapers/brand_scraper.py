from bs4 import BeautifulSoup
import requests

def scrape_hbx_brands():
    url = "https://hbx.com/brands"
    response = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
    })
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    brands = []
    sections = soup.select("div.py-lg.text-lg.border-b")
    for section in sections:
        # Each letter group (A, B, C, etc.)
        letter = section.select_one("h4").get_text(strip=True)

        # Get all <a> tags within <li> elements
        links = section.select("ul li a")

        for a in links:
            name = a.get_text(strip=True)
            href = a.get("href")
            # Ensure it's a valid brand URL
            if href and href.startswith("http"):
                brands.append({
                    "letter": letter,
                    "name": name,
                    "url": href,
                    # "official_site": official_site
                })

    # print(f"Found {len(brands)} brands")
    # print(brands[:10])
    return brands

# def get_official_site_url(brand_name):
#     url = f"https://api.brandfetch.io/v2/brands/{brand_name}.com"
#     headers = {"Authorization": "Bearer"}
#     response = requests.get(url, headers=headers)
#     if response.ok:
#         data = response.json()
#         print(data)
#         return data.get("link")


if __name__ == "__main__":
    scrape_hbx_brands()
    official_site = get_official_site_url("AIAIAI")
