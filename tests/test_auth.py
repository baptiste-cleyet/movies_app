def test_anon_index_redirects_to_login(anon_client):
    r = anon_client.get("/")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_anon_watchlist_redirects_to_login(anon_client):
    r = anon_client.get("/watchlist")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_anon_api_returns_401_json(anon_client):
    r = anon_client.post("/search_movie", json={"title": "fake"})
    assert r.status_code == 401
    assert "error" in r.get_json()


def test_login_page_renders(anon_client):
    r = anon_client.get("/login")
    assert r.status_code == 200
    assert b"password" in r.data


def test_login_wrong_password(anon_client):
    r = anon_client.post("/login", data={"password": "nope"})
    assert r.status_code == 401
    # Toujours anonyme après un échec
    r2 = anon_client.get("/")
    assert r2.status_code == 302


def test_login_success_and_logout(anon_client):
    r = anon_client.post("/login", data={"password": "test-password"})
    assert r.status_code in (302, 303)
    assert anon_client.get("/").status_code == 200
    r_out = anon_client.get("/logout")
    assert r_out.status_code in (302, 303)
    assert anon_client.get("/").status_code == 302


def test_login_next_param(anon_client):
    r = anon_client.post("/login?next=/watchlist", data={"password": "test-password"})
    assert r.status_code in (302, 303)
    assert r.headers["Location"].endswith("/watchlist")


def test_login_open_redirect_rejected(anon_client):
    r = anon_client.post(
        "/login", data={"password": "test-password", "next": "https://evil.example/"}
    )
    assert r.status_code in (302, 303)
    assert r.headers["Location"].endswith("/")


def test_login_rate_limited(anon_client, app):
    for _ in range(11):
        anon_client.post("/login", data={"password": "nope"})
    r = anon_client.post("/login", data={"password": "nope"})
    assert r.status_code == 429


def test_logout_menu_item_has_icon(client):
    html = client.get("/").get_data(as_text=True)
    assert 'id="logout-button"' in html
    assert 'data-lucide="log-out"' in html


def test_logout_icon_registered():
    import pathlib
    icons_js = pathlib.Path(__file__).resolve().parent.parent / "static" / "js" / "icons.js"
    src = icons_js.read_text()
    assert "log-out.js" in src and "LogOut" in src


def test_login_page_design_elements(anon_client):
    html = anon_client.get("/login").get_data(as_text=True)
    assert "login.css" in html
    assert 'id="toggle-password"' in html
    assert 'id="caps-hint"' in html
    assert 'data-lucide="log-in"' in html
    assert 'data-lucide="lock"' in html


def test_login_error_shakes_card(anon_client):
    html = anon_client.post("/login", data={"password": "nope"}).get_data(as_text=True)
    assert "login-shake" in html


def test_private_pages_not_cached(client):
    # Le HTML (token CSRF de session) et le JSON d'API ne doivent jamais
    # être mis en cache, sinon jetons périmés et fuites de contenu.
    r = client.get("/")
    assert r.headers["Cache-Control"] == "no-store, max-age=0"
    r = client.post("/search_movie", json={"title": ""})
    assert r.headers["Cache-Control"] == "no-store, max-age=0"
