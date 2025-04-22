import streamlit as st
import pandas as pd
import openai
import json
import os

# Securely pull OpenAI API key from Streamlit secrets
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

# Define the Power BI target schema for HR Attrition Dashboard
TARGET_SCHEMA = [
    "EmployeeID", "FullName", "StartDate", "EndDate", "Department", "Region", "Status"
]

st.title("PowerDash Data Adapter")
st.write("Upload your HR data and we'll reformat it to fit your Power BI dashboard.")

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Read the file into a dataframe
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("🔍 **Preview of your file:**")
    st.dataframe(df.head())

    # Extract columns from uploaded file
    user_columns = list(df.columns)

    # Create mapping prompt
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
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful data assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        mapping_str = response.choices[0].message.content
        mapping = json.loads(mapping_str)

        st.success("✅ Column mapping complete.")
        st.json(mapping)

        # Rename columns and filter based on target schema
        df_mapped = df.rename(columns=mapping)
        final_df = df_mapped[[col for col in TARGET_SCHEMA if col in df_mapped.columns]]

        st.write("📊 **Transformed Data:**")
        st.dataframe(final_df.head())

        # Allow download
        csv = final_df.to_csv(index=False)
        st.download_button("📥 Download Transformed File", csv, "transformed_hr_data.csv", "text/csv")

    except Exception as e:
        st.error("❌ Something went wrong during column mapping.")
        st.text("Error:")
        st.text(e)
