from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("API_KEY")
URL = "https://api-publica.datajud.cnj.jus.br/api_publica_tjgo/_search"

@app.route("/consultar", methods=["POST"])
def consultar():
    dados_recebidos = request.get_json()
    numero_processo = dados_recebidos.get("numeroProcesso", "")

    if not numero_processo:
        return jsonify({"erro": "Número do processo não informado."}), 400

    headers = {
        "Authorization": f"APIKey {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "size": 1,
        "query": {
            "term": {
                "numeroProcesso": numero_processo
            }
        }
    }

    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        dados = response.json()
        hits = dados.get("hits", {}).get("hits", [])

        if not hits:
            return jsonify({"erro": "Processo não encontrado."}), 404

        processo = hits[0].get("_source", {})
        movimentos = processo.get("movimentos", [])

        if not movimentos:
            return jsonify({"erro": "Sem movimentações."}), 404

        ultimo = max(movimentos, key=lambda x: x.get("dataHora", ""))
        data_hora = ultimo.get("dataHora", "")
        tema = ultimo.get("nome", "Não informado")

        if "T" in data_hora:
            data, hora = data_hora.split("T")
        else:
            data = data_hora
            hora = ""

        return jsonify({
            "data": data,
            "hora": hora,
            "tema": tema
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"erro": f"Erro na consulta: {str(e)}"}), 500

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)