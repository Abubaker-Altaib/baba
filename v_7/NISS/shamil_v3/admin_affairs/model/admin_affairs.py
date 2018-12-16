# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv, fields
from openerp.tools.translate import _
from lxml import etree
from openerp.osv.orm import setup_modifiers
import openerp.addons.decimal_precision as dp
import time
import datetime
from openerp.addons.account_voucher.account_voucher import resolve_o2m_operations

#--------------------------
#   Vehicle Out Department
#--------------------------
class vehicle_out_department(osv.osv):
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _dept_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _name = "vehicle.out.department"
    _columns = {
        'name': fields.char('Department Name', size=64, required=True),
        'complete_name': fields.function(_dept_name_get_fnc, type="char", string='Name'),
        'company_id': fields.many2one('res.company', 'Company', select=True, required=False),
        'parent_id': fields.many2one('vehicle.out.department', 'Parent Department', select=True),
        'child_ids': fields.one2many('vehicle.out.department', 'parent_id', 'Child Departments'),
        'note': fields.text('Note'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.department', context=c),
                }

    def _check_recursion(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from vehicle_out_department where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error! You cannot create recursive departments.', ['parent_id'])
    ]
#--------------------------
#   Vehicle License
#--------------------------
class  driving_license(osv.osv):
    """ To manage driving license of employee """
    _name = "driving.license"
    _columns = {
        'employee_id': fields.many2one('hr.employee', "Employee",required=True),
        'degree_id': fields.related('employee_id','degree_id',type="many2one",relation="hr.salary.degree",string="Degree",readonly=1),
        'license_no': fields.char(string="License No" ,required=True),
        'license_type': fields.selection([('ownership', 'Ownership'), ('commercial', 'Commercial'), ('general', 'General')], 'License Type'),
        'license_date': fields.date(string="License Date"),
        'end_date': fields.date(string="License End Date" ,required=True),
        'state': fields.selection([('draft', 'Draft'), ('confirm', 'Confirm')], 'State'),
        'notes': fields.text('Notes', size=256 ), 
        'company_id': fields.related('employee_id','company_id',type="many2one",relation='res.company',string="company",readonly=1),
    }

    _defaults = {
        'state' : 'draft',
    }

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft']:
                raise osv.except_osv(_('Warning!'),_('You cannot delete record that is not in draft state.'))
        return super(driving_license, self).unlink(cr, uid, ids, context)

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.license_no + '-' + record.license_type
            res.append((record.id, name))
        return res

    def confirm(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to confirm.

        @return: Boolean True
        """
        for rec in self.browse(cr, uid, ids, context):
            rec.write({'state': 'confirm'})
        return True

    def set_to_draft(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to confirm.

        @return: Boolean True
        """
        for rec in self.browse(cr, uid, ids, context):
            rec.write({'state': 'draft'})
        return True

    def _check_unique(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a place with the same name

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            idss = self.search(cr,uid, [('employee_id', '=', rec.employee_id.id),('id','!=',rec.id)])
            if idss:
                raise osv.except_osv(_('ERROR'), _('This employee already have license record (%s)') % (rec.license_no +"-"+ rec.license_type))
            num = self.search(cr,uid, [('license_type', '=', rec.license_type),('license_no', '=', rec.license_no),('id','!=',rec.id)])
            if num:
                raise osv.except_osv(_('ERROR'), _('License No must Be unique'))
        return True

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            num=rec.license_no.strip()
            if not num:
                raise osv.except_osv(_('ValidateError'), _("License No must not be spaces"))
        return True


    _sql_constraints = [
        ('license_no_uniqe', 'unique(license_no)', 'you can not create same License No !'),
        ('date_check',"CHECK (end_date > license_date)",_("License date must be before End date!")),
    ]

    _constraints = [
         (_check_unique, '', []),
         (_check_spaces, '', []),
    ]

    def create(self, cr, uid, vals, context=None):
        """
        Override create method to check if license_no contains spaces
        @return: super create method
        """
        if 'license_no' in vals:
            vals['license_no'] = vals['license_no'].strip()
        
        return super(driving_license, self).create(cr, uid, vals, context=context)

class admin_affairs_account(osv.osv):
    """To manage admin affairs account """
    _name = "admin_affairs.account"

    _description = 'Admin Affairs Account'

    _rec_name = "model_id"


    def _model_ids(self,cr,uid,context=None):
        List = []
        model_obj = self.pool.get("ir.model")
        search_ids = model_obj.search(cr,uid,[],context=context)
        for mo in model_obj.browse(cr,uid,search_ids,context=context):
            modules = mo.modules.split(',')
            flag = 'service' in modules or 'fleet' in modules
            flag = flag or 'admin_affairs' in modules or 'fuel_management' in modules 
            if flag:
                List.append( str(mo.id))
        return List


    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """ Returns views and fields for current model.
        @param cr: A database cursor
        @param user: ID of the user currently logged in
        @param view_id: list of fields, which required to read signatures
        @param view_type: defines a view type. it can be one of (form, tree, graph, calender, gantt, search, mdx)
        @param context: context arguments, like lang, time zone
        @param toolbar: contains a list of reports, wizards, and links related to current model

        @return: Returns a dictionary that contains definition for fields, views, and toolbars
        """
        if not context:
            context = {}
        res = super(admin_affairs_account, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)

        for field in res['fields']:
            if field == 'model_id':
                res['fields'][field]['domain'] = [('id','in',
                    self._model_ids(cr,uid,context=context)),('osv_memory','=',False)]
        return res

    _columns = {
        'model_id': fields.many2one('ir.model','Model',required=True),
        'journal_id': fields.property('account.journal', required=True,type='many2one', relation='account.journal',
                                      string='Journal', method=True, view_load=True),                        
        'account_id': fields.property('account.account',type='many2one', relation='account.account', 
                                      string='Account', method=True, view_load=True,required=True),
        'analytic_id': fields.property('account.analytic.account', type='many2one', relation='account.analytic.account',
                                       string='Analytic Account', method=True, view_load=True),
        'notes': fields.text('Notes', size=256 ), 

    }

    _sql_constraints = [
        ('model_uniq', 'unique(model_id)', _('The Model Must Be Unique For Each Service!')),
    ]
class  vehicle_category(osv.osv):
    """ To manage vehicle categories """
    _name = "vehicle.category"
    _columns = {
        'name': fields.char(string="Name" ,required=True),
        #'license_cost': fields.float(string="License Cost"),
        'vehicle_model_id': fields.many2one('fleet.vehicle.model','Fleet Model'),
        'company_id': fields.many2one('res.company','company'),
        'share': fields.boolean(string="share Category"),
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
        'share' : 0,
        'company_id' : _default_company
    }

    def check_name(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a place with the same name

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            idss = self.search(cr,uid, [('name', '=', rec.name),('id','!=',rec.id)])
            if idss:
                raise osv.except_osv(_('ERROR'), _('This category name is already exisit for the company %s') % (rec.company_id.name))
        return True

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ','')) <= 0):
                raise osv.except_osv(_('ValidateError'), _("name must not be spaces"))
        return True

    _constraints = [
         (check_name, '', []),
         (_check_spaces, '', ['name'])
    ]

    

    _sql_constraints = [
        ('vehicle_category_uniqe', 'unique(name)', 'you can not create same name !')
    ]

    def create(self, cr, uid, vals, context=None):
    	"""
        Override create method to check if category name contains spaces
        @return: super create method
        """
        if 'name' in vals:
            vals['name'] = vals['name'].strip()
        
        return super(vehicle_category, self).create(cr, uid, vals, context=context)
    
    '''def _check_negative(self, cr, uid, ids, context=None):
        """ 
        Check the value of license cost,
        if greater than zero or not.

        @return: Boolean of True or False
        """
        count = 0
        for act in self.browse(cr, uid, ids, context):
            message = _("The Value Of ")
            if (act.license_cost < 0):
                message = message + _("License Cost") 
                count = count + 1
            message = message + _(" Must Be Positive Value!")
        if count > 0 :
            raise osv.except_osv(_('ValidateError'), _(message)) 
        return True
    _constraints = [
        (_check_negative, _(''), ['license_cost'])
    ]'''

class  vehicle_place(osv.osv):
    """ To manage vehicle places """
    _name = "vehicle.place"
    _columns = {
        'name': fields.char(string="Name" ,required=True),
        'company_id': fields.many2one('res.company','company'),
        'share': fields.boolean(string="share Category"),
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
        'share' : 0,
        'company_id' : _default_company
    }

    def check_name(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a place with the same name

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            idss = self.search(cr,uid, [('name', '=', rec.name),('id','!=',rec.id)])
            if idss:
                raise osv.except_osv(_('ERROR'), _('This place name is already exisit for the company %s') % (rec.company_id.name))
        return True

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ','')) <= 0):
                raise osv.except_osv(_('ValidateError'), _("name must not be spaces"))
        return True


    _sql_constraints = [
        ('vehicle_place_name_uniqe', 'unique(name)', 'you can not create same name !')
    ]

    _constraints = [
         (check_name, '', []),
         (_check_spaces, '', ['name'])
    ]

    def create(self, cr, uid, vals, context=None):
    	"""
        Override create method to check if place name contains spaces
        @return: super create method
        """
        if 'name' in vals:
            vals['name'] = vals['name'].strip()
        
        return super(vehicle_place, self).create(cr, uid, vals, context=context)


#--------------------------
#   Vehicle Accident
#--------------------------

class  vehicle_accident(osv.osv):
    """ To manage vehicle Accident process """
    _name = "vehicle.accident"
    _columns = {
        'police_department': fields.char(string="Police department" , size=156),
        'report_no':fields.char(string="Report number" , size=156),

        'license_no': fields.char(string="License No"),
        'license_type': fields.selection([('ownership', 'Ownership'), ('commercial', 'Commercial'), ('general', 'General')], 'License Type'),
        'license_end_date': fields.date(string="License End Date"),

        'employee_id': fields.many2one("hr.employee", string="Employee"),
        'out_driver': fields.char('Driver'),
        'out': fields.boolean("Out"),
        'vehicle_id': fields.many2one('fleet.vehicle',string="Vehicle" ,required=True),
        'accident_date': fields.date(string="Accident Date" ,required=True),
        'accident_place': fields.char(string="Accident Place" , size=156,required=True),
        #'driver_id': fields.related('vehicle_id','driver_id',type="many2one",relation="res.partner",string="Driver",readonly=1,store=True),
        'driver_id': fields.many2one("hr.employee", string="Driver"),
        'members_ids': fields.many2many('hr.employee', 'accident_members_rel', 'emp_id', 'member_id', 'Committee members'),
        'decision': fields.text('Decision'),
        'notes': fields.text('Notes'),
        'accident_type': fields.selection([('criminal','Criminal'),('non_criminal','Non-criminal')],string="Accident Type",required=True),
        'wrong':fields.boolean('Is the employee wrong?'),
        'traffic_report':fields.boolean('Receipt Traffic police report'),
        'state_report':fields.boolean('State report'),
        'court_attach':fields.boolean('Court attachment'),
        #'insurance_report':fields.boolean('Is the insurance report was printed?'),
        'state': fields.selection([('draft', 'Draft'), ('done', 'Done'),('committee','Wait Committee'),('vehicle_dept','vehicle department'),('maintenace_dept','maintenace department'), ('refuse', 'Refuse')], 'State'),
        'company_id': fields.many2one('res.company','company'),
    	'hq': fields.boolean("HQ"),
    	'license_id' : fields.many2one('driving.license', 'License'),
    }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id

        return company
    def _default_hq(self,cr,uid,context=None):
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        if not user.company_id.hq:
            hq = True
        else:
            hq = False
        return hq

    _defaults ={
    'accident_date': lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
    'state':'draft',
    'company_id' : _default_company,
    'hq':_default_hq,
    'out':False,
    }


    def onchange_vehicle_id(self, cr, uid, ids, vehicle_id,context=None):
        """
        to set license driving data.

        @param emp_id: Id of vehicle
        @return: Dictionary of values 
        """
        vehicle_obj = self.pool.get('fleet.vehicle')
        driving_obj = self.pool.get('driving.license')
        vals={}
        driving_ids = []
        vals.update({'employee_id': False,'driver_id':False,'license_id': False,'license_no':False,
            'license_type':False, 'license_end_date':False,'out_driver':False,'out':False})
        if vehicle_id:
            vehicle = vehicle_obj.browse(cr, uid, vehicle_id, context=context)
            if vehicle.belong_to == 'out':
                vals['out']=True
                vals['out_driver'] = vehicle.out_driver
            if vehicle.employee_id:
                driving_ids = driving_obj.search(cr,uid, [('employee_id', '=', vehicle.employee_id.id),('state','=','confirm')])
                vals['employee_id']= vals['driver_id']= vehicle.employee_id.id
            if vehicle.driver:
                driving_ids = driving_obj.search(cr,uid, [('employee_id', '=', vehicle.driver.id),('state','=','confirm')])
                vals['driver_id']=vehicle.driver.id
                if not vehicle.employee_id:
                    vals['employee_id']=vehicle.driver.id
            
            if driving_ids:
                driving = driving_obj.browse(cr, uid, driving_ids, context=context)[0]     
                vals.update({'license_id':driving.id ,'license_no':driving.license_no,'license_type':driving.license_type,'license_end_date':driving.end_date})
        return {'value':vals}

    def onchange_driver_id(self, cr, uid, ids, driver_id, context={}):
        """
        to set license driving data.

        @param emp_id: Id of vehicle
        @return: Dictionary of values 
        """
        vehicle_obj = self.pool.get('fleet.vehicle')
        driving_obj = self.pool.get('driving.license')
        vals = {}
        vals.update({'license_id': False,'license_no':False,'license_type':False,'license_end_date':False})
        driving_ids = []
        if driver_id:
            driving_ids = driving_obj.search(cr,uid, [('employee_id', '=', driver_id),('state','=','confirm')])
            if driving_ids:
                driving = driving_obj.browse(cr, uid, driving_ids, context=context)[0]     
                vals.update({'license_id':driving.id ,'license_no':driving.license_no,'license_type':driving.license_type,'license_end_date':driving.end_date})
            
        return {'value':vals}

    def create(self, cr, uid, vals, context=None):
        """
        to set license driving data.

        @param vals: Dictionary contains the enterred values
        @return: Super create Mehtod
        """
        value={}
        vehicle_obj = self.pool.get('fleet.vehicle')
        driving_obj = self.pool.get('driving.license')
        vehicle = vehicle_obj.browse(cr, uid, vals['vehicle_id'], context=context)
        driving_ids = []
        driver_id = vals['driver_id']
        if vehicle.belong_to == 'out':
            vals['out']=True

        onchange_vals = self.onchange_vehicle_id(cr, uid, [], vals['vehicle_id'])
        onchange_vals_driver = self.onchange_driver_id(cr, uid, [], vals['driver_id'])

        if onchange_vals['value']: vals.update(onchange_vals['value'])
        if onchange_vals_driver['value']: vals.update(onchange_vals_driver['value'])

        vals.update({'driver_id':driver_id})
        
        
        return super(vehicle_accident, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        to set license driving data.

        @param vals: Dictionary contains the enterred values
        @return: Super write Mehtod
        """
        custody_pool = self.pool.get('vehicle.custody.move')
        driving_obj = self.pool.get('driving.license')
        vehicle_obj = self.pool.get('fleet.vehicle')
        for rec in self.browse(cr, uid, ids, context=context):
            driving_ids = []
            if 'vehicle_id' in vals:
                vehicle = vehicle_obj.browse(cr, uid, vals['vehicle_id'], context=context)
                if vehicle.belong_to == 'out':
                    vals['out']=True
                onchange_vals = self.onchange_vehicle_id(cr, uid, ids, vals['vehicle_id'])
                onchange_vals_driver = self.onchange_driver_id(cr, uid, ids, onchange_vals['value']['driver_id'])

                if onchange_vals['value']: vals.update(onchange_vals['value'])
                if onchange_vals_driver['value']: vals.update(onchange_vals_driver['value'])
                
            if ('driver_id' in vals) and (not 'vehicle_id' in vals) and rec.state == 'draft':
                onchange_vals_driver = self.onchange_driver_id(cr, uid, ids, vals['driver_id'])
                if onchange_vals_driver['value']: vals.update(onchange_vals_driver['value'])

            if not rec.license_id and (not 'driver_id' in vals or 'driver_id' in vals) and rec.state == 'draft':
                if rec.driver_id:
                    driving_ids = driving_obj.search(cr,uid, [('employee_id', '=', rec.driver_id.id),('state','=','confirm')])
                    if driving_ids:
                        driving = driving_obj.browse(cr, uid, driving_ids, context=context)[0]     
                        vals.update({'license_id':driving.id ,'license_no':driving.license_no,'license_type':driving.license_type,'license_end_date':driving.end_date})

                
        return super(vehicle_accident, self).write(cr, uid, ids, vals)

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.vehicle_id.name + '-' + record.accident_type + '-'+record.accident_date
            res.append((record.id, name))
        return res


    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft']:
                raise osv.except_osv(_('Warning!'),_('You cannot delete record that is not in draft state.'))
        return super(vehicle_accident, self).unlink(cr, uid, ids, context)


    def to_vehicle_dept(self,cr,uid,ids,context=None):
        """
        Mehtod that check go to vehicle_dept state constraints .

        @return: Boolean True
        """
        driving_obj = self.pool.get('driving.license')
        for rec in self.browse(cr, uid, ids, context):
            #if rec.state == 'vehicle_dept':
            vals = {}
            if (not rec.out and not rec.driver_id) or (rec.out and not rec.out_driver):
                print ">>>>>>>>>>>>>>>>>>driver",rec.out,rec.driver_id,rec.out_driver
                raise osv.except_osv(_('ValidateError'), _("Please select driver"))
            
            if rec.driver_id and not rec.license_id:
                driving_ids = driving_obj.search(cr,uid, [('employee_id', '=', rec.driver_id.id),('state','=','confirm')])
                if driving_ids:
                    driving = driving_obj.browse(cr, uid, driving_ids, context=context)[0]     
                    vals.update({'license_id':driving.id ,'license_no':driving.license_no,'license_type':driving.license_type,'license_end_date':driving.end_date})
                    self.write(cr, uid, ids, vals, context)
                elif not driving_ids and not rec.out:
                    raise osv.except_osv(_('ValidateError'), _("There is No license driving data For This Employee."))
            attachment=self.pool.get('ir.attachment').search(cr,uid,[('res_model','=','vehicle.accident'),('res_id','=',ids[0])],context=context)
            if rec.hq:
                if rec.accident_type == 'criminal' and len(attachment) < 2:
                    raise osv.except_osv(_('ValidateError'), _("you must attach driving license and Report of the engineer of the insurance company."))
                    return False
                elif not attachment:
                    raise osv.except_osv(_('ValidateError'), _("you must attach driving license."))
                    return False
            else:
                if rec.accident_type == 'criminal' and len(attachment) < 3:
                    raise osv.except_osv(_('ValidateError'), _("you must attach:-\n 1- driving license \n 2- Report of the engineer of the insurance company \n 3- state Report."))
                    return False
                elif not attachment:
                    raise osv.except_osv(_('ValidateError'), _("you must attach driving license."))
                    return False
        return True

    def check_attach(self,cr,uid,ids,context=None):
        """
        Mehtod that check go to vehicle_dept state constraints .

        @return: Boolean True
        """
        for rec in self.browse(cr, uid, ids, context):
            attachment=self.pool.get('ir.attachment').search(cr,uid,[('res_model','=','vehicle.accident'),('res_id','=',ids[0])],context=context)
            if rec.hq:
                if not rec.traffic_report or (rec.accident_type == 'criminal' and len(attachment) < 3) or (rec.accident_type != 'criminal' and len(attachment) < 2):
                    raise osv.except_osv(_('ValidateError'), _("The Traffic police report is not Receipt or attach Yet."))
                    return False
            else:
                if not rec.traffic_report or (rec.accident_type == 'criminal' and len(attachment) < 4) or (rec.accident_type != 'criminal' and len(attachment) < 3):
                    raise osv.except_osv(_('ValidateError'), _("The Traffic police report is not Receipt or attach Yet."))
                    return False
        return True


    def check_to_maintenace(self,cr,uid,ids,context=None):
        """
        Mehtod that check go to maintenace_dept state constraints .

        @return: Boolean True
        """
        attachment=self.pool.get('ir.attachment').search(cr,uid,[('res_model','=','vehicle.accident'),('res_id','=',ids[0])],context=context)
        for rec in self.browse(cr, uid, ids, context):
            if rec.wrong: 

                if not rec.members_ids:
                    raise osv.except_osv(_('ValidateError'), _("Plase Enter Committee members."))
                    return False
                elif not rec.decision:
                    raise osv.except_osv(_('ValidateError'), _("Plase Enter Committee Decision."))
                    return False
                if rec.hq:
                    if rec.court_attach and ((rec.accident_type == 'criminal' and len(attachment) < 4) or (rec.accident_type != 'criminal' and len(attachment) < 3)):
                        raise osv.except_osv(_('ValidateError'), _("Place attach court Decision."))
                        return False
                else:
                     if rec.court_attach and ((rec.accident_type == 'criminal' and len(attachment) < 5) or (rec.accident_type != 'criminal' and len(attachment) < 4)):
                        raise osv.except_osv(_('ValidateError'), _("Place attach court Decision."))
                        return False
        return True

    def check_to_Done(self,cr,uid,ids,context=None):
        """
        abistract Mehtod that check go to Done state constraints .

        @return: Boolean True
        """
        return True


    def _check_driver(self, cr, uid, ids, context={}):
        """
        Check if there is driver or not .

        @return: Boolean True
        """
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state == 'vehicle_dept':
                if (not rec.out and not rec.driver_id) or (rec.out and not rec.out_driver):
                    raise osv.except_osv(_('ValidateError'), _("Please select driver"))
                if rec.driver_id and not rec.license_id:
                    raise osv.except_osv(_('ValidateError'), _("There is No license driving data For This Employee."))
        return True

    _constraints = [
        (_check_driver, '', ['state']),
     ]

#--------------------------
#   Vehicle Custody Move
#--------------------------

class  vehicle_custody_move(osv.osv):
    """ To manage vehicle custody move process """
    _name = "vehicle.custody.move"
    _columns = {
        'before_custody_ids' :fields.many2many('fleet.vehicle.custody', 'before_custody_rel', 'vehicle_custody_id','custody_id', 'Before Custody'),
        'after_custody_ids' :fields.many2many('fleet.vehicle.custody', 'after_custody_rel', 'vehicle_custody_id','custody_id', 'After Custody'),
        'vehicle_id': fields.many2one('fleet.vehicle',string="Vehicle" ,required=True),
        'move_id':fields.many2one('vehicle.move','related vehicle move'),       
    }


#--------------------------
#   Vehicle Move
#--------------------------

class  vehicle_move(osv.osv):
    """ To manage vehicle move and assigning process """
    _name = "vehicle.move"
    _columns = {
        'name':fields.char('Name',readonly=1),
        'place_id': fields.many2one('vehicle.place', 'Vehicle Place'),
        'custody_move_id': fields.many2one('vehicle.custody.move', 'vehicle custody move'),
        'move_date': fields.date(string="Move Date" ,required=True),
        #'assign_type': fields.selection([('internal','Internal'),('external','External')],string="Assign Type"),
        'move_type': fields.selection([('assign','Assign'),('return','Return'),('assign_oc','Assign OC'),('return_oc','Return OC'),('other','Other')],string="Move Type",required=True),
        'use': fields.many2one('fleet.vehicle.use','Use',required=True),
        'use_type': fields.char(string="Use Type"),
        'custody_ids' :fields.many2many('fleet.vehicle.custody', 'fleet_move_vehicle_custody_rel', 'vehicle_custody_id','custody_id', 'Custody'),
        'vehicle_status':fields.selection([('operation', 'Operational Use'), ('internal', 'Internal Use'),('supply_custody', 'Supply Custody'),
            ('disabled', 'Disabled'),('off', 'Off'),('custody', 'Custody'),('sold', 'Sold'),('for_sale', 'For Sale'),
            ('removal', 'Removal'),('missing', 'Missing')], 'Vehicle Status',required=False),
        'vehicle_id': fields.many2one('fleet.vehicle',string="Vehicle" ,required=True),
        'out_driver': fields.char('Driver'),
        'out_department': fields.many2one('vehicle.out.department', 'External Department'),
        'out': fields.boolean("Out"),
        #'vehicle_place': fields.related('vehicle_id','location',type="many2one",relation="vehicle.place",string="current location",readonly=1),
        'vehicle_place': fields.many2one('vehicle.place', 'current location'),
        'department_id':fields.many2one('hr.department','Department',readonly=True),
        'body_id': fields.related('vehicle_id','vin_sn',type="char",string="Chassis Number",readonly=1),
        'license_plate': fields.related('vehicle_id','license_plate',type="char",string="vehicle License Plate",readonly=1),
        #'driver_id': fields.many2one('res.partner', 'Driver'),
        'driver_id': fields.many2one('hr.employee', 'Driver'),
        'employee_id': fields.many2one('hr.employee', "Employee"),
        'degree_id': fields.related('employee_id','degree_id',type="many2one",relation="hr.salary.degree",string="Degree",readonly=1),
        'state': fields.selection([('draft', 'Draft'), ('done', 'Done'),('receipt','Receipt'),('delivery','Delivery'),('refuse','Refuse')], 'State'),
        'comment': fields.text('Notes'),
        'company_id': fields.many2one('res.company','company'),
        'responser': fields.many2one('res.users', "Responser", required=True),
        'hq': fields.boolean("HQ"),
        'share': fields.boolean("Share"),
        'previous_employee_id':fields.many2one('hr.employee', "Previous Employee"),
        'previous_old_system_driver':fields.char("Previous old system driver"),
        'previous_department_id':fields.many2one('hr.department','Previous Department'),
        'previous_use':fields.many2one('fleet.vehicle.use','Previous Use'),
    }

    def _default_company(self,cr,uid,context=None):
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    def _default_hq(self,cr,uid,context=None):
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        if user.company_id.hq:
            hq = True
        else:
            hq = False
        return hq

    _defaults ={
    'share':False,
    'out':False,
    'hq':_default_hq,
    'move_date': lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
    'state':'draft',
    'company_id' : _default_company,
    'responser':lambda self, cr, uid, context: uid,
    }

    """_sql_constraints = [
        ('assign_uniq', 'unique(move_date,vehicle_id,move_type)', _("You can't Do same operation to same vehicle in same date!")),
    ]"""

    def onchange_out_driver(self, cr, uid, ids, out_driver):
        """
        check if out_driver contains space and return it without space
        """
        vals = {}
        if out_driver:
            vals['out_driver'] = out_driver.strip()

        return {'value': vals}

    def create(self, cr, uid, vals, context=None):
        """
        Mehtod to create Vehicle Custody Move from move process.

        @param vals: Dictionary contains the enterred values
        @return: Super create Mehtod
        """
        value={}
        custody_pool = self.pool.get('vehicle.custody.move')
        vehicle_obj = self.pool.get('fleet.vehicle')
        vehicle = vehicle_obj.browse(cr, uid, vals['vehicle_id'], context=context)
        emp_name=False
        emp_name_old=False
        if vehicle.employee_id:
            emp_name = vehicle.employee_id.id
        elif vehicle.driver:
            emp_name = vehicle.driver.id or False
        else:
            emp_name_old = vehicle.old_system_driver and vehicle.old_system_driver or False

        if vals['move_type'] in ('assign_oc','return_oc'):
            vals['share']=True

        seq = self.pool.get('ir.sequence').next_by_code(cr, uid, 'vehicle.move')
        vals['name'] = seq
        if not seq:
            raise  osv.except_osv(_('Warning'), _('No sequence defined!\nPleas contact administartor to configue sequence with code \'vehicle.move\'') )

        
        if vehicle.belong_to == 'out':
            vals['out']=True
        vals.update({'previous_use':vehicle.use.id,'previous_employee_id':emp_name,'previous_old_system_driver':emp_name_old,'previous_department_id':vehicle.department_id.id,'vehicle_place':vehicle.location.id})
        custodys=[]
        for custody in vehicle.custody_ids:
            custodys.append(custody.id)
        value={'after_custody_ids':[(6, 0,custodys)],'vehicle_id':vals['vehicle_id']}
        custody_move_id=custody_pool.create(cr, uid, value, context=context)
        vals['custody_move_id']=custody_move_id
        return super(vehicle_move, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        Mehtod that updates Vehicle Custody Move.

        @param vals: Dictionary contains the enterred values
        @return: Super write Mehtod
        """
        custody_pool = self.pool.get('vehicle.custody.move')
        vehicle_obj = self.pool.get('fleet.vehicle')
        for rec in self.browse(cr, uid, ids, context=context):
            emp_name=False
            emp_name_old=False
            
            if 'vehicle_id' in vals:
                vehicle = vehicle_obj.browse(cr, uid, vals['vehicle_id'], context=context)
                if vehicle.employee_id:
                    emp_name = vehicle.employee_id.id
                elif vehicle.driver:
                    emp_name = vehicle.driver.id or False
                else:
                    emp_name_old = vehicle.old_system_driver and vehicle.old_system_driver or False

                if rec.vehicle_id.belong_to == 'out':
                    vals['out']=True
                vals.update({'previous_use':rec.vehicle_id.use.id,'previous_employee_id':emp_name,'previous_old_system_driver':emp_name_old,'previous_department_id':rec.vehicle_id.department_id.id,'vehicle_place':rec.vehicle_id.location.id})
            if 'vehicle_id' in vals and rec.move_type in ('assign_oc','return_oc'):
                vals['share']=True
            value={}
            if vals.has_key('custody_ids'):
                custodys=[]
                for custody in rec.custody_ids:
                    custodys.append(custody.id)
                value={'after_custody_ids':custodys}
            if not rec.custody_move_id.move_id:
                value={'move_id':rec.id}
            custody_pool.write(cr, uid,rec.custody_move_id.id, value)
        return super(vehicle_move, self).write(cr, uid, ids, vals)

    def onchange_vehicle_id(self, cr, uid, ids, vehicle_id,hq,use,employee_id,department_id,context=None):
        """
        Set default custody_ids.

        @param emp_id: Id of vehicle
        @return: Dictionary of values 
        """
        emp_obj = self.pool.get('hr.employee')
        dept_obj = self.pool.get('hr.department')
        value={}
        domain={}
        value.update({'out_driver':False,'out':False,'out_department':False})
        if not hq:
            domain = {'use':[('type','in',['management','dedicated_managemnet'])]}
        if use:
            value['use_type'] = self.pool.get('fleet.vehicle.use').browse(
                cr, uid, use, context=context).type
            if value['use_type'] == 'dedicated':
                value['employee_id'] = False
                value['department_id'] = False
                domain['employee_id'] = [('state','=','approved')]
                domain['department_id'] = [('id','in',[])]
                if employee_id:
                    #department = emp_obj.browse(cr, uid, employee_id).department_id.id
                    #value['department_id'] = department
                    #domain['department_id'] = [('id','in',[department])]
                    value['employee_id'] = employee_id
                    value['degree_id'] = emp_obj.browse(cr, uid, employee_id).degree_id.id
            else:
                value['employee_id'] = False
                value['department_id'] = False
                domain['employee_id'] = [('state','=','approved')]
                #domain['employee_id'] = [('id','in',[])]
                dep_ids = dept_obj.search(cr,uid,[])
                #domain['department_id'] = [('id','in',dep_ids)]
                if department_id:
                    #department = emp_obj.browse(cr, uid, employee_id).department_id.id
                    #domain['employee_id'] = [('department_id','in',[department_id])]
                    value['department_id'] = department_id
                    if employee_id:
                        department = emp_obj.browse(cr, uid, employee_id).department_id.id
                        value['employee_id'] = department in [department_id] and employee_id or False

        custody_pool = self.pool.get('vehicle.custody.move')
        vehicle_obj = self.pool.get('fleet.vehicle')
        if employee_id:
            value['degree_id'] = emp_obj.browse(cr, uid, employee_id).degree_id.id
        if vehicle_id:
            rec=self.browse(cr, uid, ids, context=context)
            vehicle = vehicle_obj.browse(cr, uid, vehicle_id, context=context)
            emp_name=False
            emp_name_old=False
            if vehicle.employee_id:
                emp_name = vehicle.employee_id.id
            elif vehicle.driver:
                emp_name = vehicle.driver.id or False
            else:
                emp_name_old = vehicle.old_system_driver and vehicle.old_system_driver or False

            if vehicle.belong_to == 'out':
                value['out']=True
                value['out_driver']=vehicle.out_driver
                value['out_department'] = vehicle.out_department.id
            custodys=[]
            for custody in vehicle.custody_ids:
                custodys.append(custody.id)
            value['previous_employee_id']=emp_name
            value['previous_old_system_driver']=emp_name_old
            value['custody_ids']=custodys
            value['vehicle_place']= vehicle.location.id
            value['license_plate']= vehicle.license_plate 
            value['body_id']= vehicle.vin_sn
            vals={'before_custody_ids':[(6, 0,custodys)],'after_custody_ids':[(6, 0,custodys)],'vehicle_id':vehicle_id}
            if rec:
                custody_pool.write(cr, uid,rec[0].custody_move_id.id, vals)
        return {'value':value,'domain':domain}

    def onchange_vehicle_use(self, cr, uid, ids, use,hq, department_id, employee_id, context=None):
        """
        To make employee_id and department_id requierd base on use type.

        @param use: Id of use
        @return: Dictionary of values 
        """
        emp_obj = self.pool.get('hr.employee')
        dept_obj = self.pool.get('hr.department')
        vals={}
        domain={}
        if not hq:
            domain = {'use':[('type','in',['management','dedicated_managemnet'])]}
        if use:
            vals['department_id'] = False
            vals['employee_id'] = False
            vals['use_type'] = self.pool.get('fleet.vehicle.use').browse(
                cr, uid, use, context=context).type
            if vals['use_type'] == 'dedicated':
                vals['employee_id'] = False
                vals['department_id'] = False
                domain['employee_id'] = [('state','=','approved')]
                domain['department_id'] = [('id','in',[])]
                if employee_id:
                    #department = emp_obj.browse(cr, uid, employee_id).department_id.id
                    #vals['department_id'] = department
                    #domain['department_id'] = [('id','in',[department])]
                    vals['employee_id'] = employee_id
            else:
                vals['employee_id'] = False
                vals['department_id'] = False
                domain['employee_id'] = [('id','in',[])]
                dep_ids = dept_obj.search(cr,uid,[])
                domain['department_id'] = [('id','in',dep_ids)]
                if department_id:
                    #department = emp_obj.browse(cr, uid, employee_id).department_id.id
                    #domain['employee_id'] = [('department_id','in',[department_id])]
                    vals['department_id'] = department_id
                    if employee_id:
                        department = emp_obj.browse(cr, uid, employee_id).department_id.id
                        vals['employee_id'] = department in [department_id] and employee_id or False
        return {'value':vals,'domain':domain}

    def onchange_custody_ids(self, cr, uid, ids, custody_ids,context=None):
        """
        Set after_custody_ids in vehicle.custody.move.

        @param emp_id: Id of vehicle
        @return: Dictionary of values 
        """
        vals={}
        custody_pool = self.pool.get('vehicle.custody.move')
        value = {}
        if custody_ids:
            rec=self.browse(cr, uid, ids, context=context)
            custodys=[]
            for custody in custody_ids[0][2]:
                custodys.append(custody)
            vals={'after_custody_ids':[(6, 0,custodys)]}
            if rec:
                custody_pool.write(cr, uid,rec[0].custody_move_id.id, vals)
        return {'value':value}

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft']:
                raise osv.except_osv(_('Warning!'),_('You cannot delete record that is not in draft state.'))
        return super(vehicle_move, self).unlink(cr, uid, ids, context)

    def check_user(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if the user is Allowed to create aprocess

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            if not rec.hq and rec.vehicle_id.use_type not in ['management','dedicated_managemnet']:
                raise osv.except_osv(_('ERROR'), _('Operations Authority Have authority only for Administrative(%s)') % (rec.vehicle_id.name))
            if not rec.hq and rec.use.type not in ['management','dedicated_managemnet']:
                raise osv.except_osv(_('ERROR'), _('The use must be of type management(%s)') % (rec.use.name))
            if rec.move_type in ('assign_oc','return_oc') and rec.use.company_id:
                raise osv.except_osv(_('ERROR'), _('you must Enter Common use in External assign or External return (%s).') % (rec.use.name))

            if (not rec.hq and rec.move_type == 'assign_oc') or (rec.hq and rec.move_type == 'return_oc'):
                raise osv.except_osv(_('ERROR'), _('you are not Allowed to do this operation(%s)') % (rec.move_type))
            if rec.place_id:
                if rec.hq and rec.move_type == 'assign_oc' and (not rec.place_id.share): 
                    raise osv.except_osv(_('ERROR'), _('You must Enter Shared place in External assign(%s)') % (rec.place_id.name))
                if not rec.hq and rec.move_type == 'return_oc' and (not rec.place_id.share):
                    raise osv.except_osv(_('ERROR'), _('You must Enter Shared place in External return(%s)') % (rec.place_id.name))
        return True

    _constraints = [
         (check_user, '', []),
    ]

    def check_assign(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if the user is Allowed to Do assign aprocess

        @return: boolean True or False
        """
        user_obj = self.pool.get('res.users')
        responser = user_obj.browse(cr ,uid, uid)
        for rec in self.browse(cr, uid, ids, context=context):
            if (rec.move_type == 'assign_oc' and not responser.company_id.hq) or (rec.move_type == 'return_oc' and responser.company_id.hq):
                raise osv.except_osv(_('ERROR'), _('you are not Allowed to do this operation(%s)') % (rec.move_type))
        return True

    def check_done(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if the user is Allowed to Done a process

        @return: boolean True or False
        """
        user_obj = self.pool.get('res.users')
        responser = user_obj.browse(cr ,uid, uid)
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.move_type == 'assign_oc' and responser.company_id.hq:
                raise osv.except_osv(_('ERROR'), _('you are not Allowed to do Done operation, Oc user only is Allowed.'))
            if rec.move_type == 'return_oc' and not responser.company_id.hq:
                raise osv.except_osv(_('ERROR'), _('you are not Allowed to do Done operation, HQ user only is Allowed.'))
        return True
        
    def done(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to done.

        @return: Boolean True
        """
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        for rec in self.browse(cr, uid, ids, context):
            #product_pool = self.pool.get('product.product')
            custodys=[]
            for custody in rec.custody_ids:
                custodys.append(custody.id)
            notes=(rec.vehicle_id.notes and rec.comment) and rec.vehicle_id.notes+'\n'+rec.comment or rec.vehicle_id.notes and rec.vehicle_id.notes or rec.comment and rec.comment
            #product_id=product_pool.search(cr,uid,[('fuel_type','=',rec.vehicle_id.fuel_type),('location','=',rec.place_id.id)],context=context)
            emp_name=False
            emp_degree=False
            if rec.previous_employee_id:
                emp_name = rec.previous_employee_id.name
                emp_degree =rec.previous_employee_id.degree_id.name
            elif rec.previous_old_system_driver:
                emp_name = rec.previous_old_system_driver
                emp_degree =rec.vehicle_id.old_system_degree

            move_note=False
            temp_move_note=False
            if emp_name or emp_degree:
                temp_move_note=str(_("Move Info :").encode('utf-8')+ emp_name.encode('utf-8') + " - "+emp_degree.encode('utf-8')+"\n")
            if temp_move_note and rec.vehicle_id.move_note:
                move_note=rec.vehicle_id.move_note.encode('utf-8')+temp_move_note
            elif not temp_move_note:
                move_note=rec.vehicle_id.move_note
            else:
                move_note=temp_move_note

            write_dict = {'company_id':user.company_id.id,'use': rec.use.id,'custody_ids':[(6, 0,custodys)],'location':rec.place_id.id,'notes':notes,'old_system_driver':False,'old_system_degree':False,'move_note':move_note}
            if rec.vehicle_status:
                write_dict['vehicle_status'] = rec.vehicle_status
            rec.vehicle_id.write(write_dict)
            #rec.vehicle_id.write({'company_id':user.company_id.id,'use': rec.use.id,'custody_ids':[(6, 0,custodys)],'location':rec.place_id.id,'notes':notes})
            if rec.driver_id:
                #rec.vehicle_id.write({'driver_id':rec.driver_id.id})
                rec.vehicle_id.write({'driver':rec.driver_id.id,'belong_to':'in','out_driver':False,'out_department':False})
            else:
                #rec.vehicle_id.write({'driver_id':False})
                rec.vehicle_id.write({'driver':False})
            if rec.employee_id:
                rec.vehicle_id.write({'employee_id':rec.employee_id.id,'belong_to':'in','out_driver':False,'out_department':False})
            else:
                rec.vehicle_id.write({'employee_id':False,'degree_id':False})
            if rec.department_id:
                rec.vehicle_id.write({'department_id':rec.department_id.id,'belong_to':'in','out_driver':False,'out_department':False})
            else:
                rec.vehicle_id.write({'department_id':False})
            if not (rec.employee_id or rec.driver_id or rec.department_id) and (not rec.out_driver and not rec.out_department):
                raise osv.except_osv(_('ERROR'), _('If you wont to assign this vehicle to Outsourse Driver, You must enter out driver and out Department \n other wise you must enter employee or Department.'))
            if not (rec.employee_id or rec.driver_id or rec.department_id) and (rec.out_driver or rec.out_department):
                if rec.use.type == 'dedicated' and not rec.out_driver:
                    raise osv.except_osv(_('ERROR'), _('You Must Enter Employee or Driver or Out Driver.'))
                if rec.use.type == 'management' and not rec.out_department:
                    raise osv.except_osv(_('ERROR'), _('You Must Enter Department or Out Department.'))
                if rec.use.type == 'dedicated_managemnet' and (not rec.out_department or not rec.out_driver):
                    raise osv.except_osv(_('ERROR'), _('You Must Enter Employee or Driver or Out Driver and Department or Out Department.'))

            #rec.vehicle_id.onchange_vehicle_status(rec.vehicle_status)
            rec.write({'state': 'done'})
        return True
#--------------------------
#   Vehicle Sale
#--------------------------

class  vehicle_sale(osv.osv):
    """ To manage vehicle sale process """
    _name = "vehicle.sale"

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            
            val=0.0
            for line in record.line_id:
               val += line.agreed_amount
            res[record.id]=val
        return res

    def _actual_sale_amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            val=0.0
            for line in record.line_id:
               val += line.actual_sale_amount
            res[record.id]=val
        return res

    def _get_record(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('vehicle.sale.lines').browse(cr, uid, ids, context=context):
            result[line.sale_id.id] = True
        return result.keys()

    _columns = {
        'reference':fields.char('Reference',readonly=1),
        'sale_date': fields.date(string="Sale Date" ,required=True),
        'name': fields.char(string="sale Description" , size=156),
        'sale_type': fields.selection([('pension','Pension'),('public','Public')],string="sale Type"),
        'state': fields.selection([('draft', 'Draft'), ('confirm', 'Confirm')], 'State'),
        'line_id': fields.one2many('vehicle.sale.lines','sale_id',"Vehicle Sale Lines"),
        'comment': fields.text('Notes'),
        'company_id': fields.many2one('res.company','company'),
        'amount_total': fields.function(_amount_all,string='Total',
            store={
                'vehicle.sale.lines': (_get_record, [], 10),
            },help="The total amount"),
        'actual_sale_amount_total': fields.function(_actual_sale_amount_all,string='The actual sale amount total',
            store={
                'vehicle.sale.lines': (_get_record, [], 10),
            },help="The actual sale amount total"),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Override copy function to edit default value.

        @param default : default vals dict
        @return: super copy() method
        """
        raise osv.except_osv(_('Warning!'),_('You cannot duplicate record.'))
        return super(vehicle_sale, self).copy(cr, uid, id, default, context)

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id

        return company

    _defaults ={
    'sale_date': lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
    'state':'draft',
    'company_id' : _default_company
    }

    def create(self, cr, uid, vals, context={}):
        """
        overwrite super to update sequence
        @ return : super methode
        """
        seq = self.pool.get('ir.sequence').next_by_code(cr, uid, 'vehicle.sale')
        vals['reference'] = seq
        if not seq:
            raise  osv.except_osv(_('Warning'), _('No sequence defined!\nPleas contact administartor to configue sequence with code \'vehicle.sale\'') )

        return super(vehicle_sale, self).create(cr, uid, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft']:
                raise osv.except_osv(_('Warning!'),_('You cannot delete record after confirm it.'))
        return super(vehicle_sale, self).unlink(cr, uid, ids, context)


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
        for rec in self.browse(cr, uid, ids, context):
            if not rec.line_id:
                raise osv.except_osv(_('Warning!'),_('You cannot confirm record without vehicles to sale them .'))
            rec.write({'state': 'confirm'})
            for line in rec.line_id:
                notes = ''
                if line.vehicle_id.notes and line.sale_id.comment:
                    notes = line.vehicle_id.notes +'\n' +line.sale_id.comment
                elif line.vehicle_id.notes and not line.sale_id.comment:
                    notes = line.vehicle_id.notes
                elif not line.vehicle_id.notes and line.sale_id.comment:
                    notes = line.sale_id.comment
                else:
                    notes = line.vehicle_id.notes
                #notes = (line.vehicle_id.notes and line.sale_id.comment) and line.vehicle_id.notes +'\n' +line.sale_id.comment or rec.vehicle_id.notes and rec.vehicle_id.notes or rec.comment and rec.comment
                line.vehicle_id.write({'purchaser': line.purchaser,'sale_ref':rec.reference,'vehicle_status': 'sold','employee_id':False,'degree_id':False,'use':False, 'notes':notes })#,'driver_id':False
        return True


class  vehicle_sale_lines(osv.osv):
    """ vehicle Line """
    _name = "vehicle.sale.lines"
    _columns = {
        'sale_id':fields.many2one('vehicle.sale',string="Vehicle" ,required=True),
        'vehicle_id': fields.many2one('fleet.vehicle',string="Vehicle" ,required=True),
        'body_id': fields.related('vehicle_id','vin_sn',type="char",string="Chassis Number",readonly=1),
        'model_id': fields.related('vehicle_id','model_id',type="many2one",relation="fleet.vehicle.model",string="vehicle model",readonly=1),
        'vehicle_sale_type': fields.related('sale_id','sale_type',type="char",string="sale type"),
        'vehicle_type': fields.related('vehicle_id','type',type="many2one",relation="vehicle.category",string="Vehicle Type",readonly=1),
        'company_assess': fields.float(string="Company Assess",required=True),
        'committee_assess': fields.float(string="Committee Assess",required=True),
        'agreed_amount': fields.float(string="Agreed Amount",required=True),
        'actual_sale_amount': fields.float(string="Actual Sale Amount"),
        'purchaser': fields.char('Purchaser',size=156),
        'card_no': fields.char('Card number',size=156),
    }

    def check_assess(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a place with the same name

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.company_assess <= 0.0 and rec.sale_id.sale_type != 'pension':
                raise osv.except_osv(_('ERROR'), _('Company assess should be more than zero') )
            if rec.committee_assess <= 0.0:
                raise osv.except_osv(_('ERROR'), _('Committee assess should be more than zero') )
            if rec.agreed_amount <= 0.0:
                raise osv.except_osv(_('ERROR'), _('Agreed amount should be more than zero') )
            
        return True


    _constraints = [
         (check_assess, '', []),
    ]



#--------------------------
#   Vehicle Theft
#--------------------------

class vehicle_theft(osv.osv):
    """ To manage vehicle theft registration process """
    _name = "vehicle.theft"
    _columns = {
        'name':fields.char('Reference',readonly=1),
        'police_department': fields.char(string="Police department" , size=156),
        'report_no':fields.char(string="Report number" , size=156),
        'theft_date': fields.date(string="Theft Date" ,required=True),
        'place': fields.char(string="Theft Place" , size=156),
        'vehicle_id': fields.many2one('fleet.vehicle',string="Vehicle" ,required=True),
        'out_driver': fields.char('Driver'),
        'out': fields.boolean("Out"),
        'body_id': fields.related('vehicle_id','vin_sn',type="char",string="Chassis Number",readonly=1),
        'vehicle_type': fields.related('vehicle_id','type',type="many2one",relation="vehicle.category",string="Vehicle Type",readonly=1),
        'model_id': fields.related('vehicle_id','model_id',type="many2one",relation="fleet.vehicle.model",string="vehicle model",readonly=1,store=True),
        'state': fields.selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('done', 'Done')], 'State'),
        'employee_id': fields.many2one("hr.employee", string="Employee"),
        'members_ids': fields.many2many('hr.employee', 'emp_members_rel', 'emp_id', 'member_id', 'Committee members'),
        'remove_custody' : fields.boolean('Remove Custody'),
        'comment': fields.text('Theft Description'),
        'company_id': fields.many2one('res.company','company'),
        'user_id': fields.many2one('res.users','Responsible'),
        'committee_attach':fields.boolean('check Committee attachment'),
        'gm_attach':fields.boolean('check General Manager attachment'),
    }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults ={
    'out':False,
    'theft_date': lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
    'state':'draft',
    'remove_custody':False,
    'company_id' : _default_company,
    'user_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).id,
    }

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Override copy function to edit default value.

        @param default : default vals dict
        @return: super copy() method
        """
        raise osv.except_osv(_('Warning!'),_('You cannot duplicate record.'))
        return super(vehicle_theft, self).copy(cr, uid, id, default, context)
    
    def create(self, cr, uid, data, context=None):
        """
        To set employee_id
        """
        seq = self.pool.get('ir.sequence').next_by_code(cr, uid, 'vehicle.theft')
        data['name'] = seq
        if not seq:
            raise  osv.except_osv(_('Warning'), _('No sequence defined!\nPleas contact administartor to configue sequence with code \'vehicle.theft\'') )

        rec=self.pool.get('fleet.vehicle').browse(cr ,uid, data['vehicle_id'],context=context)
        if rec.employee_id:
            data['employee_id']=rec.employee_id.id
        elif rec.driver:
            data['employee_id']=rec.driver.id
        if rec.belong_to == 'out':
            data['out']=True
            data['out_driver']=rec.out_driver
        return super(vehicle_theft, self).create(cr, uid, data, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        To set employee_id
        """
        if 'vehicle_id' in vals:
            rec=self.pool.get('fleet.vehicle').browse(cr ,uid, vals['vehicle_id'],context=context)
            if rec.employee_id:
                vals['employee_id']=rec.employee_id.id
            elif rec.driver:
                vals['employee_id']=rec.driver.id
            if rec.belong_to == 'out':
                vals['out']=True
                vals['out_driver']=rec.out_driver
        return super(vehicle_theft, self).write(cr, uid, ids,vals, context=context)

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.vehicle_id.name + '-' + record.place + '-'+record.theft_date
            res.append((record.id, name))
        return res

    def onchange_out_driver(self, cr, uid, ids, out_driver):
        """
        check if out_driver contains space and return it without space
        """
        vals = {}
        if out_driver:
            vals['out_driver'] = out_driver.strip()
        return {'value': vals}

    def onchange_vehicle_id(self, cr, uid, ids, vehicle_id,context=None):
        """
        @param vehicle_id: Id of vehicle
        @return: Dictionary of values 
        """
        vals={}
        if vehicle_id:
            rec=self.pool.get('fleet.vehicle').browse(cr ,uid, vehicle_id,context=context)
            vals={'type':rec.type.id,'body_id':rec.vin_sn,'model_id':rec.model_id.id,'vehicle_type':rec.type.id}
            if rec.employee_id:
                vals['employee_id']=rec.employee_id.id
            elif rec.driver:
                vals['employee_id']=rec.driver.id
            if rec.belong_to == 'out':
                vals['out']=True
                vals['out_driver']=rec.out_driver
        return {'value':vals}

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft']:
                raise osv.except_osv(_('Warning!'),_('You cannot delete record after confirm it.'))
        return super(vehicle_theft, self).unlink(cr, uid, ids, context)

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
        for rec in self.browse(cr, uid, ids, context):
            rec.write({'state': 'confirm'})
        return True

    def done(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to confirm.

        @return: Boolean True
        """
        for rec in self.browse(cr, uid, ids, context):
            rec.write({'state': 'done'})
            notes = ''
            attachment=self.pool.get('ir.attachment').search(cr,uid,[('res_model','=','vehicle.theft'),('res_id','=',ids[0])],context=context)
            if rec.vehicle_id.notes and rec.comment:
                notes = rec.vehicle_id.notes +'\n' +rec.comment
            elif rec.vehicle_id.notes and not rec.comment:
                notes = rec.vehicle_id.note
            elif not rec.vehicle_id.notes and rec.comment:
                notes = rec.comment
            else:
                notes = rec.vehicle_id.note
            if rec.remove_custody:
                rec.vehicle_id.write({'vehicle_status': 'removal','employee_id':False,'ownership':False, 'notes': notes})
            else:
                rec.vehicle_id.write({'vehicle_status': 'missing','notes': notes})
            #chech attachments
            if rec.committee_attach and not rec.gm_attach:
                if not attachment:
                    raise osv.except_osv(_('ValidateError'), _("Plase attach Committee's decision"))
            elif not rec.committee_attach and rec.gm_attach:
                if not attachment:
                    raise osv.except_osv(_('ValidateError'), _("Plase attach General Manager decision"))
            elif rec.committee_attach and rec.gm_attach and len(attachment) < 2:
                raise osv.except_osv(_('ValidateError'), _("Plase attach General Manager decision and Committee's decision"))
        return True


#--------------------------
#   Service Type
#--------------------------
class fleet_service_type(osv.osv):
    """
    Manage and customize fleet service types.
    """
    _inherit='fleet.service.type'

    _columns = {
        'name': fields.char('Name', required=True, translate=True),
        'category': fields.selection([('contract', 'Maintenance'), ('service', 'Service'), ('both', 'Vehicle Request'),
                                      ('insurance','Vehicle Insurance'),('license','Vehicle License')], 'Category',required=True),
        'active':fields.boolean('Active'),
        
    }
    _defaults = {
        'active':True,
    }

#--------------------------
#   Vehicle Contract
#--------------------------
class fleet_vehicle_log_contract(osv.osv):
    """
    Manage admin affairs services.
    """
    _inherit='fleet.vehicle.log.contract'

    def _vehicle_contract_name_get_fnc_custom(self, cr, uid, ids, name, unknow_none, context=None):
        res = {}
        if context == None: context = {}
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if name == '/':
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'fleet.vehicle.log.contract')
                name =  sequence.upper()
                sub_type = ""
                prefix = ""
                if 'default_category' in context:
                    sub_type += context['default_category'] == 'license' and 'License' or 'Insurance'
                    prefix += context['default_category'] == 'license' and 'FL' or 'FI'
                #sub_type=record.cost_subtype_id.name or "" 
                if sub_type:
                    #name += ' / '+ sub_type
                    name = prefix + name
            res[record.id] = name
        return res
    
    _columns = {
        'name': fields.function(_vehicle_contract_name_get_fnc_custom, type="char", string='Name', store=True),
        'insurer_id' :fields.many2one('res.partner', 'Partner'),
        'cost_subtype_id': fields.many2one('fleet.service.type', 'Type',help='Cost type purchased with this cost'),
        'expiration_date': fields.date('To Date', help='Date when the coverage of the contract expired (by default, one year after begin date)'),
        'date' :fields.datetime('Date',help='Date when the cost has been executed'),
	    'duration': fields.char(string='Duration', help='Date When The Coverage Of The Contract Begins And End'),
        'start_date': fields.date(string='From Date', help='Date When The Coverage Of The Contract Begins'),
        'company_id': fields.many2one('res.company', 'Company',readonly=True),
        #'generated_cost_ids': fields.one2many('fleet.vehicle.cost', 'contract_id', 'Generated Costs',
        #                                    ondelete='cascade'),
        'state': fields.selection([('draft', 'Draft'),('confirm', 'Confirm'),('cancel', 'Cancel')],'Status'),
        'cat_subtype': fields.related('cost_subtype_id', 'category', type="selection",selection=[('contract', 'Maintenance'),
                     ('service', 'Service'), ('both', 'Vehicle Request'),
                    ('insurance','Vehicle Insurance'),('license','Vehicle License')], string="Service Type Category"),
        'vehicles_ids': fields.many2many('fleet.vehicle', 'fleet_vehicle_contract_vehicle', 'model_id', 'vehicle_id', string='Vehicles'),
        #'purchaser_id': fields.many2one('res.users', 'Contractor', help='Person to which the contract is signed for'),
        'insurance_type': fields.selection([('part', 'Third Part'),('all', 'All')],'Insurance Type'),
        'category': fields.selection([('insurance','Vehicle Insurance'),('license','Vehicle License')], 'Category',required=True),
        'amount': fields.float('Total Amount'),
        'line_ids': fields.one2many('fleet.vehicle.log.contract.line','fleet_contract_id','Contract Lines')
    }

    _defaults = {
        'state':'draft',
        'name':'/',
        'cost_subtype_id':False,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'fleet.vehicles', context=c),
        #'purchaser_id': lambda self, cr, uid, context: uid,
    }

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Override copy function to edit default value.

        @param default : default vals dict
        @return: super copy() method
        """
        raise osv.except_osv(_('Warning!'),_('You cannot duplicate record.'))
        return super(fleet_vehicle_log_contract, self).copy(cr, uid, id, default, context)
    
    def confirm(self, cr, uid, ids, context=None):
        """
        Change state of contract To Confirm.

        @return: write state
        """
        for rec in self.browse(cr, uid, ids, context):
            if not rec.line_ids:
                raise osv.except_osv(_('Warning!'),_('You cannot confirm record without vehicles.'))
            self.write(cr, uid, [rec.id], {'state':'confirm'}, context=context)
            for line in rec.line_ids:
                if rec.category == 'license':
                    line.vehicle_id.write({'license_plate':line.new_license_plate, 'license_date':line.fleet_contract_id.start_date})
                if rec.category == 'insurance':
                    line.vehicle_id.write({'insurance_date':line.fleet_contract_id.start_date})

        return True

    def draft(self, cr, uid, ids, context=None):
        """
        Change state of contract To draft.

        @return: write state
        """
        for rec in self.browse(cr, uid, ids, context):
            self.write(cr, uid, [rec.id], {'state':'draft'}, context=context)
            if rec.category == 'license':
                for line in rec.line_ids:
                    line.vehicle_id.write({'license_plate':line.license_plate})
        return True

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft']:
                raise osv.except_osv(_('Warning!'),_('You cannot delete record which is not in a draft state.'))
        return super(fleet_vehicle_log_contract, self).unlink(cr, uid, ids, context)

    def get_date(self, str):
        return datetime.datetime.strptime(str, "%Y-%m-%d")

    def get_datetime(self, str):
        return datetime.datetime.strptime(str, "%Y-%m-%d %H:%M:%S")

    def _check_date(self, cr, uid, ids, context=None):
        """
        Check the value of start_date if greater than expiration_date or not.

        @return: Boolean of True or False
        """
        for act in self.browse(cr, uid, ids, context):
            if act.start_date and act.expiration_date:
                if self.get_date(act.start_date) > self.get_date(act.expiration_date):
                    raise osv.except_osv(_(''), _("Start Date Must Be Less Than Expiration Date!"))

            if act.date and act.start_date:
                if self.get_datetime(act.date) > self.get_date(act.start_date):
                    raise osv.except_osv(_(''), _("Request Date Must Be Less Than Start Date!"))
        return True
    

    def _check_contracts(self, cr, uid, ids, context=None):
        for contract in self.browse(cr, uid, ids, context=context):
            for vehicle in contract.vehicles_ids:
                vehicle._check_contracts()
        return True


    def _check_amount(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            line_amount = 0.0
            for line in rec.line_ids:
                line_amount += line.amount
            if rec.amount < line_amount and rec.category == 'insurance' and rec.state == 'confirm':
                raise osv.except_osv(_(''), _("Insurance total amount should be more than or equal to the sum of insurance amount for the vehicles "))
            if rec.amount < line_amount and rec.category == 'license' and rec.state == 'confirm':
                raise osv.except_osv(_(''), _("License total amount should be more than or equal to the sum of license amount for the vehicles "))
            if rec.amount == 0.0 and rec.category == 'insurance' and rec.state == 'confirm':
                raise osv.except_osv(_(''), _("Insurance total amount should be more than zero"))
            if rec.amount == 0.0 and rec.category == 'license' and rec.state == 'confirm':
                raise osv.except_osv(_(''), _("License total amount should be more than zero"))

        return True
    
    _constraints = [
        (_check_date, _(''), ['date','start_date','expiration_date']),
        (_check_contracts, '', []),
        (_check_amount, '', ['amount']),
    ]


    def write(self, cr, uid, ids, vals, context={}):
        """
        overwrite write method to update amount based on total amount of the 
        lines
        @return: super method
        """
        for rec in self.browse(cr, uid, ids, context):
            line_ids = []
            amount = rec.amount
            if 'amount' in vals:
                amount = vals['amount']
            if 'line_ids' in vals:
                line_ids = vals['line_ids']
            else:
                for line in rec.line_ids:
                    line_ids.append([4,line.id,False])

            if line_ids:
                line_amount = 0.0
                line_idss = resolve_o2m_operations(cr, uid, self.pool.get('fleet.vehicle.log.contract.line'),
                                                        line_ids, ["amount"], context)
                for line in line_idss:
                    line_amount  +=  line['amount']

                if line_amount > amount:
                    vals.update({'amount': line_amount})

        return super(fleet_vehicle_log_contract, self).write(cr, uid, ids, vals, context)

    def create(self, cr, uid, vals, context={}):
        """
        overwrite create method to update amount based on total amount of the 
        lines
        @return: super method
        """
        amount = vals['amount']
        if 'line_ids' in vals and vals['line_ids']:
                line_amount = 0.0
                line_idss = resolve_o2m_operations(cr, uid, self.pool.get('fleet.vehicle.log.contract.line'),
                                                        vals['line_ids'], ["amount"], context)
                for line in line_idss:
                    line_amount  +=  line['amount']

                if line_amount > amount:
                    vals.update({'amount': line_amount})
        

        return super(fleet_vehicle_log_contract, self).create(cr, uid, vals, context)


    def update_lines(self, cr, uid, ids, context={}):
        """
        check if status of vehicles in lines has been inactive then delete it from lines 
        @return: boolean
        """
        line_ids = self.pool.get('fleet.vehicle.log.contract.line').search(cr ,uid, [('fleet_contract_id','=',ids[0])])
        if line_ids:
            cr.execute("SELECT lines.id as id "\
                                "FROM fleet_vehicle_log_contract_line lines " \
                                #"FROM fleet_vehicle fleet,hr_employee emp,hr_employee driver,hr_salary_degree emp_deg,hr_salary_degree driver_deg, "\
                                #"hr_department dep,resource_resource emp_res,resource_resource driver_res,fleet_vehicle_model model,vehicle_category cat, " \
                                #"fleet_vehicle_use use, fleet_vehicle_ownership ownership " \
                                "left join fleet_vehicle fleet ON (lines.vehicle_id = fleet.id) "\
                                "WHERE lines.id in %s and fleet.status = 'inactive' " \
                                #"group by fleet.id, fleet.vin_sn, fleet.license_plate, fleet.old_system_driver,fleet.old_system_degree, fleet.vehicle_status,use.name, " \
                                #"fleet.machine_no, fleet.year,dep.name,emp_res.name, driver_res.name, emp_deg.name,driver_deg.name,model.name, cat.name,ownership.name  " \
                                "order by fleet.year desc", (tuple(line_ids),) ) 
            res = cr.dictfetchall()
            if res:
                unlink_ids = [x['id'] for x in res]
                self.pool.get('fleet.vehicle.log.contract.line').unlink(cr, uid, unlink_ids)
        
        

        return True


#--------------------------
#   Vehicle Contract Lines
#--------------------------
class fleet_vehicle_log_contract_line(osv.osv):
    """
    Manage admin affairs services.
    """
    _name = 'fleet.vehicle.log.contract.line'
    
    _columns = {
        'fleet_contract_id': fields.many2one('fleet.vehicle.log.contract', 'Contract', ondelete="cascade"),
        'vehicle_id': fields.many2one('fleet.vehicle', 'Vehicle'),
        'model_id': fields.many2one('fleet.vehicle.model', 'Model'),
        'vin_sn': fields.char('Chassis Number', size=32),
        'license_plate': fields.char('License Plate', size=32),
        'new_license_plate': fields.char('New License Plate', size=32),
        'driver': fields.many2one('hr.employee', 'Driver', help='Driver Of The Vehicle'),
        'fuel_type': fields.selection([('gasoline', 'Gasoline'), ('diesel', 'Benzene'), ('electric', 'Electric'), ('hybrid', 'Hybrid')],
                                      'Fuel Type', help='Fuel Used by the vehicle'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'status': fields.selection([('active', 'Active'), ('inactive', 'InActive')], 'vehicle Activation'),
        'ownership': fields.many2one('fleet.vehicle.ownership', 'Ownership'),
        'type': fields.many2one('vehicle.category', string='Vehicle Type'),
        'amount': fields.float('Amount'),


    }

    _defaults = {
        'amount': 0.0,
        
    }

    def onchange_vehicle_id(self, cr, uid, ids, vehicle_id, context={}):
        """
        """
        vals = {'model_id': False, 'vin_sn': False, 'license_plate': False, 'driver': False,
                'fuel_type': False, 'department_id': False, 'status': False, 'type': False}
        if vehicle_id:
            vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context)
            vals = {'model_id': vehicle.model_id and vehicle.model_id.id or False, 
                    'vin_sn': vehicle.vin_sn, 
                    'license_plate': vehicle.license_plate,
                    'new_license_plate': vehicle.license_plate, 
                    'driver': (vehicle.driver and vehicle.driver.id) or (vehicle.employee_id and vehicle.employee_id.id) or False,
                    'fuel_type': vehicle.fuel_type,
                    'department_id':  vehicle.department_id and vehicle.department_id.id or False, 
                    'status': vehicle.status, 
                    'type': vehicle.type and vehicle.type.id or False,
                    
                    }

        return {'value':vals}        


    def create(self, cr, uid, vals, context={}):
        """
        overwrite create method to change related vehicle fields
        @return: super method
        """
        valss = vals
        onchange_vals = self.onchange_vehicle_id(cr ,uid , [], vals['vehicle_id'])['value']
        vals.update(onchange_vals)

        if 'new_license_plate' in valss:
                vals.update({'new_license_plate':valss['new_license_plate']})

        if 'new_license_plate' in vals:
            vals.update({'new_license_plate':vals['new_license_plate'].strip()})


        return super(fleet_vehicle_log_contract_line, self).create(cr, uid, vals, context)


    def write(self, cr, uid, ids, vals, context={}):
        """
        overwrite write method to change related vehicle fields
        @return: super method
        """
        for rec in self.browse(cr, uid, ids, context):
            valss = vals
            if 'vehicle_id' in vals:
                onchange_vals = self.onchange_vehicle_id(cr ,uid , [], vals['vehicle_id'])
                vals.update(onchange_vals)

            if 'new_license_plate' in valss:
                vals.update({'new_license_plate':valss['new_license_plate']})

            if 'new_license_plate' in vals:
                vals.update({'new_license_plate':vals['new_license_plate'].strip()})

        return super(fleet_vehicle_log_contract_line, self).write(cr, uid, ids, vals, context)


    def _check_amount(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.amount < 0.0 and rec.fleet_contract_id.category == 'insurance':
                raise osv.except_osv(_(''), _("Insurance amount should not be less than 0 for the vehicle %s ")%(rec.vehicle_id.name))

            if rec.amount < 0.0 and rec.fleet_contract_id.category == 'license':
                raise osv.except_osv(_(''), _("License amount should not be less than 0 for the vehicle %s ")%(rec.vehicle_id.name))

        return True

    def _check_license_plate(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            #if not rec.license_plate < 0.0 and rec.fleet_contract_id.category == 'insurance':
            #   raise osv.except_osv(_(''), _("Insurance amount should be more than 0 for the vehicle %s ")%(rec.vehicle_id.name))

            if not rec.new_license_plate and rec.fleet_contract_id.category == 'license':
                raise osv.except_osv(_(''), _("You have to enter license plate for the vehicle %s ")%(rec.vehicle_id.name))

        return True
    
    _constraints = [
        (_check_amount, _(''), ['amount']),
        (_check_license_plate, _(''), ['new_license_plate']),
    ]

    

    
