import click
import requests
import json

BASE = "http://127.0.0.1:5000"

@click.group()
def cli():
    """Simple Inventory CLI"""
    pass

@cli.command()
def list():
    r = requests.get(f"{BASE}/items")
    click.echo(json.dumps(r.json(), indent=2))

@cli.command()
@click.argument("id", type=int)
def get(id):
    r = requests.get(f"{BASE}/items/{id}")
    click.echo(json.dumps(r.json(), indent=2))

@cli.command()
@click.option("--name")
@click.option("--barcode")
@click.option("--quantity", default=0, type=int)
@click.option("--price", type=float)
def add(name, barcode, quantity, price):
    payload = {"quantity": quantity}
    if name: payload["name"] = name
    if barcode: payload["barcode"] = barcode
    if price is not None: payload["price"] = price

    r = requests.post(f"{BASE}/items", json=payload)
    click.echo(json.dumps(r.json(), indent=2))

@cli.command()
@click.argument("id", type=int)
@click.option("--name")
@click.option("--quantity", type=int)
@click.option("--price", type=float)
def update(id, name, quantity, price):
    payload = {}
    if name: payload["name"] = name
    if quantity is not None: payload["quantity"] = quantity
    if price is not None: payload["price"] = price

    r = requests.patch(f"{BASE}/items/{id}", json=payload)
    click.echo(json.dumps(r.json(), indent=2))

@cli.command()
@click.argument("id", type=int)
def delete(id):
    r = requests.delete(f"{BASE}/items/{id}")
    click.echo(r.json())

@cli.command()
@click.argument("barcode")
def lookup(barcode):
    r = requests.get(f"{BASE}/lookup/{barcode}")
    click.echo(json.dumps(r.json(), indent=2))

if __name__ == "__main__":
    cli()