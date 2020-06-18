import sqlite3
conn = sqlite3.connect('database.db')
cur = conn.cursor()

def create_table():
  query = """ 
          CREATE TABLE IF NOT EXISTS record(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user VARCHAR(255),
            bicep_curls INT,
            front_raise INT,
            lateral_raise INT,
            squat INT,
            create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
          )
          """
  try:
    cur.execute(query)
  except Exception as err:
    print('ERROR BY CREATE TABLE', err)

def delete_all():
  try:
    cur.execute('DELETE FROM record;')
    conn.commit()
  except Exception as err:
    print('ERROR BY DELETE:', err)
    
def select_all():
  return cur.execute('SELECT * FROM record').fetchall()

def insert_into_db(val_list):
  query = """
      INSERT INTO record(user, bicep_curls, front_raise, lateral_raise, squat)
      VALUES (?, ?, ?, ?, ?);
      """
  try:
      cur.execute(query, val_list)
      conn.commit()
  except Exception as err:
      print('ERROR BY INSERT:', err)

def drop_table():
  query = """ 
        DROP TABLE record
        """
  try:
    cur.execute(query)
  except Exception as err:
    print('ERROR BY DROP TABLE', err)

delete_all()
l = ['andang', 0, 0, 0, 0]
insert_into_db(l)