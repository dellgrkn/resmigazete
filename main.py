import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Telegram bot ayarları (GitHub Secrets'tan alınacak)
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHANNEL_ID = os.environ['TELEGRAM_CHANNEL_ID']

def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def temizle_telegram_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    izinli_tagler = ['b', 'i', 'u', 's', 'code', 'pre', 'a']
    for tag in soup.find_all(True):
        if tag.name not in izinli_tagler:
            tag.unwrap()
    return str(soup)

def get_latest_publications():
    driver = setup_selenium()
    url = "https://www.resmigazete.gov.tr/"
    try:
        driver.get(url)
        time.sleep(5)

        baslik_element = driver.find_element(By.CLASS_NAME, "text-white.text-center.text-sm-left")
        baslik = baslik_element.text if baslik_element else "Başlık bulunamadı"

        icerik_element = driver.find_element(By.CLASS_NAME, "container.gunluk-akis")
        raw_html = icerik_element.get_attribute("innerHTML") if icerik_element else "İçerik bulunamadı"
        temiz_icerik = temizle_telegram_html(raw_html)

        return [{
            'title': baslik,
            'icerik': temiz_icerik,
            'url': url
        }]
    finally:
        driver.quit()

def send_to_telegram(publication):
    icerik_duzenli = publication['icerik'].replace("––", "\n––")
    message = f"📢 <b>{publication['title']}</b>\n\n{icerik_duzenli}\n\n🔗 {publication['url']}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, data=payload)

def main():
    publications = get_latest_publications()
    if publications:
        for pub in publications:
            send_to_telegram(pub)

if __name__ == "__main__":
    main()
