from flask import Flask, request, jsonify
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

@app.route("/parse", methods=["POST"])
def parse():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "URL not provided"}), 400

        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--headless=new')

        driver = uc.Chrome(options=options)
        driver.get(url)
        time.sleep(6)
        html = driver.page_source
        driver.quit()

        soup = BeautifulSoup(html, "lxml")

        title = soup.find("h1", class_=lambda c: c and "text-dark" in c)
        title_text = title.get_text(strip=True) if title else "❌ Не найдено"

        link_tag = soup.find("a", href=lambda h: h and h.startswith("https://t.me/"))
        tg_link = link_tag["href"] if link_tag else "❌ Не найдена"

        desc_block = soup.find("p", class_="card-text mt-3")
        description = "❌ Не найдено"
        if desc_block:
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)