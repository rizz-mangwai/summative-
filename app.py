from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inventory.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# -------------------- Model --------------------
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    barcode = db.Column(db.String(50), unique=True)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float)
    brand = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "barcode": self.barcode,
            "quantity": self.quantity,
            "price": self.price,
            "brand": self.brand,
            "created_at": self.created_at.isoformat()
        }

# -------------------- Open Food Facts --------------------
def fetch_from_openfoodfacts(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    headers = {"User-Agent": "InventoryApp/1.0"}
    try:
        r = requests.get(url, headers=headers, timeout=8)
        data = r.json()
        if data.get("status") != 1:
            return None
        p = data["product"]
        return {
            "name": p.get("product_name") or "Unknown",
            "barcode": p.get("code"),
            "brand": p.get("brands")
        }
    except:
        return None

# -------------------- CRUD Routes --------------------
@app.route("/items", methods=["GET"])
def list_items():
    items = Item.query.all()
    return jsonify([i.to_dict() for i in items])

@app.route("/items/<int:id>", methods=["GET"])
def get_item(id):
    item = Item.query.get_or_404(id)
    return jsonify(item.to_dict())

@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json() or {}
    name = data.get("name")
    barcode = data.get("barcode")

    # Auto-fetch from Open Food Facts if barcode given
    if barcode and not name:
        product = fetch_from_openfoodfacts(barcode)
        if product:
            name = product["name"]
            data["brand"] = product.get("brand")

    if not name:
        return jsonify({"error": "name or barcode required"}), 400

    item = Item(
        name=name,
        barcode=barcode,
        quantity=data.get("quantity", 0),
        price=data.get("price"),
        brand=data.get("brand")
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@app.route("/items/<int:id>", methods=["PUT", "PATCH"])
def update_item(id):
    item = Item.query.get_or_404(id)
    data = request.get_json() or {}

    item.name = data.get("name", item.name)
    item.barcode = data.get("barcode", item.barcode)
    item.quantity = data.get("quantity", item.quantity)
    item.price = data.get("price", item.price)
    item.brand = data.get("brand", item.brand)

    db.session.commit()
    return jsonify(item.to_dict())

@app.route("/items/<int:id>", methods=["DELETE"])
def delete_item(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "deleted"})

# Helper route
@app.route("/lookup/<barcode>")
def lookup(barcode):
    product = fetch_from_openfoodfacts(barcode)
    if not product:
        return jsonify({"error": "not found"}), 404
    return jsonify(product)

# -------------------- Start --------------------
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)