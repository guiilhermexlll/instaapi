from flask import Flask, request, jsonify, render_template_string
import requests
import re

app = Flask(__name__)

COOKIES = {}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.196 Mobile Safari/537.36",
    "X-IG-App-ID": "936619743392459",
    "Referer": "https://www.instagram.com/accounts/login/",
    "X-Requested-With": "XMLHttpRequest"
}

# Página de login
HTML_LOGIN = '''
<!DOCTYPE html>
<html>
<head><title>Login Instagram</title></head>
<body>
  <h2>Login no Instagram</h2>
  <form method="POST">
    Usuário: <input type="text" name="username"><br>
    Senha: <input type="password" name="password"><br>
    <button type="submit">Login</button>
  </form>
</body>
</html>
'''

@app.route("/login", methods=["GET", "POST"])
def login_instagram():
    global COOKIES
    if request.method == "GET":
        return render_template_string(HTML_LOGIN)

    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        return "Usuário e senha são obrigatórios."

    session = requests.Session()
    session.headers.update(HEADERS)

    # Pegando token CSRF inicial
    resp = session.get("https://www.instagram.com/accounts/login/")
    csrf_token = session.cookies.get("csrftoken")

    payload = {
        "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:&:{password}",
        "username": username,
        "queryParams": {},
        "optIntoOneTap": "false"
    }

    session.headers.update({
        "X-CSRFToken": csrf_token
    })

    login_url = "https://www.instagram.com/accounts/login/ajax/"
    res = session.post(login_url, data=payload, allow_redirects=True)

    if res.status_code == 200 and res.json().get("authenticated"):
        COOKIES = session.cookies.get_dict()
        return "✅ Login realizado com sucesso!"
    else:
        return f"❌ Falha no login: {res.text}"

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
    print("🔐 Acesse: http://localhost:5000/login para logar")
    print("🔍 Depois use: http://localhost:5000/dados?usuario=usuario")
    app.run(host="0.0.0.0", port=5000, debug=True)
