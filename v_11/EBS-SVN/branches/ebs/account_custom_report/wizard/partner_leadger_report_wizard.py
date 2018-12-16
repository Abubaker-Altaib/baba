# -*- coding: utf-8 -*-

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from dateutil.relativedelta import *
from datetime import date, datetime, timedelta


class accountAccount(models.Model):
    _inherit = 'account.account'



class PartnerLeadgerReportWizard(models.TransientModel):
    _name = 'partner.leadger.report.wizard'

    parent_id = fields.Many2one('account.account')

    account_ids = fields.Many2many('account.account', 'partner_ledger_account_rel', 'ledger_account_id',
                               'account_id', 'Accounts', required=True)

    partner_ids = fields.Many2many('res.partner', 'res_partner_leadger_account_rel', 'ledger_partner_id',
                                   'account_id', 'Partners', required=True)
    init_balance = fields.Boolean(string='Include Initial Balances' , default=True)
    # default date is first day of the current year
    date_from = fields.Date(required=1, default=lambda self: date(date.today().year, 1, 1))
    # default date is last day of the current year
    date_to = fields.Date(required=1, default=lambda self: date(date.today().year, 12, 31))

    target_moves = fields.Selection([('post', 'All Posted Entries'), ('all', 'All Entries')], required=1, default='post')
    report_type  = fields.Selection([('leadger', 'Leadger Report'), ('balance', 'Partner Balance')], default='leadger')
    with_balance = fields.Boolean(string="Just Balance",default=False)



    def print_report(self):
        """
        Print Partner Leadger Report
        :return:
        """
        if self.mapped('date_from') > self.mapped('date_to'):
            raise UserError(('Date From must be equal or less than Date To!!'))


        if len(self.mapped('partner_ids')) == 0 or len(self.mapped('account_ids')) == 0 :
            raise UserError(('You Must atleast select one partner and one account !!!'))



        data = {}

        partner = self.env['res.partner']
        move_line = self.env['account.move.line']

        get_partner_ids =tuple([line.id for line in self.partner_ids])
        get_account_ids =tuple([line.id for line in self.account_ids])

        get_partner_ids = tuple([line.id for line in self.partner_ids])


        parent = '-'
        is_parent_only = False

        if len(self.parent_id) == 0:
            parent = tuple([line.name for line in self.account_ids])
            get_account_ids = tuple([line.id for line in self.account_ids])
        else:
            is_parent_only = True
            #parent = tuple([line.name for line in self.env['account.account'].search([('id','child_of',self.parent_id.id)])])
            parent = tuple([line.code+' '+line.name for line in self.env['account.account'].with_context(show_parent_account=True).search([('id','=',self.parent_id.id)])])
            parent_child = self.env['account.account'].search([('id','child_of',self.parent_id.id)])
            get_account_ids = tuple([line.id for line in parent_child])





        #if len(get_partner_ids) == 1:
        #    get_partner_ids = str(get_partner_ids).replace(",","")

        #if len(get_account_ids) == 1:
        #    get_account_ids = str(get_account_ids).replace(",","")

        data.update({'get_partner_ids':get_partner_ids})
        data.update({'get_account_ids':get_account_ids})
        data.update({'partner_ids':self.partner_ids})
        data.update({'date_from':self.date_from})
        data.update({'date_to':self.date_to})
        data.update({'init_balance':self.init_balance})
        data.update({'parent_account':parent})
        data.update({'is_parent_only':is_parent_only})
        data.update({'target_moves':self.target_moves})

        #for line in data['partner_ids']:
        #    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>",line.name)

        # for line in partner.search([('id','in', get_partner_ids)]):
        #     print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",line.name)
        #
        #     for m_line in move_line.search([('account_id','in',get_account_ids),('partner_id','=',line.id)]):
        #         print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",move_line.name)



        # sql_query = """
        # select * from account_move_line line
        #   join
        #   account_account account on line.account_id = account.id
        #   join
        #   res_partner partner on line.partner_id = partner.id
        #
        # """

        #return

        return self.env.ref('account_custom_report.action_partner_ledger_report').with_context(
            landscape=True).report_action(self, data=data)


class partnerLedgerReport(models.AbstractModel):
    _name = 'report.account_custom_report.partner_ledger_report_tamplate'

    @api.model
    def get_report_values(self, docids, data=None):
        """
        Desc : Send Data to report
        :param docids:
        :param data:
        :return:
        """


        return {
            'data': data,
            'get': self
        }


    def get_partner_info(self,partner_id):
        partner_info = self.env['res.partner'].search([('id','=',partner_id)])
        #print(">>>>>>>>>")
        return partner_info


    def get_account_info(self,account_id):
        account_info = self.env['account.account'].search([('id','=',account_id)])
        #print(">>>>>>>>>")
        return account_info

    def get_partner_real_accounts(self,partner_id, accounts_id,data):
        accounts_id = tuple(accounts_id)

        date_params = 'and line.date between %s and %s'
        params = [partner_id, accounts_id, data['date_from'],data['date_to']]
        if data['init_balance'] == True:
            date_params = 'and line.date <= %s'
            params = [partner_id, accounts_id, data['date_to']]



        print(">>>>>>>>>>>>>>>>>>>>accounts_id ",accounts_id)
        target_moves = " and move.state = 'posted' "
        if data['target_moves'] == 'all':
            target_moves = ""

        sql_query = """
                        select line.account_id acc_id from account_move_line line
                          join
                          account_account account on line.account_id = account.id
                          join
                          res_partner partner on line.partner_id = partner.id
                          join account_move move on line.move_id = move.id
                          where line.partner_id = %s and line.account_id in %s """+date_params+"""
                          """+target_moves+"""

                          group by line.account_id

                        """
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>",sql_query, partner_id, accounts_id, data['date_from'])
        self._cr.execute(sql_query, params)
        result = self._cr.dictfetchall()
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>RESULT REAL ",result)
        return result




    def get_partner_move_line(self,partner_id,account_id,data):

        target_moves = " and move.state = 'posted' "
        if data['target_moves'] == 'all':
            target_moves = ""

        sql_query = """
                select line.date,line.name,move.ref,move.name "move_name",line.debit,line.credit,(line.debit - line.credit) balance from account_move_line line
                  join account_account account on line.account_id = account.id
                  join res_partner partner on line.partner_id = partner.id
                  join account_move move on line.move_id = move.id
                  where line.partner_id = %s and line.account_id = %s and line.date between %s and %s

                """ + target_moves
        print (">>>>>>>>>>>>>>>>>>>SQL QUERY ",sql_query,[partner_id,account_id,data['date_from'],data['date_to']])
        self._cr.execute(sql_query,[partner_id,account_id,data['date_from'],data['date_to']])
        result = self._cr.dictfetchall()
        return result


    def get_partner_move_line_total(self,partner_id,account_id,data):



        date_params = 'and line.date between %s and %s'
        params = [partner_id, account_id, data['date_from'], data['date_to']]
        if data['init_balance'] == True:
            date_params = 'and line.date <= %s'
            params = [partner_id, account_id, data['date_to']]

        target_moves = " and move.state = 'posted' "
        if data['target_moves'] == 'all':
            target_moves = ""


        sql_query = """
                select sum(line.debit) debit,sum(line.credit) credit,sum((line.debit - line.credit)) balance from account_move_line line
                  join account_account account on line.account_id = account.id
                  join res_partner partner on line.partner_id = partner.id
                  join account_move move on line.move_id = move.id
                  where line.partner_id = %s and line.account_id = %s """+date_params + target_moves
        self._cr.execute(sql_query,params)
        result = self._cr.dictfetchall()
        print(">>>>>>>>>",result)
        return result


    def get_partner_move_line_init(self,partner_id,account_id,data):

        target_moves = " and move.state = 'posted' "
        if data['target_moves'] == 'all':
            target_moves = ""

        sql_query = """
                select COALESCE (sum(line.debit),0) debit,COALESCE (sum(line.credit),0) credit,COALESCE (sum((line.debit - line.credit)),0) balance from account_move_line line
                  join account_account account on line.account_id = account.id
                  join res_partner partner on line.partner_id = partner.id
                  join account_move move on line.move_id = move.id
                  where line.partner_id = %s and line.account_id = %s and line.date <= %s

                """ + target_moves
        self._cr.execute(sql_query,[partner_id,account_id,data['date_from']])
        result = self._cr.dictfetchall()
        return result

