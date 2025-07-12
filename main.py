from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import time

app = Flask(__name__)

@app.route('/')
def index():
    return "✅ TGStat Parser работает!"

@app.route('/parse', methods=['POST'])
def parse():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'Не передан параметр url'}), 400

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = uc.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(6)
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")

        # Название канала
        title = soup.find("h1", class_=lambda c: c and "text-dark" in c)
        title_text = title.get_text(strip=True) if title else ""

        # Ссылка на Telegram
        link_tag = soup.find("a", href=lambda h: h and h.startswith("https://t.me/"))
        tg_link = link_tag["href"] if link_tag else ""

        # Описание
        desc_block = soup.find("p", class_="card-text mt-3")
        description = ""
        if desc_block and desc_block.parent:
            parent = desc_block.parent
            parts = []
            started = False
            for tag in parent.children:
                if tag == desc_block:
                    started = True
                    continue
                if started:
                    if getattr(tag, "name", None) == "div":
                        break
                    if getattr(tag, "name", None) == "br":
                        parts.append("\n")
                    else:
                        parts.append(tag.get_text(strip=True) if hasattr(tag, "get_text") else str(tag))
            description = "\n".join(filter(None, [line.strip() for line in parts])).strip()

        return jsonify({
            "title": title_text,
            "telegram_link": tg_link,
            "description": description
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
