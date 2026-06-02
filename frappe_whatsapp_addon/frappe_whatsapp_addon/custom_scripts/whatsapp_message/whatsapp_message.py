import frappe
import frappe.utils

def after_insert(doc, method):
	if doc.type == 'Incoming':
		phone_number = doc.get('from')
		patient = get_patient_from_number(phone_number)
		message_txt = doc.message
		if 'book' in message_txt.lower():
			create_patient_appointment(doc, patient)
		if 'cancel' in message_txt.lower():
			cancel_patient_appointment(doc, patient)

def create_patient_appointment(doc, patient):
	healthcare_practitioner = frappe.db.get_single_value('Frappe Health Config', 'healthcare_practitioner')
	appointment_type = frappe.db.get_single_value('Frappe Health Config', 'appointment_type')
	if healthcare_practitioner:
		appointment = frappe.get_doc({
			'doctype': 'Patient Appointment',
			'patient': patient,
			'practitioner': healthcare_practitioner,
			'status': 'Scheduled',
			'appointment_date': frappe.utils.add_days(frappe.utils.nowdate(), 1),
			'appointment_time': '11:00',
			'appointment_type': appointment_type,
			'appointment_for': 'Practitioner'
		})
		appointment.flags.ingore_mandatory = True
		appointment.insert(ignore_permissions=True)

def cancel_patient_appointment(doc, patient):
	patient_appointments = frappe.get_all('Patient Appointment', filters={'patient': patient, 'status': 'Scheduled'}, fields=['name'])
	for appointment in patient_appointments:
		frappe.db.set_value('Patient Appointment', appointment.name, 'status', 'Cancelled')

def get_patient_from_number(phone_number):
	deafault_patient = frappe.db.get_single_value('Frappe Health Config', 'patient')
	patient = frappe.get_all('Patient', filters={'mobile': phone_number}, fields=['name'])
	if patient:
		return patient[0].name
	if deafault_patient:
		return deafault_patient
	return None
