# -*- coding: utf-8 -*-

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class ebsTrialBalanceMovesReportWizard(models.TransientModel):
    _name = 'trial.balance.report.wizard'

    account_id = fields.Many2one('account.account', 'Parent Account')
    target_moves = fields.Selection([('post','All Posted Entries'),('all','All Entries')],required=1,default='all')
    date_from = fields.Date(required=1)
    date_to = fields.Date(required=1)

    def print_report(self, data):

        if self.date_from > self.date_to:
            raise ValidationError(_("""You Must Set 'Date From' less Than 'Date To'."""))



        parent_account = ''
        if self.account_id:
            parent_account = " and acc.parent_id = " + str(self.account_id.id)
        if self.target_moves=='post':
            parent_account+=" and mv.state = 'posted'"
        sql = (""" select acc.code ,
	acc.name ,

	(select COALESCE (sum(debit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id) "Depit Op" ,
	(select COALESCE (sum(credit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id) "Credit Op",
	COALESCE (sum(debit),0) "Movements-Debit" ,
	COALESCE (sum(credit),0) "Movements-Credit" ,
	COALESCE (sum(debit - credit),0) "Balance" ,
	(
	   COALESCE ( (
		(select COALESCE (sum(debit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum(credit),0) ),0)
	) "Balance O"
	,
	case when

	(
	    (
		(select COALESCE (sum(debit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	)


	>= 0 THEN (
	    (
		(select COALESCE (sum(debit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	)  else 0 END
	 "Balance O Depit"
	,
	case when

	(
	    (
		(select COALESCE (sum(debit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	)


	< 0 THEN (
	    (
		(select COALESCE (sum(debit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	) * -1  else 0 END "Balance O Credit"




      from account_move_line line

 join account_move mv on mv.id = line.move_id join
	account_account acc on acc.id = line.account_id where line.date between '""" + self.date_from + """' and '""" + self.date_to + "' " + parent_account + """
group by acc.id
    """)

        self._cr.execute(sql)
        data.update({'query_result':self._cr.dictfetchall()})
        data.update({'moves_state': self.target_moves})
        data.update({'time_now': fields.datetime.now()})
        data.update({'date_from': self.date_from})
        data.update({'date_to': self.date_to})
        if self.account_id:
            data.update({'parent_account': self.account_id.code + " " +self.account_id.name})


        return self.env.ref('account_custom.action_trial_b').with_context(landscape=True).report_action(
            self, data=data)


class trialBalanceReportDetals(models.AbstractModel):
    _name = 'report.account_custom.trial_b'



    @api.model
    def get_report_values(self, docids, data=None):
        print("ABSTRACT ", data)
        if len(data.get('query_result')) == 0 :
            raise UserError(_("No Data , this report cannot be printed."))

        return {
            'doc_ids': 1,
            'data': data,
            'docs': self.env['account.account'].search([('id', 'in',(1,2) )]),#data['ids']

        }
