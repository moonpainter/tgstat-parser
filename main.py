from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

@app.route("/parse", methods=["POST"])
def parse():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "No URL provided"}), 400

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Название канала
        title_tag = soup.find("h1", class_=lambda c: c and "text-dark" in c)
        title = title_tag.get_text(strip=True) if title_tag else ""

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
            "title": title,
            "telegram_link": tg_link,
            "description": description
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
