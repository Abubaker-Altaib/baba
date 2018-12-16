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
#rented_cars_allowances_archive_wiz
#----------------------------------------
class rented_cars_allowances_archive_wiz(osv.osv_memory):

    def _get_months(sel, cr, uid, context):
       """
	Method that returns months of year as numbers.
	@return: List Of tuple
       """
       months=[(str(n),str(n)) for n in range(1,13)]
       return months

    _name = "rented.cars.allowances.wiz"
    _description = "Rented Cars Allowances Archive Wizard"

    _columns = {
	    'company_id' : fields.many2one('res.company', 'Company',required=True),
            'dep':fields.many2one('hr.department', 'Department',required=True),
            'month': fields.selection(_get_months,'Month', required=True),
            'year': fields.char('Year',size=32, required=True),
        'action_type':fields.selection([('compute','Compute'),('transfer','Transfer')],'Action Type'),
   		 }
    _defaults = {
	'action_type' :'compute',
        'year': str(time.strftime('%Y')),
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'rented.cars.allowances.wiz', context=c),
		}

    def compuete_allowances(self,cr,uid,ids,context={}):
           """Compute rented Cars  allowances per departments in specific company during specific period of time .
           @return: Dictionary 
           """
           rented_obj = self.pool.get('rented.cars')
           rented_cars_allowances_obj = self.pool.get('rented.cars.allowances.archive')
           allowances_lines_obj = self.pool.get('rented.cars.allowances.lines')

       	   for record in self.browse(cr,uid,ids,context=context):

  		check_allowance = rented_cars_allowances_obj.search(cr,uid,[('month','=',record.month),('year','=',record.year),('company_id','=',record.company_id.id)],context=context)
                if check_allowance:
	      		raise osv.except_osv('ERROR', 'Rented Cars Allowances For This Month Already Computed')
                
           	first_date = datetime(year=int(record.year), month= int(record.month), day=1)
		print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",int(record.year)
           	# Last Day of the Mont
                if first_date.month < 12:
            	    next_month = datetime(year=first_date.year, month=first_date.month+1, day=1)
		else:
            	    next_month = datetime(year=first_date.year+1, month=1, day=1)
            	last_day = next_month - timedelta(days=1)
          	rented_ids = rented_obj.search(cr,uid,[('company_id','=',record.company_id.id),('state','=','confirmed') ])
                zain=rented_obj.search(cr,uid,[('company_id','=',record.company_id.id),(('date_of_return','<=',last_day) and ('date_of_return','>=',first_date)) or  
(('date_of_return','>=',last_day) and ('date_of_rent','<=',last_day )),('state','=','confirmed') ])

          	if not rented_ids:
             		raise osv.except_osv(_('Warning'), _("No Rented Cars to compute in this period or already computed "))
# Select for Partner that Satisfy the condition 
          	cr.execute("""SELECT distinct partner_id as partner_id from rented_cars where company_id =%s and state = 'confirmed' and (date_of_return <=%s and date_of_return >=%s) or 
		  (date_of_return>=%s and date_of_rent<=%s ) group by partner_id """,(record.company_id.id,last_day,first_date,last_day,last_day))
          	partner_res=cr.dictfetchall()
# Define
		tax=0
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
                		cr.execute("""SELECT distinct id as rent_id ,cost_rate as cost_rate, cost_of_rent as cost ,date_of_rent as start_date , date_of_return as end_date , car_id as car_id , amount_tax as tax ,amount_total as total , department_id as department_id from rented_cars where company_id =%s and state ='confirmed' and partner_id =%s and date_of_return >= %s """,(record.company_id.id,partner['partner_id'],first_date))
                		res=cr.dictfetchall()

                		if res:
                   		  partner_archive_dict = rented_cars_allowances_obj.create(cr, uid,{
			 'company_id' : record.company_id.id,
		         'partner_id' :partner['partner_id'],
		         'month': record.month,
		         'year': record.year,
                         'dep': record.dep.id,

		      			 })
				  for res_rent in res :
				     	contract_start = datetime.strptime(res_rent['start_date'],"%Y-%m-%d")
				     	contract_end = datetime.strptime(res_rent['end_date'],"%Y-%m-%d")
					"""print "w1",first_date
					print "w2",last_day
					print "c1",contract_start
					print "c2",contract_end"""
				     	wiz_diff = first_date - last_day
				     	wiz_total = 1 + abs(wiz_diff.days)
                                        if not res_rent['tax']:
                                                res_rent['tax']=0  
				     	tax_avg = round(res_rent['tax']/wiz_total,2)
                                        if not tax_avg:
                                                tax_avg=0          
                                       
				     # If cost Per Month Or Per Day
				        if res_rent['cost_rate']=='per_month':
						amount_avg = round(res_rent['cost']/wiz_total,2)
					else :
						amount_avg = res_rent['cost']

					if contract_start == first_date :
						if contract_end > last_day :
							total = res_rent['total']
		         				total_untax = res_rent['cost']
        		                        	total_tax = res_rent['tax']
							date_dedc = 0.0
							dedc_amount = 0.0
						elif contract_end < last_day :
							date_diff = contract_start - contract_end
				     			total_date = 1+ abs(date_diff.days)
				     			total_untax = amount_avg * total_date
				     			total = amount_avg * total_date  + tax_avg * total_date
				     			total_tax =  tax_avg * total_date 
				     			date_dedc = abs(wiz_total - total_date)
				     			dedc_amount = abs(res_rent['cost'] - total)
					if contract_start >=first_date and contract_end <=last_day :
						date_diff = contract_start - contract_end
				     		total_date = 1+ abs(date_diff.days)
				     		total_untax = amount_avg * total_date
				     		total = amount_avg * total_date  + tax_avg * total_date
				     		total_tax =  tax_avg * total_date 
				     		date_dedc = abs(wiz_total - total_date)
				     		dedc_amount = abs(res_rent['cost'] - total)
					if contract_start < first_date :
						if contract_end < last_day and contract_end >= first_date:
							date_diff = first_date - contract_end
				     			total_date = 1+ abs(date_diff.days)
				     			total_untax = amount_avg * total_date
				     			total = amount_avg * total_date  + tax_avg * total_date
				    			total_tax =  tax_avg * total_date 
				     			date_dedc = abs(wiz_total - total_date)
				     			dedc_amount = abs(res_rent['cost'] - total)
						elif contract_end > last_day:
							date_diff = first_date - last_day
				     			total_date = 1+ abs(date_diff.days)
				     			total_untax = amount_avg * total_date
				     			total = amount_avg * total_date  + tax_avg * total_date
				     			total_tax =  tax_avg * total_date 
				     			date_dedc = abs(wiz_total - total_date)
				     			dedc_amount = abs(res_rent['cost'] - total)
						elif contract_end == last_day :
							total = res_rent['total']
		         				total_untax = res_rent['cost']
        		                        	total_tax = res_rent['tax']
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

						total = res_rent['total']
		         			total_untax = res_rent['cost']
        		                        total_tax = res_rent['tax']
						date_dedc = 0.0
						dedc_amount = 0.0
                      		     	partner_allow_dict = {
			 					'rented_cars_allow_id' : partner_archive_dict,
		         					'partner_id' :partner['partner_id'],
		         					'cost_of_rent':res_rent['total'],
		         					'amount_untaxed':total_untax,
        		 					'amount_tax':total_tax,
        		 					'amount_total':total,
        		 					'deduct_days':date_dedc,
        		 					'deduct_amount':dedc_amount,
        		 					'department_id': res_rent['department_id'],
        		 					'rent_id': res_rent['rent_id'],
        		 					'car_id': res_rent['car_id'],
		      				    }

 			             	allowances_lines_obj.create(cr, uid ,partner_allow_dict, context=context)
           return {}

    def create_ratification(self,cr,uid,ids,context={}):
       """Transfers the amount to account voucher.
       @return: Dictionary 
       """
       for record in self.browse(cr,uid,ids,context=context):
       	rented_cars_allowances_obj = self.pool.get('rented.cars.allowances.archive')
       	allowances_ids = rented_cars_allowances_obj.search(cr,uid,[('month','=',record.month),('year','=',record.year),('company_id','=',record.company_id.id),('transfer','=',False)])
       if not allowances_ids:
             raise osv.except_osv(_('Warning'), _("No Rented Cars to transfer, or already transfered "))
       rented_cars_allowances_obj.action_create_ratification(cr,uid,allowances_ids,context)
       return {}

rented_cars_allowances_archive_wiz()

