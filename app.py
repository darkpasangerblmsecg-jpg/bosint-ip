from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import os
import phonenumbers
from phonenumbers import carrier, geocoder, timezone, number_type

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

@app.route('/search-phone', methods=['GET'])
def search_phone():
    phone = request.args.get('phone')
    if not phone:
        return jsonify({"error": "Telefon numarası gereklidir."}), 400

    clean_phone = phone.strip()

    try:
        parsed_number = phonenumbers.parse(clean_phone)
        
        if not phonenumbers.is_valid_number(parsed_number):
            return jsonify({
                "found": False,
                "phone": clean_phone,
                "message": "Geçersiz veya hatalı telefon numarası formatı."
            })

        location = geocoder.description_for_number(parsed_number, "tr") or "Küresel / Belirtilmemiş"
        
        carrier_name = carrier.name_for_number(parsed_number, "tr")
        if not carrier_name:
            carrier_name = "Operatör Bilgisi Gizli veya Numara Taşınmış"

        n_type = number_type(parsed_number)
        if n_type == phonenumbers.PhoneNumberType.MOBILE:
            line_type = "Mobil Hat (Cellular)"
        elif n_type == phonenumbers.PhoneNumberType.FIXED_LINE:
            line_type = "Sabit Hat (Landline)"
        else:
            line_type = "VoIP / Sanal / Diğer Hat"

        tzs = timezone.time_zones_for_number(parsed_number)
        timezone_str = tzs[0] if tzs else "Bilinmiyor"

        formatted_num = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

        return jsonify({
            "found": True,
            "phone": formatted_num,
            "full_name": "Kayıtlı Abone (KVKK / Gizli)",
            "operator": carrier_name,
            "line_type": line_type,
            "location": location,
            "timezone": timezone_str,
            "source": "Global Telecom & Metadata Engine"
        })

    except Exception as e:
        return jsonify({
            "found": False,
            "phone": clean_phone,
            "message": "Numara analiz edilemedi: Hatalı format."
        })

@app.route('/', methods=['GET'])
def home():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)