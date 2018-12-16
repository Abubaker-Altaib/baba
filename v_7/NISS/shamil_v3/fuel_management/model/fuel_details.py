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

class fuel_stop_reasons(osv.osv):

    _name = "fuel.stop.reasons"
    
    _columns = {
        'name': fields.char('Name', required=True),
        'company_id': fields.many2one('res.company','Company'),
    }

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            idss = self.pool.get('fleet.fuel').search(cr, uid, [('fuel_stop_reason_id','=',rec.id)])
            if idss:
                raise osv.except_osv(
                    _(''), _("can not delete record linked with other record"))
        return super(fuel_stop_reasons, self).unlink(cr, uid, ids, context=context)


    def onchange_name(self, cr, uid, ids, name, context={}):
        """
        """
        vals = {}
        if name:
            vals['name'] = name.strip()

        return {'value': vals}


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
    }


class fleet_vehicle(osv.osv):
    """ 
    To manage operation of fleet vehicle
    """

    def get_uom_domin(self, cr, uid, ids, pro_id, context=None):
        """ 
        On change product id field value function gets the domin of Product uom.

        @param pro_id: id of current product
        @return: Dictionary of product_uom default value with product_uom domin
        """
        res = {'value': {}, 'domain': {}}
        if pro_id:
            pro_cat = self.pool.get('product.product').browse(
                cr, uid, pro_id, context=context).uom_id
            res = {
                'value': {
                    'product_uom': pro_cat.id,
                },
                'domain': {
                    'product_uom': [('category_id', '=', pro_cat.category_id.id)],
                }
            }
        return res

    def get_product_qty(self, cr, uid, ids, typee, location, employee_id, use, company_id, fuel_type, department_id, belong_to, context={}):
        """ 
        On change product id field value function gets the domin of Product uom.

        @param pro_id: id of current product
        @return: Dictionary of product_uom default value with product_uom domin
        """
        vals = {}
        domain_vals = {}
        fuel_amount_obj = self.pool.get('fuel.amount')
        emp_obj = self.pool.get('hr.employee')
        custody_obj = self.pool.get('fleet.vehicle.custody')
        # To make employee_id and department_id requierd base on use type
        vals['employee_id'] = False
        vals['department_id'] = False
        vals['use_type'] = False
        domain_vals['employee_id'] = [('id','in',[])]
        domain_vals['department_id'] = [('id','in',[])]
        #To set custodys value and domain base on type
        if typee:
            ttype=[]
            custodys = custody_obj.search(cr, uid, [('default', '=', True)])
            custodyss = custody_obj.browse(cr, uid, custodys, context=context)
            for custody in custodyss:
                for t in custody.vehicle_type:
                    if t.id == typee:
                        ttype.append(custody.id)
            vals['custody_ids']=ttype

            ttype=[]
            custodys = custody_obj.search(cr, uid, [])
            custodyss = custody_obj.browse(cr, uid, custodys, context=context)
            for custody in custodyss:
                for t in custody.vehicle_type:
                    if t.id == typee:
                        ttype.append(custody.id)
            domain_vals['custody_ids']=[('id', 'in', ttype)]
        if use:
            vals['use_type'] = self.pool.get('fleet.vehicle.use').browse(
                cr, uid, use, context=context).type
            if not belong_to or belong_to == 'in':
                if vals['use_type'] == 'dedicated':
                    vals['employee_id'] = False
                    vals['department_id'] = False
                    domain_vals['employee_id'] = [('state','=','approved')]
                    domain_vals['department_id'] = [('id','in',[])]
                    if employee_id:
                        department = emp_obj.browse(cr, uid, employee_id).department_id.id
                        vals['department_id'] = department
                        domain_vals['department_id'] = [('id','in',[department])]
                        vals['employee_id'] = employee_id
                else:
                    vals['employee_id'] = False
                    vals['department_id'] = False
                    domain_vals['employee_id'] = [('id','in',[])]
                    dep_ids = self.pool.get('hr.department').search(cr,uid,[])
                    domain_vals['department_id'] = [('id','in',dep_ids)]
                    if department_id:
                        #department = emp_obj.browse(cr, uid, employee_id).department_id.id
                        domain_vals['employee_id'] = [('department_id','in',[department_id])]
                        vals['department_id'] = department_id
                        if employee_id:
                            department = emp_obj.browse(cr, uid, employee_id).department_id.id
                            vals['employee_id'] = department in [department_id] and employee_id or False
                    
        
        vals['product_qty'] = 0.0
        vals['product_id'] = False
        vals['fuel_amount_id'] = False
        if typee and location and use and company_id:

            domain = [('vehicle_category', '=', typee), ('vehicle_place', '=', location),
                      ('company_id', '=', company_id), ('vehicle_use', '=', use)]
            if vals['use_type'] in ['dedicated','dedicated_managemnet'] and employee_id:
                degree = emp_obj.browse(cr, uid, employee_id).degree_id.id
                department = emp_obj.browse(cr, uid, employee_id).department_id.id
                domain.append(('degree_id', '=', degree))

            idss = fuel_amount_obj.search(cr, uid, domain , context=context)
            if idss:
                amount = fuel_amount_obj.browse(cr, uid, idss[0]).fuel_amount
                vals['product_qty'] = amount
                vals['fuel_amount_id'] = idss[0]
            else:
                vals['product_qty'] = 0.0
                vals['fuel_amount_id'] = False

        if location and fuel_type:
            product_id = self.pool.get('product.product').search(cr, uid, [(
                'fuel_ok', '=', True), ('location', '=', location), ('fuel_type', '=', fuel_type)])
            if product_id:
                vals['product_id'] = product_id[0]
                vals['product_uom'] = self.get_uom_domin(cr, uid, ids, product_id[0], context)[
                    'value']['product_uom']

        return {'value': vals, 'domain': domain_vals}

    def reset_id(self, cr, uid, ids, context=None):
        """ 
        On change fuel type field value function rest product id value.

        @return: Dictionary of product_id new value
        """
        return {'value': {
            'product_id': False,
            'product_uom': False,
        }
        }

    def _check_negative(self, cr, uid, ids, context=None):
        """ 
        Check the value of fuel tank capacity and quantity,
        if greater than zero or not.

        @return: Boolean of True or False
        """
        count = 0
        for fuel in self.browse(cr, uid, ids, context=context):
            message = _("The Value Of ")
            if (fuel.fueltankcap <= 0) and fuel.state != 'draft':
                raise osv.except_osv(_('ValidateError'), _(
                    "The Value Of Tank Capacity Must Be Greater Than Zero!"))

            '''if fuel.monthly_plan == True and rec.state == 'confirm':
                if (fuel.product_qty <= 0):
                    if (count > 0):
                        message += _(" And ")
                    message += _("Fuel Quantity")
                    count += 1
                    raise osv.except_osv(_('ValidateError'), _("You should Have Fuel amount For The Type %s and The Degree %s and The Location %s and The Use %s and the Company %s !")%(fuel.type.name, fuel.employee_id.degree_id.name, fuel.location.name, fuel.use.name, fuel.company_id.name))'''
        return True

    def _check_fuel_amount(self, cr, uid, ids, context=None):
        """ 
        Check the value of fuel tank capacity and quantity,
        if greater than zero or not.

        @return: Boolean of True or False
        """
        fuel_amount_obj = self.pool.get('fuel.amount')
        count = 0
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state == 'confirm' and rec.status == 'active':
                if rec.monthly_plan and rec.product_qty <= 0.0:
                    domain = [('vehicle_category', '=', rec.type.id),
                              ('vehicle_place', '=', rec.location.id),
                              ('company_id', '=', rec.company_id.id), ('vehicle_use', '=', rec.use.id)]
                    if rec.use.type in ['dedicated','dedicated_managemnet'] and rec.degree_id:
                        domain.append(('degree_id', '=', rec.degree_id.id))
                    idss = fuel_amount_obj.search(
                        cr, uid, domain, context=context)
                    if not idss and rec.use.type == 'dedicated':
                        raise osv.except_osv(_('ValidateError'), _("You should Have Fuel amount For The Type %s and The Degree %s and The Location %s and The Use %s and the Company %s !") % (
                            rec.type.name, rec.employee_id.degree_id.name, rec.location.name, rec.use.name, rec.company_id.name))

                    elif not idss:
                        raise osv.except_osv(_('ValidateError'), _("You should Have Fuel amount For The Type %s and The Location %s and The Use %s and the Company %s !") % (
                            rec.type.name, rec.location.name, rec.use.name, rec.company_id.name))

                    else:
                        if idss and fuel_amount_obj.browse(cr, uid, idss[0], context).fuel_amount == 0.0:
                            raise osv.except_osv(_('ValidateError'), _("You should Have Fuel amount greater than 0 For The Type %s and The Location %s and The Use %s and the Company %s !") % (
                                rec.type.name, rec.location.name, rec.use.name, rec.company_id.name))

                if rec.monthly_plan and not rec.product_id:
                    raise osv.except_osv(_('ValidateError'), _(
                        "There Is No fuel with The selected location and fuel type"))
        return True

    _inherit = "fleet.vehicle"

    _columns = {
        'monthly_plan': fields.boolean('Monthly Plan',),
        'fueltankcap': fields.float('Tank Capacity', states={'confirm': [('readonly', True)]},
                                    help="The unit of measurement Of Tank Capacity depends on the measuring unit of Car fuel"),
        'product_id': fields.many2one('product.product', 'Fuel', states={'confirm': [('readonly', True)]}),
        'product_qty': fields.float('Fuel Quantity',),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', states={'confirm': [('readonly', True)]}),
        'fuel_plan_ids': fields.one2many('fuel.qty.line', 'vehicles_id', string='Fuel Plans',
                                         readonly=True),
        'additional_qty': fields.float('Fuel Additional Quantity',),
        'fuel_amount_id': fields.many2one('fuel.amount', 'Fuel Amount'),
        'fuel_exchange_status': fields.selection([('exchange','Currently Disbursed'),('stop','Stopped')], 'Fuel Exchange Status'),
        'fuel_stop_reason_id': fields.many2one('fuel.stop.reasons', 'Fuel Stopped Reason'),
    }

    _constraints = [
        #(_check_negative, '', []),
        (_check_fuel_amount, '', []),
    ]

    def create(self, cr, uid, vals, context=None):
        """
        To set status of vehicle inactive base on vehicle_status
        """

        typee = 'type' in vals and vals['type'] or False
        location = 'location' in vals and vals['location'] or False
        employee_id = 'employee_id' in vals and vals['employee_id'] or False
        use = 'use' in vals and vals['use'] or False
        fuel_type = 'fuel_type' in vals and vals['fuel_type'] or False
        company_id = 'company_id' in vals and vals['company_id'] or False
        department_id = 'department_id' in vals and vals['department_id'] or False
        belong_to = 'belong_to' in vals and vals['belong_to'] or False

        onchange_vals = self.get_product_qty(
            cr, uid, [], typee, location, employee_id, use, company_id, fuel_type, department_id, belong_to, context)

        vals['product_qty'] = onchange_vals['value']['product_qty']
        vals['product_id'] = 'product_id' in onchange_vals['value'] and onchange_vals['value']['product_id'] or False
        vals['fuel_amount_id'] = onchange_vals['value']['fuel_amount_id']
        onchange_val2 = self.get_uom_domin(
            cr, uid, [], vals['product_id'], context)
        vals['product_uom'] = 'product_uom' in onchange_val2['value'] and onchange_val2['value']['product_uom'] or False

        return super(fleet_vehicle, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        To set product_qty and product_id
        """
        rec = self.browse(cr, uid, ids[0], context)

        typee = 'type' in vals and vals['type'] or (
            rec.type and rec.type.id) or False
        location = 'location' in vals and vals['location'] or (
            rec.location and rec.location.id) or False
        employee_id = 'employee_id' in vals and vals['employee_id'] or (
            rec.employee_id and rec.employee_id.id) or False
        use = 'use' in vals and vals['use'] or (
            rec.use and rec.use.id) or False
        fuel_type = 'fuel_type' in vals and vals['fuel_type'] or (
            rec.fuel_type and rec.fuel_type) or False
        company_id = 'company_id' in vals and vals['company_id'] or (
            rec.company_id and rec.company_id.id) or False
        department_id = 'department_id' in vals and vals['department_id'] or (
            rec.department_id and rec.department_id.id) or False
        belong_to = 'belong_to' in vals and vals['belong_to'] or (
            rec.belong_to and rec.belong_to) or False

        onchange_vals = self.get_product_qty(
            cr, uid, ids, typee, location, employee_id, use, company_id, fuel_type, department_id, belong_to, context)

        vals['product_qty'] = onchange_vals['value']['product_qty']
        vals['product_id'] = 'product_id' in onchange_vals['value'] and onchange_vals['value']['product_id'] or False
        vals['fuel_amount_id'] = onchange_vals['value']['fuel_amount_id']
        onchange_val2 = self.get_uom_domin(
            cr, uid, ids, vals['product_id'], context)
        vals['product_uom'] = 'product_uom' in onchange_val2['value'] and onchange_val2['value']['product_uom'] or False

        return super(fleet_vehicle, self).write(cr, uid, ids, vals, context)
