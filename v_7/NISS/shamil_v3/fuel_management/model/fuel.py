# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv, fields
from tools.translate import _
import sys
import time
import datetime
import openerp.addons.decimal_precision as dp
from openerp.addons.account_voucher.account_voucher import resolve_o2m_operations
import netsvc


#--------------------------
#   vehicle Destination
#--------------------------
class  vehicle_dest(osv.osv):
    """ To manage vehicle places """
    _name = "vehicle.dest"
    _columns = {
        'name': fields.char(string="Name" ,required=True),
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
                raise osv.except_osv(_('ERROR'), _('This destination name is already exisit for the company %s') % (rec.company_id.name))
        return True

    

    _constraints = [
         (check_name, '', []),
    ]

    def create(self, cr, uid, vals, context=None):
        """
        Override create method to check if place name contains spaces
        @return: super create method
        """
        if 'name' in vals:
            vals['name'] = vals['name'].strip()
        
        return super(vehicle_dest, self).create(cr, uid, vals, context=context)

    def onchange_name(self, cr, uid, ids, name, context={}):
        """
        """
        vals = {}
        if name:
            vals['name'] = name.strip()

        return {'value': vals}



class outgoing_fuel_type(osv.osv):
    """ The outgoing type of fuel"""
    _name = "outgoing.fuel.type"
    _columns = {
        'name': fields.char('outgoing type', size=256),
        'company_id': fields.many2one('res.company','company'),
        'require_user': fields.boolean('Require Employee',),
        'evaporation_type': fields.boolean('evaporation type',),
        #'vehicles_ids': fields.one2many('fleet.vehicle', 'use', string='Vehicles'),
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
        'company_id' : _default_company
    }

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if not rec.name.strip():
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
        return True

    def _check_name(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a outgoing fuel type with the same name

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            idss = self.search(cr,uid, [('name', '=', rec.name),('company_id', '=', rec.company_id.id),('id','!=',rec.id)])
            if idss:
                raise osv.except_osv(_('ERROR'), _('This outgoing type name is already exisit for the company (%s)') % (rec.company_id.name))
        return True

    _constraints = [
        (_check_spaces, '', []),
        (_check_name, '', []),
    ]

    '''def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            if rec.vehicles_ids:
                raise osv.except_osv(
                    _(''), _("can not delete record linked with other record"))
        return super(fleet_vehicle_use, self).unlink(cr, uid, ids, context=context)'''

class fuel_delegate(osv.osv):
    """ 
    To manage fuel delegate employee
    """
    _name = "fuel.delegate"
    _rec_name = 'employee_id'

    _columns = {
        'employee_id': fields.many2one('hr.employee', "Employee"),
        'degree_id': fields.related('employee_id','degree_id',type="many2one",relation="hr.salary.degree",string="Degree",readonly=1),
        'department_id': fields.related('employee_id','department_id',type="many2one",relation="hr.department",string="Department",readonly=1),
        'emp_code': fields.related('employee_id','emp_code',type="char",string="Employee Code",readonly=1),
        'line_id': fields.one2many('fuel.delegate.lines', 'delegate_id' , string="fuel delegate lines" ),
        'state': fields.selection([('draft', 'Draft'), ('confirm', 'Confirm')], 'State'),
        'company_id': fields.many2one('res.company','company'),    
        'employee_type': fields.selection([('delegate', 'Delegate'), ('worker', 'worker')], 'Employee Type'),
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
    'company_id' : _default_company,
    'state':'draft',
    }

    def create(self, cr, uid, data, context=None):
        """
        To set employee details
        """
        if data['employee_id']:
            rec=self.pool.get('hr.employee').browse(cr ,uid, data['employee_id'],context=context)
            data.update({'degree_id':rec.degree_id.id,'department_id':rec.department_id.id,'emp_code':rec.emp_code})
        return super(fuel_delegate, self).create(cr, uid, data, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        To set employee details
        """
        if 'employee_id' in vals:
            rec=self.pool.get('hr.employee').browse(cr ,uid, vals['employee_id'],context=context)
            vals.update({'degree_id':rec.degree_id.id,'department_id':rec.department_id.id,'emp_code':rec.emp_code})
        return super(fuel_delegate, self).write(cr, uid, ids,vals, context=context)

    def onchange_employee_id(self, cr, uid, ids, employee_id,context=None):
        """
        @param employee_id: Id of employee
        @return: Dictionary of values 
        """
        vals={}
        if employee_id:
            rec=self.pool.get('hr.employee').browse(cr ,uid, employee_id,context=context)
            vals={'degree_id':rec.degree_id.id,'department_id':rec.department_id.id,'emp_code':rec.emp_code}
        return {'value':vals}

    def confirm(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to confirm.

        @return: Boolean True
        """
        for rec in self.browse(cr, uid, ids, context):
            if not rec.line_id:
                raise osv.except_osv(_('ERROR'), _('You must Enter fuel delegate lines!'))
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
        Constrain method to check delegate employee unique

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            idss = self.search(cr,uid, [('employee_id', '=', rec.employee_id.id),('id','!=',rec.id)])
            if idss:
                raise osv.except_osv(_('ERROR'), _('This employee already have fuel delegate record'))
        return True

    def _check_lines(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check unique of Fuel type in lines

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.employee_type == 'worker':
                continue
            line_obj=self.pool.get('fuel.delegate.lines')
            fuel_type=[]
            no_dupes=[]
            lines = line_obj.search(cr, uid, [('delegate_id', '=', rec.id)])
            reads = line_obj.read(cr, uid, lines, ['fuel_type'], context=context)
            for read in reads:
                fuel_type.append(read['fuel_type'])
                no_dupes = [x for n, x in enumerate(fuel_type) if x not in fuel_type[:n]]
            if fuel_type != no_dupes:
                raise osv.except_osv(_('ERROR'), _('You Can not create more than one Fuel Type for the same employee.'))
        return True

    _constraints = [
         (_check_unique, '', []),
         (_check_lines, '', []),
    ]


    def name_get(self, cr, uid, ids, context=None):
        """override to compute name from other fields"""
        if not len(ids):
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.employee_id.name  
            res.append((record.id,name))
        return res

class fuel_delegate_lines(osv.osv):
    """ 
    To manage fuel delegate lines
    """
    _name = "fuel.delegate.lines"

    _columns = {
        'delegate_id': fields.many2one('fuel.delegate', 'Delegate'),
        'product_id': fields.many2one('product.product', 'Product'),
        'fuel_type': fields.selection([('gasoline','Gasoline'),('diesel', 'Diesel'),('electric', 'Electric'), ('hybrid', 'Hybrid')],'Fuel type') ,
        'location_id': fields.many2one('stock.location', 'Location'), 
        'fuel_qty': fields.float('Fuel', digits=(16,2)), 
        'card_no': fields.char('Fuel Card Number'),   
        'state': fields.related('delegate_id','state',type="char", string="Delegate State"),
        'delegation_auther': fields.many2one('hr.employee','Delegation auther'),    
        'delegation_type': fields.selection([('daily', 'Daily'), ('monthly', 'Monthly'),
        ('open', 'open'), ('until_end', 'Until End'), ('renew_after_end', 'Renew After End')], 'Delegation Type'),
    }

    def onchange_fuel_type(self, cr, uid, ids, fuel_type,context=None):
        """
        @param fuel_type: fuel type
        @return: Dictionary of values 
        """
        vals={}
        domain={'product_id':[('fuel_ok','=',True),('fuel_type','=',fuel_type)]}
        vals['product_id']=False
        return {'value':vals,'domain':domain}

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            card=rec.card_no.strip()
            if not card:
                raise osv.except_osv(_('ValidateError'), _("Fuel Card Number must not be spaces"))
        return True

    _constraints = [
         (_check_spaces, '', []),
    ]

class additional_fuel_purpose(osv.osv):
    """ 
    To manage additional fuel purpose
    """
    _name = "additional.fuel.purpose"


    _columns = { 
       'name': fields.char('Purpose Name', size=156),
       'company_id': fields.many2one('res.company','company'),
    }

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ','')) <= 0):
                raise osv.except_osv(_('ValidateError'), _("name must not be spaces"))
        return True
    _constraints = [
        (_check_spaces, '', ['name'])
    ]
    _sql_constraints = [
        ('additional_fuel_purpose_name_uniqe', 'unique(name)', 'you can not create same name !')
    ]

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults ={
    'company_id' : _default_company,
    }

#--------------------------
#   additional fuel
#--------------------------

class  additional_fuel(osv.osv):
    """ To manage vehicle additional fuel request """
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "additional.fuel"
    _track = {
        'state': {
            'fuel.mt_order_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['draft'],
            'fuel.mt_order_done': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['done'],
            'fuel.mt_order_approve': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['approve'],
            'fuel.mt_order_reapprove': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['reapprove']
        },
		}
    def _get_record(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('moving.lines').browse(cr, uid, ids, context=context):
            result[line.add_fuel_id.id] = True
        return result.keys()

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            
            val=0.0
            for line in record.move_line_id:
               val += line.total
            res[record.id]=val
        return res

    _columns = {
        'name':fields.char('Name'),
        'filling': fields.selection([('once','Once'),('several','Several')],"Additional fuel filling",track_visibility='onchange',),
        'destination': fields.selection([('once','Once'),('several','Several')],"Destination"),
        'add_type': fields.selection([('other','Other'),('permanent','Permanent'),('temporary','Temporary'),('moving','Moving'),('additional','Additional')],"Additional fuel Type",required=True,track_visibility='onchange',),
        'distance_id': fields.many2one('fuel.distance', 'fuel distance'),
        'comments': fields.related('distance_id', 'comments', type="char", string='The route'),
        'fuel_amount_id': fields.many2one('fuel.distance.amount', 'fuel amount'),
        'purpose_id': fields.many2one('additional.fuel.purpose', 'fuel purpose'),
        'order_date': fields.date(string="Order Date" ,required=True,track_visibility='onchange',),
        'start_date': fields.date(string="Start Date",track_visibility='onchange',),
        'end_date': fields.date(string="End Date",track_visibility='onchange',),
        'go_date': fields.date(string="Go Date",track_visibility='onchange', ),
        'back_date': fields.date(string="Back Date",track_visibility='onchange',),
        'vehicle_id': fields.many2one('fleet.vehicle',string="Vehicle",track_visibility='onchange',),
        'department_id':fields.many2one('hr.department','Department',track_visibility='onchange',),
        'body_id': fields.related('vehicle_id','vin_sn',type="char",string="Chassis Number",readonly=1),

        'fuel_type': fields.related('vehicle_id','fuel_type',type="char",string="Fuel type",readonly=1),
        'fuel_qty': fields.related('vehicle_id','product_qty',type="float",string="Fuel qty",readonly=1),
        'add_qty': fields.float('Additional Fuel Quantity',),

        'license_plate': fields.related('vehicle_id','license_plate',type="char",string="vehicle License Plate",readonly=1),
        'degree_id': fields.related('vehicle_id','degree_id',type="many2one",relation="hr.salary.degree",string="Degree",readonly=1),        
        'type': fields.many2one("vehicle.category",string="Vehicle Type"),
        'location': fields.many2one("vehicle.place",string="vehicle location"),
        'use': fields.many2one("fleet.vehicle.use",string="Vehicle use"),
        'state': fields.selection([('draft', 'Draft'), ('done', 'Done'),('approve','Approve'),('reapprove','Re-Approve'),('confirm','Confirm'),('cancel','Cancel')], 'State'),
        'comment': fields.text('Notes'),
        'description': fields.text('Description'),
        'company_id': fields.many2one('res.company','company'),
        'line_id': fields.one2many('additional.fuel.lines','add_fuel_id',"Additional fuel Lines"),
        'move_line_id': fields.one2many('moving.lines','add_fuel_id',"Moving Lines"),
        'dest_line_id': fields.one2many('destination.lines','add_dest_id',"Destination Lines",track_visibility='onchange',),
        'amount_total': fields.function(_amount_all,string='Total',
            store={
                'moving.lines': (_get_record, [], 10),
            },help="The total amount"),
        'total_distance': fields.float('Total Distance',track_visibility='onchange',),
        'total_fuel': fields.float('Total Fuel',track_visibility='onchange',),
        'employee_id': fields.many2one('hr.employee', 'Certitication Authority',track_visibility='onchange',),

        'applier_employee_id': fields.many2one('hr.employee', 'Applier',track_visibility='onchange',),
        'applier_degree_id': fields.related('applier_employee_id','degree_id',type="many2one",relation="hr.salary.degree",string="Applier Degree",readonly=1),        

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
    'name':'/',
    'order_date': lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
    'state':'draft',
    'company_id' : _default_company,
    'add_qty':0.0,
    }

    def _check_amount(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.add_type == 'temporary' and rec.end_date < rec.start_date:
                raise osv.except_osv(_('ValidateError'), _("End date should be equal to or greater than start date!"))
            if rec.add_type == 'other' and rec.back_date < rec.go_date:
                raise osv.except_osv(_('ValidateError'), _("Back date should be equal to or greater than go date!"))
            all_amount=0.0
            #if rec.filling == 'several' and not rec.line_id:
                #raise osv.except_osv(_('ValidateError'), _("you must enter fuel filling details!"))
            if rec.line_id:
                for line in rec.line_id:
                    all_amount+=line.amount
                if all_amount != rec.add_qty:
                    raise osv.except_osv(_('ValidateError'), _("The fuel amount from all location must be equal additional fuel amount!"))
        return True
    
    def _check_date_unique(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state == 'confirm':
                idss = []
                permanent_idss = []
                if rec.add_type == 'other':
                    idss += self.search(cr, uid, [('vehicle_id','=',rec.vehicle_id.id),
                            ('state','not in',['draft','cancel']),
                            ('add_type','=','other'),
                            ('go_date', '<=', rec.go_date), 
                            ('back_date', '>=', rec.back_date),
                            ('id', '!=', rec.id)])

                    idss += self.search(cr, uid, [('vehicle_id','=',rec.vehicle_id.id),
                            ('state','not in',['draft','cancel']),
                            ('add_type','=','temporary'),
                            ('start_date', '<=', rec.go_date), 
                            ('end_date', '>=', rec.back_date),
                            ('id', '!=', rec.id)])

                elif rec.add_type == 'temporary':
                    idss += self.search(cr, uid, [('vehicle_id','=',rec.vehicle_id.id),
                            ('state','not in',['draft','cancel']),
                            ('add_type','=','other'),
                            ('go_date', '<=', rec.start_date), 
                            ('back_date', '>=', rec.end_date),
                            ('id', '!=', rec.id)])

                    idss += self.search(cr, uid, [('vehicle_id','=',rec.vehicle_id.id),
                            ('state','not in',['draft','cancel']),
                            ('add_type','=','temporary'),
                            ('start_date', '<=', rec.start_date), 
                            ('end_date', '>=', rec.end_date),
                            ('id', '!=', rec.id)])

                elif rec.add_type == 'permanent':

                    permanent_idss += self.search(cr, uid, [('vehicle_id','=',rec.vehicle_id.id),
                            ('state','not in',['draft','cancel']),
                            ('add_type','=','permanent'),('id', '!=', rec.id)])
                    
                    if permanent_idss:

                        raise osv.except_osv(_('ValidateError'), _("You can not have 2 additional fuel records of type permanent for the same vehicle"))
                
                if idss:
                    raise osv.except_osv(_('ValidateError'), _("You can not have 2 additional fuel records that overlaps on same day for the same vehicle"))
            
        return True

    _constraints = [
        (_check_amount, '', []),
        (_check_date_unique, '', [])
    ]

    def create(self, cr, uid, vals, context=None):
        """
        """
        vehicle_obj = self.pool.get('fleet.vehicle')
        if vals['add_type'] != 'moving':
            rec = vehicle_obj.browse(cr, uid, vals['vehicle_id'], context=context)
            vals.update({'type':rec.type.id,'location':rec.location.id,'use':rec.use.id})
        seq = self.pool.get('ir.sequence').next_by_code(cr, uid, 'additional.fuel')
        vals['name'] = seq
        if not seq:
            raise  osv.except_osv(_('Warning'), _('No sequence defined!\nPleas contact administartor to configue sequence with code \'additional.fuel\'') )
        return super(additional_fuel, self).create(cr, uid, vals, context=context)

    def onchange_vehicle_id(self, cr, uid, ids, vehicle_id,distance_id,add_type,context=None):
        """
        @param vehicle_id: Id of vehicle
        @return: Dictionary of values 
        """
        vals={}
        domain={}
        domains=[]
        distance_obj=self.pool.get('fuel.distance.amount')
        amount_obj=self.pool.get('fuel.amount')
        if vehicle_id and add_type != 'moving':
            rec=self.pool.get('fleet.vehicle').browse(cr ,uid, vehicle_id,context=context)
            vals={'degree_id':rec.degree_id.id,'type':rec.type.id,'location':rec.location.id,'use':rec.use.id,'fuel_type':rec.fuel_type,'fuel_qty':rec.product_qty,
            'body_id':rec.vin_sn,'department_id':rec.department_id.id,'license_plate':rec.license_plate}
            distance_ids = distance_obj.search(cr,uid,[('fuel_distance_id','=',distance_id)])
            for dist in distance_obj.browse(cr,uid,distance_ids):
                if dist.fuel_amount_id.degree_id:
                    amount_ids = amount_obj.search(cr,uid,[('id','=',dist.fuel_amount_id.id),('degree_id','=',rec.degree_id.id),('vehicle_category','=',rec.type.id),('vehicle_place','=',rec.location.id),('vehicle_use','=',rec.use.id)])
                else:
                    amount_ids = amount_obj.search(cr,uid,[('id','=',dist.fuel_amount_id.id),('vehicle_category','=',rec.type.id),('vehicle_place','=',rec.location.id),('vehicle_use','=',rec.use.id)])
                if amount_ids:
                    domains.append(dist.id)
            domain={'fuel_amount_id':[('id','in',domains)]}
        return {'value':vals,'domain':domain}

    def onchange_add_type(self, cr, uid, ids, add_type,context=None):
        """
        @param add_type: add_type
        @return: Dictionary of values 
        """
        vals={}
        vals['filling']= False
        return {'value':vals}

    def onchange_fuel_amount_id(self, cr, uid, ids, fuel_amount_id, add_type,context=None):
        """
        @param fuel_amount_id: Id of fuel.amount
        @param add_type: add_type
        @return: Dictionary of values 
        """
        vals={}
        if fuel_amount_id:
            if add_type in ('other','moving'):
                vals['add_qty']=self.pool.get('fuel.distance.amount').browse(cr, uid, fuel_amount_id, context).fuel_amount
        return {'value':vals}

    def ochange_distance_id(self, cr, uid, ids, distance_id, context={}):
        """
        """
        comments = ''
        vals = {}
        if distance_id:
            comments = self.pool.get('fuel.distance').browse(cr, uid, distance_id).comments
        vals['comments'] = comments
        return {'value': vals}

    def confirm(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to confirm.

        @return: Boolean True
        """
        for rec in self.browse(cr, uid, ids, context=context):
            all_amount=0.0
            if rec.filling == 'several' and not rec.line_id:
                raise osv.except_osv(_('ValidateError'), _("you must enter fuel filling details!"))
        self.write(cr, uid, ids, {'state': 'confirm'}, context=context)
        return True



    def calc_total(self, cr, uid, ids, context=None):
	total_desc = total_fuel = 0.0
        for record in self.browse(cr, uid, ids, context):
		for line in record.dest_line_id :
			total_desc += line.no_distance
			total_fuel += line.no_fuel	
        self.write(cr, uid, ids, {'total_distance': total_desc,'total_fuel':total_fuel}, context=context)
        return True

    def cancel(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to cancel.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

    def done(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to done.

        @return: Boolean True
        """
        for rec in self.browse(cr, uid, ids, context):
            if rec.add_type not in ('other','moving','additional'):
                rec.vehicle_id.write({'additional_qty': rec.add_qty})
            rec.write({'state': 'done'})
        return True

    def reapprove(self, cr, uid, ids=None, use_new_cursor=False, context=None):
        """
        Mehtod that sets the state to reapprove.

        @return: Boolean True
        """
        if ids:
            for record in self.browse(cr, uid, ids, context):
                if record.add_type == 'temporary':
                    date=time.strftime('%Y-%m-%d')
                    today = datetime.datetime.strptime(date,"%Y-%m-%d")
                    add_fuel_ids = self.search(cr,uid,[('state','=','done'),('end_date','<=',today)])
                    for rec in self.browse(cr, uid, add_fuel_ids):
                        rec.vehicle_id.write({'additional_qty':rec.vehicle_id.additional_qty - rec.add_qty})
                        rec.write({'state': 'reapprove'})
        return True
        
    def approve(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to approve.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'approve'}, context=context)
        return True

    def set_to_draft(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to draft.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def unlink(self, cr, uid, ids, context={}):
        """
        Method that prevent delete record not in draft state
        @return : Super unlink function 
        """
        for rec in self.browse(cr, uid, ids, context):
            if rec.state != 'draft':
                raise osv.except_osv(_('Error'), _("You can not delete record not in the draft state!"))

        return super(additional_fuel, self).unlink(cr, uid, ids, context)

class moving_lines(osv.osv):
    """ 
    
    """
    _name = "moving.lines"

    def _total(self, cr, uid, ids, name, attr, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.fuel_pattarn == 'fixed':
                res[line.id] = line.number * line.amount
            if line.fuel_pattarn == 'different':
                res[line.id] = 0.0
                for vhc in line.line_id:
                    res[line.id] += vhc.amount
        return res

    def on_change_number(self, cr, uid, ids, amount, number, *a):
        """ Compute the total """
        return {'value' : {'total' : (amount * number) or 0.0 }}

    def on_change_amount(self, cr, uid, ids, amount, number, *a):
        """ Compute the total """
        return {'value' : {'total' : (amount * number) or 0.0 }}

    _columns = { 
       'add_fuel_id': fields.many2one('additional.fuel','additional fuel'),
       'vehicle_type': fields.many2one('vehicle.category','vehicle Type'),
       'number': fields.integer('Number'),
       'amount': fields.float('Amount'),
       'total': fields.function(_total,string="Total",type='float', digits_compute=dp.get_precision('Account')),
       'line_id': fields.one2many('vehicle.moving.lines','moving_id',"Moving Lines"),
       'fuel_pattarn': fields.selection([('fixed','Fixed'),('different','Different')],"fuel pattarn",track_visibility='onchange',),

    }


class destination_lines(osv.osv):
    """ 
    
    """
    _name = "destination.lines"


    def onchange_fuel_distance_amount(self, cr, uid, ids, distance_id,vehicle_id,fuel_type,context={}):
        no_distance = ''
	no_fuel = ''
	model = ''
        vals = {}
        if distance_id:
            no_distance = self.pool.get('fuel.distance').browse(cr, uid, distance_id).distance
	if distance_id and vehicle_id and fuel_type :
            fuel_amount_ids = self.pool.get('fuel.distance.amount').search(cr, uid, [('fuel_distance_id','=',distance_id)])
	    if not fuel_amount_ids : 
		raise osv.except_osv(_('Error'), _("Your Distination Configuration is Wrong Please modify it or contact system adminstrator"))
	    model = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id) 
	    fuel_distance_amount = self.pool.get('fuel.distance.amount').browse(cr, uid, fuel_amount_ids[0]).models_ids
	    for record in fuel_distance_amount :
			if record.model_id.id == model.model_id.id and record.fuel_type == model.fuel_type : 
            			no_fuel = record.fuel_amount_all_dist_l
        vals['no_distance'] = no_distance
        vals['no_fuel'] = no_fuel
        return {'value': vals}
    _columns = { 
       'add_dest_id': fields.many2one('additional.fuel','additional fuel'),
       'distance_id': fields.many2one('fuel.distance', 'fuel distance'),
       'no_distance': fields.float('Distance'),
       'no_fuel': fields.float('Fuel Per Litter'),
    }


class vehicle_moving_lines(osv.osv):
    """ 
    
    """
    _name = "vehicle.moving.lines"
    
    _columns = { 
       'moving_id': fields.many2one('moving.lines',"Moving Lines"),
       'vehicle_id': fields.many2one('fleet.vehicle',string="Vehicle"),
       'amount': fields.float('Amount'),
    }

class additional_fuel_lines(osv.osv):
    """ 
    
    """
    _name = "additional.fuel.lines"


    _columns = { 
       'add_fuel_id': fields.many2one('additional.fuel','additional fuel'),
       'location': fields.many2one('stock.location', 'Location',domain=[('usage','<>','view'),('fuel_ok','=',True)]),
       'amount': fields.float('Amount'),
    }

class fleet_vehicle(osv.Model):

    _inherit = "fleet.vehicle"

    _columns = { 
       'fuel_card': fields.char('Fuel Card Number'),
       'fuel_slice': fields.char('Fuel Slice Number',size=16),
    }

    def _check_unique(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check fuel_card and fuel_slice unique

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.fuel_card:
                fuel_card = self.search(cr,uid, [('fuel_card', '=', rec.fuel_card),('id','!=',rec.id)])
                if fuel_card:
                    raise osv.except_osv(_('ERROR'), _('Fuel Card Number must Be Unique'))
            if rec.fuel_slice:
                fuel_slice = self.search(cr,uid, [('fuel_slice', '=', rec.fuel_slice),('id','!=',rec.id)])
                if fuel_slice:
                    raise osv.except_osv(_('ERROR'), _('Fuel Slice Number must Be Unique'))
        return True

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.fuel_card:
                card=rec.fuel_card.strip()
                if not card:
                    raise osv.except_osv(_('ValidateError'), _("Fuel Card Number must not be spaces"))
        return True

    _constraints = [
         (_check_unique, '', []),
          (_check_spaces, '', []),
    ]

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        vehicle_type=context.get('vehicle_type', [])
        if vehicle_type:
            args.append(('type','=',vehicle_type))
        if 'vehicle_line' in context:
            line_ids = resolve_o2m_operations(cr, uid, self.pool.get('vehicle.moving.lines'),
                                                context.get('vehicle_line'), ["vehicle_id"], context)
            args.append(('id', 'not in', [isinstance(
                d['vehicle_id'], tuple) and d['vehicle_id'][0] or d['vehicle_id'] for d in line_ids]))

        return super(fleet_vehicle, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)

class vehicle_category(osv.Model):

    _inherit = "vehicle.category"

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        """
        Method that overwrites name_search method Search for vehicle.category That is not in line.

        @param name: Object name to search
        @param args: List of tuples specifying search criteria
        @param operator: Operator for search criterion
        @param limit: Max number of records to return
        @return: Super name_search method 
        """
        if context is None:
            context = {}
        if 'move_line_id' in context:
            type_ids = resolve_o2m_operations(cr, uid, self.pool.get('moving.lines'),
                                                context.get('move_line_id'), ["vehicle_type"], context)
            args.append(('id', 'not in', [isinstance(
                d['vehicle_type'], tuple) and d['vehicle_type'][0] or d['vehicle_type'] for d in type_ids]))

        return super(vehicle_category, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)



class fuel_amount(osv.osv):
    """ 
    To manage Fuel Amounts
    """
    _name = "fuel.amount"
    _rec_name = "degree_id"

    def name_get(self, cr, uid, ids, context=None):
        """override to compute name from other fields"""
        if not len(ids):
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.vehicle_category.name + '-' + record.vehicle_place.name + '-'
            if record.degree_id:
                name += record.degree_id.name + '-'
            name += record.vehicle_use.name 
            res.append((record.id,name))
        return res

    _columns = { 
       #'name': fields.function(_name_func, type="char", string='Name', store=True),
       'vehicle_category': fields.many2one('vehicle.category','Vehicle Type'),
       'vehicle_place': fields.many2one('vehicle.place','Vehicle Place'),
       'degree_id': fields.many2one('hr.salary.degree','Degree'),
       'vehicle_use': fields.many2one('fleet.vehicle.use','Vehicle Usage'),
       'fuel_amount': fields.float('Fuel Amount'),
       'company_id': fields.many2one('res.company','company'),
       'type': fields.selection([('management', 'Management'), ('dedicated', 'Dedicated'), ('dedicated_managemnet', 'Dedicated Management')], 'Use Type'),
       'vehicle_ids': fields.one2many('fleet.vehicle', 'fuel_amount_id', string='Vehicles', readonly=True),
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
        'company_id' : _default_company,
        'type': 'management'
            }


    def check_unique(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a place with the same name

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.fuel_amount <= 0.0:
                raise osv.except_osv(_('ERROR'), _('Fuel Amount Should be Greater Than Zero !') )
            domain = [('vehicle_category', '=', rec.vehicle_category.id),
                ('vehicle_place', '=', rec.vehicle_place.id),('type', '=', rec.type),
                ('vehicle_use', '=', rec.vehicle_use.id),('company_id', '=', rec.company_id.id),
                ('id','!=',rec.id)]
            if rec.type in ['dedicated','dedicated_managemnet']:
                domain.append((('degree_id', '=', rec.degree_id.id)))
            idss = self.search(cr,uid, domain)
            if idss:
                raise osv.except_osv(_('ERROR'), _('This fuel amount is already exisit for the company %s') % (rec.company_id.name))
        return True

    _constraints = [
         (check_unique, '', []),
    ]

    def onchange_vehicle_use(self, cr, uid, ids, vehicle_use, context={}):
        vals ={}
        vals['degree_id'] = False
        if vehicle_use:
            type = self.pool.get('fleet.vehicle.use').browse(cr, uid, vehicle_use, context).type
            vals['type'] = type
        return {'value': vals, 'domain':{}}


    def unlink(self, cr, uid, ids, context={}):
        for rec in self.browse(cr, uid, ids, context):
            if rec.vehicle_ids:
                raise osv.except_osv(_('ERROR'), _('You can not delete this record, there are vehicles use this fuel amount'))

        return super(fuel_amount, self).unlink(cr, uid, ids, context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        """
        write_boolean = super(fuel_amount,self).write(cr, uid, ids, vals, context=context)
        for rec in self.browse(cr, uid, ids):
            if 'fuel_amount' in vals:
                vehicles_ids = self.pool.get('fleet.vehicle').search(cr, uid, [('fuel_amount_id','=',rec.id)])
                if vehicles_ids:
                    self.pool.get('fleet.vehicle').write(cr, uid, vehicles_ids, {'product_qty': vals['fuel_amount']})

        return write_boolean

class fuel_distance(osv.osv):
    """ 
    To manage Fuel Distances
    """
    _name = "fuel.distance"
    _rec_name = "comments"

    _columns = {
       #'start_place': fields.many2one('vehicle.place','Moving Point'),
       #'end_place': fields.many2one('vehicle.place','Distination'),
       'start_place': fields.many2one('vehicle.dest','Moving Point'),
       'end_place': fields.many2one('vehicle.dest','Distination'),
       'distance': fields.float('Distance'),
       'company_id': fields.many2one('res.company','company'),
       'comments': fields.text('The route'),
    }

    def name_get(self, cr, uid, ids, context=None):
        """override to compute name from other fields"""
        if not len(ids):
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.start_place.name + '-' + record.end_place.name 
            res.append((record.id,name))
        return res

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id

        return company

    _defaults = {
        'company_id' : _default_company
    }


    def check_unique(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a place with the same name

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.start_place.id == rec.end_place.id:
                raise osv.except_osv(_('ERROR'), _('Distination should not be the Moving Point') )
            if rec.distance <= 0.0:
                raise osv.except_osv(_('ERROR'), _('Distance Should be Greater Than Zero !') )
            idss = self.search(cr,uid, [('start_place', '=', rec.start_place.id),
                ('end_place', '=', rec.end_place.id),('company_id', '=', rec.company_id.id),
                ('id','!=',rec.id)])
            if idss:
                raise osv.except_osv(_('ERROR'), _('This distination and distance is already exisit for the company %s') % (rec.company_id.name))
        return True

    _constraints = [
         (check_unique, '', []),
    ]

    def unlink(self, cr,uid, ids, context={}):
        """
        ovewrite super to check if this record is using by other record
        """
        for rec in self.browse(cr, uid, ids, context):
            idss = self.pool.get('fuel.distance.amount').search(cr, uid, [('fuel_distance_id','=',rec.id)])
            if idss:
                raise osv.except_osv(_('ERROR'), _('You can not delete this record, there are distinations and fuel amounts records use this distination and distance'))
        return super(fuel_distance, self).unlink(cr, uid, ids, context)

class fleet_vehicle_model(osv.Model):

    _inherit = "fleet.vehicle.model"

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):

        if 'models' in context:
            models = resolve_o2m_operations(cr, uid, self.pool.get('fleet.vehicle.model.distance.fuel'),
                                              context.get('models'), ["model_id"], context)
            args.append(('id', 'not in', [isinstance(d['model_id'], tuple) and d['model_id'][0] or d['model_id'] for d in models]))
        

        return super(fleet_vehicle_model, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)



class fleet_vehicle_model_distance_fuel(osv.osv):
    """ 
    To manage Fuel for vehicle in spcific Distance
    """
    _name = "fleet.vehicle.model.distance.fuel"

    _columns = { 
       'fuel_dis_conf': fields.many2one('fuel.distance.amount','Fuel Distance Configuration'),
       'model_id': fields.many2one('fleet.vehicle.model','Vehicle Model'),
       'fuel_type': fields.selection([('gasoline', 'Gasoline'), ('diesel', 'Benzene'), ('electric', 'Electric'), ('hybrid', 'Hybrid')],
                                      'Fuel Type'),
       'dist_fuel_amount': fields.float('Distance for Fuel Amount'),
       'fuel_amount_all_dist_g': fields.float('Fuel Amount for All Distance Gallons'),
       'fuel_amount_all_dist_l': fields.float('Fuel Amount for All Distance Liters'),
    }

    def onchange_dist_fuel_amount(self, cr, uid, ids,dist_fuel_amount,distance, context={}):
        vals = {}
        dist_fuel_amount = dist_fuel_amount or 0.0
        distance = distance or 0.0

        vals['fuel_amount_all_dist_g'] = distance/dist_fuel_amount
        vals['fuel_amount_all_dist_l'] = (distance/dist_fuel_amount)*3.78

        return {'value': vals}

    def check_unique(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check model and fuel type unique

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            idss = self.search(cr,uid, [('fuel_dis_conf', '=', rec.fuel_dis_conf.id),
                ('model_id', '=', rec.model_id.id),('fuel_type', '=', rec.fuel_type),
                ('id','!=',rec.id)])
            if idss:
                raise osv.except_osv(_('ERROR'), _('The model and fuel type must be unique') )
        return True

    _constraints = [
         (check_unique, '', []),
    ]

class fuel_distance_amount(osv.osv):
    """ 
    To manage Fuel Distance and Amounts
    """
    _name = "fuel.distance.amount"
    _rec_name = "comments"

    _columns = { 
       #'name': fields.char( string='Name', store=True),
       'fuel_distance_id': fields.many2one('fuel.distance','Distination',required=True),
       'fuel_amount_id': fields.many2one('fuel.amount','Consumed Fuel Amount'),
       'distance': fields.related('fuel_distance_id', 'distance', type="float", string='Distance'),
       'comments': fields.related('fuel_distance_id', 'comments', type="char", string='The route'),
       'vehicle_place': fields.related('fuel_amount_id', 'vehicle_place', type="many2one",relation="vehicle.place",string='Vehicle Place'),
       'vehicle_use': fields.related('fuel_amount_id', 'vehicle_use', type="many2one",relation="fleet.vehicle.use",string='Vehicle Usage'),
       'vehicle_category': fields.related('fuel_amount_id', 'vehicle_category', type="many2one",relation="vehicle.category",string='Vehicle Type'),
       'degree_id': fields.related('fuel_amount_id', 'degree_id', type="many2one",relation="hr.salary.degree",string='Degree'),
       'type': fields.selection([('management', 'Management'), ('dedicated', 'Dedicated')], 'Use Type'),
       'company_id': fields.many2one('res.company','company'),
       'fuel_amount': fields.float('Fuel Amount'),
       'models_ids': fields.one2many('fleet.vehicle.model.distance.fuel', 'fuel_dis_conf', 'Models'),
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
        'company_id' : _default_company,
        #'name' : '/',
    }

    def create(self, cr, uid, vals, context={}):
        """
        override create to give the name sequence
        """
        #seq_obj_name =  self._name
        #vals['name'] = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name) or '/'

        return super(fuel_distance_amount, self).create(cr, uid, vals, context)


    def onchange_fuel_distance_id(self, cr, uid, ids,fuel_distance_id, context={}):
        fuel_distance_obj = self.pool.get('fuel.distance')
        comments = ''
        distance = 0.0
        vals = {}
        if fuel_distance_id:
            distance = fuel_distance_obj.browse(cr, uid, fuel_distance_id).distance
            comments = fuel_distance_obj.browse(cr, uid, fuel_distance_id).comments
        vals['distance'] = distance
        vals['comments'] = comments

        return {'value': vals}

    def onchange_fuel_amount_id(self, cr, uid, ids,fuel_amount_id, context={}):
        fuel_amount_obj = self.pool.get('fuel.amount')
        vals = {}
        if fuel_amount_id:
            fuel_amount_rec = fuel_amount_obj.browse(cr, uid, fuel_amount_id)
            vehicle_use = fuel_amount_obj.browse(cr, uid, fuel_amount_id).vehicle_use.id
            vehicle_place = fuel_amount_obj.browse(cr, uid, fuel_amount_id).vehicle_place.id
            vals['vehicle_use'] = fuel_amount_rec.vehicle_use.id
            vals['vehicle_place'] = fuel_amount_rec.vehicle_place.id
            vals['vehicle_category'] = fuel_amount_rec.vehicle_category.id
            vals['degree_id'] = fuel_amount_rec.degree_id and fuel_amount_rec.degree_id.id or False
            vals['type'] = fuel_amount_rec.type
        else:
            vals = {'vehicle_use': False, 'vehicle_place': False, 'vehicle_category':False,
                    'degree_id':False, 'type':False}

        return {'value': vals}

    def check_unique(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a place with the same name

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            # if rec.fuel_amount <= 0.0:
            #     raise osv.except_osv(_('ERROR'), _('Fuel Amount Should be Greater Than Zero !') )
            idss = self.search(cr,uid, [('fuel_distance_id', '=', rec.fuel_distance_id.id),
                ('fuel_amount_id', '=', rec.fuel_amount_id.id),('company_id', '=', rec.company_id.id),
                ('id','!=',rec.id)])
            if idss:
                raise osv.except_osv(_('ERROR'), _('This fuel distination and amount is already exisit for the company %s') % (rec.company_id.name))
        return True

    _constraints = [
         (check_unique, '', []),
    ]

    def name_get(self, cr, uid, ids, context=None):
        """override to compute name from other fields"""
        if not len(ids):
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            #name = record.fuel_amount_id.name_get()[0][1] + _('Destination') + record.fuel_distance_id.name_get()[0][1]
            #record.fuel_amount_id
            #name = record.fuel_amount_id.vehicle_category.name + '-' + record.fuel_amount_id.vehicle_place.name + '-'
            #if record.fuel_amount_id.degree_id:
            #    name += record.fuel_amount_id.degree_id.name + '-'
            #name += record.fuel_amount_id.vehicle_use.name 
            #seq_obj_name =  self._name
            #name = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
            name = record.comments
            res.append((record.id,name))
        return res

    
    def unlink(self, cr,uid, ids, context={}):
        """
        ovewrite super to check if this record is using by other record
        """
        for rec in self.browse(cr, uid, ids, context):
            idss = self.pool.get('additional.fuel').search(cr, uid, [('fuel_amount_id','=',rec.id)])
            if idss:
                raise osv.except_osv(_('ERROR'), _('You can not delete this record, there are additional fuel records use this distination and fuel amount'))
        return super(fuel_distance_amount, self).unlink(cr, uid, ids, context)

            


    
#--------------------------
#   vehicle Fuel Slice
#--------------------------
class  vehicle_fuel_slice(osv.osv):
    """ To manage vehicle places """
    _name = "vehicle.fuel.slice"
    _order = "date desc, id desc"
    _columns = {
        'vehicle_id': fields.many2one('fleet.vehicle','Vehicle'),
        'employee_id': fields.many2one('hr.employee','Employee'),
        'degree_id': fields.many2one('hr.salary.degree','Degree'),
        'department_id': fields.many2one('hr.department','Department'),
        #'department_id': fields.related('vehicle_id','department_id',type="many2one",relation="hr.department",string="Department", store=True),
        'vin_sn': fields.char('Chassis Number', size=32),
        'machine_no': fields.char('Machine No', size=64),
        'license_plate': fields.char('License Plate', size=32),
        'date': fields.date('Date'),
        'product_id': fields.many2one('product.product', 'Fuel'),
        'previous_product_id': fields.many2one('product.product', 'Previous Fuel'),
        'fuel_card': fields.char('Fuel Card Number'),
        'fuel_slice': fields.char('Fuel Slice Number',size=16),
        'previous_fuel_card': fields.char('Previous Fuel Card Number'),
        'previous_fuel_slice': fields.char('Previous Fuel Slice Number',size=16),
        'process_type': fields.selection([('modify','Modify'),('insert','Insert')],'Process Type'),
        'state': fields.selection([('draft','Draft'),('confirm','Confirm')],'State'),
        'fuel_type': fields.selection([('gasoline', 'Gasoline'), ('diesel', 'Benzene'), ('electric', 'Electric'), ('hybrid', 'Hybrid')],
                                      'Fuel Type'),
        'company_id': fields.many2one('res.company','company'),
        'type': fields.related('vehicle_id','type',type="many2one",relation="vehicle.category",string="Vehicle Category", store=True),
        'year': fields.related('vehicle_id','year',type="char",string="Vehicle Model", store=True),
        'model_id': fields.related('vehicle_id','model_id',type="many2one",relation="fleet.vehicle.model",string="Vehicle Brand", store=True),
        
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
        'date': time.strftime('%Y-%m-%d'),
    }

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False):
        try:
            res = super(vehicle_fuel_slice,self).read_group(cr, uid, domain, fields, groupby, offset=offset, limit=limit, context=context, orderby=orderby)
        except :
            return []
        new_res = []
        for i in res:
            if 'process_type' in i:
                i['process_type'] = i['process_type'] == 'insert' and u'إدخال' or i['process_type'] =='modify' and u'تعديل'
            new_res.append(i)
        return new_res

    def name_get(self, cr, uid, ids, context=None):
        return ids and [(item.id, "%s" % ( item.vehicle_id.name,)) for item in self.browse(cr, uid, ids, context=context)] or []

    def create(self, cr, uid, vals, context=None):
        """
        Override create method to change vals based on vehicle_id 
        @return: super create method
        """
        if 'vehicle_id' in vals:
            onchange_vals = self.onchange_vehicle_id(cr, uid, [], vals['vehicle_id'], context)['value']
            vals.update({
                'employee_id': onchange_vals['employee_id'],
                'degree_id': onchange_vals['degree_id'],
                'license_plate': onchange_vals['license_plate'],
                'department_id': onchange_vals['department_id'],
                'vin_sn': onchange_vals['vin_sn'] ,
                'machine_no': onchange_vals['machine_no'] ,
                'previous_product_id': onchange_vals['previous_product_id'] ,
                'previous_fuel_card': onchange_vals['previous_fuel_card'] ,
                'previous_fuel_slice':onchange_vals['previous_fuel_slice'] ,
                'fuel_type': onchange_vals['fuel_type'], 
                })

        if 'fuel_slice' in vals and vals['fuel_slice']:
            vals.update({'fuel_slice': vals['fuel_slice'].strip()})

        if 'fuel_card' in vals and vals['fuel_card']:
            vals.update({'fuel_card': vals['fuel_card'].strip()})

        return super(vehicle_fuel_slice, self).create(cr, uid, vals, context=context)


    def write(self, cr, uid, ids, vals, context=None):
        """
        """
        if 'vehicle_id' in vals:
            onchange_vals = self.onchange_vehicle_id(cr, uid, ids, vals['vehicle_id'], context)['value']
            vals.update({
                'employee_id': onchange_vals['employee_id'],
                'degree_id': onchange_vals['degree_id'],
                'license_plate': onchange_vals['license_plate'],
                'department_id': onchange_vals['department_id'],
                'vin_sn': onchange_vals['vin_sn'] ,
                'machine_no': onchange_vals['machine_no'] ,
                'previous_product_id': onchange_vals['previous_product_id'] ,
                'previous_fuel_card': onchange_vals['previous_fuel_card'] ,
                'previous_fuel_slice':onchange_vals['previous_fuel_slice'] ,
                'fuel_type': onchange_vals['fuel_type'], 
                })

        if 'fuel_slice' in vals and vals['fuel_slice']:
            vals.update({'fuel_slice': vals['fuel_slice'].strip()})

        if 'fuel_card' in vals and vals['fuel_card']:
            vals.update({'fuel_card': vals['fuel_card'].strip() })


        return super(vehicle_fuel_slice, self).write(cr, uid, ids, vals, context=context)


    def onchange_vehicle_id(self, cr, uid, ids, vehicle_id, context={}):
        """
        """
        vals = {'employee_id': False,
                'department_id': False,
                'vin_sn': False,
                'machine_no': False,
                'previous_product_id': False,
                'previous_fuel_card': False,
                'previous_fuel_slice': False,
                'fuel_type': False,
                'product_id': False,
                'fuel_card': False,
                'fuel_slice': False,
                'degree_id': False,
                'license_plate': False,
                }
        domain = []
        if vehicle_id:
            vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id)
            employee_id = (vehicle.employee_id and vehicle.employee_id.id) or (vehicle.driver and vehicle.driver.id) or False
            degree_id = (vehicle.degree_id and vehicle.degree_id.id) or (vehicle.employee_id and vehicle.employee_id.degree_id.id) or (vehicle.driver and vehicle.driver.degree_id.id) or False
            vals = {'employee_id': employee_id,
                    'degree_id': degree_id,
                    'license_plate': vehicle.license_plate or False,
                    'department_id': vehicle.department_id and vehicle.department_id.id or False,
                    'vin_sn': vehicle.vin_sn or False,
                    'machine_no': vehicle.machine_no or False,
                    'previous_product_id': vehicle.product_id and vehicle.product_id.id or False,
                    'previous_fuel_card': vehicle.fuel_slice or False,
                    'previous_fuel_slice': vehicle.fuel_card or False,
                    'fuel_type': vehicle.fuel_type or False,
                    'product_id': vehicle.product_id and vehicle.product_id.id or False,
                    'fuel_card': vehicle.fuel_slice or False,
                    'fuel_slice': vehicle.fuel_card or False,}

        return {'value': vals}


    def confirm(self, cr, uid, ids, context={}):
        """
        """
        for rec in self.browse(cr, uid, ids):
            if not rec.product_id and not rec.fuel_card and not rec.fuel_slice:
                raise osv.except_osv(_(''), _('Please Entering updated data'))
            vals = {
            'product_id': (rec.product_id and rec.product_id.id) or (rec.previous_product_id and rec.previous_product_id.id) or False,
            'fuel_card': (rec.fuel_slice and rec.fuel_slice) or (rec.previous_fuel_slice and rec.previous_fuel_slice) or False,
            'fuel_slice': (rec.fuel_card and rec.fuel_card) or (rec.previous_fuel_card and rec.previous_fuel_card) or False,

            }
            rec.vehicle_id.write(vals)

        return self.write(cr, uid, ids, {'state':'confirm'})


    def set_to_draft(self, cr, uid, ids, context={}):
        """
        """

        for rec in self.browse(cr, uid, ids):
            vals = {
            'product_id': rec.previous_product_id and rec.previous_product_id.id or False,
            'fuel_card': rec.previous_fuel_slice and rec.previous_fuel_slice or False,
            'fuel_slice': rec.previous_fuel_card and rec.previous_fuel_card or False,
            }
            rec.vehicle_id.write(vals)

        return self.write(cr, uid, ids, {'state':'draft'})


    def onchange_fuel_card(self,cr, uid, ids, fuel_card, context={}):
        """
        """
        vals = {}
        if fuel_card:
            vals['fuel_card'] = vals['fuel_card'].strip()

        return {'value': vals}


    def onchange_fuel_slice(self,cr, uid, ids, fuel_slice, context={}):
        """
        """
        vals = {}
        if fuel_slice:
            vals['fuel_slice'] = vals['fuel_slice'].strip()

        return {'value': vals}


class fuel_well(osv.osv):
    """ 
    To manage Fuel Wells
    """
    _name = "fuel.well"
    _rec_name = "name"

    _columns = { 
       'name': fields.char( string='Name'),
       'fuel_type': fields.selection([('gasoline', 'Gasoline'), ('diesel', 'Benzene'), ('electric', 'Electric'), ('hybrid', 'Hybrid')],
                                      'Fuel Type'),
       'company_id': fields.many2one('res.company','company'),
       'store_amount': fields.float('Store Amount'),
       'station': fields.many2one('stock.location', 'Station'),
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
        'company_id' : _default_company,
        'name' : '/',
    }

class picking_well(osv.osv):
    """ 
    To manage picking Wells
    """
    _name = "picking.well"

    _columns = { 
       'fuel_type': fields.related('well_id', 'fuel_type', 
        type="selection",selection=[('gasoline', 'Gasoline'), ('diesel', 'Benzene'), ('electric', 'Electric'), ('hybrid', 'Hybrid')], string="Fuel Type"),
        
       'well_id': fields.many2one('fuel.well','Well'),
       'before_amount': fields.float('Before Amount'),
       'after_amount': fields.float('After Amount'),
       'recieved_amount': fields.float('Recieved Amount'),
       'picking_id': fields.many2one('stock.picking', 'Picking', ondelete="cascade"),
    }

    _sql_constraints = [
        ('name_uniq', 'unique(picking_id, well_id)', 'Picking Well Must be Unique!!!'),
    ]

    def check_capicity(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a place with the same name

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.recieved_amount > rec.well_id.store_amount:
                raise osv.except_osv(_('ERROR'), _('This well can not recieve more than it\'s capacity %s') % (rec.well_id.name))
        return True

    _constraints = [
         (check_capicity, '', []),
    ]

    def onchange_quantity(self,cr , uid, ids, before_amount,after_amount, context={}):
        """
        """
        vals = {'recieved_amount': 0.0}
        vals['recieved_amount'] = after_amount - before_amount
        if before_amount and after_amount:
            vals['recieved_amount'] = after_amount - before_amount

        return {'value': vals}

    def write(self, cr, uid, ids, vals, context=None):
        """
        """
        read = self.read(cr, uid, ids,[])
        if 'before_amount' in vals or 'after_amount' in vals:
            read = read[0]
            read['before_amount'] = 'before_amount' in vals and vals['before_amount'] or read['before_amount']
            read['after_amount'] = 'after_amount' in vals and vals['after_amount'] or read['after_amount']
            onchange_quantity = self.onchange_quantity(cr, uid, [],read['before_amount'], read['after_amount'], context)['value']
            vals['recieved_amount'] = onchange_quantity['recieved_amount']

        
        return super(picking_well, self).write(cr, uid, ids, vals, context)

    def create(self, cr, uid, vals, context=None):
        """
        """
        if 'before_amount' in vals or 'after_amount' in vals:
            onchange_quantity = self.onchange_quantity(cr, uid, [],vals['before_amount'], vals['after_amount'], context)['value']
            vals['recieved_amount'] = onchange_quantity['recieved_amount']
        return super(picking_well, self).create(cr, uid, vals, context)
            


class fuel_evaporation(osv.osv):
    """ 
    To manage Fuel evaporations
    """
    _name = "fuel.evaporation"
    _rec_name = "fuel_product"

    _columns = { 
       'fuel_product': fields.many2one('product.product', 'Fuel'),
       'percentage': fields.float('percentage %100', digits=(16,6)),
    }

    def check_valid(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check valid

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.percentage < 0:
                raise osv.except_osv(_('ERROR'), _('percentage must be greater than zero'))
            if self.search(cr, uid, [('id', '!=', rec.id), ('fuel_product', '=', rec.fuel_product.id)]):
                raise osv.except_osv(_('ERROR'), _('Fuel can not duplicated'))
        return True

    _constraints = [
         (check_valid, '', []),
    ]


    def evaporation_scheduler(self, cr, uid, context=None):
        """ 
        create picking out every day

        @return: boolean True or False
        """

        stock_location_obj = self.pool.get('stock.location')
        outgoing_fuel_type_obj = self.pool.get('outgoing.fuel.type')
        stock_move_obj = self.pool.get('stock.move')
        stock_picking_out_obj = self.pool.get('stock.picking.out')
        outgoing_fuel_type = outgoing_fuel_type_obj.search(cr, uid, [('evaporation_type','=',True)], context=context)

        if not outgoing_fuel_type:
            return 
        outgoing_fuel_type = outgoing_fuel_type[0]

        to_stock_location_ids = stock_location_obj.search(cr, uid, [('fuel_ok','=',True), ('usage','=','customer')], context=context)
        if not to_stock_location_ids:
            return
        to_stock_location_ids = to_stock_location_ids[0]

        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        partner_id = user.company_id.partner_id.id
        stock_location_ids = stock_location_obj.search(cr, uid, [('fuel_ok','=',True), ('usage','=','internal')], context=context)
        
        to_time = datetime.datetime.now()
        ids = self.search(cr, uid, [], context=context)
        for rec in self.browse(cr, uid, ids, context=context):
            stock_real = stock_location_obj._product_value(cr, uid, stock_location_ids, ['stock_real'], False, context={'product_id':rec.fuel_product.id})
            for station in stock_real:
                if stock_real[station]['stock_real'] <= 0.0:
                    continue
                evaporation_value = stock_real[station]['stock_real'] * rec.percentage
                evaporation_value = evaporation_value / 100.0
                #evaporation_value = round(evaporation_value, 2)

                line_dict = {'date_expected': to_time, 
                        'fuel_ok': True, 'date': to_time, 
                        'partner_id': partner_id, 'location_id': station, 'hq': user.company_id.hq, 
                        'company_id': user.company_id.id, 'product_packaging': False,
                        'location_dest_id': to_stock_location_ids, 'tracking_id': False, 
                        'type': 'out', 'product_id': rec.fuel_product.id, 'product_qty':evaporation_value,
                        'state':'done'}

                line_on_change = stock_move_obj.onchange_product_id(cr, uid,[], rec.fuel_product.id,station,to_stock_location_ids, partner_id)
                
                for field in line_on_change['value']:
                    line_dict[field] = line_on_change['value'][field]

                line_on_change = stock_move_obj.onchange_quantity(cr, uid, [], rec.fuel_product.id, evaporation_value,
                          line_dict['product_uom'], line_dict['product_uos'])
                
                for field in line_on_change['value']:
                    line_dict[field] = line_on_change['value'][field]

                line_dict['product_qty'] = evaporation_value
                vals = {'origin': False, 'auto_picking': False, 
                        'move_lines': 
                        [[0, False, line_dict]], 
                        'fuel_ok': True, 'message_follower_ids': False, 'type': 'out', 
                        'fuel_delegate_id': False, 'move_type': 'direct', 
                        'invoice_state': 'none', 'message_ids': False, 
                        'note': u'سجل حساب التبخر', 'date': to_time, 
                        'outgoing_fuel_type': outgoing_fuel_type, 'date_done': False, 
                        'fuel_product_id': False, 'fleet_employee_id': False, 
                        'stock_fuel_id': [], 'partner_id': False, 'fuel_type': False, 
                        'stock_journal_id': False, 'state':'done'}
                stock_picking_out_obj.create(cr, uid, vals)
                
                


        return True