from odoo import models, api, _
from datetime import datetime


class EmergencyCaseStudy(models.AbstractModel):
    _name = 'report.dzc_1.emergency_form_report'

    @api.model
    def get_report_values(self, docids, data):
        docs = self.env['emergency.and.urgent.cases'].search([('id', '=', data['emergency'])])
        date = datetime.strftime(datetime.today(), '%d-%m-%Y')
        famliy_no = 0
        for member in docs.partnrt_id.family_ids:
            famliy_no += 1
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'emergency.and.urgent.cases',
            'docs': docs,
            'famliy_no': famliy_no,
            'date': date,

                    }
        return docargs


class ZakatApplicationForm(models.AbstractModel):
    _name = 'report.dzc_1.certificate_of_entitlement_report'

    @api.model
    def get_report_values(self, docids, data):
        docs = self.env['zakat.aplication.form'].search([('id', '=', data['dzc1'])])
        date = datetime.strftime(datetime.today(), '%d-%m-%Y')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'zakat.aplication.form',
            'docs': docs,
            'date': date,

                    }
        return docargs

class FederalTreatmentReport(models.AbstractModel):
    _name = 'report.dzc_1.guarantee_letter_report'

    @api.model
    def get_report_values(self, docids, data):
        docs = self.env['zkate.federaltreatment'].search([('id', '=', data['treatment'])])
        date = datetime.strftime(datetime.today(), '%Y-%m-%d')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'zkate.federaltreatment',
            'docs': docs,
            'date': date,

                    }
        return docargs

class FederalTreatmentReport(models.AbstractModel):
    _name = 'report.dzc_1.english_guarantee_letter_report'

    @api.model
    def get_report_values(self, docids, data):
        treatment_record = self.env['zkate.federaltreatment'].search([('id', '=', data['treatment'])])
        m_dir=''
        date = datetime.strftime(datetime.today(), '%Y-%m-%d')
        for record in treatment_record[0].hospital_id.staff_ids:
            if record.title == 'medical':
               m_dir=record.name
        docs={'d_name':m_dir,'hospital':treatment_record[0].hospital_id.name,'country':treatment_record[0].hospital_id.location_name,'name':treatment_record[0].partner_id.e_name,'total_cost':treatment_record[0].total_cost,'z_cost':treatment_record[0].zakat_support,'p_cost':treatment_record[0].total_cost *0.85 - treatment_record[0].zakat_support ,'p_no':treatment_record[0].passport_no,'actual_cost':treatment_record[0].total_cost * 0.15,'date': datetime.today().strftime('%Y-%m-%d'), 'ref':treatment_record[0].code}
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'zkate.federaltreatment',
            'docs': docs,
            'date': date,

                    }
        return docargs


class FollowFormReport(models.AbstractModel):
    _name = 'report.dzc_1.follow_form_report'

    @api.model
    def get_report_values(self, docids, data):
        docs = self.env['zkate.federaltreatment'].search([('id', '=', data['treatment'])])
        date = datetime.strftime(datetime.today(), '%Y-%m-%d')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'zkate.federaltreatment',
            'docs': docs,
            'date': date,

                    }
        return docargs


class AbroadTreatment(models.AbstractModel):
    _name = 'report.dzc_1.abroad_treatment_report'

    @api.model
    def get_report_values(self, docids, data):
        docs = self.env['zkate.federaltreatment'].search([('id', '=', data['treatment'])])
        date = datetime.strftime(datetime.today(), '%Y-%m-%d')
        year = datetime.today().year
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'zkate.federaltreatment',
            'docs': docs,
            'date': date,
            'year': year,

        }
        return docargs


class TreatmentPayment(models.AbstractModel):
    _name = 'report.dzc_1.treatment_payment_report'

    @api.model
    def get_report_values(self, docids, data):
        docs = self.env['zakat.treatmentpayment'].search([('id', 'in', docids)])
        date = datetime.strftime(datetime.today(), '%Y-%m-%d')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'zakat.treatmentpayment',
            'docs': docs,
            'date': date,

                    }
        return docargs
        
class UrgentCasesPayment(models.AbstractModel):
    _name = 'report.dzc_1.urgent_cases_payment_report'
    report_values = []

    @api.model
    def get_report_values(self, docids, data):
        docs = self.env['urgent.cases.payments'].search([('id', 'in', docids)])
        date = docs.committe_date
        age =   0
        index = 0
        address = ''
        report_values = []
        
        for case in docs.cases_ids:
            index += 1
            age =   datetime.strptime(docs.order_date,"%Y-%m-%d").year - datetime.strptime(case.partnrt_id.birth_date,"%Y-%m-%d").year
            address  = case.partnrt_id.city+ '/' + case.partnrt_id.faqeer_id.Village
            report_values.append({'index' : index , 'name': case.partnrt_id.name , 'age' : age , 'address' : address ,'social' : case.partnrt_id.social_status, 'amount':case.amount ,'type':case.case_classification.name })
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'urgent.cases.payments',
            'docs': report_values,
            'date': date,
            'record' :docs,
            'cases_num' : index
            

                    }
        return docargs



########### Organizations support #################
class Dzc1OrganizationsReport(models.AbstractModel):
    _name = 'report.dzc_1.organization_support_report'

    @api.model
    def get_report_values(self, docids, data):
        docs = self.env['support.order'].search([('id', 'in', docids)])
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'support.order',
            'docs': docs,

                    }
        return docargs

#################### Sergury Fees ####################
class SerguryFeesReport(models.AbstractModel):
    _name = 'report.dzc_1.sergury_fees_list_report'

    @api.model
    def get_report_values(self, docids, data):
        docs = self.env['zkate.federaltreatment'].search([('id', '=', data['treatment'])])

        ill = docs.illness_id.id
        ill_name = docs.illness_id.name
        ser_fee = []
        all_data = []
        index = 0

        fees = self.env['hospital.treatment'].search(['&',('op_fees_ids.illness_id.id', '=', ill),('contract','=','TRUE') , ('state' ,'=','approve')])
        
        for rec in fees:
            index += 1
            discount = rec.op_fees_ids.discount
            fee = (rec.op_fees_ids.operation_fees  - rec.op_fees_ids.operation_fees  * rec.op_fees_ids.discount / 100)  
            
            ser_fee.append({'index': index ,'hospital_name' : rec.name ,'discount':discount , 'total_f':rec.op_fees_ids.operation_fees, 'fees':fee})

        all_data.append({'ser_fee': ser_fee , 'ill': ill_name })
       
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'zkate.federaltreatment',
            'docs': all_data,

                    }
        return docargs
