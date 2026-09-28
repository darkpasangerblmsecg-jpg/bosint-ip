from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

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
            response = requests.get(target_url, headers=headers, timeout=5)
            if response.status_code == 200:
                found_sites[platform] = target_url
        except requests.exceptions.RequestException:
            continue

    return jsonify({
        "username": username,
        "found_sites": found_sites
    })

# Telefon numarası sorgulama API uç noktası (İsim, Soyisim ve Operatör döner)
@app.route('/search-phone', methods=['GET'])
def search_phone():
    phone = request.args.get('phone')
    if not phone:
        return jsonify({"error": "Telefon numarası gereklidir."}), 400

    # Örnek Veritabanı / Simülasyon Verisi (Burayı kendi veri kaynağınla değiştirebilirsin)
    # İleride buraya SQL veya büyük bir JSON/CSV okuma entegre edebilirsin.
    mock_database = {
        "+905554443322": {
            "name": "Eymen Abdullah",
            "operator": "Vodafone",
            "city": "İstanbul",
            "source": "Breach Database v4"
        }
    }

    # Numarayı veritabanında ara (Boşlukları temizleyerek)
    clean_phone = phone.strip()
    if clean_phone in mock_database:
        data = mock_database[clean_phone]
        return jsonify({
            "found": True,
            "phone": clean_phone,
            "full_name": data["name"],
            "operator": data["operator"],
            "city": data["city"],
            "source": data["source"]
        })
    else:
        return jsonify({
            "found": False,
            "phone": clean_phone,
            "message": "Bu numaraya ait sızıntı/kayıt bulunamadı."
        })

@app.route('/', methods=['GET'])
def home():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)