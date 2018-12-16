# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

# import time
# import datetime
# from openerp.osv import osv, fields, orm
# from openerp.tools.translate import _

# from openerp import netsvc
# import openerp.addons.decimal_precision as dp
# import math

from odoo import api, fields, models , exceptions,_
import time
from datetime import date, datetime, timedelta

from odoo.exceptions import UserError, ValidationError


#----------------------------------------
#Loan Payment
#----------------------------------------

class hr_employee_loan_paid(models.Model):

  _name ='hr.employee.loan.paid'
  _description = "Employee's Out Of Salary Loan Payment"

  name =  fields.Char("Name",  readonly=True,translate=True )
  employee_id = fields.Many2one("hr.employee",'Employee')
  emp_loan_id = fields.Many2one('hr.loan.request', 'Loan')
  loan_amount = fields.Float(related='emp_loan_id.remain_installment',string='Amount', store=True, readonly=True)
  #loan_amount =  fields.Float(related='loan_id.remain_installment',string='Amount', store=True, readonly=True)
  loan_amount2 = fields.Float("Amount" )
  date = fields.Date("Date" ,default=fields.datetime.now())
  month = fields.Selection([(1, '1'),(2,' 2'),(3, '3'),(4, '4'),(5, '5'),(6, '6'),
                                   (7, '7'),(8, '8'),(9, '9'),(10, '10'),(11, '11'),(12, '12')],'Month')
  year = fields.Integer("Year")
  note = fields.Text("Notes")
  pay_type = fields.Selection([('installment','Installment') , ('once','Once')],"Pay Type")
  installment_no = fields.Integer("Installments Number")
  rais = fields.Float("Rais")
  voucher_id = fields.Many2one("account.voucher",'Voucher')
  state = fields.Selection([('draft','Draft') ,('confirm','Confirm'), ('paid','Paid')],string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
  refund_remain_from = fields.Selection([('salary','Salary'),('addendum','Addendum')],'Refund Remain From')
  installment_type = fields.Selection([('pay_installment','Pay For Installments'),
                                 ('reduce_installment',('Reduce Installments Amount'))])
  #loan_arc_ids = fields.One2many('hr.loan.archive','loan_pay_id',string='Loan Archives')
  loan_arc_ids = fields.Many2many('hr.loan.archive', 'loan_pay_arch_rel', 'loan_pay_id', 'arch_id',string='Loan Archives') 


  def confirm(self):
    self.create_payment_voucher()
    self.write({'state':'confirm'})


  def create_payment_voucher(self):
    date = time.strftime('%Y-%m-%d')
    reference = 'HR/Loan/Pay '+" / "+str(date)
    partner_id = self.employee_id.user_id.partner_id.id or False
    account_id = self.employee_id.user_id.partner_id.property_account_payable_id.id or False
    journal_id = self.env['res.config.settings'].search([('company_id','=',self.employee_id.company_id.id)],order='id desc',limit=1).hr_journal_id.id
    currency_id_ebs = self.env['res.company'].search([('id','=',self.env.user.company_id.id)]).currency_id.id
    user_id = self.env.user.id
    department_id = self.emp_loan_id.department_id.id
    company_id = self.env.user.company_id.id

    if not account_id:
      raise UserError(_("The Partner has no payable account"))
    if not journal_id:
      raise UserError(_("The Company has no journal, Please go to HR settings"))

     
    price_unit = 0
    if self.pay_type == 'once' :
      if self.loan_amount > self.emp_loan_id.remain_installment :
        raise UserError(_("the  amount you  is greater than the remain amount"))
      else :  
        price_unit = self.loan_amount

    if self.pay_type == 'installment' :
      #######################################################################
      if self.installment_type == 'pay_installment' :
        if not self.loan_arc_ids :
          raise UserError(_('Please select archives to pay for'))

        is_all_draft = True
        for archive in self.loan_arc_ids:
          if archive.state != 'draft' :
            is_all_draft = False
        
        if is_all_draft == False :
          raise UserError(_('not all archives are draft'))    

        else :  
          price_unit = sum([archive.loan_amount for archive in self.loan_arc_ids])
        ########################################################################

      if self.installment_type == 'reduce_installment' :  
        if self.loan_amount2 > self.emp_loan_id.remain_installment :
          raise UserError(_("the amount you entered is greater than the remain amount "))
        else :  
          price_unit = self.loan_amount2

    voucher = {    'date':date,
                   'account_date':date,
                   'reference':reference,
                   'partner_id':partner_id,
                   'journal_id':journal_id,
                   'currency_id_ebs':currency_id_ebs,
                   'state':'draft',
                   'user_id':user_id,
                   'department_id':department_id,
                   'company_id':company_id,
                   'account_id':account_id,
                   'voucher_type':'sale',
                   'payment_type':'direct_payment'}

    voucher_id = self.env['account.voucher'].create(voucher)
    voucher_id.journal_id.type = 'sale' 
          
        

    lines = {    'name':self.emp_loan_id.loan_id.name,
                 'account_id':account_id,
                 'account_analytic_id':self.emp_loan_id.department_id.analytic_account_id.id,
                 'price_unit':price_unit,
                 'price_subtotal':price_unit,
                 'voucher_id':voucher_id.id  }

    voucher_line_id = self.env['account.voucher.line'].create(lines)


    self.voucher_id = voucher_id.id



class accountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def write(self,vals):
        rec = super(accountVoucher, self).write(vals)
        for line in self:
            if line.state == 'done':
                hr_loan_pay = self.env['hr.employee.loan.paid'].search([('voucher_id','=',self.id)])
                if hr_loan_pay.id and hr_loan_pay.state == 'confirm':

                  ####################################### if pay type = once
                  if hr_loan_pay.pay_type == 'once' :
                    #search for all the payment archives based on the field emp_loan_id
                    archives = self.env['hr.loan.archive'].search([('loan_request_id','=',hr_loan_pay.emp_loan_id.id),
                                                                    ('state','=','draft')])
                    for archive in archives :
                      archive.write({'state':'paid'})

                  ###################################### if pay type = installment  
                  if hr_loan_pay.pay_type == 'installment' :

                    #################################### if installment type = pay installment
                    if hr_loan_pay.installment_type == 'pay_installment' :
                      # make state of selected archives in paid state 
                      for archive in hr_loan_pay.loan_arc_ids :
                        archive.write({'state':'paid'})

                    #################################### if installment ype = reduce installment
                    if hr_loan_pay.installment_type == 'reduce_installment' : 
                      # substract the entered amount (loan_amount2) from loan residual amount(loan_amount) 
                      new_remain = hr_loan_pay.loan_amount - hr_loan_pay.loan_amount2    
                      # find number of draft archives and devide new_remain by number of draft archives
                      draft_archives = self.env['hr.loan.archive'].search([('state','=','draft'),
                                                  ('loan_request_id','=',hr_loan_pay.emp_loan_id.id)])
                      count=0
                      for archive in draft_archives :
                        count = count + 1
                      new_archive_amount =round( new_remain / count,2)

                      count_num = count
                      for archive in draft_archives : 
                        if count_num > 0 :
                      
                          if count_num == 1:
                            last_archive_amount = new_remain - (count-1) * new_archive_amount
                            
                            archive.loan_amount= last_archive_amount
            
                          else :
                            count_num-=1
                            archive.loan_amount= new_archive_amount
                           
                  
                  hr_loan_pay.state = 'paid'        
                      
           
        return rec



