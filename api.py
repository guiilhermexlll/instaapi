from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# Cookies da sessão logada (já autenticada)
COOKIES = {
    "csrftoken": "yBE0gLfLlSG2OADk3EFCkM",
    "datr": "44RkaAql36k7tgldbwVulUxK",
    "ds_user_id": "73861894039",
    "ig_did": "C6223CC8-F9F9-47D6-A7B8-CA5519EB9A16",
    "ig_nrcb": "1",
    "mid": "aGSE4wAEAAEgj9IEMeRGPsLFdtH-",
    "ps_l": "1",
    "ps_n": "1",
    "rur": 'NCG,73861894039,1783109112:01fedb9c2e271152572d212b4b314f7788d55b2ea62d318cc2c4a92f6fafd8df889a3031',
    "sessionid": "73861894039:oA1nMnpip2oFg4:10:AYerR_HME7RUj6Y26xARn_to-HJVM3zZn_Kkg4XXgg",
    "wd": "400x821"
}

# Simulando acesso via celular Samsung Android
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.196 Mobile Safari/537.36",
    "X-IG-App-ID": "936619743392459",  # ID do app web do Instagram
}

@app.route("/dados")
def obter_dados():
    usuario = request.args.get("usuario")
    if not usuario:
        return jsonify({"erro": "Parâmetro 'usuario' é obrigatório"}), 400

    if usuario.startswith("http"):
        usuario = usuario.rstrip("/").split("/")[-1]

    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={usuario}"

    try:
        res = requests.get(url, headers=HEADERS, cookies=COOKIES)
        if res.status_code != 200:
            return jsonify({"erro": "Falha ao acessar o Instagram", "status_code": res.status_code})

        data = res.json()
        user = data.get("data", {}).get("user", {})

        if not user:
            return jsonify({"erro": "Perfil não encontrado ou bloqueado"})

        resultado = {
            "usuario": user.get("username"),
            "nome": user.get("full_name"),
            "seguidores": user.get("edge_followed_by", {}).get("count"),
            "seguindo": user.get("edge_follow", {}).get("count"),
            "publicacoes": user.get("edge_owner_to_timeline_media", {}).get("count"),
            "bio": user.get("biography"),
            "verificado": user.get("is_verified"),
            "foto_perfil": user.get("profile_pic_url_hd"),
            "link_bio": user.get("external_url"),
            "privado": user.get("is_private"),
            "categoria": user.get("category_name"),
        }

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    print("🔐 API ativa em: http://localhost:5000/dados?usuario=usuario")
    app.run(host="0.0.0.0", port=5000, debug=True)
