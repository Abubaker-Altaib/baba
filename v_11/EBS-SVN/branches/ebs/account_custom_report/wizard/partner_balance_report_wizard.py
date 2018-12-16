# -*- coding: utf-8 -*-

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from dateutil.relativedelta import *
from datetime import date, datetime, timedelta




class PartnerBalanceReportWizard(models.TransientModel):
    _inherit = 'partner.leadger.report.wizard'




    def get_partner_trial_balance(self,partner_ids,account_id,date_start,date_end):
        partners = tuple(partner_ids)
        if len(partners) == 1:
            partners = str(partners).replace(',','')
        print("""

        		select
        			partner.name,
        			(select COALESCE(sum(debit),0) from account_move_line where partner_id = partner.id and date < '%s' and account_id=%s) Op_Debit ,
        			(select COALESCE(sum(credit),0) from account_move_line where partner_id = partner.id and date < '%s' and account_id=%s) Op_Crebit ,
        			sum(debit) Movement_Debit,
        			sum(credit) Movement_Credit,





	case when

	(
	    (
		(select COALESCE (sum(debit),0) from account_move_line  where date < '%s' and account_id = %s and partner_id = partner.id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line where date < '%s' and account_id = '%s' and  partner_id = partner.id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	)


	>= 0 THEN (
	    (
		(select COALESCE (sum(debit),0) from account_move_line where date < '%s' and account_id = %s and partner_id = partner.id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line where date < '%s' and account_id = %s and  partner_id = partner.id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	)  else 0 END
	 "Balance O Debit"

	,
	case when

	(
	    (
		(select COALESCE (sum(debit),0) from account_move_line  where date < '%s' and account_id = %s and  partner_id = partner.id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line  where date < '%s' and account_id = %s and partner_id = partner.id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	)


	< 0 THEN (
	    (
		(select COALESCE (sum(debit),0) from account_move_line where date < '%s' and account_id = %s and partner_id = partner.id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line where date < '%s' and account_id = %s and partner_id = partner.id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	) * -1  else 0 END "Balance O Credit"


        		from account_move_line line join res_partner partner on partner.id = line.partner_id where line.partner_id in %s and line.date between '%s' and '%s' and line.account_id = %s group by partner.name,partner.id

                                """%(date_start, account_id, date_start, account_id, date_start, account_id, date_start, account_id, date_start,
                                     account_id, date_start, account_id, date_start, account_id, date_start, account_id, date_start, account_id,
                                     date_start, account_id, partners, date_start, date_end, account_id))

        res = self._cr.execute( """

        		select
        			partner.name,partner.code,
        			(select COALESCE(sum(debit),0) from account_move_line where partner_id = partner.id and date < '%s' and account_id=%s) Op_Debit ,
        			(select COALESCE(sum(credit),0) from account_move_line where partner_id = partner.id and date < '%s' and account_id=%s) Op_Crebit ,
        			sum(debit) Movement_Debit,
        			sum(credit) Movement_Credit,





	case when

	(
	    (
		(select COALESCE (sum(debit),0) from account_move_line  where date < '%s' and account_id = %s and partner_id = partner.id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line where date < '%s' and account_id = '%s' and  partner_id = partner.id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	)


	>= 0 THEN (
	    (
		(select COALESCE (sum(debit),0) from account_move_line where date < '%s' and account_id = %s and partner_id = partner.id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line where date < '%s' and account_id = %s and  partner_id = partner.id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	)  else 0 END
	 "Balance O Debit"

	,
	case when

	(
	    (
		(select COALESCE (sum(debit),0) from account_move_line  where date < '%s' and account_id = %s and  partner_id = partner.id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line  where date < '%s' and account_id = %s and partner_id = partner.id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	)


	< 0 THEN (
	    (
		(select COALESCE (sum(debit),0) from account_move_line where date < '%s' and account_id = %s and partner_id = partner.id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line where date < '%s' and account_id = %s and partner_id = partner.id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	) * -1  else 0 END "Balance O Credit"


        		from account_move_line line join res_partner partner on partner.id = line.partner_id where line.partner_id in %s and line.date between '%s' and '%s' and line.account_id = %s group by partner.name,partner.id order by partner.code

                                """%(date_start, account_id, date_start, account_id, date_start, account_id, date_start, account_id, date_start,
                                     account_id, date_start, account_id, date_start, account_id, date_start, account_id, date_start, account_id,
                                     date_start, account_id, partners, date_start, date_end, account_id))

        #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",sql_query)

        results = self._cr.dictfetchall()
        #print(">>>>>>>>>>>>>>>>>>>>.RESULTS ",results)
        return results

    def print_partner_balance(self):
        """
        Desc : print partner balance report
        :return:
        """



        if self.mapped('date_from') > self.mapped('date_to'):
            raise UserError(('Date From must be equal or less than Date To!!'))


        if len(self.mapped('partner_ids')) == 0 or len(self.mapped('account_ids')) == 0 :
            raise UserError(('You Must atleast select one partner and one account !!!'))

        get_partner_ids = tuple([line.id for line in self.partner_ids])
        get_account_ids = tuple([line.id for line in self.account_ids])

        get_partner_names = tuple([line.name for line in self.partner_ids])
        get_account_names = tuple([line.name for line in self.account_ids])

        # collect all parameters
        data = {}
        data.update({'get_account_ids': get_account_ids})
        data.update({'get_partner_ids': get_partner_ids})
        data.update({'get_account_names': get_partner_names})
        data.update({'get_partner_names': get_partner_names})
        data.update({'date_from': self.date_from})
        data.update({'date_to': self.date_to})
        data.update({'init_balance': self.init_balance})
        if self.init_balance == False:
            self.with_balance = False
        data.update({'with_balance': self.with_balance})
        data.update({'time_now': fields.datetime.now()})

        if self.target_moves == 'post':
            data.update({'move_state': ('posted',)})
        else:
            data.update({'move_state': ('draft', 'posted')})



        if self.init_balance:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")



            data.update({'query_result': self._cr.dictfetchall()})
            return self.env.ref('account_custom_report.action_partner_balance_report').with_context(
                landscape=True).report_action(self, data=data)




        return self.env.ref('account_custom_report.action_partner_balance_report').with_context(
            landscape=True).report_action(self, data=data)



class partnerBalanceReport(models.AbstractModel):
    _name = 'report.account_custom_report.partner_balance_report_tamplate'

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
            'get': self.env['partner.leadger.report.wizard'],
            'self': self,
        }
