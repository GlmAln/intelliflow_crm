from flask import Flask, render_template_string, request, redirect, url_for, session, make_response
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from .models import CUSTOMER_DATA, PRODUCT_DATA
from .campaign_manager import campaign_manager
from .event_bus import event_bus 
import time
import logging
import uuid 

# Flask config and security

app = Flask(__name__)
app.secret_key = "crm-secure-secret-for-cs411" 
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

csrf = CSRFProtect(app)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
limiter.init_app(app)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crm_auth_audit")

CRM_USERS_AUTH = {
    "leo.dupont": {
        "password_hash": generate_password_hash("crmpassword", method="pbkdf2:sha256:260000"),
        "role": "MarketingAgent",
        "segment": "Male",
        "customer_id": next((c.customer_id for c in CUSTOMER_DATA if c.name == "Leo Dupont"), None),
        "locked_until": 0,
    },
    "mia.dubois": {
        "password_hash": generate_password_hash("crmpassword", method="pbkdf2:sha256:260000"),
        "role": "MarketingAgent",
        "segment": "Female",
        "customer_id": next((c.customer_id for c in CUSTOMER_DATA if c.name == "Mia Dubois"), None),
        "locked_until": 0,
    },
    "jean.petit": {
        "password_hash": generate_password_hash("crmpassword", method="pbkdf2:sha256:260000"),
        "role": "Admin",
        "segment": "Senior Male",
        "customer_id": next((c.customer_id for c in CUSTOMER_DATA if c.name == "Jean Petit"), None),
        "locked_until": 0,
    },
    "victor.moreau": {
        "password_hash": generate_password_hash("crmpassword", method="pbkdf2:sha256:260000"),
        "role": "Client",
        "segment": "Male",
        "customer_id": next((c.customer_id for c in CUSTOMER_DATA if c.name == "Victor Moreau"), None),
        "locked_until": 0,
    },
    "sophie.leroux": {
        "password_hash": generate_password_hash("crmpassword", method="pbkdf2:sha256:260000"),
        "role": "Client",
        "segment": "Female",
        "customer_id": next((c.customer_id for c in CUSTOMER_DATA if c.name == "Sophie Leroux"), None),
        "locked_until": 0,
    },
    "marc.durand": {
        "password_hash": generate_password_hash("crmpassword", method="pbkdf2:sha256:260000"),
        "role": "Client",
        "segment": "Senior Male",
        "customer_id": next((c.customer_id for c in CUSTOMER_DATA if c.name == "Marc Durand"), None),
        "locked_until": 0,
    },
}
# Brute force protection state
FAILED_ATTEMPTS = {}
LOCKOUT_THRESHOLD = 5
LOCKOUT_PERIOD = 300


def is_locked(user_record):
    return user_record.get("locked_until", 0) > time.time()

def record_failed_attempt(key):
    now = time.time()
    rec = FAILED_ATTEMPTS.get(key, {"count": 0, "last_failed": 0})
    rec["count"] += 1
    rec["last_failed"] = now
    FAILED_ATTEMPTS[key] = rec
    if rec["count"] >= LOCKOUT_THRESHOLD:
        if key in CRM_USERS_AUTH:
            CRM_USERS_AUTH[key]["locked_until"] = now + LOCKOUT_PERIOD
            logger.info(f"account locked: {key} until {CRM_USERS_AUTH[key]['locked_until']}")
        else:
            rec["locked_until"] = now + LOCKOUT_PERIOD
            FAILED_ATTEMPTS[key] = rec

def reset_failed_attempts(key):
    if key in FAILED_ATTEMPTS:
        del FAILED_ATTEMPTS[key]

def login_user(username, user_auth_record):
    session["username"] = username
    session["role"] = user_auth_record["role"]
    session["segment"] = user_auth_record["segment"]
    session["customer_id"] = str(user_auth_record["customer_id"]) 
    session.permanent = True

def logout_user():
    session.pop("username", None)
    session.pop("role", None)
    session.pop("segment", None)
    session.pop("customer_id", None)

def require_login(f):
    @wraps(f)
    def _wrap(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return _wrap

# --- Templates (Minimalist UI/UX) ---

STYLE_SHEET = """
    body{font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background:#f4f7f6; color:#333; margin:0; padding:0;}
    .container{max-width:1100px; margin:40px auto; padding:20px; background:#fff; border-radius:12px; box-shadow:0 6px 20px rgba(0,0,0,0.05);}
    .card{background:#fff;padding:32px;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.05);width:100%;max-width:380px; margin: auto;}
    h1, h3{color:#1a1a1a; font-weight:600;}
    .header{display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #e0e0e0; padding-bottom:15px; margin-bottom:25px;}
    .nav-link{text-decoration:none; color:#555; margin-left:20px; font-weight:500; padding: 5px 10px; border-radius:4px;}
    .nav-link:hover{background:#f0f0f0; color:#007bff;}
    hr{border:none; border-top:1px solid #e0e0e0; margin:20px 0;}
    .alert{padding:12px; border-radius:8px; margin-bottom:16px; font-size:14px;}
    .alert-error{background:#fdd; color:#c00; border:1px solid #fbc;}
    .alert-success{background:#e8f5e9; color:#2e7d32; border:1px solid #a5d6a7;}
    .alert-warning{background:#fff3e0; color:#ff9800; border:1px solid #ffcc80;}
    .form-group{margin-bottom:16px;}
    label{display:block;margin-bottom:6px;color:#4a4a4a;font-size:14px;font-weight:500;}
    input[type="text"],input[type="password"],input[type="number"],select{width:100%;padding:10px;border-radius:6px;border:1px solid #ddd;font-size:15px;box-sizing:border-box; margin-top:4px; transition:border-color 0.2s;}
    input:focus, select:focus{border-color:#007bff;}
    button{padding:10px 15px; border-radius:6px; border:none; background:#007bff; color:#fff; font-size:15px; font-weight:600; cursor:pointer; transition:background 0.2s;}
    button:hover{background:#0056b3;}
    .btn-green{background:#28a745;}
    .btn-green:hover{background:#1e7e34;}
    .btn-red{background:#dc3545;}
    .btn-red:hover{background:#c82333;}
    table{width:100%; border-collapse:collapse; margin-top:20px;}
    th, td{padding:12px; border:1px solid #e0e0e0; text-align:center;}
    th{background:#f8f9fa; color:#333; font-weight:600;}
    .metric-primary{color:#007bff; font-weight:bold;}
    .metric-success{color:#28a745; font-weight:bold;}
    .metric-danger{color:#dc3545; font-weight:bold;}
    .metric-warning{color:#ffc107; font-weight:bold;}
    .action-box{border: 1px solid #ddd; padding: 20px; border-radius: 8px; background: #f9f9f9; margin-top: 20px;}
"""

LOGIN_PAGE = """
<!doctype html>
<html>
<head>
  <title>CS411 CRM - Secure Login</title>
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline'">
  <style>
    """ + STYLE_SHEET + """
    body{background:#e9ecef; display:flex; align-items:center; justify-content:center; min-height:100vh;}
  </style>
</head>
<body>
  <div class="card">
    <h1 style="text-align:center; color:#007bff;">IntelliFlow CRM Login</h1>
    {% if error %}
      <div class="alert alert-error">{{ error }}</div>
    {% endif %}
    <form method="post" action="{{ url_for('login') }}">
      <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
      <div class="form-group">
        <label for="username">👤 Username</label>
        <input type="text" id="username" name="username" placeholder="leo.dupont" required autofocus>
      </div>
      <div class="form-group">
        <label for="password">🔒 Password</label>
        <input type="password" id="password" name="password" placeholder="Enter your password" required>
      </div>
      <button type="submit">Login to CRM</button>
    </form>
    <small class="note">CS411 Project #2 - Secure Login Adapted</small>
  </div>
</body>
</html>
"""

PRODUCT_LISTING_PAGE = """
<!doctype html>
<html>
<head><title>Product Listing - MA Module</title>
<style>
    """ + STYLE_SHEET + """
    .action-box{border: 1px solid #e0e0e0; padding: 25px; border-radius: 8px; background: #fdfdfd;}
    .product-select{margin-bottom: 20px; display: flex; align-items: center;}
    .product-select select{flex-grow: 1; margin-right: 15px;}
    
    /* Styles pour la navigation corrigée */
    .nav-group {
        display: flex;
        align-items: center;
        gap: 10px; 
    }
    .user-info {
        font-size: 14px; 
        color: #555;
        font-weight: 500;
    }
</style>
</head>
<body>
  <div class="container">
    <div class="header">
        <h1>🛒 Product Listing</h1>
        
        <div class="nav-group">
            <span class="user-info">User: <strong>{{ username }}</strong> (Segment: {{ segment }})</span>
            <a href="{{ url_for('campaigns_page') }}" class="nav-link">📊 Campaign Analytics</a>
            
            <a href="{{ url_for('logout') }}" class="nav-link btn-red" style="color: white; padding: 8px 12px;">Logout</a>
        </div>
    </div>
    
    <h3>1. Personalized Product Display</h3>
    
    {% if last_event %}
        <div class="alert alert-success">🔔 {{ last_event }}</div>
    {% endif %}

    <div class="action-box">
        {% if is_targeting_active %}
            <div class="alert alert-success">✅ Targeting ACTIVE: Campaign running for segment <strong>{{ segment }}</strong>.</div>
        {% else %}
            <div class="alert alert-warning">⚠️ Targeting INACTIVE: No campaign running for this segment.</div>
        {% endif %}

        <form method="post" action="{{ url_for('simulate_action') }}">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
            
            <div class="product-select form-group">
                <label for="product_id" style="min-width: 150px; margin-right: 10px;">Product Interaction:</label>
                <select name="product_id" required>
                    {% for product in product_list %}
                        <option value="{{ product.product_id }}">
                            {% if product.is_targeted %} 🎯 **TARGETED** | {% endif %}
                            {{ product.name }} (${{ "%.2f"|format(product.base_price) }})
                        </option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="form-group">
                <label for="action_type">Customer Behavior (Triggers Pub-Sub Event):</label>
                <select name="action_type" required>
                    <option value="AdInteraction">➡️ View/Click Ad (Impression)</option>
                    <option value="PutToBasket">🧺 Add to Basket (Intent)</option>
                    <option value="Purchase">💰 Purchase (Conversion)</option>
                    <option value="Cancel">❌ Cancel / Remove (Negative Signal)</option>
                    <option value="Ignore">📉 Ignore Outreach (Negative Signal)</option>
                </select>
            </div>
            
            <button type="submit" class="btn-green" style="width: 100%;">Publish Behavior Event</button>
        </form>
    </div>
  </div>
</body>
</html>
"""

CAMPAIGN_MANAGEMENT_PAGE = """
<!doctype html>
<html>
<head><title>Campaign Management - MA Module</title>
<style>
    """ + STYLE_SHEET + """
    .form-section, .analytics-section{border: 1px solid #e0e0e0; padding: 25px; border-radius: 8px; margin-bottom: 30px; background: #fdfdfd;}
</style>
</head>
<body>
  <div class="container">
    <div class="header">
        <h1>📊 Marketing Analytics & Campaign Management</h1>
        <div>
            <a href="{{ url_for('dashboard') }}" class="nav-link">🛒 Product Listing</a>
            <a href="{{ url_for('logout') }}" class="nav-link btn-red" style="margin-left: 10px;">Logout</a>
        </div>
    </div>

    {% if message %}<div class="alert alert-success">{{ message }}</div>{% endif %}

    <div class="form-section">
        <h3>2. Create New Campaign</h3>
        <form method="post" action="{{ url_for('campaigns_page') }}">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
            <input type="hidden" name="form_type" value="create_campaign"/>
            <div class="form-group"><label for="name">Campaign Name:</label><input type="text" name="name" required></div>
            <div class="form-group"><label for="budget">Allocated Budget ($):</label><input type="number" name="budget" step="0.01" min="0.01" required></div>
            <div class="form-group">
                <label for="product_id">Product & Target Segment:</label>
                <select name="product_id" required>
                    {% for product in product_list %}
                        <option value="{{ product.product_id }}">{{ product.name }} (Targets: {{ product.targeting_segment }})</option>
                    {% endfor %}
                </select>
            </div>
            <button type="submit" class="btn-green">➕ Create Campaign</button>
        </form>
    </div>

    <div class="analytics-section">
        <h3>3. Real-Time Performance Dashboard (Updated by Pub-Sub)</h3>
        {% if campaigns %}
            <table>
                <thead>
                    <tr class="metric-row-header"><th>Campaign</th><th>Target</th><th>Budget</th><th>Conversion Rate</th><th>ROI</th><th>Effectiveness</th></tr>
                </thead>
                <tbody>
                {% for c in campaigns %}
                <tr class="metric-row-data">
                    <td>{{ c.name }}</td>
                    <td>{{ c.target_segment }}</td>
                    <td>${{ "%.2f"|format(c.budget) }}</td>
                    <td class="metric-primary">{{ "%.2f"|format(c.conversion_rate) }}%</td>
                    <td class="{% if c.roi >= 0 %}metric-success{% else %}metric-danger{% endif %}">{{ "%.2f"|format(c.roi) }}</td>
                    <td class="{% if c.effectiveness >= 90 %}metric-success{% elif c.effectiveness < 75 %}metric-danger{% else %}metric-warning{% endif %}">{{ "%.1f"|format(c.effectiveness) }}%</td>
                </tr>
                {% endfor %}
                </tbody>
            </table>
        {% else %}
            <div class="alert alert-warning">No campaigns created yet.</div>
        {% endif %}
    </div>
  </div>
</body>
</html>
"""

# --- Routes ---

@app.route("/", methods=["GET"])
def home():
    if "username" in session:
        return redirect(url_for("dashboard")) 
    return render_template_string(LOGIN_PAGE, error=None)

@app.route("/login", methods=["POST"])
@csrf.exempt
@limiter.limit("5 per minute")
def login():
    try:
        username = request.form.get("username", "").lower().strip()
        password = request.form.get("password", "")
        client_ip = get_remote_address()
        user_auth_record = CRM_USERS_AUTH.get(username)

        if user_auth_record and is_locked(user_auth_record):
            logger.info(f"Blocked login attempt for locked account: {username} from {client_ip}")
            return render_template_string(LOGIN_PAGE, error="Invalid credentials or account temporarily locked.")

        if not user_auth_record or not check_password_hash(user_auth_record["password_hash"], password):
            record_failed_attempt(username)
            record_failed_attempt(client_ip) 
            logger.info(f"Failed login: user={username} ip={client_ip}")
            return render_template_string(LOGIN_PAGE, error="Invalid credentials or account temporarily locked.")

        reset_failed_attempts(username)
        login_user(username, user_auth_record)
        logger.info(f"Login success: user={username} ip={client_ip}")
        return redirect(url_for("dashboard")) 

    except Exception as ex:
        logger.exception("Unexpected error in login")
        return make_response("<h1>Internal Server Error (500)</h1>", 500)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/dashboard", methods=["GET"])
@require_login
def dashboard():
    """
    Implements the Product Listing Page and Segmentation logic.
    """
    customer_segment = session.get("segment")
    active_campaign_product_id = None
    is_targeting_active = False 
    for campaign in campaign_manager.campaigns.values():
        if campaign.target_segment == customer_segment:
            is_targeting_active = True
            if campaign.product_ids:
                active_campaign_product_id = campaign.product_ids[0]
            break
            
    product_list_data = []
    
    for p in PRODUCT_DATA:
        product_data = {
            'product_id': p.product_id,
            'name': p.name,
            'base_price': p.base_price,
            'is_targeted': (p.product_id == active_campaign_product_id)
        }
        product_list_data.append(product_data)
        
    if active_campaign_product_id:
        targeted_product = next((p for p in product_list_data if p['product_id'] == active_campaign_product_id), None)
        if targeted_product:
            product_list_data.remove(targeted_product)
            product_list_data.insert(0, targeted_product)
            
    return render_template_string(
        PRODUCT_LISTING_PAGE, 
        username=session.get("username"),
        segment=customer_segment,
        is_targeting_active=is_targeting_active, 
        product_list=product_list_data,
        last_event=session.pop("last_event", None) 
    )

@app.route("/campaigns", methods=["GET", "POST"])
@require_login
def campaigns_page():
    """
    Implements Campaign Creation and Marketing Analytics display.
    """
    message = None

    if request.method == "POST":
        form_type = request.form.get('form_type')
        
        if form_type == 'create_campaign':
            try:
                name = request.form.get("name")
                budget = float(request.form.get("budget"))
                product_id_str = request.form.get("product_id")
                
                selected_product = next(p for p in PRODUCT_DATA if str(p.product_id) == product_id_str)
                
                campaign_manager.create_campaign(
                    name=name,
                    target_segment=selected_product.targeting_segment,
                    budget=budget,
                    product_ids=[selected_product.product_id] 
                )
                message = f"Campaign '{name}' successfully created and targets segment '{selected_product.targeting_segment}'."

            except Exception as e:
                message = f"Error creating campaign: {e}"
                logger.error(f"Campaign creation failed: {e}")
        
    return render_template_string(
        CAMPAIGN_MANAGEMENT_PAGE,
        campaigns=campaign_manager.campaigns.values(),
        product_list=PRODUCT_DATA,
        message=message
    )


@app.route("/simulate-action", methods=["POST"])
@require_login
def simulate_action():
    """
    Implements the Publisher logic by simulating a customer action and publishing the event.
    """
    product_id_str = request.form.get("product_id")
    action_type = request.form.get("action_type")
    selected_product = next((p for p in PRODUCT_DATA if str(p.product_id) == product_id_str), None)
    campaign_id = None
    campaign_name = "Unknown Campaign"
    
    for campaign in campaign_manager.campaigns.values():
        if selected_product and selected_product.product_id in campaign.product_ids:
            campaign_id = campaign.campaign_id
            campaign_name = campaign.name
            break

    if not campaign_id or not selected_product:
        session["last_event"] = f"Action '{action_type}' ignored: No active campaign tracks this product."
        return redirect(url_for('dashboard'))

    event_data = {
        'customer_id': session.get("customer_id"),
        'product_id': selected_product.product_id,
        'campaign_id': campaign_id,
        'value': selected_product.base_price
    }
    
    event_bus.publish(action_type, event_data) 
    
    session["last_event"] = f"Event '{action_type}' published successfully for campaign '{campaign_name}'."
    
    return redirect(url_for('dashboard'))


campaign_manager.setup_subscriptions()


if __name__ == "__main__":
    print("\n--- Running Flask App for Login and MA Demo ---")
    print("Access: http://127.0.0.1:5000/")
    app.run(debug=True, use_reloader=False)