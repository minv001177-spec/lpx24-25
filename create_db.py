# create_db.py - исправленная версия
import sqlite3
import os

def create_database():
    # Создаем папку instance, если её нет
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    # Путь к базе данных в папке instance
    db_path = 'instance/users.db'
    
    # Подключаемся к базе данных (она создастся автоматически)
    conn = sqlite3.connect(db_path)
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
    
    # Создаем другие необходимые таблицы
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS guestbook (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()
    
    print(f"✅ База данных успешно создана: {db_path}")
    print(f"📁 Полный путь: {os.path.abspath(db_path)}")
    
    # Проверяем, создалась ли база данных
    if os.path.exists(db_path):
        print(f"✅ Файл базы данных существует (размер: {os.path.getsize(db_path)} байт)")
    else:
        print(f"❌ Ошибка: файл базы данных не создан!")

def check_database():
    """Проверка существования и структуры базы данных"""
    db_path = 'instance/users.db'
    
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена по пути: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📊 Таблицы в базе данных:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Проверяем структуру таблицы users
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print(f"\n📋 Структура таблицы users:")
        for col in columns:
            print(f"   • {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке БД: {e}")
        return False

if __name__ == "__main__":
    print("🔨 СОЗДАНИЕ БАЗЫ ДАННЫХ")
    print("="*40)
    
    # Создаем базу данных
    create_database()
    
    # Проверяем результат
    print("\n" + "="*40)
    print("ПРОВЕРКА БАЗЫ ДАННЫХ")
    print("="*40)
    check_database()
    
    print("\n💡 Теперь запустите:")
    print("   python show_users.py")