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
import netsvc

#----------------------------------------
#sale_employee_loan_wiz
#----------------------------------------
class sale_employee_loan_wiz(osv.osv_memory):

    _name = "sale.employee.loan.wiz"
    _description = "Sale order employee loan wizard"

    _columns = {
        'from_date': fields.date('From', required=True,), 
        'to_date': fields.date('To', required=True),
        'loan_date': fields.date('Loan date', required=True),
        'category_id' : fields.many2one('sale.category','Category',required=True),
        'company_id' : fields.many2one('res.company','Company' ,readonly=True),
   		 }
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'sale.employee.loan.wiz', context=c),
		}

    def transfer_loan(self,cr,uid,ids,context={}):
	loan_obj = self.pool.get('hr.employee.loan')
	loan_amount = 0.0
	for record in self.browse(cr,uid,ids,context=context):
		if record.company_id.loan_id.id:
			cr.execute ("""select so.id as id , so.employee_id as emp
						from sale_order so
						where (to_char(so.create_date,'YYYY-mm-dd')>=%s and to_char(so.create_date,'YYYY-mm-dd')<=%s) and so.state in ('done') and so.payment_type ='installment' and so.company_id=%s and so.category_id=%s
						group by so.id """,(record.from_date,record.to_date,record.company_id.id,record.category_id.id))
        		result = cr.dictfetchall()
			for order in result :
				cr.execute ("""select l.period as period , sum (l.installment_value * l.product_uom_qty) installment 
						from sale_order_line l
                                                left join sale_order so on (so.id = l.order_id)  
						where l.order_id = '%s'
						group by l.period """%order['id'])
        			result_line = cr.dictfetchall()
				for line in result_line :
					loan_id = loan_obj.create(cr, uid, {'employee_id':order['emp'],\
	                                		'refund_from':'salary',\
							'loan_id':record.company_id.loan_id.id ,\
					 		'total_installment':line['period'],\
							'loan_amount': line['installment'] * line['period'] ,
							'salary_refund':line['installment'],
			   				'addendum_refund' : 1,
			   				'state':'draft',
							'sale_order_id':order['id'],
							'start_date':record.loan_date,
							'comments':'أقساط المؤسسة التعاونية',
			   				'addendum_install_no' : 1 , }, context)
                                        wf_service = netsvc.LocalService("workflow")
                                        wf_service.trg_validate(uid , 'hr.employee.loan' , loan_id , 'cooperative_loan_paid' ,cr )
                                        loan_obj.write(cr ,uid , loan_id , {'state' : 'paid'},context = context)
				
             	else:
             		raise osv.except_osv(_('Error!'),_('No loan created, Please creat a loan in the company form in Hr setting page .'))
	return {}
