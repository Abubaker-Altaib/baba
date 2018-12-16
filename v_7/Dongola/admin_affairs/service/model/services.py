# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv,fields
from datetime import date,datetime,timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
import math
from openerp import tools
from admin_affairs.model.copy_attachments import copy_attachments as copy_attachments
from admin_affairs.model.copy_attachments import copy_attachments_set
from admin_affairs.model.email_serivce import send_mail
import inspect

class fleet_vehicle_cost(osv.Model):
    """
    Manage cost amounts of vehicle.
    """
    _inherit = 'fleet.vehicle.cost'

    def _cost_name_get_fnc_custom(self, cr, uid, ids, name, unknow_none, context=None):
        """
        Set cost name.

        @param name: variable to store cost name
        @param unknow_none: extra name
        @return: Dictionary of cost name
        """
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            name = record.vehicle_id.name
            if record.cost_subtype_id.name and record.vehicle_id.name:
                name += ' / '+ record.cost_subtype_id.name
            if record.date and record.vehicle_id.name:
                name += ' / '+ record.date
            if record.date and record.cost_subtype_id.name:
                name = record.date +' / '+ record.cost_subtype_id.name
            res[record.id] = name
        return res

    def _tax_amount_fnc(self, cr, uid, ids, field_name, arg, context=None):
        """
        Compute tax amount.

        @param field_name: list contains name of fields that call this method
        @param arg: extra arguments
        @return: Dictionary of tax total amount
        """
        res = {}
        totalsum = 0
        taxess = self.pool.get('account.tax')
        for cost in self.browse(cr, uid, ids, context=context):
            totalsum = 0
            if cost.contract_id.tax_ids:
                for tax in taxess.compute_all(cr, uid, cost.contract_id.tax_ids, cost.amount,1)['taxes']:
                    unit_tax= tax.get('amount', 0.0)
                    totalsum += unit_tax
                res[cost.id] = totalsum
        return res

    def _total_fnc(self, cr, uid, ids, field_name, arg, context=None):
        """
        Compute total cost amount.

        @param field_name: list contains name of fields that call this method
        @param arg: extra arguments
        @return: Dictionary of cost total amount
        """
        res = {}
        totalsum = 0
        taxess = self.pool.get('account.tax')
        for cost in self.browse(cr, uid, ids, context=context):
            totalsum = cost.amount * cost.quantity
            if cost.quantity <= 0:
                totalsum = cost.amount
            res[cost.id] = totalsum
            if cost.contract_id.tax_ids:
                for tax in taxess.compute_all(cr, uid, cost.contract_id.tax_ids, totalsum,1)['taxes']:
                    unit_tax= tax.get('amount', 0.0)
                    totalsum += unit_tax
                res[cost.id] = totalsum
        return res

    _columns = {
        'name': fields.function(_cost_name_get_fnc_custom, type="char", string='Name', store=True),
        'tax_amount': fields.function(_tax_amount_fnc, type="float", string='Tax Amount'),
        'total': fields.function(_total_fnc, type="float", string='Total'),
        'cost_ids': fields.one2many('fleet.vehicle.cost', 'parent_id', 'Included Services'),
        'parent_prod': fields.many2one('fleet.vehicle.cost', 'Parent', help='Parent cost to this current cost'),
        'cost_product': fields.one2many('fleet.vehicle.cost', 'parent_prod',),
        'quantity':fields.float('Quantity'),
        'voucher_id': fields.many2one('account.voucher','Voucher',help='Voucher That Cost Pay With'),
        'vehicle_id': fields.many2one('fleet.vehicle', 'Vehicle', required=False, help='Vehicle Concerned By This Log'),
        'product_id':fields.many2one('product.product', 'Product'),
        'date_to': fields.date(string='To Date'),
       	'form_date': fields.date(string='From Date'),
       	'progress':fields.float('Progress'),
        'vehicle_cost':fields.related('vehicle_id','car_value',type='float',string='Vehicle Cost'),
        'activation':fields.boolean('Activation'),
        'notes':fields.char('Notes'),
        'insurer_id' :fields.many2one('res.partner', 'Partner'),
        'fault_id': fields.many2one('building.maintenance.faults.solution', 'Fault'),
        'solution_ids': fields.many2many('building.maintenance.faults.solution', 'costs_solutions', string='Solutions',
                                            ondelete='cascade'),
        'responsible':fields.related('fault_id','responsible', type="many2many", relation='hr.employee', string='Responsible'),
        'time': fields.integer(string='Time'),
        'note': fields.char(string='Note'),
        'contract_type': fields.related('contract_id', 'contract_type', type='selection', selection=[('contract', 'Contract'),
        ('service', 'Service'), ('fault', 'Fault')], string='Contract Type'),
        'state': fields.selection([('draft', 'Draft'),
         ('confirm', 'Confirm'), \
         ('smanager', 'Section Manager'), \
         ('dmanager', 'Depatment Manager'), \
         ('gdmanager', 'General Depatment Manager'), \
         ('gmanager', 'General Manager'),
         ], 'Status', translate=True),
        'start_time': fields.datetime(string='start_time'),
        'end_time': fields.datetime(string='end_time'),
        'expected_time': fields.float(string='Expected Time'),
        'price': fields.float(string='Price'),
        'v_state':fields.related('voucher_id','state', type="char", string='state'),

    }
    _defaults={
    'activation':True,
    'progress':100,
    'state':'draft',
    }

    def confirm(self, cr, uid, ids, context=None):
        """
        Button method changes the state to 'confirm'.
        @return: write state
        """
        
        return self.write(cr, uid, ids, {'state':'confirm'}, context=context)
    

    def smanager(self, cr, uid, ids, context=None):
        """
        Button method changes the state to 'smanager'.
        @return: write state
        """
        
        return self.write(cr, uid, ids, {'state':'smanager'}, context=context)

    
    def dmanager(self, cr, uid, ids, context=None):
        """
        Button method changes the state to 'dmanager'.
        @return: write state
        """
        
        return self.write(cr, uid, ids, {'state':'dmanager'}, context=context)
    

    def gdmanager(self, cr, uid, ids, context=None):
        """
        Button method changes the state to 'gdmanager'.
        @return: write state
        """
        
        return self.write(cr, uid, ids, {'state':'gdmanager'}, context=context)
    
    def gmanager(self, cr, uid, ids, context=None):
        """
        Button method changes the state to 'gmanager'.
        @return: write state
        """

        return self.write(cr, uid, ids, {'state':'gmanager'}, context=context)
    
    def create_payment(self, cr, uid, ids, context=None):
        """
        Button method create payment of the cost.
        """
        if 'voucher_id' in context and context['voucher_id']:
            raise osv.except_osv(_('Error'), _("The Payment is already Created!!"))    
        contract_id = self.read(cr, uid, ids, ['contract_id'], context=context)[0]['contract_id'][0]
        self.pool.get('fleet.vehicle.log.contract').transfer(cr=cr, uid=uid, ids=[contract_id], context=context, costIds = ids)

    def on_change_progress(self, cr, uid, ids, progress,amount, context=None):
    	"""
    	On change service field value function gets the cost  of payment.
    	@return: Cost of Payment
    	"""
        progress = progress/100.0
        if progress != 1:
            amount = amount - (amount * progress)
    	return {
    	'value': {
                'amount': amount,}
                }
            
        
   

    def onchange_service(self, cr, uid, ids, cost_subtype_id, context=None):
    	"""
    	On change service field value function gets the cost  of service.
    	@return: Cost of service
    	"""
    	service_type_obj=self.pool.get('fleet.service.type').browse(cr, uid, cost_subtype_id, context=context)
    	cost=service_type_obj.cost
        qty=service_type_obj.quantity
    	return {
    	'value': {
                'amount': cost,
                'quantity':qty,}
                }
    def onchange_value(self, cr, uid, ids, amount,quantity, context=None):
        """
        On change amount field value function check it is positive or not.
        @return: Cost of service
        """
        if (amount<0):
            raise osv.except_osv(_(''), _("The Value Of Indecative Cost Must Be Positive"))            
        if quantity <= 0:quantity = 1
        
        self.write(cr,uid,ids,{ 'total': amount * quantity, },context=context)
        return {
    	'value': 
                {
                'total': amount * quantity,
                }
            }
        return True
    
    def onchange_time(self, cr, uid, ids, start_time, end_time, context=None):
        """
        On change dates fields this method will change the time field accordenly.
        @return: time value
        """

        if start_time and end_time:
            if start_time <= end_time:
                
                start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                
                hours = (end_time - start_time).seconds/3600.0

                return {
                'value': 
                        {
                        'time': hours,
                        }
                }
        return {
                'value': 
                        {
                        'time': 0,
                        }
        }
    
    def onchange_product(self, cr, uid, ids, product_id, context=None):
    	"""
    	On change product field value function gets the cost  of product_id.
    	@return: Cost of product
    	"""
    	product_obj=self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        cost = product_obj.standard_price
    	return { 'value': {'amount': cost, 'quantity':1} }
    	
    def onchange_vehicle_id(self, cr, uid,ids, vehicle_id, context=None):
        vehicle_obj=self.pool.get('fleet.vehicle')

        vehicle = vehicle_obj.browse(cr, uid, vehicle_id, context=context)
        return {
            'value': {
                'vehicle_cost':vehicle.car_value,
                'amount': vehicle.type.license_cost,}
                    }
    def _set_vehicle_id (self, cr, uid, id, context=None):
        """
        On change vehicle id field value function gets the value and domain of another fields.

        @return: Super method _set_vehicle_id
        """

        veh_id = self.browse(cr, uid, id, context=context)
        res = super(fleet_vehicle_cost, self)._set_vehicle_id( cr, uid, id)
        for r in res:
            r.update({'vehicle_id':veh_id.vehicle_id.id})
        return res

    def create(self, cr, uid, data, context=None):
        """
        Check entered data.

        @param data: extra data
        @return: super method create
        """
        
        #make sure that the data are consistent with values of parent and contract records given
        vehicle_id = False
        if 'contract_type' in data:
            if data['contract_type'] == 'service':
                data['state'] = 'gmanager'
        if 'vehicle_id' in data:
            vehicle_id = data['vehicle_id']
        if 'parent_id' in data and data['parent_id']:
            parent = self.browse(cr, uid, data['parent_id'], context=context)
            if parent.vehicle_id.id :
                data['vehicle_id'] = parent.vehicle_id.id
            data['date'] = parent.date
            data['cost_type'] = parent.cost_type
            if 'insurer_id' not in data:
               data['insurer_id'] = parent.insurer_id.id
        if 'contract_id' in data and data['contract_id']:
            contract = self.pool.get('fleet.vehicle.log.contract').browse(cr, uid, data['contract_id'], context=context)
            if contract.vehicle_id.id:
                data['vehicle_id'] = contract.vehicle_id.id
            data['cost_subtype_id'] = contract.cost_subtype_id.id
            data['cost_type'] = contract.cost_type
        if 'odometer' in data and not data['odometer']:
            #if received value for odometer is 0, then remove it from the data as it would result to the creation of a
            #odometer log with 0, which is to be avoided
            del(data['odometer'])

        id = super(fleet_vehicle_cost, self).create(cr, uid, data, context=context)
        
        
        #case for insurance contracts to set the vehicle to it's original
        if vehicle_id:
            self.write(cr, uid, id, {'vehicle_id':vehicle_id}, context=context)
        return id
    


class services(osv.osv):
    """
    Manage admin affairs services.
    """
    _inherit='fleet.vehicle.log.contract'

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if not context:
            context = {}
        res = super(services, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if 'contract_type' in res['fields']:
            view_name = self.pool.get("ir.ui.view").read(cr,uid,res['view_id'],['name'],context=context)
            if str(view_name['name']) == 'contract.building.form':
                if 'contract_type' in res['fields']:
                    List = ['fault']
                    user_obj = self.pool.get('res.users')
                    flag = user_obj.has_group(cr, uid, 'service.group_building_maintenace') and \
                    user_obj.has_group(cr, uid, 'service.group_building_service_officer')
                    if not flag:    
                        new_list = [item for item in res['fields']['contract_type']['selection'] if item[0] == 'fault' ]
                        res['fields']['contract_type']['selection'] = new_list

        return res

    def write(self, cr, uid, ids, vals, context=None):
        if 'cat_subtype' in vals:
            del vals['cat_subtype']

        factor = 0.5
        if 'out_hall' in vals and vals['out_hall']:
            factor = 1.0
        if 'start_time' in vals:
            if vals['start_time'] < 1.0:
                raise osv.except_osv(_('Error'), _('start time must be greater than or equal to one'))
            vals['start_time']=(vals['start_time']-factor)%24.0
        if 'end_time' in vals:
            if vals['end_time'] > 23.0:
                raise osv.except_osv(_('Error'), _('start time must be less than or equal to 23'))
            vals['end_time']=(vals['end_time']+factor)%24.0

        super(services,self).write(cr, uid, ids, vals, context)
        ids = ( type(ids) is list ) and ids or [ids]
        for contract in self.browse(cr,uid,ids,context=context):
            if contract.cost_subtype_id.category == 'hall':
                if (contract.start_time + factor )== (contract.end_time - factor):
                        raise osv.except_osv(_(''), _("Contract Start Time Must Be Less Than End Time!"))
                if 'cost_subtype_id' in vals:
                    if contract.state in ['w_ss', 'w_so', 'w_haa', 'w_gm', 'w_admin']:
                        if not self.pool.get('res.users').has_group(cr, uid, 'admin_affairs.group_admin_affair_manager'):
                            raise osv.except_osv(_("Error"),_('You have to be admin affairs manager'))
                    if contract.hall_registrations:
                        hall_ids = [x.write({'hall_id':vals['cost_subtype_id']}) for x in contract.hall_registrations]
                        
                if 'hall_registrations' in vals:
                    if contract.state in ['w_ss', 'w_so', 'w_haa', 'w_gm', 'w_admin']:
                        if not self.pool.get('res.users').has_group(cr, uid, 'admin_affairs.group_admin_affair_manager'):
                            raise osv.except_osv(_("Error"),_('You have to be admin affairs manager'))


                #contract.count_availability()
            if contract.cost_subtype_id.category == 'building':
                if contract.contract_type == "fault" and contract.faults_ids:
                    faults_ids = [x.id for x in contract.faults_ids]
                    super(services,self).write(cr, uid, contract.id, {'cost_ids':[[6, 0, faults_ids]]}, context)
                elif contract.contract_type == "contract" and contract.tasks_ids:
                    tasks_ids = [x.id for x in contract.tasks_ids]
                    super(services,self).write(cr, uid, contract.id, {'cost_ids':[[6, 0, tasks_ids]]}, context)
        return True
    
    def create(self, cr, uid, data, context=None):
        if 'cat_subtype' in data and data['cat_subtype'] == 'hall':
            factor = 0.5
            
            if 'start_time' in data and data['start_time'] < 1.0:
                raise osv.except_osv(_('Error'), _('start time must be greater than or equal to one'))
            if 'end_time' in data and data['end_time'] > 23.0:
                raise osv.except_osv(_('Error'), _('start time must be less than or equal to 23'))
            if 'start_time' in data and data['start_time']:
                if 'end_time' in data and data['end_time']:
                    if data['start_time'] == data['end_time']:
                        raise osv.except_osv(_(''), _("Contract Start Time Must Be Less Than End Time!"))
            
             
            data['start_time']= (data['start_time'] - factor)%24.0
            data['end_time']  = (data['end_time'] +factor)%24.0

        contract_id = super(services,self).create(cr, uid, data, context)
        contract = self.browse(cr,uid,contract_id,context=context)

        #for cost_id in contract.cost_ids:cost_id.write({'contract_id':contract.id})
        #if contract.cost_subtype_id.category == 'hall':
        #contract.count_availability()
            
        if contract.cost_subtype_id.category == 'building':
            if contract.contract_type == "fault" and contract.faults_ids:
                faults_ids = [x.id for x in contract.faults_ids]
                contract.write({'cost_ids':[[6, 0, faults_ids]]}, context=context)
            elif contract.contract_type == "contract" and contract.tasks_ids:
                tasks_ids = [x.id for x in contract.tasks_ids]
                contract.write({'cost_ids':[[6, 0, tasks_ids]]}, context=context)
        return contract_id

    def unlink(self, cr, uid, ids, context=None):
        holl_availability =self.pool.get("service.hall_availability")
        for contract in self.browse(cr,uid,ids,context=context):
            if contract.state not in ['draft', 'cancel']:
                raise osv.except_osv(_('Error'), _('the contract have to be in draft or cancel state to be deleted!'))
            for cost in contract.generated_cost_ids:
                cost.unlink()
            deleted_ids = holl_availability.search(cr,uid,[('contract_id','=',contract.id)],context=context)
            holl_availability.unlink(cr,uid,deleted_ids,context=context)
        
        super(services, self).unlink(cr, uid,ids, context=context)    




    def onchange_value(self, cr, uid, ids, context=None):
        if ids:
            contract = self.browse(cr,uid,ids[0],context=context)
            total = 0
            for service in contract.cost_ids:
                total += service.total
            
            if contract.cat_subtype == 'hall':
                if contract.internal:
                    total = 0
                total = total * int(contract.end_time - contract.start_time) 
                
            return {
            'value': 
                    {
                    'sum_cost': total,
                    }
                }
        return True
    

    def onchange_contract_type(self, cr, uid, ids, cost_ids, faults_ids, contract_type=False, context=None):
        '''
        empty cost_ids, faults_ids
        '''
        cost_ids = [[2,x[1],False] for x in cost_ids ]
        faults_ids = [[2,x[1],False] for x in faults_ids ]
        if contract_type == 'service':
            return {
            'value': 
                    {
                    'cost_ids': cost_ids,
                    'faults_ids': faults_ids,
                    'state' : 'confirm',
                    }
                }

        return {
            'value': 
                    {
                    'cost_ids': cost_ids,
                    'faults_ids': faults_ids,
                    'state' : 'draft',
                    }
                }


    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({'generated_cost_ids':None, 'paid':0, 'residual':0, 'purchase_requisition': False})

        o = super(services, self).copy(cr, uid,id, default, context=context)
        copy_attachments(self,cr,uid,[id],'fleet.vehicle.log.contract',o,'fleet.vehicle.log.contract', context=context)
        self.write(cr, uid, o, {'state':'draft', }, context=context)
        cost_obj=self.pool.get('fleet.vehicle.cost')
        search_ids = cost_obj.search(cr, uid, [('contract_id','=',o)],context=context)
        cost_obj.unlink(cr, uid, search_ids,context=context)
        return o
    

    def _period_bookings(self, booking_frequency, first_booking_date, last_booking_date, start_time, end_time, skip):
        """
        return a list of all booking times of a hall
        """
        frequency={'daily':relativedelta(days=1),'weekly':relativedelta(weeks=1),'monthly':relativedelta(months=1),'yearly':relativedelta(years=1)}
        List = []
        interval = first_booking_date
        date_format = "%Y-%m-%d"
        interval  = datetime.strptime(interval , date_format)
        last_date = datetime.strptime(last_booking_date, date_format)
        factor = 0.5
        
        start_time = (start_time ) % 24.0 #+ factor
        end_time = (end_time ) % 24.0   #- factor




        start_hour,start_minute = self.get_time(start_time)
        end_hour,end_minute     = self.get_time(end_time)

        while interval <= last_date:
            start_datetime = datetime(interval.year,interval.month,interval.day,start_hour,start_minute)
            end_datetime   = datetime(interval.year,interval.month,interval.day,end_hour  ,end_minute)
            List.append((  start_datetime , end_datetime   ))
            if booking_frequency == 'no':
                break
            interval += frequency[booking_frequency]
            if skip:
                interval += frequency[booking_frequency]

        return List
    
    def update_hall_reg(self, cr, uid, ids, context=None):     
        weekdays = {0:'monday', 1:'tuesday', 2: 'wednesday', 3: 'thursday', 4: 'friday', 5: 'saturday', 6: 'sunday'}                        
        hall = context.get('hall',0)
        first_booking_date = context.get('first_booking_date','')
        last_booking_date = context.get('last_booking_date','')
        start_time = context.get('start_time')
        end_time = context.get('end_time')
        weekday = context.get('weekday')
        booking_frequency = context.get('booking_frequency')
        skip = context.get('skip')
        if hall == 0:
            raise osv.except_osv(_('Error'), _('No Hall Entered!'))
        
        contract = self.read(cr, uid, ids, ['start_time','end_time','name'], context=context)
        start_time = contract[0]['start_time']
        end_time = contract[0]['end_time']
        name = contract[0]['name']
        
        try:
            first_date = datetime.strptime(first_booking_date , "%Y-%m-%d  %H:%M:%S").date()
            last_date = datetime.strptime(last_booking_date , "%Y-%m-%d  %H:%M:%S").date()
        except:
            first_date = datetime.strptime(first_booking_date , "%Y-%m-%d")
            last_date = datetime.strptime(last_booking_date , "%Y-%m-%d")
        
        founded = False
        if weekday == first_date.weekday():
            founded = True
        if weekday != first_date.weekday():
            while first_date <= last_date:
                if weekday == first_date.weekday():
                    first_booking_date = datetime.strftime(first_date, "%Y-%m-%d" )
                    founded = True
                    break
                first_date += relativedelta(days=1)
        List = []
        if founded:
            List = self._period_bookings(booking_frequency, first_booking_date, last_booking_date, start_time, end_time, skip)
        
        data = [{'name': name, 'date_start':x[0], 'date_stop':x[1], 'contract_id':ids[0], 'hall_id':hall, 'weekday': weekdays[x[0].weekday()]} for x in List]

        holl_availability = self.pool.get('service.hall_availability')
        for line in data:
            holl_availability.create(cr, uid, line, context=context)

        
        




    def _vehicle_contract_name_get_fnc_custom(self, cr, uid, ids, name, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            contract_type = record.contract_type
            if contract_type:
                contract_type = contract_type[0:2]
            else:
                contract_type = "CO"
            sequence =contract_type + self.pool.get('ir.sequence').get(cr, uid, 'fleet.vehicle.log.contract')
            name =  sequence.upper()
            sub_type=record.cost_subtype_id.name or ""
            if sub_type:
                name += ' / '+ sub_type

            res[record.id] = name
        return res
    def _count_times(self,cr, uid, id, context=None):
        hall_availability = self.pool.get('service.hall_availability')
        search_ids = hall_availability.search(cr, uid, [('contract_id','=',id)], context=context)
        count = 0.0
        for record in hall_availability.browse(cr, uid, search_ids, context=context):
            date_start = datetime.strptime(record.date_start, "%Y-%m-%d %H:%M:%S")
            date_stop = datetime.strptime(record.date_stop, "%Y-%m-%d %H:%M:%S")
            delta = date_stop - date_start
            count += delta.seconds/3600.0
        return count

        
    def _get_sum_cost(self, cr, uid, ids, field_name, arg, context=None):
        """
        Calculate total cost.

        @return: Dictionary of total cost
        """
        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            sum_cost = sum([cost.total for cost in contract.cost_ids])
            if contract.contract_type == 'contract' and contract.cat_subtype not in ['contract','service','both','license','insurance','building','hall']:
                sum_cost = contract.contract_cost
            if contract.cat_subtype == 'hall':
                times = self._count_times(cr, uid, contract.id, context=context)
                if times > 0:
                    times-=1
                #temp_sum_cost = contract.cost_subtype_id.cost * times
                sum_cost = contract.cost_subtype_id.cost
                temp_sum_cost = sum_cost * times                
                sum_cost = temp_sum_cost

            paid = sum([cost.amount for cost in contract.generated_cost_ids])
            res[contract.id] = sum_cost
            if contract.cat_subtype in ['hall'] and not contract.rent:
                res[contract.id] = 0
                sum_cost = 0

            if contract.cat_subtype in ['hospitality'] and not contract.rent:
                res[contract.id] = 0
                sum_cost = 0
            if field_name=='paid':
                res[contract.id] = paid
            if field_name=='residual':
                res[contract.id] = round(sum_cost,2)-round(contract.amount,2)
                if paid != 0:
                    res[contract.id] = round(sum_cost,2) - round(paid,2)
        return res

    def emptyinstallment(self, cr, uid,ids, context=None):
        return {
            'value': {
                'installment':0,}
                    }
    def _cost_generated(self, cr, uid, ids, field_name, arg, context=None):
        """
        Calculate cost generated.

        @return: Dictionary of total cost
        """
        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            res[contract.id] = 0
            if contract.installment and contract.installment != 0:
                res[contract.id]= (contract.sum_cost-contract.amount)/contract.installment #- len(contract.generated_cost_ids))
            elif contract.cost_frequency != 'no':
                date_format = "%Y-%m-%d"
                start = datetime.strptime(contract.start_date, date_format)
                expiration = datetime.strptime(contract.expiration_date , date_format)
                delta = expiration - start
                days = delta.days + 1
                if contract.cost_frequency == 'daily':
                    res[contract.id] = contract.residual /days
                elif contract.cost_frequency == 'weekly':
                    res[contract.id] = contract.residual /(days/7.0)
                elif contract.cost_frequency == 'monthly':
                    res[contract.id] = contract.residual /(days/30.0)
                elif contract.cost_frequency == 'yearly':
                    res[contract.id] = contract.residual /(days/365.0)
                contract.write({'installment' : contract.residual/res[contract.id],})

        return res
    def _total_cost_fnc(self, cr, uid, ids, field_name, arg, context=None):
        """
        Method to compute the total cost amount from amount + frequency amount + sum_cost.

        @return: Dictionary of total cost amount
        """
        res = {}
        totalsum = 0
        for contract in self.browse(cr, uid, ids, context=context):
            totalsum = 0
            totalsum += contract.amount+contract.sum_cost
            res[contract.id] = totalsum

        return res
    
    #self, cr, uid, ids,context=None,passed=False
    #self, cr, uid, context=None
    #
    def scheduler_manage_auto_costs(self, cr, uid, context=None):
        #This method is called by a cron task
        #It creates costs for contracts having the "recurring cost" field setted, depending on their frequency
        #For example, if a contract has a reccuring cost of 200 with a weekly frequency, this method creates a cost of 200 on the first day of each week, from the date of the last recurring costs in the database to today
        #If the contract has not yet any recurring costs in the database, the method generates the recurring costs from the start_date to today
        #The created costs are associated to a contract thanks to the many2one field contract_id
        #If the contract has no start_date, no cost will be created, even if the contract has recurring costs
        vehicle_cost_obj = self.pool.get('fleet.vehicle.cost')
        d = datetime.strptime(fields.date.context_today(self, cr, uid, context=context), tools.DEFAULT_SERVER_DATE_FORMAT).date()
        d = datetime.combine(d, datetime.min.time())
        contract_ids = self.pool.get('fleet.vehicle.log.contract').search(cr, uid, [('state','=','open')], offset=0, limit=None, order=None,context=None, count=False)
        deltas = {'yearly': relativedelta(years=+1), 'monthly': relativedelta(months=+1), 'weekly': relativedelta(weeks=+1), 'daily': relativedelta(days=+1)}
        for contract in self.pool.get('fleet.vehicle.log.contract').browse(cr, uid, contract_ids, context=context):
            if contract.installment == 0:
                continue
            found = False
            last_cost_date = datetime.strptime(contract.start_date, "%Y-%m-%d")
            counted = 0
            if contract.generated_cost_ids:
                last_autogenerated_cost_id = vehicle_cost_obj.search(cr, uid, ['&', ('contract_id','=',contract.id), ('auto_generated','=',True), ('state','=','gmanager'),], offset=0, order='date desc',context=context, count=False)
                if last_autogenerated_cost_id:
                    counted = len(last_autogenerated_cost_id)
                    found = True
                    last_cost_date = vehicle_cost_obj.browse(cr, uid, last_autogenerated_cost_id[0], context=context).date
                    last_cost_date = datetime.strptime(last_cost_date, "%Y-%m-%d")

            left = contract.installment - counted
            if contract.amount > 0:
                left +=1
            start = datetime.strptime(contract.start_date, "%Y-%m-%d")
            expiration = datetime.strptime(contract.expiration_date , "%Y-%m-%d")
            delta = expiration - start
            days = delta.days + 1
            startdate = last_cost_date

            ins = days/contract.installment
            if found:
                if contract.cost_frequency == "no":
                    startdate = startdate + relativedelta(days=ins)
                elif contract.cost_frequency == "daily":
                    startdate = startdate + relativedelta(days=1)
                elif contract.cost_frequency == "weekly":
                    startdate = startdate + relativedelta(weeks=1)
                elif contract.cost_frequency == "monthly":
                    startdate = startdate + relativedelta(months=1)
                elif contract.cost_frequency == "yearly":
                    startdate = startdate + relativedelta(years=1)

            startdate = datetime.combine(startdate, datetime.min.time())
            while (startdate <= expiration) and left > 0 and (startdate <= d)  and contract.residual > 0:
                data = {
                    'amount': contract.cost_generated,
                    'date': startdate.strftime(tools.DEFAULT_SERVER_DATE_FORMAT),
                    'vehicle_id': contract.vehicle_id.id,
                    'cost_subtype_id': contract.cost_subtype_id.id,
                    'contract_id': contract.id,
                    'auto_generated': True,
                    'contract_type': contract.contract_type,
                }
                cost_id = self.pool.get('fleet.vehicle.cost').create(cr, uid, data, context=context)
                counted+=1
                left -= 1
                if contract.cost_frequency == "no":
                    startdate =startdate+ relativedelta(days=ins)
                elif contract.cost_frequency == "daily":
                    startdate =startdate+ relativedelta(days=1)
                elif contract.cost_frequency == "weekly":
                    startdate =startdate+ relativedelta(weeks=1)
                elif contract.cost_frequency == "monthly":
                    startdate =startdate+ relativedelta(months=1)
                elif contract.cost_frequency == "yearly":
                    startdate =startdate+ relativedelta(years=1)
        return True

    _columns = {
        'name': fields.function(_vehicle_contract_name_get_fnc_custom, type="char", string='Name', store=True),
        'insurer_id' :fields.many2one('res.partner', 'Partner'),
        'cost_subtype_id': fields.many2one('fleet.service.type', 'Type',help='Cost type purchased with this cost'),
        'amount': fields.float('Total Price'),
        'expiration_date': fields.date('To Date', help='Date when the coverage of the contract expired (by default, one year after begin date)'),
        'date' :fields.datetime('Date',help='Date when the cost has been executed'),
	    'duration': fields.char(string='Duration', help='Date When The Coverage Of The Contract Begins And End'),
        'start_date': fields.date(string='From Date', help='Date When The Coverage Of The Contract Begins'),
        'cost_frequency': fields.selection([('no','No'), ('daily', 'Daily'), ('weekly','Weekly'), ('monthly','Monthly'), ('yearly','Yearly')],
                                        'Recurring Cost Frequency', help='Frequency of the recurring cost'),
        'cost_generated': fields.function(_cost_generated, string= 'Recurring Cost Amount',
            help="Costs paid at regular intervals, depending on the cost frequency. If the cost frequency is set to unique, the cost will be logged at the start date"),
        'total_cost':fields.function(_total_cost_fnc, type="float", string='Total Cost'),
        'company_id': fields.many2one('res.company', 'Company',readonly=True),
        'generated_cost_ids': fields.one2many('fleet.vehicle.cost', 'contract_id', 'Generated Costs',
                                            ondelete='cascade'),
        'expected_odometer':fields.float(string="Expected Odometer"),
        'next_maintenance_date':fields.date(string="Next Maintenance"),
        'quantity':fields.float('Quantity'),
        'sum_cost': fields.function(_get_sum_cost, type='float', string='Indicative Costs Total'),
        'department_id': fields.many2one('hr.department','Department'),
        'driver_id': fields.many2one('hr.employee',"Driver"),
        'enrich_id': fields.many2one('payment.enrich', 'Payment Enrich'),
        'car_type': fields.related('vehicle_id','ownership', type='selection', selection=[('owned','Owned'),('rented','Rented'),('generator','Generator'),('mile','Instead mile')],string ='Car Type'),
        'payment_method': fields.selection((('nothing','Nothing'),('voucher','Voucher'),('enrich','Enrich')), "Payment method"),
        'tax_ids': fields.many2many('account.tax',string = 'Taxes', readonly=True),
        'state': fields.selection([('draft', 'Draft'),('confirm', 'Confirm'),('request', 'Request'),('confirm_sm', 'Section Manager'), ('confirm_ss', 'Service Section Manager'),
                                ('confirm_so','Service Officer '),('affairs_mg','Admin Affairs Manager'),
                                ('human_financial','Human resources and Financial Manager'),
                                ('general_mg','General Manager'),('open','open'),
                                ('cancel','Cancel'),('technical','Technical'),
                                ('legal','Legal'), ('wait','Wait Execution'),('confirm_hs','Hospitality Service Officer'),
                                ('approved_mo','Maintenance Officer'),('w_legal','Waiting Legal Management'),
                                ('w_it','Wainting for IT Officer'),('w_admin','Wainting for Adminstrative Manager'),
                                ('w_ss','Wainting for Service Section Manager'),('w_so','Waiting For Seriver Officer'),
                                ('w_haa','Wainting for HR and Accounting Manager'),('w_gm','Wainting for General Manager'),
                                ('w_ho','Wainting for Hopitality Officer'),
                                ('toclose','To Close'),('closed','Terminated'),],'Status'),
        'rent': fields.boolean('Rent'),
        'cat_subtype': fields.related('cost_subtype_id', 'category', type="selection",selection=[('contract', 'Contract'), ('service', 'Service'), ('both', 'Both'), ('env_safety', 'Environment & Safety'),('hospitality','Hospitality'),('occasion','Occasion'),('hall','Hall'),('building','Building'),('media','Media'),('public_relation','Public Relation'),('general','General')], string="Service Type Category"),
        'start_time':fields.float('Start Time'),
        'end_time':fields.float('End Time'),
        'first_booking_date': fields.date(string='First Booking Date', help='The First Booking Date'),
        'last_booking_date': fields.date(string='Last Booking Date', help='The Last Booking Date'),
        'booking_frequency': fields.selection([('no','No'), ('daily', 'Daily'), ('weekly','Weekly'), ('monthly','Monthly'), ('yearly','Yearly')],
                                        'Booking Frequency', help='Frequency Of The Booking Of The Hotel'),
        'location_id':fields.many2one('stock.location','Location'),
        'stock_id':fields.many2one('stock.picking.out','Stock Order'),
        'building_id':fields.many2one('fleet.service.type', 'Building'),
        'installment':fields.integer(string='Installment'),
        'vehicles_ids': fields.many2many('fleet.vehicle', 'fleet_vehicle_contract_vehicle', 'model_id', 'vehicle_id', string='Vehicles'),
        'residual': fields.function(_get_sum_cost,string='Residual'),
        'paid': fields.function(_get_sum_cost,type='float', string= 'Paid'),
        'hall_type': fields.many2one( 'service.hall.type',string='Hall Type'),
        'out_hall':fields.boolean('OutSide Hall'),
        'addtion_notes':fields.boolean('Addtional Notes'),
        'faults_ids': fields.many2many('fleet.vehicle.cost', 'contracts_faults' ,string= 'Faults',
                                            ondelete='cascade'),
        'contract_type':fields.selection([('contract', 'Contract'),('service', 'Service'), ('fault', 'Fault')],'Contract Type', translate=True),
        'purchase_requisition': fields.many2one( 'purchase.requisition',string='Purchase Requisition'),
        'product_ids': fields.many2many('fleet.vehicle.cost', 'contracts_products', string= 'Included Products'),
        'tasks_ids': fields.many2many('fleet.vehicle.cost', 'contracts_tasks', string= 'Included Tasks'),
        'internal': fields.boolean('Internal'),
        'hospitality_subtype_id': fields.many2one('fleet.service.type', 'Type',help='hospitality type purchased with this contract/service'),
        'hospitality_ids': fields.many2many('fleet.vehicle.cost', 'hall_hospitality', string= 'Included Hospitality'),
        'cordinators_ids': fields.many2many('hr.employee', 'contracts_cordinators_emp', string= 'Cordinators'),
        'contract_cost': fields.float('Total Cost'),
        'purchaser_id': fields.many2one('res.users', 'Contractor', help='Person to which the contract is signed for'),
        'weekday':fields.selection([(5, 'saturday'), (6, 'sunday'),(0, 'monday'), (1, 'tuesday'), (2, 'wednesday'), (3, 'thursday'), (4, 'friday')], 'Start Weekday',store=True),
        'hall_registrations': fields.one2many('service.hall_availability', 'contract_id', string= 'Hall Registrations'),
        'skip':fields.boolean('skip a time'),
        'num_needed':fields.integer(string='Number Needed'),
        'place':fields.char(string='Place'),
        'reason':fields.char(string='Reason'),
        'open_hall':fields.boolean('Open The Hall'),
        'partner_name':fields.char(string='partner'),
        'ref_char':fields.char(string='مرجع العقد'),
        'repeat_registration':fields.boolean('Repeat Registration'),
        'hall_reg_type': fields.char('Hall Registration Type'),
        'addition_managerial':fields.boolean('Addition Managerial'),
        'time_exceeded':fields.datetime(string='Time Exceeded'),

    }

    '''def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False):
        try:
            res = super(services,self).read_group(cr, uid, domain, fields, groupby, offset=offset, limit=limit, context=context, orderby=orderby)
        except :
            return []
        return res'''
    
    def read(self, cr, user, ids, fields=None, context=None, load='_classic_read'):
        if context and 'dashboard' in context and 'type' in context :
            type_ = context['type']
            user_obj = self.pool.get('res.users')

            states = []
            
            if user_obj.has_group(cr, user, 'base_custom.group_account_general_manager'):
                if type_ == "g_services":
                    states.append('w_gm')
                if type_ == "g_contracts":
                    states.append('human_financial')
                if type_ == "g_buildings":
                    states.append('general_mg')
            if user_obj.has_group(cr, user, 'base_custom.group_general_hr_manager'):
                if type_ == "g_services":
                    states.append('w_haa')
                if type_ == "g_contracts":
                    states.append('confirm')
                if type_ == "g_buildings":
                    states.append('human_financial')

            if user_obj.has_group(cr, user, 'admin_affairs.group_admin_affair_manager'):
                if type_ == "g_services":
                    states.append('w_admin')
            
            
            ids = self.search(cr, user,[('id','in',ids),('state','in',states)],context=context)  
        res = super(services,self).read(cr, user, ids, fields=fields, context=context, load=load)

        return res


    def open_hall(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'open_hall':True},context=context)
    
    def close_hall(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'open_hall':False},context=context)

    def on_change_exc_date(self, cr, uid, ids, date, context=None):
        #date  = datetime.strptime(date , "%Y-%m-%d")
        if date:
            first_booking_date = last_booking_date = date
            try:
                first_booking_date = datetime.strptime(first_booking_date , "%Y-%m-%d  %H:%M:%S").date()
                last_booking_date = datetime.strptime(last_booking_date , "%Y-%m-%d  %H:%M:%S").date()
            except :
                first_booking_date = datetime.strptime(first_booking_date , "%Y-%m-%d")
                last_booking_date = datetime.strptime(last_booking_date , "%Y-%m-%d")
            try:
                weekday = datetime.strptime(date , "%Y-%m-%d").weekday()
            except :
                weekday = datetime.strptime(date , "%Y-%m-%d  %H:%M:%S").weekday()

            try:
                start_time = datetime.strptime(date , "%Y-%m-%d  %H:%M:%S").hour
            except :
                start_time = 0
            
            
            return {
                'value':{
                    'first_booking_date':str(first_booking_date),
                    'last_booking_date':str(last_booking_date),
                    'weekday':weekday,
                    'start_time':start_time,
                }
            }
        return {}

    def _get_user_department(self, cr, uid, ids, context={}):
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid, context)
        return user.context_department_id.id
    _defaults = {
        'state':'draft',
        'name':'/',
        'notes':'Notes',
        'cost_subtype_id':False,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'fleet.vehicles', context=c),
        #'addtion_notes':'managerial',
        'contract_type' : 'service',
        'purchaser_id': lambda self, cr, uid, context: uid,
        'booking_frequency':'no',
        'department_id':_get_user_department
    }

    def w_request(self, cr, uid, ids, context=None):
        if context:
            if 'cat_subtype' in context and 'rent' in context and 'addtion_notes' in context:
                if 'cost_subtype_id' in context and context['cost_subtype_id']:
                    context['cat_subtype'] = self.get_leatest_category(cr, uid, context['cost_subtype_id'], context)
                if context['cat_subtype'] == 'hall':
                    holl_availability =self.pool.get("service.hall_availability")
                    hall_ids = holl_availability.search(cr,uid,[('contract_id','in',ids)],context=context)
                    if not hall_ids:
                        raise osv.except_osv(_(""),_('No Hall Entered'))
                    if 'hospitality_subtype_id' in context and context['hospitality_subtype_id']:
                        self.w_check_hospitality(cr, uid, ids, context={'cat_subtype':'hospitality',
                        'cost_subtype_id':context['hospitality_subtype_id'],'date':context['date']})
                    if context['rent']:
                        if not context['partner_name']:
                            raise osv.except_osv(_(''), _("insert insurer!"))
                        return self.write(cr, uid, ids, {'state':'w_ss'}, context=context)
                    if not context['rent']:
                        if not context['addtion_notes']:
                            send_mail(self, cr, uid, ids[0], 'admin_affairs.group_admin_affair_manager',unicode(' طلب قاعة', 'utf-8') , unicode(' طلب قاعة في', 'utf-8'), context=context)
                            return self.write(cr, uid, ids, {'state':'w_admin'}, context=context)
                        if context['addtion_notes']:
                            send_mail(self, cr, uid,ids[0],'admin_affairs.group_admin_affairs_it',unicode(' طلب قاعة', 'utf-8') , unicode(' طلب قاعة في', 'utf-8'),context=context)
                            return self.write(cr, uid, ids, {'state':'w_it'}, context=context)
            if context['cat_subtype'] == 'hospitality':
                self.w_check_hospitality(cr, uid, ids, context=context)
                return self.write(cr, uid, ids, {'state':'w_ss'}, context=context)
            if context['cat_subtype'] not in('hall', 'hospitality'):
                return self.write(cr, uid, ids, {'state':'w_ss'}, context=context)
    
    def w_it(self, cr, uid, ids, context=None): 
        send_mail(self, cr, uid, ids[0], 'admin_affairs.group_admin_affair_manager',unicode(' طلب قاعة', 'utf-8') , unicode(' طلب قاعة في', 'utf-8'), context=context)
        return self.write(cr, uid, ids, {'state':'w_admin'}, context=context)
    
    def w_admin(self, cr, uid, ids, context=None): 
        if context:
            if 'cat_subtype' in context and 'rent' in context:
                if 'cost_subtype_id' in context and context['cost_subtype_id']:
                    context['cat_subtype'] = self.get_leatest_category(cr, uid, context['cost_subtype_id'], context)
                if context['cat_subtype'] == 'hall':
                    if context['rent']:
                        self.create_hopitality(cr, uid, ids, context=context)
                        send_mail(self, cr, uid, ids[0], 'base_custom.group_general_hr_manager',unicode(' طلب قاعة', 'utf-8') , unicode(' طلب قاعة في', 'utf-8'), context=context)
                        return self.write(cr, uid, ids, {'state':'w_haa'}, context=context)
                    if not context['rent']:
                        self.create_hopitality(cr, uid, ids, context=context)
                        return self.write(cr, uid, ids, {'state':'w_ss'}, context=context)
                if context['cat_subtype'] == 'hospitality':
                    return self.write(cr, uid, ids, {'state':'w_so'}, context=context)
                else:
                    self.w_roof(cr, uid, ids, 1, skip_to=True, context=context)
    
    def w_ss(self, cr, uid, ids, context=None): 
        if context:
            if 'cat_subtype' in context and 'rent' in context and 'addtion_notes' in context:
                if 'cost_subtype_id' in context and context['cost_subtype_id']:
                    context['cat_subtype'] = self.get_leatest_category(cr, uid, context['cost_subtype_id'], context)
                if context['cat_subtype'] == 'hall':
                    if context['rent']:
                        if not context['addtion_notes']:
                            send_mail(self, cr, uid, ids[0], 'admin_affairs.group_admin_affair_manager',unicode(' طلب قاعة', 'utf-8') , unicode(' طلب قاعة في', 'utf-8'), context=context)
                            return self.write(cr, uid, ids, {'state':'w_admin'}, context=context)
                        if context['addtion_notes']:
                            send_mail(self, cr, uid, ids[0], 'admin_affairs.group_admin_affairs_it',unicode(' طلب قاعة', 'utf-8') , unicode(' طلب قاعة في', 'utf-8'), context=context)
                            return self.write(cr, uid, ids, {'state':'w_it'}, context=context)
                    if not context['rent']:
                        return self.write(cr, uid, ids, {'state':'w_so'}, context=context)
            if context['cat_subtype'] == 'hospitality':
                if context['payment_method'] == 'voucher':
                    if not context['insurer_id']:
                        if context['rent']:
                            raise osv.except_osv(_(''), _("insert insurer!"))
                val = self.w_roof(cr, uid, ids, 0, skip_to=False, context=context)
                if val:
                    return val
                else:
                    return self.write(cr, uid, ids, {'state':'w_so'}, context=context)

            else:
                if context['cat_subtype'] != 'hall':
                    if context['payment_method'] == 'voucher':
                        if not context['insurer_id']:
                            raise osv.except_osv(_(''), _("insert insurer!"))
                send_mail(self, cr, uid, ids[0], 'admin_affairs.group_admin_affair_manager',unicode(' طلب قاعة', 'utf-8') , unicode(' طلب قاعة في', 'utf-8'), context=context)
                return self.write(cr, uid, ids, {'state':'w_admin'}, context=context)
    
    def w_so(self, cr, uid, ids, context=None): 
        if context:
            if 'cat_subtype' in context and 'rent' in context :
                if 'cost_subtype_id' in context and context['cost_subtype_id']:
                    context['cat_subtype'] = self.get_leatest_category(cr, uid, context['cost_subtype_id'], context)
                if context['cat_subtype'] == 'hall':
                    if not context['rent']:
                        return self.open(cr=cr, uid=uid, ids=ids,context=context,passed=True)
                if context['cat_subtype'] == 'hospitality':
                    self.open(cr=cr, uid=uid, ids=ids,context=context,passed=True)
                    return self.write(cr, uid, ids, {'state':'w_ho'}, context=context)
    
    def w_haa(self, cr, uid, ids, context=None): 
        if context:
            if 'cat_subtype' in context and 'rent' in context :
                if 'cost_subtype_id' in context and context['cost_subtype_id']:
                    context['cat_subtype'] = self.get_leatest_category(cr, uid, context['cost_subtype_id'], context)
                if context['cat_subtype'] == 'hall':
                    if context['rent']:
                        return self.open(cr=cr, uid=uid, ids=ids,context=context,passed=True)
                        #send_mail(self, cr, uid, ids[0], 'base_custom.group_account_general_manager',unicode(' طلب قاعة', 'utf-8') , unicode(' طلب قاعة في', 'utf-8'), context=context)
                        #return self.write(cr, uid, ids, {'state':'w_gm'}, context=context)
                if context['cat_subtype'] not in ('hospitality', 'hall'):
                    self.w_roof(cr, uid, ids, 2, skip_to=True, context=context)
    
    def w_ho(self, cr, uid, ids, context=None): 
        if context:
            if 'cat_subtype' in context and 'rent' in context :
                if 'cost_subtype_id' in context and context['cost_subtype_id']:
                    context['cat_subtype'] = self.get_leatest_category(cr, uid, context['cost_subtype_id'], context)
                if context['cat_subtype'] == 'hospitality':
                    return self.write(cr, uid, ids, {'state':'toclose'}, context=context)
    def w_gm(self, cr, uid, ids, context=None):
        return self.open(cr=cr, uid=uid, ids=ids,context=context,passed=True)
        
    
    def w_roof(self, cr, uid, ids, roof, skip_to, context=None):
        name = ['affairs_mg', 'human_financial', 'general_mg'][roof]
        target = ['w_admin', 'w_haa', 'w_gm'][roof]
        contract = self.browse(cr, uid, ids[0], context=context)
        bay_roof = self.pool.get('admin.affairs.payment.roof')
        service_bay_roof_ids = bay_roof.search(cr,uid,[('model_id', '=', 'fleet.vehicle.log.contract'),
                ('service_id', '=', contract.cost_subtype_id.id),
                ('cost_from', '<=', contract.sum_cost),
                ('name', '=', name)],context=context)
        service_bay_roof = bay_roof.browse(cr,uid,service_bay_roof_ids,context=context)
        if service_bay_roof:
            for i in service_bay_roof:  
                    return contract.write({'state':target})
        if skip_to:
            return self.open(cr=cr, uid=uid, ids=ids,context=context,passed=True)
        else:
            return False
    
    def create_hopitality(self, cr, uid, ids, context=None):
        if context:
            if 'cat_subtype' in context and context['cat_subtype'] == 'hall':
                if 'hospitality_ids' in context and context['hospitality_ids']:
                    hospitality_ids = [x[1] for x in context['hospitality_ids'] ]
                    rent = 'rent' in context and context['rent']
                    service = context['hospitality_subtype_id']
                    num_needed =  context['num_needed'] or 0
                    if service:
                        self.w_check_hospitality(cr, uid, ids, context={'cat_subtype':'hospitality',
                        'cost_subtype_id':service,'date':context['date']})
                        date = datetime.strptime(context['date'], "%Y-%m-%d %H:%M:%S")
                        hall = self.read(cr,uid, ids,['cost_subtype_id'], context=context)
                        hall = hall[0]['cost_subtype_id'][1]
                        new_id = self.copy(cr, uid, ids[0], {'date':date,'num_needed':num_needed,'cost_subtype_id':None, 'cost_ids':[[6, 0, hospitality_ids ]], 'cost_subtype_id':service,
                        'place':hall,'reason':'ضيافة قاعة','rent':rent, 'hall_registrations':None}, context=context)
    

    def w_check_hospitality(self, cr, uid, ids, context=None):
        if context:
            if 'cat_subtype' in context and 'cost_subtype_id' in context and 'date' in context :
                if context['cat_subtype'] == 'hospitality':
                    if context['date']:
                        hours = datetime.strptime(context['date'], "%Y-%m-%d %H:%M:%S") - datetime.now()
                        hours = hours.total_seconds() / 3600.0

                    record = self.pool.get('fleet.service.type').read(cr, uid, context['cost_subtype_id'],['time_to_request','users'], context=context )
                    time_to_request = record['time_to_request']
                    users = record['users'] or []
                    #check if the current user in the permitted users
                    user_in = uid in users
                    zero = time_to_request == 0

                    if 'mode' in context and context['mode'] == 1:
                        return {
                            'title': _('Hour/s You have Before Request'),
                            'message': _(str(time_to_request))}

                    if hours < time_to_request and not user_in and not zero:
                        raise osv.except_osv(_(""),
                            _('The diffrent between the invoice date and date from must be less than of equal to the service time to request!'))
    
    def get_leatest_category(self, cr, uid, id, context=None):
        return str(self.pool.get('fleet.service.type').read(cr, uid, id, ['category'],context=context)['category'])

    def _check_negative(self, cr, uid, ids, context=None):
        """
        Check the value of amount, cost_generated and odometer,
        if greater than zero or not.

        @return: Boolean of True or False
        """
        count = 0
        for act in self.browse(cr, uid, ids, context):
            message = _("")
            if (act.amount < 0):
                message = message + _("Total Price")
                count = count + 1
            if (act.cost_generated < 0):
                if (count > 0):
                    message = message + ", "
                message = message + _("Recurring Cost Amount")
                count = count + 1
            if (act.odometer < 0):
                if (count > 0):
                    message = message + _(" And ")
                message = message + _("Odometer")
            if (act.expected_odometer < 0):
                if (count > 0):
                    message = message + _(" And ")
                message = message + _("Expected Odometer")
                count = count + 1

            if (act.residual < 0):
                if (count > 0):
                    message = message + ", "
                message = message + _("Residual Amount\n(All Paid Money The greater Than The Total Cost The)\n")
                count = count + 1

            message = message + _(" Must Be Positive Value!")
        if count > 0 :
            raise osv.except_osv(_(''), _(message))
        return True

    def _check_date(self, cr, uid, ids, context=None):
        """
        Check the value of start_date if greater than expiration_date or not.

        @return: Boolean of True or False
        """
        for act in self.browse(cr, uid, ids, context):
            if ((act.start_date > act.expiration_date) and act.expiration_date):
                raise osv.except_osv(_(''), _("Contract Start Date Must Be Less Than Expiration Date!"))
            if act.cost_subtype_id.category == 'hall':
                if act.first_booking_date > act.last_booking_date:
                    raise osv.except_osv(_(''), _("Contract First Booking Date Must Be Less Than Last Booking Date!"))
                if act.first_booking_date < act.start_date:
                    pass
                    #raise osv.except_osv(_(''), _("Contract First Booking Date Must Be Greater Than Start Date!"))
                if act.first_booking_date > act.expiration_date:
                    raise osv.except_osv(_(''), _("Contract First Booking Date Must Be Less Than Expiration Date!"))
                if act.last_booking_date < act.start_date:
                    pass
                    #raise osv.except_osv(_(''), _("Contract Last Booking Date Must Be Greater Than Start Date!"))
                if act.last_booking_date > act.expiration_date:
                    raise osv.except_osv(_(''), _("Contract Last Booking Date Must Be Less Than Expiration Date!"))
        return True

    def _check_time(self, cr, uid, ids, context=None):
        """
        Check the value of start_time if greater than end_time or not.

        @return: Boolean of True or False
        """
        for act in self.browse(cr, uid, ids, context):
            if act.cat_subtype == 'hall':
                if ( (act.start_time) >= (act.end_time) ):
                    raise osv.except_osv(_(''), _("Contract Start Time Must Be Less Than End Time!"))
        return True

    def _check_empty(self, cr, uid, ids, context=None):
        """
        Check the value of start_time if greater than end_time or not.

        @return: Boolean of True or False
        """
        for act in self.browse(cr, uid, ids, context):
            if (act.installment == 0 and act.cost_frequency == "no" and act.state != "draft"):
                raise osv.except_osv(_(''), _("Contract installment Or Cost Frequency Must Be Set!"))
        return True

    def _check_hall_booking(self, cr, uid, ids, context=None):
        """
        Check the hall to see if it had booked or not.

        @return: Boolean of True or False
        """
        for act in self.browse(cr, uid, ids, context):
            if act.cat_subtype == 'hall':
                if self._exist_hall_booking(cr, uid, act, context):
                    raise osv.except_osv(_(''), _("this hall is already booked!"))
        return True

    def _exist_hall_booking(self, cr, uid, hall, context=None):
        ids = self.search(cr,uid,[('cost_subtype_id','=',hall.cost_subtype_id.id),('id','!=',hall.id),('state','not in',('cancel','closed')),],context=context)
        for h in self.browse(cr,uid,ids,context = context):
            if self._compare(self._all_bookings(hall),self._all_bookings(h)):
                return True
        return False

    def _compare(self,l1,l2):
        for i in l1:
            for o in l2:
                if o[0] >=  i[0]:
                    if o[0] < i[1]:
                        return True
                if i[0] >=  o[0]:
                    if i[0] < o[1]:
                        return True

        return False


    def get_time(self,time):
        hour = int(time)%24
        minute=int((time - hour)*60)%60
        #minute =time - int(time)
        
        #minute = int(minute*100)
        #minute =60*minute/100

        return hour,minute
    def _all_bookings(self, hall):
        """
        return a list of all booking times of a hall
        """
        frequency={'daily':relativedelta(days=1),'weekly':relativedelta(weeks=1),'monthly':relativedelta(months=1),'yearly':relativedelta(years=1)}
        List = []
        interval = hall.first_booking_date
        date_format = "%Y-%m-%d"
        interval  = datetime.strptime(interval , date_format)
        last_date = datetime.strptime(hall.expiration_date, date_format)
        factor = 0.5
        if hall.out_hall:
            factor = 1.0
        start_time = (hall.start_time ) % 24.0 #+ factor
        end_time = (hall.end_time ) % 24.0   #- factor




        start_hour,start_minute = self.get_time(start_time)
        end_hour,end_minute     = self.get_time(end_time)


        while interval <= last_date:
            start_datetime = datetime(interval.year,interval.month,interval.day,start_hour,start_minute)
            end_datetime   = datetime(interval.year,interval.month,interval.day,end_hour  ,end_minute)
            List.append((  start_datetime , end_datetime   ))
            if hall.booking_frequency == 'no':
                break
            interval += frequency[hall.booking_frequency]

        return List


    _constraints = [
        (_check_date, _(''), ['start_date','expiration_date']),
        (_check_time, _(''), ['start_time','end_time']),
        (_check_negative, '', ['amount','cost_generated','expected_odometer','odometer','residual']),
        #(_check_hall_booking, _(''), ['cost_subtype_id','start_time','end_time','state','first_booking_date','booking_frequency','start_date','expiration_date']),
        
        #(_check_empty, _(''), ['installment','cost_frequency']),
    ]


    def open(self, cr, uid, ids,context=None,passed=False):
        """
        Change state of contract To open.

        @return: write state
        """
        serv_obj=self.pool.get('fleet.service.type')
        ser=serv_obj.browse(cr, uid, ids, context=context)
        cost_obj=self.pool.get('fleet.vehicle.cost')
        bay_roof = self.pool.get('admin.affairs.payment.roof')
        count=0
        contract = self.browse(cr, uid, ids[0], context=context)
        contract.write({'state':'open'})
        
        if not passed:
            service_bay_roof_ids = bay_roof.search(cr,uid,[('model_id','=','fleet.vehicle.log.contract'),
                ('service_id','=',contract.cost_subtype_id.id),
                ('cost_from','<=',contract.sum_cost),],context=context)
            service_bay_roof = service_bay_roof_ids and bay_roof.browse(cr,uid,service_bay_roof_ids,context=context) or False
            if service_bay_roof:
                for i in service_bay_roof:
                    if i.name == 'affairs_mg':
                        return contract.write({'state':i.name})
                    if i.name == 'human_financial':
                        return contract.write({'state':i.name})
                    if i.name == 'general_mg':
                        return contract.write({'state':i.name})            

        for record in contract.cost_ids:
            if record.cost_subtype_id:
                record.cost_subtype_id.write({'cost':record.amount})
        
        if contract.payment_method == 'voucher' and contract.amount > 0:
            self.pool.get('fleet.vehicle.cost').create(cr, uid, {
			'amount': contract.amount,
			'date': contract.start_date,
			'vehicle_id': contract.vehicle_id.id,
			'cost_subtype_id': contract.cost_subtype_id.id,
			'contract_id': contract.id,
            'insurer_id':contract.insurer_id.id,
			'auto_generated': True,
			'activation':True,
            'contract_type':contract.contract_type,
			},
            context=context)
            
        if contract.payment_method == 'enrich' and contract.sum_cost > 0:
            details = 'Enrich Line :'+contract.name and contract.name or ""
            self.pool.get('payment.enrich.lines').create(cr, uid, {'enrich_id':contract.enrich_id.id,'date':contract.date,
                                                    'cost':contract.sum_cost,'name':details,
                                                    'service_id':contract.cost_subtype_id.id,
                                                    'model_id':'fleet.vehicle.log.contract',
                                                    'department_id':contract.department_id.id,
                                                    'owner_id':contract.id},
                                                    context=context)
            contract.write({'state':'wait'})
            copy_attachments(self,cr,uid,[contract.id],'fleet.vehicle.log.contract',contract.enrich_id.id,'payment.enrich', context=context)
        
        if contract.car_type =='rented':
    	    self.pool.get('fleet.vehicle').write(cr,uid,[contract.vehicle_id.id] ,{'ownership':'rented','status':'active'},context=context)



    def affairs_mg(self, cr, uid, ids, context=None):
        """
        Button method changes the state to 'Admin Affairs Manager'.
        @return: write state
        """
        contract = self.browse(cr, uid, ids[0], context=context)
        bay_roof = self.pool.get('admin.affairs.payment.roof')
        service_bay_roof_ids = bay_roof.search(cr,uid,[('model_id','=','fleet.vehicle.log.contract'),
                ('service_id','=',contract.cost_subtype_id.id),
                ('cost_from','<=',contract.sum_cost),],context=context)
        service_bay_roof = service_bay_roof_ids and bay_roof.browse(cr,uid,service_bay_roof_ids,context=context) or False
        if service_bay_roof:
            for i in service_bay_roof:
                if i.name == 'human_financial':
                    return contract.write({'state':i.name})
                if i.name == 'general_mg':
                    return contract.write({'state':i.name}) 
        return self.open(cr=cr, uid=uid, ids=ids,context=context,passed=True)

    def human_financial(self, cr, uid, ids, context=None):
        """
        Button method changes the state to 'human resources and financial Manager'.
        @return: write state
        """
        contract = self.browse(cr, uid, ids[0], context=context)
        
        bay_roof = self.pool.get('admin.affairs.payment.roof')
        service_bay_roof_ids = bay_roof.search(cr,uid,[('model_id','=','fleet.vehicle.log.contract'),
                ('service_id','=',contract.cost_subtype_id.id),
                ('cost_from','<=',contract.sum_cost),],context=context)
        service_bay_roof = service_bay_roof_ids and bay_roof.browse(cr,uid,service_bay_roof_ids,context=context) or False
        if service_bay_roof:
            for i in service_bay_roof:
                if i.name == 'general_mg':
                    send_mail(self, cr, uid, ids[0], 'base_custom.group_account_general_manager','adminstartive affairs request', 'adminstartive affairs request at ', context=context)
                    return contract.write({'state':i.name})
        return self.open(cr=cr, uid=uid, ids=ids,context=context,passed=True)

    def general_mg(self, cr, uid, ids, context=None):
        """
        Button method changes the state to 'General Manager'.
        @return: write state
        """
        contract = self.browse(cr,uid,ids[0],context)
        if contract.cost_subtype_id.category == 'license':
            data={}
            data['date']   = datetime.strptime(contract.start_date, "%Y-%m-%d")
            data['year']   = data['date'].year
            data['month']  = str(data['date'].month)
            data['amount'] = contract.sum_cost
            data['state']  = 'done'
            data['company_id'] = contract.company_id.id
            data['desc'] = contract.name
            data['department_id'] = contract.department_id.id
            List = []
            for suplier in contract.cost_ids:
                List.append( (0,0,{'name':suplier.insurer_id.name,'cost':suplier.amount,'date':contract.date}) )
            data['enrich_lines'] = List
            enrich_id = self.pool.get("payment.enrich").create(cr,uid,data,context=context)
            copy_attachments(self,cr,uid,[contract.id],'fleet.vehicle.log.contract',enrich_id,'payment.enrich', context=context)
            return self.write(cr, uid, contract.id, {'state':'closed','enrich_id':enrich_id}, context=context)
        elif contract.cost_subtype_id.category == 'insurance':
            contract.write({'amount':contract.sum_cost,'residual':contract.sum_cost,'paid':0})
            self.open(cr=cr, uid=uid, ids=ids,context=context,passed=True)
            contract.transfer()
            contract.write({'state':'closed'})
        else:
            self.open(cr=cr, uid=uid, ids=ids,context=context,passed=True)
            send_mail(self, cr, uid, ids[0], 'base_custom.group_account_general_manager','adminstartive affairs request', 'adminstartive affairs request at ', context=context)
                    




    #########################################################################
    def count_availability(self, cr, uid, ids, context=None):
        holl_availability =self.pool.get("service.hall_availability")
        frequency={'daily':relativedelta(days=1),'weekly':relativedelta(weeks=1),'monthly':relativedelta(months=1),'yearly':relativedelta(years=1)}
        for record in self.browse(cr, uid, ids,context=context):
            lines = []
            first_booking_date = datetime.strptime(record.first_booking_date, "%Y-%m-%d")
            expiration_date = datetime.strptime(record.expiration_date, "%Y-%m-%d")
            booking_frequency = record.booking_frequency
            while first_booking_date <= expiration_date:
                #found the start_datetime and end_datetime
                factor = 0.5
                if record.out_hall:
                    factor = 1

                start_time = record.start_time #+ factor
                start_hour = int(start_time)%24
                start_minute=int((start_time - start_hour)*60)%60

                end_time = record.end_time #- factor
                end_hour = int(end_time)%24
                end_minute=int((end_time - end_hour)*60)%60
                start_datetime = datetime(first_booking_date.year,first_booking_date.month,first_booking_date.day,start_hour,start_minute)
                end_datetime   = datetime(first_booking_date.year,first_booking_date.month,first_booking_date.day,end_hour  ,end_minute)
                lines.append({'contract_id':record.id,
                              'string':record.cost_subtype_id.name,
                              'date_start':start_datetime,
                              'date_stop':end_datetime})
                if booking_frequency == 'no':
                    break
                first_booking_date += frequency[booking_frequency]
            deleted_ids = holl_availability.search(cr,uid,[('contract_id','=',record.id)],context=context)
            holl_availability.unlink(cr,uid,deleted_ids,context=context)
            for l in lines:
                holl_availability.create(cr,uid,l,context=context)


    def request(self, cr, uid, ids, context=None):
        """
        Button method changes the state to 'request' or to technical.
        @return: write state
        """
        next_state = 'request'
        for record in self.browse(cr, uid, ids,context=context):
            if record.cat_subtype == "hall" and record.addtion_notes:
                next_state = 'technical'

            if record.cat_subtype == "hospitality":
                hours = datetime.strptime(record.date, "%Y-%m-%d %H:%M:%S") - datetime.now()
                
                hours = hours.total_seconds() / 3600.0

                #check if the current user in the permitted users
                user_in = uid in [user.id for user in record.cost_subtype_id.users]
                zero = record.cost_subtype_id.time_to_request == 0
                if hours < record.cost_subtype_id.time_to_request and not user_in and not zero:
                    raise osv.except_osv(_(""),
                        _('The diffrent between the invoice date and date from must be less than of equal to the service time to request!'))
            if record.payment_method =='enrich' and record.sum_cost > 0 and record.enrich_id.residual_amount < record.sum_cost:
                    raise osv.except_osv(_(""),_('No Enough Money In The Enrich!'))
                    
        return self.write(cr, uid, ids, {'state':next_state}, context=context)

    def technical(self, cr, uid, ids, context=None):
        """
        Button method changes the state to 'request'.
        @return: write state
        """
        
        return self.write(cr, uid, ids, {'state':'request'}, context=context)

    def confirm(self, cr, uid, ids, context=None):
        """
        Button method changes the state to 'confirm'.
        @return: write state
        """
        for record in self.browse(cr, uid, ids,context=context):
            if record.cat_subtype == "building":
                faluts_ids = [x.id for x in record.faults_ids]
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                now = datetime.strptime(now,"%Y-%m-%d %H:%M:%S")
                self.pool.get('fleet.vehicle.cost').write(cr, uid, faluts_ids, {'start_time':now})
        
        #for contract and service case not neet middle state before the roofs
        if 'contract_type' in context and context['contract_type'] != 'fault':
            return self.approve(cr, uid, ids, context=context)
        send_mail(self, cr, uid, ids[0], 'base_custom.group_general_hr_manager','adminstrative affairs request', 'adminstrative affairs request at ', context=context)
        return self.write(cr, uid, ids, {'state':'confirm'}, context=context)
    
    def approve(self, cr, uid, ids, context=None):
        """
        Button set start date in faults and call method 'open'.
        @return: write state
        """
        for record in self.browse(cr, uid, ids,context=context):
            if record.cat_subtype == "building":
                 for fault in record.faults_ids:
                     if fault.end_time:
                         start_time = datetime.strptime(fault.start_time, "%Y-%m-%d %H:%M:%S")
                         end_time = datetime.strptime(fault.end_time, "%Y-%m-%d %H:%M:%S")
                         hours = (end_time - start_time).seconds/3600.0
                         fault.write({'time':hours},context=context)
                     
        if context:
            if 'contract_type' in context and context['contract_type'] == 'fault':
                if 'internal'in context and context['internal'] == False:
                    if 'internal'in context and context['internal'] == False:
                        if 'payment_method' in context and context['payment_method'] == 'enrich':
                            return self.write(cr, uid, ids, {'state':'approved_mo'}, context=context)
                        if 'payment_method' in context and context['payment_method'] == 'voucher':
                            return self.write(cr, uid, ids, {'state':'affairs_mg'}, context=context)
        return self.open(cr=cr, uid=uid, ids=ids, context=context,passed=False)

    def to_affairs_mg(self, cr, uid, ids, context=None):
        """
        Button method changes the state to 'Admin Affairs Manager'.
        @return: write state
        """
        '''for contract in self.browse(cr, uid, ids, context=context):
            if contract.'''
        if 'cat_subtype' in context and context['cat_subtype'] == 'hall':
            if 'hospitality_ids' in context and context['hospitality_ids']:
                hospitality_ids = [x[1] for x in context['hospitality_ids'] ]
                internal = 'internal' in context and context['internal']
                service = self.pool.get('fleet.service.type').search(cr, uid, [('category','=','hospitality')],context=context)
                if service:
                    new_id = self.copy(cr, uid, ids[0], {'cost_subtype_id':None, 'cost_ids':[[6, 0, hospitality_ids ]], 'cost_subtype_id':service[0], 'internal':internal}, context=context)
        send_mail(self, cr, uid, ids[0], 'base_custom.group_general_hr_manager','adminstartive affairs request', 'adminstartive affairs request at ', context=context)
        return self.write(cr, uid, ids, {'state':'affairs_mg'}, context=context)

    def to_human_financial(self, cr, uid, ids, context=None):
        """
        Button method changes the state to 'human resources and financial Manager'.
        @return: write state
        """
        send_mail(self, cr, uid, ids[0], 'base_custom.group_account_general_manager','adminstrative affairs request', 'adminstrative affairs request at ', context=context)
        return self.write(cr, uid, ids, {'state':'human_financial'}, context=context)

    def to_general_mg(self, cr, uid, ids, context=None):
        """
        Button method changes the state to 'General Manager'.
        @return: write state
        """
        if 'internal' in context:
            return self.open(cr, uid, ids, context=context,passed=True)
        return self.write(cr, uid, ids, {'state':'general_mg'}, context=context)
    
    def to_w_legal(self, cr, uid, ids, context=None):
        """
        Button method changes the state to 'w_legal'.
        @return: write state
        """
        return self.write(cr, uid, ids, {'state':'w_legal'}, context=context)


    def open_license(self, cr, uid, ids,context=None):
        """
        Change state of contract To open.

        @return: write state
        """
        serv_obj=self.pool.get('fleet.service.type')
        ser=serv_obj.browse(cr, uid, ids, context=context)
        cost_obj=self.pool.get('fleet.vehicle.cost')
        bay_roof = self.pool.get('admin.affairs.payment.roof')
        count=0
        for contract in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, ids, {'state':'open'}, context=context)
            for record in contract.cost_ids:
                a = record.cost_subtype_id.id
                self.pool.get('fleet.service.type').write(cr, uid,a,{'cost':record.amount},context=context)
            if contract.payment_method == 'voucher':
                if contract.vehicle_id.id and contract.cost_frequency =='no' :
                    data = {
                    'amount': contract.amount+contract.sum_cost,
                    'date': contract.start_date,
                    'vehicle_id': contract.vehicle_id.id,
                    'cost_subtype_id': contract.cost_subtype_id.id,
                    'contract_id': contract.id,
                    'auto_generated': True,
                    'activation':True,
                    'contract_type':contract.contract_type,
                    }
                else :
                    data = {
                    'amount': contract.amount,
                    'date': contract.start_date,
                    'cost_subtype_id': contract.cost_subtype_id.id,
                    'contract_id': contract.id,
                    'auto_generated': True,
                    'activation':True,
                    'contract_type':contract.contract_type,
                    }
                self.pool.get('fleet.vehicle.cost').create(cr, uid, data, context=context)

            if contract.car_type =='rented':
                self.pool.get('fleet.vehicle').write(cr,uid,[contract.vehicle_id.id] ,{'ownership':'rented','status':'active'},context=context)



    def contract_close(self, cr, uid, ids, context=None):
        """
        Change state of contract To closed.

        @return: write state
        """
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.vehicle_id:
            self.pool.get('fleet.vehicle').write(cr, uid, [obj.vehicle_id.id],
                                                {'expected_odometer':obj.expected_odometer,
                                                'next_maintenance_date':obj.next_maintenance_date}, context=context)
        return self.write(cr, uid, ids, {'state': 'closed'}, context=context)

    def cancel(self, cr, uid, ids, context=None):
        """
        Button method changes the state to 'cancel' and writes notes about the cancellation.
        @return: write state
        """
        new_id = self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        holl_availability =self.pool.get("service.hall_availability")
        deleted_ids = holl_availability.search(cr,uid,[('contract_id','in',ids)],context=context)
        holl_availability.unlink(cr,uid,deleted_ids,context=context)
        
        return new_id


    def onchange_cost(self, cr, uid, ids, cost_subtype_id, context=None):
        """
        Onchange method change value of vehicle_id depended on cost_subtype_id.category

        @param method: cost_subtype_id of current value in contract
        @return: domain of vehicle_id
        """
        serv_obj =self.pool.get('fleet.service.type')
        veh = self.pool.get('fleet.vehicle')
        values = []
        domain = []
        res = {}
        if cost_subtype_id:
            cate = serv_obj.browse(cr, uid, cost_subtype_id)
            if (cate.category == 'contract'):
                domain += [('state','=','confirm'),('ownership','=','owned')]
            if (cate.category == 'both'):
                domain += [('state','=','confirm'),'|',('ownership','=','owned'),('ownership','=','rented')]
            vehicle_both = veh.search(cr , uid, domain)
            for vehicle in veh.browse(cr, uid, vehicle_both):
                values.append(vehicle.id)
            res = {'domain':{'vehicle_id':[('id','=',values)]}}
            return res
        else:
            res = {'domain':{'vehicle_id':[('id','=',False)]}}
            return res


    def onchange_service_type(self, cr, uid, ids, cost_subtype_id, context=None):
        """
        On change service field value function gets the cost  of service.
        @return: Cost of service
        """
        
        if cost_subtype_id:
            date = False
            service_type_obj=self.pool.get('fleet.service.type').browse(cr, uid, cost_subtype_id, context=context)
            domain = {}
            category=service_type_obj and service_type_obj.category or False
            value = {
                    'cat_subtype': category, 'cost_ids':[]}
            warning = {}

            if ids:
                self.write(cr, uid, ids[0],{'cat_subtype':category}, context=context)
                contract = self.browse(cr, uid, ids[0], context=context)
                date = contract.date
                list_lines = []
                for item in contract.cost_ids:
                    list_lines += (0,2,item.id)
                    item.unlink()
                value['cost_ids'] += list_lines


            
            if category == "hall":
                list_ids = [i.id for i in service_type_obj.hall_type]
                domain = {'hall_type':[('id','in',list_ids)],
                  }
                data = [{'cost_subtype_id':x.id, 'quantity':x.quantity, 'amount': x.cost} for x in service_type_obj.child_ids]
                new_list_lines = [(0,0,item) for item in data]
                value['cost_ids'] += new_list_lines
            elif category == 'hospitality':
                warning = self.w_check_hospitality(cr, uid, ids,context={'date':date,'cost_subtype_id':cost_subtype_id,'cat_subtype':category,'mode':1})
                data = [{'cost_subtype_id':x.id, 'quantity':x.quantity, 'amount': x.cost} for x in service_type_obj.child_ids]
                list_lines = [(0,0,item) for item in data]
                value['cost_ids'] += list_lines
            
            elif category == 'env_safety':
                data = [{'cost_subtype_id':x.id, 'quantity':x.quantity, 'amount': x.cost} for x in service_type_obj.child_ids]
                list_lines = [(0,0,item) for item in data]
                value['cost_ids'] += list_lines
            return {
            'value': value,
            'domain':domain,
            'warning':warning
            }
        return {}
    
    def onchange_hospitality_type(self, cr, uid, ids, cost_subtype_id, context=None):
        if cost_subtype_id:
            service_type_obj=self.pool.get('fleet.service.type').browse(cr, uid, cost_subtype_id, context=context)
            value = {
                    'hospitality_ids':[]}

            if ids:
                contract = self.browse(cr, uid, ids[0], context=context)
                list_lines = []
                for item in contract.cost_ids:
                    list_lines += (0,2,item.id)
                    item.unlink()
                value['hospitality_ids'] += list_lines
            
            list_ids = [i.id for i in service_type_obj.hall_type]
            data = [{'cost_subtype_id':x.id, 'quantity':x.quantity, 'amount': x.cost} for x in service_type_obj.child_ids]
            new_list_lines = [(0,0,item) for item in data]
            value['hospitality_ids'] += new_list_lines
            warning = self.w_check_hospitality(cr, uid, ids,context={'date':False,'cost_subtype_id':cost_subtype_id,'cat_subtype':'hospitality','mode':1})
            return {
            'value': value,
            'warning':warning
            }
        return {}

    def onchange_car_type(self, cr, uid, ids, vehicle_id, cost_subtype_id, car_type, context=None):
        """
        Onchange method set value of car_type with vehicle.ownership
        @return: value of car_type
        """
        res={}
        serv_obj =self.pool.get('fleet.service.type')
        veh = self.pool.get('fleet.vehicle')
        vehicle = veh.browse(cr, uid, vehicle_id)
        res['value']={'car_type':vehicle.ownership}
        cate = serv_obj.browse(cr, uid, cost_subtype_id)
        if (cate.category == 'both')and(vehicle.ownership=='owned'):
                res['value']['payment_method']= 'nothing'
        return res

    def on_change_pay_method(self, cr, uid, ids, method, context=None):
        """
        On change payment method  field value function gets the value of anoter fields.

        @param method: payment method of current contract
        @return: Dictionary of amount, cost_generated and cost_frequancy values
        """
        if not method:
            return {}

        if method=='enrich':
            return {
                'value': {
                    'cost_generated': 0,
                    'cost_frequency': 'no',
                    },
            }
        if method=='nothing':
            return {
                'value': {
                    'amount': 0,
                    'cost_generated': 0,
                    'cost_frequency': 'no',
                    },
            }
        return {}


    def onchange_out_hall(self, cr, uid, ids, out_hall, context=None):
        """
        On change out_hall field value function sets the value of rent.

        @param out_hall: is the hall is outside 
        @return: Dictionary of rent
        """

        if not out_hall:
            return {}

        if out_hall:
            return {
                'value': {
                    'rent': False,
                    },
            }


    def extend_action(self, cr, uid, ids, context=None):
        """
        Return form data to wizard.

        @return: Dictionary of form data
        """
        dummy , view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'service', 'vehicle_rent_extend_form')
        obj = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':_("Extend Contract"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'vehicle.rent.extend',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
           	'con_id' : obj.id ,
            }
        }

    def renew_action(self, cr, uid, ids, context=None):
        """
        Return form data to wizard.

        @return: Dictionary of form data
        """
        dummy , view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'service', 'vehicle_rent_renew_form')
        obj = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':_("Renew Contract"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'vehicle.rent.renew',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'con_id' : obj.id ,
            }
        }
    


    def create_purchase(self, cr, uid, ids, context=None):
        """ 
        create purchase order for selected contract(s).

        @return: Dictionary that close the wizard
        """
        contract = self.browse(cr, uid, ids[0], context=context)
        if not contract.product_ids:
            raise osv.except_osv(_("Error"),_('There is no included products!'))
        
        lines = []
       
        for x in contract.product_ids:
            if x.product_id:
                lines.append((0, 0, {'product_id': x.product_id.id,
                         'product_qty': x.quantity,
                         'product_uom_id': x.product_id.uom_id.id,
                         'name': x.product_id.name}),)
        
        if not lines:
            raise osv.except_osv(_("Error"),_('There is no included products!'))
        # cause all product are from the same category
        category = contract.product_ids[0].product_id.categ_id.id
        department = contract.department_id.id
        data = {'origin':contract.name, 'category_id': category,
                'department_id': department, 'line_ids': lines}
        created_id = self.pool.get('purchase.requisition').create(
            cr, uid, data, context=context)
        for line in lines:
            line[2]['purchase_requisition'] = created_id
        contract.write({'purchase_requisition':created_id})
        contract.vehicle_id.write({'purchase_requisitions':lines})

    def transfer(self, cr, uid, ids, context=None, costIds = None):
        """
        Transfer cost of contract generated cost to voucher.
        costIds : if you want to transfer specific cost
        """
        contract = self.pool.get('fleet.vehicle.log.contract')
        for con in contract.browse(cr, uid,ids, context=context):
            account = self.pool.get('admin_affairs.account').search(cr, uid, [('model_id','=','fleet.vehicle.log.contract'),('service_id','=',con.cost_subtype_id.id)])#Contract information on a vehicle
            if len(account) == 0:
                raise osv.except_osv(_("Configuration Error"),_('There Is No Configuration For Contracts Accounting!'))
            else:
                account_id = self.pool.get('admin_affairs.account').browse(cr, uid,account, context=context)[0]
            cost = 0
            if con.payment_method == 'voucher':
                sub_lines = []
                tax_id = []
                types = ""
                voucher_lines = ""
                for tax in con.tax_ids:
                    tax_id.insert(0,tax.id)

                for cost_id in con.generated_cost_ids:
                    if not cost_id.voucher_id and cost_id.state == "gmanager":
                        if costIds:
                            if cost_id.id in costIds:
                                cost += cost_id.amount
                        if not costIds:
                            cost += cost_id.amount
                
                types=account_id.journal_id.type
                voucher_lines="line_dr_ids"
                if (con.rent==True):
                    types="sale"
                    voucher_lines="line_cr_ids"
                
                if cost > 0 :
                    data = {
                        "type":types,
                        "partner_id":con.insurer_id.id,
                        "account_id":int(account_id.account_id.id),
                        "reference":con.ins_ref and con.ins_ref+""+con.name and con.name,
                        "company_id":con.company_id.id,
                        "date":date.today(),
                        "journal_id":int(account_id.journal_id.id),
                        'amount' : cost,
                        voucher_lines:[(0,0,{
                                    'amount': cost,
                                    'date_original': date.today(),
                                    "account_id":int(account_id.account_id.id),
                                    "account_analytic_id":(account_id.analytic_id and account_id.analytic_id.id) or (con.department_id and (con.department_id.analytic_account_id and con.department_id.analytic_account_id.id) or False),
                                    'name': con.cat_subtype,
                                    'tax_ids':tax_id})],
                        }
                    acount_voucher = self.pool.get('account.voucher')
                    v_id = acount_voucher.create(cr, uid, data, context=context)
                    copy_attachments(self,cr,uid,[con.id],'fleet.vehicle.log.contract',v_id,'account.voucher', context=context)
                    
                    ids_costs = [x.id for x in con.generated_cost_ids]
                    obj_cost= self.pool.get('fleet.vehicle.cost')
                    obj_cost.write(cr, uid,ids_costs,{'voucher_id':v_id}, context=context)
                    
            if cost <= 0 :
                raise osv.except_osv(_(""),_('There Is No Record To Transfer!'))

    def confirm_so(self, cr, uid, ids, context=None):
        """
        change state of contract To confirm service officer.

        @return: write state
        """
        for record in self.browse(cr, uid, ids,context=context):
            if record.payment_method =='enrich' and record.sum_cost > 0 and record.enrich_id.residual_amount < record.sum_cost:
                    raise osv.except_osv(_(""),_('No Enough Money In The Enrich!'))
        
        if 'cat_subtype' in context and context['cat_subtype'] in ['hospitality']:
            return self.write(cr, uid, ids, {'state':'open'}, context=context)
        
        if 'cat_subtype' in context and context['cat_subtype'] in ['hall']:
            if 'internal' in context and context['internal']:
                return self.write(cr, uid, ids, {'state':'open'}, context=context)
                    
        return self.write(cr, uid, ids, {'state':'confirm_so'}, context=context)

    def draft(self, cr, uid, ids, context=None):
        """
        Set state of contract To draft.

        @return: write state
        """
        #draft all hall registration linked with this contract
        holl_availability =self.pool.get("service.hall_availability")
        deleted_ids = holl_availability.search(cr,uid,[('contract_id', 'in', ids)],context=context)
        holl_availability.write(cr,uid,deleted_ids,{'state':'draft'},context=context)
        return self.write(cr, uid, ids, {'state':'draft'}, context=context)

    def confirm_sm(self, cr, uid, ids, context=None):
        """
        Change state of contract To service manager.

        @return: write state
        """
        return self.write(cr, uid, ids, {'state':'confirm_sm'}, context=context)

    def confirm_ss(self, cr, uid, ids, context=None):
        """
        Change state of contract To service section.

        @return: write state
        """
        next_state = "confirm_ss"
        if 'cat_subtype' in context and context['cat_subtype'] in ['hospitality']:
            next_state = "confirm_hs"
            self.general_mg(cr, uid, ids, context=context)
        vehicle_id = self.read(cr, uid, ids,['vehicle_id'])[0]['vehicle_id']
        vehicle_id = vehicle_id and vehicle_id[0] or None
        vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context=context)
        owns = vehicle.ownership
        

        if ((owns == 'owned') or (owns == 'rented')):
            return self.write(cr, uid, ids, {'state':next_state, 'car_type': owns}, context=context)
        else:
            return self.write(cr, uid, ids, {'state':next_state}, context=context)


    def closed(self, cr, uid, ids, context=None):
        """
        Change state of contract To closed.

        @return: write state
        """
        return self.write(cr, uid, ids, {'state':'closed'}, context=context)
        
    ###########################################################################
    #building
    ###########################################################################
    def fill_inventory(self, cr, uid, ids, context=None):
        """ To Import stock inventory according to products available in the selected locations.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}
        ids = ids[0]
        contract = self.browse(cr, uid, ids, context=context)
        res = {}
        if contract.building_id.child_ids:
            list_lines = []
            for item in contract.building_id.child_ids:
                line = item.read()[0]
                line['amount'] = line['cost']
                line['cost_subtype_id'] = line['id']
                list_lines.append((0,0,line))
            self.write(cr,uid,ids,{'cost_ids':None})
            lines_ids =  [item.id for item in self.browse(cr,uid,ids,context).cost_ids]
            self.pool.get('fleet.vehicle.cost').unlink(cr,uid,lines_ids,context)
            return self.write(cr,uid,ids,{'cost_ids':list_lines})

    def fill_product(self, cr, uid, ids, context=None):
        """ To Import stock inventory according to products available in the selected locations.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        ids = ids[0]
        contract = self.browse(cr, uid, ids, context=context)
        res = {}
        datas = {}
        location_ids = []
        if contract.building_id.location_id:
            location_ids = [contract.building_id.location_id.id]
        for location in location_ids:
            res[location] = {}
            move_ids = move_obj.search(cr, uid, ['|',('location_dest_id','=',location),('location_id','=',location),('state','=','done')], context=context)
            local_context = dict(context)
            local_context['raise-exception'] = False
            for move in move_obj.browse(cr, uid, move_ids, context=context):
                prod_id = move.product_id.id
                if move.location_dest_id.id != move.location_id.id:
                    if move.location_dest_id.id == location:
                        qty = uom_obj._compute_qty_obj(cr, uid, move.product_uom,move.product_qty, move.product_id.uom_id, context=local_context)
                    else:
                        qty = -uom_obj._compute_qty_obj(cr, uid, move.product_uom,move.product_qty, move.product_id.uom_id, context=local_context)
                    if datas.get(prod_id):
                        qty += datas[prod_id]['quantity']
                    datas[prod_id] = {'product_id':prod_id,'quantity': qty,'amount':move.product_id.standard_price}
            if datas:
                res[location] = datas
            list_lines = [(0,0,item) for item in datas.values()]
            self.write(cr,uid,ids,{'location_id':location,'cost_product':None})
            lines_ids =  [item.id for item in self.browse(cr,uid,ids,context).cost_product]
            self.pool.get('fleet.vehicle.cost').unlink(cr,uid,lines_ids,context)
            return self.write(cr,uid,ids,{'cost_product':list_lines})

    def request_product(self, cr, uid, ids, context=None):
        for contract in self.browse(cr,uid,ids,context=context):
            location_id = contract.building_id.location_id.id
            products = []
            have_product = False
            department_id = contract.department_id.id
            for item in contract.cost_product:
                if item.product_id:
                    names = '/'
                    line = item.read(['quantity','name','product_id'])[0]
                    if contract.name:
                        names = contract.name
                    line['product_id']  = line['product_id'][0]
                    line['product_qty'] = line['quantity']
                    line['name'] = names
                    line['location_id'] = location_id   
                    line['location_dest_id'] = location_id

                    category_id  = item.product_id.categ_id.id
                    unit = item.product_id.uom_id.id
                    line.update({'product_uom':unit})
                    products.append((0,0,line))
                    have_product = True
        if have_product:
            stock_picking_out = self.pool.get("stock.picking.out")
            data={
            'category_id':category_id,
            'move_lines':products,
            'department_id':department_id,
            }
            stock_id = stock_picking_out.create(cr,uid,data,context=context)
            old_stock_ids = self.read(cr, uid, ids, ['stock_id'], context=context)[0]['stock_id']

            stock_picking_out.unlink(cr, uid, old_stock_ids and [old_stock_ids[0]] or [], context=context)
            self.write(cr, uid, ids, {'stock_id':stock_id}, context=context)
            return True
    ############################################################################################
    #insurance contract
    ############################################################################################
    def department_vehicle(self,cr,uid,ids,context=None):
        if ids:
            contract = self.browse(cr,uid,ids[0],context=context)
            vehicles_ids = self.pool.get("fleet.vehicle").search(cr,uid,[('status','=','active'),('ownership','=','owned')],context=context)
            List = []
            for vehicle in self.pool.get("fleet.vehicle").browse(cr,uid,vehicles_ids,context=context):
                List.append((0,0,{'vehicle_id':vehicle.id,'amount':vehicle.car_value,'auto_generated':True,'activation':True,'cost_type':'insurance'}))

            old_List = [service.id for service in contract.cost_ids]
            self.pool.get('fleet.vehicle.cost').unlink(cr,uid,old_List,context)
            contract.write({'cost_ids':None})
            contract.write({'cost_ids':List})
        return True

    
    def to_legal(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'legal'}, context=context)
    



class fleet_service_type(osv.osv):
    """
    Manage and customize fleet service types.
    """
    _inherit='fleet.service.type'

    def onchange_child_ids(self,cr,uid,ids,child_ids,context=None):
        sum_cost = 0
        list_ids = []
        for item in child_ids:
            if item[2]:
                sum_cost+=item[2]['cost']
            if item[2] == False and item[0] == 4:
                list_ids.append(item[1])
        for rc in self.browse(cr,uid,list_ids,context=context):
            sum_cost += rc.cost
        return {
        'value': {
                'cost':sum_cost,}
                }

    def onchange_free(self,cr,uid,ids,cost,is_free,context=None):
        temp = cost
        if is_free:
            temp = 0
        return {
        'value': {
                'cost':temp,}
                }

    _columns = {
        'name': fields.char('Name', required=True, translate=True),
        'parent_id': fields.many2one('fleet.service.type', string='Parent'),
        'category': fields.selection([('contract', 'Maintenance'), ('service', 'Service'), ('both', 'Vehicle Request'),
                                      ('env_safety', 'Environment & Safety'),('hospitality','Hospitality'),
                                      ('occasion','Occasion'),('hall','Hall'),('building','Building'),('media','Media'),
                                      ('public_relation','Public Relation'),('general','General'),
                                      ('insurance','Vehicle Insurance'),('license','Vehicle License')], 'Category',required=True),
        'cost': fields.float(string="Cost"),
        'building': fields.boolean('Building'),
        'quantity':fields.float("Quantity"),
        'active':fields.boolean('Active'),
        'child_ids': fields.one2many('fleet.service.type', 'parent_id', 'Items'),
        'location_id': fields.many2one('stock.location', string='Location'),
        'address': fields.char('Address',),
        'time_to_request': fields.integer('Hours To Request',),
        'users': fields.many2many('hr.employee',string = 'Users'),
        'hall_type': fields.many2many( 'service.hall.type',string='Types'),
        'is_free':fields.boolean('Free'),
        'price': fields.float(string='Price'),
        'linked_to_hall': fields.many2many('fleet.service.type', 'linked_to_hall_rel','current_hall', 'linked_hall', string='Linked'),
    }
    _defaults = {
        'building':lambda self, cr, uid, c: c.get('building', False),
        'category':lambda self, cr, uid, c: c.get('category', False),
        'active':True,
        'quantity': 1.0,
    }


class admin_affairs_account_custom(osv.osv):
    """
    Customize admin affairs account.
    """
    _inherit='admin_affairs.account'

    _columns = {
        'service_id': fields.many2one('fleet.service.type','Service'),
    }

    _sql_constraints = [
        ('model_uniq', 'unique(model_id,service_id)', _('Service Must Be Unique For Each Model!')),
    ]


class fleet_model_custom(osv.osv):
    """
    Customize fleet vehicle model.
    """
    _inherit='fleet.vehicle.model'

    _sql_constraints = [
        ('model_uniq', 'unique(modelname,brand_id)', _('Model must be unique!')),
    ]

class fleet_model_brand_custom(osv.osv):
    """
    Customize fleet vehicle model brand.
    """
    _inherit='fleet.vehicle.model.brand'

    def _check_unique_insesitive(self, cr, uid, ids, context={}):
        """
        Check uniqueness of product name.

        @return: Boolean of True or False
        """
        name = self.browse(cr, uid, ids[0], context=context).name
        if len(self.search(cr, uid, [('name','=ilike',name)],  context=context)) > 1:
            raise osv.except_osv(_('Constraint Error'), _("Brand Name Must Be Unique!"))
        return True

    _constraints = [
        (_check_unique_insesitive, _(''), [''])
    ]


class fleet_vehicle(osv.osv):
    """
    Customize fleet vehicle.
    """
    _inherit='fleet.vehicle'

    _columns = {
        'expected_odometer':fields.float(string="Expected odometer"),
        'next_maintenance_date':fields.date(string="Next Maintenance"),
        'type': fields.many2one('vehicle.category', string='Type',required=True),
        'purchase_requisitions': fields.one2many('vehicle.maintenance.purchase','vehicle_id', string='Purchase Requisitions'),
    }
    def _check_negative(self, cr, uid, ids, context=None):
        """
        Check the value of amount, cost_generated and odometer,
        if greater than zero or not.

        @return: Boolean of True or False
        """
        count = 0
        for act in self.browse(cr, uid, ids, context):
            message = _("The Value Of ")
            if (act.expected_odometer < 0):
                message = message + _("Expected Odometer")
                count = count + 1
            message = message + _(" Must Be Positive Value!")
        if count > 0 :
            raise osv.except_osv(_(''), _(message))
        return True
    _constraints = [
        (_check_negative, _(''), [''])
    ]

class payment_enrich_custom(osv.osv):
    """ To manage admin affairs payment """
    _inherit = "payment.enrich"

    _columns = {
        'service_id': fields.many2one('fleet.service.type','Service'),
    }


class payment_enrich_lines_custom(osv.osv):
    """ To manage admin affairs payment lines """
    _inherit = "payment.enrich.lines"

    _columns = {
        'service_id': fields.many2one('fleet.service.type','Service'),
    }

class admin_affairs_payment_roof(osv.osv):
    """To manage admin affairs payment roof """
    _inherit = "admin.affairs.payment.roof"

    _columns = {
        'service_id': fields.many2one('fleet.service.type','Service'),
        'name': fields.selection([('affairs_mg','Admin Affairs Manager'),('human_financial',
            'human resources and financial Manager'),('general_mg','General Manager'),],'Name',required=True),
    }
    _sql_constraints = [
        ('model_uniq', 'unique(name,model_id,service_id)', _('The Model Must Be Unique For Each Name!')),
    ]

class hall_availability(osv.osv):
    _name = "service.hall_availability" 
    rec_name="string"
    _columns = {
        'contract_id':fields.many2one('fleet.vehicle.log.contract', 'Contract', readonly=True,invisible=True),
        'hall_id':fields.many2one('fleet.service.type', 'Hall'),
        'weekday':fields.char('Weekday', readonly=True),
        'name': fields.char('Name',readonly=True),
        'date_stop':fields.datetime('End Time'),
        'date_start':fields.datetime('Start Time'),
        'state':fields.selection([('draft','draft'),('cancel','cancel')],'State'),
        'hall_reg_type':fields.related('contract_id','hall_reg_type',type='char',string='Hall Registration Type'),
        'insurer_id':fields.related('contract_id','insurer_id',type='many2one',string='Partner',relation='res.partner'),
        'department_id':fields.related('contract_id','department_id',type='many2one',string='Department',relation='hr.department'),
    }

    _defaults={
        'state':'draft',
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='calendar', context=None, toolbar=False, submenu=False):
        if not context:
            context = {}
        res = super(hall_availability, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        return res

    def read(self, cr, user, ids, fields=None, context=None, load='_classic_read'):
        res = super(hall_availability,self).read(cr, user, ids, fields=fields, context=context, load=load)
        if context:
            weekdays = {'monday':'اﻹثنين', 'tuesday':"الثلاثاء", 'wednesday':"الأربعاء", 'thursday':"الخميس", 'friday':"الجمعة",'saturday':"السبت", 'sunday':"الأحد"} 
            #for add and supscarbt of time in hall registration
            if 'hall_rgistrations' in context:
                for rec in res:
                   start = rec['date_start'] 
                   start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                   start += relativedelta(minutes=30)
                   rec['date_start'] = str(start)

                   end = rec['date_stop'] 
                   end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                   end -= relativedelta(minutes=30)
                   rec['date_stop'] = str(end)

                   rec['weekday'] = weekdays.get(rec['weekday'],rec['weekday'])
        return res

    def _compare(self,i,l2):
        for o in l2:
            if o[0] >=  i[0]:
                if o[0] < i[1]:
                    return True
            if i[0] >=  o[0]:
                if i[0] < o[1]:
                    return True

        return False
    
    def to_datetime(self, stri):
        return datetime.strptime(stri, "%Y-%m-%d %H:%M:%S")

    def cancel_reg(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancel'}, context=context)
    
    def draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'draft'}, context=context)

    def _check_founded(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            date_start = record.date_start
            date_stop = record.date_stop
            hall_id = record.hall_id.id
            contract_id = record.contract_id.id
            hall_linked = []
            #hall_linked.append( hall_id )
            service_type = self.pool.get('fleet.service.type')
            def get_ids(inner_hall_id):
                if inner_hall_id in hall_linked:
                    return
                hall_linked.append( inner_hall_id )
                for new_id in service_type.read(cr, uid, inner_hall_id,['linked_to_hall'])['linked_to_hall']:
                    get_ids(new_id)
            
            get_ids(hall_id)

            founded_ids = self.search(cr, uid,[('hall_id','in',hall_linked),('id','!=',record.id),('state','=','draft')],context=context)
            other_times = self.read(cr,uid, founded_ids,['date_start','date_stop'], context=context)
            other_times = [(x['date_start'],x['date_stop']) for x in other_times]
            other_times = [( self.to_datetime(x[0]), self.to_datetime(x[1]) ) for x in other_times]
            current_time = [self.to_datetime(date_start), self.to_datetime(date_stop)]
            founded = False
            for time in other_times:
                if self._compare(current_time,other_times):
                    founded = True
                    raise osv.except_osv(_('Error'), _('This Hall is reserved at this time'))
            return True

    _constraints = [
        (_check_founded, '', ['date_start','date_stop','state','hall_id']),
    ]



class hall_type(osv.osv):
    _name='service.hall.type'

    _columns = {
        'name': fields.char('Type'),
        'capacity': fields.integer('Capacity'),
    }

    _sql_constraints = [
        ('model_uniq', 'unique(name)', _('Type name must be unique!')),
    ]


class faults_solution_category(osv.osv):
    _name='faults.solution.category'
    rec_name='name'
    _columns = {
        'name': fields.char('Name'),
        'specific_user':fields.boolean('For Specific User'),
        'users': fields.many2many('hr.employee',string = 'Users'),
    }
    _sql_constraints=[
        ('model_uniq', 'unique(name)', _('name must be unique!')),
    ]




class building_maintenance_faults_solution(osv.osv):
    _name='building.maintenance.faults.solution'
    rec_name='name'
    _columns = {
        'name': fields.char('Name'),
        'responsible':fields.many2many('hr.employee',string='Responsible'),
        'priority':fields.selection([('low','Low'),('normal','Normal'),('high','High')],string='Priority'),
        'description': fields.char('Description'),
        'type':fields.selection([('fault','Fault'),('solution','Solution'),],string='Type'),
        'category_id': fields.many2one('faults.solution.category',string='Category'),
    }
    _sql_constraints=[
        ('model_uniq', 'unique(name,type)', _('name must be unique!')),
    ]

class vehicle_maintenance_purchase(osv.osv):
    _name='vehicle.maintenance.purchase'
    rec_name='name'
    _columns = {
        'purchase_requisition': fields.many2one('purchase.requisition',string='Purchase Requisition'),
        'product_id': fields.many2one('product.product',string='Product'),
        'product_qty':fields.float(string='Quantity'),
        'price': fields.related('product_id','standard_price',type='float',string='Unit Price'),
        'product_uom_id':fields.related('product_id','uom_id',type='many2one',string='Unit of Measure',relation='product.uom'),
        'vehicle_id': fields.many2one('fleet.vehicle', string='Vehicle'),
    }



class product_product(osv.Model):
    _inherit = "product.product"

    _columns = {
        'is_admin_affaris':fields.boolean('Is admin affaris Item'),
    }

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        List = []
        products = []            
        if 'maintenance_products' in context:
            for i in context['maintenance_products']:
                if not i[1] :
                    products.append(i[2]['product_id'])
                else:
                    List.append(i[1])

            List = filter(lambda x : x != False,List)

            for line in self.pool.get("fleet.vehicle.cost").browse(cr,uid,List,context=context):
                products.append(line.product_id.id)
            args.append(('id', 'not in', products))

        return super(product_product, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)

class hall_reg_type(osv.Model):
    _name='hall.reg.type'

    _columns = {
        'name':fields.char('Name'),
    }

"""class account_voucher(osv.Model):
    _inherit = "account.voucher"
    def proforma_voucher_custom_admin(self, cr, uid, ids, context=None):
        self.action_move_line_create_custom_admin(cr, uid, ids, context=context)
        return True
    
    def action_move_line_create_custom_admin(self, cr, uid, ids, context=None):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            local_context = dict(context, force_company=voucher.journal_id.company_id.id)
            if voucher.move_id:
                continue
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            # we select the context to use accordingly if it's a multicurrency case or not
            context = self._sel_context(cr, uid, voucher.id, context)
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = context.copy()
            ctx.update({'date': voucher.date})
            # Create the account move record.
            move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
            
            # Get the name of the account_move just created
            name = move_pool.browse(cr, uid, move_id, context=context).name

            # Create the first line of the voucher
            move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, local_context), local_context)
            move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
            line_total = move_line_brw.debit - move_line_brw.credit
            rec_list_ids = []
            if voucher.type == 'sale':
                line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            elif voucher.type == 'purchase':
                line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            # Create one move line per voucher line where amount is not 0.0
            line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)

            # Create the writeoff line if needed
            ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, local_context)
            if ml_writeoff:
                move_line_pool.create(cr, uid, ml_writeoff, local_context)
            '''# We post the voucher.
            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            if voucher.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context={})
            # We automatically reconcile the account move lines.
            reconcile = False
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)'''
        return True"""
