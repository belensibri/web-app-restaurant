import os, requests
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "frontend_secret_key"
API = os.getenv("API_BASE_URL", "http://localhost:8000")

def auth_headers():
    token = session.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = {
            "username": request.form.get("username"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "full_name": request.form.get("full_name")
        }
        resp = requests.post(f"{API}/auth/register", json=data)
        if resp.status_code == 201:
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash(f"Error: {resp.text}", "error")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = {
            "username": request.form.get("username"),
            "password": request.form.get("password")
        }
        resp = requests.post(f"{API}/auth/login", json=data)
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            session["token"] = token
            session["username"] = data["username"]
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get("token"): return redirect(url_for('login'))
    resp = requests.get(f"{API}/orders/mine", headers=auth_headers())
    orders = resp.json() if resp.status_code == 200 else []
    return render_template('dashboard.html', orders=orders)

@app.route('/menu')
def menu():
    if not session.get("token"): return redirect(url_for('login'))
    resp = requests.get(f"{API}/menu/all", headers=auth_headers())
    items = resp.json() if resp.status_code == 200 else []
    return render_template('menu.html', items=items)

@app.route('/menu/add', methods=['GET', 'POST'])
def add_menu_item():
    if not session.get("token"): return redirect(url_for('login'))
    if request.method == 'POST':
        data = {
            "name": request.form.get("name"),
            "description": request.form.get("description"),
            "price": float(request.form.get("price")),
            "category": request.form.get("category"),
            "is_available": "is_available" in request.form
        }
        resp = requests.post(f"{API}/menu/", json=data, headers=auth_headers())
        if resp.status_code == 201:
            flash("Item added successfully.", "success")
            return redirect(url_for('menu'))
        else:
            flash(f"Error: {resp.text}", "error")
    return render_template('add_menu_item.html')

@app.route('/menu/<int:item_id>/toggle', methods=['POST'])
def toggle_availability(item_id):
    if not session.get("token"): return redirect(url_for('login'))
    requests.post(f"{API}/menu/{item_id}/toggle", headers=auth_headers())
    return redirect(url_for('menu'))

@app.route('/orders')
def orders():
    if not session.get("token"): return redirect(url_for('login'))
    resp = requests.get(f"{API}/orders/", headers=auth_headers())
    all_orders = resp.json() if resp.status_code == 200 else []
    return render_template('orders.html', orders=all_orders)

@app.route('/orders/new', methods=['GET', 'POST'])
def new_order():
    if not session.get("token"): return redirect(url_for('login'))
    if request.method == 'POST':
        items = []
        for key, value in request.form.items():
            if key.startswith('qty_') and value and int(value) > 0:
                item_id = int(key.split('_')[1])
                items.append({
                    "menu_item_id": item_id,
                    "quantity": int(value),
                    "notes": request.form.get(f"notes_{item_id}", "")
                })
        
        data = {
            "table_number": int(request.form.get("table_number")),
            "notes": request.form.get("notes", ""),
            "items": items
        }
        
        resp = requests.post(f"{API}/orders/", json=data, headers=auth_headers())
        if resp.status_code == 201:
            flash("Order placed successfully.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Some items are unavailable or missing. Or invalid transition.", "error")

    resp = requests.get(f"{API}/menu/", headers=auth_headers())
    available_items = resp.json() if resp.status_code == 200 else []
    return render_template('new_order.html', items=available_items)

@app.route('/orders/<int:order_id>/status', methods=['POST'])
def update_order_status(order_id):
    if not session.get("token"): return redirect(url_for('login'))
    status = request.form.get("status")
    resp = requests.patch(f"{API}/orders/{order_id}/status", json={"status": status}, headers=auth_headers())
    if resp.status_code == 422:
        flash("Invalid status transition", "error")
    
    referrer = request.referrer
    if referrer and 'dashboard' in referrer:
        return redirect(url_for('dashboard'))
    return redirect(url_for('orders'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
