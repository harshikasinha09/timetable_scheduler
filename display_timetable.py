import pandas as pd
import streamlit as st


# Load the generated timetable (assuming you've created it already)
timetable_df = pd.read_csv("final_timetable.csv")
st.write("Columns:", timetable_df.columns.tolist())

# Pivot the table: Rows = Time Slots, Columns = Days
timetable_df.columns = timetable_df.columns.str.strip()  # Remove leading/trailing spaces
pivot_table = timetable_df.pivot(index='Time', columns='Day', values='Subject')

pivot_table = timetable_df.pivot(index='Time', columns='Day', values='Subject')

# Fill NaNs with empty string for clean display
pivot_table = pivot_table.fillna("")

# Set Streamlit page layout
st.set_page_config(page_title="AI Timetable Scheduler", layout="wide")

st.title("📅 Generated Timetable")

# Display as a table with better styling
st.dataframe(pivot_table.style.set_properties(**{
    'text-align': 'center',
    'font-size': '16px'
}), use_container_width=True)
st.write(timetable_df.head())

