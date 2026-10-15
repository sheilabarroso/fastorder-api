import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "online"


def test_soma(client):
    resp = client.get("/api/soma?a=5&b=7")
    assert resp.status_code == 200
    assert resp.get_json()["resultado"] == 12


def test_soma_decimais(client):
    resp = client.get("/api/soma?a=1.5&b=2.5")
    assert resp.get_json()["resultado"] == 4


def test_soma_negativos(client):
    resp = client.get("/api/soma?a=-3&b=3")
    assert resp.get_json()["resultado"] == 0


def test_soma_parametro_ausente(client):
    resp = client.get("/api/soma?a=5")
    assert resp.status_code == 400


def test_soma_parametro_invalido(client):
    resp = client.get("/api/soma?a=abc&b=2")
    assert resp.status_code == 400


def test_subtracao(client):
    assert client.get("/api/subtracao?a=10&b=4").get_json()["resultado"] == 6


def test_multiplicacao(client):
    assert client.get("/api/multiplicacao?a=3&b=4").get_json()["resultado"] == 12


def test_divisao(client):
    assert client.get("/api/divisao?a=10&b=4").get_json()["resultado"] == 2.5


def test_divisao_por_zero(client):
    resp = client.get("/api/divisao?a=10&b=0")
    assert resp.status_code == 400
