# Inventory Management System

Simple Flask REST API to manage inventory items.  
Supports full CRUD and automatically fetches product info from Open Food Facts using barcode.

## Features

- Create, Read, Update, Delete inventory items
- Auto-fetch product name & brand from Open Food Facts by barcode
- Simple CLI
- Unit tests

## Project Files

- `app.py` → Main Flask application
- `cli.py` → Command line interface
- `test_app.py` → Tests
- `requirements.txt` → Dependencies

## Installation

```bash
pip install -r requirements.txt