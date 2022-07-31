import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

dbUser = os.getenv("DB_USER")
dbPassword = os.getenv("DB_PASSWORD")
dbHost = os.getenv("DB_HOST")
dbPort = os.getenv("DB_PORT")
dbName = os.getenv("DB")

connection = psycopg2.connect(
    user=dbUser,
    password=dbPassword,
    host=dbHost,
    port=dbPort,
    database=dbName
)

cursor = connection.cursor()

cursor.execute('DROP TABLE IF EXISTS table2')

cursor.execute('''
CREATE TABLE table2 (
    id INTEGER PRIMARY KEY,
    completed BOOLEAN NOT NULL DEFAULT FALSE
);
''')

cursor.execute('''
INSERT INTO table2 (id, completed) VALUES (%s, %s);
''', (1, True))

cursor.execute('''
INSERT INTO table2 (id, completed) VALUES (%(id)s, %(completed)s);
''', {
    'id': 2,
    'completed': False
})

SQL = 'INSERT INTO table2 (id, completed) VALUES (%(id)s, %(completed)s);'
data = {
    'id': 3,
    'completed': True
}
cursor.execute(SQL, data)

cursor.execute('''
SELECT * FROM table2;
''')

result = cursor.fetchall()
print(result)

connection.commit()

connection.close()
cursor.close()
