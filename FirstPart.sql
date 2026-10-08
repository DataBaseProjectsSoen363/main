-- =====================================================================
-- Task 3: Writing the Queries
-- File: FirstPart.sql
-- =====================================================================
-- ---------------------------------------------------------------------
-- Instructions:
-- 1. Find the block assigned to your handle below.
-- 2. Run each query in pgAdmin to confirm it executes.
-- 3. Screenshot of the Data Output grid captured
-- 4. Screenshot pasted into the shared Word document
-- 5. Comment under the screenshot explaining what the query does
--    and what the result shows (2-4 sentences)
-- 6. Commit this file when done.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1 - 4   |   @Zitkq
-- ---------------------------------------------------------------------

-- Q1


-- Q2


-- Q3


-- Q4


-- ---------------------------------------------------------------------
-- 5 - 8   |   @JuanMa_487
-- ---------------------------------------------------------------------

-- Q5


-- Q6


-- Q7


-- Q8


-- ---------------------------------------------------------------------
-- 9 - 12   |   @Mohammad
-- ---------------------------------------------------------------------

-- Q9


-- Q10


-- Q11


-- Q12


-- ---------------------------------------------------------------------
-- 13 - 16   |   @Laurent
-- ---------------------------------------------------------------------

-- Q13


-- Q14


-- Q15


-- Q16


-- ---------------------------------------------------------------------
-- 17 - 20   |   @fmvemba
-- ---------------------------------------------------------------------

-- Q17: Find all admissions during which the patient received more than one distinct ICD-
--      9 diagnosis. Display the patient name, admission identifier, and number of distinct
--      ICD-9 codes.
    SELECT patient.name,
		   admission.admission_id,
		   COUNT(DISTINCT diagnosis.icd9_code) AS num_distinct_diagnoses
    FROM patient
	JOIN admission USING(patient_id)
	JOIN diagnosis USING(admission_id)
	GROUP BY patient.name, admission.admission_id
	HAVING COUNT(DISTINCT diagnosis.icd9_code) > 1;

	SELECT * FROM clinical_note;

-- Q18: Retrieve the latest clinical note for each patient. Display the patient name, note
-- type, note creation date and time, and note contents
	SELECT patient.name,clinical_note.type,clinical_note.creation_date,clinical_note.patient_symptoms
	FROM patient
	JOIN admission on admission.patient_id = patient.patient_id
	JOIN clinical_note ON admission.admission_id = clinical_note.admission_id
	
-- Q19: List all admissions where the patient’s discharge status or discharge condition indicates
-- that the patient died during the hospital stay. Display the patient name, admission
-- date, recorded date of death, and associated primary ICD-9 diagnosis.
SELECT
    p.name ,                                 
    a.admission_id,
    d.discharge_date_time,              
    dg.icd9_code                    
FROM admission a
JOIN patient           p  ON p.patient_id       = a.patient_id
JOIN discharge_record  d  ON d.admission_id     = a.admission_id
LEFT JOIN diagnosis    dg ON dg.admission_id    = a.admission_id
                          AND dg.primary_diagnosis = TRUE
WHERE d.condition_at_discharge = 'Deceased'
ORDER BY d.discharge_date_time;

-- Q20: Find all patients who underwent a surgical procedure and a radiology examination
-- on the same calendar day during the same admission. Display the patient
-- name, admission identifier, procedure type, radiology examination type, and the common
-- date.
SELECT
	patient.name,
	admission.admission_id,
	surgical_procedure.procedure_name,
	radiology_examination.examination_type,
	DATE(surgical_procedure.procedure_date_time) AS common_date
FROM patient
JOIN admission 			   ON admission.patient_id = patient.patient_id
JOIN surgical_procedure    ON admission.admission_id = surgical_procedure.admission_id
JOIN diagnostic_order      ON diagnostic_order.admission_id = admission.admission_id
JOIN radiology_examination ON radiology_examination.order_id = diagnostic_order.order_id
WHERE DATE(surgical_procedure.procedure_date_time) = DATE(radiology_examination.examination_date_time)
ORDER BY common_date,patient.name;

-- Show all surgery dates and exam dates per admission, side by side
SELECT
    a.admission_id,
    DATE(sp.procedure_date_time)      AS surgery_date,
    DATE(re.examination_date_time)    AS exam_date,
    (DATE(sp.procedure_date_time) = DATE(re.examination_date_time)) AS same_day
FROM admission a
JOIN surgical_procedure  sp ON sp.admission_id = a.admission_id
JOIN diagnostic_order    o  ON o.admission_id  = a.admission_id
JOIN radiology_examination re ON re.order_id   = o.order_id
ORDER BY a.admission_id;
	



