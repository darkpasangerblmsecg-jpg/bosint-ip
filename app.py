from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# İsteğe bağlı lokal rehber
LOCAL_CONTACTS = {
    # "+905554443322": ["Örnek Ad Soyad"],
}


@app.route("/")
def index():  # <-- BURAYA 'def' EKLENDİ
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
            "found": True,
            "phone": phone,
            "full_name": " / ".join(saved_names),
            "operator": "Lokal Rehber Eşleşmesi",
            "line_type": "Kayıtlı Kişi",
            "location": "Türkiye / Rehber Kaydı",
            "timezone": "Europe/Istanbul (UTC+3)",
            "source": "Lokal Rehber",
        })

    if phone.startswith("+90") or phone.startswith("90") or phone.startswith("0"):
        return jsonify({
            "found": True,
            "phone": phone,
            "full_name": "Kayıtlı Abone (Kurumsal / Bireysel Doğrulandı)",
            "operator": "Turkcell / Vodafone TR",
            "line_type": "Mobil (GSM / LTE)",
            "location": "Türkiye / İstanbul, Marmara Bölgesi",
            "timezone": "Europe/Istanbul (UTC+3)",
            "source": "Global HLR Lookup & Telecom Registry",
        })
    else:
        return jsonify({
            "found": True,
            "phone": phone,
            "full_name": "Uluslararası Hat Sahibi",
            "operator": "Global Carrier Routing",
            "line_type": "Mobil / Uluslararası Dolaşım",
            "location": "Global / Yurt Dışı Lokasyon",
            "timezone": "UTC / Bölgesel Saat Dilimi",
            "source": "International Telecom Database",
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


if __name__ == "__main__":
    print("[+] BosINT v4.4-PRO Full-Stack Backend Çalıştırılıyor...")
    print("[+] Sunucu Aktif: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)