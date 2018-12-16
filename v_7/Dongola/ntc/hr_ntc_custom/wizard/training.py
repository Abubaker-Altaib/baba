# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import pooler
import time
from datetime import datetime
from dateutil import relativedelta
from tools.translate import _
from openerp.osv import fields, osv, orm



class training_report_outside(osv.osv_memory):

    _name = 'training.report.outside'

    _columns = {
        'company_id': fields.many2many('res.company', 'hr_report_company_rel_training', 'report_id', 'company_id', 'Company', required=True),
        'training_category_id': fields.many2many('hr.training.category', 'hr_report_training_rel_report', 'report_id', 'category_id', string='Category', required=True),
        'payroll_ids': fields.many2many('hr.salary.scale', 'hr_report_payroll_rel_training', 'pay_bonus', 'pay_id', 'Salary Scale'),
        'qual_ids': fields.many2many('hr.qualification', 'hr_report_qulaification_rel_training', 'pay_bonus', 'pay_id', 'Qualification'),
        'type': fields.selection([('1', 'بين الوحدة و نظيراتها'), ('2', 'بين الدولة و نظيراتها'), ('3', 'داخل السودان')],
                                 'Type', required=True),
        'type1': fields.selection([('1', 'بالموظفين'), ('2', 'بالدرجة الوظيفية')],
                                  'Type', required=True),
        'date_from': fields.date('Start Date'),
        'date_to': fields.date('End Date'),
    }

    def _get_companies(self, cr, uid, context=None):
        return [self.pool.get('res.users').browse(cr, uid, uid).company_id.id]

    _defaults = {
        'type': '1',
        'type1': '1',
        'company_id': _get_companies,
    }

    def print_report(self, cr, uid, ids, context={}):

        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
            'ids': context.get('active_ids', []),
            'model': 'hr.employee.training',
            'form': data
        }
        return{
            'type': 'ir.actions.report.xml',
            'report_name': 'course.outside',
            'datas': datas,
        }



    def print_report_2(self, cr, uid, ids, context={}):
        
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        if data['type1'] == '1':
            datas = {
                'ids': context.get('active_ids', []),
                'model': 'hr.employee.training',
                'form': data
            }
            return{
                'type': 'ir.actions.report.xml',
                'report_name': 'training.employee',
                'datas': datas,
            }
        else:
            datas = {
                'ids': context.get('active_ids', []),
                'model': 'hr.employee',
                'form': data
            }
            return{
                'type': 'ir.actions.report.xml',
                'report_name': 'training.employee_two',
                'datas': datas,
            }


class training_wizard(osv.osv_memory):

    _name = 'training.wizard'

    _columns = {
        'emp_id': fields.many2one('hr.employee', 'Employee', invisible=True, readonly=False),
        'suggested_blank': fields.one2many('training.suggested.blank.wizard', 'line_id', string="new"),
        'suggested': fields.many2many('hr.training.course', 'training_line_course_wizard_rel', string='Training Suggested'),
        'inc_emps': fields.boolean('Include Relative Employees'),
    }

    def w_create(self, cr, uid, ids, context=None):
        datas = self.browse(cr, uid, ids, context=context)
        user = self.pool.get('res.users').read(
            cr, uid, uid, ['employee_ids'], context=context)['employee_ids']
        form_obj = self.pool.get('training.form')
        form_line_obj = self.pool.get('training.form.line')
        form_id = form_obj.search(
            cr, uid, [('flage', '=', False), ('done', '=', False)], context=context)
        if not form_id:
            raise osv.except_osv(_('Error'), _(
                'please ask training managment for help'))
        form_id = form_id[0]
        for data in datas:
            line = {}
            line['emp_id'] = user and user[0] or 0
            line['form_id'] = form_id

            line['suggested_blank'] = [
                (0, 0, {'name': x.name}) for x in data.suggested_blank]
            line['suggested'] = [(4, x.id) for x in data.suggested]

            form_line_obj.create(cr, uid, line, context=context)
            #reload form_id not know the reason
            line['form_id'] = form_id
            if data.inc_emps and user:
                emp_obj = self.pool.get('hr.employee')
                department_obj = self.pool.get('hr.department')
                dep_id = department_obj.search(
                    cr, uid, [('manager_id', 'in', user)], context=context)
                if dep_id:
                    inc_emps_ids = emp_obj.search(
                        cr, uid, [('department_id', 'child_of', dep_id),('id','not in',user)], context=context)

                    for emp in inc_emps_ids:
                        line['emp_id'] = emp
                        form_line_obj.create(cr, uid, line, context=context)
        return True


class training_suggested_blank_wizard(osv.osv_memory):
    _name = "training.suggested.blank.wizard"
    _columns = {
        'name': fields.char('Name'),
        'line_id': fields.many2one('training.wizard', invisible=True, readonly=False),
    }

class training_mail_wizard(osv.osv_memory):

    _name = 'training.mail.wizard'
    _columns = {
        'text': fields.text('Text'),
        'mail': fields.char('mail'),
    }
    _defaults = {
        'mail': 'erptest1@itisalat.ntc.org.sd'
    }
    def send_mail(self, cr, uid, ids, context=None):
        template_obj = self.pool.get('email.template')
        data_obj = self.pool.get('ir.model.data')
        mail_template_id = data_obj.get_object_reference(
            cr, uid, 'hr_ntc_custom', 'email_training_form')
        template_obj.send_mail(cr, uid, mail_template_id[
                               1], ids[0], True, context=context)

class training_search_wizard(osv.osv_memory):

    _name = 'training.search.wizard'
    _columns = {
        'lines_ids': fields.one2many('training.form.line', 'form_id', 'Lines'),
    }

    def _default_lines(self, cr, uid, context=None):
        search = context.get('search',False)
        active_ids = context.get('active_ids',[])
        line_obj = self.pool.get("training.form.line")
        blank_obj = self.pool.get("training.suggested.blank")
        lines_ids = line_obj.search(cr, uid, [('form_id','in',active_ids)],context=context)
        blank_ids = blank_obj.search(cr, uid, [('line_id','in',lines_ids), ('name','like',search)],context=context)
        lines_ids = blank_obj.read(cr, uid, blank_ids, ['line_id'],context=context)
        lines_ids = [i['line_id'][0] for i in lines_ids]
        lines_ids = [(4, id) for id in lines_ids]
        return lines_ids
    _defaults = {
        'lines_ids': _default_lines,
    }

    def save(self, cr, uid, ids, context=None):
        lines_ids = context.get('lines_ids',[])
        #active_ids = context.get('active_ids',[])
        #line_obj = self.pool.get("training.form.line")
        #blank_obj = self.pool.get("training.suggested.blank")
        return {}

