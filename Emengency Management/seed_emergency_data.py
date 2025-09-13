import sqlite3
from datetime import datetime, timedelta
import random

DB_PATH = "C:/Users/ADMIN/Documents/Emengency Management/emergency.db"

def seed_sample_data(db_name='emergency.db', num_records=20):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Sample patient names and symptoms
    names = ["John Doe", "Jane Smith", "Alice Johnson", "Bob Lee", "Chris Evans",
             "Diana Prince", "Ethan Hunt", "Fiona Gallagher", "George Clooney", "Hannah Baker"]
    symptoms_list = ["Chest pain", "Headache", "Shortness of breath", "Fever", "Broken arm",
                     "Severe abdominal pain", "High blood pressure", "Dizziness", "Loss of consciousness", "Severe allergic reaction"]

    # Insert sample records
    for _ in range(num_records):
        name = random.choice(names)
        age = random.randint(1, 90)
        symptoms = random.choice(symptoms_list)
        urgency_level = random.choice([1, 2, 3])
        # Random arrival time within last 7 days
        arrival_time = datetime.now() - timedelta(days=random.randint(0,6), hours=random.randint(0,23), minutes=random.randint(0,59))
        status = random.choice(["Pending", "In Progress", "Completed"])

        cursor.execute('''
            INSERT INTO cases (patient_name, age, symptoms, urgency_level, arrival_time, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, age, symptoms, urgency_level, arrival_time.strftime('%Y-%m-%d %H:%M:%S'), status))

    conn.commit()
    conn.close()
    print(f"Inserted {num_records} sample records into {db_name}")

if __name__ == "__main__":
    seed_sample_data()
