import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    user=os.getenv('user'),
    password=os.getenv('password'),
    host=os.getenv('host'),
    port=os.getenv('port'),
    dbname=os.getenv('dbname')
)

cur = conn.cursor()

# Select top 5 transcripts
query = "SELECT * FROM dw.fact_youtube_transcripts LIMIT 5;"

cur.execute(query)
records = cur.fetchall()

print("Transcripts:")
for record in records:
    print(record)

cur.close()
conn.close()