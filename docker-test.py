from sqlalchemy import create_engine, text
import time

time.sleep(10)  # Wait for the database to be ready

engine = create_engine("postgresql+psycopg2://dbadmin:pass@database:5432/postgres")
conn = engine.connect()
print("Connected to the database successfully.")

conn.execute(text("CREATE TABLE IF NOT EXISTS identity (id SERIAL PRIMARY KEY, _name VARCHAR(255), surname VARCHAR(255));"))
conn.commit()
print("Table 'identity' created successfully.")

query=text("INSERT INTO identity (_name, surname) VALUES ('Michel', 'Palefrois'), ('Renaud', 'Bertop');")
conn.execute(query)
conn.commit()
print("Data inserted into 'identity' table successfully.")

result = conn.execute(text("SELECT * FROM identity;"))
for row in result:
    print(row)

conn.close()
print("Database connection closed.")

print("Test completed successfully.")