from flask import Flask, jsonify, request

app = Flask(__name__)


def _ler_numeros():
    """Lê os parâmetros 'a' e 'b' da query string e converte para float.

    Retorna (a, b, None) em caso de sucesso ou (None, None, erro) se falhar.
    """
    a_raw = request.args.get("a")
    b_raw = request.args.get("b")
    if a_raw is None or b_raw is None:
        return None, None, "Parâmetros 'a' e 'b' são obrigatórios"
    try:
        return float(a_raw), float(b_raw), None
    except ValueError:
        return None, None, "Parâmetros 'a' e 'b' devem ser numéricos"


def _numero(valor):
    """Devolve int quando o float for inteiro (5.0 -> 5), para uma resposta limpa."""
    return int(valor) if valor == int(valor) else valor


@app.route("/")
def home():
    return jsonify({"status": "online", "servico": "FastOrder API"})


@app.route("/api/soma")
def soma():
    a, b, erro = _ler_numeros()
    if erro:
        return jsonify({"erro": erro}), 400
    return jsonify({"operacao": "soma", "resultado": _numero(a + b)})


@app.route("/api/subtracao")
def subtracao():
    a, b, erro = _ler_numeros()
    if erro:
        return jsonify({"erro": erro}), 400
    return jsonify({"operacao": "subtracao", "resultado": _numero(a - b)})


@app.route("/api/multiplicacao")
def multiplicacao():
    a, b, erro = _ler_numeros()
    if erro:
        return jsonify({"erro": erro}), 400
    return jsonify({"operacao": "multiplicacao", "resultado": _numero(a * b)})


@app.route("/api/divisao")
def divisao():
    a, b, erro = _ler_numeros()
    if erro:
        return jsonify({"erro": erro}), 400
    if b == 0:
        return jsonify({"erro": "Divisão por zero não é permitida"}), 400
    return jsonify({"operacao": "divisao", "resultado": _numero(a / b)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
