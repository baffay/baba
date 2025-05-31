from flask import Flask, render_template, g
import sqlite3
from datetime import datetime
from routes.daily_routes import daily_bp
from routes.categories_routes import categories_bp
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# تسجيل Blueprints
app.register_blueprint(daily_bp, url_prefix='/daily')
app.register_blueprint(categories_bp, url_prefix='/categories')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('finance.db')
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    
    # إحصائيات اليوم
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT type, SUM(amount) as total
        FROM records 
        WHERE date = ?
        GROUP BY type
    ''', (today,))
    today_stats = {row['type']: row['total'] for row in cursor.fetchall()}
    
    # إحصائيات الشهر
    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute('''
        SELECT type, SUM(amount) as total
        FROM records 
        WHERE strftime('%Y-%m', date) = ?
        GROUP BY type
    ''', (current_month,))
    month_stats = {row['type']: row['total'] for row in cursor.fetchall()}
    
    # آخر 5 عمليات
    cursor.execute('''
        SELECT * FROM records 
        ORDER BY date DESC, id DESC 
        LIMIT 5
    ''')
    recent_transactions = cursor.fetchall()
    
    return render_template('index.html',
                         today_stats=today_stats,
                         month_stats=month_stats,
                         recent_transactions=recent_transactions,
                         current_date=today)

@app.template_filter('format_money')
def format_money(amount):
    if amount is None:
        return "0.00"
    return "{:,.2f}".format(amount)

if __name__ == '__main__':
    app.run(debug=True)