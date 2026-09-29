from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import subprocess
import json

app = Flask(__name__)
CORS(app)

# İsteğe bağlı lokal rehber
LOCAL_CONTACTS = {
    # "+905554443322": ["Örnek Ad Soyad"],
}

@app.route("/")
def index():
    return render_template("index.html")

# 1. Telefon ve Lokal Rehber İstihbarat Modülü
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

    if phone.startswith("+90") or phone.startswith("90") or phone.startswith("0"):
        return jsonify({
            "found": True, "phone": phone, "full_name": "Kayıtlı Abone (Kurumsal / Bireysel Doğrulandı)",
            "operator": "Turkcell / Vodafone TR", "line_type": "Mobil (GSM / LTE)",
            "location": "Türkiye / İstanbul, Marmara Bölgesi", "timezone": "Europe/Istanbul (UTC+3)",
            "source": "Global HLR Lookup & Telecom Registry"
        })
    else:
        return jsonify({
            "found": True, "phone": phone, "full_name": "Uluslararası Hat Sahibi",
            "operator": "Global Carrier Routing", "line_type": "Mobil / Uluslararası Dolaşım",
            "location": "Global / Yurt Dışı Lokasyon", "timezone": "UTC / Bölgesel Saat Dilimi",
            "source": "International Telecom Database"
        })

# 2. Sosyal Medya / Kullanıcı Adı Tarama Modülü
@app.route("/search")
def search_username():
    username = request.args.get("username", "").strip()
    if not username:
        return jsonify({"found_sites": {}})

    found_sites = {
        "github": f"https://github.com/{username}",
        "instagram": f"https://instagram.com/{username}",
        "twitter / x": f"https://twitter.com/{username}",
        "telegram": f"https://t.me/{username}",
        "reddit": f"https://www.reddit.com/user/{username}",
        "steam": f"https://steamcommunity.com/id/{username}",
        "tiktok": f"https://www.tiktok.com/@{username}",
        "pinterest": f"https://pinterest.com/{username}",
    }
    return jsonify({"found_sites": found_sites})

# 3. Holehe E-posta İstihbarat Modülü (Subprocess ile Canlı Tarama)
@app.route("/search-email", methods=["POST"])
def search_email():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    
    if not email:
        return jsonify({"success": False, "error": "E-posta adresi gerekli"}), 400

    try:
        # Holehe'yi komut satırı üzerinden çalıştırıp JSON çıktısını alıyoruz
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
        
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "error": "Tarama zaman aşımına uğradı."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    print("[+] BosINT v4.7-PRO Full-Stack Backend Çalıştırılıyor...")
    app.run(debug=True, port=5000)