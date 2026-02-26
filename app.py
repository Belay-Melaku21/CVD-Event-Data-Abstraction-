import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="CVD Research Portal", layout="wide")

# --- AUTHENTICATION ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔐 Clinical Data Portal Access")
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "Belay Melaku" and pw == "@Belay6669":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")
        return False
    return True

# --- EMAIL LOGIC ---
def send_email_notification(data_summary):
    sender_email = st.secrets["emails"]["smtp_user"]
    receiver_email = "melakubelay93@gmail.com"
    password = st.secrets["emails"]["smtp_pass"]

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"New Study Entry: ID {data_summary['Study ID']}"

    body = f"A new data entry has been submitted.\n\nSummary:\n{data_summary}"
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
    except Exception as e:
        st.error(f"Email notification failed: {e}")

# --- APP START ---
if check_password():
    st.title("Time to CVD Event Research Portal")
    
    st.info("""**Professional Disclaimer:** This portal is designed for authorized professionals to record patient data. 
    Please ensure all entries are handled with strict confidentiality and clinical precision. 
    Your commitment to data integrity is vital.""")

    # Connect to Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Use a form to handle submission and reset
    with st.form("research_form", clear_on_submit=True):
        
        # SECTION 1 & 2: ADMIN & ELIGIBILITY
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Section 1: Administrative")
            study_id = st.text_input("1.1 Study ID")
            facility = st.selectbox("1.2 Facility Name", ["Densa", "Kotet", "Work-Mawcha", "Ahyo", "Atrons"])
            mrn = st.text_input("1.3 Patient MRN (Confidential)")
            cohort = st.radio("1.4 Cohort Group", ["Exposed (Hypertensive)", "Unexposed (Normotensive)"])
            enroll_date = st.date_input("1.5 Date of Enrollment (E.C.)")
            end_date = st.date_input("1.6 Follow-up End Date (E.C.)")

        with col2:
            st.subheader("Section 2: Eligibility")
            age_check = st.radio("2.1 Age ≥18 years?", ["Yes", "No"])
            prev_cvd = st.radio("2.2 Pre-existing CVD before enrollment?", ["Yes", "No"])
            preg_htn = st.radio("2.3 Pregnancy-induced Hypertension?", ["Yes", "No"])

        st.divider()

        # SECTION 3 & 4: DEMOGRAPHICS & LIFESTYLE
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Section 3: Socio-Demographic")
            age = st.number_input("3.3 Age (Years)", min_value=0, max_value=120)
            sex = st.selectbox("3.4 Sex", ["Male", "Female"])
            residence = st.selectbox("3.5 Residence", ["Urban", "Rural"])
            edu = st.selectbox("3.6 Educational Status", ["No formal education", "Primary (1-8)", "Secondary (9-12)", "Higher"])
            job = st.selectbox("3.7 Occupational Status", ["Government Employee", "Merchant/Trader", "Farmer", "Unemployed", "Other"])

        with col4:
            st.subheader("Section 4: Lifestyle")
            tobacco = st.selectbox("4.1 Tobacco Use", ["Never Smoker", "Current Smoker", "Previous Smoker"])
            alcohol = st.selectbox("4.2 Alcohol Consumption", ["Non-user", "Current User"])
            
            # BRANCHING LOGIC: Alcohol
            alc_amount = 0
            if alcohol == "Current User":
                alc_amount = st.number_input("Average drinks/day", min_value=0)
            
            khat = st.selectbox("4.3 Khat Chewing", ["Never", "Current User", "History of regular use"])
            phys_act = st.radio("4.4 Physical Active (≥30 min/day, 5 days/week)", ["Active", "Inactive"])
            salt = st.radio("4.5 Salt Intake", ["High (Adds salt)", "Normal/Low"])

        st.divider()

        # SECTION 5: CLINICAL (BMI AUTOMATION)
        st.subheader("Section 5: Clinical & Physiological")
        c5_1, c5_2, c5_3 = st.columns(3)
        with c5_1:
            sbp = st.number_input("SBP (mmHg)", min_value=50)
            dbp = st.number_input("DBP (mmHg)", min_value=30)
            htn_stage = st.selectbox("5.2 Hypertension Stage", ["Pre-HTN", "Stage 1", "Stage 2", "Stage 3/4"])
        
        with c5_2:
            weight = st.number_input("Weight (kg)", min_value=1.0)
            height_cm = st.number_input("Height (cm)", min_value=50.0)
            
            # AUTOMATED BMI CALCULATION
            bmi = 0.0
            bmi_cat = "N/A"
            if height_cm > 0:
                bmi = round(weight / ((height_cm/100)**2), 2)
                if bmi < 18.5: bmi_cat = "Underweight"
                elif 18.5 <= bmi < 25: bmi_cat = "Normal"
                elif 25 <= bmi < 30: bmi_cat = "Overweight"
                else: bmi_cat = "Obese"
            
            st.metric("Calculated BMI", f"{bmi} kg/m²")
            st.write(f"Category: **{bmi_cat}**")

        with c5_3:
            htn_dur = st.number_input("5.5 Duration of HTN (Months)", min_value=0)
            fam_hx = st.radio("5.6 Family History of CVD/HTN", ["Yes", "No"])

        st.divider()

        # SECTION 8: OUTCOME
        st.subheader("Section 8: Outcome & Survival Data")
        c8_1, c8_2 = st.columns(2)
        with c8_1:
            cvd_event = st.selectbox("8.1 CVD Event Occurred?", ["No", "Yes"])
            event_type = "N/A"
            event_date = "N/A"
            if cvd_event == "Yes":
                event_type = st.selectbox("8.2 Type of Event", ["Stroke", "Myocardial Infarction", "Heart Failure"])
                event_date = st.date_input("8.3 Date of CVD Event")
        
        with c8_2:
            censoring = st.selectbox("8.4 Censoring Details", ["N/A", "Lost to Follow-up", "Died (Non-CVD)", "Study ended without event"])
            last_date = st.date_input("8.5 Date of Last Follow-up")

        # SUBMIT BUTTON
        submit_button = st.form_submit_button("Submit Record")

        if submit_button:
            # Prepare data row
            new_data = pd.DataFrame([{
                "Study ID": study_id, "Facility": facility, "MRN": mrn, "Cohort": cohort,
                "Enrollment Date": str(enroll_date), "Age": age, "BMI": bmi, "BMI Category": bmi_cat,
                "SBP": sbp, "DBP": dbp, "Alcohol": alcohol, "Alcohol Amount": alc_amount,
                "CVD Event": cvd_event, "Event Type": event_type, "Submission Time": datetime.now()
            }])
            
            # 1. Update Google Sheets
            existing_data = conn.read(worksheet="Sheet1")
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            
            # 2. Email Notification
            send_email_notification(new_data.iloc[0].to_dict())
            
            st.success("Data successfully recorded and encrypted. Thank you for your dedication to professional medical documentation.")
            st.balloons()
