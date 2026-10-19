import pytest
from app import app, db, Item

@pytest.fixture
def client():
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()      # ← important: clean first
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_create_and_list(client):
    r = client.post("/items", json={"name": "Test Item", "quantity": 5})
    assert r.status_code == 201

    r = client.get("/items")
    assert r.status_code == 200
    assert len(r.get_json()) == 1

def test_update_and_delete(client):
    r = client.post("/items", json={"name": "Old", "quantity": 1})
    item_id = r.get_json()["id"]

    r = client.patch(f"/items/{item_id}", json={"name": "New", "quantity": 10})
    assert r.status_code == 200
    assert r.get_json()["name"] == "New"

    r = client.delete(f"/items/{item_id}")
    assert r.status_code == 200

def test_lookup(client, mocker):
    mocker.patch("app.fetch_from_openfoodfacts", return_value={
        "name": "Nutella",
        "barcode": "3017624010701",
        "brand": "Ferrero"
    })
    r = client.get("/lookup/3017624010701")
    assert r.status_code == 200
    assert r.get_json()["name"] == "Nutella"