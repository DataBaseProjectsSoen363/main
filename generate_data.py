import random
from datetime import datetime, timedelta

# ---- CONFIGURATION ----
NUM_PHYSICIANS = 15
NUM_NURSES = 10
NUM_PATIENTS = 40
NUM_ADMISSIONS = 50

# Pool elements to generate realistic fields
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

def generate_postgres_script(filename="populate_all_hospital.sql"):
    sql = ["-- Complete PostgreSQL Population Script\n", "BEGIN;\n\n"]
    
    # 1. POPULATE ICD-9 DICTIONARY
    sql.append("-- 1. ICD-9 Dictionary\n")
    for code, title, desc, cat in ICD9_POOL:
        sql.append(f"INSERT INTO icd9_dict (icd9_code, official_diagnosis_title, description, disease_category) VALUES ('{code}', '{title}', '{desc}', '{cat}');\n")
        
    # 2. POPULATE PHYSICIANS
    sql.append("\n-- 2. Physicians\n")
    for p_id in range(1, NUM_PHYSICIANS + 1):
        name = f"Dr. {random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        sql.append(f"INSERT INTO physician (physician_id, name) VALUES ({p_id}, '{name}');\n")

    # 3. POPULATE NURSES
    sql.append("\n-- 3. Nurses\n")
    for n_id in range(1, NUM_NURSES + 1):
        name = f"Nurse {random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        sql.append(f"INSERT INTO nurse (nurse_id, name) VALUES ({n_id}, '{name}');\n")

    # 4. POPULATE PATIENTS
    sql.append("\n-- 4. Patients\n")
    for p_id in range(1, NUM_PATIENTS + 1):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        hin = f"RAMQ{random.randint(100000, 999999)}"
        status = random.choice(["Alive", "Alive", "Alive", "Deceased"])
        addr = f"{random.randint(100, 5000)} {random.choice(STREETS)}, {random.choice(CITIES)}"
        dob = (datetime.now() - timedelta(days=random.randint(6500, 30000))).strftime('%Y-%m-%d')
        gender = random.choice(["Male", "Female"])
        phone = f"514-555-{random.randint(1000, 9999)}"
        sql.append(f"INSERT INTO patient (patient_id, name, health_insurance_number, life_status, address, date_birth, gender, emergency_contact_number, phone_number) VALUES ({p_id}, '{name}', '{hin}', '{status}', '{addr}', '{dob}', '{gender}', '{phone}', '{phone}');\n")

    # 5. POPULATE ADMISSIONS, TRIAGE, AND DOWNSTREAM ENTITIES
    sql.append("\n-- 5. Admissions and Dependent Systems\n")
    
    order_id = 1
    exam_id = 1
    note_id = 1
    stay_id = 1
    diag_id = 1

    for a_id in range(1, NUM_ADMISSIONS + 1):
        p_id = random.randint(1, NUM_PATIENTS)
        doc_id = random.randint(1, NUM_PHYSICIANS)
        nurse_id = random.randint(1, NUM_NURSES)
        
        admit_date = datetime.now() - timedelta(days=random.randint(5, 300))
        discharge_date = admit_date + timedelta(days=random.randint(1, 14))
        
        admit_str = admit_date.strftime('%Y-%m-%d %H:%M:%S')
        discharge_str = discharge_date.strftime('%Y-%m-%d %H:%M:%S')

        # Generate Admission
        sql.append(
            f"INSERT INTO admission (admission_id, patient_id, admission_date_time, discharge_date_time, admission_type, admission_source, reason_admission, insurance_information, current_condition, admitting_professional_id) "
            f"VALUES ({a_id}, {p_id}, '{admit_str}', '{discharge_str}', '{random.choice(['Emergency', 'Urgent', 'Elective'])}', 'Emergency Room', 'Chest Pain/Discomfort', 'Private Insurance', 'Stable', {doc_id});\n"
        )
        
        # Generate Triage Assessment
        sql.append(
            f"INSERT INTO triage_assessment (triage_id, admission_id, nurse_id, blood_pressure, heart_rate, respiratory_rate, body_temperature, oxygen_saturation, pain_level, reported_symptoms, triage_priority_level) "
            f"VALUES ({a_id}, {a_id}, {nurse_id}, '130/85', {random.randint(60, 110)}, 18, 37.2, {random.randint(92, 100)}, 7, 'Severe fatigue and discomfort', '{random.choice(['High-Priority Emergency', 'Routine'])}');\n"
        )
        
        # Generate Diagnosis (At least Primary)
        primary_code = random.choice(ICD9_POOL)[0]
        sql.append(
            f"INSERT INTO diagnosis (diagnosis_id, patient_id, admission_id, icd9_code, diagnosis_date_time, primary_diagnosis, secondary_diagnosis, diagnosing_physician_id) "
            f"VALUES ({diag_id}, {p_id}, {a_id}, '{primary_code}', '{admit_str}', TRUE, FALSE, {doc_id});\n"
        )
        diag_id += 1

        # Optionally add a secondary diagnosis
        if random.choice([True, False]):
            sec_code = random.choice(ICD9_POOL)[0]
            if sec_code != primary_code:
                sql.append(
                    f"INSERT INTO diagnosis (diagnosis_id, patient_id, admission_id, icd9_code, diagnosis_date_time, primary_diagnosis, secondary_diagnosis, diagnosing_physician_id) "
                    f"VALUES ({diag_id}, {p_id}, {a_id}, '{sec_code}', '{admit_str}', FALSE, TRUE, {doc_id});\n"
                )
                diag_id += 1

        # Generate ICU/CCU Stays
        if random.choice([True, False]):
            entry_time = admit_date + timedelta(hours=2)
            exit_time = entry_time + timedelta(days=random.randint(1, 8))
            sql.append(
                f"INSERT INTO icu_stay (unit_stay_id, admission_id, responsible_physician_id, unit_type, room_number, bed_number, entry_date_time, exit_date_time, reason_transfer) "
                f"VALUES ({stay_id}, {a_id}, {doc_id}, '{random.choice(UNIT_TYPES)}', 'Room B', 'Bed 4', '{entry_time.strftime('%Y-%m-%d %H:%M:%S')}', '{exit_time.strftime('%Y-%m-%d %H:%M:%S')}', 'Continuous Monitoring Required');\n"
            )
            stay_id += 1

        # Generate Clinical Notes
        sql.append(
            f"INSERT INTO clinical_note (note_id, admission_id, physician_id, type, creation_date, patient_symptoms, initial_treatment) "
            f"VALUES ({note_id}, {a_id}, {doc_id}, 'Progress Note', '{admit_str}', 'Patient shows clear signs of improvement following initial recovery procedures.', 'Oxygen therapy administered.');\n"
        )
        note_id += 1

        # Generate Diagnostic Orders and Radiology Records
        if random.choice([True, False]):
            sql.append(
                f"INSERT INTO diagnostic_order (order_id, admission_id, patient_id, requesting_physician_id, requested_examination, request_date_time, order_status) "
                f"VALUES ({order_id}, {a_id}, {p_id}, {doc_id}, 'Chest Imaging', '{admit_str}', 'Completed');\n"
            )
            
            sql.append(
                f"INSERT INTO radiology_examination (examination_id, order_id, examination_type, examination_date_time, body_area_examined, referring_physician_id, examination_status) "
                f"VALUES ({exam_id}, {order_id}, '{random.choice(EXAM_TYPES)}', '{admit_str}', 'Chest', {doc_id}, 'Finalized');\n"
            )
            
            sql.append(
                f"INSERT INTO radiology_report (radiology_report_id, radiologist_findings, interpretation, clinical_conclusion) "
                f"VALUES ({exam_id}, 'Lungs appear clear.', 'No major effusion detected.', 'Normal structural limits.');\n"
            )
            order_id += 1
            exam_id += 1

        # Generate Discharge Records
        sql.append(
            f"INSERT INTO discharge_record (discharge_record_id, admission_id, discharge_date_time, discharge_destination, condition_at_discharge, responsible_physician) "
            f"VALUES ({a_id}, {a_id}, '{discharge_str}', 'Home', 'Fully Recovered', {doc_id});\n"
        )

    sql.append("\nCOMMIT;\n")
    
    with open(filename, "w") as file:
        file.writelines(sql)
    print(f"File successfully created: '{filename}'")

if __name__ == "__main__":
    generate_postgres_script()

