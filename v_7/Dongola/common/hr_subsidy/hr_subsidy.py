from datetime import datetime
import time
from openerp.osv import osv, fields, orm


#----------------------------------------
# HR Subsidy
#----------------------------------------
class hr_subsidy(osv.Model):

    _name ="hr.subsidy"

    _description = "Subsidy "

    def compute_subsidy(self, cr, uid,ids,name,args,context=None):
        """
        Method that computes susidy allowance for specific employee.
        
        @return: Dictionary of amount of records to be updated
        """
        for s in self.browse( cr, uid,ids):
            amount= {}
            payroll_obj = self.pool.get('payroll')
            employee_obj = self.pool.get('hr.employee')
            subsidy_archive_obj = self.pool.get('hr.subsidy')
            check= subsidy_archive_obj.search(cr,uid,[('id','=',s.id)],context=context)
	    allow_dict=payroll_obj.allowances_deductions_calculation(cr, uid,s.date,s.employee_id,{}, [s.allowance.id])
            amount[s.id] = {
                    'amount':allow_dict['result'][0]['amount'],
                }
        return amount

    _columns ={
        'emp_code': fields.related('employee_id', 'emp_code', type='char', string='Code', store=True, readonly=True,size=64),
        'employee_id':fields.many2one('hr.employee',"Employee", required= True,size=64),
        'allowance':fields.many2one('hr.allowance.deduction',"Allowance", required= True,size=64),
        'amount': fields.function(compute_subsidy, string='Amount',type='float', readonly=True,multi='sums',store=True,size=64), 
        'date' :fields.date("Date", required= True,size=64),
        'transfer' :fields.boolean('Transfered', readonly=True),
        'acc_number': fields.many2one('account.voucher', 'Accounting Number', readonly=True),
    }

    _defaults = {
        'transfer': lambda *a: 0,
    } 

# *********************************************  Transfer  Funcatin ************************************
    def transfer_subsidy(self, cr, uid,ids,context={}):
        """
        Method transfers amount of susidy allowance for specific employee voucher.

        @return: dictionary
        """
        for subsidy in self.browse( cr, uid,ids):
            allow_deduct_obj  = self.pool.get('hr.allowance.deduction')
            check= self.search(cr,uid,[('employee_id','=',subsidy.employee_id.id),('allowance','=',subsidy.allowance.id)],context=context) 
            lines=[]
            employee = subsidy.employee_id
            if employee.payroll_id.id and employee.degree_id.id:
                if not subsidy.transfer and subsidy.amount:
                    date = time.strftime('%Y-%m-%d')
                    reference = 'HR/Subsidy/ '+" / "+str(date)
                    scale_allow_duduct_ids=allow_deduct_obj.search(cr,uid,[('id','=',subsidy.allowance.id)],context=context)
                    if scale_allow_duduct_ids:
                        scale_allow_duduct = allow_deduct_obj.browse(cr,uid,scale_allow_duduct_ids,context=context)[0]
                        d={
                           'amount': subsidy.amount,
                           'account_id': scale_allow_duduct.account_id.id
                        }
                        lines.append(d)
                        voucher=self.pool.get('payroll').create_payment(cr, uid, ids,{'reference':reference,'lines':lines},context=context)
                        self.write(cr,uid,check,{'acc_number': voucher,'transfer':True})
                    else:
                        raise osv.except_osv('Sorry', 'This Allownces Already Transfered !' ) 
        return {}

