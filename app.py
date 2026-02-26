import streamlit as st
from streamlit_gsheets import GSheetsConnection

# ... (Authentication code here) ...

conn = st.connection("gsheets", type=GSheetsConnection)

with st.form("cvd_form"):
    # Lifestyle Section with Branching Logic
    st.subheader("Section 4: Lifestyle")
    alcohol = st.selectbox("4.2 Alcohol Consumption", ["Non-user", "Current User"])
    
    # Conditional Branching
    alc_freq = "N/A"
    if alcohol == "Current User":
        alc_freq = st.number_input("Average drinks/day", min_value=0.0, step=0.1)

    # Clinical Section with BMI Automation
    st.subheader("Section 5: Clinical Measurements")
    weight = st.number_input("Weight (kg)", min_value=1.0)
    height_cm = st.number_input("Height (cm)", min_value=50.0)
    
    # BMI Formula: BMI = weight / (height_m^2)
    height_m = height_cm / 100
    bmi = round(weight / (height_m**2), 2) if height_m > 0 else 0
    
    # Real-time BMI Category logic
    if bmi < 18.5: bmi_cat = "Underweight"
    elif 18.5 <= bmi < 25: bmi_cat = "Normal"
    elif 25 <= bmi < 30: bmi_cat = "Overweight"
    else: bmi_cat = "Obese"

    st.info(f"Computed BMI: **{bmi}** (Category: **{bmi_cat}**)")

    # Submit
    if st.form_submit_button("Submit Record"):
        # Code to save to Sheet and send email
        st.success("Record Submitted Successfully")
