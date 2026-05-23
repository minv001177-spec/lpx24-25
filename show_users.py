# show_users.py - исправленная версия
import sqlite3
import os
import sys

def find_database():
    """Поиск базы данных в разных местах"""
    possible_paths = [
        'instance/users.db',  # Основной путь
        'users.db',           # Альтернативный путь
        os.path.join('instance', 'users.db'),
        os.path.join(os.path.dirname(__file__), 'instance', 'users.db'),
        os.path.join(os.path.dirname(__file__), 'users.db'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def get_db_connection():
    """Подключение к базе данных"""
    db_path = find_database()
    
    if db_path is None:
        print("❌ База данных не найдена!")
        print("\n🔍 Поиск велся в следующих местах:")
        possible_paths = [
            'instance/users.db',
            'users.db',
            os.path.join('instance', 'users.db'),
        ]
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            print(f"   • {abs_path} - {'✅ существует' if os.path.exists(path) else '❌ не найдено'}")
        
        print("\n💡 Решение:")
        print("   1. Запустите python create_db.py для создания БД")
        print("   2. Или проверьте, что файл БД существует в папке instance/")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        print(f"✅ Подключено к БД: {db_path}")
        return conn
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return None

def show_all_users():
    """Показать всех пользователей из базы данных"""
    conn = get_db_connection()
    if conn is None:
        return
    
    cursor = conn.cursor()
    
    # Получаем список всех таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("\n" + "="*80)
    print("📊 АНАЛИЗ БАЗЫ ДАННЫХ")
    print("="*80)
    
    print(f"\n📁 Таблицы в базе данных: {[t['name'] for t in tables]}")
    
    # Проверяем наличие таблицы users
    if 'users' not in [t['name'] for t in tables]:
        print("\n❌ Таблица 'users' не найдена!")
        print("💡 Запустите python create_db.py для создания таблиц")
        conn.close()
        return
    
    # Получаем всех пользователей
    cursor.execute("SELECT * FROM users ORDER BY id")
    users = cursor.fetchall()
    
    if not users:
        print("\n📭 В базе данных нет пользователей.")
        print("💡 Зарегистрируйте первого пользователя через веб-интерфейс")
    else:
        print(f"\n👥 НАЙДЕНО ПОЛЬЗОВАТЕЛЕЙ: {len(users)}")
        print("-"*80)
        
        for user in users:
            print(f"\n🔹 ID: {user['id']}")
            print(f"   📧 Email: {user['email']}")
            print(f"   👤 Username: {user.get('username', 'N/A')}")
            # Показываем только хеш пароля (первые 20 символов)
            if user.get('password'):
                print(f"   🔐 Password hash: {user['password'][:20]}...")
            print(f"   📅 Created: {user.get('created_at', 'N/A')}")
            print(f"   🖼️ Avatar: {user.get('avatar', 'default-avatar.png')}")
            if user.get('bio'):
                bio_preview = user['bio'][:100] + ('...' if len(user['bio']) > 100 else '')
                print(f"   📝 Bio: {bio_preview}")
            print("-"*40)
    
    conn.close()

def show_database_info():
    """Показать информацию о базе данных"""
    db_path = find_database()
    
    if db_path:
        print(f"\n📁 Информация о БД:")
        print(f"   • Путь: {os.path.abspath(db_path)}")
        print(f"   • Размер: {os.path.getsize(db_path)} байт")
        print(f"   • Последнее изменение: {os.path.getmtime(db_path)}")
    else:
        print("\n❌ База данных не найдена")

def fix_database():
    """Создать базу данных, если её нет"""
    print("\n🔧 Попытка создать базу данных...")
    
    # Проверяем, существует ли create_db.py
    if os.path.exists('create_db.py'):
        print("✅ Найден create_db.py, запускаем его...")
        os.system('python create_db.py')
    else:
        print("❌ create_db.py не найден")
        print("Создаю базу данных вручную...")
        
        # Создаем папку instance
        if not os.path.exists('instance'):
            os.makedirs('instance')
        
        # Создаем базу данных
        conn = sqlite3.connect('instance/users.db')
        cursor = conn.cursor()
        
        # Создаем таблицу users
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            avatar TEXT DEFAULT 'default-avatar.png',
            bio TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ База данных создана вручную")

if __name__ == "__main__":
    print("🐍 СКРИПТ ПРОСМОТРА ПОЛЬЗОВАТЕЛЕЙ")
    print("="*50)
    
    # Показываем информацию о БД
    show_database_info()
    
    # Показываем всех пользователей
    show_all_users()
    
    # Если БД не найдена, предлагаем создать
    if find_database() is None:
        print("\n" + "="*50)
        choice = input("💡 Создать базу данных? (y/n): ").strip().lower()
        if choice == 'y':
            fix_database()
            # Повторно показываем пользователей
            show_all_users()