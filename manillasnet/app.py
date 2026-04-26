"""
🌸 NORA Y RO ACCESORIOS - Tienda Premium
📍 Bucaramanga, Colombia | 📱 3013065949
👤 admin / Admin@2026
"""
import sys, subprocess

def install_packages():
    required = {'flask':'Flask','flask_cors':'Flask-Cors','flask_sqlalchemy':'Flask-SQLAlchemy',
                'flask_jwt_extended':'Flask-JWT-Extended','werkzeug':'Werkzeug'}
    for m, pkg in required.items():
        try: __import__(m)
        except ImportError:
            print(f"📦 Instalando {pkg}...")
            subprocess.check_call([sys.executable,'-m','pip','install',pkg,'--quiet'])
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
app.config['JWT_SECRET_KEY'] = 'noraro_secret_2026'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
CORS(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)

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
    payment_method = db.Column(db.String(50), default='transferencia')
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

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        if get_jwt().get('role') != 'admin':
            return jsonify({'error': 'Solo administradores'}), 403
        return fn(*args, **kwargs)
    return wrapper

def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password=generate_password_hash('Admin@2026'), name='Nora', role='admin'))
        if Product.query.count() == 0:
            productos = [
                ('Manilla Personalizada con Nombre','Manilla tejida a mano con nombre personalizado en letras doradas. Hilos de alta calidad, resistente al agua. Longitud ajustable.','Manillas',25000,30,'MAN001','https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=600'),
                ('Collar Inicial Dorado','Collar con dije de inicial en baño de oro 18k. Cadena fina de 45cm ajustable. Hipoalergénico.','Collares',45000,25,'COL001','https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600'),
                ('Anillo Personalizado Grabado','Anillo de acero quirúrgico con grabado personalizado. No se oxida. Tallas 5-9.','Anillos',35000,20,'ANI001','https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=600'),
                ('Manilla Pareja (Par)','Set de 2 manillas coordinadas para pareja. Hilos de colores y dijes de corazón. Empaque de regalo.','Manillas',40000,15,'MAN002','https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=600'),
                ('Collar Perlas Naturales','Collar con perlas naturales cultivadas. Cierre de plata 925. Longitud 42cm. Estuche de terciopelo.','Collares',65000,12,'COL002','https://images.unsplash.com/photo-1599643477877-530eb83abc8e?w=600'),
                ('Anillo Flores Minimalista','Anillo delicado con detalle floral. Materiales hipoalergénicos que no manchan la piel.','Anillos',28000,22,'ANI002','https://images.unsplash.com/photo-1602173574767-37ac01994b2a?w=600'),
                ('Manilla Piedras Naturales','Manilla de piedras naturales energéticas: cuarzo rosa, amatista, ojo de tigre. Elástica.','Manillas',22000,40,'MAN003','https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=600'),
                ('Collar Mamá e Hija','Set de 2 collares con dijes complementarios. El detalle perfecto. Tarjeta personalizada.','Collares',55000,10,'COL003','https://images.unsplash.com/photo-1611107683227-e9060eccd846?w=600'),
                ('Set Completo Personalizado','Kit: collar + manilla + anillo personalizados. Perfecto como regalo único.','Personalizados',95000,8,'PER001','https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=600'),
                ('Manilla Infinito','Manilla con símbolo infinito en baño de oro. Delicada. Cadena ajustable 16-19cm.','Manillas',32000,18,'MAN004','https://images.unsplash.com/photo-1588444837495-c6cfeb53f32d?w=600'),
                ('Collar Nombre Cursiva','Collar con tu nombre en letra cursiva elegante. Baño de oro 18k. Cadena de 45cm.','Collares',50000,25,'COL004','https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=600'),
                ('Anillo Ajustable Luna','Anillo ajustable con dije de luna y estrella. Acabado plateado.','Anillos',20000,35,'ANI003','https://images.unsplash.com/photo-1535556116002-6281ff3e9f36?w=600'),
            ]
            for p in productos:
                db.session.add(Product(name=p[0],description=p[1],category=p[2],price=p[3],stock=p[4],sku=p[5],image=p[6]))
        db.session.commit()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username'), active=True).first()
    if user and check_password_hash(user.password, data.get('password')):
        token = create_access_token(identity=str(user.id), additional_claims={'role': user.role})
        return jsonify({'token': token, 'user': {'id': user.id, 'username': user.username, 'name': user.name, 'role': user.role}})
    return jsonify({'error': 'Credenciales inválidas'}), 401

@app.route('/api/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    data = request.json
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user: return jsonify({'error': 'Usuario no encontrado'}), 404
    current = data.get('current_password', '')
    new = data.get('new_password', '')
    if not check_password_hash(user.password, current):
        return jsonify({'error': 'Contraseña actual incorrecta'}), 401
    if len(new) < 8: return jsonify({'error': 'Mínimo 8 caracteres'}), 400
    if current == new: return jsonify({'error': 'Debe ser diferente a la actual'}), 400
    user.password = generate_password_hash(new)
    db.session.commit()
    return jsonify({'message': 'Contraseña actualizada'})

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.filter_by(active=True).all()
    return jsonify([{'id':p.id,'name':p.name,'description':p.description,'category':p.category,
                     'price':p.price,'stock':p.stock,'min_stock':p.min_stock,'image':p.image,'sku':p.sku} for p in products])

@app.route('/api/products/<int:id>', methods=['GET'])
def get_product(id):
    p = Product.query.get_or_404(id)
    return jsonify({'id':p.id,'name':p.name,'description':p.description,'category':p.category,
                    'price':p.price,'stock':p.stock,'min_stock':p.min_stock,'image':p.image,'sku':p.sku})

@app.route('/api/products', methods=['POST'])
@jwt_required()
def create_product():
    d = request.json
    p = Product(name=d['name'], description=d.get('description',''), category=d['category'],
                price=float(d['price']), stock=int(d.get('stock',0)), min_stock=int(d.get('min_stock',5)),
                image=d.get('image',''), sku=d.get('sku', f'SKU{int(datetime.now().timestamp())}'))
    db.session.add(p); db.session.commit()
    return jsonify({'id': p.id, 'message': 'Producto creado'}), 201

@app.route('/api/products/<int:id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    p = Product.query.get_or_404(id); d = request.json
    for k in ['name','description','category','image','sku']:
        if k in d: setattr(p, k, d[k])
    if 'price' in d: p.price = float(d['price'])
    if 'stock' in d: p.stock = int(d['stock'])
    if 'min_stock' in d: p.min_stock = int(d['min_stock'])
    db.session.commit()
    return jsonify({'message': 'Actualizado'})

@app.route('/api/products/<int:id>', methods=['DELETE'])
@admin_required
def delete_product(id):
    p = Product.query.get_or_404(id); p.active = False; db.session.commit()
    return jsonify({'message': 'Eliminado'})

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
    sale = Sale(user_id=user_id, total=total, payment_method=d.get('payment_method','transferencia'), customer_name=d.get('customer_name',''))
    db.session.add(sale); db.session.flush()
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
# ============== INTERFAZ HTML PREMIUM ==============
HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>✨ Nora y Ro Accesorios - Collares, Manillas y Anillos</title>
<meta name="description" content="Accesorios personalizados en Bucaramanga. Collares, manillas y anillos. Envíos a toda Colombia.">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Playfair+Display:wght@400;700;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Poppins',sans-serif}
html{scroll-behavior:smooth}
:root{
  --pink-1:#ff4d94;--pink-2:#ff80b5;--pink-3:#ffb3d1;--pink-4:#ffe0ec;
  --dark:#1a0a15;--gray:#2a1a24;--light:#fff5f9;
  --gradient:linear-gradient(135deg,#ff4d94 0%,#c44bce 50%,#7a3fb8 100%);
  --gradient-2:linear-gradient(135deg,#ff80b5 0%,#ff4d94 100%);
  --glass:rgba(255,255,255,0.7);--shadow:0 20px 60px rgba(255,77,148,0.2);
}
body{background:linear-gradient(135deg,#ffe0ec 0%,#fff5f9 50%,#ffe0ec 100%);color:var(--dark);min-height:100vh;overflow-x:hidden}
body::before{content:'';position:fixed;top:-50%;left:-50%;width:200%;height:200%;background:
  radial-gradient(circle at 20% 30%,rgba(255,77,148,0.15) 0%,transparent 40%),
  radial-gradient(circle at 80% 70%,rgba(196,75,206,0.12) 0%,transparent 40%),
  radial-gradient(circle at 50% 50%,rgba(255,128,181,0.1) 0%,transparent 50%);
  animation:bgFloat 20s ease infinite;z-index:-1}
@keyframes bgFloat{0%,100%{transform:translate(0,0) rotate(0)}50%{transform:translate(-5%,5%) rotate(180deg)}}

#loader{position:fixed;inset:0;background:linear-gradient(135deg,#ff4d94,#c44bce,#7a3fb8);display:flex;align-items:center;justify-content:center;flex-direction:column;z-index:9999;transition:opacity .5s}
#loader.hidden{opacity:0;pointer-events:none}
.loader-logo{font-family:'Playfair Display',serif;font-size:3rem;color:#fff;font-weight:900;animation:pulse 1.5s infinite;text-shadow:0 4px 20px rgba(0,0,0,0.3)}
.loader-sub{color:#fff;margin-top:1rem;opacity:.9;letter-spacing:3px;font-size:.9rem}
@keyframes pulse{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.05);opacity:.9}}

.promo-banner{background:linear-gradient(90deg,#ff4d94,#c44bce,#7a3fb8,#c44bce,#ff4d94);background-size:200% 100%;animation:promoSlide 4s linear infinite;color:#fff;text-align:center;padding:.7rem 1rem;font-weight:600;font-size:.9rem;position:relative;z-index:101;text-shadow:0 1px 3px rgba(0,0,0,0.2)}
@keyframes promoSlide{0%{background-position:0% 50%}100%{background-position:200% 50%}}

.navbar{background:rgba(255,255,255,0.95);backdrop-filter:blur(20px);padding:1rem 2rem;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:100;border-bottom:1px solid rgba(255,77,148,0.2);box-shadow:0 4px 20px rgba(255,77,148,0.08)}
.logo{font-family:'Playfair Display',serif;font-size:1.6rem;font-weight:900;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1.1}
.logo small{font-size:.6rem;letter-spacing:3px;display:block;text-transform:uppercase;font-weight:500}
.nav-links{display:flex;gap:.8rem;align-items:center;flex-wrap:wrap}
.nav-links button{background:rgba(255,77,148,0.1);color:var(--pink-1);border:1px solid rgba(255,77,148,0.2);padding:.6rem 1.2rem;border-radius:50px;cursor:pointer;font-weight:600;font-size:.9rem;transition:all .3s}
.nav-links button:hover{background:var(--gradient);color:#fff;transform:translateY(-2px);box-shadow:0 8px 20px rgba(255,77,148,0.4)}
#userLabel{color:var(--pink-1);font-weight:600;font-size:.9rem}

.container{max-width:1400px;margin:2rem auto;padding:0 2rem}

.hero{background:var(--gradient);padding:5rem 2rem;border-radius:30px;text-align:center;margin-bottom:3rem;position:relative;overflow:hidden;box-shadow:var(--shadow)}
.hero::before{content:'';position:absolute;top:-50%;right:-20%;width:500px;height:500px;background:radial-gradient(circle,rgba(255,255,255,0.2) 0%,transparent 70%);animation:float 6s ease-in-out infinite;pointer-events:none}
.hero::after{content:'';position:absolute;bottom:-30%;left:-10%;width:400px;height:400px;background:radial-gradient(circle,rgba(255,255,255,0.15) 0%,transparent 70%);animation:float 8s ease-in-out infinite reverse;pointer-events:none}
@keyframes float{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-30px) scale(1.1)}}
.hero-content{position:relative;z-index:10}
.hero-title-wrap{display:inline-block;position:relative;z-index:10}
.hero-title-wrap h1{font-family:'Playfair Display',serif;font-size:4rem;margin:0;font-weight:900;color:#ffffff;-webkit-text-fill-color:#ffffff;background:transparent;background-image:none;text-shadow:0 3px 10px rgba(0,0,0,0.35),0 6px 20px rgba(0,0,0,0.25);letter-spacing:2px;line-height:1.1}
.hero p{font-size:1.3rem;color:#ffffff;margin-top:1.2rem;font-weight:400;text-shadow:0 2px 10px rgba(0,0,0,0.3);position:relative;z-index:10}
.hero-badge{display:inline-block;background:rgba(255,255,255,0.25);padding:.6rem 1.8rem;border-radius:50px;margin-bottom:1.5rem;font-size:.9rem;font-weight:600;backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.4);color:#fff;text-shadow:0 1px 3px rgba(0,0,0,0.2);position:relative;z-index:10}
.hero-cta{display:inline-flex;gap:1rem;margin-top:2rem;flex-wrap:wrap;justify-content:center;position:relative;z-index:10}
.hero-cta button{background:#fff;color:var(--pink-1);border:none;padding:1rem 2rem;border-radius:50px;cursor:pointer;font-weight:700;font-size:1rem;transition:.3s;box-shadow:0 10px 30px rgba(0,0,0,0.2)}
.hero-cta button:hover{transform:translateY(-3px);box-shadow:0 15px 40px rgba(0,0,0,0.3)}
.hero-cta .btn-outline-light{background:transparent;color:#fff;border:2px solid #fff}
.hero-cta .btn-outline-light:hover{background:#fff;color:var(--pink-1)}

.section-title{font-family:'Playfair Display',serif;font-size:2.5rem;text-align:center;margin:3rem 0 .5rem;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;font-weight:900}
.section-sub{text-align:center;color:#888;margin-bottom:2.5rem;font-size:1rem}

.features{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1.5rem;margin-bottom:3rem}
.feature-card{background:rgba(255,255,255,0.85);padding:2rem 1.5rem;border-radius:20px;text-align:center;border:1px solid rgba(255,255,255,0.5);box-shadow:0 10px 30px rgba(255,77,148,0.08);transition:.4s}
.feature-card:hover{transform:translateY(-8px);box-shadow:0 20px 40px rgba(255,77,148,0.2)}
.feature-icon{font-size:3rem;margin-bottom:1rem;display:block}
.feature-card h3{font-family:'Playfair Display',serif;color:var(--dark);margin-bottom:.5rem;font-size:1.2rem}
.feature-card p{color:#666;font-size:.9rem;line-height:1.5}

.categories{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1.5rem;margin-bottom:3rem}
.cat-card{position:relative;border-radius:20px;overflow:hidden;cursor:pointer;height:200px;box-shadow:0 10px 30px rgba(255,77,148,0.15);transition:.4s}
.cat-card:hover{transform:scale(1.03);box-shadow:0 20px 50px rgba(255,77,148,0.3)}
.cat-card img{width:100%;height:100%;object-fit:cover;transition:.6s}
.cat-card:hover img{transform:scale(1.15)}
.cat-overlay{position:absolute;inset:0;background:linear-gradient(to top,rgba(122,63,184,0.9) 0%,rgba(255,77,148,0.3) 70%,transparent 100%);display:flex;flex-direction:column;justify-content:flex-end;padding:1.5rem;color:#fff}
.cat-overlay h3{font-family:'Playfair Display',serif;font-size:1.5rem;margin-bottom:.3rem;text-shadow:0 2px 10px rgba(0,0,0,0.3)}
.cat-overlay p{font-size:.85rem;opacity:.95}

.filters{background:var(--glass);backdrop-filter:blur(20px);padding:1.5rem;border-radius:25px;margin-bottom:2rem;box-shadow:0 10px 40px rgba(255,77,148,0.1);display:flex;gap:1rem;flex-wrap:wrap;border:1px solid rgba(255,255,255,0.5)}
.filters input,.filters select{padding:.9rem 1.3rem;border:2px solid rgba(255,77,148,0.15);border-radius:15px;font-size:1rem;flex:1;min-width:200px;background:rgba(255,255,255,0.8);transition:.3s}
.filters input:focus,.filters select:focus{outline:none;border-color:var(--pink-1);box-shadow:0 0 0 4px rgba(255,77,148,0.1)}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:2rem}
.card{background:rgba(255,255,255,0.85);border-radius:25px;overflow:hidden;box-shadow:0 10px 40px rgba(255,77,148,0.1);transition:all .4s;cursor:pointer;border:1px solid rgba(255,255,255,0.5);animation:fadeInUp .6s backwards}
@keyframes fadeInUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
.card:hover{transform:translateY(-10px) scale(1.02);box-shadow:0 25px 60px rgba(255,77,148,0.3)}
.card-img-wrap{position:relative;overflow:hidden;height:260px;background:linear-gradient(135deg,var(--pink-4),var(--pink-3))}
.card img{width:100%;height:100%;object-fit:cover;transition:transform .6s}
.card:hover img{transform:scale(1.1)}
.card-badge{position:absolute;top:1rem;right:1rem;background:var(--gradient);color:#fff;padding:.3rem .8rem;border-radius:20px;font-size:.75rem;font-weight:600;box-shadow:0 4px 15px rgba(255,77,148,0.4)}
.card-body{padding:1.5rem}
.card-category{color:var(--pink-1);font-size:.8rem;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:.5rem}
.card-body h3{font-family:'Playfair Display',serif;font-size:1.3rem;margin-bottom:.8rem;color:var(--dark);font-weight:700}
.card-price{font-size:1.8rem;font-weight:800;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:.8rem 0}
.card-stock{font-size:.85rem;color:#888;margin-bottom:1rem}
.card-stock.available{color:#10b981}

.btn{background:var(--gradient);color:#fff;border:none;padding:.9rem 1.5rem;border-radius:50px;cursor:pointer;font-weight:600;width:100%;transition:.3s;font-size:1rem;box-shadow:0 8px 20px rgba(255,77,148,0.3)}
.btn:hover{transform:translateY(-2px);box-shadow:0 12px 30px rgba(255,77,148,0.5)}
.btn:disabled{opacity:.5;cursor:not-allowed;transform:none}
.btn-sm{padding:.5rem 1rem;font-size:.85rem;width:auto;border-radius:30px}
.btn-danger{background:linear-gradient(135deg,#ff4757,#ff6b81)}
.btn-secondary{background:rgba(255,77,148,0.1);color:var(--pink-1);border:2px solid rgba(255,77,148,0.2);box-shadow:none}
.btn-secondary:hover{background:rgba(255,77,148,0.2)}
.btn-outline{background:transparent;border:2px solid var(--pink-1);color:var(--pink-1);box-shadow:none}
.btn-outline:hover{background:var(--gradient);color:#fff;border-color:transparent}
.btn-wa{background:linear-gradient(135deg,#25d366,#128c7e)}

.testimonials{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem;margin-bottom:3rem}
.testimonial{background:rgba(255,255,255,0.9);padding:2rem;border-radius:20px;box-shadow:0 10px 30px rgba(255,77,148,0.1);position:relative}
.testimonial::before{content:'"';position:absolute;top:-.5rem;left:1rem;font-size:5rem;font-family:Georgia,serif;color:var(--pink-3);line-height:1;opacity:.6}
.testimonial-stars{color:#ffa500;font-size:1.1rem;margin-bottom:.8rem;position:relative;z-index:1}
.testimonial-text{color:#555;line-height:1.6;margin-bottom:1rem;font-style:italic;position:relative;z-index:1}
.testimonial-author{font-weight:700;color:var(--pink-1);font-size:.9rem}

.modal{display:none;position:fixed;inset:0;background:rgba(26,10,21,0.7);z-index:1000;align-items:center;justify-content:center;padding:1rem;backdrop-filter:blur(8px);animation:fadeIn .3s}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.modal.active{display:flex}
.modal-content{background:rgba(255,255,255,0.98);border-radius:30px;padding:2.5rem;max-width:500px;width:100%;max-height:90vh;overflow-y:auto;box-shadow:0 30px 80px rgba(255,77,148,0.3);animation:slideUp .4s}
@keyframes slideUp{from{transform:translateY(50px);opacity:0}to{transform:translateY(0);opacity:1}}
.modal-content h2{font-family:'Playfair Display',serif;margin-bottom:1.5rem;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;font-size:1.8rem;font-weight:900}
.modal-content input,.modal-content select,.modal-content textarea{width:100%;padding:.9rem 1.2rem;border:2px solid rgba(255,77,148,0.15);border-radius:15px;margin-bottom:1rem;font-size:1rem;background:rgba(255,255,255,0.8)}
.modal-content textarea{min-height:80px;resize:vertical}
.modal-detail{max-width:900px !important}
.detail-grid{display:grid;grid-template-columns:1fr 1fr;gap:2rem}
.detail-img{width:100%;height:400px;object-fit:cover;border-radius:20px}
.detail-info h1{font-family:'Playfair Display',serif;font-size:2rem;color:var(--dark);margin-bottom:.5rem;line-height:1.2}
.detail-category{display:inline-block;background:var(--gradient);color:#fff;padding:.3rem 1rem;border-radius:20px;font-size:.75rem;font-weight:600;margin-bottom:1rem}
.detail-price{font-size:2.8rem;font-weight:800;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:1rem 0}
.detail-desc{color:#555;line-height:1.7;margin:1rem 0;font-size:.95rem}
.detail-stock{padding:.8rem 1.2rem;border-radius:15px;font-weight:600;font-size:.9rem;margin:1rem 0;display:inline-block}
.stock-yes{background:rgba(16,185,129,0.1);color:#10b981}
.stock-no{background:rgba(255,71,87,0.1);color:#ff4757}
.qty-selector{display:flex;align-items:center;gap:.5rem;margin:1.5rem 0}
.qty-selector button{width:40px;height:40px;border-radius:50%;border:2px solid var(--pink-1);background:#fff;color:var(--pink-1);font-size:1.2rem;font-weight:700;cursor:pointer}
.qty-selector input{width:60px;text-align:center;border:2px solid rgba(255,77,148,0.2);border-radius:10px;padding:.5rem;font-size:1rem;font-weight:600}
.detail-features{display:grid;grid-template-columns:repeat(2,1fr);gap:.8rem;margin:1.5rem 0}
.feat{background:rgba(255,77,148,0.08);padding:.7rem 1rem;border-radius:12px;font-size:.85rem;border:1px solid rgba(255,77,148,0.15)}
.feat strong{color:var(--pink-1)}

.cart-item{display:flex;justify-content:space-between;align-items:center;padding:1rem;background:rgba(255,77,148,0.05);border-radius:15px;margin-bottom:.8rem;border:1px solid rgba(255,77,148,0.1)}
.cart-item img{width:60px;height:60px;border-radius:12px;object-fit:cover}
.cart-item-info{flex:1;margin-left:1rem}
.cart-item-info strong{display:block;margin-bottom:.3rem}
.cart-item-info small{color:#888}
.cart-actions{display:flex;gap:.3rem;align-items:center}
.cart-total{font-size:1.5rem;font-weight:800;margin:1.5rem 0;text-align:right;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}

.payment-info{background:rgba(255,77,148,0.08);padding:1.2rem;border-radius:15px;margin:1rem 0;font-size:.85rem;border:1px solid rgba(255,77,148,0.2)}
.payment-info strong{color:var(--pink-1);display:block;margin-bottom:.5rem}
.payment-info code{background:#fff;padding:.2rem .5rem;border-radius:6px;color:var(--dark);font-weight:600}

.password-tips{background:rgba(255,77,148,0.08);padding:1rem;border-radius:12px;margin-bottom:1rem;font-size:.85rem;color:#666}
.password-tips strong{color:var(--pink-1);display:block;margin-bottom:.3rem}
.password-tips ul{margin:.3rem 0 0 1.2rem;line-height:1.6}

.dashboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1.5rem;margin-bottom:2rem}
.stat{background:rgba(255,255,255,0.85);padding:1.8rem;border-radius:20px;box-shadow:0 10px 30px rgba(255,77,148,0.1);position:relative;overflow:hidden}
.stat::before{content:'';position:absolute;top:0;left:0;width:100%;height:4px;background:var(--gradient)}
.stat h3{color:#888;font-size:.8rem;text-transform:uppercase;margin-bottom:.5rem;font-weight:600}
.stat .value{font-size:2rem;font-weight:800;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}

.table{width:100%;background:rgba(255,255,255,0.85);border-radius:20px;overflow:hidden;box-shadow:0 10px 30px rgba(255,77,148,0.1);border-collapse:separate;border-spacing:0}
.table th,.table td{padding:1rem;text-align:left;border-bottom:1px solid rgba(255,77,148,0.1)}
.table th{background:rgba(255,77,148,0.08);font-weight:700;color:var(--pink-1);text-transform:uppercase;font-size:.8rem}

.tab-btns{display:flex;gap:.5rem;margin-bottom:1.5rem;flex-wrap:wrap}
.tab-btn{background:rgba(255,255,255,0.7);border:2px solid rgba(255,77,148,0.15);padding:.7rem 1.3rem;border-radius:50px;cursor:pointer;font-weight:600;color:var(--dark)}
.tab-btn.active{background:var(--gradient);color:#fff;border-color:transparent}

.hidden{display:none}
.badge{padding:.3rem .8rem;border-radius:20px;font-size:.75rem;font-weight:700}
.badge-admin{background:linear-gradient(135deg,#ffd700,#ffa500);color:#fff}
.badge-employee{background:var(--gradient);color:#fff}
.badge-low{background:#ff4757;color:#fff}
.alert{padding:1rem;border-radius:15px;margin-bottom:1rem;font-weight:500}
.alert-error{background:rgba(255,71,87,0.1);color:#ff4757}
#cartBadge{background:#fff;color:var(--pink-1);border-radius:50%;padding:.15rem .5rem;font-size:.75rem;margin-left:.3rem;font-weight:700;min-width:20px;display:inline-block;text-align:center}

.panel-title{font-family:'Playfair Display',serif;margin-bottom:1.5rem;font-size:2.5rem;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;font-weight:900}

.empty-cart{text-align:center;padding:3rem 1rem;color:#888}
.empty-cart .icon{font-size:4rem;margin-bottom:1rem;display:block}

.wa-float{position:fixed;bottom:2rem;right:2rem;background:linear-gradient(135deg,#25d366,#128c7e);color:#fff;width:60px;height:60px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2rem;text-decoration:none;box-shadow:0 10px 30px rgba(37,211,102,0.5);z-index:999;transition:.3s;animation:waBounce 2s infinite}
.wa-float:hover{transform:scale(1.1) rotate(10deg);box-shadow:0 15px 40px rgba(37,211,102,0.7)}
@keyframes waBounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}

footer{background:linear-gradient(135deg,#1a0a15 0%,#2a1528 50%,#1a0a15 100%);color:#fff;padding:4rem 2rem 2rem;margin-top:4rem;border-radius:40px 40px 0 0;position:relative;overflow:hidden}
footer::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--gradient)}
.footer-grid{max-width:1400px;margin:0 auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:2.5rem;margin-bottom:2rem}
.footer-col h3{font-family:'Playfair Display',serif;font-size:1.3rem;margin-bottom:1rem;background:var(--gradient-2);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.footer-col p,.footer-col a{color:rgba(255,255,255,0.75);line-height:1.8;font-size:.9rem;text-decoration:none;display:block;transition:.3s;cursor:pointer}
.footer-col a:hover{color:var(--pink-2);padding-left:5px}
.footer-logo{font-family:'Playfair Display',serif;font-size:2rem;font-weight:900;color:#fff;margin-bottom:1rem;line-height:1.1}
.footer-logo small{font-size:.7rem;letter-spacing:3px;color:var(--pink-2);display:block;text-transform:uppercase}
.footer-bottom{max-width:1400px;margin:0 auto;padding-top:2rem;border-top:1px solid rgba(255,255,255,0.1);text-align:center;color:rgba(255,255,255,0.6);font-size:.85rem}
.footer-contact-item{display:flex;align-items:center;gap:.6rem;margin-bottom:.5rem;color:rgba(255,255,255,0.75);font-size:.9rem}
.footer-contact-item span{color:var(--pink-2);font-size:1.2rem}

@media(max-width:768px){
  .hero-title-wrap h1{font-size:2.5rem}
  .hero p{font-size:1rem}
  .nav-links{gap:.4rem}
  .nav-links button{padding:.4rem .8rem;font-size:.8rem}
  .detail-grid{grid-template-columns:1fr}
  .detail-img{height:280px}
  .logo{font-size:1.3rem}
  .container{padding:0 1rem}
  .modal-content{padding:1.5rem}
  .section-title{font-size:1.8rem}
  .wa-float{bottom:1rem;right:1rem;width:55px;height:55px;font-size:1.7rem}
  footer{padding:3rem 1.5rem 1.5rem}
}
</style>
</head>
"""
HTML += r"""
<body>

<div id="loader">
  <div class="loader-logo">✨ Nora y Ro</div>
  <div class="loader-sub">CARGANDO MAGIA...</div>
</div>

<div class="promo-banner" id="promoBanner">
  🎉 ENVÍO GRATIS en compras superiores a $150.000 · ¡Aprovecha ahora!
</div>

<nav class="navbar">
  <div class="logo">Nora y Ro<small>Accesorios</small></div>
  <div class="nav-links">
    <button onclick="showView('shop')">🛍️ Tienda</button>
    <button onclick="showCart()">🛒<span id="cartBadge">0</span></button>
    <button id="adminBtn" class="hidden" onclick="showView('admin')">⚙️ Panel</button>
    <button id="changePassBtn" class="hidden" onclick="openChangePassword()">🔐</button>
    <button id="loginBtn" onclick="showLogin()">🔑 Ingresar</button>
    <button id="logoutBtn" class="hidden" onclick="logout()">🚪 Salir</button>
    <span id="userLabel"></span>
  </div>
</nav>

<div class="container">
  <section id="shopView">
    <div class="hero">
      <div class="hero-content">
        <div class="hero-badge">✨ Colección 2026</div>
        <div class="hero-title-wrap">
          <h1>Accesorios que Enamoran</h1>
        </div>
        <p>Collares · Manillas · Anillos Personalizados · Bucaramanga</p>
        <div class="hero-cta">
          <button onclick="document.getElementById('productsSection').scrollIntoView({behavior:'smooth'})">Ver Productos ✨</button>
          <button class="btn-outline-light" onclick="openWhatsApp()">💬 Contáctanos</button>
        </div>
      </div>
    </div>

    <h2 class="section-title">¿Por Qué Elegirnos?</h2>
    <p class="section-sub">Más de 4 años brindando accesorios únicos</p>
    <div class="features">
      <div class="feature-card">
        <span class="feature-icon">🚚</span>
        <h3>Envíos Nacionales</h3>
        <p>Llegamos a toda Colombia en 3-6 días hábiles</p>
      </div>
      <div class="feature-card">
        <span class="feature-icon">💎</span>
        <h3>Calidad Premium</h3>
        <p>Materiales seleccionados que no manchan la piel</p>
      </div>
      <div class="feature-card">
        <span class="feature-icon">✨</span>
        <h3>100% Personalizados</h3>
        <p>Diseños únicos hechos especialmente para ti</p>
      </div>
      <div class="feature-card">
        <span class="feature-icon">💝</span>
        <h3>Empaque Regalo</h3>
        <p>Listos para sorprender a quien más amas</p>
      </div>
    </div>

    <h2 class="section-title">Nuestras Categorías</h2>
    <p class="section-sub">Encuentra el accesorio perfecto</p>
    <div class="categories">
      <div class="cat-card" onclick="filterByCat('Collares')">
        <img src="https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500" alt="Collares">
        <div class="cat-overlay"><h3>Collares</h3><p>Elegantes y personalizados</p></div>
      </div>
      <div class="cat-card" onclick="filterByCat('Manillas')">
        <img src="https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=500" alt="Manillas">
        <div class="cat-overlay"><h3>Manillas</h3><p>Únicas y con tu estilo</p></div>
      </div>
      <div class="cat-card" onclick="filterByCat('Anillos')">
        <img src="https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500" alt="Anillos">
        <div class="cat-overlay"><h3>Anillos</h3><p>Detalles que enamoran</p></div>
      </div>
      <div class="cat-card" onclick="filterByCat('Personalizados')">
        <img src="https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=500" alt="Personalizados">
        <div class="cat-overlay"><h3>Personalizados</h3><p>Sets completos exclusivos</p></div>
      </div>
    </div>

    <div id="productsSection">
      <h2 class="section-title">Nuestros Productos</h2>
      <p class="section-sub">Descubre toda nuestra colección</p>
      <div class="filters">
        <input type="text" id="searchInput" placeholder="🔍 Buscar productos..." oninput="renderProducts()" autocomplete="off">
        <select id="categoryFilter" onchange="renderProducts()">
          <option value="">Todas las categorías</option>
        </select>
      </div>
      <div class="grid" id="productsGrid"></div>
    </div>

    <h2 class="section-title">Lo que dicen nuestras clientas</h2>
    <p class="section-sub">Experiencias reales de compradoras felices</p>
    <div class="testimonials">
      <div class="testimonial">
        <div class="testimonial-stars">⭐⭐⭐⭐⭐</div>
        <p class="testimonial-text">¡Me encantó mi manilla personalizada! La calidad es increíble y llegó súper rápido. Sin duda volveré a comprar.</p>
        <div class="testimonial-author">💖 María Camila · Medellín</div>
      </div>
      <div class="testimonial">
        <div class="testimonial-stars">⭐⭐⭐⭐⭐</div>
        <p class="testimonial-text">El collar con el nombre de mi hija quedó hermoso. La atención fue súper amable y el empaque muy lindo.</p>
        <div class="testimonial-author">💖 Ana Lucía · Bogotá</div>
      </div>
      <div class="testimonial">
        <div class="testimonial-stars">⭐⭐⭐⭐⭐</div>
        <p class="testimonial-text">Compré un set para mi novia y quedó fascinada. Son accesorios de muy buena calidad. 100% recomendados.</p>
        <div class="testimonial-author">💖 Carolina R. · Cali</div>
      </div>
    </div>
  </section>

  <section id="adminView" class="hidden">
    <h1 class="panel-title">⚙️ Panel de Administración</h1>
    <div class="tab-btns">
      <button class="tab-btn active" onclick="showTab('dashboard',event)">📊 Dashboard</button>
      <button class="tab-btn" onclick="showTab('products',event)">📦 Productos</button>
      <button class="tab-btn" onclick="showTab('sales',event)">💰 Ventas</button>
      <button class="tab-btn" onclick="showTab('users',event)">👥 Usuarios</button>
    </div>
    <div id="dashboardTab">
      <div class="dashboard" id="statsGrid"></div>
      <h3 style="margin-bottom:1rem;font-family:'Playfair Display',serif;color:var(--pink-1)">🏆 Productos Más Vendidos</h3>
      <table class="table"><thead><tr><th>Producto</th><th>Cantidad</th></tr></thead><tbody id="topProductsBody"></tbody></table>
    </div>
    <div id="productsTab" class="hidden">
      <button class="btn btn-sm" style="margin-bottom:1rem" onclick="openProductModal()">➕ Nuevo Producto</button>
      <div style="overflow-x:auto"><table class="table"><thead><tr><th>Imagen</th><th>Nombre</th><th>Categoría</th><th>Precio</th><th>Stock</th><th>Acciones</th></tr></thead><tbody id="productsTableBody"></tbody></table></div>
    </div>
    <div id="salesTab" class="hidden">
      <div style="overflow-x:auto"><table class="table"><thead><tr><th>ID</th><th>Fecha</th><th>Cliente</th><th>Vendedor</th><th>Método</th><th>Total</th></tr></thead><tbody id="salesTableBody"></tbody></table></div>
    </div>
    <div id="usersTab_content" class="hidden">
      <button class="btn btn-sm" style="margin-bottom:1rem" onclick="openUserModal()">➕ Nuevo Usuario</button>
      <div style="overflow-x:auto"><table class="table"><thead><tr><th>Usuario</th><th>Nombre</th><th>Rol</th><th>Estado</th><th>Acciones</th></tr></thead><tbody id="usersTableBody"></tbody></table></div>
    </div>
  </section>
</div>

<footer>
  <div class="footer-grid">
    <div class="footer-col">
      <div class="footer-logo">Nora y Ro<small>Accesorios</small></div>
      <p>Accesorios personalizados hechos con amor en Bucaramanga. Desde 2020 creando diseños únicos para ti.</p>
    </div>
    <div class="footer-col">
      <h3>📍 Contacto</h3>
      <div class="footer-contact-item"><span>📱</span> 301 306 5949</div>
      <div class="footer-contact-item"><span>📍</span> Bucaramanga, Colombia</div>
      <div class="footer-contact-item"><span>🕘</span> Lun-Sáb · 9am-9pm</div>
      <div class="footer-contact-item"><span>🚚</span> Envíos a toda Colombia</div>
    </div>
    <div class="footer-col">
      <h3>💳 Métodos de Pago</h3>
      <p><strong>Bancolombia:</strong> Ahorros 020-000190-93</p>
      <p><strong>Titular:</strong> Nora Torres</p>
      <p><strong>C.C.:</strong> 1097094688</p>
      <p><strong>Nequi:</strong> 312 422 3657</p>
    </div>
    <div class="footer-col">
      <h3>📋 Información</h3>
      <a onclick="document.getElementById('productsSection').scrollIntoView({behavior:'smooth'})">🛍️ Catálogo</a>
      <a onclick="openWhatsApp()">💬 WhatsApp</a>
      <a onclick="showInfo('envios')">🚚 Envíos ($8.000-$25.000)</a>
      <a onclick="showInfo('cambios')">🔄 Cambios (10 días)</a>
    </div>
  </div>
  <div class="footer-bottom">
    <p>© 2020-2026 Nora y Ro Accesorios · Todos los derechos reservados · Hecho con 💖 en Bucaramanga</p>
  </div>
</footer>

<a href="#" class="wa-float" onclick="openWhatsApp();return false;" title="Escríbenos por WhatsApp">
  <span>💬</span>
</a>

<div class="modal" id="detailModal">
  <div class="modal-content modal-detail">
    <div id="detailContent"></div>
    <button class="btn btn-secondary" style="margin-top:1rem" onclick="closeModal('detailModal')">← Volver a la tienda</button>
  </div>
</div>

<div class="modal" id="loginModal">
  <div class="modal-content">
    <h2>🔑 Iniciar Sesión</h2>
    <div id="loginError"></div>
    <input type="text" id="loginUser" placeholder="Usuario" autocomplete="off">
    <input type="password" id="loginPass" placeholder="Contraseña">
    <button class="btn" onclick="doLogin()">Ingresar ✨</button>
    <button class="btn btn-secondary" style="margin-top:.5rem" onclick="closeModal('loginModal')">Cancelar</button>
  </div>
</div>

<div class="modal" id="changePassModal">
  <div class="modal-content">
    <h2>🔐 Cambiar Contraseña</h2>
    <div id="changePassAlert"></div>
    <input type="password" id="currentPass" placeholder="🔑 Contraseña actual">
    <input type="password" id="newPass" placeholder="✨ Nueva contraseña (mín. 8 caracteres)">
    <input type="password" id="confirmPass" placeholder="✅ Confirmar nueva contraseña">
    <div class="password-tips">
      <strong>💡 Consejos de seguridad:</strong>
      <ul>
        <li>Mínimo 8 caracteres</li>
        <li>Combina mayúsculas y minúsculas</li>
        <li>Incluye números y símbolos</li>
      </ul>
    </div>
    <button class="btn" onclick="changePassword()">🔒 Actualizar</button>
    <button class="btn btn-secondary" style="margin-top:.5rem" onclick="closeModal('changePassModal')">Cancelar</button>
  </div>
</div>

<div class="modal" id="cartModal">
  <div class="modal-content">
    <h2>🛒 Tu Carrito</h2>
    <div id="cartItems"></div>
    <div class="cart-total" id="cartTotal">Total: $0</div>
    <input type="text" id="customerName" placeholder="👤 Tu nombre completo">
    <input type="text" id="customerPhone" placeholder="📱 Tu WhatsApp">
    <input type="text" id="customerCity" placeholder="📍 Ciudad de envío">
    <div class="payment-info">
      <strong>💳 Datos para transferencia:</strong>
      <p>• Bancolombia Ahorros: <code>02000019093</code></p>
      <p>• Nequi: <code>312 422 3657</code></p>
      <p>• Titular: Nora Torres (C.C. 1097094688)</p>
      <p style="margin-top:.5rem">📦 Envío: $8.000 - $25.000 según ciudad</p>
    </div>
    <button class="btn btn-wa" onclick="checkoutWhatsApp()">💬 Pedir por WhatsApp</button>
    <button class="btn" style="margin-top:.5rem" id="checkoutBtn" onclick="checkout()">✨ Registrar Pedido</button>
    <button class="btn btn-secondary" style="margin-top:.5rem" onclick="closeModal('cartModal')">Seguir comprando</button>
  </div>
</div>

<div class="modal" id="productModal">
  <div class="modal-content">
    <h2 id="productModalTitle">Producto</h2>
    <input type="hidden" id="productId">
    <input type="text" id="productName" placeholder="Nombre">
    <textarea id="productDesc" placeholder="Descripción"></textarea>
    <select id="productCategory">
      <option value="Collares">Collares</option>
      <option value="Manillas">Manillas</option>
      <option value="Anillos">Anillos</option>
      <option value="Personalizados">Personalizados</option>
      <option value="Otros">Otros</option>
    </select>
    <input type="number" id="productPrice" placeholder="Precio">
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
"""
HTML += r"""
<script>
const API='/api';
const WA_NUMBER='573013065949';
const WA_MSG='Hola, vengo de tu web y me interesan estos productos';
let token=localStorage.getItem('token')||'';
let currentUser=JSON.parse(localStorage.getItem('user')||'null');
let products=[];
let cart=JSON.parse(localStorage.getItem('cart')||'[]');

function fmt(n){return '$'+Math.round(n).toLocaleString('es-CO');}

function openWhatsApp(customMsg){
  const msg=customMsg||WA_MSG;
  window.open('https://wa.me/'+WA_NUMBER+'?text='+encodeURIComponent(msg),'_blank');
}

async function api(path, options){
  options=options||{};
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
    document.getElementById('changePassBtn').classList.remove('hidden');
    document.getElementById('userLabel').textContent='✨ '+currentUser.name;
    document.getElementById('adminBtn').classList.remove('hidden');
    document.getElementById('checkoutBtn').classList.remove('hidden');
  } else {
    document.getElementById('loginBtn').classList.remove('hidden');
    document.getElementById('logoutBtn').classList.add('hidden');
    document.getElementById('changePassBtn').classList.add('hidden');
    document.getElementById('userLabel').textContent='';
    document.getElementById('adminBtn').classList.add('hidden');
    document.getElementById('checkoutBtn').classList.add('hidden');
  }
  document.getElementById('cartBadge').textContent=cart.reduce(function(s,i){return s+i.quantity},0);
}

function showView(v){
  document.getElementById('shopView').classList.toggle('hidden', v!=='shop');
  document.getElementById('adminView').classList.toggle('hidden', v!=='admin');
  if(v==='admin') loadDashboard();
  window.scrollTo({top:0,behavior:'smooth'});
}

function filterByCat(cat){
  document.getElementById('categoryFilter').value=cat;
  document.getElementById('searchInput').value='';
  renderProducts();
  document.getElementById('productsSection').scrollIntoView({behavior:'smooth'});
}

function showInfo(type){
  const msgs={
    envios:'🚚 ENVÍOS:\n• Tiempo: 3-6 días hábiles\n• Costo: $8.000 a $25.000 según ciudad y tamaño\n• Envíos a toda Colombia\n• GRATIS en compras superiores a $150.000',
    cambios:'🔄 CAMBIOS Y DEVOLUCIONES:\n• 10 días para cambios por defectos de fábrica\n• La garantía depende del producto y su cuidado\n• Contáctanos por WhatsApp para procesar'
  };
  alert(msgs[type]);
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

function openChangePassword(){
  ['currentPass','newPass','confirmPass'].forEach(function(id){document.getElementById(id).value='';});
  document.getElementById('changePassAlert').innerHTML='';
  document.getElementById('changePassModal').classList.add('active');
}

async function changePassword(){
  const current=document.getElementById('currentPass').value;
  const newP=document.getElementById('newPass').value;
  const confirm=document.getElementById('confirmPass').value;
  const alertBox=document.getElementById('changePassAlert');
  if(!current||!newP||!confirm){ alertBox.innerHTML='<div class="alert alert-error">⚠️ Completa todos los campos</div>'; return; }
  if(newP.length<8){ alertBox.innerHTML='<div class="alert alert-error">⚠️ Mínimo 8 caracteres</div>'; return; }
  if(newP!==confirm){ alertBox.innerHTML='<div class="alert alert-error">⚠️ Las contraseñas no coinciden</div>'; return; }
  if(current===newP){ alertBox.innerHTML='<div class="alert alert-error">⚠️ Debe ser diferente</div>'; return; }
  try{
    await api('/auth/change-password',{method:'POST',body:JSON.stringify({current_password:current,new_password:newP})});
    closeModal('changePassModal');
    showToast('🔐 ¡Contraseña actualizada!');
    setTimeout(function(){ logout(); alert('Inicia sesión con tu nueva contraseña'); },1500);
  }catch(e){ alertBox.innerHTML='<div class="alert alert-error">❌ '+e.message+'</div>'; }
}

async function loadProducts(){
  try{
    products=await api('/products');
    const cats=[...new Set(products.map(function(p){return p.category}))];
    const sel=document.getElementById('categoryFilter');
    sel.innerHTML='<option value="">Todas las categorías</option>'+cats.map(function(c){return '<option value="'+c+'">'+c+'</option>'}).join('');
    renderProducts();
  }catch(e){ console.error(e); }
}

function renderProducts(){
  const search=document.getElementById('searchInput').value.toLowerCase();
  const cat=document.getElementById('categoryFilter').value;
  const filtered=products.filter(function(p){
    return (!cat||p.category===cat)&&(!search||p.name.toLowerCase().includes(search)||(p.description||'').toLowerCase().includes(search));
  });
  if(filtered.length===0){
    document.getElementById('productsGrid').innerHTML='<div style="grid-column:1/-1;text-align:center;padding:3rem;color:#888"><h3>😔 No se encontraron productos</h3></div>';
    return;
  }
  document.getElementById('productsGrid').innerHTML=filtered.map(function(p,i){
    return '<div class="card" style="animation-delay:'+(i*0.05)+'s" onclick="showProductDetail('+p.id+')">'+
      '<div class="card-img-wrap">'+
        '<img src="'+p.image+'" onerror="this.src=\'https://via.placeholder.com/400x300/ffb3d1/ffffff?text=Nora+y+Ro\'">'+
        (p.stock<=3&&p.stock>0?'<div class="card-badge">¡Últimas unidades!</div>':'')+
        (p.stock<=0?'<div class="card-badge" style="background:#ff4757">Agotado</div>':'')+
      '</div>'+
      '<div class="card-body">'+
        '<div class="card-category">'+p.category+'</div>'+
        '<h3>'+p.name+'</h3>'+
        '<div class="card-price">'+fmt(p.price)+'</div>'+
        '<div class="card-stock '+(p.stock>0?'available':'')+'">'+(p.stock>0?'✓ Disponible':'✗ Sin stock')+'</div>'+
        '<button class="btn" onclick="event.stopPropagation();showProductDetail('+p.id+')">Ver detalles →</button>'+
      '</div>'+
    '</div>';
  }).join('');
}

function showProductDetail(id){
  const p=products.find(function(x){return x.id===id});
  if(!p) return;
  document.getElementById('detailContent').innerHTML=
    '<div class="detail-grid">'+
      '<div><img src="'+p.image+'" class="detail-img" onerror="this.src=\'https://via.placeholder.com/500/ffb3d1/ffffff\'"></div>'+
      '<div class="detail-info">'+
        '<div class="detail-category">'+p.category+'</div>'+
        '<h1>'+p.name+'</h1>'+
        '<div class="detail-price">'+fmt(p.price)+'</div>'+
        '<div class="detail-stock '+(p.stock>0?'stock-yes':'stock-no')+'">'+(p.stock>0?'✓ '+p.stock+' disponibles':'✗ Agotado')+'</div>'+
        '<p class="detail-desc">'+(p.description||'Producto de alta calidad')+'</p>'+
        '<div class="detail-features">'+
          '<div class="feat"><strong>SKU:</strong> '+(p.sku||'N/A')+'</div>'+
          '<div class="feat"><strong>Categoría:</strong> '+p.category+'</div>'+
          '<div class="feat">🚚 Envío 3-6 días</div>'+
          '<div class="feat">💝 Empaque regalo</div>'+
        '</div>'+
        (p.stock>0?
          '<div class="qty-selector">'+
            '<button onclick="changeDetailQty(-1)">−</button>'+
            '<input type="number" id="detailQty" value="1" min="1" max="'+p.stock+'">'+
            '<button onclick="changeDetailQty(1)">+</button>'+
          '</div>'+
          '<button class="btn" onclick="addToCartFromDetail('+p.id+')">🛒 Agregar al Carrito</button>'+
          '<button class="btn btn-wa" style="margin-top:.5rem" onclick="askByWhatsApp(\''+p.name.replace(/'/g,'')+'\')">💬 Consultar por WhatsApp</button>'
        :'<button class="btn" disabled>Agotado</button>')+
      '</div>'+
    '</div>';
  document.getElementById('detailModal').classList.add('active');
}

function askByWhatsApp(name){
  openWhatsApp('Hola, me interesa el producto: '+name+'. ¿Podrías darme más información?');
}

function changeDetailQty(d){
  const input=document.getElementById('detailQty');
  let v=parseInt(input.value)+d;
  const max=parseInt(input.max);
  if(v<1) v=1;
  if(v>max) v=max;
  input.value=v;
}

function addToCartFromDetail(id){
  const qty=parseInt(document.getElementById('detailQty').value)||1;
  const p=products.find(function(x){return x.id===id});
  const existing=cart.find(function(i){return i.product_id===id});
  if(existing){
    if(existing.quantity+qty<=p.stock) existing.quantity+=qty;
    else return alert('Stock insuficiente');
  } else cart.push({product_id:id,name:p.name,price:p.price,quantity:qty,stock:p.stock,image:p.image});
  localStorage.setItem('cart',JSON.stringify(cart));
  updateUI();
  closeModal('detailModal');
  showToast('✨ ¡Agregado al carrito!');
}

function showToast(msg){
  const t=document.createElement('div');
  t.textContent=msg;
  t.style.cssText='position:fixed;bottom:6rem;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,#ff4d94,#c44bce);color:#fff;padding:1rem 2rem;border-radius:50px;box-shadow:0 10px 30px rgba(255,77,148,0.4);z-index:2000;font-weight:600';
  document.body.appendChild(t);
  setTimeout(function(){t.remove()},2500);
}

function showCart(){
  const items=document.getElementById('cartItems');
  if(cart.length===0){
    items.innerHTML='<div class="empty-cart"><span class="icon">🛒</span><p>Tu carrito está vacío</p></div>';
  } else {
    items.innerHTML=cart.map(function(i,idx){
      return '<div class="cart-item">'+
        '<img src="'+(i.image||'')+'" onerror="this.src=\'https://via.placeholder.com/60/ffb3d1/ffffff\'">'+
        '<div class="cart-item-info">'+
          '<strong>'+i.name+'</strong>'+
          '<small>'+fmt(i.price)+' × '+i.quantity+' = <b>'+fmt(i.price*i.quantity)+'</b></small>'+
        '</div>'+
        '<div class="cart-actions">'+
          '<button class="btn btn-sm btn-outline" onclick="changeQty('+idx+',-1)">−</button>'+
          '<button class="btn btn-sm btn-outline" onclick="changeQty('+idx+',1)">+</button>'+
          '<button class="btn btn-sm btn-danger" onclick="removeFromCart('+idx+')">🗑️</button>'+
        '</div>'+
      '</div>';
    }).join('');
  }
  const total=cart.reduce(function(s,i){return s+i.price*i.quantity},0);
  document.getElementById('cartTotal').textContent='Total: '+fmt(total);
  document.getElementById('cartModal').classList.add('active');
}

function changeQty(idx, d){
  cart[idx].quantity+=d;
  if(cart[idx].quantity<=0) cart.splice(idx,1);
  else if(cart[idx].quantity>cart[idx].stock){ cart[idx].quantity=cart[idx].stock; alert('Stock máximo'); }
  localStorage.setItem('cart',JSON.stringify(cart));
  showCart(); updateUI();
}

function removeFromCart(idx){ cart.splice(idx,1); localStorage.setItem('cart',JSON.stringify(cart)); showCart(); updateUI(); }

function checkoutWhatsApp(){
  if(cart.length===0) return alert('Tu carrito está vacío');
  const nombre=document.getElementById('customerName').value||'Cliente';
  const city=document.getElementById('customerCity').value||'';
  let msg='¡Hola! Soy '+nombre+(city?' de '+city:'')+'. Quiero hacer este pedido:\n\n';
  cart.forEach(function(i){ msg+='• '+i.name+' (x'+i.quantity+') - '+fmt(i.price*i.quantity)+'\n'; });
  const total=cart.reduce(function(s,i){return s+i.price*i.quantity},0);
  msg+='\n💰 Total: '+fmt(total)+'\n\n¿Cómo procedemos con el pago y envío?';
  openWhatsApp(msg);
}

async function checkout(){
  if(!currentUser){ closeModal('cartModal'); showLogin(); return alert('Inicia sesión para registrar ventas'); }
  if(cart.length===0) return alert('Carrito vacío');
  try{
    await api('/sales',{method:'POST',body:JSON.stringify({
      items:cart.map(function(i){return {product_id:i.product_id, quantity:i.quantity}}),
      payment_method:'transferencia',
      customer_name:document.getElementById('customerName').value
    })});
    showToast('✅ ¡Venta registrada!');
    cart=[]; localStorage.removeItem('cart');
    closeModal('cartModal'); updateUI(); loadProducts();
  }catch(e){ alert('Error: '+e.message); }
}

function showTab(t,ev){
  document.querySelectorAll('.tab-btn').forEach(function(b){b.classList.remove('active')});
  if(ev) ev.target.classList.add('active');
  ['dashboardTab','productsTab','salesTab','usersTab_content'].forEach(function(id){document.getElementById(id).classList.add('hidden')});
  if(t==='dashboard'){ document.getElementById('dashboardTab').classList.remove('hidden'); loadDashboard(); }
  if(t==='products'){ document.getElementById('productsTab').classList.remove('hidden'); loadAdminProducts(); }
  if(t==='sales'){ document.getElementById('salesTab').classList.remove('hidden'); loadSales(); }
  if(t==='users'){ document.getElementById('usersTab_content').classList.remove('hidden'); loadUsers(); }
}

async function loadDashboard(){
  try{
    const d=await api('/reports/dashboard');
    document.getElementById('statsGrid').innerHTML=
      '<div class="stat"><h3>📦 Productos</h3><div class="value">'+d.total_products+'</div></div>'+
      '<div class="stat"><h3>⚠️ Stock Bajo</h3><div class="value">'+d.low_stock+'</div></div>'+
      '<div class="stat"><h3>💰 Ventas Hoy</h3><div class="value">'+d.today_sales+'</div></div>'+
      '<div class="stat"><h3>💵 Ingresos Hoy</h3><div class="value">'+fmt(d.today_revenue)+'</div></div>'+
      '<div class="stat"><h3>🛒 Ventas Totales</h3><div class="value">'+d.total_sales+'</div></div>'+
      '<div class="stat"><h3>💎 Ingresos Totales</h3><div class="value">'+fmt(d.total_revenue)+'</div></div>';
    document.getElementById('topProductsBody').innerHTML=d.top_products.map(function(p){return '<tr><td>'+p.name+'</td><td>'+p.quantity+'</td></tr>'}).join('')||'<tr><td colspan="2">Sin datos</td></tr>';
  }catch(e){ console.error(e); }
}

async function loadAdminProducts(){
  const prods=await api('/products');
  document.getElementById('productsTableBody').innerHTML=prods.map(function(p){
    return '<tr>'+
      '<td><img src="'+p.image+'" style="width:50px;height:50px;object-fit:cover;border-radius:10px" onerror="this.src=\'https://via.placeholder.com/50\'"></td>'+
      '<td>'+p.name+'</td><td>'+p.category+'</td><td>'+fmt(p.price)+'</td>'+
      '<td>'+p.stock+(p.stock<=p.min_stock?' <span class="badge badge-low">BAJO</span>':'')+'</td>'+
      '<td>'+
        '<button class="btn btn-sm" onclick=\'editProduct('+JSON.stringify(p).replace(/'/g,"&apos;")+')\'>✏️</button>'+
        (currentUser&&currentUser.role==='admin'?'<button class="btn btn-sm btn-danger" onclick="deleteProduct('+p.id+')">🗑️</button>':'')+
      '</td>'+
    '</tr>';
  }).join('');
}

function openProductModal(){
  document.getElementById('productModalTitle').textContent='Nuevo Producto';
  ['productId','productName','productDesc','productPrice','productStock','productMinStock','productImage','productSku'].forEach(function(id){document.getElementById(id).value=''});
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
  document.getElementById('salesTableBody').innerHTML=sales.map(function(s){
    return '<tr>'+
      '<td>#'+s.id+'</td>'+
      '<td>'+new Date(s.created_at).toLocaleString('es-CO')+'</td>'+
      '<td>'+(s.customer_name||'-')+'</td>'+
      '<td>'+s.user+'</td>'+
      '<td>🏦 '+s.payment_method+'</td>'+
      '<td><strong>'+fmt(s.total)+'</strong></td>'+
    '</tr>';
  }).join('')||'<tr><td colspan="6" style="text-align:center">Sin ventas</td></tr>';
}

async function loadUsers(){
  try{
    const users=await api('/users');
    document.getElementById('usersTableBody').innerHTML=users.map(function(u){
      return '<tr>'+
        '<td>'+u.username+'</td><td>'+u.name+'</td>'+
        '<td><span class="badge badge-'+u.role+'">'+u.role+'</span></td>'+
        '<td>'+(u.active?'✅ Activo':'❌ Inactivo')+'</td>'+
        '<td>'+(u.role!=='admin'?'<button class="btn btn-sm btn-danger" onclick="deleteUser('+u.id+')">🗑️</button>':'-')+'</td>'+
      '</tr>';
    }).join('');
  }catch(e){ alert('Solo administradores'); }
}

function openUserModal(){
  ['userUsername','userName','userPassword'].forEach(function(id){document.getElementById(id).value=''});
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

window.addEventListener('load',function(){
  setTimeout(function(){document.getElementById('loader').classList.add('hidden')},800);
});

updateUI();
loadProducts();
</script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML)

if __name__ == '__main__':
    init_db()
    import os
    port = int(os.environ.get('PORT', 5000))
    print('\n' + '='*55)
    print('🌸 NORA Y RO ACCESORIOS - TIENDA PREMIUM')
    print('='*55)
    print(f'🌐 URL:      http://localhost:{port}')
    print('👤 Usuario:  admin')
    print('🔑 Password: Admin@2026')
    print('📱 WhatsApp: 301 306 5949')
    print('='*55 + '\n')
    app.run(host='0.0.0.0', port=port, debug=False)
