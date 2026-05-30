import sqlite3

def add_default_admin():
    conn = sqlite3.connect('station.db')
    cursor = conn.cursor()
    
    # Check if admin already exists
    cursor.execute("SELECT * FROM user WHERE username = 'admin'")
    if cursor.fetchone():
        print("Admin user already exists.")
    else:
        cursor.execute('''
            INSERT INTO user (username, password, role)
            VALUES (?, ?, ?)
        ''', ('admin', '123456', 'admin'))
        conn.commit()
        print("Admin user created successfully!")
        
    conn.close()

if __name__ == '__main__':
    add_default_admin()
