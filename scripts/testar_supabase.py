import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("PG_HOST"),
    port=os.getenv("PG_PORT"),
    dbname=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD")
)

cur = conn.cursor()

cur.execute("SELECT 1;")

resultado = cur.fetchone()

print("Conexão OK:", resultado)

cur.close()
conn.close()