# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
from fleet import fleet


class vehicle_maintenance_purchase_wizard(osv.osv_memory):
    """
    To manage vehicle maintenance purchase orders operation
    """
    _name = "vehicle.maintenance.purchase.wizard"

    _description = "Vehicle maintenance purchase wizard"

    def purchase_order(self, cr, uid, ids, context=None):
        """ 
        create purchase order for selected contract(s).

        @return: Dictionary that close the wizard
        """
        contract_obj = self.pool.get('fleet.vehicle.log.contract')
        vals = {}
        vehicles_vals={}
        
        #ids of all processed contracts 
        contracts_ids = []
        all_product_id = False
        for contract in contract_obj.browse(cr, uid, context.get('active_ids'), context):
            if contract.state == 'confirm_sm' and contract.cat_subtype == 'contract' and not (contract.purchase_requisition):
                #for the current contract
                product_id = False
                lines = []

                for service in contract.product_ids:
                    if service.product_id:
                        #for the current contract
                        product_id = service.product_id
                        
                        #for all contracts
                        all_product_id = product_id

                        vals[service.product_id.id] = vals.get(service.product_id.id,{
                            'product_qty':0,
                            'name':''
                        })
                        vals[service.product_id.id]['product_id'] = service.product_id.id
                        vals[service.product_id.id]['product_qty'] += service.quantity
                        vals[service.product_id.id]['product_uom_id'] = service.product_id.uom_id.id
                        vals[service.product_id.id]['name'] += "/"+service.product_id.name
                        #for the current contract
                        lines.append((0, 0, {'product_id': service.product_id.id,
                         'product_qty': service.quantity,
                         'product_uom_id': service.product_id.uom_id.id,
                         'name': service.product_id.name}),)
                        
                if lines:
                    category = product_id.categ_id.id
                    department = contract.department_id.id
                    data = {'origin':contract.name, 'category_id': category,
                            'department_id': department, 'line_ids': lines}
                    
                    vehicles_vals[contract.id, contract.vehicle_id.id]=data
                    contracts_ids.append(contract.id)

        if vals:
            data= [(0,0,x) for x in vals.values()]

            #get the department of the current user
            category = all_product_id.categ_id.id
            department = self.pool.get('hr.employee').read(cr, uid, uid,['department_id'],
            context=context)['department_id'][0]
            
            all_data = {'origin':'vehicles maintenance contracts', 'category_id': category,
                    'department_id': department, 'line_ids': data}
            
            created_id = self.pool.get('purchase.requisition').create(
                cr, uid, all_data, context=context)
            
            #write the purchase lines in contracts
            contract_obj.write(cr, uid, contracts_ids, {'purchase_requisition':created_id})

            #write the purchase lines in vehicles
            for vehicle in vehicles_vals:
                for line in vehicles_vals[vehicle]['line_ids']:
                    line[2]['purchase_requisition'] = created_id
                self.pool.get('fleet.vehicle').write(cr, uid, [vehicle[1]], {'purchase_requisitions':vehicles_vals[vehicle]['line_ids']}, context=context)

        if not vals:
            raise osv.except_osv(_("Error"),_('There is no product to purchase!'))
        