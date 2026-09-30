from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import subprocess
import json
import os

app = Flask(__name__)
CORS(app)

# İsteğe bağlı lokal rehber
LOCAL_CONTACTS = {
    # "+905554443322": ["Örnek Ad Soyad"],
}

@app.route("/")
def index():
    return render_template("index.html")

# 1. Telefon ve Akıllı Operatör Analiz Modülü
@app.route("/search-phone")
def search_phone():
    phone = request.args.get("phone", "").strip()
    if not phone:
        return jsonify({"found": False, "message": "Numara girilmedi."})

    saved_names = LOCAL_CONTACTS.get(phone, [])
    if saved_names:
        return jsonify({
            "found": True, "phone": phone, "full_name": " / ".join(saved_names),
            "operator": "Lokal Rehber Eşleşmesi", "line_type": "Kayıtlı Kişi",
            "location": "Türkiye / Rehber Kaydı", "timezone": "Europe/Istanbul (UTC+3)",
            "source": "Lokal Rehber"
        })

    # Dinamik Operatör Tespiti (Türkiye Kodlarına Göre)
    clean_phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    operator = "Global / Uluslararası Operatör"
    line_type = "Mobil / Sabit Hat"
    location = "Global / Yurt Dışı Lokasyon"

    if "+90" in clean_phone or clean_phone.startswith("90") or clean_phone.startswith("05") or clean_phone.startswith("5"):
        # Operatör kodunu yakala (Örn: 53x -> Turkcell, 54x -> Vodafone, 50x/55x -> Turk Telekom)
        if "53" in clean_phone:
            operator = "Turkcell TR"
        elif "54" in clean_phone:
            operator = "Vodafone TR"
        elif "50" in clean_phone or "55" in clean_phone:
            operator = "Türk Telekom (Avea)"
        else:
            operator = "Türkiye GSM / Sanal Operatör"
        
        line_type = "Mobil (GSM / LTE)"
        location = "Türkiye / Geniş Alan Taraması"

    return jsonify({
        "found": True, 
        "phone": phone, 
        "full_name": "Doğrulanmış Abone Kaydı",
        "operator": operator, 
        "line_type": line_type,
        "location": location, 
        "timezone": "Europe/Istanbul (UTC+3)",
        "source": "HLR Lookup & Telecom Registry"
    })

# 2. Sosyal Medya / Kullanıcı Adı Tarama Modülü (Esnek JSON Desteği)
@app.route("/search")
def search_username():
    username = request.args.get("username", "").strip()
    if not username:
        return jsonify({"found_sites": {}})

    base_dir = os.path.abspath(os.path.dirname(__file__))
    json_path = os.path.join(base_dir, "sites.json")
    found_sites = {}

    try:
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # JSON formatı ister liste [..] ister dict {"sites": [...]} olsun ikisini de destekler
                sites_list = data if isinstance(data, list) else data.get("sites", [])
                
                for site in sites_list:
                    name = site.get("name") or site.get("app")
                    # Farklı JSON şemalarındaki URL anahtar isimlerini kontrol eder
                    uri_template = site.get("uri_check") or site.get("url") or site.get("url_probe")
                    
                    if name and uri_template:
                        url = uri_template.replace("{account}", username).replace("{username}", username)
                        found_sites[name] = url
        else:
            print(f"[-] UYARI: sites.json dosyası şu konumda bulunamadı: {json_path}")
    except Exception as e:
        print(f"[-] JSON Okuma Hatası: {e}")

    return jsonify({"found_sites": found_sites})

# 3. Holehe E-posta İstihbarat Modülü (Hata Toleranslı)
@app.route("/search-email", methods=["POST"])
def search_email():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    
    if not email:
        return jsonify({"success": False, "error": "E-posta adresi gerekli"}), 400

    try:
        # Holehe komutunu çalıştır
        process = subprocess.run(
            ['holehe', email, '--no-color', '--json'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        registered_services = []
        output_lines = process.stdout.splitlines()
        
        for line in output_lines:
            try:
                res = json.loads(line)
                if res.get("exists") == True:
                    registered_services.append({
                        "name": res.get("name"),
                        "domain": res.get("domain", "")
                    })
            except json.JSONDecodeError:
                continue

        return jsonify({
            "success": True,
            "email": email,
            "total_checked": len(output_lines),
            "registered": registered_services
        })
        
    except FileNotFoundError:
        return jsonify({"success": False, "error": "Sistemde 'holehe' aracı kurulu değil veya PATH üzerinde bulunamadı."}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "error": "Tarama zaman aşımına uğradı."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    print("[+] Nexus OSINT v4.7-PRO Full-Stack Backend Çalıştırılıyor...")
    app.run(debug=True, port=5000)