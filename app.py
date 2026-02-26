import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# ---------------- AUTHENTICATION ----------------
st.title("Professional Health Data Collection Portal")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if username == "Belay Melaku" and password == "@Belay6669":
    st.success("Login successful ✅")
    st.markdown("""
    **Disclaimer:** This portal is designed for authorized professionals to record patient data.  
    Please ensure all entries are handled with strict confidentiality and clinical precision.  
    Your commitment to data integrity is vital.
    """)

    # ---------------- FORM ----------------
    with st.form("data_entry_form", clear_on_submit=True):
        st.subheader("Section 1: Administrative & Eligibility")
        study_id = st.text_input("Study ID")
        facility = st.selectbox("Facility Name", ["Densa","Kotet","Work-Mawcha","Ahyo","Atrons"])
        mrn = st.text_input("Patient MRN")
        cohort = st.radio("Cohort Group", ["Exposed (Hypertensive)", "Unexposed (Normotensive)"])
        enrollment_date = st.date_input("Date of Enrollment (Baseline Visit)")
        followup_end = st.date_input("Follow-up End Date")

        st.subheader("Section 3: Socio-Demographic")
        age = st.number_input("Age (years)", min_value=0)
        sex = st.radio("Sex", ["Male","Female"])
        residence = st.radio("Residence", ["Urban","Rural"])
        education = st.selectbox("Educational Status", ["No formal education","Primary","Secondary","Higher"])
        occupation = st.text_input("Occupation")

        st.subheader("Section 4: Lifestyle & Behavioral Factors")
        tobacco = st.radio("Tobacco Use", ["Never Smoker","Current Smoker","Previous Smoker"])
        alcohol = st.radio("Alcohol Consumption", ["Non-user","Current User"])
        drinks_per_day = None
        if alcohol == "Current User":
            drinks_per_day = st.number_input("Average drinks/day", min_value=0)

        khat = st.radio("Khat Chewing", ["Never","Current User","History of regular use"])
        physical_activity = st.radio("Physical Activity", ["Active","Inactive"])
        salt_intake = st.radio("Salt Intake", ["High","Normal/Low"])

        st.subheader("Section 5: Clinical Measurements")
        sbp = st.number_input("SBP (mmHg)", min_value=0)
        dbp = st.number_input("DBP (mmHg)", min_value=0)
        weight = st.number_input("Weight (kg)", min_value=0.0)
        height = st.number_input("Height (m)", min_value=0.0)

        # BMI Calculation
        bmi = None
        bmi_category = None
        if weight > 0 and height > 0:
            bmi = round(weight / (height**2), 2)
            if bmi < 18.5:
                bmi_category = "Underweight"
            elif 18.5 <= bmi < 25:
                bmi_category = "Normal"
            elif 25 <= bmi < 30:
                bmi_category = "Overweight"
            else:
                bmi_category = "Obese"
            st.write(f"**BMI:** {bmi} kg/m² ({bmi_category})")

        # ---------------- SUBMIT ----------------
        submitted = st.form_submit_button("Submit")
        if submitted:
            # Save to Google Sheets
            conn = st.connection("gsheets", type="gsheets")
            df = pd.DataFrame([{
                "Study ID": study_id,
                "Facility": facility,
                "MRN": mrn,
                "Cohort": cohort,
                "Enrollment Date": enrollment_date.strftime("%d/%m/%Y"),
                "Follow-up End": followup_end.strftime("%d/%m/%Y"),
                "Age": age,
                "Sex": sex,
                "Residence": residence,
                "Education": education,
                "Occupation": occupation,
                "Tobacco": tobacco,
                "Alcohol": alcohol,
                "Drinks/day": drinks_per_day,
                "Khat": khat,
                "Physical Activity": physical_activity,
                "Salt Intake": salt_intake,
                "SBP": sbp,
                "DBP": dbp,
                "Weight": weight,
                "Height": height,
                "BMI": bmi,
                "BMI Category": bmi_category
            }])
            conn.update(worksheet="Sheet1", data=df)

            # Email Notification
            msg = MIMEText(f"New submission recorded for Study ID: {study_id}, MRN: {mrn}")
            msg["Subject"] = "New Health Data Submission"
            msg["From"] = st.secrets["email"]["smtp_user"]
            msg["To"] = "melakubelay93@gmail.com"

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(st.secrets["email"]["smtp_user"], st.secrets["email"]["smtp_pass"])
                server.send_message(msg)

            st.success("Data submitted successfully and email notification sent ✅")
            st.info("Thank you for accurately completing this record and for your dedication to professional medical documentation.")
else:
    st.warning("Please log in to access the portal.")
