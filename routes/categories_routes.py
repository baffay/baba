from flask import Blueprint, render_template, request, redirect, url_for, flash, g
import sqlite3

categories_bp = Blueprint('categories', __name__)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('finance.db')
        g.db.row_factory = sqlite3.Row
    return g.db

def dict_from_row(row):
    """تحويل Row object إلى dictionary"""
    return dict(zip(row.keys(), row))

@categories_bp.route('/')
def categories_home():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT 
            c.id,
            c.name,
            c.type,
            COUNT(r.id) as usage_count,
            COALESCE(SUM(r.amount), 0) as total_amount
        FROM categories c
        LEFT JOIN records r ON c.name = r.category
        GROUP BY c.id, c.name, c.type
        ORDER BY c.type, c.name
    ''')
    
    categories = cursor.fetchall()
    
    # تنظيم التصنيفات حسب النوع
    organized_categories = {
        'دخل': [],
        'مصروف': [],
        'توفير': [],
        'إعانة': []
    }
    
    for cat in categories:
        # تحويل كل صف إلى dictionary
        cat_dict = {
            'id': cat['id'],
            'name': cat['name'],
            'type': cat['type'],
            'usage_count': cat['usage_count'],
            'total_amount': float(cat['total_amount']) if cat['total_amount'] else 0
        }
        organized_categories[cat['type']].append(cat_dict)
    
    return render_template('categories.html', categories=organized_categories)

@categories_bp.route('/add', methods=['POST'])
def add_category():
    name = request.form['name'].strip()
    type_ = request.form['type']
    
    if not name:
        flash('اسم التصنيف مطلوب!', 'error')
        return redirect(url_for('categories.categories_home'))
    
    db = get_db()
    try:
        db.execute('INSERT INTO categories (name, type) VALUES (?, ?)', 
                  (name, type_))
        db.commit()
        flash('تم إضافة التصنيف بنجاح!', 'success')
    except sqlite3.IntegrityError:
        flash('هذا التصنيف موجود بالفعل!', 'error')
    except sqlite3.Error as e:
        flash(f'حدث خطأ: {str(e)}', 'error')
    
    return redirect(url_for('categories.categories_home'))

@categories_bp.route('/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    db = get_db()
    cursor = db.cursor()
    
    # التحقق من وجود عمليات تستخدم هذا التصنيف
    cursor.execute('''
        SELECT COUNT(*) as count 
        FROM records r 
        JOIN categories c ON r.category = c.name 
        WHERE c.id = ?
    ''', (category_id,))
    
    if cursor.fetchone()['count'] > 0:
        flash('لا يمكن حذف التصنيف لأنه مستخدم في بعض العمليات!', 'error')
        return redirect(url_for('categories.categories_home'))
    
    try:
        db.execute('DELETE FROM categories WHERE id = ?', (category_id,))
        db.commit()
        flash('تم حذف التصنيف بنجاح!', 'success')
    except sqlite3.Error as e:
        flash(f'حدث خطأ: {str(e)}', 'error')
    
    return redirect(url_for('categories.categories_home'))

@categories_bp.route('/edit/<int:category_id>', methods=['POST'])
def edit_category(category_id):
    name = request.form['name'].strip()
    type_ = request.form['type']
    
    if not name:
        flash('اسم التصنيف مطلوب!', 'error')
        return redirect(url_for('categories.categories_home'))
    
    db = get_db()
    try:
        # جلب الاسم القديم للتصنيف
        cursor = db.cursor()
        cursor.execute('SELECT name FROM categories WHERE id = ?', (category_id,))
        old_category = cursor.fetchone()
        
        if old_category:
            old_name = old_category['name']
            
            # تحديث اسم التصنيف في جدول التصنيفات
            db.execute('UPDATE categories SET name = ?, type = ? WHERE id = ?',
                      (name, type_, category_id))
            
            # تحديث اسم التصنيف في جدول العمليات إذا تغير الاسم
            if old_name != name:
                db.execute('UPDATE records SET category = ? WHERE category = ?',
                          (name, old_name))
            
            db.commit()
            flash('تم تعديل التصنيف بنجاح!', 'success')
        else:
            flash('لم يتم العثور على التصنيف!', 'error')
            
    except sqlite3.IntegrityError:
        flash('هذا التصنيف موجود بالفعل!', 'error')
    except sqlite3.Error as e:
        flash(f'حدث خطأ: {str(e)}', 'error')
    
    return redirect(url_for('categories.categories_home'))