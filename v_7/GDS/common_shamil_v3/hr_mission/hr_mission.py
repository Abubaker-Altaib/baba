# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import math
import time
import datetime
from dateutil.relativedelta import relativedelta
from osv import osv , fields
from tools.translate import _
import openerp.addons.decimal_precision as dp
from attachments_copy.copy_attachments import copy_attachments as copy_attachments
from tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import netsvc


#----------------------------------------
#mission category
#----------------------------------------
mission_type = [
    ('1', 'Mission'),
    ('2', 'Operation'),
    ('3', 'Transmission'),
]
tansport_type = [
    ('1', 'Internal transport'),
    ('2', 'Train'),
    ('3', 'Plane'),
    ('4', 'Bus'),
    ('5', 'Taxi'),
    ('6', 'Other'),
]

mission_state = [
    ('draft', 'Draft'),
    ('completed','Completed'),
    ('confirmed', 'Confirmed'),
    ('validated','Validated'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('open', 'Opened'),# Transmission additional state
    ('close', 'Closed'),# Transmission additional state
    ('pending', 'Pending'),# Transmission additional state

]

class mission_category(osv.osv):
    
    _name = "hr.mission.category"
    _description = "Mission Category"    

    _columns = {
        'place':fields.selection([('inside','Inside'),('outside','Outside')] ,'place'),
        'cat_type': fields.selection([('1', 'Mission Destination'),('2', 'Operation sector'),('3', 'Transmission Station')], "mission category Type"),
        'name': fields.char("Mission Category", size=200 , required=True),
        'code': fields.char('Code', size=64),
        'max_days' :fields.integer("Max days"),
        'allowance_id' :fields.many2one('hr.allowance.deduction', 'Allowance', required=False),
        'mission_account_id':fields.property('account.account', type='many2one', relation='account.account',
                                             string="Mission Account", method=True, view_load=True,
                                             domain="[('user_type.report_type','=','expense'),('type','!=','view')]"),
        'fees_account_id': fields.property('account.account', type='many2one', relation='account.account',
                                           string="Fees Account", method=True, view_load=True,
                                           domain="[('user_type.report_type','=','expense'),('type','!=','view')]"),
        'fees_currency_id':fields.many2one('res.currency', 'Fees Currency'),
        'journal_id':  fields.property('account.journal', type='many2one', relation='account.journal',
                                       string="Journal", method=True, view_load=True,
                                       domain="[('type','=','purchase')]"),
        'account_analytic_id': fields.property('account.analytic.account', type='many2one',relation='account.analytic.account',
                                               string="Analytic Account", method=True, view_load=True),
        #'destination':fields.char("Destination name",size=200),
        'company_id' : fields.many2one('res.company', 'Company'),
        'currency':fields.many2one('res.currency', 'Currency'),
        'parent_id': fields.many2one('hr.mission.category', 'Mission Parent', domain="[('type','=','view')]"),
        'type': fields.selection([('view', 'view'), ('normal', 'Normal')], 'Type'),
        'validate':fields.boolean('Double Validation'),
    }
    
    _sql_constraints = [
        ('name_unique', 'unique(name,cat_type)', 'you can not create same name !')
    ]
    
    _defaults = {
        'type' : 'normal',
    }

    def onchange_parent_id(self, cr, uid, ids, parent_id,context=None):
        """
        Onchange method to set cat_type to catogery as parent type.

        @param start_date: Mission parent_id
        @return: dictionary contain the cat_type
        """
        result = {}
        if parent_id:
            for rec in self.browse(cr, uid, [parent_id], context=context):
                result['value'] = {
                    'cat_type': rec.cat_type,
                    'place': rec.place
                }
        return result

    def create(self, cr, uid, vals, context=None):
        """
        Override create method to check if category name contains spaces
        @return: super create method
        """
        if 'name' in vals:
            vals['name'] = vals['name'].strip()
        if not vals['name']:
            raise osv.except_osv(_('Warning!'),_('The Category Name Must Not be space'))
        return super(mission_category, self).create(cr, uid, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        mission_obj = self.pool.get('hr.mission.category')
        mission_id = mission_obj.search(cr, uid, [('parent_id', 'in', ids)], context=context)

        emp_mission_obj = self.pool.get('hr.employee.mission')
        emp_mission_id = emp_mission_obj.search(cr, uid, [('mission_id', 'in', ids)], context=context)
        
        for rec in self.browse(cr, uid, ids, context=context):
            if mission_id:
                raise osv.except_osv(_('Warning!'),_('You cannot delete this mission category because it is parent to another mission category'))
            if emp_mission_id:
                raise osv.except_osv(_('Warning!'),_('You cannot delete this mission category because it is reference to employee mission'))

        return super(mission_category, self).unlink(cr, uid, ids, context)

    def copy(self, cr, uid, id, default=None, context=None):
        default = {} if default is None else default.copy()
        mission = self.browse(cr, uid, id, context=context)
        default.update({'name':mission.name+"(copy)"})
        return super(mission_category, self).copy(cr, uid, id, default, context=context)

#----------------------------------------
#HR Operation Service Type
#----------------------------------------
class operation_service_type(osv.osv):
    _name = "operation.service.type"
    _description = "Operation Service Type"

    _columns = {
        'ferocity': fields.boolean('Ferocity Zone'),
        'name': fields.char('Service Type name', size=256,required=True),
    }

    def create(self, cr, uid, vals, context=None):
        """
        Override create method to check if Operation Service Type name contains spaces
        @return: super create method
        """
        if 'name' in vals:
            vals['name'] = vals['name'].strip()
        if not vals['name']:
            raise osv.except_osv(_('Warning!'),_('The Operation Service Type Name Must Not be space'))
        return super(operation_service_type, self).create(cr, uid, vals, context=context)

#----------------------------------------
# employee missions
#----------------------------------------
class employee_mission(osv.osv):

    _name = "hr.employee.mission"
    _description = "Employee Mission"

#FIXME: when days change dates doesn't change
    _columns = {
            'illness':fields.one2many('hr.employee.illness', 'transmission_id', "Illness",required=True),
            'service_type':fields.many2one('operation.service.type', "Service Type"),
            'type': fields.selection(mission_type, "mission Type",required=True),
            'dept_report':fields.boolean('department Is reporting'),
            'name' :fields.char('Name', size=64 , readonly=True),
            'company_id' : fields.many2one('res.company', 'Company' , required=True , readonly=True),
            'mission_place_id': fields.many2one('hr.mission.category', "Destination"),
            'mission_id': fields.many2one('hr.mission.category', "Place", required=True),
            'mission_leader': fields.many2one('hr.employee', "Leader"),
		    'department_id':fields.many2one('hr.department', "Department"),
            'start_date' :fields.date("Start Date", required=True),
            'end_date' :fields.date("End Date", required=True),
            'mission_fee': fields.float("Mission Fee", digits_compute=dp.get_precision('Payroll')),
            'real_fees_amount': fields.float("Real Fess Amount", digits_compute=dp.get_precision('Payroll')),
            'notes': fields.text("Comments"),
            'purpose': fields.text("Purpose"),
            'mission_place':fields.selection([('inside','Inside'),('outside','Outside')] ,'Mission place'),
            'expense_type':fields.selection([('especially','Especially'),('hospital','On the hospital')] ,'expense type'),
            'address': fields.text("Address"),
            'phone': fields.text("Phone Numbers"),
            'transport': fields.selection(tansport_type, "Transport Type"),
            'travel_path': fields.text("Travel Path"),
            'days': fields.float('Number of Days'),
            'mission_line':fields.one2many('hr.employee.mission.line', 'emp_mission_id', "mission",required=True),
            'state': fields.selection(mission_state, 'State', readonly=True),
		    'voucher_id' :fields.many2one('account.voucher','Voucher',readonly=True),
		    'fees_voucher_id' :fields.many2one('account.voucher','Fees Voucher',readonly=True),
            'percentage':fields.integer('Percentage(%)'),
            'validate': fields.related('mission_id', 'validate', type='boolean', relation='hr.mission.category', string='Apply Double Validation'),
    }

    _defaults = {
            'state': 'draft',
            'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.employee.mission', context=c),
            'name': '/',
    }
    _sql_constraints = [('Date_check',"CHECK (end_date>=start_date and days>=0.0 )",_("Start_date must be before End_date!")),
                        ('Fee_check_nagtive',"CHECK (mission_fee>=0.0)",_("Fee amount must be greater than Zero!")),('real_fee_check_nagtive',"CHECK (real_fees_amount>=0.0)",_("Real Fee amount must be greater than Zero!"))]


    def onchange_date(self, cr, uid, ids, start_date, end_date, days_no, field, context=None):
        """

        @param end_date: End date
        @param start_date: Start date
        @param days_no: Number of days
        @param field: Changed field
        @return: Dictionary of values 
        """
        vals = {}
        print">>>>>>>>>>>>>>>>>>>>>>start_date",start_date,end_date
        dt_from = start_date and datetime.datetime.strptime(start_date, '%Y-%m-%d')
        dt_to = end_date and datetime.datetime.strptime(end_date, '%Y-%m-%d')

        if field == 'start_date':
            if dt_from and days_no is not None:
                dt_time=dt_from + datetime.timedelta(days_no - 1)
                end_date=dt_time.strftime('%Y-%m-%d')
                vals.update({'end_date':end_date})
            elif dt_from and dt_to:
                vals.update({'days':round(self._get_number_of_days(start_date, end_date) + 1)})
        if field == 'end_date':
            if dt_from and dt_to:
                vals.update({'days':round(self._get_number_of_days(start_date, end_date) + 1)})
            elif days_no is not None and dt_to:
                dt_time=dt_to - datetime.timedelta(days_no - 1)
                start_date=dt_time.strftime('%Y-%m-%d')
                vals.update({'start_date':start_date})
        if field == 'days':
            if dt_from and days_no is not None:
                df_time=dt_from + datetime.timedelta(days_no - 1)
                end_date=df_time.strftime('%Y-%m-%d')
                vals.update({'end_date':end_date})
            elif days_no is not None and dt_to:
                dt_time=dt_to - datetime.timedelta(days_no - 1)
                start_date=dt_time.strftime('%Y-%m-%d')
                vals.update({'start_date':start_date})
        return {'value':vals}

    def _check_mission_line(self, cr, uid, ids, context={}):
        """
        Check that mission line is not empty
        @return: boolean True or False 
        """
        for obj in self.browse(cr, uid, ids, context=context):
            if not obj.mission_line:
                raise osv.except_osv(_('Warning!'),_('You must Enter employee/s.'))

        return True

    def _check_mission_leader(self, cr, uid, ids, context={}):
        """
        Check that mission leader is in the line
        @return: boolean True or False 
        """
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.mission_leader:
                check=False
                for line in obj.mission_line:
                    if line.employee_id.id == obj.mission_leader.id:
                        check=True
                        break
                if not check:
                    raise osv.except_osv(_('Warning!'),_('Mission Leader must Entered in the Line.'))

        return True

    _constraints = [
         (_check_mission_line, "", []),(_check_mission_leader, "", []), 
    ]


    def set_to_draft_mission(self, cr, uid, ids, context=None):
        """
        Mehtod that sets the state to draft.

        @return: Boolean True
        """
        for rec in self.browse(cr,uid,ids,context=context):
            if rec.move_order_id:
                    if rec.move_order_id.state == 'draft':
                        self.pool.get('hr.move.order').unlink(cr,uid,[rec.move_order_id.id])
                    else:
                        raise osv.except_osv(_('warning') , _('There is a Confirmed Move Order releted to this record, you must delete it before set the record to draft'))
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'hr.employee.mission', id, cr)
            wf_service.trg_create(uid, 'hr.employee.mission', id, cr)
        return True

    def rejecte_mission(self, cr, uid, ids, context=None):
        """
        Mehtod that sets the state to rejected.

        @return: Boolean True
        """
        for rec in self.browse(cr,uid,ids,context=context):
            if rec.voucher_id :
                    if rec.voucher_id.state == 'draft' :
                        self.pool.get('account.voucher').unlink(cr,uid,[rec.voucher_id.id])
                    elif rec.voucher_id.state == 'cancel' :
                        self.write(cr,uid,ids,{'voucher_id':False})
                    else : 
                        raise osv.except_osv(_('warning') , _('There is a voucher releted to this record, you must cancel it before set the record to draft'))
            if rec.fees_voucher_id :
                    if rec.fees_voucher_id.state == 'draft' :
                        self.pool.get('account.voucher').unlink(cr,uid,[rec.fees_voucher_id.id])
                    elif rec.fees_voucher_id.state == 'cancel' :
                        self.write(cr,uid,ids,{'fees_voucher_id':False})
                    else : 
                        raise osv.except_osv(_('warning') , _('There is a Fess voucher releted to this record, you must cancel it before set the record to draft'))
            if rec.move_order_id:
                if rec.move_order_id.state == 'draft':
                    self.pool.get('hr.move.order').unlink(cr,uid,[rec.move_order_id.id])
                else:
                    raise osv.except_osv(_('warning') , _('There is a Confirmed Move Order releted to this record, you must delete it before set the record to draft'))

        self.write(cr, uid, ids, {'state': 'rejected'}, context=context)
        return True

    def create(self, cr, uid, vals, context=None):
        """
        Method thats overwrite the create method and naming the mission by adding its sequence to the name.

        @param vals: Values that have been entered
        @return: super create method
        """
        if vals.get('mission_id'):
            mission = self.pool.get('hr.mission.category').browse(cr, uid, vals.get('mission_id'), context=context)
            vals.update({'name': mission.name + '/' + self.pool.get('ir.sequence').get(cr, uid, 'hr.employee.mission')})
        return super(employee_mission, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        Method thats overwrite the write method and updates the mission name by adding its sequence to the it.

        @param vals: Values that have been entered
        @return: Supper copy Method 
        """
        print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>write",vals

        if vals.get('mission_id'):
            mission = self.pool.get('hr.mission.category').browse(cr, uid, vals.get('mission_id'), context=context)
            emp_mission = self.browse(cr, uid, ids, context=context)[0]
            vals.update({'name': mission.name + '/' + emp_mission.name.split('/',1)[1]})
        update_field = [key for key in vals.keys() if key in ('mission_id', 'start_date' , 'end_date' , 'mission_fee')]
        for mission in  self.browse(cr, uid, ids, context=context):
            if update_field and mission.mission_line:
                sdate= vals.get('start_date', mission.start_date)
                edate= vals.get('end_date', mission.end_date)
                mission_id= vals.get('mission_id',mission.mission_id.id)
                for line in mission.mission_line:
                    res=line.change_days(line.employee_id.id,mission_id,sdate,edate)
                    if 'mission_fee' in vals:
                        self.pool.get('hr.employee.mission.line').write(cr, uid, line.id, {'mission_fees':vals['mission_fee']}, context=context)
        return super(employee_mission, self).write(cr, uid, ids, vals, context=context)

    def _get_number_of_days(self, start_date, end_date):
        """
        Returns a float equals to the timedelta between two dates given as string.

        @param start_date: Mission Start date
        @param end_date: Mission End date
        @return: Float that represents the days between two dates 
        """ 
        if start_date and end_date:
            timedelta = datetime.datetime.strptime(end_date, DEFAULT_SERVER_DATE_FORMAT) - datetime.datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
            return  (timedelta.days + float(timedelta.seconds) / 86400)
        

    def onchange_time_from(self, cr, uid, ids, start_date, end_date):
        """
        Onchange method to return the number of days between to dates when change start_date or end_date.

        @param start_date: Mission Start date
        @param end_date: Mission End date
        @return: dictionary contain the days

        """
        result = {}
        if end_date and start_date:
            result['value'] = {
                'days': self._get_number_of_days(end_date, start_date)
            }
        return result

    def unlink(self, cr, uid, ids, context=None):
            for rec in self.browse(cr, uid, ids, context=context):
                if rec.state != 'draft':
                    if rec.type == '1':
                        raise osv.except_osv(_('Warning!'),_('You cannot delete an employee mission which is in %s state.')%(rec.state))
                    elif rec.type == '2':
                        raise osv.except_osv(_('Warning!'),_('You cannot delete an employee Operation which is in %s state.')%(rec.state))
                    elif rec.type == '3':
                        raise osv.except_osv(_('Warning!'),_('You cannot delete an employee Transmission which is in %s state.')%(rec.state))
            return super(employee_mission, self).unlink(cr, uid, ids, context)


    def operation_duration_computation(self, cr, uid, ids,context=None):
        print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>operation_duration_computation"
        res={}
        emp_obj=self.pool.get("hr.employee")
        mission_line_obj=self.pool.get("hr.employee.mission.line")
        """
        calculate operation duration for emolpyee
        """
        hr_setting = self.pool.get('hr.config.settings')
        config_ids=hr_setting.search(cr,uid,[])
        config_browse=hr_setting.browse(cr, uid, config_ids)[0]
        settings=config_browse.get_default_operation_service()['operation_service']
        for rec in self.browse(cr,uid,ids,context=context):
            
            for emp in rec.mission_line:
                operation_service_days=0.0
                operation_service_months=0.0
                operation_service_years=0.0
                temp_months=0
                temp_days=0
                emp_line_ids=mission_line_obj.search(cr, uid, [('employee_id','=',emp.employee_id.id),('type','=','2')], context=context)
                for emp_line in mission_line_obj.browse(cr,uid,emp_line_ids,context=context):
                    #if emp_line.emp_mission_id.type=='2':
                    # and emp_line.emp_mission_id.state=='approved'
                    '''df=datetime.datetime.strptime(emp_line.start_date,'%Y-%m-%d')
                    dt=datetime.datetime.strptime(emp_line.end_date,'%Y-%m-%d')
                    date=relativedelta(dt,df)
                    operation_service_years+=date.years
                    temp_days+=date.days
                    temp_months+=date.months'''
                    temp_days += emp_line.days
                    print"______________________________temp_days",temp_days
                if temp_days >= 30:
                    temp_days=temp_days*settings
                if temp_days >= 30:
                    temp_cal=temp_days / 30
                    frac, whole = math.modf(temp_cal)
                    operation_service_days=frac*30
                    temp_months=whole
                else:
                    operation_service_days+=temp_days

                if temp_months >= 12:
                    operation_service_months+=temp_months%12
                    operation_service_years+=temp_months/12
                else:
                    operation_service_months+=temp_months
                res = {'operation_service_years':operation_service_years,'operation_service_months':operation_service_months,'operation_service_days':operation_service_days}
                print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>res",res
                emp_obj.write(cr,uid,emp.employee_id.id,res,context=context)
        return res

    def mission_approved(self, cr, uid, ids, context=None):
        """
        Workflow method change record state to 'approved' and 
        Transfer Mission amount to voucher

        @return: Boolean True    
        """
        for mission in self.browse(cr, uid, ids, context=context):
            if mission.type=='2':
                mission.operation_duration_computation()
            elif mission.type=='3':
                miss=self.write(cr, uid, ids,{'state':'approved'}, context=context)
                return miss
            mission_amount = 0.0
            number=False
            fees_amount = 0.0
            fees_num=0
            employees_dic = {}
            employees_fees_dic = {}
            for emp_mission_amount in mission.mission_line:
                employees_dic[emp_mission_amount.employee_id] = emp_mission_amount.mission_amounts
                employees_fees_dic[emp_mission_amount.employee_id] = emp_mission_amount.mission_fees
                mission_amount += emp_mission_amount.mission_amounts
                fees_amount += emp_mission_amount.mission_fees
            '''if mission_amount <= 0:
                raise osv.except_osv(_('Warnning!'),_("Sorry you can not transfer this mission the amoutn is zero"))'''
            lines = []
            fees_lines=[]
            setting=mission.mission_id
            account_analytic_id=setting.parent_id.account_analytic_id and setting.parent_id.account_analytic_id.id or False
            if mission.department_id and not account_analytic_id:
                account_analytic_id=mission.department_id and mission.department_id.analytic_account_id and mission.department_id.analytic_account_id.id or False
            if mission.department_id and not account_analytic_id:
                raise osv.except_osv(_('Warning!'),_('Please Set an analytic account for this department.'))
            if not mission.department_id:
                lines = self.pool.get('hr.employee').get_emp_analytic(cr, uid, employees_dic,  {'name':mission.name,
                                'account_id':setting.parent_id.mission_account_id and setting.parent_id.mission_account_id.id or False,
                                          })
                fees_lines = self.pool.get('hr.employee').get_emp_analytic(cr, uid, employees_fees_dic,  {'name':mission.name,
                                'account_id':setting.parent_id.fees_account_id and setting.parent_id.fees_account_id.id or False,
                                          })
            else:
                lines.append({'name':mission.name,
                          'account_id':setting.parent_id.mission_account_id and setting.parent_id.mission_account_id.id or False,
                          'account_analytic_id':account_analytic_id,
                          'amount':mission_amount,
                         })
                fees_lines.append({'name':mission.name,
                          'account_id':setting.parent_id.fees_account_id and setting.parent_id.fees_account_id.id or False,
                          'account_analytic_id':account_analytic_id,
                          'amount':fees_amount,
                         })
            if fees_amount > 0:

                fees_dic={ 
                      'company_id':setting.fees_account_id.company_id and setting.fees_account_id.company_id.id or False,
                      'journal_id':setting.parent_id.journal_id and setting.mission_id.parent_id.journal_id.id or False,
                      'account_id':setting.parent_id.fees_account_id and setting.parent_id.fees_account_id.id or False,
                      'name': 'Fees of ' + mission.name + ' - ' + mission.start_date,
                      'reference':'HR/Mission Fees/' + mission.name + ' - ' + mission.start_date,
                      'narration':'HR/Mission Fees/' + mission.name ,
                      #'currency_id':setting.fees_currency_id.id,
                      'department_id':mission.department_id.id,
                      'lines':fees_lines, 
                       }
                if setting.fees_currency_id: fees_dic.update({'currency_id':setting.fees_currency_id.id,})
                fees_num = self.pool.get('payroll').create_payment(cr, uid, ids, fees_dic, context=context)

            mission_dic={ 
                          'lines':lines, 
                          'department_id':mission.department_id.id,
                          'company_id':setting.mission_account_id.company_id and setting.mission_account_id.company_id.id or False,
                         # 'journal_id':setting.parent_id.journal_id and setting.mission_id.parent_id.journal_id.id or False,
                          'account_id':setting.mission_account_id and setting.mission_account_id.id or False,
                          'name': mission.name + ' - ' + mission.start_date,
                          'reference':'HR/Mission/' + mission.name + ' - ' + mission.start_date,
                          'narration':'HR/Mission/' + mission.name ,
                           }
            if setting.currency: mission_dic.update({'currency_id':setting.currency.id,})
            if lines[0]['amount'] > 0:
                number = self.pool.get('payroll').create_payment(cr, uid, ids, mission_dic, context=context)
            miss={}
            miss=self.write(cr, uid, ids,{'state':'approved','voucher_id':number,'fees_voucher_id':fees_num}, context=context)
            copy_attachments(self,cr,uid,ids,'hr.employee.mission',number,'account.voucher', context)
        return miss

    def recalcuate_days(self, cr, uid, ids, context=None):
        """
        Recalculate amount of mission if number of days changed.

        @return: True
        """
        employee_mission_line_obj = self.pool.get('hr.employee.mission.line')
        for rec in self.browse(cr, uid, ids, context=context):
            for line in rec.mission_line:
                new_amount = employee_mission_line_obj.onchange_days(cr, uid, ids, line.days, line.employee_id.id, rec.mission_id.id)
                employee_mission_line_obj.write(cr, uid, [line.id], new_amount['value'], context=context)
        return True

    def copy(self, cr, uid, ids, default={}, context=None):
        default.update({'mission_line': False})
        return super(employee_mission, self).copy(cr, uid, ids, default=default, context=context)


#----------------------------------------
# Mission Line
#----------------------------------------
class employee_mission_line(osv.osv):

    _name = "hr.employee.mission.line"
    _description = "Employee Mission Line"
    _rec_name = "emp_mission_id"
    #TODO: update name_get & name search for employee to search by name & code
    _columns = {
        'emp_mission_id': fields.many2one('hr.employee.mission', "Mission", required=True, ondelete='cascade'),
        'employee_id' : fields.many2one('hr.employee', "Employee", required=True),
        'emp_degree': fields.related('employee_id','degree_id',type="many2one",relation="hr.salary.degree",string="Degree",readonly=1),
        'mission_amounts': fields.float("Mission Amount",digits_compute=dp.get_precision('Payroll'), readonly=True),
        'mission_fees': fields.float("Mission Fee", digits_compute=dp.get_precision('Payroll')),
        'days': fields.float("Days", digits_compute=dp.get_precision('Payroll')),
        'amount': fields.float("Amount", digits_compute=dp.get_precision('Payroll'), readonly=True),
        'start_date':fields.date(string='Start Date'),
        'end_date':fields.date(string='End Date'),
        'type': fields.related('emp_mission_id','type',type="char", string="mission Type"),
        'supervisor':fields.boolean('Supervisor'),
        'notes': fields.text("Comments"),
    }
    
    _defaults = {
		'employee_id': lambda *a: False,
    }

    def _get_number_of_days(self, start_date, end_date):
        """
        Returns a float equals to the timedelta between two dates given as string.

        @param start_date: Mission Start date
        @param end_date: Mission End date
        @return: Float that represents the days between two dates 
        """ 
        if start_date and end_date:
            timedelta = datetime.datetime.strptime(end_date, DEFAULT_SERVER_DATE_FORMAT) - datetime.datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
            return  (timedelta.days + float(timedelta.seconds) / 86400)

    def onchange_line_date(self, cr, uid, ids, start_date, end_date, days_no, field, context=None):
        """

        @param end_date: End date
        @param start_date: Start date
        @param days_no: Number of days
        @param field: Changed field
        @return: Dictionary of values 
        """
        print">>>>>>>>>>>>>>onchange_line_date>>>>>>>>>",start_date, end_date, days_no
        vals = {}
        dt_from = start_date and datetime.datetime.strptime(start_date, '%Y-%m-%d')
        dt_to = end_date and datetime.datetime.strptime(end_date, '%Y-%m-%d')

        if field == 'start_date':
            if dt_from and days_no is not None:
                dt_time=dt_from + datetime.timedelta(days_no - 1)
                end_date=dt_time.strftime('%Y-%m-%d')
                vals.update({'end_date':end_date})
            elif dt_from and dt_to:
                vals.update({'days':round(self._get_number_of_days(start_date, end_date) + 1)})
        if field == 'end_date':
            if dt_from and dt_to:
                vals.update({'days':round(self._get_number_of_days(start_date, end_date) + 1)})
            elif days_no is not None and dt_to:
                dt_time=dt_to - datetime.timedelta(days_no - 1)
                start_date=dt_time.strftime('%Y-%m-%d')
                vals.update({'start_date':start_date})
        if field == 'days':
            if dt_from and days_no is not None:
                df_time=dt_from + datetime.timedelta(days_no - 1)
                end_date=df_time.strftime('%Y-%m-%d')
                vals.update({'end_date':end_date})
            elif days_no is not None and dt_to:
                dt_time=dt_to - datetime.timedelta(days_no - 1)
                start_date=dt_time.strftime('%Y-%m-%d')
                vals.update({'start_date':start_date})
        return {'value':vals}

    def onchange_days(self, cr, uid, ids, days, employee_id, mission_id, context=None):
        """
        Compute missions amount for(Internal/External missions).
        
        @param days: integer no of days entered by user
        @param employee_id: ID of employee
        @param mission_id: ID of mission
        @return: Dictionary of mission amount to be updated
        """
        if not employee_id: 
            return {'value':{'mission_amounts':0,'amount':0}}
        payroll_obj = self.pool.get('payroll')
        mission_obj = self.pool.get('hr.mission.category')
        emp_obj = self.pool.get('hr.employee')
        allowance_id = mission_obj.browse(cr, uid, mission_id).allowance_id
        emp = emp_obj.browse(cr, uid, employee_id, context=context)
        date = time.strftime('%Y-%m-%d')
        total_payroll=payroll_obj.allowances_deductions_calculation(cr,uid,date,emp,{}, [allowance_id.id],False,[allowance_id.id])
        amount = total_payroll['total_allow'] * days
        emp_mission_dict = {
            'mission_amounts':amount,
            'amount':total_payroll['total_allow'],
            'stamp':allowance_id.stamp
        }
        return {'value': emp_mission_dict}

    def check_employee_mission(self, cr, uid, ids, context={}):
        for line in self.browse(cr,uid,ids,context=context):
            active_mission_ids=self.search(cr,uid,[('start_date','<=',line.start_date),('end_date','>=',line.start_date),
                                                   ('id','!=',line.id),('employee_id','=',line.employee_id.id),('type','=',line.type)],context=context)
            print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>....",line.type,active_mission_ids,ids
            if active_mission_ids and line.type == '1':
                raise osv.except_osv(_('ERROR'),_('Sorry This Employee Is currently in a mission!'))
                return False
            elif active_mission_ids and line.type == '2':
                raise osv.except_osv(_('ERROR'),_('Sorry This Employee Is currently in a Operation!'))
                return False
            elif active_mission_ids and line.type == '3':
                raise osv.except_osv(_('ERROR'),_('Sorry This Employee Is currently in a Trasmission!'))
                return False
        return True

    def check_date(self, cr, uid, ids, context={}):
        for line in self.browse(cr,uid,ids,context=context):
            mission=line.emp_mission_id
            if line.start_date < mission.start_date or line.end_date > mission.end_date:
                print">>>>>>>>>>>>>>>",line.start_date , mission.start_date , line.end_date , mission.end_date,line.type
                if line.type == '1':
                    print">>>>>>>>>>>raise osv.except_osv"
                    raise osv.except_osv(_('ERROR'),_('the period in mission line must be  within the piriod of mission!'))
                    return False
                elif line.type == '2':
                    raise osv.except_osv(_('ERROR'),_('the period in Operation line must be  within the piriod of Operation!'))
                    return False
                elif line.type == '3':
                    raise osv.except_osv(_('ERROR'),_('the period in Trasmission line must be  within the piriod of Trasmission!'))
                    return False
        return True

    _constraints = [
        (check_employee_mission, '', []),(check_date, '', []),
    ]

    _sql_constraints = [
       ('date_check',"CHECK (end_date>=start_date and days>=0.0 )",_("Start_ddddate must be before End_date!")),
       ('employee_mission_uniqe', 'unique (emp_mission_id,employee_id)', 'You can not enter the same employee!'),
                          ]


    def change_days(self, cr, uid, ids, employee_id, mission_id ,sdate,edate,context=None):
        """
        Compute missions amount for(Internal/External missions).        
        @param days: integer no of days entered by user
        @param employee_id: ID of employee
        @param mission_id: ID of mission
        @return: Dictionary of mission amount to be updated
        """
        days=0
        #print">>>>>>>>>>change_days3",self, cr, uid, ids, employee_id, mission_id ,sdate,edate
        if not employee_id: return {}
        payroll_obj = self.pool.get('payroll')
        category_obj = self.pool.get('hr.mission.category')
        days=self._get_number_of_days(sdate,edate)+1
        allowance_id= mission_id and  category_obj.browse(cr, uid, [mission_id])[0].allowance_id.id or 0
        if allowance_id==0: return {}
        emp = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
        allow_dict= payroll_obj.allowances_deductions_calculation(cr,uid,sdate,emp,{'no_sp_rec':True},[allowance_id], False,[])
        if not days :
            days=0
        emp_mission_dict = {
            'mission_amounts':allow_dict['total_allow'] * days,
            'amount':allow_dict['total_allow'],
            'days':days,
                 }
        self.write(cr, uid, ids, emp_mission_dict )
        return {'value': emp_mission_dict}

    def onchange_employee(self, cr, uid, ids, emp_id,mission_id,sdate, edate ,context=None):
        """
        Method returns the employee_type that missions is enabled for them.
        @param emp_id: ID of the employee
        @return: Dictionary contains the domain of the employee_type
        """
        #print"*********************************************************", emp_id
        res ={}
        emp_obj = self.pool.get('hr.employee')
        company_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id
        contractors = company_obj.mission_contractors
        employee = company_obj.mission_employee
        recruit = company_obj.mission_recruit
        trainee = company_obj.mission_trainee
        employee_domain = emp_obj._get_default_employee_domain(cr, uid, ids, contractors, employee, recruit, trainee)
        employee_domain['employee_id'].append(('state', '=', 'approved'))
        domain = {'employee_id':employee_domain['employee_id']}
        if emp_id:
            res.update({'domain': domain})
            res = self.change_days(cr, uid, ids, emp_id,mission_id,sdate,edate, context=context)
        res.update({'domain': domain})
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
