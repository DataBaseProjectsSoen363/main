import random
from datetime import datetime, timedelta

# ---- CONFIGURATION ----
NUM_PHYSICIANS = 15
NUM_NURSES = 10
NUM_PATIENTS = 40
NUM_ADMISSIONS = 50
SURGERY_PROBABILITY = 0.35  # ~35% of admissions have a surgical procedure

NOW = datetime.now().replace(microsecond=0)

ICD9_POOL = [
    ("401.9", "Unspecified essential hypertension", "High blood pressure with no specific cause.", "Circulatory System"),
    ("410.9", "Acute myocardial infarction, unspecified site", "Heart attack occurring in an unspecified heart region.", "Circulatory System"),
    ("250.00", "Diabetes mellitus without complication", "Type II or unspecified diabetes managed stably.", "Endocrine/Metabolic"),
    ("272.4", "Other and unspecified hyperlipidemia", "Elevated cholesterol and lipids.", "Endocrine/Metabolic")
]
FIRST_NAMES = ["Daniel", "Sarah", "John", "Emily", "Michael", "Amelie", "David", "Jessica", "Robert", "Rachel"]
LAST_NAMES = ["Tremblay", "Smith", "Roy", "Gagnon", "Jones", "Williams", "Brown", "Charette", "Taylor", "Miller"]
CITIES = ["Montreal", "Laval", "Longueuil", "Sherbrooke", "Quebec City"]
STREETS = ["Sherbrooke St", "Sainte-Catherine St", "Papineau Ave", "Guy St", "Atwater Ave"]
UNIT_TYPES = ["ICU", "CCU", "MICU", "SICU"]
EXAM_TYPES = ["Chest X-Ray", "CT Scan - Chest", "Abdominal Ultrasound", "MRI Brain"]
SPECIALTIES = ["Cardiology", "Internal Medicine", "Emergency Medicine", "Pulmonology", "General Surgery"]
ALLERGIES = ["None", "Penicillin", "Sulfa drugs", "Latex", "Peanuts"]
MEDS = ["None", "Metformin", "Atorvastatin", "Lisinopril", "Aspirin", "Metoprolol"]
PRIORITIES = ["Routine", "Urgent", "STAT"]
TECHNICIANS = ["Tech A. Roy", "Tech B. Gagnon", "Tech C. Smith", "Tech D. Tremblay"]
DISCHARGE_DESTINATIONS = ["Home", "Rehab Facility", "Long-Term Care", "Transfer to Another Hospital"]

# Surgical procedure catalogue: (name, body_site)
SURGICAL_PROCEDURES = [
    ("Coronary Artery Bypass Graft", "Heart"),
    ("Appendectomy",                 "Appendix"),
    ("Hip Replacement",              "Right Hip"),
    ("Cholecystectomy",              "Gallbladder"),
    ("Hernia Repair",                "Inguinal Region"),
    ("Knee Replacement",             "Left Knee"),
    ("Craniotomy",                   "Skull"),
    ("Bowel Resection",              "Small Intestine"),
    ("Thoracotomy",                  "Chest Wall"),
    ("Spinal Fusion",                "Lumbar Spine"),
]

# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
def sql_str(value):
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"

def fmt(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def safe_random_date_in_past(max_days_ago):
    return NOW - timedelta(days=random.randint(1, max_days_ago),
                           hours=random.randint(0, 23),
                           minutes=random.randint(0, 59))

def generate_postgres_script(filename="populate_all_hospital.sql"):
    random.seed(42)
    sql = ["-- Complete PostgreSQL Population Script\n", "BEGIN;\n\n"]

    admission_discharge = {}
    admission_alive = {}

    # 1. ICD-9 DICTIONARY
    sql.append("-- 1. ICD-9 Dictionary\n")
    for code, title, desc, cat in ICD9_POOL:
        sql.append(
            f"INSERT INTO icd9_dict (icd9_code, official_diagnosis_title, description, disease_category) "
            f"VALUES ({sql_str(code)}, {sql_str(title)}, {sql_str(desc)}, {sql_str(cat)});\n"
        )

    # 2. PHYSICIANS (with specialty)
    sql.append("\n-- 2. Physicians\n")
    for p_id in range(1, NUM_PHYSICIANS + 1):
        name = f"Dr. {random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        specialty = random.choice(SPECIALTIES)
        sql.append(
            f"INSERT INTO physician (physician_id, name, specialty) "
            f"VALUES ({p_id}, {sql_str(name)}, {sql_str(specialty)});\n"
        )

    # 3. NURSES
    sql.append("\n-- 3. Nurses\n")
    for n_id in range(1, NUM_NURSES + 1):
        name = f"Nurse {random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        sql.append(
            f"INSERT INTO nurse (nurse_id, name) VALUES ({n_id}, {sql_str(name)});\n"
        )

    # 4. PATIENTS
    sql.append("\n-- 4. Patients\n")
    for p_id in range(1, NUM_PATIENTS + 1):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        hin = f"RAMQ{random.randint(100000, 999999)}"
        addr = f"{random.randint(100, 5000)} {random.choice(STREETS)}, {random.choice(CITIES)}"
        dob = (NOW - timedelta(days=random.randint(6500, 30000))).strftime("%Y-%m-%d")
        gender = random.choice(["Male", "Female"])
        phone = f"514-555-{random.randint(1000, 9999)}"
        sql.append(
            f"INSERT INTO patient (patient_id, name, health_insurance_number, life_status, address, "
            f"date_birth, gender, emergency_contact_number, phone_number) "
            f"VALUES ({p_id}, {sql_str(name)}, {sql_str(hin)}, 'Alive', {sql_str(addr)}, "
            f"{sql_str(dob)}, {sql_str(gender)}, {sql_str(phone)}, {sql_str(phone)});\n"
        )

    # 5. ADMISSIONS + DEPENDENT ENTITIES
    sql.append("\n-- 5. Admissions and Dependent Systems\n")

    order_id = 1
    exam_id = 1
    note_id = 1
    stay_id = 1
    diag_id = 1
    triage_id = 1
    discharge_id = 1
    procedure_id = 1

    for a_id in range(1, NUM_ADMISSIONS + 1):
        p_id = random.randint(1, NUM_PATIENTS)
        doc_id = random.randint(1, NUM_PHYSICIANS)
        nurse_id = random.randint(1, NUM_NURSES)

        admit_date = safe_random_date_in_past(300)
        los_days = random.randint(1, 14)
        discharge_date = admit_date + timedelta(days=los_days)
        if discharge_date > NOW:
            discharge_date = NOW - timedelta(hours=1)

        admit_str = fmt(admit_date)
        discharge_str = fmt(discharge_date)

        admission_discharge[a_id] = discharge_date

        died_during_stay = random.random() < 0.05
        admission_alive[a_id] = not died_during_stay
        current_condition = "Deceased" if died_during_stay else "Stable"

        sql.append(
            f"INSERT INTO admission (admission_id, patient_id, admission_date_time, discharge_date_time, "
            f"admission_type, admission_source, reason_admission, insurance_information, current_condition, "
            f"admitting_professional_id) "
            f"VALUES ({a_id}, {p_id}, {sql_str(admit_str)}, {sql_str(discharge_str)}, "
            f"{sql_str(random.choice(['Emergency', 'Urgent', 'Elective']))}, 'Emergency Room', "
            f"'Chest Pain/Discomfort', 'Private Insurance', {sql_str(current_condition)}, {doc_id});\n"
        )

        # ----- Triage -----
        sql.append(
            f"INSERT INTO triage_assessment (triage_id, admission_id, nurse_id, blood_pressure, heart_rate, "
            f"respiratory_rate, body_temperature, oxygen_saturation, pain_level, reported_symptoms, "
            f"known_allergies, current_medications, triage_priority_level) "
            f"VALUES ({triage_id}, {a_id}, {nurse_id}, '130/85', {random.randint(60, 110)}, 18, 37.2, "
            f"{random.randint(92, 100)}, {random.randint(0, 10)}, 'Severe fatigue and discomfort', "
            f"{sql_str(random.choice(ALLERGIES))}, {sql_str(random.choice(MEDS))}, "
            f"{sql_str(random.choice(['High-Priority Emergency', 'Routine']))});\n"
        )
        triage_id += 1

        # ----- Diagnosis -----
        primary_code = random.choice(ICD9_POOL)[0]
        sql.append(
            f"INSERT INTO diagnosis (diagnosis_id, patient_id, admission_id, icd9_code, diagnosis_date_time, "
            f"primary_diagnosis, secondary_diagnosis, diagnosing_physician_id) "
            f"VALUES ({diag_id}, {p_id}, {a_id}, {sql_str(primary_code)}, {sql_str(admit_str)}, TRUE, FALSE, {doc_id});\n"
        )
        diag_id += 1

        if random.choice([True, False]):
            sec_code = random.choice(ICD9_POOL)[0]
            if sec_code != primary_code:
                sql.append(
                    f"INSERT INTO diagnosis (diagnosis_id, patient_id, admission_id, icd9_code, diagnosis_date_time, "
                    f"primary_diagnosis, secondary_diagnosis, diagnosing_physician_id) "
                    f"VALUES ({diag_id}, {p_id}, {a_id}, {sql_str(sec_code)}, {sql_str(admit_str)}, FALSE, TRUE, {doc_id});\n"
                )
                diag_id += 1

        # ----- ICU stay (clamped) -----
        if random.choice([True, False]):
            entry_time = admit_date + timedelta(hours=2)
            max_exit = discharge_date - timedelta(hours=1)
            if entry_time < max_exit:
                stay_hours = random.randint(6, max(6, int((max_exit - entry_time).total_seconds() // 3600)))
                exit_time = entry_time + timedelta(hours=stay_hours)
                if exit_time > max_exit:
                    exit_time = max_exit
                sql.append(
                    f"INSERT INTO icu_stay (unit_stay_id, admission_id, responsible_physician_id, unit_type, "
                    f"room_number, bed_number, entry_date_time, exit_date_time, reason_transfer) "
                    f"VALUES ({stay_id}, {a_id}, {doc_id}, {sql_str(random.choice(UNIT_TYPES))}, 'Room B', 'Bed 4', "
                    f"{sql_str(fmt(entry_time))}, {sql_str(fmt(exit_time))}, 'Continuous Monitoring Required');\n"
                )
                stay_id += 1

        # ----- Clinical note -----
        sql.append(
            f"INSERT INTO clinical_note (note_id, admission_id, physician_id, type, creation_date, patient_symptoms, "
            f"physical_examination, initial_clinical_findings, suspected_condition, planned_diagnostic_examinations, "
            f"initial_treatment) "
            f"VALUES ({note_id}, {a_id}, {doc_id}, 'Progress Note', {sql_str(admit_str)}, "
            f"'Patient shows clear signs of improvement following initial recovery procedures.', "
            f"'Vitals stable, alert and oriented.', "
            f"'Mild discomfort on palpation.', "
            f"'Acute coronary syndrome suspected.', "
            f"'ECG and chest imaging ordered.', "
            f"'Oxygen therapy administered.');\n"
        )
        note_id += 1

        # ----- Diagnostic order + radiology -----
        if random.choice([True, False]):
            sql.append(
                f"INSERT INTO diagnostic_order (order_id, admission_id, patient_id, requesting_physician_id, "
                f"requested_examination, request_date_time, clinical_reason_examination, priority, order_status) "
                f"VALUES ({order_id}, {a_id}, {p_id}, {doc_id}, 'Chest Imaging', {sql_str(admit_str)}, "
                f"'Rule out pulmonary embolism.', {sql_str(random.choice(PRIORITIES))}, 'Completed');\n"
            )
            sql.append(
                f"INSERT INTO radiology_examination (examination_id, order_id, examination_type, examination_date_time, "
                f"body_area_examined, referring_physician_id, radiology_technician, examination_status, medical_images) "
                f"VALUES ({exam_id}, {order_id}, {sql_str(random.choice(EXAM_TYPES))}, {sql_str(admit_str)}, 'Chest', "
                f"{doc_id}, {sql_str(random.choice(TECHNICIANS))}, 'Finalized', 'DICOM-{exam_id:04d}');\n"
            )
            sql.append(
                f"INSERT INTO radiology_report (radiology_report_id, radiologist_findings, interpretation, clinical_conclusion) "
                f"VALUES ({exam_id}, 'Lungs appear clear.', 'No major effusion detected.', 'Normal structural limits.');\n"
            )
            order_id += 1
            exam_id += 1

        # ----- Surgical procedure (NEW) -----
        # Only perform surgery if the patient is alive at discharge and the stay is long enough
        # for a recovery window. Procedure timestamp = admission + a few hours, clamped to
        # before discharge. Surgeon = admitting physician (simplification) OR a random one.
        has_surgery = (
            not died_during_stay
            and los_days >= 1
            and random.random() < SURGERY_PROBABILITY
        )
        if has_surgery:
            procedure_name, body_site = random.choice(SURGICAL_PROCEDURES)
            # Procedure happens between 2h and (LOS - 2h) after admission
            earliest = admit_date + timedelta(hours=2)
            latest = discharge_date - timedelta(hours=2)
            if latest <= earliest:
                latest = earliest + timedelta(minutes=30)
            offset_seconds = random.randint(0, int((latest - earliest).total_seconds()))
            procedure_dt = earliest + timedelta(seconds=offset_seconds)
            # Surgeon: use admitting physician (must exist). Could also pick a random one.
            surgeon_id = doc_id

            sql.append(
                f"INSERT INTO surgical_procedure (procedure_id, admission_id, patient_id, procedure_name, "
                f"body_site, procedure_date_time, surgeon_id) "
                f"VALUES ({procedure_id}, {a_id}, {p_id}, {sql_str(procedure_name)}, {sql_str(body_site)}, "
                f"{sql_str(fmt(procedure_dt))}, {surgeon_id});\n"
            )
            procedure_id += 1

        # ----- Discharge record -----
        if died_during_stay:
            discharge_destination = "Mortuary"
            condition = "Deceased"
            discharge_status = "Deceased"
            followup_instr = "N/A"
            followup_appts = "N/A"
        else:
            discharge_destination = random.choice(DISCHARGE_DESTINATIONS)
            condition = random.choice(["Fully Recovered", "Stable", "Improved"])
            discharge_status = "Discharged"
            followup_instr = "Follow up with primary care in 2 weeks."
            followup_appts = (discharge_date + timedelta(days=14)).strftime("%Y-%m-%d")

        sql.append(
            f"INSERT INTO discharge_record (discharge_record_id, admission_id, discharge_date_time, discharge_destination, "
            f"condition_at_discharge, discharge_status, followup_instructions, followup_appointments, responsible_physician) "
            f"VALUES ({discharge_id}, {a_id}, {sql_str(discharge_str)}, {sql_str(discharge_destination)}, "
            f"{sql_str(condition)}, {sql_str(discharge_status)}, {sql_str(followup_instr)}, {sql_str(followup_appts)}, {doc_id});\n"
        )
        discharge_id += 1

    # 6. Update patient life_status from discharge records
    sql.append("\n-- 6. Update patients who died during an admission\n")
    sql.append(
        "UPDATE patient SET life_status = 'Deceased'\n"
        "WHERE patient_id IN (\n"
        "    SELECT a.patient_id FROM admission a\n"
        "    JOIN discharge_record d ON d.admission_id = a.admission_id\n"
        "    WHERE d.discharge_status = 'Deceased'\n"
        ");\n"
    )

    sql.append("\nCOMMIT;\n")

    with open(filename, "w") as f:
        f.writelines(sql)
    print(f"File successfully created: '{filename}'")


if __name__ == "__main__":
    generate_postgres_script()