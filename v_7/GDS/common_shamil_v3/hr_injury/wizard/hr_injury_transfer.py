# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from mx import DateTime
import time
from datetime import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import netsvc
import openerp.addons.decimal_precision as dp




#----------------------------------------
#transfer accounts 
#----------------------------------------
class hr_transfer_account(osv.osv_memory):
    _name = 'hr.transfer.account'
    _columns = {
                 'type':fields.selection([('treatment', 'Treatment'), ('compensation', 'Compensation'),('all', 'All')],'Type',required="1"),

                }

    def transfer(self, cr, uid, ids, context={}):
       """
       Method that transfers employee injury from injury form to acounting voucher.

       @return: dictionary of action to close wizard 
       """
       if not context:
           context = {}
       emp_injury_obj = self.pool.get('hr.injury')
       emp_injury_id = context.get('active_id', False)
       injury = emp_injury_obj.browse(cr, uid, emp_injury_id, context=context)
       data = self.browse(cr, uid, ids[0], context=context)
       hr_setting = self.pool.get('hr.config.settings')
       config_ids=hr_setting.search(cr,uid,[])
       config_browse=hr_setting.browse(cr, uid, config_ids)
       lines=[]
       date = time.strftime('%Y-%m-%d')
       reference = 'HR/Employee Injury/ '+" / "+str(injury.injury_date)
       ttype=data.type
       if ttype == 'compensation':
          if not injury.compensation_transfer:
             if injury.inability_amount > 0.0:            
                if config_browse[0].hr_journal_id and injury.department_id.analytic_account_id and config_browse[0].treatment_account_id:
                   compensation_dict={'account_id': config_browse[0].treatment_account_id.id,'amount': injury.inability_amount,}
                   lines.append(compensation_dict) 
	           voucher=self.pool.get('payroll').create_payment(cr, uid, ids,{'reference':reference,'lines':lines},context=context)
		   emp_injury_obj.write(cr, uid, [emp_injury_id], {'inability_acc_number':voucher, 'compensation_transfer':True, }, context=context)
                else:
                   raise osv.except_osv(_('ERROR'), _('Please enter account,journal and analytic account'))
             else:
                raise osv.except_osv(_('ERROR'), _('Please enter amount for inability amount'))
          else:
             raise osv.except_osv(_('ERROR'), _('the amount already transfered'))
       elif ttype == 'treatment':
          if not injury.transfer:
             if injury.treatment_amount > 0.0 :            
                if config_browse[0].hr_journal_id and injury.department_id.analytic_account_id and config_browse[0].treatment_account_id:
                   treatment_dict={'account_id': config_browse[0].treatment_account_id.id,'amount': injury.treatment_amount,}
                   lines.append(treatment_dict) 
	           voucher=self.pool.get('payroll').create_payment(cr, uid, ids,{'reference':reference,'lines':lines},context=context)
		   emp_injury_obj.write(cr, uid, [emp_injury_id], {'acc_number':voucher, 'transfer':True, }, context=context)
                else :
                   raise osv.except_osv(_('ERROR'), _('Please enter account,journal and analytic account'))
             else:
                raise osv.except_osv(_('ERROR'), _('Please enter amount for treatment'))
          else:
             raise osv.except_osv(_('ERROR'), _('the amount already transfered'))
       elif ttype == 'all':
          if not injury.transfer and not injury.compensation_transfer:
             if injury.treatment_amount > 0.0 and injury.inability_amount > 0.0:
                if config_browse[0].hr_journal_id and injury.department_id.analytic_account_id and config_browse[0].treatment_account_id:
                   both_dict={'account_id': config_browse[0].treatment_account_id.id,'amount': injury.inability_amount +injury.treatment_amount ,}
                   lines.append(both_dict) 
	           voucher=self.pool.get('payroll').create_payment(cr, uid, ids,{'reference':reference,'lines':lines},context=context)
		   emp_injury_obj.write(cr, uid, [emp_injury_id], {'acc_number':voucher, 'transfer':True,'inability_acc_number':voucher, 'compensation_transfer':True }, context=context)
                else:
                   raise osv.except_osv(_('ERROR'), _('Please enter account,journal and analytic account'))
             else:
                raise osv.except_osv(_('ERROR'), _('Please check amount for treatment or compensation '))
          else:
             raise osv.except_osv(_('ERROR'), _('the amount already transfered'))
       return {'type': 'ir.actions.act_window_close'}

   
