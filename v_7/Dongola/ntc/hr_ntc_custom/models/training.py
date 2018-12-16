# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
############################################################################
from openerp.osv import fields, osv, orm
from tools.translate import _
from datetime import date, datetime, timedelta
import openerp.addons.decimal_precision as dp
import time


class training_form(osv.Model):

    _name = "training.form"
    _rec_name = "date"
    _columns = {
        'state': fields.selection([('draft', 'Draft'), ('t_manager', 'Training Manager'), ('hr_manager', 'HR Manager'), ('haa_manager', 'Finicial and Human Resources Manager'), ('confirmed', 'Confirmed')], 'State'),
        'lines_ids': fields.one2many('training.form.line', 'form_id', 'Lines'),
        'flage': fields.boolean('flage', invisible=True),

        'checkeddm': fields.boolean('checked department manager', invisible=True),

        'checkedgdm': fields.boolean('checked general department manager', invisible=True),

        'done': fields.boolean('done', invisible=True),

        'mail': fields.char('Mail'),

        'department_ids': fields.one2many('training.form.departments', 'form_id', 'Lines', readonly=False),

        'search': fields.char('search word'),

        'direct':fields.boolean('my employees',),
        'date':fields.char('Date'),
    }
    _defaults = {
        'state': 'draft',
        'mail': 'erptest1@itisalat.ntc.org.sd',
        'checkeddm': True,
        'checkedgdm': True,
        'date':int(time.strftime('%Y')),
    }

    

    def send_mail(self, cr, uid, ids, context=None):
        template_obj = self.pool.get('email.template')
        data_obj = self.pool.get('ir.model.data')
        mail_template_id = data_obj.get_object_reference(
            cr, uid, 'hr_ntc_custom', 'email_training_form')
        template_obj.send_mail(cr, uid, mail_template_id[
                               1], ids[0], True, context=context)

    def read(self, cr, user, ids, fields=None, context=None, load='_classic_read'):
        res = super(training_form, self).read(cr=cr, user=user,
                                              ids=ids, fields=fields, context=context, load=load)
        line_obj = self.pool.get("training.form.line")
        for rec in res:
            lines_ids = rec.get('lines_ids', [])
            states = line_obj.read(cr, user, lines_ids, [
                                   'state'], context=context)
            draft = filter(lambda x: x['state'] == 'draft', states)
            confirmed = filter(lambda x: x['state'] == 'confirmed', states)
            approved = filter(lambda x: x['state'] == 'approved', states)
            done = filter(lambda x: x['state'] == 'done', states)
            rec['checkeddm'] = True
            rec['checkedgdm'] = True
            rec['done'] = True
            if len(states) == len(draft):
                rec['checkeddm'] = False
                rec['checkedgdm'] = True            
                rec['done'] = True

            if len(states) == len(confirmed):
                rec['checkeddm'] = True
                rec['checkedgdm'] = False
                rec['done'] = True
            if len(states) == len(approved):
                rec['checkeddm'] = True
                rec['checkedgdm'] = True
                rec['done'] = False
            if len(states) == len(done):
                rec['checkeddm'] = True
                rec['checkedgdm'] = True
                rec['done'] = True
        return res

    def d_manager(self, cr, uid, ids, context=None):
        if context and 'lines_ids' in context:
            lines_ids = [x[1] for x in context.get('lines_ids', [])]
            self.pool.get('training.form.line').write(
                cr, uid, lines_ids, {'state': 'confirmed'})
            self.write(cr, uid, ids, {'checkeddm': True}, context=context)
            department_rel_obj = self.pool.get('training.form.departments')

            department_obj = self.pool.get('hr.department')

            users_obj = self.pool.get('res.users')

            emp_id = users_obj.read(
                cr, uid, uid, ['employee_ids'], context=context)

            dep_id = department_obj.search(
                cr, uid, [('manager_id', 'in', emp_id['employee_ids'])], context=context)

            department_rel_ids = department_rel_obj.search(
                cr, uid, [('ener_form_id', 'in', ids), ('department_id', 'in', dep_id)])

            department_rel_obj.write(
                cr, uid, department_rel_ids, {'checked': True})

    def t_manager(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 't_manager', 'flage': True,
                                  'checkeddm': True, 'checkedgdm': True, 'done': True})

    def hr_manager(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'hr_manager', 'flage': True,
                                  'checkeddm': True, 'checkedgdm': True, 'done': True})

    def haa_manager(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'haa_manager', 'flage': True,
                                  'checkeddm': True, 'checkedgdm': True, 'done': True})

    def gd_manager(self, cr, uid, ids, context=None):
        if context and 'lines_ids' in context:
            lines_ids = [x[1] for x in context.get('lines_ids', [])]
            self.pool.get('training.form.line').write(
                cr, uid, lines_ids, {'state': 'approved'})
            self.write(cr, uid, ids, {'checkedgdm': True}, context=context)
            department_rel_obj = self.pool.get('training.form.departments')

            department_obj = self.pool.get('hr.department')

            users_obj = self.pool.get('res.users')

            emp_id = users_obj.read(
                cr, uid, uid, ['employee_ids'], context=context)

            dep_id = department_obj.search(
                cr, uid, [('manager_id', 'in', emp_id['employee_ids'])], context=context)

            department_rel_ids = department_rel_obj.search(
                cr, uid, [('form_id', 'in', ids), ('department_id', 'in', dep_id)])

            department_rel_obj.write(
                cr, uid, department_rel_ids, {'checked': True})

            self.browse(cr, uid, ids, context=context)
            cr.execute(
                'SELECT state FROM suggested_attendance_line WHERE report_id = %s ', (ids[0], ))
            res = cr.dictfetchall()
            approved = filter(lambda x: x['state'] == 'approved', res)
            if len(res) == len(approved):
                self.write(cr, uid, ids, {
                           'done': True}, context=context)
        return True

    def gm_confirm(self, cr, uid, ids, context=None):
        lines_obj = self.pool.get('training.form.line')
        lines_ids = lines_obj.search(
            cr, uid, [('form_id', 'in', ids), ('state', 'not in', ['approved'])])

        if lines_ids:
            raise osv.except_osv(_('Error'), _(
                'you have to confirm all details'))
        self.write(cr, uid, ids, {'state': 'confirmed', 'flage': True,
                                  'checkeddm': True, 'checkedgdm': True, 'done': True})

        lines_ids = lines_obj.search(
            cr, uid, [('form_id', 'in', ids)], context=context)

        lines = lines_obj.browse(cr, uid, lines_ids, context=context)

        rows = {}
        deps = {}
        for line in lines:
            for suggested in line.suggested:
                rows[suggested.id] = rows.get(suggested.id, [])
                rows[suggested.id].append(
                    (0, 0, {'employee_id': line.emp_id.id, 'department_id': line.dep_id.id}))

                deps[(suggested.id, line.dep_id.id)] = deps.get(
                    (suggested.id, line.dep_id.id), 0)
                deps[(suggested.id, line.dep_id.id)] += 1

        suggested_obj = self.pool.get('hr.employee.training.suggested')
        for row in rows.keys():
            try:
                cr_deps = filter(lambda x: x[0] == row, deps.keys())
                cr_deps = [
                    (0, 0, {'department_id': x[1], 'candidate_no':deps[x]}) for x in cr_deps]
                #row
                new_row = suggested_obj.create(cr, uid, {'course_id':row, 
                'line_ids': rows[row], 'department_ids': cr_deps, 'type': 'hr.approved.course'}, context=context)
            except:
                pass
            '''suggested_obj.write(cr, uid, new_row, {'line_ids': rows[
                                row], 'department_ids': cr_deps, 'type': 'hr.approved.course'}, context=context)'''
        #raise osv.except_osv(_('Error'), _('you have to confirm all details'))

    def create(self, cr, uid, vals, context=None):
        uid = 1
        id = super(training_form, self).create(cr, uid, vals, context=context)

        department_obj = self.pool.get('hr.department')
        department_cat_obj = self.pool.get('hr.department.cat')

        department_cat_ids = department_cat_obj.search(
            cr, uid, [], context=context)
        departments_cats = department_cat_obj.read(cr, uid, department_cat_ids, [
                                                   'category_type'], context=context)
        cats = {x['id']: {'category_type': x['category_type']}
                for x in departments_cats}

        department_ids = department_obj.search(cr, uid, [], context=context)

        departments = department_obj.read(cr, uid, department_ids, [
                                          'parent_id', 'cat_id'], context=context)

        departments = [{'id': x['id'], 'parent_id':x['parent_id'] and x['parent_id'][0], 'cat_id': (
            x['cat_id'] and x['cat_id'][0] in cats) and cats[x['cat_id'][0]]['category_type'] or False} for x in departments]

        parents = [x['parent_id'] for x in departments]

        parents = list(set(parents))

        parents_dict = {x: 0 for x in parents}

        department_rel_obj = self.pool.get('training.form.departments')

        for i in parents:
            new_id = department_rel_obj.create(cr, uid, {'department_id': i})
            parents_dict[i] = new_id

        for item in departments:
            print "....................i",item
            # relatio with the form
            relation = 'ener_form_id'

            # parent of the current dep
            parent = parents_dict[item['parent_id']]
            if item['cat_id'] == 'general_dep':
                relation = 'form_id'
            if item['id'] in parents:
                department_rel_obj.write(cr, uid, parents_dict[item['id']], {
                                         'parent': parent, relation: id})
            else:
                department_rel_obj.create(cr, uid, {'department_id': item[
                                          'id'], 'parent': parent, relation: id})

        return id


class training_form_line(osv.Model):
    _name = "training.form.line"
    _rec_name = "name"
    _columns = {
        'emp_id': fields.many2one('hr.employee', 'Employee', readonly=False, invisible=True),
        'name': fields.related('emp_id', 'name_related', string='name',  type="char",  readonly=True),
        'dep_name': fields.char('department name', readonly=True),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('approved', 'Approved')], 'State', readonly=True),
        'form_id': fields.many2one('training.form', invisible=True, readonly=True),
        'suggested_blank': fields.one2many('training.suggested.blank', 'line_id', string="new"),
        'suggested': fields.many2many('hr.training.course', 'training_line_course_rel', string='Training Suggested'),
        'dep_id': fields.many2one('hr.department', 'Department', readonly=False),
        'reason': fields.text('Reason'),
    }
    _defaults = {
        'state': 'draft'
    }
    def d_manager(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'confirmed'}, context=context)
    
    def gd_manager(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'approved'}, context=context)
    def write(self, cr, uid, ids, vals, context=None):
        if 'form_id' in vals:
            del vals['form_id']
        reason = False
        if 'reason' in vals:
            reason = vals['reason']

        emp_dict_list = self.read(cr, uid,ids,['emp_id'], context=context)

        to_return = super(training_form_line, self).write(cr, uid, ids, vals, context=context)

        user_obj = self.pool.get('res.users')
        if user_obj.has_group(cr, uid, 'base.group_training_manager'):
            emp_id_list = [emp_dict['emp_id'][0] for emp_dict in emp_dict_list]

            hr_employee_obj = self.pool.get('hr.employee')
            hr_employee_dict = {i.id:i for i in hr_employee_obj.browse(cr, uid, emp_id_list, context=context)}

            department_cat_obj = self.pool.get('hr.department.cat')

            department_cat_ids = department_cat_obj.search(
                cr, uid, [('category_type','=','general_dep')], context=context)


            hr_department_obj = self.pool.get('hr.department')
            department_id_list = hr_department_obj.search(cr, uid, [('cat_id','in',department_cat_ids)], context=context)
            hr_department_dict = {i.manager_id and i.manager_id.user_id.id:i.manager_id and i.manager_id.user_id.email or '' for i in hr_department_obj.browse(cr, uid, department_id_list, context=context)}

            mail_dict = []
            for emp_dict in emp_dict_list:
                emp_name = emp_dict['emp_id'][1]
                rec_id = emp_dict['id']

                for manager in hr_department_dict.keys():
                    if manager:
                        try:
                            temp = self.read(cr, manager,rec_id,[], context=context)
                            if temp:

                                mail_dict.append({
                                    'mail':hr_department_dict[manager],
                                    'text':emp_name+"       "+reason,
                                })
                        except:
                            pass

            mail_obj = self.pool.get('training.mail.wizard')
            for mail in mail_dict:
                mail['mail'] = 'erptest1@itisalat.ntc.org.sd'
                new_id = mail_obj.create(cr, uid, mail, context=context)
                mail_obj.browse(cr, uid, new_id, context=context).send_mail()
        return to_return

    def create(self, cr, uid, vals, context=None):
        if 'emp_id' in vals:
            department = self.pool.get('hr.employee').read(
                cr, uid, vals['emp_id'], ['department_id'], context=context)
            vals['dep_id'] = department['department_id'][0]
            vals['dep_name'] = department['department_id'][1]

        if 'form_id' in vals and 'emp_id' in vals:
            # check for line with same employee and form_id
            ex_line = self.search(
                cr, uid, [('form_id', '=', vals['form_id']), ('emp_id', '=', vals['emp_id'])])
            if ex_line:
                return self.write(cr, uid, ex_line[0], vals, context=context)

        return super(training_form_line, self).create(cr, uid, vals, context=context)


class training_form_departments(osv.Model):
    _name = "training.form.departments"
    _rec_name = "department_id"
    _columns = {
        'department_id': fields.many2one('hr.department', 'Department', readonly=False),
        'name': fields.related('department_id', 'name', string='name',  type="char",  readonly=True),
        'parent': fields.many2one('training.form.departments', invisible=True, readonly=False),
        'lines_ids': fields.one2many('training.form.departments', 'parent', 'Lines'),
        'checked': fields.boolean('checked', readonly=False),
        'form_id': fields.many2one('training.form', invisible=True, readonly=True),
        'ener_form_id': fields.many2one('training.form', invisible=True, readonly=True),
    }


class training_suggested_blank(osv.Model):
    _name = "training.suggested.blank"
    _columns = {
        'name': fields.char('Name'),
        'line_id': fields.many2one('training.form.line', invisible=True, readonly=False),
    }

class training_eva_line(osv.Model):
    _name = "training.eva.line"
    _columns = {
        'name': fields.char('Name'),
        'value': fields.selection(string='Value',selection= [('excelant', 'Excelant'), ('v_good', 'Vary Good'), ('good', 'Good'), ('accepted', 'Accepted'), ('poor', 'Poor')]),
        'eva': fields.many2one('training.eva', invisible=True, readonly=False),
        
        
    }

class training_eva(osv.Model):
    _name = "training.eva"
    _rec_name="template_name"
    _columns = {
        'emp_id': fields.many2one('hr.employee', 'Employee'),
        'name': fields.char('Name'),
        'place': fields.char('place'),
        'trainer': fields.char('trainer'),
        'from': fields.char('from'),
        'to': fields.char('to'),
        'eva_lines': fields.one2many('training.eva.line', 'eva', 'Lines'),
        'template': fields.boolean('Template'),
        'template_name': fields.char('Template'),
        'course_id': fields.many2one('hr.employee.training.approved', 'Course'),
        'type': fields.selection(string='type',selection= [('regular', 'Regular'), ('irregular', 'Irregular')]),
        'comments': fields.text('Comments'),
        
    }
    _defaults = {
        'type': 'regular'
    }

#----------------------------------------
# Employee Training
#----------------------------------------
class hr_employee_training(osv.Model):

    _name = "hr.employee.training"
    _inherit = "hr.employee.training"

    _columns = {
        'plan_id' : fields.many2one('hr.training.plan', 'Plan', required=False, readonly=True, ondelete='restrict',
                                    states={'draft':[('readonly', False)], 'edit':[('readonly', False)]}),
    }

class hr_employee_training_approved_inherit(osv.Model):

    _name = "hr.employee.training.approved"
    _inherit = "hr.employee.training.approved"

    _columns = {
        'plan_id' : fields.many2one('hr.training.plan', 'Plan', required=False, readonly=True, ondelete='restrict',
                                    states={'draft':[('readonly', False)], 'edit':[('readonly', False)]}),
    }

#----------------------------------------
# Employee Training
#----------------------------------------
class hr_employee_training_department(osv.Model):

    _name = "hr.employee.training.department"
    _inherit = "hr.employee.training.department"

    _description = "Department's Training Request"

    def _check_dept_percentage(self, cr, uid, ids, context=None):
        """
        Method that checks if department's candidates exceeds the specified percentage 
        in training plan or not.

        @return: Boolean True or False
        """ 
        '''for d in self.browse(cr, uid, ids, context=context):
            if d.employee_training_id.plan_id.percentage == 0:
                continue
            candidates = self.read_group(cr, uid, [('employee_training_id.plan_id', '=', d.employee_training_id.plan_id.id), ('department_id', '=', d.department_id.id)],
                                  ['type', 'candidate_no'], ['type'], context=context)
            for c in candidates:
                if not d.department_id.member_ids or c['candidate_no'] * 100 / len(d.department_id.member_ids) > d.employee_training_id.plan_id.percentage:
                    return False'''
        return True

    _constraints = [
        (_check_dept_percentage, _('The total number of department candidates shouldn\'t exceed the specified percentage in training plan!'), []),
    ]


class hr_employee_training_line(osv.Model):

    _name = "hr.employee.training.line"
    _inherit = "hr.employee.training.line"

    def _compute(self, cr, uid, ids , final_amount, arg=None , context=None) :
        """
        Method that computes training enrich for employees attend specific course.

        @return: Dictionary of data
        """
        payroll_pool = self.pool.get('payroll')
        enrich_state_pool = self.pool.get('emp.states')
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            amount = line.days and (line.supervisor and line.supervision_amount or \
                        line.training_employee_id.enrich_id.enrich_type == '3' and line.training_employee_id.enrich_id.fixed_value) or 0
            final_amount = (line.supervisor or line.training_employee_id.enrich_id.enrich_type == '3') and amount or 0
            total_days = self._get_days(cr, uid, {'start_date': line.training_employee_id.start_date, 'end_date': line.training_employee_id.end_date})
            if not line.supervisor and line.training_employee_id.enrich_id.enrich_type == '1':
                enrich_state_ids = enrich_state_pool.search(cr, uid, [('company_id', '=', line.employee_id.company_id.id) , ('name', '=', line.training_employee_id.enrich_id.id)])
                emp_enrich_state = enrich_state_pool.browse(cr, uid, enrich_state_ids, context=context)
                amount = (emp_enrich_state and emp_enrich_state[0].amount or 0.0) * total_days
                final_amount = (emp_enrich_state and emp_enrich_state[0].amount or 0.0) * line.days
            if not line.supervisor and line.training_employee_id.enrich_id.enrich_type == '2':
                if line.training_employee_id.enrich_id.allowance_id:
                        allow_deduct_dict = payroll_pool.allowances_deductions_calculation(cr, uid, line.training_employee_id.start_date, line.employee_id, {}, [line.training_employee_id.enrich_id.allowance_id.id], False, [])
                        amount = allow_deduct_dict['total_allow'] * total_days
                        final_amount = allow_deduct_dict['total_allow'] * line.days
            res.update({line.id: {'amount': amount, 'final_amount': final_amount}})
        return res

    '''_columns = {
        'final_amount': fields.function(_compute, method=True , multi='amount', string='Final Amount',
                        digits_compute=dp.get_precision('Account')),
    }'''

    