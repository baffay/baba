import sqlite3
from datetime import datetime

def init_db():
    with sqlite3.connect('finance.db') as conn:
        c = conn.cursor()
        
        # جدول التصنيفات
        c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, type)
        )
        ''')
        
        # جدول العمليات
        c.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category) REFERENCES categories(name)
        )
        ''')
        
        # التصنيفات الافتراضية
        default_categories = [
            # دخل
            ('راتب', 'دخل'),
            ('مكافأة', 'دخل'),
            ('عمل إضافي', 'دخل'),
            ('استثمار', 'دخل'),
            ('تجارة', 'دخل'),
            # مصروف
            ('طعام', 'مصروف'),
            ('نقل', 'مصروف'),
            ('إيجار', 'مصروف'),
            ('فواتير', 'مصروف'),
            ('تسوق', 'مصروف'),
            ('صحة', 'مصروف'),
            ('تعليم', 'مصروف'),
            ('ترفيه', 'مصروف'),
            # توفير
            ('توفير شهري', 'توفير'),
            ('صندوق الطوارئ', 'توفير'),
            ('استثمار', 'توفير'),
            # إعانة
            ('إعانة عائلية', 'إعانة'),
            ('تبرع', 'إعانة'),
            ('زكاة', 'إعانة')
        ]
        
        # إضافة التصنيفات الافتراضية
        for cat in default_categories:
            try:
                c.execute('INSERT INTO categories (name, type) VALUES (?, ?)', cat)
            except sqlite3.IntegrityError:
                pass  # تجاهل إذا كان التصنيف موجود
        
        conn.commit()
        
        print("✅ تم إنشاء قاعدة البيانات بنجاح")
        
        # عرض التصنيفات الحالية
        c.execute('SELECT type, GROUP_CONCAT(name) as names FROM categories GROUP BY type')
        categories = c.fetchall()
        print("\nالتصنيفات المتوفرة:")
        for type_, names in categories:
            print(f"\n{type_}:")
            for name in names.split(','):
                print(f"  - {name}")

if __name__ == '__main__':
    init_db()