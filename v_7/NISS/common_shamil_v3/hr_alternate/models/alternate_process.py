# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from mx import DateTime
import time
from datetime import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import netsvc
import openerp.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta
import calendar
from openerp.addons.account_voucher.account_voucher import resolve_o2m_operations


class hr_alternative_process_line(osv.Model):
    _name = "hr.alternative.process.line"

    _description = "Hr Alternative Process"

    _columns = {
        'employee_id': fields.many2one('hr.employee', string='Employee'),
        'degree': fields.related('employee_id', 'degree_id', string="Degree", type="many2one", relation="hr.salary.degree"),
        'alternative_process_id': fields.many2one('hr.alternative.process', string='Process'),
        'date': fields.date('Date'),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], 'State'),
        'weekday': fields.selection([('Sunday', 'Sunday'), ('Monday', 'Monday'),
                                     ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
                                     ('Thursday', 'Thursday'), ('Friday', 'Friday'),
                                     ('Saturday', 'Saturday')], 'Weekday'),
        'alternative_setting_id': fields.related('alternative_process_id', 'alternative_setting_id', string='Category' ,type='many2one',relation='hr.alternative.setting'),
    }
    _defaults = {
        'state': 'draft',
    }

    _sql_constraints = [
        ('hr_alternative_setting_name_uniqe', 'unique(alternative_process_id,date)',
         'you must have one employee in a day')
    ]

    def confirm(self,  cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if not rec.employee_id:
                raise osv.except_osv(
                    _(''), _("con not confirm a day without employee"))
        return self.write(cr, uid, ids, {'state': 'confirmed'})

    def draft(self,  cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'})


class hr_alternative_process(osv.Model):
    _name = "hr.alternative.process"

    _description = "Hr Alternative Process"

    _columns = {
        'sequance' :fields.char('Sequance'),
        'number' :fields.char('The number'),
        'alternative_setting_id': fields.many2one('hr.alternative.setting', string='Category'),
        'degrees_ids': fields.related('alternative_setting_id', 'degrees_ids', string="Degrees", type="many2many", relation="hr.salary.degree"),
        'date_from': fields.date('Date Form'),
        'date_to': fields.date('Date To'),
        'lines_ids': fields.one2many('hr.alternative.process.line', 'alternative_process_id', string='Lines'),
        'alternative1': fields.many2one('hr.employee', string='alternative One'),
        'alternative2': fields.many2one('hr.employee', string='alternative Two'),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], 'State'),
        'alternative_process_collective_id': fields.many2one('hr.alternative.process.collective', string='Process Collective'),
        'company_id': fields.many2one('res.company','company'),
        'report_header' :fields.text('Report Header'),
        'report_alerts': fields.text(string='Report Alerts'),
    }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company
        
    _defaults = {
        'state': 'draft',
        'company_id' : _default_company,
    }

    def create(self, cr, uid, data, context=None):
        """
        To set number
        """
        seq = self.pool.get('ir.sequence').next_by_code(cr, uid, 'hr.alternative.process')
        data['sequance'] = seq
        if not seq:
            raise  osv.except_osv(_('Warning'), _('No sequence defined!\nPleas contact administartor to configue sequence with code \'hr.alternative.process\'') )

        return super(hr_alternative_process, self).create(cr, uid, data, context=context)

    def onchange_alternative_setting_id(self, cr, uid, ids, alternative_setting_id, context=None):
        res={}
        if alternative_setting_id:
            setting = self.pool.get('hr.alternative.setting').browse(cr, uid, [alternative_setting_id])[0]
            res['value']={'report_alerts': setting.report_alerts}
        return res

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            header=rec.report_header.strip()
            alerts=rec.report_alerts.strip()
            number=rec.number.strip()
            if not header:
                raise osv.except_osv(_('ValidateError'),
                                     _("Report Header must not be spaces"))
            if not alerts:
                raise osv.except_osv(_('ValidateError'),
                                     _("Report Alerts must not be spaces"))
            if not number:
                raise osv.except_osv(_('ValidateError'),
                                     _("The number must not be spaces"))
        return True
    _constraints = [
        (_check_spaces, '', [])
    ]

    def _check_date(self, cr, uid, ids, context=None):
        for act in self.browse(cr, uid, ids, context):
            if datetime.strptime(act.date_from, "%Y-%m-%d") > datetime.strptime(act.date_to, "%Y-%m-%d"):
                raise osv.except_osv(
                    _(''), _("date from can not be after date to"))
        return True

    def get_date(self,str):
        return datetime.strptime(str, "%Y-%m-%d")

    def _check_dates(self, cr, uid, ids, context=None):
        """
        Check the value of date_from if greater than date_to or not.

        @return: Boolean of True or False
        """
        for act in self.browse(cr, uid, ids, context):
            date_from = self.get_date(act.date_from)
            date_to = self.get_date(act.date_to)
            previous_ids = self.search(cr, uid, [('id','!=',act.id), ('alternative_setting_id','=',act.alternative_setting_id.id)],context=context)
            dates = self.read(cr, uid, previous_ids, ['date_from','date_to'], context=context)

            dates = [{'date_from':self.get_date(x['date_from']),'date_to':self.get_date(x['date_to'])} for x in dates]
            for date in dates:
                case0 = date['date_from'] >= date_from and date['date_to'] <= date_to

                case1 = date['date_from'] <= date_from and date['date_to'] >= date_to

                case2 = date['date_from'] <= date_from and date_from <= date['date_to'] 

                case3 = date_from <= date['date_from'] and date['date_from'] <= date_to
                
                if case0 or case1 or case2 or case3:
                    raise osv.except_osv(_('Error'), _("THIS RANGE OF DATE HAVE BEEN FETCHED BEFORE"))
        return True

    _constraints = [
        (_check_date, _(''), ['date_from', 'date_to']),
        (_check_dates, _(''), ['date_from','date_to']),
    ]

    
    

    def copy(self, cr, uid, id, default=None, context=None):
        """
        @return: super duplicate() method
        """
        raise osv.except_osv(_('Invalid Action Error'),
                             _('can not duplicate this record'))
        return super(hr_alternative_process, self).copy(cr, uid, id, default, context)

    def unlink(self, cr, uid, ids, context=None):
        """
        @return: super unlink() method
        """

        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state == 'confirmed':
                raise osv.except_osv(_('Invalid Action Error'),
                                     _('can not delete a record in confirmed state'))
            for line in rec.lines_ids:
                line.unlink()
        return super(hr_alternative_process, self).unlink(cr, uid, ids, context=context)

    def confirm(self,  cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            for line in rec.lines_ids:
                if line.state == 'confirmed':
                    continue
                line.confirm()
        return self.write(cr, uid, ids, {'state': 'confirmed'})

    def draft(self,  cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            for line in rec.lines_ids:
                if line.state == 'draft':
                    continue
                line.draft()
        return self.write(cr, uid, ids, {'state': 'draft'})

    def name_get(self, cr, uid, ids, context=None):
        return ids and [(item.id, "%s-%s-%s" % (item.alternative_setting_id.name, item.date_from, item.date_to)) for item in self.browse(cr, uid, ids, context=context)] or []
    
    def get_unavailable(self, cr, uid, ids, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context=context):
            res[rec.id] = []
            cr.execute(
                ''' select employee_id from hr_employee_illness where 
                (date>=%s and date<=%s) or 
                (end_date>=%s and end_date<=%s) 
                ''', (rec.date_from,rec.date_to,rec.date_from,rec.date_to))
            history = cr.dictfetchall()
            history = [x['employee_id'] for x in history]
            res[rec.id] += history

            cr.execute(
                ''' select employee_id from hr_employee_mission_line where 
                (start_date>=%s and start_date<=%s) or 
                (end_date>=%s and end_date<=%s) 
                ''', (rec.date_from,rec.date_to,rec.date_from,rec.date_to))
            history = cr.dictfetchall()
            history = [x['employee_id'] for x in history]
            res[rec.id] += history

            cr.execute(
                ''' select employee_id from hr_holidays where 
                (date_from>=%s and date_from<=%s) or 
                (date_to>=%s and date_to<=%s) 
                ''', (rec.date_from,rec.date_to,rec.date_from,rec.date_to))
            history = cr.dictfetchall()
            history = [x['employee_id'] for x in history]
            res[rec.id] += history

            cr.execute(
                ''' select employee_id from hr_unlock where 
                (start_date>=%s and start_date<=%s) or 
                (end_date>=%s and end_date<=%s) 
                ''', (rec.date_from,rec.date_to,rec.date_from,rec.date_to))
            history = cr.dictfetchall()
            history = [x['employee_id'] for x in history]
            res[rec.id] += history

            cr.execute(
                ''' select employee_id from hr_holidays_absence where 
                (date_from>=%s and date_from<=%s) or 
                (date_to>=%s and date_to<=%s) 
                ''', (rec.date_from,rec.date_to,rec.date_from,rec.date_to))
            history = cr.dictfetchall()
            history = [x['employee_id'] for x in history]
            res[rec.id] += history

            cr.execute(
                ''' select employee_id from hr_military_training where 
                (start_date>=%s and start_date<=%s) or 
                (end_date>=%s and end_date<=%s) 
                ''', (rec.date_from,rec.date_to,rec.date_from,rec.date_to))
            history = cr.dictfetchall()
            history = [x['employee_id'] for x in history]
            res[rec.id] += history
        
        return res




    def fetch(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('hr.alternative.process.line')
        for rec in self.browse(cr, uid, ids, context=context):
            un_ables = rec.get_unavailable()
            un_ables = un_ables[rec.id]
            line_obj.unlink(cr, uid, [x.id for x in rec.lines_ids])
            rec.write({'alternative1': False, 'alternative2': False})
            degrees_ids = [
                x.id for x in rec.alternative_setting_id.degrees_ids]
            degrees_ids += degrees_ids
            degrees_ids = tuple(degrees_ids)

            departments_ids = [
                x.id for x in rec.alternative_setting_id.departments_ids]
            departments_ids += departments_ids
            departments_ids = tuple(departments_ids)

            ex_employees_ids = [
                x.id for x in rec.alternative_setting_id.employees_ids]
            ex_employees_ids += ex_employees_ids + un_ables
            ex_employees_ids = tuple(ex_employees_ids)

            if not departments_ids:
                departments_ids = (0,0)

            if not ex_employees_ids:
                ex_employees_ids = (0,0)

            cr.execute(
                ''' Select emp.id,(SELECT MAX(date) as max_date
                    FROM hr_alternative_process_line
                    WHERE employee_id=emp.id and state='confirmed')date
                    from hr_employee emp
                    where emp.degree_id in %s 
                    and emp.department_id not in %s
                    and emp.state = 'approved' 
                    and emp.gender='male' 
                    and emp.payroll_state = 'khartoum' 
                    and emp.id not in %s
                    order by date NULLS LAST''', (degrees_ids,departments_ids,ex_employees_ids))
            history = cr.dictfetchall()
            date_from = datetime.strptime(rec.date_from, "%Y-%m-%d")
            date_to = datetime.strptime(rec.date_to, "%Y-%m-%d")
            while date_from <= date_to:
                employee_id = False
                try:
                    employee_id = history.pop()['id']
                except:
                    pass

                line_obj.create(
                    cr, uid, {'date': date_from, 'alternative_process_id': rec.id, 'employee_id': employee_id, 'weekday':calendar.day_name[date_from.weekday()]})
                date_from += relativedelta(days=1)
            try:
                employee_id = history.pop()['id']
                rec.write({'alternative1': employee_id})
                employee_id = history.pop()['id']
                rec.write({'alternative2': employee_id})
            except:
                pass


class hr_alternative_process_collective(osv.Model):
    _name = "hr.alternative.process.collective"

    _description = "Hr Alternative Process Collective"

    _columns = {
        'date_from': fields.date('Date Form'),
        'date_to': fields.date('Date To'),
        'lines_ids': fields.one2many('hr.alternative.process', 'alternative_process_collective_id', string='Lines'),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], 'State'),
        'company_id': fields.many2one('res.company','company'),
    }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company
        
    _defaults = {
        'state': 'draft',
        'company_id' : _default_company,
    }

    def _check_date(self, cr, uid, ids, context=None):
        for act in self.browse(cr, uid, ids, context):
            if datetime.strptime(act.date_from, "%Y-%m-%d") > datetime.strptime(act.date_to, "%Y-%m-%d"):
                raise osv.except_osv(
                    _(''), _("date from can not be after date to"))
        return True
    
    def get_date(self,str):
        return datetime.strptime(str, "%Y-%m-%d")

    def _check_dates(self, cr, uid, ids, context=None):
        """
        Check the value of date_from if greater than date_to or not.

        @return: Boolean of True or False
        """
        for act in self.browse(cr, uid, ids, context):
            date_from = self.get_date(act.date_from)
            date_to = self.get_date(act.date_to)
            previous_ids = self.search(cr, uid, [('id','!=',act.id)],context=context)
            dates = self.read(cr, uid, previous_ids, ['date_from','date_to'], context=context)

            dates = [{'date_from':self.get_date(x['date_from']),'date_to':self.get_date(x['date_to'])} for x in dates]
            for date in dates:
                case0 = date['date_from'] >= date_from and date['date_to'] <= date_to

                case1 = date['date_from'] <= date_from and date['date_to'] >= date_to

                case2 = date['date_from'] <= date_from and date_from <= date['date_to'] 

                case3 = date_from <= date['date_from'] and date['date_from'] <= date_to
                
                if case0 or case1 or case2 or case3:
                    raise osv.except_osv(_('Error'), _("THIS RANGE OF DATE HAVE BEEN FETCHED BEFORE"))
        return True

    _constraints = [
        (_check_date, _(''), ['date_from', 'date_to']),
        (_check_dates, _(''), ['date_from','date_to']),
    ]

    def write(self, cr, uid, ids, vals, context=None):
        if 'date_from' in vals or 'date_to' in vals:
            for rec in self.browse(cr, uid, ids, context=context):
                for line in rec.lines_ids:
                    line.unlink()
        return super(hr_alternative_process_collective, self).write(cr, uid, ids, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        """
        @return: super unlink() method
        """

        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state == 'confirmed':
                raise osv.except_osv(_('Invalid Action Error'),
                                     _('can not delete a record in confirmed state'))
            for line in rec.lines_ids:
                line.unlink()
        return super(hr_alternative_process_collective, self).unlink(cr, uid, ids, context=context)

    def confirm(self,  cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            for line in rec.lines_ids:
                if line.state == 'confirmed':
                    continue
                line.confirm()
        return self.write(cr, uid, ids, {'state': 'confirmed'})

    def draft(self,  cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            for line in rec.lines_ids:
                if line.state == 'draft':
                    continue
                line.draft()
        return self.write(cr, uid, ids, {'state': 'draft'})

    def copy(self, cr, uid, id, default=None, context=None):
        """
        @return: super duplicate() method
        """
        raise osv.except_osv(_('Invalid Action Error'),
                             _('can not duplicate this record'))
        return super(hr_alternative_process_collective, self).copy(cr, uid, id, default, context)

    def name_get(self, cr, uid, ids, context=None):
        return ids and [(item.id, "%s-%s" % (item.date_from, item.date_to)) for item in self.browse(cr, uid, ids, context=context)] or []

    def fetch(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('hr.alternative.process')
        setting_obj = self.pool.get('hr.alternative.setting')
        created_lines = []
        for rec in self.browse(cr, uid, ids, context=context):
            line_obj.unlink(cr, uid, [x.id for x in rec.lines_ids])
            for setting_id in setting_obj.search(cr, uid, [], context=context):
                new_id = line_obj.create(
                    cr, uid, {'date_from': rec.date_from, 'date_to': rec.date_to, 'alternative_process_collective_id': rec.id, 'alternative_setting_id': setting_id})
                created_lines.append(new_id)
        return line_obj.fetch(cr, uid, created_lines, context=context)


#----------------------------------------
# Employee (Inherit) 
# Adding new fields
#----------------------------------------
class hr_employee(osv.Model):

    _inherit = "hr.employee"

    def get_date(self,str):
        return datetime.strptime(str, "%Y-%m-%d")


    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        """
        Method that overwrites name_search method Search for employee (only employees 
        that requested trainings) and their display name.

        @param name: Object name to search
        @param args: List of tuples specifying search criteria
        @param operator: Operator for search criterion
        @param limit: Max number of records to return
        @return: Super name_search method 
        """
        if context is None:
            context = {}
        if 'emp_hours' in context:
            emp_ids = resolve_o2m_operations(cr, uid, self.pool.get('emp.luggage_transfer.hours'),
                                              context.get('emp_hours'), ["employee"], context)
            args.append(('id', 'not in', [isinstance(d['employee'], tuple) and d['employee'][0] or d['employee'] for d in emp_ids]))
        if 'mission_line' in context:
            emp_ids = resolve_o2m_operations(cr, uid, self.pool.get('hr.employee.mission.line'),
                                              context.get('mission_line'), ["employee_id"], context)
            args.append(('id', 'not in', [isinstance(d['employee_id'], tuple) and d['employee_id'][0] or d['employee_id'] for d in emp_ids]))
        
        if 'illness' in context:
            emp_ids = resolve_o2m_operations(cr, uid, self.pool.get('hr.employee.illness'),
                                              context.get('illness'), ["employee_id"], context)
            args.append(('id', 'not in', [isinstance(d['employee_id'], tuple) and d['employee_id'][0] or d['employee_id'] for d in emp_ids]))
        

        if 'same' in context:
            emp_ids = resolve_o2m_operations(cr, uid, self.pool.get('hr.employee.mission.line'),
                                              context.get('same'), ["employee_id"], context)
            args.append(('id', 'in', [isinstance(d['employee_id'], tuple) and d['employee_id'][0] or d['employee_id'] for d in emp_ids]))
        
        
        if 'alternative_setting_id' in context:
            old_ids = super(hr_employee, self).name_search(cr, uid, name, args=args, operator=operator, context={}, limit=limit)

            alternative_setting_id = context.get('alternative_setting_id')
            setting_obj = self.pool.get('hr.alternative.setting')
            alternative_setting_id = setting_obj.browse(cr, uid, alternative_setting_id)
            degrees_ids = [
                x.id for x in alternative_setting_id.degrees_ids]
            degrees_ids += degrees_ids
            degrees_ids = tuple(degrees_ids)

            departments_ids = [
                x.id for x in alternative_setting_id.departments_ids]
            departments_ids += departments_ids
            departments_ids = tuple(departments_ids)

            ex_employees_ids = [
                x.id for x in alternative_setting_id.employees_ids]
            ex_employees_ids += ex_employees_ids
            ex_employees_ids = tuple(ex_employees_ids)


            old_ids_tuple = [x[0] for x in old_ids] + [x[0] for x in old_ids]
            old_ids_tuple = tuple(old_ids_tuple)

            accessed_ids = self.search(cr, uid, [])
            accessed_ids += accessed_ids
            accessed_ids = tuple(accessed_ids)

            if not old_ids_tuple:
                old_ids_tuple = (0,0)
            
            if not departments_ids:
                departments_ids = (0,0)
            cr.execute(
                ''' Select emp.id,(SELECT MAX(date) as max_date
                    FROM hr_alternative_process_line
                    WHERE employee_id=emp.id and state='confirmed')date
                    from hr_employee emp
                    where emp.degree_id in %s 
                    and emp.department_id not in %s 
                    and emp.state = 'approved' 
                    and emp.payroll_state = 'khartoum' 
                    and emp.id in %s 
                    and emp.gender='male' 
                    and emp.id in %s 
                    and emp.id not in %s 
                    order by date NULLS LAST''', (degrees_ids,departments_ids,old_ids_tuple,accessed_ids,ex_employees_ids))
            history = cr.dictfetchall()
            new_ids = []
            while True:
                try:
                    new_ids.append( history.pop()['id'] )
                except:
                    break

            temp = dict(old_ids)
            old_ids = [x for x in old_ids if x[0] in new_ids]
            #new_ids = [x for x in new_ids if x in accessed_ids]
            #print "..........................temp",new_ids
            #print "......................",[(x, temp.get(x,False) ) for x in new_ids]
            #print "......................",sorted(old_ids, key=lambda x :new_ids.index(x[0]))
            return sorted(old_ids, key=lambda x :new_ids.index(x[0]))

        return super(hr_employee, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)


    def search(self, cr, uid, args, offset=0, limit=None, order=None, 
            context=None, count=False):
        """
        Search for records based on a search domain.

        @param args: list of tuples specifying the search domain [('field_name', 'operator', value), ...]. Pass an empty list to match all records.
        @param offset: optional number of results to skip in the returned values (default: 0)
        @param limit: optional max number of records to return (default: **None**)
        @param order: optional columns to sort by (default: self._order=id )
        @param count: optional (default: **False**), if **True**, returns only the number of records matching the criteria, not their ids
        @return: id or list of ids of records matching the criteria
        """
        if context is None:
            context = {}
        if 'alternative_setting_id' in context:
            alternative_setting_id = context.get('alternative_setting_id')
            setting_obj = self.pool.get('hr.alternative.setting')
            alternative_setting_id = setting_obj.browse(cr, uid, alternative_setting_id)
            degrees_ids = [
                x.id for x in alternative_setting_id.degrees_ids]
            degrees_ids += degrees_ids
            degrees_ids = tuple(degrees_ids)

            departments_ids = [
                x.id for x in alternative_setting_id.departments_ids]
            departments_ids += departments_ids
            departments_ids = tuple(departments_ids)

            ex_employees_ids = [
                x.id for x in alternative_setting_id.employees_ids]
            ex_employees_ids += ex_employees_ids
            ex_employees_ids = tuple(ex_employees_ids)

            search_ids = super(hr_employee, self).search(cr, uid, args, offset, limit, order, context={}, count=count)
            search_ids += search_ids
            search_ids = tuple(search_ids)
            if not search_ids:
                search_ids = (0,0)
            
            if not departments_ids:
                departments_ids = (0,0)
            cr.execute(
                ''' Select emp.id,(SELECT MAX(date) as max_date
                    FROM hr_alternative_process_line
                    WHERE employee_id=emp.id and state='confirmed')date
                    from hr_employee emp
                    where emp.degree_id in %s 
                    and emp.department_id not in %s 
                    and emp.state = 'approved' 
                    and emp.payroll_state = 'khartoum' 
                    and emp.id in %s 
                    and emp.gender='male' 
                    and emp.id not in %s 
                    order by date NULLS LAST''', (degrees_ids,departments_ids,search_ids,ex_employees_ids))
            history = cr.dictfetchall()
            new_ids = []
            while True:
                try:
                    new_ids.append( history.pop()['id'] )
                except:
                    break
            #new_ids = list(reversed( new_ids ) )
            # search_ids = super(hr_employee, self).search(cr, uid, args, offset, limit, order, context=context, count=count)
            # new_ids = new_ids[offset:limit]
            # if search_ids:
            #     new_ids = [x for x in new_ids if x in search_ids]
            # return new_ids[offset:limit]
            return new_ids[offset:limit]
        return super(hr_employee, self).search(cr, uid, args, offset, limit, order, context=context, count=count)
