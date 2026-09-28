from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # Arayüzün farklı bir porttan/domainden istek atabilmesi için CORS aktif edilir

# Örnek popüler platformlar ve kontrol linkleri (Username OSINT mantığı)
SUPPORTED_PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Instagram": "https://www.instagram.com/{}",
    "Twitter": "https://twitter.com/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "Pinterest": "https://tr.pinterest.com/{}/",
    "Steam": "https://steamcommunity.com/id/{}",
    "Telegram": "https://t.me/{}"
}

@app.route('/search', methods=['GET'])
def search_username():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Kullanıcı adı parametresi gereklidir."}), 400

    found_sites = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    for platform, url_template in SUPPORTED_PLATFORMS.items():
        target_url = url_template.format(username)
        try:
            # Siteleri kontrol et (Timeout süresi kısa tutulur ki hızlı yanıt dönsün)
            response = requests.get(target_url, headers=headers, timeout=5)
            
            # Genellikle 200 dönüyorsa profil mevcuttur (Platforma göre özelleştirilebilir)
            if response.status_code == 200:
                found_sites[platform] = target_url
        except requests.exceptions.RequestException:
            # Bağlantı hatası veya zaman aşımı durumunda pas geçilir
            continue

    return jsonify({
        "username": username,
        "found_sites": found_sites
    })

@app.route('/', methods=['GET'])
def home():
    # Artık ana dizine girildiğinde doğrudan index.html arayüzünü sunar
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)