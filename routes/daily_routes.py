from flask import Blueprint, render_template, request, redirect, url_for, flash, g
import sqlite3
from datetime import datetime, timedelta

daily_bp = Blueprint('daily', __name__)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('finance.db')
        g.db.row_factory = sqlite3.Row
    return g.db

def get_date_range(period='today'):
    today = datetime.now()
    if period == 'today':
        start_date = end_date = today.strftime('%Y-%m-%d')
    elif period == 'week':
        start_date = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    elif period == 'month':
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    else:
        return None, None
    return start_date, end_date

@daily_bp.route('/', methods=['GET'])
def daily_home():
    db = get_db()
    cursor = db.cursor()

    # معلمات الفلترة
    period = request.args.get('period', 'all')
    filter_type = request.args.get('filter_type', '')
    filter_category = request.args.get('filter_category', '')
    min_amount = request.args.get('min_amount', '')
    max_amount = request.args.get('max_amount', '')
    search = request.args.get('search', '')

    # بناء الاستعلام
    query = '''
        SELECT r.*, c.type as cat_type
        FROM records r
        LEFT JOIN categories c ON r.category = c.name
        WHERE 1=1
    '''
    params = []

    # إضافة شروط الفلترة
    start_date, end_date = get_date_range(period)
    if start_date and end_date:
        query += ' AND r.date BETWEEN ? AND ?'
        params.extend([start_date, end_date])

    if filter_type:
        query += ' AND r.type = ?'
        params.append(filter_type)

    if filter_category:
        query += ' AND r.category = ?'
        params.append(filter_category)

    if min_amount:
        query += ' AND r.amount >= ?'
        params.append(float(min_amount))

    if max_amount:
        query += ' AND r.amount <= ?'
        params.append(float(max_amount))

    if search:
        query += ' AND (r.note LIKE ? OR r.category LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term, search_term])

    query += ' ORDER BY r.date DESC, r.id DESC'

    # تنفيذ الاستعلام وتجميع النتائج
    cursor.execute(query, params)
    records = cursor.fetchall()

    # تجميع العمليات حسب التاريخ
    grouped_records = {}
    for record in records:
        date = record['date']
        if date not in grouped_records:
            grouped_records[date] = {
                'records': [],
                'totals': {'دخل': 0, 'مصروف': 0, 'توفير': 0, 'إعانة': 0}
            }
        grouped_records[date]['records'].append(record)
        grouped_records[date]['totals'][record['type']] += record['amount']

    # جلب التصنيفات
    cursor.execute('SELECT name, type FROM categories ORDER BY type, name')
    categories = cursor.fetchall()

    # حساب الإحصائيات
    summary = {
        'دخل': {'total': 0, 'count': 0},
        'مصروف': {'total': 0, 'count': 0},
        'توفير': {'total': 0, 'count': 0},
        'إعانة': {'total': 0, 'count': 0}
    }

    for date_data in grouped_records.values():
        for record in date_data['records']:
            type_ = record['type']
            summary[type_]['total'] += record['amount']
            summary[type_]['count'] += 1

    summary['الرصيد'] = summary['دخل']['total'] - summary['مصروف']['total']

    return render_template('daily.html',
                         grouped_records=grouped_records,
                         categories=categories,
                         summary=summary,
                         period=period,
                         filter_type=filter_type,
                         filter_category=filter_category,
                         min_amount=min_amount,
                         max_amount=max_amount,
                         search=search,
                         today=datetime.now().strftime('%Y-%m-%d'))

@daily_bp.route('/add', methods=['POST'])
def add_record():
    if request.method == 'POST':
        type_ = request.form['type']
        category = request.form['category']
        try:
            amount = float(request.form['amount'])
            if amount <= 0:
                raise ValueError("المبلغ يجب أن يكون أكبر من صفر")
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('daily.daily_home'))

        date = request.form['date']
        note = request.form['note']

        db = get_db()
        try:
            db.execute('''
                INSERT INTO records (type, category, amount, date, note)
                VALUES (?, ?, ?, ?, ?)
            ''', (type_, category, amount, date, note))
            db.commit()
            flash('تمت إضافة العملية بنجاح!', 'success')
        except sqlite3.Error as e:
            flash(f'حدث خطأ: {str(e)}', 'error')

    return redirect(url_for('daily.daily_home'))

@daily_bp.route('/edit/<int:record_id>', methods=['GET'])
def edit_record(record_id):
    db = get_db()
    cursor = db.cursor()
    
    # جلب العملية المطلوب تعديلها
    cursor.execute('SELECT * FROM records WHERE id = ?', (record_id,))
    record = cursor.fetchone()
    
    # جلب التصنيفات
    cursor.execute('SELECT name FROM categories')
    categories = cursor.fetchall()
    
    if record:
        return render_template('edit_daily.html', record=record, categories=categories)
    else:
        flash('لم يتم العثور على العملية!', 'error')
        return redirect(url_for('daily.daily_home'))

@daily_bp.route('/update/<int:record_id>', methods=['POST'])
def update_record(record_id):
    type_ = request.form['type']
    category = request.form['category']
    amount = float(request.form['amount'])
    date = request.form['date']
    note = request.form['note']
    
    if amount <= 0:
        flash('المبلغ يجب أن يكون أكبر من صفر!', 'error')
        return redirect(url_for('daily.edit_record', record_id=record_id))
    
    db = get_db()
    try:
        db.execute('''
            UPDATE records 
            SET type = ?, category = ?, amount = ?, date = ?, note = ?
            WHERE id = ?
        ''', (type_, category, amount, date, note, record_id))
        
        db.commit()
        flash('تم تحديث العملية بنجاح!', 'success')
    except sqlite3.Error as e:
        flash(f'حدث خطأ: {str(e)}', 'error')
    
    return redirect(url_for('daily.daily_home'))

@daily_bp.route('/delete/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    db = get_db()
    try:
        db.execute('DELETE FROM records WHERE id=?', (record_id,))
        db.commit()
        flash('تم حذف العملية بنجاح!', 'success')
    except sqlite3.Error as e:
        flash(f'حدث خطأ: {str(e)}', 'error')
    
    return redirect(url_for('daily.daily_home'))