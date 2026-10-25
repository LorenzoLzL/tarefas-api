TAREFA = {"titulo": "Estudar FastAPI", "prioridade": "alta", "prazo": "2026-12-01"}


def criar(client, auth, **extra):
    r = client.post("/tarefas", json={**TAREFA, **extra}, headers=auth)
    assert r.status_code == 201, r.text
    return r.json()


def test_criar_tarefa_aplica_valores_padrao(client, auth):
    r = client.post("/tarefas", json={"titulo": "Comprar pão"}, headers=auth)
    assert r.status_code == 201
    t = r.json()
    assert t["status"] == "pendente" and t["prioridade"] == "media"
    assert t["id"] and t["criado_em"]


def test_listar_tarefas(client, auth):
    criar(client, auth)
    criar(client, auth, titulo="Outra tarefa")
    r = client.get("/tarefas", headers=auth)
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_consultar_tarefa_por_id(client, auth):
    t = criar(client, auth)
    r = client.get(f"/tarefas/{t['id']}", headers=auth)
    assert r.status_code == 200
    assert r.json()["titulo"] == "Estudar FastAPI"


def test_consultar_tarefa_inexistente_retorna_404(client, auth):
    r = client.get("/tarefas/9999", headers=auth)
    assert r.status_code == 404
    assert "detail" in r.json()


def test_filtros_por_status_prioridade_e_busca(client, auth):
    criar(client, auth, titulo="Relatório da disciplina", prioridade="alta")
    criar(client, auth, titulo="Passear com o cachorro", prioridade="baixa", status="concluida")
    assert len(client.get("/tarefas?status=concluida", headers=auth).json()) == 1
    assert len(client.get("/tarefas?prioridade=alta", headers=auth).json()) == 1
    assert len(client.get("/tarefas?busca=relat", headers=auth).json()) == 1
    assert client.get("/tarefas?status=invalido", headers=auth).status_code == 400


def test_filtro_por_categoria_e_paginacao(client, auth):
    cid = client.post("/categorias", json={"nome": "Trabalho"}, headers=auth).json()["id"]
    for i in range(3):
        criar(client, auth, titulo=f"Tarefa {i}", categoria_id=cid)
    criar(client, auth, titulo="Sem categoria")
    assert len(client.get(f"/tarefas?categoria_id={cid}", headers=auth).json()) == 3
    assert len(client.get("/tarefas?limit=2", headers=auth).json()) == 2
    assert client.get("/tarefas?limit=1000", headers=auth).status_code == 400


def test_patch_altera_apenas_campos_enviados(client, auth):
    t = criar(client, auth)
    r = client.patch(f"/tarefas/{t['id']}", json={"status": "em_andamento"}, headers=auth)
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["status"] == "em_andamento"
    assert corpo["titulo"] == t["titulo"] and corpo["prioridade"] == "alta"


def test_patch_permite_remover_prazo_com_null(client, auth):
    t = criar(client, auth)
    r = client.patch(f"/tarefas/{t['id']}", json={"prazo": None}, headers=auth)
    assert r.status_code == 200
    assert r.json()["prazo"] is None


def test_patch_titulo_nulo_retorna_400(client, auth):
    t = criar(client, auth)
    assert client.patch(f"/tarefas/{t['id']}", json={"titulo": None}, headers=auth).status_code == 400


def test_patch_tarefa_inexistente_retorna_404(client, auth):
    assert client.patch("/tarefas/9999", json={"status": "concluida"}, headers=auth).status_code == 404


def test_excluir_tarefa(client, auth):
    t = criar(client, auth)
    r = client.delete(f"/tarefas/{t['id']}", headers=auth)
    assert r.status_code == 204 and r.content == b""
    assert client.get(f"/tarefas/{t['id']}", headers=auth).status_code == 404
    assert client.delete(f"/tarefas/{t['id']}", headers=auth).status_code == 404


def test_validacao_de_entrada_retorna_400_com_detalhes(client, auth):
    r = client.post(
        "/tarefas",
        json={"titulo": "ab", "status": "feito", "prazo": "amanhã", "prioridade": "urgente"},
        headers=auth,
    )
    assert r.status_code == 400
    campos = {e["campo"] for e in r.json()["erros"]}
    assert {"titulo", "status", "prazo", "prioridade"} <= campos


def test_categoria_inexistente_retorna_400(client, auth):
    r = client.post("/tarefas", json={"titulo": "Teste", "categoria_id": 999}, headers=auth)
    assert r.status_code == 400


def test_usuario_nao_acessa_tarefa_de_outro(client, auth, auth_outro):
    t = criar(client, auth)
    assert client.get(f"/tarefas/{t['id']}", headers=auth_outro).status_code == 404
    assert client.patch(f"/tarefas/{t['id']}", json={"status": "concluida"}, headers=auth_outro).status_code == 404
    assert client.delete(f"/tarefas/{t['id']}", headers=auth_outro).status_code == 404
    assert client.get("/tarefas", headers=auth_outro).json() == []


def test_cors_permite_origem_configurada_e_bloqueia_outras(client):
    permitida = client.options(
        "/tarefas",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
    )
    assert permitida.headers.get("access-control-allow-origin") == "http://localhost:3000"
    bloqueada = client.options(
        "/tarefas",
        headers={"Origin": "http://site-malicioso.com", "Access-Control-Request-Method": "GET"},
    )
    assert "access-control-allow-origin" not in bloqueada.headers
