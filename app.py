import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- ደህንነት እና መግቢያ ---
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

# --- የኢሜል ማሳወቂያ ---
def send_submission_email(details):
    try:
        sender = st.secrets["emails"]["smtp_user"]
        pwd = st.secrets["emails"]["smtp_pass"]
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = "melakubelay93@gmail.com" # [cite: 81]
        msg['Subject'] = f"New CVD Entry - Study ID: {details.get('1.1 Study ID')}"
        body = "\n".join([f"{k}: {v}" for k, v in details.items()])
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, pwd)
        server.sendmail(sender, msg['To'], msg.as_string())
        server.quit()
    except Exception as e:
        st.warning(f"Email could not be sent: {e}")

if check_password():
    st.title("CVD Event Research Portal")
    st.info("This portal is designed for authorized professionals. Please ensure confidentiality and clinical precision. [cite: 84]")

    conn = st.connection("gsheets", type=GSheetsConnection) # [cite: 80]

    with st.form("main_form", clear_on_submit=True): # [cite: 78]
        # Section 1: Administrative
        st.header("Section 1: Administrative & Eligibility")
        s1_col1, s1_col2 = st.columns(2)
        with s1_col1:
            study_id = st.text_input("1.1 Study ID") # [cite: 17]
            facility = st.selectbox("1.2 Facility", ["1=Densa", "2=Kotet", "3=Work-Mawcha", "4=Ahyo", "5=Atrons"]) # [cite: 18]
        with s1_col2:
            mrn = st.text_input("1.3 Patient MRN") # [cite: 19]
            cohort = st.selectbox("1.4 Cohort Group", ["1= Exposed", "2= Unexposed"]) # [cite: 20]
        enroll_date = st.text_input("1.5 Date of Enrollment (Baseline) E.C.") # [cite: 21]
        followup_end = st.text_input("1.6 Follow-up End Date E.C.") # [cite: 22]

        # Section 2: Eligibility
        st.header("Section 2: Eligibility Checklist")
        age_18 = st.radio("2.1 Age ≥18 years?", ["1 = Yes", "2 = No"]) # [cite: 24]
        pre_cvd = st.radio("2.2 Pre-existing CVD?", ["1 = Yes", "2 = No"]) # [cite: 25]
        preg_htn = st.radio("2.3 Pregnancy-induced Hypertension?", ["1 = Yes", "2 = No"]) # [cite: 26]

        # Section 3: Socio-Demographic
        st.header("SECTION 3: SOCIO-DEMOGRAPHIC")
        age = st.number_input("3.3 Age (years)", min_value=0) # [cite: 28]
        sex = st.radio("3.4 Sex", ["1 = Male", "2 = Female"]) # [cite: 29]
        residence = st.radio("3.5 Residence", ["1 = Urban", "2 = Rural"]) # [cite: 30]
        edu = st.selectbox("3.6 Education", ["1=No formal", "2=Primary", "3=Secondary", "4=Higher"]) # [cite: 31]
        occ = st.selectbox("3.7 Occupation", ["1=Gov Employee", "2=Merchant", "3=Farmer", "4=Unemployed", "5=Other"]) # [cite: 32]
        marital = st.selectbox("3.8 Marital Status", ["1=Single", "2=Married", "3=Widowed", "4=Divorced"]) # [cite: 33]

        # Section 4: Lifestyle (Branching Logic)
        st.header("SECTION 4: LIFESTYLE FACTORS")
        tobacco = st.selectbox("4.1 Tobacco Use", ["1=Never", "2=Current", "3=Previous"]) # [cite: 35]
        alcohol = st.selectbox("4.2 Alcohol Consumption", ["1 = Non-user", "2 = Current User"]) # 
        alc_amount = "NA"
        if alcohol == "2 = Current User":
            alc_amount = st.text_input("Drinks per day") # 
        
        khat = st.selectbox("4.3 Khat Chewing", ["1=Never", "2=Current", "3=History"]) # [cite: 37]
        activity = st.radio("4.4 Physical Activity", ["1=Active", "2=Inactive"]) # [cite: 38]
        salt = st.radio("4.5 Salt Intake", ["1=High", "2=Normal/Low"]) # [cite: 39]

        # Section 5: Clinical (BMI calculation)
        st.header("SECTION 5: CLINICAL MEASUREMENTS")
        sbp = st.number_input("5.1 SBP (mmHg)") # [cite: 41]
        dbp = st.number_input("5.1 DBP (mmHg)") # [cite: 41]
        htn_stage = st.selectbox("5.2 HTN Stage", ["1=Pre-HTN", "2=Stage 1", "3=Stage 2", "4=Stage 3/4"]) # [cite: 42]
        
        weight = st.number_input("5.3 Weight (kg)", min_value=0.0) # [cite: 43, 75]
        height_cm = st.number_input("5.3 Height (cm)", min_value=1.0) # [cite: 43, 75]
        
        # BMI Auto-Calculation 
        bmi = 0.0
        bmi_cat = "NA"
        if weight > 0 and height_cm > 0:
            bmi = round(weight / ((height_cm/100)**2), 2)
            if bmi < 18.5: bmi_cat = "1 = Underweight"
            elif 18.5 <= bmi < 25: bmi_cat = "2 = Normal"
            elif 25 <= bmi < 30: bmi_cat = "3 = Overweight"
            else: bmi_cat = "4 = Obese"
        st.write(f"**Calculated BMI:** {bmi} ({bmi_cat})")

        htn_duration = st.text_input("5.5 HTN Duration (months)") # [cite: 45]
        fam_hist = st.radio("5.6 Family History", ["1 = Yes", "2 = No"]) # [cite: 46]

        # Section 6: Biochemical
        st.header("SECTION 6: BIOCHEMICAL PROFILE")
        dm = st.radio("6.1 Diabetes Mellitus", ["1 = Yes", "2 = No"]) # [cite: 48]
        ckd = st.radio("6.2 CKD", ["1 = Yes", "2 = No"]) # [cite: 49]
        proteinuria = st.radio("6.3 Proteinuria", ["1 = Positive", "2 = Negative"]) # [cite: 50]
        cholesterol = st.text_input("6.4 Total Cholesterol (mg/dL)") # [cite: 51]
        complications = st.selectbox("6.5 Baseline Complications", ["1=None", "2=Prior Stroke", "3=Prior Cardiac"]) # [cite: 52]

        # Section 7: Treatment
        st.header("SECTION 7: TREATMENT FACTORS")
        tx_type = st.selectbox("7.1 Med Type", ["1=Monotherapy", "2=Dual", "3=Poly"]) # [cite: 54]
        tx_class = st.selectbox("7.2 Specific Class", ["1=ACEi/ARB", "2=CCB", "3=Diuretics", "4=Beta-Blocker"]) # [cite: 55]
        adherence = st.radio("7.3 Adherence", ["1=Good", "2=Poor"]) # [cite: 56]

        # Section 8: Outcome
        st.header("SECTION 8: OUTCOME DATA")
        cvd_event = st.radio("8.1 CVD Event Occurred?", ["1 = Yes", "2 = No"]) # [cite: 58]
        event_type = "NA"
        event_date = "NA"
        if cvd_event == "1 = Yes":
            event_type = st.selectbox("8.2 Type", ["1=Stroke", "2=MI", "3=Heart Failure"]) # [cite: 59]
            event_date = st.text_input("8.3 Event Date") # [cite: 60]
        
        censoring = st.selectbox("8.4 Censoring", ["1=Lost to Follow-up", "2=Died (Non-CVD)", "3=Study ended"]) # [cite: 61]
        last_visit = st.text_input("8.5 Last Visit Date") # [cite: 62]

        if st.form_submit_button("Submit"):
            submission = {
                "1.1 Study ID": study_id, "1.3 MRN": mrn, "1.2 Facility": facility,
                "BMI": bmi, "BMI Cat": bmi_cat, "Alcohol": alcohol, "Alc Amount": alc_amount,
                "CVD Event": cvd_event, "Event Type": event_type, "Last Date": last_visit,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            # Save to Sheet
            df = pd.DataFrame([submission])
            existing_data = conn.read()
            updated_df = pd.concat([existing_data, df], ignore_index=True)
            conn.update(data=updated_df)
            
            # Email Notification [cite: 81]
            send_submission_email(submission)
            st.success("Record submitted successfully! [cite: 85]")
            st.balloons()
