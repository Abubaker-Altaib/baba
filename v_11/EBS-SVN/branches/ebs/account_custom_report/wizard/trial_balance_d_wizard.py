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
    report_type = fields.Selection([('normal', 'Normal'), ('details', 'Details')],required=1,default='details')
    show_type = fields.Selection([('total', 'Parents Totals Only'), ('details', 'Parent with Details')],default='total')
    initial_balance = fields.Boolean(string="Initial Balances")


    @api.onchange('account_id')
    def set_show_type(self):

        if self.account_id:
            self.show_type = 'details'


    def print_report_details(self):
        if self.date_from > self.date_to:
            raise ValidationError(_("""You Must Set 'Date From' less Than 'Date To'."""))

        parent_accounts = False
        #get all parents accounts
        if self.account_id:
            parent_accounts = [line.account_id.parent_id.id for line in self.env['account.move.line'].search(
                [('date', '>=', self.date_from), ('date', '<=', self.date_to), ('account_id.parent_id', '!=', False),('account_id.parent_id', '=', self.account_id.id)])]
        else:
            parent_accounts = [line.account_id.parent_id.id for line in self.env['account.move.line'].search([('date','>=',self.date_from),('date','<=',self.date_to),('account_id.parent_id','!=',False)])]

        if len(parent_accounts) == 0:
            raise UserError(_("No Data To Print!!"))

        parent_accounts_unique = []
        for line in self.env['account.account'].with_context(show_parent_account=True).search([('id','in',list(set(parent_accounts)))]):
            parent_accounts_unique.append(line.id)

        if len(parent_accounts_unique) == 1:
            parent_accounts_unique = str(tuple(parent_accounts_unique)).replace(",", "")
        else:
            parent_accounts_unique = str(tuple(parent_accounts_unique))




        sql_query = """

        select  p_acc.code, p_acc.name, acc.parent_id,


        (select round(COALESCE (sum(debit),0),2) from account_move_line join account_account on account_move_line.account_id = account_account.id where date < '"""+self.date_from+"""' and parent_id = acc.parent_id) "Depit Op" ,
	(select round(COALESCE (sum(credit),0),2) from account_move_line join account_account on account_move_line.account_id = account_account.id where date < '"""+self.date_from+"""' and parent_id = acc.parent_id) "Credit Op",

    round(COALESCE (sum(debit),0),2) "Movements-Debit" ,
	round(COALESCE (sum(credit),0),2) "Movements-Credit" ,
	round(COALESCE (sum(debit - credit),0),2) "Balance" ,
	(
	   round(COALESCE ( (
		(select COALESCE (sum(debit),0) from account_move_line join account_account on account_move_line.account_id = account_account.id where date < '"""+self.date_from+"""' and parent_id = acc.parent_id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line join account_account on account_move_line.account_id = account_account.id where date < '"""+self.date_from+"""' and parent_id = acc.parent_id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum(credit),0) ),0),2)
	) "Balance O"
	,




	case when

	(
	    (
		(select COALESCE (sum(debit),0) from account_move_line  join account_account on account_move_line.account_id = account_account.id  where date < '"""+self.date_from+"""' and parent_id = acc.parent_id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line  join account_account on account_move_line.account_id = account_account.id  where date < '"""+self.date_from+"""' and parent_id = acc.parent_id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	)


	>= 0 THEN round((
	    (
		(select COALESCE (sum(debit),0) from account_move_line join account_account on account_move_line.account_id = account_account.id where date < '"""+self.date_from+"""' and parent_id = acc.parent_id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line join account_account on account_move_line.account_id = account_account.id  where date < '"""+self.date_from+"""' and parent_id = acc.parent_id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	),2)  else 0 END
	 "Balance O Depit"
	,
	case when

	(
	    (
		(select COALESCE (sum(debit),0) from account_move_line  join account_account on account_move_line.account_id = account_account.id  where date < '"""+self.date_from+"""' and parent_id = acc.parent_id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line  join account_account on account_move_line.account_id = account_account.id  where date < '"""+self.date_from+"""' and parent_id = acc.parent_id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	)


	< 0 THEN round((
	    (
		(select COALESCE (sum(debit),0) from account_move_line  join account_account on account_move_line.account_id = account_account.id  where date < '"""+self.date_from+"""' and parent_id = acc.parent_id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line  join account_account on account_move_line.account_id = account_account.id  where date < '"""+self.date_from+"""' and parent_id = acc.parent_id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	),2) * -1  else 0 END "Balance O Credit"



      from account_move_line line

 join account_move mv on mv.id = line.move_id join
	account_account acc on acc.id = line.account_id join account_account p_acc on acc.parent_id = p_acc.id where line.date between '"""+self.date_from+"""' and '"""+self.date_to+"""' and  acc.parent_id  in """+parent_accounts_unique+"""
group by acc.parent_id,p_acc.code, p_acc.name order by p_acc.code
"""

        print(">>>>>>>>>>>>>>>>>>>>>>>>>>1 ",sql_query)
        data = {}
        self._cr.execute(sql_query)
        data.update({'query_result': self._cr.dictfetchall()})
        data.update({'report_type':self.report_type})
        data.update({'moves_state': self.target_moves})
        data.update({'time_now': fields.datetime.now()})
        data.update({'date_from': self.date_from})
        data.update({'date_to': self.date_to})
        data.update({'show_type': self.show_type})
        data.update({'initial_balance': self.initial_balance})

        # if lang not arabic then don't set dir to rtl in report CSS
        lang = 'en'

        if self._context.get('lang', 'en')[0:2] != 'en':
            lang = 'ar'

        data.update({'lang': lang})



        if self.account_id:
            data.update({'parent_account': self.account_id.code + " " + self.account_id.name})

        return self.env.ref('account_custom_report.action_trial_b').with_context(landscape=True).report_action(
            self, data=data)


        raise UserError(("Not Used"))



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

	(select round(COALESCE (sum(debit),0),2) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id) "Depit Op" ,
	(select round(COALESCE (sum(credit),0),2) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id) "Credit Op",
	round(COALESCE (sum(debit),0),2) "Movements-Debit" ,
	round(COALESCE (sum(credit),0),2) "Movements-Credit" ,
	round(COALESCE (sum(debit - credit),0),2) "Balance" ,
	round((
	   COALESCE ( (
		(select COALESCE (sum(debit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum(credit),0) ),0)
	),2) "Balance O"
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


	>= 0 THEN round((
	    (
		(select COALESCE (sum(debit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	),2)  else 0 END
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


	< 0 THEN round((
	    (
		(select COALESCE (sum(debit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id)
		 -
		(select COALESCE (sum(credit),0) from account_move_line where date < '""" + self.date_from + """' and account_id = acc.id)
	    )
			+
			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
	),2) * -1  else 0 END "Balance O Credit"




      from account_move_line line

 join account_move mv on mv.id = line.move_id join
	account_account acc on acc.id = line.account_id where line.date between '""" + self.date_from + """' and '""" + self.date_to + "' " + parent_account + """
group by acc.id order by acc.code
    """)


        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>222 ",sql)


        self._cr.execute(sql)
        data.update({'query_result':self._cr.dictfetchall()})
        data.update({'report_type': self.report_type})
        data.update({'moves_state': self.target_moves})
        data.update({'time_now': fields.datetime.now()})
        data.update({'date_from': self.date_from})
        data.update({'date_to': self.date_to})
        if self.account_id:
            data.update({'parent_account': self.account_id.code + " " +self.account_id.name})


        return self.env.ref('account_custom_report.action_trial_b').with_context(landscape=True).report_action(
            self, data=data)


class trialBalanceReportDetals(models.AbstractModel):
    _name = 'report.account_custom_report.trial_b'




    @api.model
    def get_report_values(self, docids, data=None):
        # print("ABSTRACT ", data)
        if len(data.get('query_result')) == 0 :
            raise UserError(_("No Data , this report cannot be printed."))




        return {
            'doc_ids': 1,
            'data': data,
            'docs': self.env['account.account'].search([('id', 'in',(1,2) )]),#data['ids']
            'get':self
        }



    def get_childs(self,parent_acc,date_from,date_to,target_moves):
        # print(">>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<COME HERE")
        parent_account = ''
        #if self.account_id:
        parent_account = " and acc.parent_id = " + str(parent_acc)
        #dont forget to add it
        if target_moves == 'post':
            parent_account += " and mv.state = 'posted'"

        sql = (""" select acc.code ,
        	acc.name ,

        	(select round(COALESCE (sum(debit),0),2) from account_move_line where date < '""" + date_from + """' and account_id = acc.id) "Depit Op" ,
        	(select round(COALESCE (sum(credit),0),2) from account_move_line where date < '""" + date_from + """' and account_id = acc.id) "Credit Op",
        	round(COALESCE (sum(debit),0),2) "Movements-Debit" ,
        	round(COALESCE (sum(credit),0),2) "Movements-Credit" ,
        	round(COALESCE (sum(debit - credit),0),2) "Balance" ,
        	(
        	   round(COALESCE ( (
        		(select COALESCE (sum(debit),0) from account_move_line where date < '""" + date_from + """' and account_id = acc.id)
        		 -
        		(select COALESCE (sum(credit),0) from account_move_line where date < '""" + date_from + """' and account_id = acc.id)
        	    )
        			+
        			( COALESCE (sum(debit),0) - COALESCE (sum(credit),0) ),0),2)
        	) "Balance O"
        	,
        	case when

        	(
        	    (
        		(select round(COALESCE (sum(debit),0),2) from account_move_line where date < '""" + date_from + """' and account_id = acc.id)
        		 -
        		(select round(COALESCE (sum(credit),0),2) from account_move_line where date < '""" + date_from + """' and account_id = acc.id)
        	    )
        			+
        			( round(COALESCE (sum(debit),0),2) - round(COALESCE (sum( credit),0),2) )
        	)


        	>= 0 THEN round((
        	    (
        		(select round(COALESCE (sum(debit),0),2) from account_move_line where date < '""" + date_from + """' and account_id = acc.id)
        		 -
        		(select round(COALESCE (sum(credit),0),2) from account_move_line where date < '""" + date_from + """' and account_id = acc.id)
        	    )
        			+
        			( round(COALESCE (sum(debit),0),2) - round(COALESCE (sum( credit),0),2) )
        	),2)  else 0 END
        	 "Balance O Depit"
        	,
        	case when

        	(
        	    (
        		(select COALESCE (sum(debit),0) from account_move_line where date < '""" + date_from + """' and account_id = acc.id)
        		 -
        		(select COALESCE (sum(credit),0) from account_move_line where date < '""" + date_from + """' and account_id = acc.id)
        	    )
        			+
        			( COALESCE (sum(debit),0) - COALESCE (sum( credit),0) )
        	)


        	< 0 THEN round((
        	    (
        		(select round(COALESCE (sum(debit),0),2) from account_move_line where date < '""" + date_from + """' and account_id = acc.id)
        		 -
        		(select round(COALESCE (sum(credit),0),2) from account_move_line where date < '""" + date_from + """' and account_id = acc.id)
        	    )
        			+
        			( round(COALESCE (sum(debit),0),2) - round(COALESCE (sum( credit),0),2) )
        	),2) * -1  else 0 END "Balance O Credit"




              from account_move_line line

         join account_move mv on mv.id = line.move_id join
        	account_account acc on acc.id = line.account_id where line.date between '""" + date_from + """' and '""" + date_to + "' " + parent_account + """
        group by acc.id order by acc.code
            """)

        self._cr.execute(sql)
        #data.update({'query_result': self._cr.dictfetchall()})
        return self._cr.dictfetchall()
