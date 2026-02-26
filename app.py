import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- ደህንነት እና መግቢያ (Authentication) ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔐 የክሊኒካዊ መረጃ ፖርታል መግቢያ")
        user = st.text_input("የተጠቃሚ ስም (Username)")
        pw = st.text_input("የይለፍ ቃል (Password)", type="password")
        if st.button("ግባ"):
            if user == "Belay Melaku" and pw == "@Belay6669":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("የገቡት መረጃ ትክክል አይደለም")
        return False
    return True

# --- የኢሜል ማሳወቂያ ---
def send_email(details):
    try:
        sender = st.secrets["emails"]["smtp_user"]
        pwd = st.secrets["emails"]["smtp_pass"]
        msg = MIMEMultipart()
        msg['From'], msg['To'] = sender, "melakubelay93@gmail.com"
        msg['Subject'] = f"አዲስ የCVD መረጃ ተመዝግቧል - Study ID: {details.get('1.1 Study ID', 'N/A')}"
        body = "\n".join([f"{k}: {v}" for k, v in details.items()])
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, pwd)
        server.sendmail(sender, msg['To'], msg.as_string())
        server.quit()
    except Exception as e:
        st.warning(f"ኢሜል መላክ አልተቻለም: {e}")

if check_password():
    st.title("Time to CVD Event Research Portal")
    st.markdown("""**መግቢያ:** *ይህ ፖርታል የተፈቀደላቸው ባለሙያዎች የታካሚ መረጃዎችን እንዲመዘግቡ የተዘጋጀ ነው። እባክዎ ሁሉም ግቤቶች በከፍተኛ ሚስጥራዊነት እና ክሊኒካዊ ትክክለኛነት መያዛቸውን ያረጋግጡ።*""")

    # ከGoogle Sheets ጋር መገናኘት
    conn = st.connection("gsheets", type=GSheetsConnection)

    with st.form("cvd_full_checklist", clear_on_submit=True):
        
        # Section 1: Administrative & Eligibility
        st.header("Section 1: Administrative & Eligibility")
        col1, col2 = st.columns(2)
        with col1:
            study_id = st.text_input("1.1 Study ID")
            facility = st.selectbox("1.2 Facility Name", ["1=Densa", "2=Kotet", "3=Work-Mawcha", "4=Ahyo", "5=Atrons"])
        with col2:
            mrn = st.text_input("1.3 Patient MRN")
            cohort = st.selectbox("1.4 Cohort Group", ["1= Exposed (Hypertensive)", "2= Unexposed (Normotensive)"])
        
        enroll_date = st.text_input("1.5 Date of Enrollment (E.C.) (DD/MM/YYYY)")
        followup_end = st.text_input("1.6 Follow-up End Date (E.C.) (DD/MM/YYYY)")

        # Section 2: Eligibility Checklist
        st.header("Section 2: Eligibility Checklist (Exclusion Criteria)")
        age_elig = st.radio("2.1 Age ≥18 years?", ["1 = Yes", "2 = No"])
        pre_cvd = st.radio("2.2 Pre-existing CVD (Stroke/MI/HF) before enrolment?", ["1 = Yes", "2 = No"])
        preg_htn = st.radio("2.3 Pregnancy-induced Hypertension?", ["1 = Yes", "2 = No"])

        # Section 3: Socio-Demographic
        st.header("SECTION 3: SOCIO-DEMOGRAPHIC CHARACTERISTICS")
        col3, col4 = st.columns(2)
        with col3:
            age = st.number_input("3.3 Age (in years)", min_value=0, max_value=120)
            sex = st.radio("3.4 Sex", ["1 = Male", "2 = Female"])
            residence = st.radio("3.5 Residence", ["1 = Urban", "2 = Rural"])
        with col4:
            edu = st.selectbox("3.6 Educational Status", ["1 = No formal education", "2 = Primary (1-8)", "3 = Secondary (9-12)", "4 = Higher"])
            occ = st.selectbox("3.7 Occupational Status", ["1 = Government Employee", "1 = Merchant/Trader", "1 = Farmer", "1 = Unemployed", "1 = Other"])
            occ_other = ""
            if "Other" in occ:
                occ_other = st.text_input("Specify Other Occupation")
            marital = st.selectbox("3.8 Marital Status", ["1 = Single", "2 = Married", "3 = Widowed", "4 = Divorced/Separated"])

        # Section 4: Lifestyle & Behavioral
        st.header("SECTION 4: LIFESTYLE & BEHAVIORAL FACTORS")
        tobacco = st.selectbox("4.1 Tobacco Use", ["1 = Never Smoker", "2 = Current Smoker", "3 = Previous Smoker"])
        alcohol = st.selectbox("4.2 Alcohol Consumption", ["1 = Non-user", "2 = Current User"])
        
        # Branching Logic ለAlcohol
        alc_freq = "NA"
        if alcohol == "2 = Current User":
            alc_freq = st.text_input("Average drinks/day")
        
        khat = st.selectbox("4.3 Khat Chewing", ["1 = Never", "2 = Current User", "3 = History of regular use"])
        physical = st.radio("4.4 Physical Activity (≥30 min/day, 5 days/week)", ["1 = Physically Active", "2 = Inactive"])
        salt = st.radio("4.5 Salt Intake", ["1 = High (Adds salt to food)", "2 = Normal/Low"])

        # Section 5: Clinical & Physiological
        st.header("SECTION 5: CLINICAL & PHYSIOLOGICAL MEASUREMENTS")
        col5, col6 = st.columns(2)
        with col5:
            sbp = st.text_input("5.1 Baseline SBP (mmHg)")
            dbp = st.text_input("5.1 Baseline DBP (mmHg)")
            htn_stage = st.selectbox("5.2 Hypertension Stage", ["1 = Pre-HTN", "2 = Stage 1", "3 = Stage 2", "4 = Stage 3/4"])
        with col6:
            weight = st.number_input("5.3 Weight (kg)", min_value=0.0)
            height_cm = st.number_input("5.3 Height (cm)", min_value=0.0)
            
            # BMI ስሌት (Auto-calculation)
            bmi = 0.0
            bmi_cat = "NA"
            if weight > 0 and height_cm > 0:
                height_m = height_cm / 100
                bmi = round(weight / (height_m ** 2), 2)
                if bmi < 18.5: bmi_cat = "1 = Underweight"
                elif 18.5 <= bmi < 25: bmi_cat = "2 = Normal"
                elif 25 <= bmi < 30: bmi_cat = "3 = Overweight"
                else: bmi_cat = "4 = Obese"
            st.write(f"**Calculated BMI:** {bmi if bmi > 0 else 'NA'}")
            st.write(f"**BMI Category:** {bmi_cat}")

        htn_duration = st.text_input("5.5 Duration of HTN (months)")
        fam_history = st.radio("5.6 Family History of CVD/HTN", ["1 = Yes", "2 = No"])

        # Section 6: Biochemical & Comorbidity
        st.header("SECTION 6: BIOCHEMICAL & COMORBIDITY PROFILE")
        dm = st.radio("6.1 Diabetes Mellitus (DM)", ["1 = Yes", "2 = No"])
        ckd = st.radio("6.2 Chronic Kidney Disease (CKD)", ["1 = Yes", "2 = No"])
        proteinuria = st.radio("6.3 Proteinuria", ["1 = Positive", "2 = Negative"])
        cholesterol = st.text_input("6.4 Total Cholesterol Level (mg/dL) (Write NA if not found)")
        baseline_comp = st.selectbox("6.5 Baseline Complications", ["1 = None", "2 = Prior Stroke", "3 = Prior Cardiac issues"])

        # Section 7: Treatment & Management
        st.header("SECTION 7: TREATMENT & MANAGEMENT FACTORS")
        tx_type = st.selectbox("7.1 Type of Antihypertensive Meds", ["1 = Monotherapy", "2 = Dual Therapy", "3 = Polytherapy"])
        tx_class = st.selectbox("7.2 Specific Class", ["1 = ACEi/ARB", "2 = CCB", "3 = Diuretics", "4 = Beta-Blockers"])
        adherence = st.radio("7.3 Medication Adherence (≥80% attendance/intake)", ["1 = Good", "2 = Poor"])

        # Section 8: Outcome & Survival Data
        st.header("SECTION 8: OUTCOME & SURVIVAL DATA")
        cvd_occurred = st.radio("8.1 CVD Event Occurred?", ["1 = Yes", "2 = No"])
        
        # Branching Logic ለCVD Event
        event_type = "NA"
        event_date = "NA"
        if cvd_occurred == "1 = Yes":
            event_type = st.selectbox("8.2 Type of CVD Event", ["1 = Stroke", "2 = Myocardial Infarction", "3 = Heart Failure"])
            event_date = st.text_input("8.3 Date of CVD Event (DD/MM/YYYY)")

        censoring = st.selectbox("8.4 Censoring Details", ["1 = Lost to Follow-up", "2 = Died (Non-CVD cause)", "3 = Study ended without event"])
        last_date = st.text_input("8.5 Date of Last Follow-up/Censoring (DD/MM/YYYY)")

        # መረጃውን ማጠቃለል
        submit = st.form_submit_button("Submit Record")
        
        if submit:
            all_data = {
                "1.1 Study ID": study_id, "1.2 Facility": facility, "1.3 MRN": mrn, "1.4 Cohort": cohort,
                "1.5 Enroll Date": enroll_date, "1.6 Follow-up End": followup_end,
                "2.1 Age Elig": age_elig, "2.2 Pre-CVD": pre_cvd, "2.3 Preg HTN": preg_htn,
                "3.3 Age": age, "3.4 Sex": sex, "3.5 Residence": residence, "3.6 Edu": edu, "3.7 Occ": occ, "3.7 Occ Other": occ_other, "3.8 Marital": marital,
                "4.1 Tobacco": tobacco, "4.2 Alcohol": alcohol, "4.2 Alc Freq": alc_freq, "4.3 Khat": khat, "4.4 Activity": physical, "4.5 Salt": salt,
                "5.1 SBP": sbp, "5.1 DBP": dbp, "5.2 HTN Stage": htn_stage, "5.3 Weight": weight, "5.3 Height": height_cm, "5.3 BMI": bmi, "5.4 BMI Cat": bmi_cat,
                "5.5 HTN Duration": htn_duration, "5.6 Family Hist": fam_history,
                "6.1 DM": dm, "6.2 CKD": ckd, "6.3 Proteinuria": proteinuria, "6.4 Cholesterol": cholesterol, "6.5 Complications": baseline_comp,
                "7.1 Tx Type": tx_type, "7.2 Class": tx_class, "7.3 Adherence": adherence,
                "8.1 CVD Event": cvd_occurred, "8.2 Event Type": event_type, "8.3 Event Date": event_date, "8.4 Censoring": censoring, "8.5 Last Date": last_date,
                "Submission Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            try:
                # ወደ Google Sheet መመዝገብ
                df = pd.DataFrame([all_data])
                conn.create(data=df)
                
                # ኢሜል መላክ
                send_email(all_data)
                
                st.success("መረጃው በትክክል ተመዝግቧል። ለሙያዊ Medical documentation ትጋትዎ እናመሰግናለን።")
                st.balloons()
            except Exception as e:
                st.error(f"መረጃውን መመዝገብ አልተቻለም: {e}")
