#!/usr/bin/env python
# -*- coding: utf-8 -*-

from odoo import api, models, fields,exceptions , _
from datetime import datetime
from umalqurra.hijri_date import HijriDate
from odoo.addons.account_check_printing_custom.models import amount_to_text_ar

class ContractPrint(models.TransientModel):
    _name = 'contract.print.wiz'

    @api.multi
    @api.onchange('order_id')
    def on_change_order(self):
        """
        Get the benaficiary that belong to an order
        :return: ids
        """
        ids = []
        project_ids = []
        if self.order_id:
            order = self.env['finance.order'].search([('id', '=', self.order_id.id)])
            for a in order.approve_ids:
                project_ids.append(a.project_id.id)
                for payment in a.payment_ids:
                    if payment.type in ['check', 'cash']:
                        for payed in payment:
                            ids.append(payed.id)
        self.benaficiary_id = False
        self.project_id = False
        for benaficiary in ids:
            self.benaficiary_id = benaficiary
            break
        if self.benaficiary_id:
            for project in project_ids:
                self.project_id = project
                break
        return {'domain': {
            'benaficiary_id': [('id', 'in', ids)],
            'project_id': [('id', 'in', project_ids)]}}

    @api.multi
    @api.onchange('contract_type')
    def ordre_domain(self):
        customer_data = []
        ids = []
        if self.contract_type in ['purchase_contract', 'receiving_product', 'murabaha_purchase', 'a_r_s_v']:
            approval_ids = self.env['finance.approval'].search([('formula_clone', 'in', ['murabaha', 'buying_murabaha'])],order="id desc",limit=300)
            for approval in approval_ids:
                if approval.visit_id.order_id.id not in customer_data:
                    customer_data.append(approval.visit_id.order_id.id)
            order_ids = self.env['finance.order'].search([('id', 'in', customer_data)])
            for order in order_ids:
                ids.append(order.id)
            return {'domain': {
                'order_id': [('id', 'in', ids)],
            }}

    @api.multi
    def get_manager(self):
        """
        get user that have a specific group only
        :return: doamin
        """
        ids = []
        for user in self.env['res.users'].search([('company_id', '=', self.env.user.company_id.id)]):
            for s in user.groups_id:
                if (s.name == 'General Manager' and s.category_id.name == "Financing") or \
                     (s.name == 'المدير العام'.decode('utf-8', 'ignore') and s.category_id.name == "التمويل".decode('utf-8', 'ignore')):
                    ids.append(user.id)
                elif (s.name == 'Operation Manager' and s.category_id.name == "Financing") or \
                        (s.name == 'مدير العمليات'.decode('utf-8', 'ignore') and s.category_id.name == "التمويل".decode('utf-8', 'ignore')):
                    ids.append(user.id)
                elif (s.name == 'Branch Manager' and s.category_id.name == "Financing") or\
                        (s.name == 'مدير الفرع'.decode('utf-8', 'ignore') and s.category_id.name == "التمويل".decode('utf-8', 'ignore')):
                    ids.append(user.id)
        return [('id', 'in', ids)]



    contract_type = fields.Selection([('purchase_contract', 'Purchase contract'),
                                      ('murabaha_purchase', 'Murabaha purchase contract'),
                                      ('receiving_product', 'Receiving Product'),
                                     ('a_r_s_v', 'Acknowledgment of receipt of sales value')], required=True)
    order_id = fields.Many2one('finance.order', string="Order", required=True)
    benaficiary_id = fields.Many2one('finance.approval.payment', string='Benaficiary', required=True)
    project_id = fields.Many2one('finance.project', string="Project", required=True)
    user_id = fields.Many2one('res.users', domain=get_manager, string='Signed By', required=True)
    amount = fields.Float(string="Amount", related="benaficiary_id.amount")
    date = fields.Date(string="Date", related="benaficiary_id.date")
    print_check_1 = fields.Boolean(related="benaficiary_id.print_check_1",string="Printed before")
    print_check_2 = fields.Boolean(related="benaficiary_id.print_check_2", string="Printed before")
    print_check_3 = fields.Boolean(related="benaficiary_id.print_check_3", string="Printed before")
    print_check_4 = fields.Boolean(related="benaficiary_id.print_check_4", string="Printed before")
    character = fields.Char(string="Character")
    first_witnesse = fields.Char(string="First witnesse", required=True)
    second_witnesse = fields.Char(string="Second witnesse", required=True)

    @api.multi
    def _onchange_user_id(self, user_id):
        chart = ' '
        if user_id:
            for user in self.env['res.users'].search([('id', '=', user_id)]):
                for s in user.groups_id:
                    if s.name == 'General Manager' or s.name == 'المدير العام'.decode('utf-8', 'ignore'):
                        chart = s.name
                    elif s.name == 'Operation Manager' or s.name == 'مدير العمليات'.decode('utf-8', 'ignore'):
                        chart = s.name
                    elif s.name == 'Branch Manager' or s.name == 'مدير الفرع'.decode('utf-8', 'ignore'):
                        chart = s.name
            return {'value': {'character': chart}}
        return {'value': {}}


    @api.multi
    def print_report(self):
        """
        Create Report
        :return:
        """
        if self.env.user.company_id.counsel == False and self.env.user.company_id.counsel_character == False:
            raise exceptions.ValidationError(_("Please Make sure you have a counsel to print your contract"))
        datas = {
            'ids': '',
            'model': '',
            'context': {
                'order_id': self.order_id.id,
                'benaficiary_id': self.benaficiary_id.name,
                'benaficiary': self.benaficiary_id.id,
                'date': self.date,
                'user_id': self.user_id.name,
                'project_id': self.project_id.name,
                'first_witnesse': self.first_witnesse,
                'second_witnesse': self.second_witnesse,
                'user': self.user_id.id,
            },}

        # Here To Check the Contract type and return the selected contract template
        if self.contract_type == 'purchase_contract':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'microfinance.purchase_contract_temp',
                'datas': datas,
            }

        elif self.contract_type == 'murabaha_purchase':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'microfinance.murabaha_purchase_contract_temp',
                'datas': datas,
            }
        elif self.contract_type == 'receiving_product':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'microfinance.receiving_product_temp',
                'datas': datas,
            }
        elif self.contract_type == 'a_r_s_v':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'microfinance.a_r_s_v_temp',
                'datas': datas,
            }


class PurchaseContract(models.AbstractModel):
    _name = 'report.microfinance.purchase_contract_temp'

    @api.model
    def render_html(self, docids, data):
        """
        :param data: Passed value form wizard
        :return: generating report
        """
        order_id = data['context']['order_id']
        benaficiary_id = data['context']['benaficiary']
        benaficiary = data['context']['benaficiary_id']
        project = data['context']['project_id']
        amount = 0
        date = data['context']['date']
        signed = data['context']['user_id']
        first = data['context']['first_witnesse']
        second = data['context']['second_witnesse']
        date_v = datetime.strptime(date, '%Y-%m-%d')
        hijri = HijriDate(date_v.year, date_v.month, date_v.day , gr=True)
        report = self.env['report']
        purchase_contract_report = report._get_report_from_name('microfinance.purchase_contract_temp')
        name = ""
        if date_v.month == 1:
            name = "يناير"
        elif date_v.month == 2:
            name = "فبراير"
        elif date_v.month == 3:
            name = "مارس"
        elif date_v.month == 4:
            name = "أبريل"
        elif date_v.month == 5:
            name = "مايو"
        elif date_v.month == 6:
            name = "يونيو"
        elif date_v.month == 7:
            name = "يوليو"
        elif date_v.month == 8:
            name = "أغسطس"
        elif date_v.month == 9:
            name = "سبتمبر"
        elif date_v.month == 10:
            name = "أوكتوبر"
        elif date_v.month == 11:
            name = "نوفمبر"
        elif date_v.month == 12:
            name = "ديسمبر"

        order_ids = self.env['finance.order'].search([('id', '=', order_id)])
        approve_id = []
        guarantee = []

        for approve in order_ids.visit_id.approve_ids:
            approve_id.append(approve.id)

        installment_ids = self.env['finance.installments'].search([('approval_id', 'in', approve_id),
                                                                   ('approval_id.formula', 'in',
                                                                    ['fixed_murabaha', 'dec_murabaha'])])
        ins_no = 0
        for installment in installment_ids:
            insurance_am = installment.approval_id.insurance_amount
            expens_am = installment.approval_id.expenses
            ins_no +=1
            amount = installment.amount_before_profit

        amount = (amount * ins_no)



        day_name = ['الأول', 'الثاني', 'الثالث', 'الرابع', 'الخامس', 'السادس', 'السابع', 'الثامن', 'التاسع',
                    'العاشر', 'الحادي عشر', 'الثاني عشر', 'الثالث عشر', 'الرابع عشر', 'الخامس عشر', 'السادس عشر',
                    'السابع عشر','الثامن عشر', 'التاسع عشر', 'العشرون', 'الواحد و العشرون', 'الثاني و العشرون', 'الثالث و العشرون',
                    'الرابع و العشرون','الخامس و العشرون', 'السادس و العشرون', 'السابع و العشرون', 'الثامن و العشرون', 'التاسع و العشرون',
                    'الثلاثين', 'الواحد و الثلاثين']
        copy = 0

        approve_payment_print_befor = self.env['finance.approval.payment'].search([('id', '=', benaficiary_id)])
        copy = 0
        fi = 0
        if approve_payment_print_befor.print_check_1 == True:
            copy = 1
        elif approve_payment_print_befor.print_check_1 == False:
            approve_payment_print_befor.write({'print_check_1': True})
            fi = 1
        company_name=""
        company = self.env.user.company_id.name
        for i in self.env['res.company'].search([]):
            if not i.parent_id:
                company_name = i.name
        if company == company_name:
            company = False
        counsel = self.env.user.company_id.counsel
        documentation = " "
        documentation = counsel.split(' ', 2)
        final = documentation[0][0] + ' ' + documentation[1][0] + ' ' + documentation[2][0]

        docargs = {
            'doc_ids': self.ids,
            'day': day_name[date_v.day - 1],
            'year': date_v.year,
            'month': name,
            'copy': copy,
            'fi': fi,
            'order_num': order_ids.name,
            'h_day': day_name[int(hijri.day)],
            'h_month': hijri.month_name,
            'h_year': int(hijri.year),
            'benaficiary': benaficiary,
            'project':project,
            'amount': amount,
            'company_name_parent': company_name,
            'company': company,
            'counsel': self.env.user.company_id.counsel,
            'counsel_character': self.env.user.company_id.counsel_character,
            'docum': final,
            'signed': signed,
            'first': first,
            'second': second,
            'final':final,
            'doc_model': purchase_contract_report.model,
        }

        return report.render('microfinance.purchase_contract_temp', docargs)

############## second type of Contract #################################

class MurabahaPurchaseContract(models.AbstractModel):
    _name = 'report.microfinance.murabaha_purchase_contract_temp'

    @api.model
    def render_html(self, docids, data):
        """
        :param data: Passed value form wizard
        :return: generating report
        """
        order_id = data['context']['order_id']
        benaficiary = data['context']['benaficiary_id']
        benaficiary_id = data['context']['benaficiary']
        project = data['context']['project_id']
        date = data['context']['date']
        signed = data['context']['user_id']
        first = data['context']['first_witnesse']
        second = data['context']['second_witnesse']
        date_v = datetime.strptime(date, '%Y-%m-%d')
        hijri = HijriDate(date_v.year, date_v.month, date_v.day , gr=True)
        report = self.env['report']
        murabaha_purchase_contract_report = report._get_report_from_name('microfinance.murabaha_purchase_contract_temp')
        ##########################

        order_ids = self.env['finance.order'].search([('id', '=', order_id)])
        approve_id = []
        guarantee = []
        guarantee_line = ""
        for approve in order_ids.visit_id.approve_ids:
            approve_id.append(approve.id)
        for guar in order_ids.guarantee_line_ids:
            guarantee.append(guar.guarantee_type.name)
        guarantee_line = u"-".join(guarantee)
        installment_ids = self.env['finance.installments'].search([('approval_id', 'in', approve_id),
                                                                   ('approval_id.formula', 'in',
                                                                    ['fixed_murabaha', 'dec_murabaha'])])
        approve_payment_print_befor = self.env['finance.approval.payment'].search([('id', '=', benaficiary_id)])
        copy = 0
        fi = 0
        if approve_payment_print_befor.print_check_1 == True:
            copy = 1
        elif approve_payment_print_befor.print_check_2 == False:
            approve_payment_print_befor.write({'print_check_2': True})
            fi = 1
        ins_no = 0
        amount_be_po = 0
        pro_or = 0
        insurance_am = 0
        expens_am = 0
        first_installment = 0
        payment_type = ""
        typ_1 = 0
        typ_2 = 0
        typ_3 = 0
        typ_4 = 0
        ins_no_min = min([l.installment_no for l in installment_ids]) + 1
        ins_nomin = min([l.installment_no for l in installment_ids])
        for installment in installment_ids:
            insurance_am = installment.approval_id.insurance_amount
            expens_am = installment.approval_id.expenses
            if installment.approval_id.downpayment > 0:
                if installment.installment_no == ins_no_min:
                    first_installment = installment.amount_before_profit + installment.profit_amount + expens_am + insurance_am
            elif installment.approval_id.downpayment == 0:
                if installment.installment_no == ins_nomin:
                    first_installment = installment.amount_before_profit
            if installment.approval_id.trust_receipt == True:
                payment_type = "إيصال أمانه"
                typ_1 = 1
            elif installment.approval_id.check == True:
                payment_type = "شيكات"
                typ_2 = 1
            elif installment.approval_id.electronic == True:
                payment_type = "إستقطاع مباشر"
                typ_3 = 1
            elif installment.approval_id.permanent_payment == True:
                payment_type = "أمر دفع مستديم"
                typ_4 = 1
            ins_no += 1
            amount_be_po = installment.amount_before_profit + installment.profit_amount + expens_am + insurance_am
            pro_or = installment.profit_amount
            total_amount = amount_be_po


        month_name = ['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أوكتوبر','نوفمبر','ديسمبر']
        day_name = ['الأول','الثاني','الثالث','الرابع','الخامس','السادس','السابع','الثامن','التاسع',
                    'العاشر','الحادي عشر','الثاني عشر','الثالث عشر','الرابع عشر','الخامس عشر','السادس عشر','السابع عشر',
                    'الثامن عشر','التاسع عشر','العشرون','الواحد و العشرون','الثاني و العشرون','الثالث و العشرون','الرابع و العشرون',
                    'الخامس و العشرون','السادس و العشرون','السابع و العشرون','الثامن و العشرون','التاسع و العشرون','الثلاثين','الواحد و الثلاثين']
        company_name=""
        company = self.env.user.company_id.name
        for i in self.env['res.company'].search([]):
            if not i.parent_id:
                company_name = i.name
        if company == company_name:
            company = False
        counsel = self.env.user.company_id.counsel
        documentation = " "
        documentation = counsel.split(' ', 2)
        final = documentation[0][0] + ' ' + documentation[1][0] + ' ' + documentation[2][0]

        docargs = {
            'doc_ids': self.ids,
            'day': day_name[date_v.day - 1],
            'year': date_v.year,
            'copy': copy,
            'fi': fi,
            'payment_type': payment_type,
            'typ_1': typ_1,
            'typ_2': typ_2,
            'typ_3': typ_3,
            'typ_4': typ_4,
            'month': month_name[date_v.month - 1],
            'first_installment': first_installment,
            'total_amount': total_amount,
            'amount_be_po': amount_be_po,
            'insurance_am': insurance_am,
            'order_num': order_ids.name,
            'pro_or': pro_or,
            'ins_no': ins_no,
            'expens_am': expens_am,
            'guarantee_line': guarantee_line,
            'h_day': int(hijri.day),
            'h_month': hijri.month_name,
            'h_year': int(hijri.year),
            'benaficiary': benaficiary,
            'project': project,
            'customer_name': order_ids.partner_id.name,
            'id_no': order_ids.partner_id.identity_number,
            'id_date': order_ids.partner_id.identity_date,
            'identity_location': order_ids.partner_id.identity_location,
            'identity_id': order_ids.partner_id.identity_id.name,
            'company_name_parent': company_name,
            'company': company,
            'counsel': self.env.user.company_id.counsel,
            'counsel_character': self.env.user.company_id.counsel_character,
            'docum': final,
            'signed': signed,
            'first': first,
            'second': second,
            'final':final,
            'doc_model': murabaha_purchase_contract_report.model,
        }

        return report.render('microfinance.murabaha_purchase_contract_temp', docargs)

############## Third type of Contract#################################


class ReceivingProduct(models.AbstractModel):
    _name = 'report.microfinance.receiving_product_temp'

    @api.model
    def render_html(self, docids, data):
        """
        :param data: Passed value form wizard
        :return: generating report
        """
        order_id = data['context']['order_id']
        project = data['context']['project_id']
        benaficiary_id = data['context']['benaficiary']
        date = data['context']['date']
        signed = data['context']['user_id']
        first = data['context']['first_witnesse']
        second = data['context']['second_witnesse']
        date_v = datetime.strptime(date, '%Y-%m-%d')
        report = self.env['report']

        receiving_product = report._get_report_from_name('microfinance.receiving_product_temp')

        order_ids = self.env['finance.order'].search([('id', '=', order_id)])

        formula = ""
        for approve in order_ids.approve_ids:
            if approve.formula_clone == 'buying_murabaha':
                formula = "مرابحه للآمر بالشراء"
            if approve.formula_clone == 'murabaha':
                formula = "مرابحه"

        approve_payment_print_befor = self.env['finance.approval.payment'].search([('id', '=', benaficiary_id)])
        copy = 0
        fi = 0
        if approve_payment_print_befor.print_check_3 == True:
            copy = 1
        elif approve_payment_print_befor.print_check_3 == False:
            approve_payment_print_befor.write({'print_check_3': True})
            fi = 1

        company_name = ""
        company = self.env.user.company_id.name
        for i in self.env['res.company'].search([]):
            if not i.parent_id:
                company_name = i.name
        if company == company_name:
            company = False
        counsel = self.env.user.company_id.counsel
        documentation = " "
        documentation = counsel.split(' ', 2)
        final = documentation[0][0] + ' ' + documentation[1][0] + ' ' + documentation[2][0]

        docargs = {

            'doc_ids': self.ids,
            'day': date_v.day,
            'year': date_v.year,
            'copy': copy,
            'fi': fi,
            'month': date_v.month,
            'project': project,
            'order_num': order_ids.name,
            'customer_name': order_ids.partner_id.name,
            'company_name_parent': company_name,
            'company': company,
            'counsel': self.env.user.company_id.counsel,
            'counsel_character': self.env.user.company_id.counsel_character,
            'docum': final,
            'formula': formula,
            'signed': signed,
            'first': first,
            'second': second,
            'final': final,
            'doc_model': receiving_product.model,
        }

        return report.render('microfinance.receiving_product_temp', docargs)

############## Forth Type of Contract #############################

class ARSV(models.AbstractModel):
    _name = 'report.microfinance.a_r_s_v_temp'

    @api.model
    def render_html(self, docids, data):
        """
        :param data: Passed value form wizard
        :return: generating report
        """
        order_id = data['context']['order_id']
        project = data['context']['project_id']
        date = data['context']['date']
        signed = data['context']['user_id']
        first = data['context']['first_witnesse']
        second = data['context']['second_witnesse']
        benaficiary = data['context']['benaficiary_id']
        date_v = datetime.strptime(date, '%Y-%m-%d')
        report = self.env['report']
        a_r_s_v = report._get_report_from_name('microfinance.a_r_s_v_temp')
        ids = []
        order = self.env['finance.order'].search([('id', '=', order_id)])
        for a in order.approve_ids:
            for payment in a.payment_ids:
                if payment.type in ['check', 'cash']:
                    for payed in payment:
                        ids.append(payed.id)
        bena_id = data['context']['benaficiary']
        copy = 0
        fi = 0
        approve_payment_print_befor = self.env['finance.approval.payment'].search([('id', '=', bena_id)])
        if approve_payment_print_befor.print_check_4 == True:
            copy = 1
        elif approve_payment_print_befor.print_check_4 == False:
            approve_payment_print_befor.write({'print_check_4': True})
            fi = 1
        amount = 0
        amount_in_word = ""
        check_no = 0
        check = 0
        account_payment = self.env['account.payment'].search([('id', '=', bena_id)])
        for account in account_payment:
            if account.payment_method_id.code == 'check_printing':
                amount = account.amount
                amount_in_word = amount_to_text_ar.amount_to_text(account.amount, 'ar')
                check_no = account.check_number
                check += 1
            elif account.payment_method_id.code == 'manual':
                amount = account.amount

        chart = ""
        for user in self.env['res.users'].search([('id', '=', data['context']['user'])]):
            for s in user.groups_id:
                if s.name == 'General Manager' or s.name == 'المدير العام'.decode('utf-8', 'ignore'):
                    chart = s.name
                elif s.name == 'Operation Manager' or s.name == 'مدير العمليات'.decode('utf-8', 'ignore'):
                    chart = s.name
                elif s.name == 'Branch Manager' or s.name == 'مدير الفرع'.decode('utf-8', 'ignore'):
                    chart = s.name
        company_name = ""
        company = self.env.user.company_id.name
        for i in self.env['res.company'].search([]):
            if not i.parent_id:
                company_name = i.name
        if company == company_name:
            company = False

        docargs = {
            'doc_ids': self.ids,
            'day': date_v.day,
            'copy': copy,
            'fi': fi,
            'year': date_v.year,
            'month': date_v.month,
            'project': project,
            'amount': amount,
            'amount_in_word': amount_in_word,
            'order_num': order.name,
            'benaficiary': benaficiary,
            'check_no': check_no,
            'customer_name': order.partner_id.name,
            'company_name_parent': company_name,
            'company': company,
            'signed': signed,
            'first': first,
            'check': check,
            'second': second,
            'character': chart,
            'doc_model': a_r_s_v.model,
        }

        return report.render('microfinance.a_r_s_v_temp', docargs)









