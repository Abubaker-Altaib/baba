# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from tools.translate import _
import time
import netsvc
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import fields,osv, orm
from openerp.tools.translate import _
from openerp.addons.account_voucher.account_voucher import resolve_o2m_operations

#----------------------------------------
#HR Append
#----------------------------------------
class hr_append(osv.osv):
    _name = "hr.append"
    _description = "HR append"

    _columns = {
        'employee_id': fields.many2one('hr.employee', "Employee", required=True), 
        'emp_code': fields.related('employee_id','emp_code',type="char",string="Employee Code",readonly=1),
        'reason': fields.text("Append Reason",required=True),
        'hr_comment': fields.text("HR Comment"),
        'state':fields.selection([('draft','Draft'), ('confirm', 'Confirm'),('end','End')] ,'Status'),  
        'destination': fields.many2one('hr.department' ,string="Append Destination"),
        'start_date' :fields.date("Start Date", required=True),
        'end_date' :fields.date("End Date", required=True),
        'move_order_line_id' : fields.many2one('hr.move.order.line' , string="Move Order") ,
        'move_order_id' : fields.many2one('hr.move.order' , string="Move Order") ,   
        'new_payroll_employee_id':fields.many2one('hr.department.payroll' , string="New Group",required=True),
        'old_payroll_employee_id':fields.many2one('hr.department.payroll' , string="Pref Group"),
        
    } 

    _defaults = {
        'state':'draft',
    }

    _sql_constraints = [ ('date_check', "CHECK ( start_date < end_date)", "The start date must be anterior to the end date."),  
    ] 


    def onchange_employee(self, cr, uid, ids, emp_id,context={}):
        #employee_type domain
        if emp_id:
            emp_obj = self.pool.get('hr.employee')
            emp = emp_obj.browse(cr , uid , [emp_id])[0]
            ref_id = emp.payroll_employee_id.id
            return {
                'value' : {
                    'old_payroll_employee_id': emp.payroll_employee_id.id,
                } ,
                'domain' : {              
                    'new_payroll_employee_id' : [('id' , '!=' , ref_id)] , 
                }
            }
        return {}

    def set_to_draft(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to draft.

        @return: Boolean True
        """
        for rec in self.browse(cr,uid,ids,context=context):
            emp = self.pool.get('hr.employee')
            if rec.move_order_id:
                    if rec.move_order_id.state == 'draft':
                        self.pool.get('hr.move.order').unlink(cr,uid,[rec.move_order_id.id])
                        emp.write(cr, uid, [rec.employee_id.id], {'payroll_employee_id': rec.old_payroll_employee_id and rec.old_payroll_employee_id.id or rec.employee_id.payroll_employee_id.id,})
                    else:
                        raise osv.except_osv(_('warning') , _('There is a Confirmed Move Order releted to this record, you must delete it before set the record to draft'))
            else:
                emp.write(cr, uid, [rec.employee_id.id], {'payroll_employee_id': rec.old_payroll_employee_id and rec.old_payroll_employee_id.id or rec.employee_id.payroll_employee_id.id,})             
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def confirm(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to confirm.

        @return: Boolean True
        """
        emp = self.pool.get('hr.employee')
        for rec in self.browse(cr , uid , ids):
            if rec.move_order_line_id:
                self.pool.get('hr.move.order.line').write(cr , uid , [rec.move_order_line_id.id] , {'append_id' : rec.id})
            emp.write(cr, uid, [rec.employee_id.id], {'payroll_employee_id': rec.new_payroll_employee_id and rec.new_payroll_employee_id.id or rec.employee_id.payroll_employee_id.id,})
        self.write(cr, uid, ids, {'state': 'confirm'}, context=context)
        return True

    def create_move_order(self, cr, uid, ids,context={}):
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_custom_military', 'hr_move_order_with_footer')
        res = {
                    'name': _('Move Order'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id' : view_id ,
                    'res_model': 'hr.move.order',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }
        for rec in self.browse(cr, uid, ids, context):
            if not rec.move_order_id :
                data = {
                    'default_move_order_line_ids': [[0 , 0 , {'employee_id' : rec.employee_id.id ,'append_id' : rec.id , 'type' : 'append' , 'date' : rec.start_date}]],
                    'default_source': rec.employee_id.department_id.id or False,
                    'default_destination': rec.destination.id,
                    'append_id': rec.id,
                    'default_type': 'append',
                    #'default_move_date': ,
                    'default_out_source': True,
                }
                res['context'] = data
            else :
                res['res_id'] = rec.move_order_id.id
        return res

    def set_to_end(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to draft.

        @return: Boolean True
        """
        for rec in self.browse(cr,uid,ids,context=context):
            emp = self.pool.get('hr.employee')
            if rec.old_payroll_employee_id:
               if not rec.hr_comment:
                  raise osv.except_osv(_('warning') , _('please Enter End Reason'))
               emp.write(cr, uid, [rec.employee_id.id], {'payroll_employee_id': rec.old_payroll_employee_id and rec.old_payroll_employee_id.id or rec.employee_id.payroll_employee_id.id,})
            else:
               raise osv.except_osv(_('warning') , _('please Enter Previous Group'))            
        self.write(cr, uid, ids, {'state': 'end'}, context=context)
        return True
#----------------------------------------
#HR Unlock Reason
#----------------------------------------
class hr_unlock_reason(osv.osv):
    _name = "hr.unlock.reason"
    _description = "HR Unlock Reason"

    _columns = {
        'name': fields.char('Reason name', size=256),
        'type':fields.selection([('holiday','Holiday'), ('mission', 'Mission'), 
                                ('transmission', 'Transmission'), ('operation', 'Operations'),
                                ('training', 'Training')] ,'Type of Unlock'),
    }

#----------------------------------------
#HR Unlock
#----------------------------------------
class hr_unlock(osv.osv):
    _name = "hr.unlock"
    _description = "HR Unlock"

    _columns = {
        'employee_ids': fields.many2many('hr.employee','employee_unlock_rel' , 'unlock_id' , 'emp_id' ,  string="Employees", required=True), 
        'emp_degree': fields.related('employee_id','degree_id',type="many2one",relation="hr.salary.degree",string="Degree",readonly=1),
        'emp_dept': fields.related('employee_id','department_id',type="many2one",relation="hr.department",string="Department",readonly=1),
        'emp_code': fields.related('employee_id','emp_code',type="char",string="Employee Code",readonly=1),
        'reason': fields.many2one('hr.unlock.reason', "Unlock Reason", required=True),
        'state':fields.selection([('draft','Draft'), ('confirm', 'Confirm'), ('approved', 'Approved')] ,'Status'),  
        'comment': fields.text("Comment"),                                   
        'dept_comment': fields.text("Department Comment"),
        'destination': fields.char("Destination Travel",size=64),
        'start_date' :fields.date("Start Date", required=True),
        'end_date' :fields.date("End Date", required=True),
        'code' : fields.char('Number' , size=64) , 
        'airport_partner_id' :  fields.many2one('res.partner' ,  string="Airport Partner")  ,  
    } 

    _defaults = {
        'state':'draft',
    }

    _sql_constraints = [ ('date_check', "CHECK ( start_date < end_date)", "The start date must be anterior to the end date."),  
    ] 

    def set_to_draft(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to draft.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def confirm(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to confirm.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'confirm'}, context=context)
        return True

    def approve(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to confirm.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'approved'}, context=context)
        return True

    
    def check_date_reason(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a place with the same name

        @return: boolean True or False
        """
        holiday_obj = self.pool.get('hr.holidays')
        mission_obj = self.pool.get('hr.employee.mission')
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.reason.type == 'holiday':
                holiday_idss = holiday_obj.search(cr, uid, [('date_from','<=',rec.start_date),
                                ('date_to','>=',rec.end_date),('employee_id','=',rec.employee_id.id)],
                                context=context)
                if not holiday_idss:
                    raise osv.except_osv(_('ERROR'), _('There is no holiday for the employee %s within this unlock duration') % (rec.employee_id.name))
            elif rec.reason.type == 'mission':
                mission_idss = mission_obj.search(cr, uid, [('start_date','<=',rec.start_date),
                                ('end_date','>=',rec.end_date),('employee_id','=',rec.employee_id.id), 
                                ('type','=','1')], context=context)
                if not mission_idss:
                    raise osv.except_osv(_('ERROR'), _('There is no mission for the employee %s within this unlock duration') % (rec.employee_id.name))
            elif rec.reason.type == 'operation':
                mission_idss = mission_obj.search(cr, uid, [('start_date','<=',rec.start_date),
                                ('end_date','>=',rec.end_date),('employee_id','=',rec.employee_id.id), 
                                ('type','=','2')], context=context)
                if not mission_idss:
                    raise osv.except_osv(_('ERROR'), _('There is no operation for the employee %s within this unlock duration') % (rec.employee_id.name))
            elif rec.reason.type == 'transmission':
                mission_idss = mission_obj.search(cr, uid, [('start_date','<=',rec.start_date),
                                ('end_date','>=',rec.end_date),('employee_id','=',rec.employee_id.id), 
                                ('type','=','3')], context=context)
                if not mission_idss:
                    raise osv.except_osv(_('ERROR'), _('There is no transmission for the employee %s within this unlock duration') % (rec.employee_id.name))
            else:
                ######## Check Training (last case)
                pass
        return True

    _constraints = [
         (check_date_reason, '', []),
    ]

#----------------------------------------
#Additional service
#----------------------------------------
class hr_additional_service(osv.osv):
    _name = "hr.additional.service"
    _description = "Additional service"
    _rec_name = "code"

    def _duration_computation(self, cr, uid, ids,field_name, default=None, context=None):
        res={}
        """
        get difference between start date and end date
        """
        for rec in self.browse(cr,uid,ids,context=context):
            res[rec.id]={
                'days':0.0,
                'months':0.0,
                'years':0.0,
            }
            df=datetime.strptime(rec.start_date,'%Y-%m-%d')
            dt=datetime.strptime(rec.end_date,'%Y-%m-%d')
            date=relativedelta(dt,df)
            res[rec.id]['days']=date.days
            res[rec.id]['months']=date.months
            res[rec.id]['years']=date.years
            
        return res
    _columns = {
        'service_place': fields.selection([('inside','Inside'),('outside','Outside')] ,'service place',required=True),
        'employee_id': fields.many2one('hr.employee', "Employee", required=True), 
        'code': fields.char("Code", size=64,readonly=True),
        'service_type':fields.selection([('connected','Connected'),('separated','Separated')] ,'Service Type',required=True),
        'state':fields.selection([('draft','Draft'),('confirm', 'Confirm')] ,'Status'),  
        'previous_place':fields.selection([('in','In Sudan'),('out','Out Sudan')] ,'Previous Work Place'),                                      
        'comments': fields.text("Comments"),
        'previous_job': fields.char("Previous Job",size=64),
        'come_from': fields.char("Come From",size=64),
        'start_date' :fields.date("Start Date", required=True),
        'end_date' :fields.date("End Date", required=True),
        'days' :  fields.function(_duration_computation, string='Days',multi="all",
                              store = { 'hr.additional.service': (lambda self,cr,uid,ids,ctx={}:ids,  ['start_date','end_date'], 10)}),
        'months' :  fields.function(_duration_computation, string='Months',multi="all",
                              store = { 'hr.additional.service': (lambda self,cr,uid,ids,ctx={}:ids,  ['start_date','end_date'], 10)}),
        'years' :  fields.function(_duration_computation, string='Years',multi="all",
                              store = { 'hr.additional.service': (lambda self,cr,uid,ids,ctx={}:ids,  ['start_date','end_date'], 10)}),
    
    } 

    _defaults = {
        'code':'/',
        'state':'draft',
    }

    _sql_constraints = [ ('date_check', "CHECK ( start_date < end_date)", "The start date must be anterior to the end date."),  
    ] 

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft']:
                raise osv.except_osv(_('Warning!'),_('You cannot delete record that is not in draft state.'))
        return super(hr_additional_service, self).unlink(cr, uid, ids, context)

    def _check_service_type(self, cr, uid, ids, context={}):
        """
        Check that service_type is connected if service_place is inside
        @return: boolean True or False 
        """
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.service_place == 'inside' and obj.service_type != 'connected':
                raise osv.except_osv(_('Warning!'),_('service type must be connected if service place is inside.'))
        return True

    def _check_duplicate(self, cr, uid, ids, context={}):
        """
        Check that service_type is connected if service_place is inside
        @return: boolean True or False 
        """
        for rec in self.browse(cr, uid, ids, context=context):
            emp_ids=self.search(cr, uid, [('employee_id','=',rec.employee_id.id),('id','!=',rec.id)], context=context)
            for emp in self.browse(cr, uid, emp_ids, context=context):
                if (rec.start_date >= emp.start_date and rec.start_date <= emp.end_date) or (rec.end_date >= emp.start_date and rec.end_date <= emp.end_date)\
                or (emp.start_date >= rec.start_date and emp.start_date <= rec.end_date) or (emp.end_date >= rec.start_date and emp.end_date <= rec.end_date):
                    raise osv.except_osv(_('Warning!'),_('There is an overlap between days with this additional service(%s).')%(emp.code))
        return True

    def _check_date(self, cr, uid, ids, context={}):
        """
        Check that date of additional service is after end date of employee or before start date
        @return: boolean True or False 
        """

        for obj in self.browse(cr, uid, ids, context=context):
            #if obj.service_type ==  'separated':
            if (obj.start_date >= obj.employee_id.employment_date and obj.start_date <= obj.employee_id.end_date) or (obj.end_date >= obj.employee_id.employment_date and obj.end_date <= obj.employee_id.end_date):
                raise osv.except_osv(_('Warning!'),_('additional separated service must be after end date of employee or before start date.'))
        return True    

    def _check_service_duration_limit(self, cr, uid, ids, context={}):
        """
        Check that service_duration not exceed spcific limit.
        @return: boolean True or False 
        """
        hr_setting = self.pool.get('hr.config.settings')
        config_ids=hr_setting.search(cr,uid,[])
        config_browse=hr_setting.browse(cr, uid, config_ids)[0]
        connected_limit=config_browse.get_default_connected_service_limit()['connected_service_limit']
        separated_limit=config_browse.get_default_separated_service_limit()['separated_service_limit']
        for obj in self.browse(cr, uid, ids, context=context):
            rec=obj.service_duration_computation()
            if rec:
                if obj.service_type=='connected':
                    if rec['connected_service_years'] > connected_limit:
                        raise osv.except_osv(_('Warning!'),_('the connected service for this employee exceed connected service limit.'))
                elif obj.service_type=='separated':
                    if rec['separated_service_years'] > separated_limit:
                        raise osv.except_osv(_('Warning!'),_('the separated service for this employee exceed separated service limit.'))
        return True 

    _constraints = [
         (_check_service_type, "", []), (_check_service_duration_limit, "", []), (_check_date, "", []),(_check_duplicate,"",[])
    ]

    def create(self, cr, user, vals, context=None):
        """
        Override to add constrain of sequance
        @param vals: Dictionary of values
        @return: super of hr_additional_service
        """
        if ('code' not in vals) or (vals.get('code') == '/'):
            seq = self.pool.get('ir.sequence').get(cr, user, 'hr.additional.service')
            vals['code'] = seq and seq or '/'
            if not seq:
                raise  osv.except_osv(_('Warning'), _('No sequence defined!\nPleas contact administartor to configue sequence with code \'hr.additional.service\'') )
        new_id = super(hr_additional_service, self).create(cr, user, vals, context)
        return new_id

    def onchange_service_place(self, cr, uid, ids, service_place,context=None):
        """
        Onchange method to set service_type base in service_place.

        @param service_place:service_place
        @return: dictionary contain the service_type
        """
        result = {}
        if service_place=='inside':
            result['value'] = {
                'service_type': 'connected'
            }
        return result

    def service_duration_computation(self, cr, uid, ids,context=None):
        res={}
        """
        ====
        """
        res={'connected_service_months': 0,
         'connected_service_days': 0, 
         'connected_service_years': 0,
         'separated_service_months': 0,
         'separated_service_days': 0, 
         'separated_service_years': 0,}
        emp_obj=self.pool.get("hr.employee")
        hr_setting = self.pool.get('hr.config.settings')

        for rec in self.browse(cr, uid, ids, context=context):
            separated_days=0
            separated_months=0
            separated_service_days=0
            separated_service_months=0
            separated_service_years=0

            connected_days=0
            connected_months=0
            connected_service_days=0
            connected_service_months=0
            connected_service_years=0
            emp_ids=self.search(cr, uid, [('employee_id','=',rec.employee_id.id),('state','=','confirm')], context=context)
            for emp in self.browse(cr,uid,emp_ids,context=context):
                if emp.service_type=='connected':
                    connected_months+=emp.months
                    connected_service_years+=emp.years
                    connected_days+=emp.days
                    if connected_days >= 30:
                        connected_service_days=connected_days%30
                        connected_service_months+=connected_days/30
                        connected_days=0
                    else:
                        connected_service_days+=connected_days

                    if connected_months >= 12:
                        connected_service_months=connected_months%12
                        connected_service_years+=connected_months/12
                        connected_months=0
                    else:
                        connected_service_months+=connected_months
                    res.update({'connected_service_months': int(connected_service_months), 'connected_service_days': connected_service_days, 'connected_service_years': connected_service_years})
                    print"______________________res",res,connected_months,connected_days
                if emp.service_type=='separated':
                    separated_service_months+=emp.months
                    separated_service_years+=emp.years
                    separated_days+=emp.days
                    if separated_days >= 30:
                        separated_service_days=separated_days%30
                        separated_service_months+=separated_days/30
                    else:
                        separated_service_days+=separated_days

                    if separated_months >= 12:
                        separated_service_months=separated_months%12
                        separated_service_years+=separated_months/12
                    else:
                        separated_service_months+=separated_months
                    
                    actual=emp.employee_id.actual_duration_computation()
                    config_ids=hr_setting.search(cr,uid,[])
                    config_browse=hr_setting.browse(cr, uid, config_ids)[0]
                    settings=config_browse.get_default_add_service()
                    if actual['actual_service_years'] >= settings['add_service']: 
                        res.update({'separated_service_months': int(separated_service_months), 'separated_service_days': separated_service_days, 'separated_service_years': separated_service_years})
            emp_obj.write(cr,uid,rec.employee_id.id,res)
            print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>...res",res,rec.employee_id.id
        return res

    def set_to_draft(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to draft.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        res=self.service_duration_computation(cr,uid,ids)
        return True

    def confirm(self, cr, uid, ids,context=None):
        """
        Workflow function change record state to 'confirm'
        @return: boolean True 
        """
        emp_obj=self.pool.get("hr.employee")
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.employee_id.first_employement_date > rec.start_date:
                emp_obj.write(cr,uid,rec.employee_id.id,{'first_employement_date':rec.start_date})
        self.write(cr, uid, ids, {'state':'confirm'})
        res=self.service_duration_computation(cr,uid,ids)
        return True 

#--------------------------
#   Health Status
#--------------------------

class health_status(osv.osv):
    """ To Add Employee Health Status"""
    _name = "health.status"
    _columns = {
        'name': fields.char('Health Status', size=256),
    }

#----------------------------------------
# Employee (Inherit) 
# Adding new fields
#----------------------------------------
class hr_employee(osv.Model):

    _inherit = "hr.employee"

    def get_date(self,str):
        return datetime.strptime(str, "%Y-%m-%d")

    '''def _get_connected_service(self, cr, uid, ids, context=None):
        """
        Count the numer of employees in the job
           
        @return: list of employee IDs
        """
        res = []
        emp=self.pool.get('hr.additional.service').browse(cr, uid, ids, context=context)[0]
        emp_services=self.pool.get('hr.additional.service').search(cr, uid, [('employee_id','=',emp.employee_id.id)], context=context)
        for rec in self.pool.get('hr.additional.service').browse(cr, uid, emp_services, context=context):
            if rec.state == 'confirm':
                res.append(rec.id)
        return res

    def _connected_duration_computation(self, cr, uid, ids,field_name, default=None, context=None):
        res={}
        """
        ====
        """
        hr_setting = self.pool.get('hr.config.settings')
        separated_days=0
        separated_service_days=0
        separated_service_months=0
        separated_service_years=0

        connected_days=0
        connected_service_days=0
        connected_service_months=0
        connected_service_years=0
        #emp=self.pool.get('hr.additional.service').browse(cr, uid, ids, context=context)[0]
        #emp_services=self.pool.get('hr.additional.service').search(cr, uid, [('employee_id','=',emp.employee_id.id)], context=context)
        for emp in self.pool.get('hr.additional.service').browse(cr, uid, ids, context=context):
        
            if emp.service_type=='connected':
                connected_service_months+=emp.months
                connected_service_years+=emp.years
                connected_days+=emp.days
                if connected_days >= 30:
                    connected_service_days=connected_days%30
                    connected_service_months+=connected_days/30
                else:
                    connected_service_days+=connected_days
                res.update({emp.employee_id.id:{'connected_service_months': int(connected_service_months), 'connected_service_days': connected_service_days, 'connected_service_years': connected_service_years}})
        
            if emp.service_type=='separated':
                separated_service_months+=emp.months
                separated_service_years+=emp.years
                separated_days+=emp.days
                if separated_days >= 30:
                    separated_service_days=separated_days%30
                    separated_service_months+=separated_days/30
                else:
                    separated_service_days+=separated_days
                actual=self.actual_duration_computation(cr,uid, [emp.employee_id.id],context=context)
                config_ids=hr_setting.search(cr,uid,[])
                config_browse=hr_setting.browse(cr, uid, config_ids)[0]
                settings=config_browse.get_default_add_service()
                if actual['actual_service_years'] >= settings['add_service']: 
                    res.update({emp.employee_id.id:{'separated_service_months': int(separated_service_months), 'separated_service_days': separated_service_days, 'separated_service_years': separated_service_years}})
        return res'''

    '''def read(self, cr, user, ids, fields=None, context=None, load='_classic_read'):
        res = super(hr_employee, self).read(cr, user, ids, fields, context, load)
        print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>read"
        self.actual_duration_computation(cr, user, ids,context=context)
        return res'''

    def lost_duration_computation(self, cr, uid, ids,context=None):
        res={}
        """
        get Lost service From Holidays and illness
        """
        holi_obj=self.pool.get('hr.holidays')
        illness_obj=self.pool.get('hr.employee.illness')
        for rec in self.browse(cr,uid,ids,context=context):
            res[rec.id]={
                'lost_service_days':0.0,
                'lost_service_months':0.0,
                'lost_service_years':0.0,
            }
            days=0
            months=0
            lost_service_days=0
            lost_service_months=0
            lost_service_years=0

            holi_ids=holi_obj.search(cr,uid,[('employee_id','=',rec.id),('state','=','validate')])
            illness_ids=illness_obj.search(cr,uid,[('employee_id','=',rec.id),('state','=','done')])
            print">>>>>>>>>>>>>>>>>>>>>>>>>>>holi_ids",holi_ids,ids
            for holi in holi_obj.browse(cr,uid,holi_ids,context=context):
                if holi.holiday_status_id.absence or holi.holiday_status_id.payroll_type == 'unpaied':
                    # and holi.state == 'validate'
                    df=datetime.strptime(holi.date_from,'%Y-%m-%d %H:%M:%S').date()
                    dt=datetime.strptime(holi.date_to,'%Y-%m-%d %H:%M:%S').date()
                    date=relativedelta(dt,df)

                    days+=date.days
                    months+=date.months
                    lost_service_years+=date.years

                    if days >= 30:
                        lost_service_days=days%30
                        lost_service_months+=days/30
                    else:
                        lost_service_days+=days

                    if months >= 12:
                        lost_service_months=months%12
                        lost_service_years+=months/12
                    else:
                        lost_service_months+=months

            days=0
            months=0

            for illness in illness_obj.browse(cr,uid,illness_ids,context=context):
                df=datetime.strptime(illness.date,'%Y-%m-%d')
                dt=datetime.strptime(illness.end_date,'%Y-%m-%d')
                date=relativedelta(dt,df)

                days+=date.days
                months+=date.months
                lost_service_years+=date.years

                if days >= 30:
                    lost_service_days=days%30
                    lost_service_months+=days/30
                else:
                    lost_service_days+=days

                if months >= 12:
                    lost_service_months=months%12
                    lost_service_years+=months/12
                else:
                    lost_service_months+=months


            res = {'lost_service_years':lost_service_years,'lost_service_months':lost_service_months,'lost_service_days':lost_service_days}
            self.write(cr,uid,rec.id,res,context=context)
            
        return res

    def actual_duration_computation(self, cr, uid, ids,context=None):
        res={}
        """
        get difference between start date and end date
        """
        for rec in self.browse(cr,uid,ids,context=context):
            actual_service_years=0
            actual_service_months=0
            actual_service_days=0
            lost=rec.lost_duration_computation()
            res[rec.id]={
                'actual_service_days':0.0,
                'actual_service_months':0.0,
                'actual_service_years':0.0,
            }
            if rec.recruitment_date:
                df=datetime.strptime(rec.recruitment_date,'%Y-%m-%d')
            else:
                df=datetime.strptime(rec.employment_date,'%Y-%m-%d')
            now=str(datetime.now().date())
            dt=datetime.strptime(now,'%Y-%m-%d')
            date=relativedelta(dt,df)
            actual_service_years=date.years
            actual_service_months=date.months
            actual_service_days=date.days
            if lost['lost_service_days'] > actual_service_days:
                days=lost['lost_service_days'] - actual_service_days
                actual_service_months-=1
                actual_service_days=30 - days
            else:
                actual_service_days-=lost['lost_service_days']

            if lost['lost_service_months'] > actual_service_months:
                months=lost['lost_service_months'] - actual_service_months
                actual_service_years-=1
                actual_service_months=12 - months
            else:
                actual_service_months-=lost['lost_service_months']
                
            actual_service_years-=lost['lost_service_years']

            qual = rec.qualification_ids
            qual = filter(lambda x: x.emp_qual_id.special and x.state == 'approved' and self.get_date(x.qual_date) < dt,qual) or []
            if qual:
                qual = min(qual, key=lambda x: self.get_date(x.qual_date)) or []
                qual_date = self.get_date(qual.qual_date)
                date = dt - qual_date
                days = date.days
                days *= 0.5
                days = round(days,0)
                years = int(days) / 365
                remain = int(days) % 365
                monthes = int(remain) / 30
                remain = remain % 30
                days = remain
                actual_service_years += years
                actual_service_months += monthes
                actual_service_days += days
            res = {'actual_service_years':actual_service_years,'actual_service_months':actual_service_months,'actual_service_days':actual_service_days}
            self.write(cr,uid,rec.id,res,context=context)
            
        return res

    def _total_duration_computation(self, cr, uid, ids,field_name, arg, context={}):
        res={}
        """
        get difference between start date and end date
        """
        for rec in self.browse(cr,uid,ids,context=context):
            res[rec.id]={
                'total_service_days':rec.connected_service_days+rec.separated_service_days+rec.actual_service_days+rec.operation_service_days,
                'total_service_months':rec.connected_service_months+rec.separated_service_months+rec.actual_service_months+rec.operation_service_months,
                'total_service_years':rec.connected_service_years+rec.separated_service_years+rec.actual_service_years+rec.operation_service_years,
            }
            
        return res

    _columns = {
        'is_isolated' : fields.boolean('Isolated') , 
        'recruitment_date' : fields.date('Recruitment Date', required=True, readonly=True, states={'draft':[('readonly', False)]}) ,
        'health_status': fields.many2one('health.status','Health Status', readonly=True, states={'draft':[('readonly', False)]}),

        'connected_service_days' :  fields.integer(string='Days',readonly=True),
        'connected_service_months' :  fields.integer(string='Months',readonly=True),
        'connected_service_years' :  fields.integer(string='Years',readonly=True),

        'separated_service_days' :  fields.integer(string='Days',readonly=True),
        'separated_service_months' :  fields.integer(string='Months',readonly=True),
        'separated_service_years' :  fields.integer(string='Years',readonly=True),

        'actual_service_days' :  fields.integer(string='Days',readonly=True),
        'actual_service_months' :  fields.integer(string='Months',readonly=True),
        'actual_service_years' :  fields.integer(string='Years',readonly=True),

        'operation_service_days' :  fields.integer(string='Days',readonly=True),
        'operation_service_months' :  fields.integer(string='Months',readonly=True),
        'operation_service_years' :  fields.integer(string='Years',readonly=True),

        'lost_service_days' :  fields.integer(string='Days',readonly=True),
        'lost_service_months' :  fields.integer(string='Months',readonly=True),
        'lost_service_years' :  fields.integer(string='Years',readonly=True),

        'total_service_days' :  fields.function(_total_duration_computation,multi='total',string='Days',readonly=True,
                                store = {'hr.employee': (lambda self, cr, uid, ids, c={}: ids, ['connected_service_days','separated_service_days','actual_service_days','operation_service_days'],10)}),
        'total_service_months' :  fields.function(_total_duration_computation,multi='total',string='Months',readonly=True,
                                store = {'hr.employee': (lambda self, cr, uid, ids, c={}: ids, ['connected_service_months','separated_service_months','actual_service_months','operation_service_months'],10)}),
        'total_service_years' :  fields.function(_total_duration_computation,multi='total',string='Years',readonly=True,
                                store = {'hr.employee': (lambda self, cr, uid, ids, c={}: ids, ['connected_service_years','separated_service_years','actual_service_years','operation_service_years'],10)}),

        'military_training_id' : fields.one2many('hr.military.training' ,'employee_id' ,string="Training Military"),
        'service_state_id' : fields.many2one('hr.service.state' , string="Service State")
    }

    _defaults = {
        'connected_service_days'  :0,
        'connected_service_months':0,
        'connected_service_years' :0,
        'separated_service_days'  :0,
        'separated_service_months':0,
        'separated_service_years' :0,
        'actual_service_days'  :0,
        'actual_service_months':0,
        'actual_service_years' :0,
        'operation_service_days'  :0,
        'operation_service_months':0,
        'operation_service_years' :0,
        'lost_service_days'  :0,
        'lost_service_months':0,
        'lost_service_years' :0,
        'total_service_days'  :0,
        'total_service_months':0,
        'total_service_years' :0,
    }

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

        if 'move_order_line_ids' in context:
            emp_ids = resolve_o2m_operations(cr, uid, self.pool.get('hr.move.order.line'),
                                              context.get('move_order_line_ids'), ["employee_id"], context)
            args.append(('id', 'not in', [isinstance(d['employee_id'], tuple) and d['employee_id'][0] or d['employee_id'] for d in emp_ids]))
        
        if 'illness' in context:
            emp_ids = resolve_o2m_operations(cr, uid, self.pool.get('hr.employee.illness'),
                                              context.get('illness'), ["employee_id"], context)
            args.append(('id', 'not in', [isinstance(d['employee_id'], tuple) and d['employee_id'][0] or d['employee_id'] for d in emp_ids]))
        

        if 'same' in context:
            emp_ids = resolve_o2m_operations(cr, uid, self.pool.get('hr.employee.mission.line'),
                                              context.get('same'), ["employee_id"], context)
            args.append(('id', 'in', [isinstance(d['employee_id'], tuple) and d['employee_id'][0] or d['employee_id'] for d in emp_ids]))
        return super(hr_employee, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)









