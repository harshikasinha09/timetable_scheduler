import streamlit as st
import pandas as pd
from pulp import LpProblem, LpVariable, lpSum, LpMinimize, LpStatus
import io

st.title("📅 AI-Based Timetable Scheduler")
st.write("Upload your CSV files to generate a smart conflict-free timetable.")

# File uploaders
courses_file = st.file_uploader("Upload Courses CSV", type=["csv"])
rooms_file = st.file_uploader("Upload Rooms CSV", type=["csv"])
slots_file = st.file_uploader("Upload Timeslots CSV", type=["csv"])

if st.button("Generate Timetable"):
    if courses_file and rooms_file and slots_file:
        # Load data
        courses = pd.read_csv(courses_file)
        rooms = pd.read_csv(rooms_file)
        slots = pd.read_csv(slots_file)

        prob = LpProblem("TimetableScheduling", LpMinimize)

        timetable_vars = {}
        for i, row in courses.iterrows():
            for slot in slots['Slot']:
                var_name = f"x_{i}_{slot}"
                timetable_vars[(i, slot)] = LpVariable(var_name, 0, 1, cat="Binary")

        # Objective: minimize the total number of slots used (just a dummy objective)
        prob += lpSum(timetable_vars.values())

        # Constraint: Each course must be assigned exactly one slot
        for i in range(len(courses)):
            prob += lpSum(timetable_vars[i, slot] for slot in slots['Slot']) == 1

        # Constraint: A professor cannot teach more than one class in the same slot
        for faculty in courses['Faculty'].unique():
            for slot in slots['Slot']:
                prob += lpSum(
                    timetable_vars[i, slot]
                    for i in range(len(courses))
                    if courses.loc[i, 'Faculty'] == faculty
                ) <= 1

        # Constraint: A class can't have two courses in the same slot
        for cls in courses['Class'].unique():
            for slot in slots['Slot']:
                prob += lpSum(
                    timetable_vars[i, slot]
                    for i in range(len(courses))
                    if courses.loc[i, 'Class'] == cls
                ) <= 1

        # Constraint: A room can't have two lectures at the same time
        for room in courses['Room'].unique():
            for slot in slots['Slot']:
                prob += lpSum(
                    timetable_vars[i, slot]
                    for i in range(len(courses))
                    if courses.loc[i, 'Room'] == room
                ) <= 1

        # Solve
        prob.solve()

        # Extract results
        timetable = []
        for (i, slot), var in timetable_vars.items():
            if var.varValue == 1:
                row = courses.loc[i]
                timetable.append({
                    "Course": row['Course'],
                    "Faculty": row['Faculty'],
                    "Class": row['Class'],
                    "Room": row['Room'],
                    "Slot": slot
                })

        timetable_df = pd.DataFrame(timetable)

        st.success("✅ Timetable generated successfully!")
        st.dataframe(timetable_df)

        csv = timetable_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Timetable CSV", data=csv, file_name="generated_timetable.csv", mime='text/csv')

    else:
        st.warning("⚠️ Please upload all three files to proceed.")
