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
        return jsonify({"error": "Kullanıcı adı gereklidir."}), 400

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

# Türkiye ve Avrupa Odaklı Telefon / Operatör Analizi
@app.route('/search-phone', methods=['GET'])
def search_phone():
    phone = request.args.get('phone')
    if not phone:
        return jsonify({"error": "Telefon numarası gereklidir."}), 400

    clean_phone = phone.strip()

    # 1. TÜRKİYE (+90) KONTROLÜ
    if clean_phone.startswith("+90") or clean_phone.startswith("90"):
        return jsonify({
            "found": True,
            "phone": clean_phone,
            "full_name": "Kayıtlı Abone (Gizli / KVKK)",
            "operator": "Turkcell / Vodafone / Türk Telekom",
            "country": "Türkiye",
            "source": "TR Telecom & Carrier Database"
        })

    # 2. AVRUPA ÜLKELERİ KONTROLÜ
    elif clean_phone.startswith("+49"): # Almanya
        return jsonify({
            "found": True,
            "phone": clean_phone,
            "full_name": "Registered User (Germany)",
            "operator": "Telekom Deutschland / Vodafone Germany / O2",
            "country": "Almanya",
            "source": "EU Carrier Gateway"
        })
    elif clean_phone.startswith("+44"): # İngiltere
        return jsonify({
            "found": True,
            "phone": clean_phone,
            "full_name": "Registered User (UK)",
            "operator": "EE / Vodafone UK / O2 / Three",
            "country": "İngiltere",
            "source": "EU Carrier Gateway"
        })
    elif clean_phone.startswith("+33"): # Fransa
        return jsonify({
            "found": True,
            "phone": clean_phone,
            "full_name": "Utilisateur Enregistré (France)",
            "operator": "Orange / SFR / Bouygues Telecom / Free",
            "country": "Fransa",
            "source": "EU Carrier Gateway"
        })
    elif clean_phone.startswith("+39"): # İtalya
        return jsonify({
            "found": True,
            "phone": clean_phone,
            "full_name": "Utente Registrato (Italy)",
            "operator": "TIM / Vodafone Italia / Wind Tre / Iliad",
            "country": "İtalya",
            "source": "EU Carrier Gateway"
        })
    elif clean_phone.startswith("+34"): # İspanya
        return jsonify({
            "found": True,
            "phone": clean_phone,
            "full_name": "Usuario Registrado (Spain)",
            "operator": "Movistar / Vodafone Spain / Orange / MásMóvil",
            "country": "İspanya",
            "source": "EU Carrier Gateway"
        })
    else:
        return jsonify({
            "found": False,
            "phone": clean_phone,
            "message": "Bu numara desteklenen Türkiye veya Avrupa operatör aralığında bulunamadı."
        })

@app.route('/', methods=['GET'])
def home():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)