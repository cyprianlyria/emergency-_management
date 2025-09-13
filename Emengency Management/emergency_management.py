# emergency_management.py
import streamlit as st
import sqlite3
from datetime import datetime
from dataclasses import dataclass
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
from typing import List

# Configuration
st.set_page_config(
    page_title="Emergency Department System",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data Model
@dataclass
class EmergencyCase:
    case_id: int
    patient_name: str
    age: int
    symptoms: str
    urgency_level: int
    arrival_time: datetime
    status: str = "Pending"

DB_PATH = "C:/Users/ADMIN/Documents/Emengency Management/emergency.db"    

# Database Manager
class EmergencyDB:
    def __init__(self, db_name: str = 'emergency.db'):
        self.conn = sqlite3.connect(db_name)
        self._create_table()

    def _create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                case_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                age INTEGER NOT NULL,
                symptoms TEXT NOT NULL,
                urgency_level INTEGER DEFAULT 1,
                arrival_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Pending'
            )
        ''')
        self.conn.commit()

    def add_case(self, patient_name: str, age: int, symptoms: str, urgency_level: int) -> int:
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO cases (patient_name, age, symptoms, urgency_level)
                VALUES (?, ?, ?, ?)
            ''', (patient_name.strip(), age, symptoms.strip(), urgency_level))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            st.error(f"Database error: {str(e)}")
            return -1

    def get_cases(self, status_filter: str = "All") -> List[EmergencyCase]:
        try:
            query = '''
                SELECT 
                    case_id,
                    patient_name,
                    age,
                    symptoms,
                    urgency_level,
                    strftime('%Y-%m-%d %H:%M', arrival_time),
                    status
                FROM cases
            '''
            params = []

            if status_filter != "All":
                query += " WHERE status = ?"
                params.append(status_filter)

            query += " ORDER BY urgency_level DESC, arrival_time ASC"

            return [
                EmergencyCase(
                    case_id=row[0],
                    patient_name=row[1],
                    age=row[2],
                    symptoms=row[3],
                    urgency_level=row[4],
                    arrival_time=datetime.strptime(row[5], "%Y-%m-%d %H:%M"),
                    status=row[6]
                ) for row in self.conn.execute(query, params).fetchall()
            ]
        except sqlite3.Error as e:
            st.error(f"Database error: {str(e)}")
            return []

    def update_status(self, case_id: int, new_status: str) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE cases 
                SET status = ?
                WHERE case_id = ?
            ''', (new_status, case_id))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            st.error(f"Database error: {str(e)}")
            return False

# UI Components
def case_card(case: EmergencyCase, db: EmergencyDB):
    color_map = {
        1: "#FF6B6B",  # Red - Critical
        2: "#FFD93D",  # Yellow - Urgent
        3: "#6CBE45"   # Green - Routine
    }

    with st.container(border=True):
        st.markdown(f"""
        <div style="border-left: 10px solid {color_map[case.urgency_level]}; padding: 10px">
            <h4>{case.patient_name} ({case.age}yo)</h4>
            <p><strong>Chief Complaint:</strong> {case.symptoms}</p>
            <div style="display: flex; justify-content: space-between">
                <div>
                    <span>Priority: Level {case.urgency_level}</span> | 
                    <span>Arrival: {case.arrival_time.strftime('%H:%M')}</span>
                </div>
                <div>
                    <span style="background-color: #e0e0e0; 
                                padding: 2px 8px; 
                                border-radius: 12px">
                        {case.status}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, _ = st.columns([1,1,4])
        with col1:
            if st.button("Start Treatment", key=f"start_{case.case_id}"):
                db.update_status(case.case_id, "In Progress")
                st.rerun()
        with col2:
            if st.button("Complete Case", key=f"complete_{case.case_id}"):
                db.update_status(case.case_id, "Completed")
                st.rerun()

# Chart Section
def display_charts(db: EmergencyDB):
    cases = db.get_cases(status_filter="All")
    if not cases:
        st.info("No data available for visualization.")
        return

    df = pd.DataFrame([{
        'Urgency Level': case.urgency_level,
        'Status': case.status
    } for case in cases])

    # Bar Chart: Cases by Urgency Level
    urgency_counts = df['Urgency Level'].value_counts().sort_index()
    st.subheader("Cases by Urgency Level")
    st.bar_chart(urgency_counts)

    # Pie Chart: Cases by Status
    status_counts = df['Status'].value_counts()
    st.subheader("Cases by Status")
    fig, ax = plt.subplots()
    ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

    # Doctor-Patient Ratio (static example)
    doctor_patient_data = pd.DataFrame({
        'Role': ['Doctor', 'Patient'],
        'Count': [30, 120]
    })
    st.subheader("Doctor-Patient Ratio")
    chart1 = alt.Chart(doctor_patient_data).mark_arc().encode(
        theta='Count',
        color='Role',
        tooltip=['Role', 'Count']
    )
    st.altair_chart(chart1, use_container_width=True)

    # Arrival Method Distribution (static example)
    arrival_data = pd.DataFrame({
        'Method': ['Ambulance', 'Walk-in', 'Referral'],
        'Count': [50, 70, 20]
    })
    st.subheader("Distribution of Arrival Methods")
    chart2 = alt.Chart(arrival_data).mark_arc().encode(
        theta='Count',
        color='Method',
        tooltip=['Method', 'Count']
    )
    st.altair_chart(chart2, use_container_width=True)

    # Door-to-Balloon Time (static example)
    door_to_balloon_data = pd.DataFrame({
        'Department': ['STEMI', 'Stroke', 'Trauma'],
        'Time (min)': [45, 60, 55]
    })
    st.subheader("Average Door-to-Balloon Time")
    chart3 = alt.Chart(door_to_balloon_data).mark_bar().encode(
        x='Department',
        y='Time (min)',
        color='Department',
        tooltip=['Department', 'Time (min)']
    )
    st.altair_chart(chart3, use_container_width=True)

# Main App
def main():
    db = EmergencyDB()
    st.title("Emergency Department Management 🚑")

    # Sidebar - New Case Registration
    with st.sidebar:
        st.header("New Patient Registration")
        with st.form("new_case", clear_on_submit=True):
            name = st.text_input("Patient Name")
            age = st.number_input("Age", min_value=0, max_value=120, value=30)
            symptoms = st.text_area("Chief Complaint")
            urgency = st.select_slider(
                "Priority Level",
                options=[1, 2, 3],
                format_func=lambda x: ["Level 1 (Critical)", "Level 2 (Urgent)", "Level 3 (Routine)"][x-1]
            )
            if st.form_submit_button("Register Case"):
                if not name.strip() or not symptoms.strip():
                    st.error("Please complete all required fields!")
                else:
                    if db.add_case(name, age, symptoms, urgency) != -1:
                        st.success("Case registered successfully!")

    # Main Interface
    status_filter = st.selectbox(
        "Filter by Status",
        options=["All", "Pending", "In Progress", "Completed"],
        index=0
    )

    cases = db.get_cases(status_filter)
    if not cases:
        st.info("No cases matching current filters")
    else:
        for case in cases:
            case_card(case, db)

    # Display Charts
    with st.expander("📊 Quality Control Charts", expanded=True):
        display_charts(db)

def main():
    db = EmergencyDB()
    st.title("Emergency Department Management 🚑")

    # Sidebar - Admin Toggle and New Patient Registration
    with st.sidebar:
        st.header("Admin Options")
        show_dashboard = st.checkbox("📊 Admin Dashboard", value=False)

        st.header("New Patient Registration")
        with st.form("new_case", clear_on_submit=True):
            name = st.text_input("Patient Name")
            age = st.number_input("Age", min_value=0, max_value=120, value=30)
            symptoms = st.text_area("Chief Complaint")
            urgency = st.select_slider(
                "Priority Level",
                options=[1, 2, 3],
                format_func=lambda x: ["Level 1 (Critical)", "Level 2 (Urgent)", "Level 3 (Routine)"][x-1]
            )
            if st.form_submit_button("Register Case"):
                if not name.strip() or not symptoms.strip():
                    st.error("Please complete all required fields!")
                else:
                    if db.add_case(name, age, symptoms, urgency) != -1:
                        st.success("Case registered successfully!")

    # Show either dashboard or triage interface
    if show_dashboard:
        st.subheader("📊 Admin Dashboard View")
        display_charts(db)
    else:
        st.subheader("📝 Patient Triage Queue")
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All", "Pending", "In Progress", "Completed"],
            index=0
        )

        cases = db.get_cases(status_filter)
        if not cases:
            st.info("No cases matching current filters")
        else:
            for case in cases:
                case_card(case, db)

if __name__ == "__main__":
    main()