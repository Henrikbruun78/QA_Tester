from __future__ import annotations

import json
from copy import deepcopy
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"

INITIAL_PRODUCTS = [
    {
        "id": 1,
        "name": "Nordic Lamp",
        "price": 699,
        "stock": 8,
        "category": "Bolig",
        "description": "Mat metal, varmt lys og et roligt formsprog til skrivebordet.",
        "image": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": 2,
        "name": "Canvas Tote",
        "price": 249,
        "stock": 14,
        "category": "Tilbehør",
        "description": "Robust taske til hverdag, laptop og hurtige indkøb.",
        "image": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": 3,
        "name": "Ceramic Cup Set",
        "price": 329,
        "stock": 5,
        "category": "Køkken",
        "description": "Sæt med fire kopper i stentøj med en let rå glasur.",
        "image": "https://images.unsplash.com/photo-1514228742587-6b1558fcf93a?auto=format&fit=crop&w=900&q=80",
    },
]

STATE = {
    "products": deepcopy(INITIAL_PRODUCTS),
    "next_product_id": 4,
    "next_order_id": 1001,
}


def json_bytes(payload: dict | list) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


class AppHandler(BaseHTTPRequestHandler):
    server_version = "QATesterDemo/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/products":
            self.send_json({"products": STATE["products"]})
            return

        if path == "/api/health":
            self.send_json({"status": "ok"})
            return

        self.serve_static(path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        body = self.read_json_body()

        if path == "/api/login":
            self.handle_login(body)
            return

        if path == "/api/checkout":
            self.handle_checkout(body)
            return

        if path == "/api/products":
            self.handle_create_product(body)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")

    def do_PUT(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        body = self.read_json_body()

        if path.startswith("/api/products/"):
            self.handle_update_product(path, body)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/products/"):
            self.handle_delete_product(path)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")

    def log_message(self, format: str, *args) -> None:
        return

    def read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid JSON")
            raise

    def send_json(self, payload: dict | list, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def serve_static(self, path: str) -> None:
        if path == "/":
            path = "/index.html"

        target = (WEB_ROOT / path.lstrip("/")).resolve()
        if not str(target).startswith(str(WEB_ROOT)) or not target.exists() or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return

        content_type = "text/plain; charset=utf-8"
        if target.suffix == ".html":
            content_type = "text/html; charset=utf-8"
        elif target.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        elif target.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"
        elif target.suffix == ".json":
            content_type = "application/json; charset=utf-8"

        data = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def handle_login(self, body: dict) -> None:
        email = str(body.get("email", "")).strip().lower()
        password = str(body.get("password", "")).strip()

        users = {
            "customer@example.com": {"password": "Test1234", "name": "Site Tester", "role": "customer"},
            "admin@example.com": {"password": "Admin1234", "name": "Site Admin", "role": "admin"},
        }
        user = users.get(email)

        if not user or user["password"] != password:
            self.send_json({"error": "Ugyldig e-mail eller adgangskode."}, status=HTTPStatus.UNAUTHORIZED)
            return

        self.send_json(
            {
                "token": f"demo-token-{user['role']}",
                "user": {"email": email, "name": user["name"], "role": user["role"]},
            }
        )

    def handle_checkout(self, body: dict) -> None:
        cart = body.get("cart", [])
        shipping = body.get("shipping", {})

        if not cart:
            self.send_json({"error": "Kurven er tom."}, status=HTTPStatus.BAD_REQUEST)
            return

        required_fields = ["fullName", "address", "city", "postalCode", "phone"]
        missing = [field for field in required_fields if not str(shipping.get(field, "")).strip()]
        if missing:
            self.send_json({"error": "Manglende obligatoriske felter.", "fields": missing}, status=HTTPStatus.BAD_REQUEST)
            return

        order_id = STATE["next_order_id"]
        STATE["next_order_id"] += 1
        total = sum(item["price"] * item["quantity"] for item in cart)

        self.send_json(
            {
                "orderId": order_id,
                "message": "Ordren er oprettet.",
                "total": total,
            },
            status=HTTPStatus.CREATED,
        )

    def handle_create_product(self, body: dict) -> None:
        name = str(body.get("name", "")).strip()
        description = str(body.get("description", "")).strip()
        category = str(body.get("category", "")).strip()
        image = str(body.get("image", "")).strip()
        stock = int(body.get("stock", 0))
        price = int(body.get("price", 0))

        if not name or not category or price <= 0:
            self.send_json({"error": "Ugyldige produktdata."}, status=HTTPStatus.BAD_REQUEST)
            return

        product = {
            "id": STATE["next_product_id"],
            "name": name,
            "price": price,
            "stock": stock,
            "category": category,
            "description": description,
            "image": image,
        }
        STATE["next_product_id"] += 1
        STATE["products"].append(product)
        self.send_json(product, status=HTTPStatus.CREATED)

    def handle_update_product(self, path: str, body: dict) -> None:
        try:
            product_id = int(path.rsplit("/", 1)[-1])
        except ValueError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid product id")
            return

        product = next((item for item in STATE["products"] if item["id"] == product_id), None)
        if not product:
            self.send_error(HTTPStatus.NOT_FOUND, "Product not found")
            return

        for key in ["name", "category", "description", "image"]:
            if key in body:
                product[key] = str(body[key]).strip()
        for key in ["price", "stock"]:
            if key in body:
                product[key] = int(body[key])

        self.send_json(product)

    def handle_delete_product(self, path: str) -> None:
        try:
            product_id = int(path.rsplit("/", 1)[-1])
        except ValueError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid product id")
            return

        before = len(STATE["products"])
        STATE["products"] = [item for item in STATE["products"] if item["id"] != product_id]
        if len(STATE["products"]) == before:
            self.send_error(HTTPStatus.NOT_FOUND, "Product not found")
            return

        self.send_json({"deleted": True})


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8000), AppHandler)
    print("QA Tester demo kører på http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
