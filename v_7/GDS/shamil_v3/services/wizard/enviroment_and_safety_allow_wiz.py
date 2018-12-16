# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields
import time
from datetime import timedelta,date , datetime
from openerp.tools.translate import _

#----------------------------------------
#enviroment_and_safety_allowances_wiz
#----------------------------------------
class rented_cars_allowances_archive_wiz(osv.osv_memory):     

    
    def _get_months(sel, cr, uid, context):
       """
       Method that returns months of year as numbers.
       @return: List Of tuple
       """
       months=[(n,n) for n in range(1,13)]
       return months

    _name = "service.contract.allowances.wiz"
    _description = "Service Contract Allowances Wizard"
    _columns = {
		 'company_id': fields.many2one('res.company', 'Company Name',required=True ),
		 'month': fields.selection(_get_months,'Month',required=True),
                 'year': fields.integer('Year',required=True),
   		 }
   
    _defaults = {
        'year': int(time.strftime('%Y')),
    }

    def compuete_allowances(self,cr,uid,ids,context={}):
           """
           Computes Service Contract allowances in specific month.
           @return: Boolean True 
           """
           enviroment_obj = self.pool.get('environment.and.safety')
           enviroment_allowances_obj = self.pool.get('services.contracts.archive')
           allowances_lines_obj = self.pool.get('services.contracts.allowances.lines')

       	   for record in self.browse(cr,uid,ids,context=context):
  		check_allowance = enviroment_allowances_obj.search(cr,uid,[('month','=',record.month),('year','=',record.year)],context=context)

                if check_allowance:
	      		raise osv.except_osv('ERROR', 'Enviroment and safety Allowances For This Month Already Computed')

           	first_date = datetime(year=record.year, month= int(record.month), day=1)
           	# Last Day of the Mont
                if first_date.month < 12:
            	    next_month = datetime(year=first_date.year, month=first_date.month+1, day=1)
		else:
            	    next_month = datetime(year=first_date.year+1, month=1, day=1)
            	last_day = next_month - timedelta(days=1)
          	contract_ids = enviroment_obj.search(cr,uid,[('company_id','=',record.company_id.id),(('date_of_return','<=',last_day) and ('date_of_return','>=',first_date)) or  
(('date_of_return','>=',last_day) and ('date_of_rent','<=',last_day )),('state','=','confirmed') ])
          	if not contract_ids:
             		raise osv.except_osv(_('Warning'), _("No Contracts to compute in this period or already computed "))
# Select for Partner that Satisfy the condition 
          	cr.execute("""SELECT distinct partner_id as partner_id from environment_and_safety where company_id =%s and state = 'confirmed' and (date_of_return <=%s and date_of_return >=%s) or 
		  (date_of_return>=%s and date_of_rent<=%s ) group by partner_id """,(record.company_id.id,last_day,first_date,last_day,last_day))
          	partner_res=cr.dictfetchall()
# Define
		date_diff = 0.0
		date_dedc = 0.0
		dedc_amount = 0.0
		amount_avg = 0.0
		tax_avg = 0.0
		total_tax = 0.0 
		total = 0.0
		total_untax = 0.0

          	if partner_res:
             		for partner in partner_res:
# select partner records
                		cr.execute("""SELECT distinct id as contract_id ,category_id as category_id, cost_of_contract as cost ,date_of_rent as start_date , date_of_return as end_date , amount_untaxed as amount_untaxed , amount_tax as tax ,amount_total as total from environment_and_safety where state ='confirmed' and partner_id =%s and date_of_return >= %s """,(partner['partner_id'],first_date))
                		res=cr.dictfetchall()
                		if res:

                   		  partner_archive_dict = enviroment_allowances_obj.create(cr, uid,{
			 'company_id' : record.company_id.id,
		         'partner_id' :partner['partner_id'],
		         'month': record.month,
		         'year': record.year,
		      			 })
               
				  for res_contract in res :
					contract_start = datetime.strptime(res_contract['start_date'],"%Y-%m-%d")
					contract_end = datetime.strptime(res_contract['end_date'],"%Y-%m-%d")
					wiz_diff = first_date - last_day
					wiz_total = 1 + abs(wiz_diff.days)
					amount_avg = round(res_contract['cost']/30,2)
					tax_avg = round (res_contract['tax']/30,2)
					if contract_start >=first_date and contract_end <=last_day :
						date_diff = contract_start - contract_end
				  		total_date = 1+ abs(date_diff.days)
						total_untax = amount_avg * total_date
				  		total = amount_avg * total_date  + tax_avg * total_date
						total_tax =  tax_avg * total_date 
				  		date_dedc = abs(wiz_total - total_date)
						dedc_amount = abs(res_contract['cost'] - total)
					if contract_start < first_date :
						if contract_end < last_day and contract_end >= first_date:
							date_diff = first_date - contract_end
				  			total_date = 1+ abs(date_diff.days)
							total_untax = amount_avg * total_date
				  			total = amount_avg * total_date  + tax_avg * total_date
							total_tax =  tax_avg * total_date 
				  			date_dedc = abs(wiz_total - total_date)
						        dedc_amount = abs(res_contract['cost'] - total)
						elif contract_end > last_day:
							date_diff = first_date - last_day
				  			total_date = 1+ abs(date_diff.days)
							total_untax = amount_avg * total_date
				  			total = amount_avg * total_date  + tax_avg * total_date
							total_tax =  tax_avg * total_date 
				  			date_dedc = abs(wiz_total - total_date)
						        dedc_amount = abs(res_contract['cost'] - total)
						elif contract_end == last_day :
							total = res_contract['total']
		         				total_untax = res_contract['amount_untaxed']
        		                        	total_tax = res_contract['tax']
							date_dedc = 0.0
							dedc_amount = 0.0
					if contract_start > first_date and contract_end > last_day:
						date_diff = contract_start - last_day
				  		total_date = 1+ abs(date_diff.days)
						total_untax = amount_avg * total_date
				  		total = amount_avg * total_date  + tax_avg * total_date
						total_tax =  tax_avg * total_date 
				  		date_dedc = abs(wiz_total - total_date)
						dedc_amount = abs(res_rent['cost'] - total)
					if(contract_start==first_date and contract_end==last_day)or(contract_start < first_date and contract_end > last_day):
						total = res_contract['total']
		         			total_untax = res_contract['amount_untaxed']
        		                        total_tax = res_contract['tax']
						date_dedc = 0.0
						dedc_amount = 0.0
                      			partner_allow_dict = {
			 					'env_allow_id_before_rate' : partner_archive_dict,
		         					'partner_id' :partner['partner_id'],
		         					'cost_of_rent':res_contract['cost'],
		         					'amount_untaxed':total_untax,
        		 					'amount_tax':total_tax,
        		 					'amount_total':total,
        		 					'deduct_days':date_dedc,
        		 					'deduct_amount':dedc_amount,
        		 					'contract_id': res_contract['contract_id'],	        		 						'category_id': res_contract['category_id'],
        		 					'type': 'before',
								'percentage_rating':100,
		      				    }
 			                allowances_lines_obj.create(cr, uid ,partner_allow_dict, context=context)
           return True
"""    def create_ratification(self,cr,uid,ids,context={}):
       Compute Rented Cars allowances per partner in specific company for specific time .
       @return: Dictionary 


       rented_cars_allowances_obj = self.pool.get('rented.cars.allowances.archive')
       allowances_lines_obj = self.pool.get('rented.cars.allowances.lines')
       voucher_obj = self.pool.get('account.voucher')
       voucher_line_obj = self.pool.get('account.voucher.line')
       account_period_obj = self.pool.get('account.period')
       for record in self.browse(cr,uid,ids,context=context):
          total_amount= 0.0
          allowances_ids = rented_cars_allowances_obj.search(cr,uid,[('month','=',record.month) and ('year','=',record.year) and ('transfer','=',False)])
          if not allowances_ids:
             raise osv.except_osv(_('Warning'), _("No Rented Cars to transfer, or already transfered "))
       #         allowances_lines_ids = allowances_lines_obj.search(cr,uid,[('rented_cars_allow_id','in',allowances_ids)])
      #     partner_ids = [allowances_line.partner_id.id for allowances_line in allowances_lines_obj.browse(cr,uid,allowances_lines_ids)]
          #make ids in tuple to used in query
         #  allowances_lines_ids = tuple(allowances_lines_ids)
          #remove the dublicate from partner ids
        #   partner_ids = list(set(partner_ids))
        #   if partner_ids:
         ##     for partner_id in partner_ids:
           #      total_amount= 0.0
          cr.execute("SELECT partner_id as partner_id , amount_total as total from rented_cars_allowances_archive where month=%s and year=%s",(record.month,record.year))
          res=cr.dictfetchall()
          for allowances_record in res:
                   voucher_dict={
                                 'company_id':record.company_id.id,
                                 'name': 'Rented/Car/'  + ' - ' + str(record.month) + ' - ' + str(record.year),
                                 'type':'ratification',
                                 'reference':'Rented/Car/' ,
                                 'partner_id' : allowances_record['partner_id'],
                                 'narration' : '/'
                     }
                   voucher = voucher_obj.create(cr, uid, voucher_dict, context=context)
# creating Voucher lines 
                   voucher_line_dict = {
                             'voucher_id':voucher,
#                             'account_analytic_id':dept['analytic'],
                             'amount':allowances_record['total'],
                             'type':'dr',
#                             'name': dept['name'],
                               }
                   voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
                   rented_cars_allowances_obj.write(cr, uid, allowances_ids,{'transfer':True,} ,context=context)           
       return {}"""



