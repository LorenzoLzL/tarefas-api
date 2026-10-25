def test_crud_completo_de_categoria(client, auth):
    r = client.post("/categorias", json={"nome": "Estudos", "descricao": "Faculdade"}, headers=auth)
    assert r.status_code == 201
    cid = r.json()["id"]

    assert client.get("/categorias", headers=auth).json()[0]["nome"] == "Estudos"
    assert client.get(f"/categorias/{cid}", headers=auth).status_code == 200

    r = client.patch(f"/categorias/{cid}", json={"descricao": "Uninter"}, headers=auth)
    assert r.status_code == 200
    assert r.json()["descricao"] == "Uninter"
    assert r.json()["nome"] == "Estudos"  # campo não enviado permanece igual

    assert client.delete(f"/categorias/{cid}", headers=auth).status_code == 204
    assert client.get(f"/categorias/{cid}", headers=auth).status_code == 404


def test_categoria_nome_duplicado_retorna_409(client, auth):
    client.post("/categorias", json={"nome": "Estudos"}, headers=auth)
    r = client.post("/categorias", json={"nome": "estudos"}, headers=auth)
    assert r.status_code == 409


def test_categoria_nome_vazio_retorna_400(client, auth):
    assert client.post("/categorias", json={"nome": "   "}, headers=auth).status_code == 400


def test_nao_exclui_categoria_com_tarefas(client, auth):
    cid = client.post("/categorias", json={"nome": "Casa"}, headers=auth).json()["id"]
    client.post("/tarefas", json={"titulo": "Lavar louça", "categoria_id": cid}, headers=auth)
    assert client.delete(f"/categorias/{cid}", headers=auth).status_code == 409


def test_categoria_de_outro_usuario_retorna_404(client, auth, auth_outro):
    cid = client.post("/categorias", json={"nome": "Privada"}, headers=auth).json()["id"]
    assert client.get(f"/categorias/{cid}", headers=auth_outro).status_code == 404
    assert client.delete(f"/categorias/{cid}", headers=auth_outro).status_code == 404
