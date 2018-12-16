from datetime import timedelta
from odoo import api, fields, models, _
from datetime import datetime
from decimal import Decimal
class PrintBudgetLines(models.AbstractModel):
  _name = 'report.account_budget_ebs.print_budget_lines_report'
  @api.model
  def get_report_values(self, docids, data):
    budget_lines = self.env['crossovered.budget.lines'].search([('analytic_account_id','=',data['analatic_account_id'][0]) , ('date_from','ilike',data['year']) ]) 
    if data['parent_account_id'] :# and not data['year'] :
      #print("################################## you have not entered year only parent account")
      budget_lines = self.env['crossovered.budget.lines'].with_context({'show_parent_account':True}).search([('analytic_account_id','=',data['analatic_account_id'][0])
                                                                                                   , ('parent_account_id','child_of',data['parent_account_id'][0]) ,
                                                                                                     ('date_from','ilike',data['year']) ])
    #if data['parent_account_id'] and data['year'] : 
      #print("################################## you have entered year and parent account")
      #budget_lines = self.env['crossovered.budget.lines'].with_context({'show_parent_account':True}).search([('analytic_account_id','=',data['analatic_account_id'][0]),
      #                                                                                                     ('parent_account_id','child_of',data['parent_account_id'][0]) 
      #                                                                                                       , ('date_from','ilike',str(data['year']))])
        
    #if data['year'] and not data['parent_account_id']:
      #print("################################## you have not entered parent account only year ")
      #budget_lines = self.env['crossovered.budget.lines'].with_context({'show_parent_account':True}).search([('analytic_account_id','=',data['analatic_account_id'][0])
       #                                                                                                      , ('date_from','ilike',str(data['year']))])
        
    amount_per_month_list=[]  
    list_of_dics=[]
    for budget_line in budget_lines:
      dic_of_months={1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,}
      months = datetime.strptime(budget_line.date_to, '%Y-%m-%d').month - datetime.strptime(budget_line.date_from, '%Y-%m-%d').month + 1
      if months != 0 :
        amount_per_month = round(Decimal(budget_line.planned_amount / months ),2) 
        amount_per_month_list.append(amount_per_month)
      my_list=list(range(datetime.strptime(budget_line.date_from, '%Y-%m-%d').month,datetime.strptime(budget_line.date_to, '%Y-%m-%d').month +1))
      for li in my_list :
        dic_of_months[li]=amount_per_month
      list_of_dics.append(dic_of_months)  
    docargs = {
            'doc_ids': self.ids,
            'doc_model': 'crossovered.budget.lines',
            'docs': budget_lines,
            'amount_per_month':amount_per_month_list,
            'list_of_dics':list_of_dics,
            'year':data['year'],
            'parent_account':data['parent_account_id'],
            'analytic_account':data['analatic_account_id'][1]
           }   
    return  docargs
    

    