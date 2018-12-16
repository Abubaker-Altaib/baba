# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv,fields
from tools.translate import _
from datetime import date,datetime,timedelta

class fleet_vehicle_cost(osv.Model):
    """
    To manage cost amounts of vehicle.
    """
    _inherit = 'fleet.vehicle.cost'

    _columns = {
        'vehicle_id': fields.many2one('fleet.vehicle', 'Vehicle', required=False, help='Vehicle concerned by this log'),
    }


class fleet_vehicle_fuel(osv.Model):
    """
    To manage vehicle fuel log
    """
    _inherit = 'fleet.vehicle.log.fuel'

    _name = 'fleet.vehicle.log.fuel'

    def copy_car(self, cr, uid, ids, context=None):
        """
        @return: to create another car fuel request.

        """
        fuel_request_obj = self.pool.get('fleet.vehicle.log.fuel')
	no_of_cars = 0.0
        for record in self.browse(cr, uid, ids):
		new_record_id = self.copy(cr,uid,record.id,{'copy_request':True},context)
		no_of_cars = record.number_copy+1
        return self.write(cr, uid, ids, {'number_copy':no_of_cars}, context=context)

    _columns = {
        'plan_type': fields.selection((('fixed_fuel','Fixed Fuel'),('extra_fuel','Extra Fuel')), "Plan Type",required = True),
        'purpose': fields.selection((('mission','Mission'),('emergency','Emergency')), "Purpose"),
        'payment_method': fields.selection((('plan','Plan'),('enrich','Enrich')), "Payment Method", required=True),#new
        'enrich_id': fields.many2one('payment.enrich', 'Payment Enrich'),#new
        'start_date' : fields.date('Travel Date',),
        'end_date' : fields.date('Return Date',),
	'mission_id': fields.many2one('hr.mission.category','Destination'),
        'copy_request': fields.boolean('Copy Request', readonly=True),
        'number_copy': fields.float('Number of additional Vehicles',readonly=True),
        'department_id': fields.many2one('hr.department','Department'),
        'product_id': fields.many2one('product.product','Product',),
        'product_uom': fields.many2one('product.uom','Unit of price',),
        'qty_line_id':fields.many2one('fuel.qty.line','Fuel Plan',readonly=True),
        'state': fields.selection([('draft', 'Draft'),('requested', 'Requested'),('approved', 'Approved'),
                                ('confirmed', 'Confirmed'),('done','Done')],readonly=True, select=True),
        'employee_ids': fields.many2many(
                                'hr.employee',
                                'name',
                                string="Employees"),
        'liter': fields.float('Quantity'),
    }

    _defaults={
        'payment_method':'plan',
	'number_copy':0.0,
        'state': 'draft',
    }

    def check_it(self, cr, uid, ids, context=None):
        """
        Check fuel type and change state.
        """
        for record in self.browse(cr, uid, ids):
            if record.plan_type =='fixed_fuel':
                self.write(cr, uid, ids, {'state':'done'}, context=context)
            if record.plan_type =='extra_fuel':
                self.write(cr, uid, ids, {'state':'requested'}, context=context)

    def _check_odometer(self, cr, uid, ids, context=None):
        """
        Check the value of cost and rise warning message.

        @return: Boolean True
        """
        for log in self.browse(cr, uid, ids, context=context):
            if log.odometer < 0 :
            	raise osv.except_osv(_('ValidateError'), _("Odometer Value Must Be Greater Than Or Equal Zero!"))
        return True

    def _check_spent(self, cr, uid, ids, context=None):
        """
        Check and compare the value of spent amount with the amount spent in line.

        @return: Boolean True
        """
        fuel_line= self.pool.get('fuel.qty.line')
        fuel_line_browser=fuel_line.browse(cr,uid,ids,context={})
        uom_obj = self.pool.get('product.uom')
        flag=0
        for log in self.browse(cr, uid, ids, context=context):
            date  = datetime.strptime(log.date , "%Y-%m-%d")
            split_date = log.date.split('-')
            year_log = str(date.year)
            #spt = split_date[1].split('0')
            mo_log = str(date.month)
            qty_log = log.liter
            if log.plan_type=='fixed_fuel':
                veh_ids = fuel_line.search(cr, uid, [('qty_id.plan_type','=',log.plan_type),('month','=',mo_log),('year','=',year_log),('vehicles_id','=',log.vehicle_id.id)])
            elif log.plan_type=='extra_fuel':
                veh_ids = fuel_line.search(cr, uid, ['|',('department_id','=',log.department_id.id),('department_id','=',False),('qty_id.plan_type','=',log.plan_type),('month','=',mo_log),('year','=',year_log),('product_id','=',log.vehicle_id.product_id.id)],order='department_id')
            if veh_ids==[]:
                raise osv.except_osv(_('ValidateError'), _("Date, Department Or Vehicle Doesn't Match Fuel Line!"))
            else:
                for spent in fuel_line.browse(cr, uid, veh_ids, context=context):
                    un_convert_unit = log.product_uom.id
                    convert_unit = spent.product_uom.id
                    convert = uom_obj._compute_qty(cr, uid, un_convert_unit, qty_log, convert_unit)
                    remaining_quantity= spent.product_qty - spent.spent_qty
                    remain_quantity=uom_obj._compute_qty(cr, uid, un_convert_unit, remaining_quantity, convert_unit)
                    if remain_quantity >= convert:
                        log.write({'qty_line_id':spent.id})
                        flag=2
                        break
                if flag==0:
                    raise osv.except_osv(_("ValidateError"),_('Fuel Quantity Is Not Enough!'))
        return True

    _constraints = [
        (_check_odometer, '', ['']),
    ]

    def on_change_vehicle(self, cr, uid, ids, vehicle_id, context=None):
        """
        On change vehicle id field value function gets the value and domain of another fields.

        @param vehicle_id: id of current vehicle
        @return: Dictionary of unit, department_id and product_uom values with product_uom domain
        """
        if not vehicle_id:
            return {
                'value': {
                    'unit':False,
                    #'department_id': False,
                    'product_id': False,
		    'product_uom':False,
				    'price_per_liter':0.00, },
                'domain': {
                    'product_id': []
                    }
				}
        vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context=context)
        return {
            'value': {
                'unit':  vehicle.odometer_unit,
                'department_id': vehicle.department_id.id,
                'product_id': vehicle.product_id and vehicle.product_id.id or False,
                'product_uom': vehicle.product_id and vehicle.product_id.uom_id.id or False,  
				'price_per_liter':vehicle.product_id.standard_price, },
        }

    def onchange_enrich(self, cr, uid, ids,date, department_id):
        if not ids:
            return{}
        split_date = date.split('-')
        year_log = split_date[0]
        spt = split_date[1].split('0')
        mo_log = spt[1][0]
        return {
            'domain': {
                'enrich_id': [
                    ('month','=',mo_log),
                    ('year','=',year_log),
                    ('state','=','confirm_gm'),
                    '|',
                    ('department_id','=',False ),
                    ('department_id','=', department_id or False),
                    
                ],
            },
        }

    def on_change_plan_type(self, cr, uid, ids,context=None):
        return {
            'value': {
                'enrich_id': False,
                'payment_method': 'plan',
            },
        }

    def on_change_price(self, cr, uid, ids, product_uom, vehicle_id,context=None):
        vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context=context)
        uom_obj = self.pool.get('product.uom')
        if not vehicle_id:
            return {'value': {
                'price_per_liter':  0.00,}
            }
        else:
            price = uom_obj._compute_price(cr, uid, vehicle.product_uom.id, vehicle.product_id.standard_price, product_uom)    
            return {'value': {
                'price_per_liter':  price,}
                }

    def draft(self, cr, uid, ids, context=None):
        """
        @return: Set state of fuel log to draft.
        """
        return self.write(cr, uid, ids, {'state':'draft'},context=context)

    def requested(self, cr, uid, ids, context=None):
        """
        @return: Change state of fuel log to confirmed.
        """
        for record in self.browse(cr, uid, ids):
            if record.payment_method =='plan':
		if record.plan_type == 'fixed_fuel':
                	self._check_spent(cr, uid,ids)
            if record.payment_method =='enrich' and record.amount > 0 and record.enrich_id.residual_amount < record.amount:
                raise osv.except_osv(_("ValidateError"),_('No Enough Money In The Enrich!'))

        return self.write(cr, uid, ids, {'state':'requested'}, context=context)

    def approved(self, cr, uid, ids, context=None):
        """
        @return: Change state of fuel log to approved.
        """
        return self.write(cr, uid, ids, {'state':'approved'}, context=context)

    def confirmed(self, cr, uid, ids, context=None):
        """
        @return: Change state of fuel log to confirmed.
        """
        return self.write(cr, uid, ids, {'state':'confirmed'}, context=context)

    def done(self, cr, uid, ids, context=None):
        """
        @return: Change state of fuel log to done and make the enrich line.
        """
        contract = self.browse(cr, uid, ids[0],context=context)
        if contract.payment_method =='enrich' and contract.amount > 0:
            details = 'Enrich Line :'+contract.purpose and contract.purpose or ""
            details += ' for the Vehicle :'+ (contract.vehicle_id and contract.vehicle_id.model_id.modelname+" "+contract.vehicle_id.model_id.brand_id.name) or ""
            self.pool.get('payment.enrich.lines').create(cr, uid, 
                                                    {'enrich_id':contract.enrich_id.id,
                                                    'date':contract.date,
                                                    'cost':contract.amount,
                                                    'name':details,
                                                    'model_id':'fleet.vehicle.log.fuel',
                                                    'department_id':contract.department_id.id},
                                                    context=context)
        return self.write(cr, uid, ids, {'state':'done'}, context=context)
