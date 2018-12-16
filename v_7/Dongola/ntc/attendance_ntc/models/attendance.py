# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
############################################################################
from openerp.osv import fields, osv, orm
from tools.translate import _
import urllib2
import json
from datetime import date,datetime,timedelta
from admin_affairs.model.email_serivce import send_mail

class suggested_attendance_exception(osv.Model):
    _name = "suggested.attendance.exception"

    _columns = {
        'emp_id':fields.many2one('hr.employee','Employee'),
        'report_id':fields.many2one('suggested.attendance', invisible=True),
        'added':fields.char('Added'),
    }
class suggested_attendance_line(osv.Model):
    _name = "suggested.attendance.line"
    def unlink(self, cr, uid, ids, context=None):
        if 1 != uid:
            raise osv.except_osv(_('Error'), _('forbidden'))
        super(suggested_attendance_line, self).unlink(cr, uid,ids, context=context)

    def create(self, cr, uid, vals, context=None):
        vals['state']='draft'
        id = super(suggested_attendance_line, self).create(cr, uid, vals, context=context)
        return id
    _columns = {
        'emp_id':fields.many2one('hr.employee','Employee',invisible=True,readonly=True),
        'name':fields.char('Name',readonly=True),
        'department':fields.char('Department',readonly=True),
        'abacense_days':fields.integer('Abacense Days',readonly=True),
        'get_holidays':fields.integer('Holidays',readonly=True),
        'late_days':fields.integer('Late Days',readonly=True),
        'early_out':fields.integer('Early Out',readonly=True),
        'forget_finger_print':fields.integer('forget finger print',readonly=True),
        'extra_work_day':fields.float('extra on work day',readonly=True),
        'extra_off_day':fields.float('extra on off day',readonly=True),
        'period_work_hours':fields.float('period work hours',readonly=True),
        'abacense_hours':fields.float('abacense hours',readonly=True),
        'forget_finger_print_hours':fields.float('forget finger print hours',readonly=True),
        'late_hours':fields.float('late hours',readonly=True),
        'training':fields.float('training',readonly=True),
        'earned':fields.float('earned',readonly=True),
        'percent':fields.float('percent',readonly=True),
        'added':fields.float('added'),
        'report_id':fields.many2one('suggested.attendance', invisible=True,readonly=True),
        'state':fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('approved', 'Approved'),('done', 'Done'),],'State',readonly=True),
        'reason':fields.char('reason'),
        'added_percent':fields.float('added_percent'),
        'flage':fields.boolean('flage', invisible=True),
        }
    _defaults={
        'state':'draft'
        }
    
    def _check_greater(self, cr, uid, ids, context=None):
        """
        @return: Boolean of True or False
        """
        for act in self.browse(cr, uid, ids, context):
            if (act.added_percent > 100.0):
                raise osv.except_osv(_(''), _('The percent must be less than or equals to 100 '))
        return True
    _constraints = [
        (_check_greater, _(''), [''])
    ]

    def d_manager(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'confirmed'}, context=context)
    
    def gd_manager(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'approved'}, context=context)

class suggested_attendance(osv.Model):
    _name = "suggested.attendance"
    _rec_name="start_date"
    _columns = {
        'state':fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed')],'State'),
        'start_date':fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'lines_ids':fields.one2many('suggested.attendance.line', 'report_id', 'Report Lines'),
        'flage':fields.boolean('flage', invisible=True),
        'direct':fields.boolean('my employees',),
        'date':fields.char('date'),

        'checkeddm':fields.boolean('checked department manager', invisible=True),

        'checkedgdm':fields.boolean('checked general department manager', invisible=True),

        'done':fields.boolean('done', invisible=True),

        'department_ids' : fields.one2many('hr.attendance.departments', 'report_id', 'Lines', readonly=False),
    }
    _defaults={
        'state':'draft'
    }

    def unlink(self, cr, uid, ids, context=None):
        suggested_attendance_line =self.pool.get("suggested.attendance.line")
        for rec in self.browse(cr,uid,ids,context=context):
            if rec.state not in ['draft']:
                raise osv.except_osv(_('Error'), _('the record have to be in draft state to be deleted!'))

            deleted_ids = suggested_attendance_line.search(cr,uid,[('report_id','=',rec.id)],context=context)
            suggested_attendance_line.unlink(cr,uid,deleted_ids,context=context)
        
        super(suggested_attendance, self).unlink(cr, uid,ids, context=context) 

    def read(self, cr, user, ids, fields=None, context=None, load='_classic_read'):
        res = super(suggested_attendance,self).read(cr=cr, user=user, ids=ids, fields=fields, context=context, load=load)
        line_obj = self.pool.get("suggested.attendance.line")
        for rec in res:
            lines_ids = rec.get('lines_ids',[])
            states = line_obj.read(cr, user, lines_ids,['state'], context=context)
            draft = filter(lambda x :x['state'] == 'draft',states)
            confirmed = filter(lambda x :x['state'] == 'confirmed',states)
            approved = filter(lambda x :x['state'] == 'approved',states)
            done = filter(lambda x :x['state'] == 'done',states)
            rec['checkeddm'] = False
            rec['checkedgdm'] = False
            
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


    def create(self, cr, uid, vals, context=None):
        if not context:
            raise osv.except_osv(_('Error'), _('Not Enable to create record'))
        if context and 'wizard' not in context:
            raise osv.except_osv(_('Error'), _('Not Enable to create record'))
        id = super(suggested_attendance, self).create(cr, uid, vals, context=context)
        self.compute(cr, uid, id, context=context)

        department_obj = self.pool.get('hr.department')
        department_cat_obj = self.pool.get('hr.department.cat')

        department_cat_ids = department_cat_obj.search(cr, uid, [], context=context)
        departments_cats = department_cat_obj.read(cr, uid, department_cat_ids,['category_type'], context=context)
        cats = {x['id']:{'category_type':x['category_type']} for x in departments_cats}

        department_ids = department_obj.search(cr, uid, [], context=context)
        departments = department_obj.read(cr, uid, department_ids,['parent_id', 'cat_id'], context=context)

        departments = [ {'id':x['id'],'parent_id':x['parent_id'] and x['parent_id'][0],'cat_id': ( x['cat_id'] and x['cat_id'][0] in cats ) and cats[x['cat_id'][0]]['category_type'] or False} for x in departments]
        

        general_d = filter(lambda x:x['cat_id'] == 'general_dep',departments)

        general_dict = {}

        department_rel_obj = self.pool.get('hr.attendance.departments')
        for item in general_d:
            general_dict[item['id']] = filter(lambda x:x['parent_id'] == item['id'] and x['cat_id'] != 'general_dep', departments)
            parent = department_rel_obj.create(cr, uid, {'department_id':item['id'],
            'report_id':id})
            for i in general_dict[item['id']]:
                new_id = department_rel_obj.create(cr, uid, {'department_id':i['id'],'ener_report_id':id,
                'parent':parent})

        return id
    
    def write(self, cr, uid, ids, vals, context=None):
        super(suggested_attendance, self).write(cr, uid, ids, vals, context=context)
        self.compute(cr, uid, ids[0], context=context)
        return True
    
    def compute(self, cr, uid, id, context=None):
        basic = self.browse(cr, uid, id, context=context)
        for line in basic.lines_ids:
            if line.added:
                earned = line.period_work_hours - line.abacense_hours
                earned = earned - line.forget_finger_print_hours
                earned = earned - line.late_hours
                earned = earned + line.added #+ line.training
                percent= earned/line.period_work_hours * 100
                percent = round(percent,2)
                line.write({'added_percent':percent})
    
    def d_manager(self, cr, uid, ids, context=None):
        if context and 'lines_ids' in context:
            lines_ids = [x[1] for x in context.get('lines_ids',[]) ]
            self.pool.get('suggested.attendance.line').write(cr, uid, lines_ids, {'state':'confirmed'})
            self.write(cr, uid, ids, {'checkeddm':True}, context=context)
            department_rel_obj = self.pool.get('hr.attendance.departments')

            department_obj = self.pool.get('hr.department')

            users_obj = self.pool.get('res.users')

            emp_id = users_obj.read(cr, uid, uid, ['employee_ids'], context=context)

            dep_id = department_obj.search(cr,uid,[('manager_id','in',emp_id['employee_ids'])],context=context)

            department_rel_ids = department_rel_obj.search(cr,uid,[('ener_report_id','in',ids), ('department_id','in',dep_id)])

            department_rel_obj.write(cr, uid, department_rel_ids, {'checked':True})
    
    def gd_manager(self, cr, uid, ids, context=None):
        if context and 'lines_ids' in context:
            lines_ids = [x[1] for x in context.get('lines_ids',[]) ]
            self.pool.get('suggested.attendance.line').write(cr, uid, lines_ids, {'state':'approved'})
            self.write(cr, uid, ids, {'checkedgdm':True}, context=context)
            department_rel_obj = self.pool.get('hr.attendance.departments')

            department_obj = self.pool.get('hr.department')

            users_obj = self.pool.get('res.users')

            emp_id = users_obj.read(cr, uid, uid, ['employee_ids'], context=context)

            dep_id = department_obj.search(cr,uid,[('manager_id','in',emp_id['employee_ids'])],context=context)

            department_rel_ids = department_rel_obj.search(cr,uid,[('report_id','in',ids),('department_id','in',dep_id)])

            department_rel_obj.write(cr, uid, department_rel_ids, {'checked':True})

            self.browse(cr, uid, ids, context=context)
            cr.execute(
               'SELECT state FROM suggested_attendance_line WHERE report_id = %s ',(ids[0], )) 
            res = cr.dictfetchall()
            approved = filter(lambda x :x['state'] == 'approved',res)
            if len(res) == len(approved):
                self.write(cr, uid, ids, {'done':True}, context=context)
        return True
    
    def done(self, cr, uid, ids, context=None):
        lines_obj = self.pool.get('suggested.attendance.line')
        lines_ids = lines_obj.search(cr, uid,[('report_id','in', ids),('state','not in', ['approved'] )])
        if lines_ids:
            raise osv.except_osv(_('Error'), _('you have to confirm all details'))
        
        self.write(cr, uid, ids, {'state':'confirmed','checkeddm':True,'checkedgdm':True,'done':False})
        lines_ids = lines_obj.search(cr, uid,[('report_id','in', ids),('state','in', ['approved'] )])

        lines_obj.write(cr, uid, lines_ids, {'state':'done'})
    
    
    def get_date(self,str):
        return datetime.strptime(str, "%Y-%m-%d %H:%M:%S")
    def mail(self, cr, uid, ids, context=None):
        send_mail(self, cr, uid, ids[0], 'attendance_ntc.group_attendace_direct_manager',unicode(' إشعار الحضور', 'utf-8') , unicode(' يرجى اﻹطلاع على سجلات الحضور', 'utf-8'), context=context)

    def attendance(self, cr, uid, ids, context=None):
        self.attend(cr, uid, context)  

    def attend(self, cr, uid, context=None):

        req = urllib2.Request("http://172.30.30.39:8081/send.php")
        opener = urllib2.build_opener()
        f = opener.open(req)
        jsons = json.loads(f.read())
        attendance_obj= self.pool.get('hr.attendance')

        company_obj= self.pool.get('res.company')

        company_id = company_obj._company_default_get(cr, uid, 'suggested.attendance', context=context)
        
        #last fetch
        last_get = company_obj.read(cr, uid, company_id, ['last_attendance_date'],context=context)
        last_get_datetime = False
        if last_get:
            last_get = last_get['last_attendance_date']
            last_get_datetime = self.get_date( last_get )

        
        #current = datetime.now()

        #pre = current - timedelta(days=1)

        if last_get_datetime:
            jsons = filter(lambda x : self.get_date(x['fetch_time']) > last_get_datetime ,jsons)

            emp_obj = self.pool.get('hr.employee')
            emp_ids = emp_obj.search(cr, uid, [], context=context )
            emp_basic = emp_obj.read(cr, uid, emp_ids,['emp_code'], context=context)
            
            emp_basic = {int(x['emp_code']):int(x['id']) for x in emp_basic}

            bigest = last_get_datetime
            for i in jsons:
                if self.get_date( i['fetch_time'] ) > bigest:
                    bigest = self.get_date( i['fetch_time'] )
                action = i['action'] == "0" and 'sign_in' or 'sign_out'
                date = i['date_of']+" "+i['time_of']
                employee_id = int(i['fing_id'])

                new_id = employee_id in emp_basic and emp_basic[employee_id] or 0
                oo = attendance_obj.create(cr,uid,{'action':action,'name':date,'employee_id':employee_id,'emp_id':new_id},context=context)
            
            company_obj.write(cr, uid, company_id, {'last_attendance_date':bigest},context=context)

        return True   

class hr_allowance_deduction(osv.Model):
    """ 
    Inherits hr.allowance.deduction an add new 1 field to be used for the attendance
    """
    _inherit = "hr.allowance.deduction"

    _columns = {
        'related_attendance' : fields.boolean('Related Attendance'),
    }

class hr_attendance_departments(osv.Model):
    _name = "hr.attendance.departments"
    _columns = {
        'department_id' : fields.many2one('hr.department', 'Department', readonly=False),
        'parent' : fields.many2one('hr.attendance.departments', invisible=True, readonly=False),
        'lines_ids' : fields.one2many('hr.attendance.departments', 'parent', 'Lines'),
        'checked' : fields.boolean('checked', readonly=False),
        'report_id':fields.many2one('suggested.attendance', invisible=True,readonly=True),

        'ener_report_id':fields.many2one('suggested.attendance', invisible=True,readonly=True),
    }

class cusotm_res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
      'last_attendance_date': fields.datetime('last attendance time'),
               }