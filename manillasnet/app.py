"""
🛍️ TIENDA DE ACCESORIOS - Sistema Completo
👤 Usuario: admin | 🔑 Contraseña: Admin@2026
▶️  Ejecutar: python app.py
🌐 Abrir: http://localhost:5000
"""

import sys, subprocess

def install_packages():
    required = {
        'flask': 'Flask', 'flask_cors': 'Flask-Cors',
        'flask_sqlalchemy': 'Flask-SQLAlchemy',
        'flask_jwt_extended': 'Flask-JWT-Extended',
        'werkzeug': 'Werkzeug'
    }
    for module, pkg in required.items():
        try:
            __import__(module)
        except ImportError:
            print(f"📦 Instalando {pkg}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '--quiet'])

install_packages()

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tienda.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'clave_secreta_tienda_2026'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
CORS(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)

# ============== MODELOS ==============
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='employee')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    min_stock = db.Column(db.Integer, default=5)
    image = db.Column(db.String(500))
    sku = db.Column(db.String(50), unique=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='efectivo')
    customer_name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('SaleItem', backref='sale', lazy=True, cascade='all, delete-orphan')
    user = db.relationship('User', backref='sales')

class SaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    product = db.relationship('Product')

# ============== DECORADOR ADMIN ==============
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        if get_jwt().get('role') != 'admin':
            return jsonify({'error': 'Solo administradores'}), 403
        return fn(*args, **kwargs)
    return wrapper

# ============== INIT DB ==============
def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password=generate_password_hash('Admin@2026'), name='Administrador', role='admin'))
            print('✅ Admin creado')
        if Product.query.count() == 0:
            productos = [
                ('Reloj Elegante Oro', 'Reloj dorado de lujo', 'Relojes', 299.99, 15, 'RLJ001', 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500'),
                ('Collar Plata 925', 'Collar de plata elegante', 'Joyería', 89.99, 20, 'JOY001', 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500'),
                ('Bolso Cuero Premium', 'Bolso negro de cuero genuino', 'Bolsos', 149.99, 10, 'BOL001', 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=500'),
                ('Gafas Sol Aviador', 'Gafas polarizadas UV400', 'Gafas', 79.99, 25, 'GAF001', 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=500'),
                ('Billetera Cuero', 'Billetera con RFID', 'Billeteras', 49.99, 30, 'BIL001', 'https://images.unsplash.com/photo-1627123424574-724758594e93?w=500'),
                ('Anillo Diamante', 'Anillo con diamante', 'Joyería', 499.99, 5, 'JOY002', 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500'),
                ('Reloj Deportivo', 'Reloj resistente al agua', 'Relojes', 189.99, 12, 'RLJ002', 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=500'),
                ('Pulsera Oro Rosa', 'Pulsera oro rosa 18k', 'Joyería', 129.99, 18, 'JOY003', 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=500'),
                ('Bolso Bandolera', 'Bolso elegante', 'Bolsos', 119.99, 8, 'BOL002', 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=500'),
                ('Gafas Cat Eye', 'Gafas retro', 'Gafas', 69.99, 15, 'GAF002', 'https://images.unsplash.com/photo-1577803645773-f96470509666?w=500'),
            ]
            for p in productos:
                db.session.add(Product(name=p[0], description=p[1], category=p[2], price=p[3], stock=p[4], sku=p[5], image=p[6]))
            print('✅ Productos creados')
        db.session.commit()

# ============== API AUTH ==============
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username'), active=True).first()
    if user and check_password_hash(user.password, data.get('password')):
        token = create_access_token(identity=str(user.id), additional_claims={'role': user.role})
        return jsonify({'token': token, 'user': {'id': user.id, 'username': user.username, 'name': user.name, 'role': user.role}})
    return jsonify({'error': 'Credenciales inválidas'}), 401

# ============== API PRODUCTOS ==============
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.filter_by(active=True).all()
    return jsonify([{'id': p.id, 'name': p.name, 'description': p.description, 'category': p.category,
                     'price': p.price, 'stock': p.stock, 'min_stock': p.min_stock, 'image': p.image, 'sku': p.sku} for p in products])

@app.route('/api/products', methods=['POST'])
@jwt_required()
def create_product():
    d = request.json
    p = Product(name=d['name'], description=d.get('description', ''), category=d['category'],
                price=float(d['price']), stock=int(d.get('stock', 0)), min_stock=int(d.get('min_stock', 5)),
                image=d.get('image', ''), sku=d.get('sku', f'SKU{int(datetime.now().timestamp())}'))
    db.session.add(p)
    db.session.commit()
    return jsonify({'id': p.id, 'message': 'Producto creado'}), 201

@app.route('/api/products/<int:id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    p = Product.query.get_or_404(id)
    d = request.json
    for k in ['name', 'description', 'category', 'image', 'sku']:
        if k in d:
            setattr(p, k, d[k])
    if 'price' in d: p.price = float(d['price'])
    if 'stock' in d: p.stock = int(d['stock'])
    if 'min_stock' in d: p.min_stock = int(d['min_stock'])
    db.session.commit()
    return jsonify({'message': 'Actualizado'})

@app.route('/api/products/<int:id>', methods=['DELETE'])
@admin_required
def delete_product(id):
    p = Product.query.get_or_404(id)
    p.active = False
    db.session.commit()
    return jsonify({'message': 'Eliminado'})

# ============== API VENTAS ==============
@app.route('/api/sales', methods=['POST'])
@jwt_required()
def create_sale():
    d = request.json
    user_id = int(get_jwt_identity())
    total = 0
    for item in d['items']:
        p = Product.query.get(item['product_id'])
        if not p or p.stock < item['quantity']:
            return jsonify({'error': f'Stock insuficiente: {p.name if p else "N/A"}'}), 400
        total += p.price * item['quantity']
    sale = Sale(user_id=user_id, total=total, payment_method=d.get('payment_method', 'efectivo'), customer_name=d.get('customer_name', ''))
    db.session.add(sale)
    db.session.flush()
    for item in d['items']:
        p = Product.query.get(item['product_id'])
        db.session.add(SaleItem(sale_id=sale.id, product_id=p.id, quantity=item['quantity'], price=p.price))
        p.stock -= item['quantity']
    db.session.commit()
    return jsonify({'id': sale.id, 'total': total, 'message': 'Venta registrada'}), 201

@app.route('/api/sales', methods=['GET'])
@jwt_required()
def get_sales():
    sales = Sale.query.order_by(Sale.created_at.desc()).limit(100).all()
    return jsonify([{'id':s.id,'total':s.total,'payment_method':s.payment_method,'customer_name':s.customer_name,
                     'created_at':s.created_at.isoformat(),'user':s.user.name,
                     'items':[{'product':i.product.name,'quantity':i.quantity,'price':i.price} for i in s.items]} for s in sales])

@app.route('/api/users', methods=['GET'])
@admin_required
def get_users():
    users = User.query.all()
    return jsonify([{'id':u.id,'username':u.username,'name':u.name,'role':u.role,'active':u.active} for u in users])

@app.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    d = request.json
    if User.query.filter_by(username=d['username']).first():
        return jsonify({'error':'Usuario ya existe'}), 400
    u = User(username=d['username'], password=generate_password_hash(d['password']), name=d['name'], role=d.get('role','employee'))
    db.session.add(u); db.session.commit()
    return jsonify({'id':u.id,'message':'Usuario creado'}), 201

@app.route('/api/users/<int:id>', methods=['DELETE'])
@admin_required
def delete_user(id):
    u = User.query.get_or_404(id)
    if u.role == 'admin': return jsonify({'error':'No se puede eliminar admin'}), 400
    u.active = False; db.session.commit()
    return jsonify({'message':'Eliminado'})

@app.route('/api/reports/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    today = datetime.utcnow().date()
    total_products = Product.query.filter_by(active=True).count()
    low_stock = Product.query.filter(Product.stock <= Product.min_stock, Product.active==True).count()
    total_sales = Sale.query.count()
    today_sales = Sale.query.filter(func.date(Sale.created_at)==today).count()
    total_revenue = db.session.query(func.sum(Sale.total)).scalar() or 0
    today_revenue = db.session.query(func.sum(Sale.total)).filter(func.date(Sale.created_at)==today).scalar() or 0
    top = db.session.query(Product.name, func.sum(SaleItem.quantity).label('qty')).join(SaleItem).group_by(Product.id).order_by(func.sum(SaleItem.quantity).desc()).limit(5).all()
    return jsonify({
        'total_products': total_products, 'low_stock': low_stock,
        'total_sales': total_sales, 'today_sales': today_sales,
        'total_revenue': float(total_revenue), 'today_revenue': float(today_revenue),
        'top_products': [{'name':t[0],'quantity':int(t[1])} for t in top]
    })

# ============== INTERFAZ HTML ==============
HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tienda de Accesorios</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',sans-serif}
body{background:#f5f5f7;color:#1d1d1f}
.navbar{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:1rem 2rem;display:flex;justify-content:space-between;align-items:center;box-shadow:0 2px 10px rgba(0,0,0,.1);position:sticky;top:0;z-index:100}
.logo{font-size:1.5rem;font-weight:bold}
.nav-links{display:flex;gap:1rem;align-items:center}
.nav-links button{background:rgba(255,255,255,.2);color:#fff;border:none;padding:.5rem 1rem;border-radius:8px;cursor:pointer;font-weight:500;transition:.3s}
.nav-links button:hover{background:rgba(255,255,255,.3)}
.container{max-width:1400px;margin:2rem auto;padding:0 2rem}
.hero{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:4rem 2rem;border-radius:20px;text-align:center;margin-bottom:2rem}
.hero h1{font-size:3rem;margin-bottom:1rem}
.hero p{font-size:1.2rem;opacity:.9}
.filters{background:#fff;padding:1.5rem;border-radius:15px;margin-bottom:2rem;box-shadow:0 2px 10px rgba(0,0,0,.05);display:flex;gap:1rem;flex-wrap:wrap}
.filters input,.filters select{padding:.7rem 1rem;border:2px solid #e5e5e7;border-radius:10px;font-size:1rem;flex:1;min-width:200px}
.filters input:focus,.filters select:focus{outline:none;border-color:#667eea}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1.5rem}
.card{background:#fff;border-radius:15px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.05);transition:.3s;cursor:pointer}
.card:hover{transform:translateY(-5px);box-shadow:0 10px 25px rgba(0,0,0,.1)}
.card img{width:100%;height:220px;object-fit:cover}
.card-body{padding:1.2rem}
.card-body h3{font-size:1.1rem;margin-bottom:.5rem}
.card-category{color:#667eea;font-size:.85rem;font-weight:600;text-transform:uppercase}
.card-price{font-size:1.4rem;font-weight:bold;color:#1d1d1f;margin:.5rem 0}
.card-stock{font-size:.85rem;color:#666}
.btn{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;padding:.7rem 1.2rem;border-radius:10px;cursor:pointer;font-weight:600;width:100%;margin-top:.5rem;transition:.3s}
.btn:hover{opacity:.9;transform:scale(1.02)}
.btn-sm{padding:.4rem .8rem;font-size:.85rem;width:auto}
.btn-danger{background:linear-gradient(135deg,#ee5a6f,#f29263)}
.btn-secondary{background:#e5e5e7;color:#1d1d1f}
.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:1000;align-items:center;justify-content:center;padding:1rem}
.modal.active{display:flex}
.modal-content{background:#fff;border-radius:20px;padding:2rem;max-width:500px;width:100%;max-height:90vh;overflow-y:auto}
.modal-content h2{margin-bottom:1.5rem;color:#1d1d1f}
.modal-content input,.modal-content select,.modal-content textarea{width:100%;padding:.8rem;border:2px solid #e5e5e7;border-radius:10px;margin-bottom:1rem;font-size:1rem}
.modal-content textarea{min-height:80px;resize:vertical;font-family:inherit}
.cart-item{display:flex;justify-content:space-between;align-items:center;padding:1rem;background:#f5f5f7;border-radius:10px;margin-bottom:.5rem}
.cart-total{font-size:1.5rem;font-weight:bold;margin:1rem 0;text-align:right}
.dashboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1.5rem;margin-bottom:2rem}
.stat{background:#fff;padding:1.5rem;border-radius:15px;box-shadow:0 2px 10px rgba(0,0,0,.05)}
.stat h3{color:#666;font-size:.9rem;text-transform:uppercase;margin-bottom:.5rem}
.stat .value{font-size:2rem;font-weight:bold;color:#667eea}
.table{width:100%;background:#fff;border-radius:15px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.05)}
.table th,.table td{padding:1rem;text-align:left;border-bottom:1px solid #e5e5e7}
.table th{background:#f5f5f7;font-weight:600}
.table tr:hover{background:#fafafa}
.tab-btns{display:flex;gap:.5rem;margin-bottom:1.5rem;flex-wrap:wrap}
.tab-btn{background:#fff;border:2px solid #e5e5e7;padding:.7rem 1.2rem;border-radius:10px;cursor:pointer;font-weight:500}
.tab-btn.active{background:#667eea;color:#fff;border-color:#667eea}
.hidden{display:none}
.badge{padding:.2rem .6rem;border-radius:20px;font-size:.75rem;font-weight:600}
.badge-admin{background:#ffd700;color:#1d1d1f}
.badge-employee{background:#667eea;color:#fff}
.badge-low{background:#ee5a6f;color:#fff}
.alert{padding:1rem;border-radius:10px;margin-bottom:1rem}
.alert-error{background:#fee;color:#c33;border:1px solid #fcc}
.alert-success{background:#efe;color:#3c3;border:1px solid #cfc}
#cartBadge{background:#ee5a6f;color:#fff;border-radius:50%;padding:.1rem .5rem;font-size:.75rem;margin-left:.3rem}
@media(max-width:768px){.hero h1{font-size:2rem}.nav-links{gap:.5rem}.nav-links button{padding:.4rem .7rem;font-size:.85rem}}
</style>
</head>
<body>
<nav class="navbar">
  <div class="logo">💎 MANILLASNET</div>
  <div class="nav-links">
    <button onclick="showView('shop')">🛍️ Tienda</button>
    <button onclick="showCart()">🛒 Carrito<span id="cartBadge">0</span></button>
    <button id="adminBtn" class="hidden" onclick="showView('admin')">⚙️ Panel</button>
    <button id="loginBtn" onclick="showLogin()">🔑 Ingresar</button>
    <button id="logoutBtn" class="hidden" onclick="logout()">🚪 Salir</button>
    <span id="userLabel"></span>
  </div>
</nav>

<div class="container">
  <div id="shopView">
    <div class="hero">
      <h1>Accesorios que te Definen</h1>
      <p>Joyería, relojes, bolsos y más — calidad premium</p>
    </div>
    <div class="filters">
      <input type="text" id="searchInput" placeholder="🔍 Buscar..." oninput="renderProducts()">
      <select id="categoryFilter" onchange="renderProducts()">
        <option value="">Todas las categorías</option>
      </select>
    </div>
    <div class="grid" id="productsGrid"></div>
  </div>

  <div id="adminView" class="hidden">
    <h1 style="margin-bottom:1.5rem">⚙️ Panel de Administración</h1>
    <div class="tab-btns">
      <button class="tab-btn active" onclick="showTab('dashboard')">📊 Dashboard</button>
      <button class="tab-btn" onclick="showTab('products')">📦 Productos</button>
      <button class="tab-btn" onclick="showTab('sales')">💰 Ventas</button>
      <button class="tab-btn" onclick="showTab('users')" id="usersTab">👥 Usuarios</button>
    </div>
    <div id="dashboardTab">
      <div class="dashboard" id="statsGrid"></div>
      <h3 style="margin-bottom:1rem">🏆 Productos Más Vendidos</h3>
      <table class="table"><thead><tr><th>Producto</th><th>Cantidad Vendida</th></tr></thead><tbody id="topProductsBody"></tbody></table>
    </div>
    <div id="productsTab" class="hidden">
      <button class="btn btn-sm" style="margin-bottom:1rem" onclick="openProductModal()">➕ Nuevo Producto</button>
      <table class="table"><thead><tr><th>Imagen</th><th>Nombre</th><th>Categoría</th><th>Precio</th><th>Stock</th><th>Acciones</th></tr></thead><tbody id="productsTableBody"></tbody></table>
    </div>
    <div id="salesTab" class="hidden">
      <table class="table"><thead><tr><th>ID</th><th>Fecha</th><th>Cliente</th><th>Vendedor</th><th>Método</th><th>Total</th></tr></thead><tbody id="salesTableBody"></tbody></table>
    </div>
    <div id="usersTab_content" class="hidden">
      <button class="btn btn-sm" style="margin-bottom:1rem" onclick="openUserModal()">➕ Nuevo Usuario</button>
      <table class="table"><thead><tr><th>Usuario</th><th>Nombre</th><th>Rol</th><th>Estado</th><th>Acciones</th></tr></thead><tbody id="usersTableBody"></tbody></table>
    </div>
  </div>
</div>

<div class="modal" id="loginModal">
  <div class="modal-content">
    <h2>🔑 Iniciar Sesión</h2>
    <div id="loginError"></div>
    <input type="text" id="loginUser" placeholder="Usuario">
    <input type="password" id="loginPass" placeholder="Contraseña">
    <button class="btn" onclick="doLogin()">Ingresar</button>
    <button class="btn btn-secondary" style="margin-top:.5rem" onclick="closeModal('loginModal')">Cancelar</button>
    <p style="margin-top:1rem;color:#666;font-size:.85rem;text-align:center">💡 admin / Admin@2026</p>
  </div>
</div>

<div class="modal" id="cartModal">
  <div class="modal-content">
    <h2>🛒 Carrito</h2>
    <div id="cartItems"></div>
    <div class="cart-total" id="cartTotal">Total: $0.00</div>
    <input type="text" id="customerName" placeholder="Nombre del cliente (opcional)">
    <select id="paymentMethod">
      <option value="efectivo">💵 Efectivo</option>
      <option value="tarjeta">💳 Tarjeta</option>
      <option value="transferencia">🏦 Transferencia</option>
    </select>
    <button class="btn" onclick="checkout()">✅ Finalizar Venta</button>
    <button class="btn btn-secondary" style="margin-top:.5rem" onclick="closeModal('cartModal')">Cerrar</button>
  </div>
</div>

<div class="modal" id="productModal">
  <div class="modal-content">
    <h2 id="productModalTitle">Producto</h2>
    <input type="hidden" id="productId">
    <input type="text" id="productName" placeholder="Nombre">
    <textarea id="productDesc" placeholder="Descripción"></textarea>
    <select id="productCategory">
      <option value="Joyería">Joyería</option>
      <option value="Relojes">Relojes</option>
      <option value="Bolsos">Bolsos</option>
      <option value="Gafas">Gafas</option>
      <option value="Billeteras">Billeteras</option>
      <option value="Otros">Otros</option>
    </select>
    <input type="number" id="productPrice" placeholder="Precio" step="0.01">
    <input type="number" id="productStock" placeholder="Stock">
    <input type="number" id="productMinStock" placeholder="Stock mínimo">
    <input type="text" id="productImage" placeholder="URL de imagen">
    <input type="text" id="productSku" placeholder="SKU">
    <button class="btn" onclick="saveProduct()">Guardar</button>
    <button class="btn btn-secondary" style="margin-top:.5rem" onclick="closeModal('productModal')">Cancelar</button>
  </div>
</div>

<div class="modal" id="userModal">
  <div class="modal-content">
    <h2>👤 Nuevo Usuario</h2>
    <input type="text" id="userUsername" placeholder="Usuario">
    <input type="text" id="userName" placeholder="Nombre completo">
    <input type="password" id="userPassword" placeholder="Contraseña">
    <select id="userRole">
      <option value="employee">Empleado</option>
      <option value="admin">Administrador</option>
    </select>
    <button class="btn" onclick="saveUser()">Guardar</button>
    <button class="btn btn-secondary" style="margin-top:.5rem" onclick="closeModal('userModal')">Cancelar</button>
  </div>
</div>

<script>
const API='/api';
let token=localStorage.getItem('token')||'';
let currentUser=JSON.parse(localStorage.getItem('user')||'null');
let products=[];
let cart=JSON.parse(localStorage.getItem('cart')||'[]');

async function api(path, options={}){
  const opts={...options, headers:{'Content-Type':'application/json', ...(options.headers||{})}};
  if(token) opts.headers['Authorization']='Bearer '+token;
  const r=await fetch(API+path, opts);
  const data=await r.json();
  if(!r.ok) throw new Error(data.error||'Error');
  return data;
}

function updateUI(){
  if(currentUser){
    document.getElementById('loginBtn').classList.add('hidden');
    document.getElementById('logoutBtn').classList.remove('hidden');
    document.getElementById('userLabel').textContent='👤 '+currentUser.name;
    document.getElementById('adminBtn').classList.remove('hidden');
  } else {
    document.getElementById('loginBtn').classList.remove('hidden');
    document.getElementById('logoutBtn').classList.add('hidden');
    document.getElementById('userLabel').textContent='';
    document.getElementById('adminBtn').classList.add('hidden');
  }
  document.getElementById('cartBadge').textContent=cart.reduce((s,i)=>s+i.quantity,0);
}

function showView(v){
  document.getElementById('shopView').classList.toggle('hidden', v!=='shop');
  document.getElementById('adminView').classList.toggle('hidden', v!=='admin');
  if(v==='admin') loadDashboard();
}

function showLogin(){ document.getElementById('loginModal').classList.add('active'); }
function closeModal(id){ document.getElementById(id).classList.remove('active'); }

async function doLogin(){
  try{
    const data=await api('/auth/login',{method:'POST',body:JSON.stringify({
      username:document.getElementById('loginUser').value,
      password:document.getElementById('loginPass').value
    })});
    token=data.token; currentUser=data.user;
    localStorage.setItem('token',token); localStorage.setItem('user',JSON.stringify(currentUser));
    closeModal('loginModal'); updateUI();
  }catch(e){ document.getElementById('loginError').innerHTML='<div class="alert alert-error">'+e.message+'</div>'; }
}

function logout(){
  token=''; currentUser=null;
  localStorage.removeItem('token'); localStorage.removeItem('user');
  updateUI(); showView('shop');
}

async function loadProducts(){
  products=await api('/products');
  const cats=[...new Set(products.map(p=>p.category))];
  const sel=document.getElementById('categoryFilter');
  sel.innerHTML='<option value="">Todas las categorías</option>'+cats.map(c=>`<option value="${c}">${c}</option>`).join('');
  renderProducts();
}

function renderProducts(){
  const search=document.getElementById('searchInput').value.toLowerCase();
  const cat=document.getElementById('categoryFilter').value;
  const filtered=products.filter(p=>(!cat||p.category===cat)&&(!search||p.name.toLowerCase().includes(search)));
  document.getElementById('productsGrid').innerHTML=filtered.map(p=>`
    <div class="card">
      <img src="${p.image}" onerror="this.src='https://via.placeholder.com/300x220?text=Sin+Imagen'">
      <div class="card-body">
        <div class="card-category">${p.category}</div>
        <h3>${p.name}</h3>
        <div class="card-price">$${p.price.toFixed(2)}</div>
        <div class="card-stock">${p.stock>0?'✅ Stock: '+p.stock:'❌ Sin stock'}</div>
        <button class="btn" onclick="addToCart(${p.id})" ${p.stock<=0?'disabled':''}>🛒 Agregar</button>
      </div>
    </div>`).join('');
}

function addToCart(id){
  const p=products.find(x=>x.id===id);
  const existing=cart.find(i=>i.product_id===id);
  if(existing){
    if(existing.quantity<p.stock) existing.quantity++;
    else return alert('Stock insuficiente');
  } else cart.push({product_id:id, name:p.name, price:p.price, quantity:1, stock:p.stock});
  localStorage.setItem('cart',JSON.stringify(cart));
  updateUI();
}

function showCart(){
  const items=document.getElementById('cartItems');
  if(cart.length===0){ items.innerHTML='<p style="text-align:center;padding:2rem;color:#666">Carrito vacío</p>'; }
  else{
    items.innerHTML=cart.map((i,idx)=>`
      <div class="cart-item">
        <div><strong>${i.name}</strong><br><small>$${i.price.toFixed(2)} × ${i.quantity}</small></div>
        <div>
          <button class="btn btn-sm" onclick="changeQty(${idx},-1)">-</button>
          <button class="btn btn-sm" onclick="changeQty(${idx},1)">+</button>
          <button class="btn btn-sm btn-danger" onclick="removeFromCart(${idx})">🗑️</button>
        </div>
      </div>`).join('');
  }
  const total=cart.reduce((s,i)=>s+i.price*i.quantity,0);
  document.getElementById('cartTotal').textContent='Total: $'+total.toFixed(2);
  document.getElementById('cartModal').classList.add('active');
}

function changeQty(idx, d){
  cart[idx].quantity+=d;
  if(cart[idx].quantity<=0) cart.splice(idx,1);
  else if(cart[idx].quantity>cart[idx].stock){ cart[idx].quantity=cart[idx].stock; alert('Stock máximo alcanzado'); }
  localStorage.setItem('cart',JSON.stringify(cart));
  showCart(); updateUI();
}
function removeFromCart(idx){ cart.splice(idx,1); localStorage.setItem('cart',JSON.stringify(cart)); showCart(); updateUI(); }

async function checkout(){
  if(!currentUser) return alert('Debes iniciar sesión para comprar');
  if(cart.length===0) return alert('Carrito vacío');
  try{
    await api('/sales',{method:'POST',body:JSON.stringify({
      items:cart.map(i=>({product_id:i.product_id, quantity:i.quantity})),
      payment_method:document.getElementById('paymentMethod').value,
      customer_name:document.getElementById('customerName').value
    })});
    alert('✅ Venta registrada exitosamente');
    cart=[]; localStorage.removeItem('cart');
    closeModal('cartModal'); updateUI(); loadProducts();
  }catch(e){ alert('Error: '+e.message); }
}

function showTab(t){
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  event.target.classList.add('active');
  ['dashboardTab','productsTab','salesTab','usersTab_content'].forEach(id=>document.getElementById(id).classList.add('hidden'));
  if(t==='dashboard'){ document.getElementById('dashboardTab').classList.remove('hidden'); loadDashboard(); }
  if(t==='products'){ document.getElementById('productsTab').classList.remove('hidden'); loadAdminProducts(); }
  if(t==='sales'){ document.getElementById('salesTab').classList.remove('hidden'); loadSales(); }
  if(t==='users'){ document.getElementById('usersTab_content').classList.remove('hidden'); loadUsers(); }
}

async function loadDashboard(){
  try{
    const d=await api('/reports/dashboard');
    document.getElementById('statsGrid').innerHTML=`
      <div class="stat"><h3>📦 Productos</h3><div class="value">${d.total_products}</div></div>
      <div class="stat"><h3>⚠️ Stock Bajo</h3><div class="value">${d.low_stock}</div></div>
      <div class="stat"><h3>💰 Ventas Hoy</h3><div class="value">${d.today_sales}</div></div>
      <div class="stat"><h3>💵 Ingresos Hoy</h3><div class="value">$${d.today_revenue.toFixed(2)}</div></div>
      <div class="stat"><h3>🛒 Ventas Totales</h3><div class="value">${d.total_sales}</div></div>
      <div class="stat"><h3>💎 Ingresos Totales</h3><div class="value">$${d.total_revenue.toFixed(2)}</div></div>`;
    document.getElementById('topProductsBody').innerHTML=d.top_products.map(p=>`<tr><td>${p.name}</td><td>${p.quantity}</td></tr>`).join('')||'<tr><td colspan="2">Sin datos</td></tr>';
  }catch(e){ console.error(e); }
}

async function loadAdminProducts(){
  const prods=await api('/products');
  document.getElementById('productsTableBody').innerHTML=prods.map(p=>`
    <tr>
      <td><img src="${p.image}" style="width:50px;height:50px;object-fit:cover;border-radius:8px" onerror="this.src='https://via.placeholder.com/50'"></td>
      <td>${p.name}</td><td>${p.category}</td><td>$${p.price.toFixed(2)}</td>
      <td>${p.stock} ${p.stock<=p.min_stock?'<span class="badge badge-low">BAJO</span>':''}</td>
      <td>
        <button class="btn btn-sm" onclick='editProduct(${JSON.stringify(p)})'>✏️</button>
        ${currentUser.role==='admin'?`<button class="btn btn-sm btn-danger" onclick="deleteProduct(${p.id})">🗑️</button>`:''}
      </td>
    </tr>`).join('');
}

function openProductModal(){
  document.getElementById('productModalTitle').textContent='Nuevo Producto';
  ['productId','productName','productDesc','productPrice','productStock','productMinStock','productImage','productSku'].forEach(id=>document.getElementById(id).value='');
  document.getElementById('productModal').classList.add('active');
}

function editProduct(p){
  document.getElementById('productModalTitle').textContent='Editar Producto';
  document.getElementById('productId').value=p.id;
  document.getElementById('productName').value=p.name;
  document.getElementById('productDesc').value=p.description||'';
  document.getElementById('productCategory').value=p.category;
  document.getElementById('productPrice').value=p.price;
  document.getElementById('productStock').value=p.stock;
  document.getElementById('productMinStock').value=p.min_stock;
  document.getElementById('productImage').value=p.image||'';
  document.getElementById('productSku').value=p.sku||'';
  document.getElementById('productModal').classList.add('active');
}

async function saveProduct(){
  const id=document.getElementById('productId').value;
  const body={
    name:document.getElementById('productName').value,
    description:document.getElementById('productDesc').value,
    category:document.getElementById('productCategory').value,
    price:document.getElementById('productPrice').value,
    stock:document.getElementById('productStock').value,
    min_stock:document.getElementById('productMinStock').value,
    image:document.getElementById('productImage').value,
    sku:document.getElementById('productSku').value
  };
  try{
    if(id) await api('/products/'+id,{method:'PUT',body:JSON.stringify(body)});
    else await api('/products',{method:'POST',body:JSON.stringify(body)});
    closeModal('productModal'); loadAdminProducts(); loadProducts();
  }catch(e){ alert('Error: '+e.message); }
}

async function deleteProduct(id){
  if(!confirm('¿Eliminar producto?')) return;
  try{ await api('/products/'+id,{method:'DELETE'}); loadAdminProducts(); loadProducts(); }
  catch(e){ alert('Error: '+e.message); }
}

async function loadSales(){
  const sales=await api('/sales');
  document.getElementById('salesTableBody').innerHTML=sales.map(s=>`
    <tr>
      <td>#${s.id}</td>
      <td>${new Date(s.created_at).toLocaleString()}</td>
      <td>${s.customer_name||'-'}</td>
      <td>${s.user}</td>
      <td>${s.payment_method}</td>
      <td><strong>$${s.total.toFixed(2)}</strong></td>
    </tr>`).join('')||'<tr><td colspan="6" style="text-align:center">Sin ventas</td></tr>';
}

async function loadUsers(){
  try{
    const users=await api('/users');
    document.getElementById('usersTableBody').innerHTML=users.map(u=>`
      <tr>
        <td>${u.username}</td><td>${u.name}</td>
        <td><span class="badge badge-${u.role}">${u.role}</span></td>
        <td>${u.active?'✅ Activo':'❌ Inactivo'}</td>
        <td>${u.role!=='admin'?`<button class="btn btn-sm btn-danger" onclick="deleteUser(${u.id})">🗑️</button>`:'-'}</td>
      </tr>`).join('');
  }catch(e){ alert('Solo administradores'); }
}

function openUserModal(){
  ['userUsername','userName','userPassword'].forEach(id=>document.getElementById(id).value='');
  document.getElementById('userModal').classList.add('active');
}

async function saveUser(){
  try{
    await api('/users',{method:'POST',body:JSON.stringify({
      username:document.getElementById('userUsername').value,
      name:document.getElementById('userName').value,
      password:document.getElementById('userPassword').value,
      role:document.getElementById('userRole').value
    })});
    closeModal('userModal'); loadUsers();
  }catch(e){ alert('Error: '+e.message); }
}

async function deleteUser(id){
  if(!confirm('¿Eliminar usuario?')) return;
  try{ await api('/users/'+id,{method:'DELETE'}); loadUsers(); }
  catch(e){ alert('Error: '+e.message); }
}

updateUI();
loadProducts();
</script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML)

# ============== EJECUTAR ==============
if __name__ == '__main__':
    init_db()
    import os
    port = int(os.environ.get('PORT', 5000))
    print('\n' + '='*50)
    print('🚀 TIENDA DE ACCESORIOS INICIADA')
    print('='*50)
    print(f'🌐 URL:      http://localhost:{port}')
    print('👤 Usuario:  admin')
    print('🔑 Password: Admin@2026')
    print('='*50 + '\n')
    app.run(host='0.0.0.0', port=port, debug=False)