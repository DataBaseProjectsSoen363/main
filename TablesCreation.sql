BEGIN;

-- 1. ICD-9 Dictionary
CREATE TABLE icd9_dict (
    icd9_code VARCHAR(10) PRIMARY KEY,
    official_diagnosis_title VARCHAR(255) NOT NULL,
    description TEXT,
    disease_category VARCHAR(150)
);

-- 2. Physicians
CREATE TABLE physician (
    physician_ID INT PRIMARY KEY,
    name VARCHAR(50),
    specialty VARCHAR(100)
);

-- 3. Nurses
CREATE TABLE nurse (
    nurse_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- 4. Patients
CREATE TABLE patient (
    patient_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    health_insurance_number VARCHAR(50),
    life_status VARCHAR(50),
    address VARCHAR(255),
    date_birth DATE,
    gender VARCHAR(20),
    emergency_contact_number VARCHAR(50),
    phone_number VARCHAR(50)
);

-- 5. Admissions
CREATE TABLE admission (
    admission_id INT PRIMARY KEY,
    patient_id INT REFERENCES patient(patient_id),
    admission_date_time TIMESTAMP NOT NULL,
    discharge_date_time TIMESTAMP,
    admission_type VARCHAR(50),
    admission_source VARCHAR(100),
    reason_admission TEXT,
    insurance_information VARCHAR(100),
    current_condition TEXT,
    admitting_professional_id INT REFERENCES Physicians(physician_id)
);

-- 6. Triage Assessment
CREATE TABLE triage_assessment (
    triage_id INT PRIMARY KEY,
    admission_id INT REFERENCES admission(admission_id),
    nurse_id INT REFERENCES nurse(nurse_id),
    blood_pressure VARCHAR(20),
    heart_rate INT,
    respiratory_rate INT,
    body_temperature NUMERIC(4,2),
    oxygen_saturation INT,
    pain_level INT,
    reported_symptoms TEXT,
    known_allergies TEXT,
    current_medications TEXT,
    triage_priority_level VARCHAR(50)
);

-- 7. Diagnosis
CREATE TABLE diagnosis (
    diagnosis_id INT PRIMARY KEY,
    patient_id INT REFERENCES patient(patient_id),
    admission_id INT REFERENCES admission(admission_id),
    icd9_code VARCHAR(10) REFERENCES icd9_dict(icd9_code),
    diagnosis_date_time TIMESTAMP NOT NULL,
    primary_diagnosis BOOLEAN DEFAULT FALSE,
    secondary_diagnosis BOOLEAN DEFAULT FALSE,
    diagnosing_physician_id INT REFERENCES Physicians(physician_id)
);

-- 8. ICU / CCU Stay
CREATE TABLE icu_stay (
    unit_stay_id INT PRIMARY KEY,
    admission_id INT REFERENCES admission(admission_id),
    responsible_physician_id INT REFERENCES Physicians(physician_id),
    unit_type VARCHAR(50) NOT NULL,
    room_number VARCHAR(20),
    bed_number VARCHAR(20),
    entry_date_time TIMESTAMP NOT NULL,
    exit_date_time TIMESTAMP,
    reason_transfer TEXT
);

-- 9. Clinical Notes
CREATE TABLE clinical_note (
    note_id INT PRIMARY KEY,
    admission_id INT REFERENCES admission(admission_id),
    physician_id INT REFERENCES Physicians(physician_id),
    type VARCHAR(50),
    creation_date TIMESTAMP NOT NULL,
    patient_symptoms TEXT,
    physical_examination TEXT,
    initial_clinical_findings TEXT,
    suspected_condition TEXT,
    planned_diagnostic_examinations TEXT,
    initial_treatment TEXT
);

-- 10. Diagnostic Orders
CREATE TABLE diagnostic_order (
    order_id INT PRIMARY KEY,
    admission_id INT REFERENCES admission(admission_id),
    patient_id INT REFERENCES patient(patient_id),
    requesting_physician_id INT REFERENCES Physicians(physician_id),
    requested_examination VARCHAR(150),
    request_date_time TIMESTAMP,
    clinical_reason_examination TEXT,
    priority VARCHAR(50),
    order_status VARCHAR(50)
);

-- 11. Radiology Examination
CREATE TABLE radiology_examination (
    examination_id INT PRIMARY KEY,
    order_id INT REFERENCES diagnostic_order(order_id),
    examination_type VARCHAR(100),
    examination_date_time TIMESTAMP,
    body_area_examined VARCHAR(100),
    referring_physician_id INT REFERENCES Physicians(physician_id),
    radiology_technician VARCHAR(100),
    examination_status VARCHAR(50),
    medical_images TEXT
);

-- 12. Radiology Report (1:1 with Radiology Examination)
CREATE TABLE radiology_report (
    radiology_report_id INT PRIMARY KEY REFERENCES radiology_examination(examination_id),
    radiologist_findings TEXT,
    interpretation TEXT,
    clinical_conclusion TEXT
);

-- 13. Discharge Record 
CREATE TABLE discharge_record (
    discharge_record_id INT PRIMARY KEY,
    admission_id INT UNIQUE REFERENCES admission(admission_id),
    discharge_date_time TIMESTAMP NOT NULL,
    discharge_destination VARCHAR(150),
    condition_at_discharge TEXT,
    discharge_status VARCHAR(20) NOT NULL DEFAULT 'Discharged',
    followup_instructions TEXT,
    followup_appointments TEXT,
    responsible_physician INT REFERENCES Physicians(physician_id)
);

-- 14. Surgical Procedure 
CREATE TABLE surgical_procedure (
    procedure_id INT PRIMARY KEY,
    admission_id INT REFERENCES admission(admission_id),
    patient_id INT REFERENCES patient(patient_id),
    procedure_name VARCHAR(150) NOT NULL,
    body_site VARCHAR(100),
    procedure_date_time TIMESTAMP NOT NULL,
    surgeon_id INT REFERENCES Physicians(physician_id)
);

COMMIT;

