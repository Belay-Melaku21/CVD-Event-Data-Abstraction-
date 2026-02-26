import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- PRIVATE KEY FORMATTING FIX ---
if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
    if "\\n" in st.secrets["connections"]["private_key"]:
        st.secrets["connections"]["private_key"] = st.secrets["connections"]["private_key"].replace("\\n", "\n")

# --- AUTHENTICATION ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔐 Clinical Data Portal Access")
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "Belay Melaku" and pw == "@Belay6669": # [cite: 69, 70]
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")
        return False
    return True

# --- EMAIL NOTIFICATION ---
def send_summary_email(data):
    try:
        sender = st.secrets["emails"]["smtp_user"]
        pwd = st.secrets["emails"]["smtp_pass"]
        msg = MIMEMultipart()
        msg['From'], msg['To'] = sender, "melakubelay93@gmail.com" # 
        msg['Subject'] = f"CVD Study Submission - ID: {data['Study ID']}"
        
        body = "A new health data record has been submitted:\n\n" + \
               "\n".join([f"{k}: {v}" for k, v in data.items()])
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, pwd)
        server.sendmail(sender, msg['To'], msg.as_string())
        server.quit()
    except Exception as e:
        st.warning(f"Email notification failed: {e}")

# --- MAIN APP ---
if check_password():
    st.title("Time to CVD Event Research Portal")
    # Professional Disclaimer [cite: 84]
    st.info("This portal is designed for authorized professionals to record patient data. "
            "Please ensure all entries are handled with strict confidentiality and clinical precision. "
            "Your commitment to data integrity is vital.")

    conn = st.connection("gsheets", type=GSheetsConnection)

    with st.form("cvd_abstraction_form", clear_on_submit=True): # [cite: 78]
        # SECTION 1 & 2: ADMIN & ELIGIBILITY [cite: 16, 23]
        st.header("Section 1 & 2: Administrative & Eligibility")
        col1, col2 = st.columns(2)
        with col1:
            study_id = st.text_input("Study ID")
            facility = st.selectbox("Facility", ["Densa", "Kotet", "Work-Mawcha", "Ahyo", "Atrons"])
            mrn = st.text_input("Patient MRN (Confidential)")
        with col2:
            cohort = st.selectbox("Cohort Group", ["Exposed (Hypertensive)", "Unexposed (Normotensive)"])
            enroll_date = st.date_input("Date of Enrollment (E.C.)")
            follow_up_end = st.date_input("Follow-up End Date (E.C.)")

        # SECTION 3: SOCIO-DEMOGRAPHIC [cite: 27]
        st.header("Section 3: Socio-Demographic")
        c1, c2, c3 = st.columns(3)
        age = c1.number_input("Age (Years)", min_value=18)
        sex = c2.selectbox("Sex", ["Male", "Female"])
        residence = c3.selectbox("Residence", ["Urban", "Rural"])
        
        edu = st.selectbox("Educational Status", ["No formal education", "Primary (1-8)", "Secondary (9-12)", "Higher"])
        occ = st.selectbox("Occupational Status", ["Government Employee", "Merchant/Trader", "Farmer", "Unemployed", "Other"])
        marital = st.selectbox("Marital Status", ["Single", "Married", "Widowed", "Divorced/Separated"])

        # SECTION 4: LIFESTYLE (BRANCHING LOGIC) [cite: 34, 73]
        st.header("Section 4: Lifestyle Factors")
        tobacco = st.selectbox("Tobacco Use", ["Never Smoker", "Current Smoker", "Previous Smoker"])
        
        alcohol = st.selectbox("Alcohol Consumption", ["Non-user", "Current User"])
        alc_freq = "N/A"
        if alcohol == "Current User":
            alc_freq = st.number_input("Average drinks/day", min_value=0.0)

        khat = st.selectbox("Khat Chewing", ["Never", "Current User", "History of regular use"])
        phys = st.selectbox("Physical Activity", ["Physically Active (≥30 min/day)", "Inactive"])
        salt = st.selectbox("Salt Intake", ["High (Adds salt)", "Normal/Low"])

        # SECTION 5: CLINICAL (BMI AUTOMATION) [cite: 40, 76]
        st.header("Section 5: Clinical Measurements")
        sbp = st.number_input("SBP (mmHg)")
        dbp = st.number_input("DBP (mmHg)")
        
        w_kg = st.number_input("Weight (kg)", min_value=1.0)
        h_cm = st.number_input("Height (cm)", min_value=50.0)
        
        # BMI Calculation
        h_m = h_cm / 100
        bmi = round(w_kg / (h_m**2), 2) if h_m > 0 else 0
        if bmi < 18.5: b_cat = "Underweight"
        elif 18.5 <= bmi < 25: b_cat = "Normal"
        elif 25 <= bmi < 30: b_cat = "Overweight"
        else: b_cat = "Obese"
        st.metric("Calculated BMI", f"{bmi} kg/m²", f"Category: {b_cat}")

        # SECTION 6 & 7: COMORBIDITY & TREATMENT [cite: 47, 53]
        st.header("Section 6 & 7: Profile & Management")
        dm = st.radio("Diabetes Mellitus?", ["Yes", "No"], horizontal=True)
        ckd = st.radio("CKD?", ["Yes", "No"], horizontal=True)
        protein = st.radio("Proteinuria?", ["Positive", "Negative"], horizontal=True)
        chol = st.text_input("Total Cholesterol (mg/dL) - Leave NA if missing", value="NA")
        
        tx_type = st.selectbox("Treatment Type", ["Monotherapy", "Dual Therapy", "Polytherapy"])
        adherence = st.selectbox("Medication Adherence", ["Good (≥80%)", "Poor (<80%)"])

        # SECTION 8: OUTCOME [cite: 57]
        st.header("Section 8: Outcome & Survival")
        cvd_event = st.selectbox("CVD Event Occurred?", ["No", "Yes"])
        
        # Branching Outcome logic
        event_type = "N/A"
        event_date = "N/A"
        if cvd_event == "Yes":
            event_type = st.selectbox("Type of CVD Event", ["Stroke", "Myocardial Infarction", "Heart Failure"])
            event_date = st.date_input("Date of CVD Event")

        censor = st.selectbox("Censoring Details (If no event)", ["N/A", "Lost to Follow-up", "Died (Non-CVD)", "Study Ended"])
        last_date = st.date_input("Date of Last Follow-up/Censoring")

        # Submit Action
        if st.form_submit_button("Submit Clinical Record"):
            record = {
                "Study ID": study_id, "Facility": facility, "MRN": mrn, "Cohort": cohort,
                "Age": age, "Sex": sex, "Alcohol": alcohol, "Drinks/Day": alc_freq,
                "BMI": bmi, "BMI Category": b_cat, "CVD Event": cvd_event, "Event Type": event_type,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save to Google Sheets [cite: 80]
            existing = conn.read(worksheet="Sheet1")
            updated = pd.concat([existing, pd.DataFrame([record])], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated)
            
            # Send Notification 
            send_summary_email(record)
            
            st.success("Record Submitted Successfully.")
            # Closing message [cite: 85]
            st.balloons()
            st.write("Thank you for accurately completing this record and for your dedication to professional medical documentation.")
