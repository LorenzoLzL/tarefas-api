def test_registro_retorna_201_e_nao_expoe_senha(client):
    r = client.post("/auth/register", json={"nome": "Maria", "email": "m@x.com", "senha": "senhaSegura123"})
    assert r.status_code == 201
    corpo = r.json()
    assert corpo["email"] == "m@x.com"
    assert "senha" not in corpo and "senha_hash" not in corpo


def test_registro_email_duplicado_retorna_409(client):
    dados = {"nome": "Maria", "email": "m@x.com", "senha": "senhaSegura123"}
    client.post("/auth/register", json=dados)
    assert client.post("/auth/register", json=dados).status_code == 409


def test_registro_dados_invalidos_retorna_400(client):
    r = client.post("/auth/register", json={"nome": "M", "email": "nao-e-email", "senha": "123"})
    assert r.status_code == 400
    assert len(r.json()["erros"]) == 3


def test_login_correto_retorna_token(client):
    client.post("/auth/register", json={"nome": "Maria", "email": "m@x.com", "senha": "senhaSegura123"})
    r = client.post("/auth/login", json={"email": "m@x.com", "senha": "senhaSegura123"})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"
    assert r.json()["access_token"]


def test_login_senha_errada_retorna_401(client):
    client.post("/auth/register", json={"nome": "Maria", "email": "m@x.com", "senha": "senhaSegura123"})
    r = client.post("/auth/login", json={"email": "m@x.com", "senha": "errada"})
    assert r.status_code == 401


def test_rota_protegida_sem_token_retorna_401(client):
    assert client.get("/tarefas").status_code == 401
    assert client.get("/categorias").status_code == 401


def test_rota_protegida_com_token_invalido_retorna_401(client):
    r = client.get("/tarefas", headers={"Authorization": "Bearer token.invalido.aqui"})
    assert r.status_code == 401


def test_me_retorna_usuario_autenticado(client, auth):
    r = client.get("/auth/me", headers=auth)
    assert r.status_code == 200
    assert r.json()["email"] == "maria@exemplo.com"
