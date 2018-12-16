# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2015-2016 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from osv import fields, osv
from tools.translate import _
import decimal_precision as dp

# fuel monthly plan wizard
class fuel_monthly_plan_wizard(osv.osv_memory):
    """ To manage fuel monthly plan """
    _name = "fuel.monthly.plan.wizard"

    _description = "Fuel Monthly Plan"

    _columns = {
        'date': fields.date('Plan Date', required=True,), 
        'month': fields.selection([(str(n),str(n)) for n in range(1,13)],'Month', required=True),
        'year': fields.char('Year',size=32, required=True),
        'type_plan':fields.selection([('constant_fuel','Constant Fuel'),('mission_extra','Mission Extra')], 'Plan Type',required=True),
        'type':fields.selection([('departments','Departments'),('general_departments','General Departments')], 'Department Type'),
        'dept_cat_id':fields.many2one('hr.department.cat', 'Department Category',),
        'company_id':fields.many2one('res.company', 'Company',required=True),
        'extra_fuel_lines': fields.one2many('extra.fuel.lines','monthly_plan_id','Extra Fuel'),
    }

    _defaults = {
        'year': str(time.strftime('%Y')),
        'date': time.strftime('%Y-%m-%d'),
        'type_plan':'constant_fuel',
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'fuel.monthly.plan.wizard', context=c),                    
    }

# Calculate fixed fuel
    def fix_plan_compute(self, cr, uid, plan_id, vehicle_obj, dept_id=False,context=None):
        """
        Compute fixed fuel.

        @param dept_id: department_id
        @param vehicle_obj: vehicleobject according to specific department
        """
        total_qty = {}
        fuel_qty_obj= self.pool.get('fuel.quantity')
        conv_lst = []
        conv_qty_lst = []
        for vehicle in vehicle_obj:
                conv_lst = self.convert_vehicle_unit(cr, uid,vehicle, context=context)
                conv_qty_lst.append(conv_lst[0])
                qty_line_dict = {
                    'vehicles_id': vehicle.id,
                    'department_id': vehicle.department_id.id,
                    'product_id': vehicle.product_id.id,
                    'product_qty': conv_lst[0],
                    'product_uom': conv_lst[1],
                    'price_unit': vehicle.product_id.standard_price,
                    'name': vehicle.name,
                } 
                fuel_type = total_qty.get(vehicle.fuel_type,{})
                line = fuel_type.get('line') or []
                line.append((0,0,qty_line_dict))
                fuel_type_dict = {'qty':fuel_type.get('qty',0)+vehicle.product_qty,
                                  'line':line}
                total_qty.update({vehicle.fuel_type: fuel_type_dict})
        index = 0
        for k,v in total_qty.items():
            fuel_qty_obj.create(cr,uid,{
                        'plan_id': plan_id,
                        'plan_type': 'fixed_fuel',
                        'department_id': dept_id,  
                        'fuel_type':k,
                        'fuel_qty':conv_qty_lst[index],
                        'qty_lines':v['line'],
                    },context=context)
            index = index + 1

    def convert_unit(self, cr, uid,line, context=None):
        """
        To convert fuel unit of measure.

        @return: list of reference unit and converted quantity
        """
        uom_obj = self.pool.get('product.uom')
        uom_id = uom_obj.search(cr,uid,[('category_id','=',line.product_id.uom_id.category_id.id),('uom_type','=','reference')],context=context)
        
        if not uom_id :
            raise osv.except_osv(_('ValidateError'), _('The Product You Entered Has No Reference Unit Of Mesure(UOM)!'))
        converted_quantity = uom_obj._compute_qty(cr, uid, line.product_id.uom_id.id, line.product_qty, uom_id[0])
        return [converted_quantity, uom_id[0]]

    def convert_vehicle_unit(self, cr, uid,vehicle, context=None):
        """
        To convert vehicle fuel unit of measure.

        @return: list of reference unit and converted quantity
        """
        uom_obj = self.pool.get('product.uom')
        uom_id = uom_obj.search(cr,uid,[('category_id','=',vehicle.product_id.uom_id.category_id.id),('uom_type','=','reference')],context=context)
        
        if not uom_id :
            raise osv.except_osv(_('ValidateError'), _('The Product You Entered Has No Reference Unit Of Mesure(UOM)!')) 
        converted_quantity = uom_obj._compute_qty(cr, uid, vehicle.product_uom.id, vehicle.product_qty, uom_id[0])
        return [converted_quantity, uom_id[0]]

# Create the fuel plan
    def create_plan(self,cr, uid, record, dept_plan, context=None):
        """
        To create fuel plan

        @return: plan_id
        """
        fuel_plan_obj= self.pool.get('fuel.plan')
        fuel_plan_dict = {
            'date':record.date,
            'month':record.month,
            'year':record.year,
            'company_id':record.company_id.id,
            'department_id':dept_plan,
            'type_plan':record.type_plan,
        }
        return fuel_plan_obj.create(cr,uid,fuel_plan_dict,context=context)

    def compute_plan(self, cr, uid, ids, context=None):
        """
        To compute fuel plan 

        @return: empty dictionary
        """
        fuel_plan_obj= self.pool.get('fuel.plan')
        fuel_qty_obj= self.pool.get('fuel.quantity')
        vehicle_pool= self.pool.get('fleet.vehicle')
        department_obj = self.pool.get('hr.department')
        conv_lst = []
        flag = False
        for record in self.browse(cr,uid,ids,context=context):
            check_plan = fuel_plan_obj.search(cr,uid,[('month','=',record.month),('year','=',record.year),('company_id','=',record.company_id.id),('type_plan','=','constant_fuel')],context=context)
            if check_plan and record.type_plan!='mission_extra':
                raise osv.except_osv(_('ValidateError'), _('Fuel Plan For This Month Is Already Computed!'))
            if record.type_plan=='mission_extra':
                if not record.extra_fuel_lines:
                    raise osv.except_osv(_('ValidateError'), _('You Must Enter Extra Fuel!'))
            for line in record.extra_fuel_lines:
                plan = fuel_plan_obj.search(cr, uid, [('department_id','=',line.department_id.id),('month','=',record.month),('year','=',record.year),('type_plan','=',record.type_plan)])
                if line.product_qty <= 0:
                    raise osv.except_osv(_('ValidateError'), _('The Extra Fuel Quantity Must Be Greater Than Zero!'))
                conv_lst = self.convert_unit(cr, uid,line, context=context)
               
                if plan:
                    department_dict={
                        'plan_id': plan[0],
                        'plan_type': 'extra_fuel',
                        'fuel_type':line.product_id.fuel_type,
                        'fuel_qty':conv_lst[0],
                        'department_id':line.department_id.id,
                        'qty_lines': [(0,0,{
                            'product_id': line.product_id.id,
                            'product_qty': conv_lst[0],
                            'product_uom': conv_lst[1],
                            'price_unit': line.product_id.standard_price,
                            'name': u' وقود اضافي' + line.product_id.name,
                            'department_id': line.department_id.id,})]
                    }
                    fuel_qty_obj.create(cr,uid,department_dict,context=context)
                else:
                    plan_extra = self.create_plan(cr,uid,record,line.department_id.id,context)
                    department_dict={
                        'plan_id': plan_extra,
                        'plan_type': 'extra_fuel',
                        'fuel_type':line.product_id.fuel_type,
                        'fuel_qty':conv_lst[0],
                        'department_id':line.department_id.id,
                        'qty_lines': [(0,0,{
                            'product_id': line.product_id.id,
                            'product_qty': conv_lst[0],
                            'product_uom': conv_lst[1],
                            'price_unit': line.product_id.standard_price,
                            'name': u' وقود اضافي' + line.product_id.name,
                            'department_id': line.department_id.id,})]
                    }
                    fuel_qty_obj.create(cr,uid,department_dict,context=context)
            if record.type=='general_departments':
                department_id= department_obj.search(cr,uid,[('cat_id','=',record.dept_cat_id.id),('company_id','=',record.company_id.id)],context=context)
                department_ids= department_obj.search(cr,uid,[('id','child_of',department_id)],context=context)
            elif  record.type=='departments':
                department_ids= department_obj.search(cr,uid,[('company_id','=',record.company_id.id)],context=context)
            if record.type_plan=='constant_fuel':
                for dept in department_obj.browse(cr,uid,department_ids,context=context):
                    vehicle_ids= vehicle_pool.search(cr,uid,[('department_id','=',dept.id),('status','=','active'),('monthly_plan','=',True),('ownership','!=','rented'),],context=context)        
                    if vehicle_ids:
                        flag = True        
                        vehicle_obj = vehicle_pool.browse(cr,uid,vehicle_ids,context=context)
                        for plan_browse in vehicle_obj:
                            plan = fuel_plan_obj.search(cr, uid, [('department_id','=',plan_browse.department_id.id),('month','=',record.month),('year','=',record.year),('type_plan','=',record.type_plan)])
                            if plan :
                                self.fix_plan_compute(cr, uid, plan[0],[plan_browse], plan_browse.department_id.id, context=context)
                            else:
                                plan_fixed = self.create_plan(cr,uid,record,plan_browse.department_id.id,context)
                                self.fix_plan_compute(cr, uid, plan_fixed,[plan_browse], plan_browse.department_id.id, context=context)
                        
                if record.type !='general_departments':
                    vehicle_ids= vehicle_pool.search(cr,uid,[('department_id','=',False),('status','=','active'),('monthly_plan','=',True),('ownership','!=','rented')],context=context)        
                    if vehicle_ids:
                        flag = True
                        vehicle_obj = vehicle_pool.browse(cr,uid,vehicle_ids,context=context)
                        for veh in vehicle_obj:
                            plan = fuel_plan_obj.search(cr, uid, [('department_id','=',False),('month','=',record.month),('year','=',record.year),('type_plan','=',record.type_plan)])
                            if plan:
                                self.fix_plan_compute(cr, uid, plan[0], [veh],context=context)
                            else :
                                plan_false = self.create_plan(cr,uid,record,False,context)
                                self.fix_plan_compute(cr, uid, plan_false,[veh], context=context)
                if (flag==False) and not record.extra_fuel_lines:
                    raise osv.except_osv(_('Warning!'), _('Please Enter Fixed Or Extra Plan To Complete Compute Operation'))
        return {}

    def onchange_dept_cat_id(self,cr,uid,ids,dept_cat_id):
        return {'value':{'dept_cat_id': False}}


class extra_fuel_lines(osv.osv_memory):
    """ To manage extra fuel lines  """
    _name = "extra.fuel.lines"

    _columns = {
        'product_id': fields.many2one('product.product', 'Fuel', required=True),
        'product_qty': fields.float('Quantity', required=True, digits_compute=dp.get_precision('Product UoM')),
        'department_id': fields.many2one('hr.department', 'Fuel Department'),
        'monthly_plan_id':fields.many2one('fuel.monthly.plan.wizard', 'Plan',),
        
    }


class hr_department(osv.Model):

    _inherit = "hr.department"

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        cat_id=context.get('cat_ids', [])
        if cat_id:
            args.append(('cat_id','=',cat_id))
        return super(hr_department, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)

