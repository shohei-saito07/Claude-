def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_shorten_creates_link(client):
    response = client.post("/shorten", json={"url": "https://example.com/page"})
    assert response.status_code == 201
    body = response.json()
    assert "code" in body
    assert body["target_url"] == "https://example.com/page"
    assert body["short_url"].endswith(body["code"])


def test_shorten_with_custom_code(client):
    response = client.post(
        "/shorten",
        json={"url": "https://example.com", "code": "my-link"},
    )
    assert response.status_code == 201
    assert response.json()["code"] == "my-link"


def test_shorten_rejects_invalid_url(client):
    response = client.post("/shorten", json={"url": "not-a-url"})
    assert response.status_code == 422


def test_shorten_duplicate_custom_code_returns_409(client):
    body = {"url": "https://example.com", "code": "dup"}
    assert client.post("/shorten", json=body).status_code == 201
    second = client.post("/shorten", json=body)
    assert second.status_code == 409


def test_redirect_to_target(client):
    code = client.post("/shorten", json={"url": "https://example.com/x"}).json()["code"]
    response = client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/x"


def test_redirect_increments_clicks(client):
    code = client.post("/shorten", json={"url": "https://example.com/x"}).json()["code"]
    for _ in range(3):
        client.get(f"/{code}", follow_redirects=False)
    info = client.get(f"/api/links/{code}").json()
    assert info["clicks"] == 3


def test_redirect_unknown_returns_404(client):
    response = client.get("/nope1234", follow_redirects=False)
    assert response.status_code == 404


def test_get_link_info(client):
    code = client.post("/shorten", json={"url": "https://example.com/x"}).json()["code"]
    response = client.get(f"/api/links/{code}")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == code
    assert body["target_url"] == "https://example.com/x"
    assert body["clicks"] == 0
    assert "created_at" in body


def test_list_links(client):
    client.post("/shorten", json={"url": "https://a.example.com"})
    client.post("/shorten", json={"url": "https://b.example.com"})
    response = client.get("/api/links")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
