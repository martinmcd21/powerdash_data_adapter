import streamlit as st
import pandas as pd
import openai
import json
import os
from PIL import Image

# Load and display the DashPrep logo
logo_path = "assets/dashprep_logo.png"
logo = Image.open(logo_path)
st.sidebar.image(logo, use_column_width=True)

# Load OpenAI key securely
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

# Dashboard schema options
schemas = {
    "Recruitment & Hiring Dashboard": [
        "Job ID", "Job Title", "Department", "Job Openings", "Filled Positions",
        "Time-to-Hire (Days)", "Cost-per-Hire (USD)", "Offer Acceptance Rate (%)",
        "Candidate Source", "Gender", "Ethnicity", "Age Group", "Date", "Job Level"
    ],
    "Employee Retention & Turnover Dashboard": [
        "Employee ID", "Employee Name", "Department", "Hire Date", "Turnover Status",
        "Exit Date", "Exit Reason", "Voluntary Exit", "Involuntary Exit", "Tenure (Years)",
        "Engagement Score", "Missed KPI", "Turnover Cost (USD)", "Year", "Quarter", "Month"
    ],
    "Payroll & Compensation Dashboard": [
        "Employees", "Month", "Year", "Employee ID", "Department", "Role", "Experience_Level",
        "Base_Salary", "Bonus", "Overtime_Hours", "Overtime_Cost", "Last_Pay_Raise_Percentage",
        "Pay_Raise_Frequency", "Benefits", "Healthcare_Usage", "Retirement_Contribution",
        "Gender", "Total Payroll Cost"
    ],
    "Employee Satisfaction & Engagement Dashboard": [
        "Month", "Employee Name", "Employee ID", "Department", "Role", "Salary",
        "Work-Life Balance Score", "Absenteeism Rate", "Employee Net Promoter Score (eNPS)",
        "Peer Feedback", "Manager Feedback", "Engagement Survey Result"
    ],
    "HR Compliance & Policy Adherence Dashboard": [
        "Employee ID", "Name", "Department", "Age", "Gender", "Position", "IncidentID", "Date",
        "Type", "Severity", "ReportedBy", "LeaveType", "DaysTaken", "PolicyLimit", "Complaint",
        "WeekStart", "HoursWorked", "LegalLimit", "Compliant", "ViolationID", "PolicyViolated",
        "ActionTaken", "TrainingType", "CompletionStatus", "CompletionDate"
    ],
    "Learning & Development Dashboard": [
        "CertificationID", "EmployeeID", "CertificationName", "IssueDate", "ExpiryDate",
        "IsExpired", "Name", "Role", "Manager", "HireDate", "EnrollmentID", "TrainingID",
        "Status", "CompletionDate", "Score", "FeedbackRating", "IsCompleted", "SkillArea",
        "CurrentSkillLevel", "RequiredSkillLevel", "Gap", "Title", "Category", "DeliverMethod",
        "StartDate", "EndDate"
    ]
}

# Sidebar schema selector
st.sidebar.header("Dashboard Configuration")
selected_dashboard = st.sidebar.selectbox("Select a Power BI Dashboard Template", list(schemas.keys()))
TARGET_SCHEMA = schemas[selected_dashboard]

# App title and instructions
st.title("DashPrep – Power BI Data Adapter")
st.write(f"### Preparing data for: **{selected_dashboard}**")

uploaded_file = st.file_uploader("📤 Upload your Excel or CSV file", type=["csv", "xlsx"])

if uploaded_file:
    # Read the file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("🔍 **Preview of your uploaded file:**")
    st.dataframe(df.head())

    user_columns = list(df.columns)

    # GPT prompt to match columns
    prompt = f"""
You are a data expert helping users map spreadsheet columns to a target schema for a Power BI dashboard.

User file columns:
{user_columns}

Target schema:
{TARGET_SCHEMA}

Return a JSON dictionary mapping user columns to matching schema fields.
Format: {{"Start Dt": "StartDate", "Emp Name": "FullName"}}
Only map relevant fields.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful data assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        mapping_str = response.choices[0].message.content
        mapping = json.loads(mapping_str)

        st.success("✅ Column mapping complete.")
        st.json(mapping)

        # Rename and filter
        df_mapped = df.rename(columns=mapping)
        final_df = df_mapped[[col for col in TARGET_SCHEMA if col in df_mapped.columns]]

        st.write("📊 **Cleaned & Matched Data:**")
        st.dataframe(final_df.head())

        # Download
        csv = final_df.to_csv(index=False)
        st.download_button("📥 Download Transformed File", csv, "transformed_data.csv", "text/csv")

    st.markdown("⚡ Powered by [PowerDash HR](https://www.powerdashhr.com)", unsafe_allow_html=True)
