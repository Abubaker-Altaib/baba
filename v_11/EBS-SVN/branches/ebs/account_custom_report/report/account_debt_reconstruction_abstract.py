# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar
from datetime import timedelta ,datetime 
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from collections import OrderedDict


class DebtReconstructionReport(models.AbstractModel):
    _name = 'report.account_custom_report.report_debt_reconstruction_view'
    _order = 'date desc'

    @api.model
    def get_report_values(self, docids, data):
        
        #short_name
        model  = data['model']
        account_parent_id = data['account_parent_id']
        accounts=[]
        smalles_move=[]
        move_one_month=[]
        move_three_month=[]
        move_six_month=[]
        move_one_year=[]
        move_two_year=[]
        move_more_year=[]
        balances1=[]
        balances3=[]
        balances6=[]
        years1=[]
        years2=[]
        years=[]


        # rase Eror if date_from max
        if data['date_from'] > data['date_to']:
            raise UserError(_('Start Date must be equal to or less than Date To'))


        #search sub accounts thate contant move with not Specific date(date_from,date_to)
        if  data['date_from'] == False and data['date_to'] == False :
            moves = self.env['account.move.line'].with_context({'show_parent_account':True}).search([
        ('account_id.parent_id','child_of',account_parent_id[0])])
           

        #non_duplicated_accounts
            for line in moves:
                accounts.append(line.account_id)
            non_duplicated_accounts=list(dict.fromkeys(accounts).keys()) 

        #small_move_for_each_account
            for accountt in non_duplicated_accounts :
                smalles_move_for_each_account = self.env['account.move.line'].with_context({'show_parent_account':True}).search([
                    ('account_id','=',accountt.id)],order='date',limit=1)
                smalles_move.append(smalles_move_for_each_account)
             
        #convert date from string to date and short name
                dates = datetime.strptime(smalles_move_for_each_account.date, '%Y-%m-%d').date()

        #balance after one month
                one_next_month =dates + relativedelta(months=1)
                move_of_one_month = self.env['account.move.line'].with_context({'show_parent_account':True}).search([('date','>=',dates ),('date','<=',one_next_month ),('account_id','=',accountt.id)])
                move_one_month.append(move_of_one_month)
                for line in move_one_month :
                    total_debit = 0.0
                    total_credit = 0.0
                    for move in line :
                        total_debit =  total_debit + move.debit
                        total_credit = total_credit+ move.credit
                balance1 =(total_debit-total_credit)
                balances1.append(balance1)

        #balance after three month
                three_next_month =dates + relativedelta(months=3)
                move_of_three_month = self.env['account.move.line'].with_context({'show_parent_account':True}).search([('date','>=',dates ),('date','<=',three_next_month ),('account_id','=',accountt.id)])
                move_three_month.append(move_of_one_month)
                for line in move_three_month :
                    total_debit = 0.0
                    total_credit = 0.0
                    for move in line :
                        total_debit =  total_debit + move.debit
                        total_credit = total_credit+ move.credit
                balance3 =(total_debit-total_credit)
                balances3.append(balance3)

        #balance after six month
                six_next_month =dates + relativedelta(months=6)
                move_of_six_month = self.env['account.move.line'].with_context({'show_parent_account':True}).search([('date','>=',dates ),('date','<=',six_next_month ),('account_id','=',accountt.id)])
                move_six_month.append(move_of_six_month)
                for line in move_six_month :
                    total_debit = 0.0
                    total_credit = 0.0
                    for move in line :
                        total_debit =  total_debit + move.debit
                        total_credit = total_credit+ move.credit
                balance6 =(total_debit-total_credit)
                balances6.append(balance6)

         #balance after one year
                one_next_year =dates + relativedelta(years=1)
                move_of_one_year = self.env['account.move.line'].with_context({'show_parent_account':True}).search([('date','>=',dates ),('date','<=',one_next_year ),('account_id','=',accountt.id)])
                move_one_year.append(move_of_one_year)
                for line in move_one_year :
                    total_debit = 0.0
                    total_credit = 0.0
                    for move in line :
                        total_debit =  total_debit + move.debit
                        total_credit = total_credit+ move.credit
                year1 =(total_debit-total_credit)
                years1.append(year1)
                   
         #balance after two year
                two_next_year =dates + relativedelta(years=2)
                move_of_two_year = self.env['account.move.line'].with_context({'show_parent_account':True}).search([('date','>=',dates ),('date','<=',two_next_year ),('account_id','=',accountt.id)])
                move_two_year.append(move_of_two_year)
                for line in move_two_year :
                    total_debit = 0.0
                    total_credit = 0.0
                    for move in line :
                        total_debit =  total_debit + move.debit
                        total_credit = total_credit+ move.credit
                year2 =(total_debit-total_credit)
                years2.append(year2)

        #balance after more
                more = dates + relativedelta(years=3)
                move_of_more_year = self.env['account.move.line'].with_context({'show_parent_account':True}).search([('date','>=',dates ),('account_id','=',accountt.id)])
                move_more_year.append(move_of_more_year)
                for line in move_more_year :
                    total_debit = 0.0
                    total_credit = 0.0
                    for move in line :
                        total_debit =  total_debit + move.debit
                        total_credit = total_credit+ move.credit
                year =(total_debit-total_credit)
                years.append(year)
            


        #get_sub accounts && search account thate contant move with Specific date(date_from,date_to)
        else : 
            moves = self.env['account.move.line'].with_context({'show_parent_account':True}).search([
            ('account_id.parent_id','child_of',account_parent_id[0]),
            ('date','>=',data['date_from']),
            ('date','<',data['date_to'])
            ])
        

        #rase Eror if not moves
        if not moves:
                raise UserError(_("this parent Account has not any childs accounts, this report cannot be printed."))



        #return to template
        docargs = {
            'doc_ids'     : self.ids,
            'doc_model'   : model,
            'account_code': data['account_code'],
            'account_name': data['account_name'],
            'account_currency': data['account_currency'],
            'date_from'       : data['date_from'],
            'date_to'         : data['date_to'],
            'moves'           :moves,
            'non_duplicated_accounts':non_duplicated_accounts,
            'smalles_move'           :smalles_move,
            'move_one_month'         :move_one_month,
            'balances1' : balances1 ,
            'balances3' : balances3 ,
            'balances6' : balances6 ,
            'years1'    : years1,
            'years2'    :years2,
            'years'     :years,
            
            }
    
        return  docargs