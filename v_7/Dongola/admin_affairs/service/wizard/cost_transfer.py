# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from datetime import date,datetime
from openerp.osv import osv, fields
from openerp.tools.translate import _
from admin_affairs.model.copy_attachments import copy_attachments_set

class cost_transfar(osv.osv_memory):
    """ To manage Transfer services cost operation """
    _name = "fleet.vehicle.log.services.cost.transfer"

    _description = "Rented Cars Report"

    _columns = {
        'start_date':fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'company_id': fields.many2one('res.company',string='Company', required=True),
        'deparment_ids':fields.many2many('hr.department',string='Departments',required=True),
        'insurer_ids':fields.many2many('res.partner',string = 'Insurers',required=True),
        'service_ids': fields.many2many('fleet.service.type','services_cost_transfer',strint='Service',required=True),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'fleet.vehicle.log.services.cost.transfer', context=c),
    }

    def transfer(self, cr, uid, ids, context=None):
        """ 
        Create voucher for all lines in services generated cost.
        """
        contract = self.pool.get('fleet.vehicle.log.contract')
        acount_voucher=self.pool.get('account.voucher')
        obj_cost= self.pool.get('fleet.vehicle.cost')
        domain_date =[]
        flag=True
        for transfer in self.browse(cr, uid, ids, context=context):
            service_ids = [x.id for x in transfer.service_ids]
            start_dat = datetime.strptime(transfer.start_date, "%Y-%m-%d")
            end_dat = datetime.strptime(transfer.end_date, "%Y-%m-%d")
            if start_dat and end_dat and start_dat > end_dat:
                raise osv.except_osv(_("ValidateError"),_('Start Date Must Be Less Than End Date!'))

            company_id = transfer.company_id
            deparment_id = [d.id for d in transfer.deparment_ids]
            insurer_ids = [i.id for i in transfer.insurer_ids] or self.pool.get('res.partner').search(cr, uid, [], context=context)

            
            account = self.pool.get('admin_affairs.account').search(cr, uid, [('model_id','=','fleet.vehicle.log.contract'),
                                                                                  ('service_id','in',service_ids)],
                                                                        context=context)#Contract information on a vehicle
            if len(account) == 0:
                raise osv.except_osv(_("Configuration Error"),_('There Is No Configuration For Contracts Accounting!'))
            
            
            for account_id in self.pool.get('admin_affairs.account').browse(cr, uid, account, context=context):

                types=account_id.journal_id.type

                for insurer in insurer_ids:
                    sum_cost_dr = 0
                    sum_cost_cr = 0
                    sub_lines_dr = []
                    sub_lines_cr = []
                    ids_dr = []
                    ids_cr = []
                    contract_ids_dr = []
                    contract_ids_cr = []
                    

                    domain = [('payment_method','=', 'voucher' ),('insurer_id','=',insurer),
                            ('company_id','=',transfer.company_id.id),('cost_subtype_id','=',account_id.service_id.id)]
                    if deparment_id:
                        domain += [('department_id','in',deparment_id)]
                    cont_ids = contract.search(cr, uid, domain, context=context)
                    #if  contracts:
                    for contracts in contract.browse(cr, uid, cont_ids, context=context):
                        domain_date=[('contract_id', '=', contracts.id), ('state', '=', 'gmanager'), ('voucher_id', '=', None)]
                        v_ids = obj_cost.search(cr, uid, domain_date, context=context)
                        allcost = 0
                        for record in obj_cost.browse(cr, uid, v_ids, context=context):
                            current_date = datetime.strptime(record.date, "%Y-%m-%d")
                            if current_date >= start_dat and current_date <= end_dat:
                                allcost += record.amount
                        if allcost > 0 :
                            flag=False
                            if (contracts.rent==True): 
                                for i in v_ids:
                                    ids_cr.append(i)
                                contract_ids_cr.append(contracts.id)
                                sum_cost_cr += allcost
                                sub_lines_cr.append((0,0,{
                                    'amount': allcost,
                                    'date_original': date.today(),
                                    "account_id":int(account_id.account_id.id),
                                    'account_analytic_id ': int(account_id.analytic_id.id),
                                    "account_analytic_id":(account_id.analytic_id and account_id.analytic_id.id) or (contracts.department_id and (contracts.department_id.analytic_account_id and contracts.department_id.analytic_account_id.id) or False),
                                    'name': contracts.name,
                                    'tax_ids':[(6, 0, [t.id for t in contracts.tax_ids])] 
                                }))
                            if (contracts.rent==False): 
                                for i in v_ids:
                                    ids_dr.append(i)
                                contract_ids_dr.append(contracts.id)
                                sum_cost_dr += allcost
                                sub_lines_dr.append((0,0,{
                                    'amount': allcost,
                                    'date_original': date.today(),
                                    "account_id":int(account_id.account_id.id),
                                    'account_analytic_id ': int(account_id.analytic_id.id),
                                    "account_analytic_id":(account_id.analytic_id and account_id.analytic_id.id) or (contracts.department_id and (contracts.department_id.analytic_account_id and contracts.department_id.analytic_account_id.id) or False),
                                    'name': contracts.name,
                                    'tax_ids':[(6, 0, [t.id for t in contracts.tax_ids])] 
                                }))
                    if sum_cost_dr > 0:
                        v_id=acount_voucher.create(cr, uid,{"type":types,
                                                            "partner_id":insurer,
                                                            "account_id":int(account_id.account_id.id),
                                                            "company_id":company_id.id,
                                                            "date":date.today(),
                                                            "journal_id":int(account_id.journal_id.id),
                                                            "line_dr_ids":sub_lines_dr,
                                                            "amount":sum_cost_dr,
                                                            }, context=context)
                       
                        copy_attachments_set(self,cr,uid,contract_ids_dr,'fleet.vehicle.log.contract',v_id,'account.voucher', context=context)
                        obj_cost.write(cr, uid,ids_dr,{'voucher_id':v_id}, context=context)
                    
                    if sum_cost_cr > 0:
                        v_id=acount_voucher.create(cr, uid,{"type":types,
                                                            "partner_id":insurer,
                                                            "account_id":int(account_id.account_id.id),
                                                            "company_id":company_id.id,
                                                            "date":date.today(),
                                                            "journal_id":int(account_id.journal_id.id),
                                                            "line_cr_ids":sub_lines_cr,
                                                            "amount":sum_cost_cr,
                                                            }, context=context)
                        
                        copy_attachments_set(self,cr,uid,contract_ids_cr,'fleet.vehicle.log.contract',v_id,'account.voucher', context=context)
                        obj_cost.write(cr, uid,ids_cr,{'voucher_id':v_id}, context=context)

        if flag:
            raise osv.except_osv(_("ValidateError"),_('There Is No Record To Transfer!'))


