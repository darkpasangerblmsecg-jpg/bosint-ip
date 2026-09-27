from flask import Flask, request, jsonify, send_from_directory
import json
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

# Arayüzü doğrudan sunmak için root rota
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/search', methods=['GET'])
def search():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Kullanıcı adı girilmedi"}), 400

    try:
        with open('wmn-data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            sites = data.get('sites', [])
    except Exception as e:
        return jsonify({"error": f"Veritabanı okunamadı: {str(e)}"}), 500

    # SADECE taranmasını istediğin popüler/kaliteli platformlar (Whitelist)
    TARGET_SITES = [
        "GitHub", "Twitter", "X", "Instagram", "Reddit", "TikTok", 
        "YouTube", "Steam", "Telegram", "Medium", "LinkedIn", 
        "Pinterest", "SoundCloud", "Twitch", "Spotify", "Discord",
        "Facebook", "Snapchat", "Substack", "Patreon", "Kick"
    ]

    results = {}

    def check_site(site):
        name = site.get("name")
        
        # Whitelist kontrolü
        if name not in TARGET_SITES:
            return None

        uri_check = site.get("uri_check")
        if not name or not uri_check:
            return None
        
        target_url = uri_check.replace("{account}", username)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        try:
            response = requests.get(target_url, headers=headers, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                return (name, target_url)
        except:
            pass
        return None

    # Çoklu iş parçacığıyla hızlı tarama
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(check_site, site) for site in sites]
        for future in as_completed(futures):
            res = future.result()
            if res:
                results[res[0]] = res[1]

    return jsonify({"found_sites": results})

if __name__ == '__main__':
    # Render'ın atadığı portu otomatik yakalar, yerelde ise 5000 portunu kullanır
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)