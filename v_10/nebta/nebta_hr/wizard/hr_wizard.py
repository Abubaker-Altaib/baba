# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import models, fields, api, exceptions, _
from datetime import datetime
from dateutil.relativedelta import *


# from dateutil import relativedelta


class EmployeeSalaryAdjustment(models.TransientModel):
    _name = "employee.salary.adjustment.wiz"

    year = fields.Selection([(num, str(num)) for num in range((datetime.now().year), datetime.now().year - 10, -1)],
                            string="year", default=datetime.now().year, required=True)
    months = fields.Selection([(num, str(num)) for num in range(1, 12 + 1)], string="month",
                              default=datetime.now().month, required=True)

    @api.multi
    def print_report(self):
        """
        print Salary Adjustment report
        :return:
        """
        datas = {
            'ids': '',
            'model': '',
            'context': {
                'year': self.year,
                'month': self.months,
            },

        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'nebta_hr.employee_salary_adjustment_temp',
            'datas': datas,
        }


class EmployeeSalaryAdjustReport(models.AbstractModel):
    _name = 'report.nebta_hr.employee_salary_adjustment_temp'

    @api.model
    def render_html(self, docids, data):
        """
        :param data: Passed value form wizard
        :return: generating report
        """
        report = self.env['report']
        employee_salary = report._get_report_from_name('nebta_hr.employee_salary_adjustment_temp')

        ################# Data From Context ######################

        month = data['context']['month']
        year = data['context']['year']

        from_date = datetime.strftime(datetime.now().replace(month=month, year=year), "%Y-%m-01")
        to_date = str(datetime.now().replace(month=month, year=year) + relativedelta(months=+1, day=1, days=-1))[:10]
        payslip_ids = self.env['hr.payslip.run'].search([('date_start', '=', from_date), ('date_end', '=', to_date),('state','=','confirmed'),('is_salary','=',True)])
        if not payslip_ids:
            raise exceptions.ValidationError(_("There is no Data"))
        BASIC = 0
        GROSS = 0
        net_tot = 0
        DED = 0
        ALLOW = 0
        ded_ids = []
        net_ids = []
        add_ids = []
        tm_total = 0
        high_total = 0
        for payslip in payslip_ids:
            for line in payslip.slip_ids:
                if line.state not in ['cancel']:
                    for l in line.details_by_salary_rule_category:
                        if l.category_id.code == 'BASIC':
                            BASIC += l.total
                        elif l.category_id.code == 'GROSS':
                            GROSS += l.total
                        elif l.category_id.code == 'DED':
                            DED += l.total
                            ded_ids.append(l.id)
                        elif l.category_id.code == 'ALW':
                            ALLOW += l.total
                        elif l.category_id.code == 'NET':
                            net_tot += l.total
                            net_ids.append(l.id)
                        elif l.category_id.code == 'ADD':
                            if 'TM' in l.code:
                                tm_total += l.total
                            if 'high' in l.code:
                                high_total += l.total
                            add_ids.append(l.id)

        name = []
        add_list = []
        tot = 0
        totals = 0

        deduction_ids = self.env['hr.payslip.line'].search([('id', 'in', ded_ids)])
        ADD = self.env['hr.payslip.line'].search([('id', 'in', add_ids)])
        add_total = 0
        for add_name in ADD:
            if add_name.name not in add_list:
                add_total += add_name.total
                add_list.append(add_name.name)
        ########################################## line one ########################
        tk = 0
        for names in deduction_ids:
            tot += names.total
            if 'TK' not in names.code and names.name not in name:
                name.append(names.name)
            if 'TK' in names.code:
                tk += names.total

        ########################################## line two #######################
        totals = net_tot + tot
        ################################# line there ############################
        my_dictionary = dict(map(lambda x: (x, 0.0), name))
        my_add = dict(map(lambda x: (x, 0.0), add_list))
        ############################# line for ##################################
        for did in deduction_ids:
            if 'TK' not in did.code:
                my_dictionary[did.name] += did.total
        ############################# line fife ################################
        for add in ADD:
            my_add[add.name] += add.total

        add_final = []
        for key in my_add.keys():
            res_add = dict(map(lambda x: (x, []), ['amount', 'add']))
            res_add['amount'] = my_add[key]
            res_add['add'] = key
            add_final.append(res_add)

        final = []
        for k in my_dictionary.keys():
            res = dict(map(lambda x: (x, []), ['amount', 'dmd']))
            res['amount'] = my_dictionary[k]
            res['dmd'] = k
            final.append(res)

            ###################################
        all_add = tm_total + high_total
        docargs = {
            'doc_ids': self.ids,
            'doc_model': employee_salary.model,
            'y': year,
            'm': month,
            'GROSS': GROSS,
            'ded': deduction_ids,
            'name': final,
            'add_final': add_final,
            'net_tot': net_tot,
            'tot': tot,
            'tm': tm_total,
            'high': high_total,
            'all_add': all_add,
            'tk': tk,
            'totals': totals,
        }

        return report.render('nebta_hr.employee_salary_adjustment_temp', docargs)


class EmployeeInsuranceReport(models.TransientModel):
    _name = "employee.insurance.wiz"

    year = fields.Selection([(num, str(num)) for num in range((datetime.now().year), datetime.now().year - 10, -1)],
                            string="year")

    @api.multi
    def print_report(self):
        """
        print Salary Adjustment report
        :return:
        """
        datas = {
            'ids': '',
            'model': '',
            'context': {
                'year': self.year,
            },

        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'nebta_hr.employee_insurance_temp',
            'datas': datas,
        }


class EmployeeInsurance(models.AbstractModel):
    _name = 'report.nebta_hr.employee_insurance_temp'

    @api.model
    def render_html(self, docids, data):
        contract_ids = []
        emp = 0
        employee_ids = []
        # month = data['context']['month']
        year = data['context']['year']
        docs = self.env['hr.contract']
        if year == False:
            docs = self.env['hr.contract'].search([('employee_id.resource_id.active', '=', True)],
                                                  order="employee_id,date_start,create_date")
            for doc in docs:
                if doc.employee_id != emp:
                    emp = doc.employee_id
                    contract_ids.append(doc.id)
            final_doc = self.env['hr.contract'].search(
                [('employee_id.resource_id.active', '=', True), ('id', 'in', contract_ids)])
        elif year:
            docs = self.env['hr.contract'].search([('employee_id.resource_id.active', '=', True)])
            for employee in docs:
                date = datetime.strptime(employee.date_start, '%Y-%m-%d')
                if date.year == year:
                    employee_ids.append(employee.id)
            docs = self.env['hr.contract'].search(
                [('id', 'in', employee_ids), ('employee_id.resource_id.active', '=', True)],
                order="employee_id,date_start,create_date")
            for doc in docs:
                if doc.employee_id != emp:
                    emp = doc.employee_id
                    contract_ids.append(doc.id)
            final_doc = self.env['hr.contract'].search(
                [('employee_id.resource_id.active', '=', True), ('id', 'in', contract_ids)])

        """docs = self.env['hr.contract'].search([('employee_id', 'in', docids)], order="employee_id,create_date,date_start")
        for doc in docs:
            if doc.employee_id != emp:
                emp = doc.employee_id
                contract_ids.append(doc.id)"""
        # final_doc = self.env['hr.contract'].search([('id', 'in', contract_ids)])

        date_time = datetime.strftime(datetime.now(), '%Y-%m-%d')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.contract',
            'docs': final_doc,
            'date_time': date_time,
        }

        return self.env['report'].render('nebta_hr.employee_insurance_temp', docargs)


class CertificateTestimony(models.AbstractModel):
    _name = 'report.nebta_hr.certificate_of_testimony_temp'

    @api.model
    def render_html(self, docids, data):
        contract_ids = []
        emp = 0
        docs = self.env['hr.contract'].search([('employee_id', 'in', docids)],
                                              order="employee_id,create_date,date_start")
        for doc in docs:
            if doc.employee_id != emp:
                emp = doc.employee_id
                contract_ids.append(doc.id)
        final_doc = self.env['hr.contract'].search([('id', 'in', contract_ids)])
        date_time = datetime.strftime(datetime.now(), '%Y-%m-%d')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.contract',
            'docs': final_doc,
            'date_time': date_time,
            'y': datetime.now().year,
            'm': datetime.now().month,

        }

        return self.env['report'].render('nebta_hr.certificate_of_testimony_temp', docargs)


class CertificateSalary(models.AbstractModel):
    _name = 'report.nebta_hr.certificate_of_salary_temp'

    @api.model
    def render_html(self, docids, data):
        docs = self.env['hr.payslip'].search([('id', 'in', docids)])
        employee = self.env['hr.employee'].search([('id', '=', docs.employee_id.id)])

        date_time = datetime.strftime(datetime.now(), '%Y-%m-%d')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.payslip',
            'docs': docs,
            'date_time': date_time,
            'y': datetime.now().year,
            'm': datetime.now().month,

        }

        return self.env['report'].render('nebta_hr.certificate_of_salary_temp', docargs)


class StaffStatements(models.TransientModel):
    _name = "staff.statements.wiz"

    statement_type =  fields.Selection([('all_emp','All'),('by_jobs','By jobs')],string="Statement Type", default='all_emp')
    year = fields.Selection([(num, str(num)) for num in range(datetime.now().year, datetime.now().year - 10, -1)],
                            string="year", required=False)
    months = fields.Selection([(num, str(num)) for num in range(1, 12 + 1)], string="month", required=False)
    active = fields.Selection([('active', 'Active'), ('archive', 'Archived')], string="Employee State",
                              default='active')
    job_id = fields.Many2one('hr.job', string="Job Title")


    @api.multi
    def print_report(self):
        """
        print Staff  report
        :return:
        """
        datas = {
            'ids': '',
            'model': '',
            'context': {
                'year': self.year,
                'month': self.months,
                'active': self.active,
                'job_id':self.job_id.id,
            },

        }
        if self.statement_type == 'all_emp':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'nebta_hr.all_employee_report_temp',
                'datas': datas,
            }
        elif self.statement_type == 'by_jobs':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'nebta_hr.job_employee_report_temp',
                'datas': datas,
            }




class AllEmployee(models.AbstractModel):
    _name = 'report.nebta_hr.all_employee_report_temp'

    @api.model
    def render_html(self, docids, data):
        report = self.env['report']
        all_employee = report._get_report_from_name('nebta_hr.all_employee_report_temp')

        ################# Data From Context ######################
        emp = 0
        contract_ids = []
        month = data['context']['month']
        year = data['context']['year']
        active = data['context']['active']
        employee_ids = []
        final_doc = self.env['hr.contract']
        docs = self.env['hr.contract']
        ############## if there no month and year ####################
        if month == False and year == False and active == False:
            docs = self.env['hr.contract'].search([], order="employee_id,date_start,create_date")
            for doc in docs:
                if doc.employee_id != emp:
                    emp = doc.employee_id
                    contract_ids.append(doc.id)
            final_doc = self.env['hr.contract'].search([('id', 'in', contract_ids)])

        ############## test if there a year or month or active ###################33
        # Active and year
        if year and active:
            if active == 'active':
                docs = self.env['hr.contract'].search([('employee_id.resource_id.active', '=', True)])
            elif active == 'archive':
                docs = self.env['hr.contract'].search([('employee_id.resource_id.active', '=', False)])
            for employee in docs:
                date = datetime.strptime(employee.date_start, '%Y-%m-%d')
                if date.year == year:
                    employee_ids.append(employee.id)
            docs = self.env['hr.contract'].search([('id', 'in', employee_ids)],
                                                  order="employee_id,date_start,create_date")
            for doc in docs:
                if doc.employee_id != emp:
                    emp = doc.employee_id
                    contract_ids.append(doc.id)
            final_doc = self.env['hr.contract'].search([('id', 'in', contract_ids)])
        elif month:
            docs = self.env['hr.contract'].search([])
            for employee in docs:
                date = datetime.strptime(employee.date_start, '%Y-%m-%d')
                if date.month == month:
                    employee_ids.append(employee.id)
            docs = self.env['hr.contract'].search([('id', 'in', set(employee_ids))],
                                                  order="employee_id,date_start,create_date")
            for doc in docs:
                if doc.employee_id != emp:
                    emp = doc.employee_id
                    contract_ids.append(doc.id)
            final_doc = self.env['hr.contract'].search([('id', 'in', contract_ids)])
        # Active and month
        elif month and active:
            if active == 'active':
                docs = self.env['hr.contract'].search([('employee_id.resource_id.active', '=', True)])
            elif active == 'archive':
                docs = self.env['hr.contract'].search([('employee_id.resource_id.active', '=', False)])
            for employee in docs:
                date = datetime.strptime(employee.date_start, '%Y-%m-%d')
                if date.month == month:
                    employee_ids.append(employee.id)
            docs = self.env['hr.contract'].search([('id', 'in', set(employee_ids))],
                                                  order="employee_id,date_start,create_date")
            for doc in docs:
                if doc.employee_id != emp:
                    emp = doc.employee_id
                    contract_ids.append(doc.id)
            final_doc = self.env['hr.contract'].search([('id', 'in', contract_ids)])
        elif month and year:
            docs = self.env['hr.contract'].search([])
            for employee in docs:
                date = datetime.strptime(employee.date_start, '%Y-%m-%d')
                if date.month == month and date.year == year:
                    employee_ids.append(employee.id)
            docs = self.env['hr.contract'].search([('id', 'in', employee_ids)],
                                                  order="employee_id,date_start,create_date")
            for doc in docs:
                if doc.employee_id != emp:
                    emp = doc.employee_id
                    contract_ids.append(doc.id)
            final_doc = self.env['hr.contract'].search([('id', 'in', contract_ids)])
        elif active:
            if active == 'active':
                docs = self.env['hr.contract'].search([('employee_id.resource_id.active', '=', True)],
                                                      order="employee_id,date_start,create_date")
                for doc in docs:
                    if doc.employee_id != emp:
                        emp = doc.employee_id
                        contract_ids.append(doc.id)
                final_doc = self.env['hr.contract'].search([('id', 'in', contract_ids)])
            elif active == 'archive':
                docs = self.env['hr.contract'].search([('employee_id.resource_id.active', '=', False)],
                                                      order="employee_id,date_start,create_date")
                for doc in docs:
                    if doc.employee_id != emp:
                        emp = doc.employee_id
                        contract_ids.append(doc.id)
                final_doc = self.env['hr.contract'].search([('id', 'in', contract_ids)])
        # if all filter is in >>>>
        elif active and year and month:
            if active == 'active':
                docs = self.env['hr.contract'].search([('employee_id.resource_id.active', '=', True)])
            elif active == 'archive':
                docs = self.env['hr.contract'].search([('employee_id.resource_id.active', '=', False)])
            for employee in docs:
                date = datetime.strptime(employee.date_start, '%Y-%m-%d')
                if date.month == month:
                    employee_ids.append(employee.id)
            docs = self.env['hr.contract'].search([('id', 'in', employee_ids)],
                                                  order="employee_id,date_start,create_date")
            for doc in docs:
                if doc.employee_id.id != emp:
                    emp = doc.employee_id.id
                    contract_ids.append(doc.id)
            final_doc = self.env['hr.contract'].search([('id', 'in', contract_ids)])

        if not final_doc:
            raise exceptions.ValidationError(_("There is no Data"))
        date_time = datetime.strftime(datetime.now(), '%Y-%m-%d')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': all_employee.model,
            'docs': final_doc,
            'date_time': date_time,
            'y': year,
            'm': month,

        }

        return report.render('nebta_hr.all_employee_report_temp', docargs)

class JobEmployeeReport(models.AbstractModel):
    _name = 'report.nebta_hr.job_employee_report_temp'

    @api.model
    def render_html(self, docids, data):
        report = self.env['report']
        job_employee = report._get_report_from_name('nebta_hr.job_employee_report_temp')

        ################# Data From Context ######################
        emp = 0
        contract_ids = []
        job_id = data['context']['job_id']
        docs = self.env['hr.contract'].search([('employee_id.resource_id.active', '=', True)],order="employee_id")
        for doc in docs:
            if doc.employee_id.id != emp:
                emp = doc.employee_id.id
                contract_ids.append(doc.id)
        final_doc = self.env['hr.contract'].search([('id', 'in', contract_ids),('employee_id.job_id','=', job_id)])
        if not final_doc:
            raise exceptions.ValidationError(_("There is no Data"))
        date_time = datetime.strftime(datetime.now(), '%Y-%m-%d')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': job_employee.model,
            'docs': final_doc,
            'date_time': date_time,

        }

        return report.render('nebta_hr.job_employee_report_temp', docargs)


class EmployeeSalaryAdjustment(models.TransientModel):
    _name = "employee.salary.adjustment.all.wiz"

    year = fields.Selection([(num, str(num)) for num in range(datetime.now().year, datetime.now().year - 10, -1)],
                            string="year", default=datetime.now().year, required=True)
    months = fields.Selection([(num, str(num)) for num in range(1, 12 + 1)], string="month",
                              default=datetime.now().month, required=True)

    @api.multi
    def print_report(self):
        """
        print Salary Adjustment report
        :return:
        """
        datas = {
            'ids': '',
            'model': '',
            'context': {
                'year': self.year,
                'month': self.months,
            },

        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'nebta_hr.employee_salary_all_adjustment_temp',
            'datas': datas,
        }

        ##################### fifth Report ##########################


class CustomerStateReport(models.AbstractModel):
    _name = 'report.nebta_hr.employee_salary_all_adjustment_temp'

    @api.model
    def render_html(self, docids, data):
        """
        :param data: Passed value form wizard
        :return: generating report
        """
        report = self.env['report']
        employee_salary = report._get_report_from_name('nebta_hr.employee_salary_all_adjustment_temp')

        ################# Data From Context ######################

        month = data['context']['month']
        year = data['context']['year']
        current_date = datetime.now()

        from_date = datetime.strftime(datetime.now().replace(month=month, year=year), "%Y-%m-01")
        to_date = str(datetime.now().replace(month=month, year=year) + relativedelta(months=+1, day=1, days=-1))[:10]

        run_payslip = self.env['hr.payslip.run'].search(
            [('date_start', '=', from_date), ('date_end', '=', to_date), ('is_salary', '=', True),
             ('state', '=', 'confirmed')])
        payslip = self.env['hr.payslip'].search([('salary', '=', True),('state','=','done'),('payslip_run_id','=',run_payslip.id)])
        pay_ids = []
        p_pay_ids = []
        names = []
        ppp = []
        add_name = []
        ded_name = []
        add_total_current = 0.0
        add_total_previous = 0.0
        defi = 0.0

        for pay in payslip:
            if not pay.name.__contains__('استرداد8:'.decode('utf-8', 'ignore')) and not pay.name.__contains__('Refund:'):
                current_date = datetime.strptime(pay.date_from, "%Y-%m-%d")
                pay_ids.append(pay.id)

        if month == 1:
            p_date = datetime.strftime((current_date.replace(month=12) - relativedelta(year=current_date.year - 1)),
                                       "%Y-%m-%d")
        else:
            p_month = month - 1
            p_date = datetime.strftime((current_date - relativedelta(month=p_month)), "%Y-%m-%d")

        previous_payslip = self.env['hr.payslip'].search([('date_from', '=', p_date), ('salary', '=', True)])
        for p_pay in previous_payslip:
            if not p_pay.name.__contains__('استرداد:'.decode('utf-8', 'ignore')) and not p_pay.name.__contains__(
                    'Refund:'):
                p_pay_ids.append(p_pay.id)

        pre_payslip = self.env['hr.payslip'].search(
            [('id', 'in', p_pay_ids), ('state', '=', 'done'), ('salary', '=', True),('payslip_run_id','=',run_payslip.id)])

        payslip_ids = self.env['hr.payslip'].search(
            [('id', 'in', pay_ids), ('state', '=', 'done'), ('salary', '=', True),('payslip_run_id','=',run_payslip.id)])
        if not payslip_ids:
            raise exceptions.ValidationError(_("There is no Data"))

        for line in payslip_ids:
            if not line.employee_id.id in names:
                names.append(line.employee_id.id)
        for pre_line in pre_payslip:
            if not pre_line.employee_id.id in names:
                names.append(pre_line.employee_id.id)

        my_dictionary = dict(map(lambda x: (x, {'name': '',
                                                'gross': 0.0,
                                                'add': {},
                                                'ded': {},
                                                'net': 0.0,
                                                'tm': 0.0,
                                                'high': 0.0,
                                                'tk': 0.0,
                                                'current': 0.0,
                                                'previous': 0.0,
                                                }), names))

        for l in payslip_ids:
            my_dictionary[l.employee_id.id].update({'name': l.employee_id.name})
            for li in l.details_by_salary_rule_category:
                if li.category_id.code == 'ADD':
                    add_total_current += li.total
                    if 'TM' in li.code:
                        my_dictionary[l.employee_id.id].update({'tm': li.total})
                    if 'high' in li.code:
                        my_dictionary[l.employee_id.id].update({'high': li.total})
                    if li.name not in add_name:
                        add_name.append(li.name)
                elif li.category_id.code == 'DED':
                    if 'TK' not in li.code and li.name not in ded_name:
                        ded_name.append(li.name)
                    if 'TK' in li.code:
                        my_dictionary[l.employee_id.id].update({'tk': li.total})

                elif li.category_id.code == 'GROSS':
                    my_dictionary[l.employee_id.id].update({'gross': li.total})
                elif li.category_id.code == 'NET':
                    my_dictionary[l.employee_id.id].update({'net': li.total})
            my_dictionary[l.employee_id.id].update({'current': add_total_current})
            add_total_current = 0

        # To check if the employee have a previous
        for p_l in pre_payslip:
            for li in p_l.details_by_salary_rule_category:
                if li.category_id.code == 'ADD':
                    add_total_previous += li.total
            my_dictionary[p_l.employee_id.id].update({'previous': add_total_previous})

        # To check if the employee have this type of add if not then add zero to it total
        for l in payslip_ids:
            final = []
            for n in add_name:
                res = dict((fn, 0.0) for fn in ['name', 'total'])
                active = False
                for li in l.details_by_salary_rule_category:
                    if li.category_id.code == 'ADD':
                        if n == li.name:
                            res['name'] = li.name
                            res['total'] = li.total
                            final.append(res)
                            active = True
                if not active:
                    res['name'] = n
                    res['total'] = 0.0
                    final.append(res)
            if len(final) != 0:
                my_dictionary[l.employee_id.id].update({'add': final})
            elif len(final) == 0:
                for n in add_name:
                    res = dict((fn, 0.0) for fn in ['name', 'total'])
                    res['name'] = n
                    res['total'] = 0.0
                    final.append(res)
                my_dictionary[l.employee_id.id].update({'add': final})

        # To check if this employee have this type of deduction if not add zero to it total
        for l in payslip_ids:
            final = []
            for n in ded_name:
                res = dict((fn, 0.0) for fn in ['name', 'total'])
                active = False
                for li in l.details_by_salary_rule_category:
                    if li.category_id.code == 'DED':
                        if n == li.name:
                            res['name'] = li.name
                            res['total'] = li.total
                            final.append(res)
                            active = True
                if not active:
                    res['name'] = n
                    res['total'] = 0.0
                    final.append(res)
            if len(final) != 0:
                my_dictionary[l.employee_id.id].update({'ded': final})
            elif len(final) == 0:
                for n in ded_name:
                    res = dict((fn, 0.0) for fn in ['name', 'total'])
                    res['name'] = n
                    res['total'] = 0.0
                    final.append(res)
                my_dictionary[l.employee_id.id].update({'ded': final})
        name = ""
        if month == 1:
            name = "يناير"
        elif month == 2:
            name = "فبراير"
        elif month == 3:
            name = "مارس"
        elif month == 4:
            name = "أبريل"
        elif month == 5:
            name = "مايو"
        elif month == 6:
            name = "يونيو"
        elif month == 7:
            name = "يوليو"
        elif month == 8:
            name = "أغسطس"
        elif month == 9:
            name = "سبتمبر"
        elif month == 10:
            name = "أوكتوبر"
        elif month == 11:
            name = "نوفمبر"
        elif month == 12:
            name = "ديسمبر"

        ########################################## line one ########################
        docargs = {
            'doc_ids': self.ids,
            'doc_model': employee_salary.model,
            'y': year,
            'm': month,
            'name': name,
            'docs': payslip_ids,
            'my_dictionary': my_dictionary,
            'add_name': add_name,
            'ded_name': ded_name,
            'ded_span': len(ded_name) + 2,

        }

        return report.render('nebta_hr.employee_salary_all_adjustment_temp', docargs)


################################## sixth Report ##############################################


class EmployeeBudgetClass(models.TransientModel):
    _name = "employee.budget.wiz"

    year = fields.Selection([(num, str(num)) for num in range((datetime.now().year), datetime.now().year - 10, -1)],
                            string="year", default=datetime.now().year, required=True)
    months = fields.Selection([(num, str(num)) for num in range(1, 12 + 1)], string="month",
                              default=datetime.now().month, required=True)

    @api.multi
    def print_report(self):
        """
        print Salary Adjustment report
        :return:
        """
        datas = {
            'ids': '',
            'model': '',
            'context': {
                'year': self.year,
                'month': self.months,
            },

        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'nebta_hr.employee_budget_temp',
            'datas': datas,
        }


class EmployeeBudgetReport(models.AbstractModel):
    _name = 'report.nebta_hr.employee_budget_temp'

    @api.model
    def render_html(self, docids, data):
        report = self.env['report']
        budget_employee = report._get_report_from_name('nebta_hr.employee_budget_temp')
        month = data['context']['month']
        year = data['context']['year']
        current_month = []
        previous_month = []
        employee_id = []
        mydate = datetime.now()
        p_date = datetime.now()

        from_date = datetime.strftime(datetime.now().replace(month=month, year=year), "%Y-%m-01")
        to_date = str(datetime.now().replace(month=month, year=year) + relativedelta(months=+1, day=1, days=-1))[:10]

        run_payslip = self.env['hr.payslip.run'].search(
            [('date_start', '=', from_date), ('date_end', '=', to_date), ('is_salary', '=', True),
             ('state', '=', 'confirmed')])
        docs = self.env['hr.payslip'].search([('payslip_run_id','=',run_payslip.id), ('state', '=', 'done'), ('salary', '=', True)])

        for payslip in docs:
            if payslip.name:
                if not payslip.name.__contains__(
                        'استرداد:'.decode('utf-8', 'ignore')) and not payslip.name.__contains__('Refund'):
                    date = datetime.strptime(payslip.date_from, '%Y-%m-%d')
                    if date.month == month and date.year == year:
                        mydate = date
                        current_month.append(payslip.id)
                        employee_id.append(payslip.employee_id.id)

            if month == 1:
                p_date = datetime.strftime((mydate.replace(month=12) - relativedelta(year=date.year - 1)), "%Y-%m-%d")
            else:
                p_month = month - 1
                p_date = datetime.strftime((mydate - relativedelta(month=p_month)), "%Y-%m-%d")
        # To get all previous payment that not refund
        previous_pay = self.env['hr.payslip'].search(
            [('date_from', '=', p_date), ('state', '=', 'done'), ('salary', '=', True)])
        for pe in previous_pay:
            if not pe.name.__contains__('استرداد:'.decode('utf-8', 'ignore')) and not pe.name.__contains__('Refund'):
                previous_month.append(pe.id)

        current = self.env['hr.payslip'].search([('id', 'in', current_month), ('salary', '=', True)])
        previous = self.env['hr.payslip'].search([('id', 'in', previous_month), ('salary', '=', True)])
        if not current:
            raise exceptions.ValidationError(_("There is no data"))

        names = []
        for pay in current:
            if pay.employee_id.id not in names:
                names.append(pay.employee_id.id)
        for pe_pay in previous:
            if pe_pay.employee_id.id not in names:
                names.append(pe_pay.employee_id.id)

        my_dictionary = dict(map(lambda x: (x, {'name': '',
                                                'empcode': '',
                                                'degree': '',
                                                'current': 0.0,
                                                'previous': 0.0,
                                                'increase': 0.0,
                                                'decrease': 0.0}), names))
        for cu in current:
            my_dictionary[cu.employee_id.id].update({'name': cu.employee_id.name,
                                                     'empcode': cu.employee_id.employee_code,
                                                     'degree': cu.employee_id.contract_id.struct_id.parent_id.name})
            for c in cu.details_by_salary_rule_category:
                if c.category_id.code == 'GROSS':
                    my_dictionary[cu.employee_id.id].update({'current': c.total})
        if previous:
            for pu in previous:
                my_dictionary[pu.employee_id.id].update({'name': pu.employee_id.name,
                                                         'empcode': pu.employee_id.employee_code,
                                                         'degree': pu.employee_id.contract_id.struct_id.parent_id.name})
                for p in pu.details_by_salary_rule_category:
                    if p.category_id.code == 'GROSS':
                        cur = my_dictionary[pu.employee_id.id]['current']
                        if cur > p.total:
                            increase = cur - p.total
                            my_dictionary[pu.employee_id.id].update({'previous': p.total, 'increase': increase})
                        elif cur < p.total:
                            decreases = p.total - cur
                            my_dictionary[pu.employee_id.id].update({'previous': p.total, 'decrease': decreases})
                        elif cur == p.total:
                            my_dictionary[pu.employee_id.id].update({'previous': p.total})

        date_time = datetime.strftime(datetime.now(), '%Y-%m-%d')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': budget_employee.model,
            'm': month,
            'y': year,
            'date_time': date_time,
            'docs': current,
            'my_dictionary': my_dictionary,

        }

        return report.render('nebta_hr.employee_budget_temp', docargs)


class HrAddWizardReport(models.Model):
    _name = "add.report.wiz"

    add_type = fields.Selection(
        [('mile_allowance', 'A mile allowance'), ('transition_allowance', 'Transition allowance'),
         ('medical', 'Medical care allowance'), ('vacation', 'Vacation allowance'), ('wearing', 'wearing allowance'),
         ('eidf', 'Eid al-Fitr grant'), ('eida', 'Eid al-Adha grant')])
    year = fields.Selection([(num, str(num)) for num in range((datetime.now().year), datetime.now().year - 10, -1)],
                            string="Year", default=datetime.now().year, required=True)
    months = fields.Selection([(num, str(num)) for num in range(1, 12 + 1)], string="month",
                              default=datetime.now().month, required=True)

    @api.multi
    def print_report(self):
        """
        print Salary Adjustment report
        :return:
        """
        datas = {
            'ids': '',
            'model': '',
            'context': {
                'add_type': self.add_type,
                'year': self.year,
                'month': self.months,
            },

        }
        if self.add_type == 'mile_allowance':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'nebta_hr.employee_allowance_temp',
                'datas': datas,
            }
        elif self.add_type == 'transition_allowance':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'nebta_hr.transition_allowance_temp',
                'datas': datas,
            }
        elif self.add_type == 'medical':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'nebta_hr.medical_allowance_temp',
                'datas': datas,
            }
        elif self.add_type == 'vacation':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'nebta_hr.vacation_allowance_temp',
                'datas': datas,
            }
        elif self.add_type == 'wearing':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'nebta_hr.wearing_allowance_temp',
                'datas': datas,
            }
        elif self.add_type == 'eidf':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'nebta_hr.eidf_allowance_temp',
                'datas': datas,
            }
        elif self.add_type == 'eida':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'nebta_hr.eida_allowance_temp',
                'datas': datas,
            }


class HrAddWizardTempMedical(models.AbstractModel):
    _name = "report.nebta_hr.medical_allowance_temp"

    @api.model
    def render_html(self, docids, data):
        report = self.env['report']
        employee_allowance = report._get_report_from_name('nebta_hr.medical_allowance_temp')

        month = data['context']['month']
        year = data['context']['year']
        employee_ids = []
        from_date = datetime.strftime(datetime.now().replace(month=month, year=year), "%Y-%m-01")
        to_date = str(datetime.now().replace(month=month, year=year) + relativedelta(months=+1, day=1, days=-1))[:10]
        payslip_ids = self.env['hr.payslip.run'].search(
            [('date_start', '=', from_date), ('date_end', '=', to_date), ('is_salary', '=', False)])
        if not payslip_ids:
            raise exceptions.ValidationError(_("There is no Data"))
        for payslip in payslip_ids:
            for line in payslip.slip_ids:
                for l in line.line_ids:
                    if l.category_id.code == 'MOO':
                        if 'hos' in l.code:
                            employee_ids.append(line.employee_id.id)
        if len(employee_ids) == 0:
            raise exceptions.ValidationError(_("There is no Data"))
        my_dictionary = dict(map(lambda x: (x, {'name': '',
                                                'emp_code': 0,
                                                'work_loc': '',
                                                'job_title': '',
                                                'quantity': 0,
                                                'total': 0.0}), employee_ids))
        final_payslip = self.env[('hr.payslip')].search([('employee_id', 'in', employee_ids)])
        for slip in final_payslip:
            my_dictionary[slip.employee_id.id].update({'name': slip.employee_id.name,
                                                       'emp_code': slip.employee_id.employee_code,
                                                       'work_loc': slip.employee_id.work_location,
                                                       'job_title': slip.employee_id.job_id.name,
                                                       })
            for detial in slip.line_ids:
                if detial.category_id.code == 'MOO':
                    if 'hos' in detial.code:
                        my_dictionary[slip.employee_id.id].update({'total': detial.total, 'quantity': detial.quantity})

        date_time = datetime.strftime(datetime.now(), '%Y-%m-%d')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': employee_allowance.model,
            'm': month,
            'y': year,
            'employee_ids': employee_ids,
            'date_time': date_time,
            'my_dictionary': my_dictionary,

        }

        return report.render('nebta_hr.medical_allowance_temp', docargs)


class HrAddWizardTempVacation(models.AbstractModel):
    _name = "report.nebta_hr.vacation_allowance_temp"

    @api.model
    def render_html(self, docids, data):
        report = self.env['report']
        employee_allowance = report._get_report_from_name('nebta_hr.vacation_allowance_temp')

        month = data['context']['month']
        year = data['context']['year']
        employee_ids = []
        from_date = datetime.strftime(datetime.now().replace(month=month, year=year), "%Y-%m-01")
        to_date = str(datetime.now().replace(month=month, year=year) + relativedelta(months=+1, day=1, days=-1))[:10]
        payslip_ids = self.env['hr.payslip.run'].search(
            [('date_start', '=', from_date), ('date_end', '=', to_date), ('is_salary', '=', False)])
        if not payslip_ids:
            raise exceptions.ValidationError(_("There is no Data"))
        for payslip in payslip_ids:
            for line in payslip.slip_ids:
                for l in line.line_ids:
                    if l.category_id.code == 'MOO':
                        if 'holy' in l.code:
                            employee_ids.append(line.employee_id.id)
        if len(employee_ids) == 0:
            raise exceptions.ValidationError(_("There is no Data"))
        my_dictionary = dict(map(lambda x: (x, {'name': '',
                                                'emp_code': 0,
                                                'work_loc': '',
                                                'job_title': '',
                                                'quantity': 0,
                                                'total': 0.0}), employee_ids))
        final_payslip = self.env[('hr.payslip')].search([('employee_id', 'in', employee_ids)])
        for slip in final_payslip:
            my_dictionary[slip.employee_id.id].update({'name': slip.employee_id.name,
                                                       'emp_code': slip.employee_id.employee_code,
                                                       'work_loc': slip.employee_id.work_location,
                                                       'job_title': slip.employee_id.job_id.name,
                                                       })
            for detial in slip.line_ids:
                if detial.category_id.code == 'MOO':
                    if 'holy' in detial.code:
                        my_dictionary[slip.employee_id.id].update({'total': detial.total, 'quantity': detial.quantity})

        date_time = datetime.strftime(datetime.now(), '%Y-%m-%d')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': employee_allowance.model,
            'm': month,
            'y': year,
            'employee_ids': employee_ids,
            'date_time': date_time,
            'my_dictionary': my_dictionary,

        }

        return report.render('nebta_hr.vacation_allowance_temp', docargs)


class HrAddWizardTempWearing(models.AbstractModel):
    _name = "report.nebta_hr.wearing_allowance_temp"

    @api.model
    def render_html(self, docids, data):
        report = self.env['report']
        employee_allowance = report._get_report_from_name('nebta_hr.wearing_allowance_temp')

        month = data['context']['month']
        year = data['context']['year']
        employee_ids = []
        from_date = datetime.strftime(datetime.now().replace(month=month, year=year), "%Y-%m-01")
        to_date = str(datetime.now().replace(month=month, year=year) + relativedelta(months=+1, day=1, days=-1))[:10]
        payslip_ids = self.env['hr.payslip.run'].search(
            [('date_start', '=', from_date), ('date_end', '=', to_date), ('is_salary', '=', False)])
        if not payslip_ids:
            raise exceptions.ValidationError(_("There is no Data"))
        for payslip in payslip_ids:
            for line in payslip.slip_ids:
                for l in line.line_ids:
                    if l.category_id.code == 'MOO':
                        if 'cloth' in l.code:
                            employee_ids.append(line.employee_id.id)
        if len(employee_ids) == 0:
            raise exceptions.ValidationError(_("There is no Data"))
        my_dictionary = dict(map(lambda x: (x, {'name': '',
                                                'emp_code': 0,
                                                'work_loc': '',
                                                'job_title': '',
                                                'quantity': 0,
                                                'total': 0.0}), employee_ids))
        final_payslip = self.env[('hr.payslip')].search([('employee_id', 'in', employee_ids)])
        for slip in final_payslip:
            my_dictionary[slip.employee_id.id].update({'name': slip.employee_id.name,
                                                       'emp_code': slip.employee_id.employee_code,
                                                       'work_loc': slip.employee_id.work_location,
                                                       'job_title': slip.employee_id.job_id.name,
                                                       })
            for detial in slip.line_ids:
                if detial.category_id.code == 'MOO':
                    if 'cloth' in detial.code:
                        my_dictionary[slip.employee_id.id].update({'total': detial.total, 'quantity': detial.quantity})

        date_time = datetime.strftime(datetime.now(), '%Y-%m-%d')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': employee_allowance.model,
            'm': month,
            'y': year,
            'employee_ids': employee_ids,
            'date_time': date_time,
            'my_dictionary': my_dictionary,

        }

        return report.render('nebta_hr.wearing_allowance_temp', docargs)


class HrAddWizardTempEidf(models.AbstractModel):
    _name = "report.nebta_hr.eidf_allowance_temp"

    @api.model
    def render_html(self, docids, data):
        report = self.env['report']
        employee_allowance = report._get_report_from_name('nebta_hr.eidf_allowance_temp')

        month = data['context']['month']
        year = data['context']['year']
        employee_ids = []
        from_date = datetime.strftime(datetime.now().replace(month=month, year=year), "%Y-%m-01")
        to_date = str(datetime.now().replace(month=month, year=year) + relativedelta(months=+1, day=1, days=-1))[:10]
        payslip_ids = self.env['hr.payslip.run'].search(
            [('date_start', '=', from_date), ('date_end', '=', to_date), ('is_salary', '=', False)])
        if not payslip_ids:
            raise exceptions.ValidationError(_("There is no Data"))
        for payslip in payslip_ids:
            for line in payslip.slip_ids:
                for l in line.line_ids:
                    if l.category_id.code == 'MOO':
                        if 'hope' in l.code:
                            employee_ids.append(line.employee_id.id)
        if len(employee_ids) == 0:
            raise exceptions.ValidationError(_("There is no Data"))
        my_dictionary = dict(map(lambda x: (x, {'name': '',
                                                'emp_code': 0,
                                                'work_loc': '',
                                                'job_title': '',
                                                'quantity': 0,
                                                'total': 0.0}), employee_ids))
        final_payslip = self.env[('hr.payslip')].search([('employee_id', 'in', employee_ids)])
        for slip in final_payslip:
            my_dictionary[slip.employee_id.id].update({'name': slip.employee_id.name,
                                                       'emp_code': slip.employee_id.employee_code,
                                                       'work_loc': slip.employee_id.work_location,
                                                       'job_title': slip.employee_id.job_id.name,
                                                       })
            for detial in slip.line_ids:
                if detial.category_id.code == 'MOO':
                    if 'hope' in detial.code:
                        my_dictionary[slip.employee_id.id].update({'total': detial.total, 'quantity': detial.quantity})

        date_time = datetime.strftime(datetime.now(), '%Y-%m-%d')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': employee_allowance.model,
            'm': month,
            'y': year,
            'employee_ids': employee_ids,
            'date_time': date_time,
            'my_dictionary': my_dictionary,

        }

        return report.render('nebta_hr.eidf_allowance_temp', docargs)


class HrAddWizardTempEida(models.AbstractModel):
    _name = "report.nebta_hr.eida_allowance_temp"

    @api.model
    def render_html(self, docids, data):
        report = self.env['report']
        employee_allowance = report._get_report_from_name('nebta_hr.eida_allowance_temp')

        month = data['context']['month']
        year = data['context']['year']
        employee_ids = []
        from_date = datetime.strftime(datetime.now().replace(month=month, year=year), "%Y-%m-01")
        to_date = str(datetime.now().replace(month=month, year=year) + relativedelta(months=+1, day=1, days=-1))[:10]
        payslip_ids = self.env['hr.payslip.run'].search(
            [('date_start', '=', from_date), ('date_end', '=', to_date), ('is_salary', '=', False)])
        if not payslip_ids:
            raise exceptions.ValidationError(_("There is no Data"))
        for payslip in payslip_ids:
            for line in payslip.slip_ids:
                for l in line.line_ids:
                    if l.category_id.code == 'MOO':
                        if 'hope2' in l.code:
                            employee_ids.append(line.employee_id.id)
        if len(employee_ids) == 0:
            raise exceptions.ValidationError(_("There is no Data"))
        my_dictionary = dict(map(lambda x: (x, {'name': '',
                                                'emp_code': 0,
                                                'work_loc': '',
                                                'job_title': '',
                                                'quantity': 0,
                                                'total': 0.0}), employee_ids))
        final_payslip = self.env[('hr.payslip')].search([('employee_id', 'in', employee_ids)])
        for slip in final_payslip:
            my_dictionary[slip.employee_id.id].update({'name': slip.employee_id.name,
                                                       'emp_code': slip.employee_id.employee_code,
                                                       'work_loc': slip.employee_id.work_location,
                                                       'job_title': slip.employee_id.job_id.name,
                                                       })
            for detial in slip.line_ids:
                if detial.category_id.code == 'MOO':
                    if 'hope2' in detial.code:
                        my_dictionary[slip.employee_id.id].update({'total': detial.total, 'quantity': detial.quantity})

        date_time = datetime.strftime(datetime.now(), '%Y-%m-%d')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': employee_allowance.model,
            'm': month,
            'y': year,
            'employee_ids': employee_ids,
            'date_time': date_time,
            'my_dictionary': my_dictionary,

        }

        return report.render('nebta_hr.eida_allowance_temp', docargs)



class HrAddWizardTempMove(models.AbstractModel):
    _name = "report.nebta_hr.transition_allowance_temp"

    @api.model
    def render_html(self, docids, data):
        report = self.env['report']
        employee_allowance = report._get_report_from_name('nebta_hr.transition_allowance_temp')

        month = data['context']['month']
        year = data['context']['year']
        employee_ids = []

        from_date = datetime.strftime(datetime.now().replace(month=month, year=year), "%Y-%m-01")
        to_date = str(datetime.now().replace(month=month, year=year) + relativedelta(months=+1, day=1, days=-1))[:10]
        payslip_ids = self.env['hr.payslip.run'].search(
            [('date_start', '=', from_date), ('date_end', '=', to_date), ('is_salary', '=', False)])
        if not payslip_ids:
            raise exceptions.ValidationError(_("There is no Data"))
        for payslip in payslip_ids:
            for line in payslip.slip_ids:
                for l in line.details_by_salary_rule_category:
                    if l.category_id.code == 'MOO':
                        if 'move' in l.code:
                            employee_ids.append(line.employee_id.id)
        if len(employee_ids) == 0:
            raise exceptions.ValidationError(_("There is no Data"))
        my_dictionary = dict(map(lambda x: (x, {'name': '',
                                                'emp_code': 0,
                                                'work_loc': '',
                                                'job_title': '',
                                                'total': 0.0}), employee_ids))
        final_payslip = self.env[('hr.payslip')].search([('employee_id', 'in', employee_ids)])
        for slip in final_payslip:
            my_dictionary[slip.employee_id.id].update({'name': slip.employee_id.name,
                                                       'emp_code': slip.employee_id.employee_code,
                                                       'work_loc': slip.employee_id.work_location,
                                                       'job_title': slip.employee_id.job_id.name,
                                                       })
            for detial in slip.details_by_salary_rule_category:
                if detial.category_id.code == 'MOO':
                    if 'move' in detial.code:
                        my_dictionary[slip.employee_id.id].update({'total': detial.total})

        date_time = datetime.strftime(datetime.now(), '%Y-%m-%d')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': employee_allowance.model,
            'm': month,
            'y': year,
            'employee_ids': employee_ids,
            'date_time': date_time,
            'my_dictionary': my_dictionary,

        }

        return report.render('nebta_hr.transition_allowance_temp', docargs)


class HrAddWizardTemp(models.AbstractModel):
    _name = "report.nebta_hr.employee_allowance_temp"

    @api.model
    def render_html(self, docids, data):
        report = self.env['report']
        employee_allowance = report._get_report_from_name('nebta_hr.employee_allowance_temp')

        month = data['context']['month']
        year = data['context']['year']
        employee_ids = []

        from_date = datetime.strftime(datetime.now().replace(month=month, year=year), "%Y-%m-01")
        to_date = str(datetime.now().replace(month=month, year=year) + relativedelta(months=+1, day=1, days=-1))[:10]
        payslip_ids = self.env['hr.payslip.run'].search(
            [('date_start', '=', from_date), ('date_end', '=', to_date), ('is_salary', '=', False)])
        if not payslip_ids:
            raise exceptions.ValidationError(_("There is no Data"))
        for payslip in payslip_ids:
            for line in payslip.slip_ids:
                for l in line.details_by_salary_rule_category:
                    if l.category_id.code == 'MOO':
                        if 'mel' in l.code:
                            employee_ids.append(line.employee_id.id)
        if len(employee_ids) == 0:
            raise exceptions.ValidationError(_("There is no Data"))
        my_dictionary = dict(map(lambda x: (x, {'name': '',
                                                'emp_code': 0,
                                                'work_loc': '',
                                                'job_title': '',
                                                'total': 0.0}), employee_ids))
        final_payslip = self.env[('hr.payslip')].search([('employee_id', 'in', employee_ids)])
        for slip in final_payslip:
            my_dictionary[slip.employee_id.id].update({'name': slip.employee_id.name,
                                                       'emp_code': slip.employee_id.employee_code,
                                                       'work_loc': slip.employee_id.work_location,
                                                       'job_title': slip.employee_id.job_id.name,
                                                       })
            for detial in slip.details_by_salary_rule_category:
                if detial.category_id.code == 'MOO':
                    if 'mel' in detial.code:
                        my_dictionary[slip.employee_id.id].update({'total': detial.total})

        date_time = datetime.strftime(datetime.now(), '%Y-%m-%d')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': employee_allowance.model,
            'm': month,
            'y': year,
            'docs': final_payslip,
            'employee_ids': employee_ids,
            'date_time': date_time,
            'my_dictionary': my_dictionary,

        }

        return report.render('nebta_hr.employee_allowance_temp', docargs)
