# -*- coding: utf-8 -*-

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from dateutil.relativedelta import *
from datetime import date, datetime, timedelta

class crossovered_Budget(models.Model):
    _inherit = 'crossovered.budget'


    def action_budget_validate(self):
        """
        very important to run analytic budget report correctly
        :return:
        """
        super(crossovered_Budget,self).action_budget_validate()

        for line in self.crossovered_budget_line:
            record = self.env['account.analytic.line'].create({
                'name': 'Draft Start',
                'date': self.date_from,
                'amount': 0,
                'account_id': self.analytic_account_id.id ,
                'general_account_id' : line.general_budget_id.account_id.id,
            })
            #not saved when created , *_* , so we must assigned after creation
            record.general_account_id = line.general_budget_id.account_id.id

            #raise UserError((">>>>>>>>ERROR"))


class AnalyticBudgetReportWizard(models.TransientModel):
    _name = 'analytic.budget.report.wizard'

    report_type = fields.Selection([('analytic', 'Analytic'), ('summation', 'Summation')],
                                   required=1, default="analytic")
    analytic_type = fields.Selection([('revenue', 'Revenue'), ('project', 'Project'), ('technical', 'Technical')],
                                     required=1, default='revenue')
    analytic_account_id = fields.Many2one('account.analytic.account')
    show_up_totals = fields.Boolean(string="Show Totals before details", default=True)
    group_totals = fields.Boolean()
    show_net_other_income = fields.Boolean()

    # parent_id = fields.Many2one('account.account', 'Parent Account')

    # default date is first day of the current year
    date_from = fields.Date(required=1, default=lambda self: date(date.today().year, 1, 1))
    # default date is last day of the current year
    date_to = fields.Date(required=1, default=lambda self: date(date.today().year, 12, 31))


    @api.onchange('group_totals')
    def set_show_net_other_income(self):
        if self.group_totals == False:
            self.show_net_other_income = False


    def print_report(self):
        """
        Print Analytic Budget Report Based on User Choices
        :return:
        """


        # Check if date from grater than date to
        if self.date_from > self.date_to:
            raise ValidationError(_("""You Must Set 'Date From' less Than 'Date To'."""))


        # set start up parameters
        params = [('account_id.analytic_type', '=', self.analytic_type),
                  ('date', '>=', self.date_from),
                  ('date', '<=', self.date_to),
                  ]

        # get first day of the year
        start_year_date = self.date_from[0:4]
        # get last day of the year
        end_year_date = self.date_to[0:4]

        if start_year_date != end_year_date:
            raise UserError(_("Plz , You must select two dates in the same year!"))

        # if user choose type analytic and select an analytic account then add ot to parameters
        if self.report_type == 'analytic' and self.analytic_account_id:
            params.append(('account_id', '=', self.analytic_account_id.id))




        # search
        budget_lines = self.env['account.analytic.line'].search(params)



        # if no data then raise exception to user
        if len(budget_lines) == 0:
            raise UserError(_("No Budget Data To Print!!"))

        # get all main parents accounts only
        accounts_parents = [line.general_account_id.parent_id.id for line in budget_lines]

        # get unique parents
        accounts_parents = tuple(set(accounts_parents))

        # to avoid comma that will trigger sql syntax error in query
        if len(accounts_parents) == 1:
            accounts_parents = str(accounts_parents).replace(",", "")

        # init data
        data = {}

        # get first day of year
        start_year_date = self.date_from[0:4]
        # get last day of year
        end_year_date = self.date_to[0:4]

        date_format = "%Y-%m-%d"
        start = datetime.strptime(self.date_from, date_format)
        end = datetime.strptime(self.date_to, date_format)
        days = end - start

        #print(">>>>>>>>>>>>>>>>>>>>>>>>>>DATE", (days.days + 1))

        # parent query
        sql_query = """
                select
                 account_parent.id ,
                 account_parent.code ,
                 account_parent.name ,
                 sum(amount)  practical ,

                 round((( select  sum(planned_amount) from
                crossovered_budget_lines crossbsubs
                 join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                 join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                 join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                 join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)
                 

                where accountsubs.parent_id = account_parent.id and analyticsubs.analytic_type = '"""+self.analytic_type+"""' and date_from between '""" + start_year_date + """-01-01' and '""" + end_year_date + """-12-31'
) / 365) * """ + str(days.days + 1) + """,2)  planned_amount  ,
sum(amount) -
round(
(( select  sum(planned_amount) from
                crossovered_budget_lines crossbsubs
                 join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                 join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                 join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                 join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)
                 

                where accountsubs.parent_id = account_parent.id and analyticsubs.analytic_type = '"""+self.analytic_type+"""' and date_from between '""" + start_year_date + """-01-01' and '""" + end_year_date + """-12-31'
) / 365 * """ + str(days.days + 1) + """),2) deviation ,


round((sum(amount) /

((( select  sum(planned_amount) from
                crossovered_budget_lines crossbsubs
                 join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                 join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                 join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                 join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)
                 

                where accountsubs.parent_id = account_parent.id and analyticsubs.analytic_type = '"""+self.analytic_type+"""' and date_from between '""" + start_year_date + """-01-01' and '""" + end_year_date + """-12-31'
) / 365) * """ + str(days.days + 1) + """))*100,2) percentage



from account_analytic_line line
 join account_analytic_account analytic on line.account_id = analytic.id
 join account_account account on line.general_account_id = account.id
 join account_account account_parent on (account.parent_id = account_parent.id)

 where account.parent_id in """ + str(accounts_parents) + """   and analytic.analytic_type = '"""+self.analytic_type+"""'  and
 date between '""" + self.date_from + """' and '""" + self.date_to + """'  group by account_parent.id

                 """




        data.update({'report_type': self.report_type})
        # if we not add new report type then the following if is useless
        #if self.report_type in ('analytic', 'summation'):
        # Execute Query
        self._cr.execute(sql_query)

        # get Query Result and save it in data 'parents_query_result'
        data.update({'parents_query_result': self._cr.dictfetchall()})

        data.update({'date_from': self.date_from})
        data.update({'date_to': self.date_to})
        data.update({'report_type': self.report_type})

        data.update({'analytic_type': self.analytic_type})
        data.update({'analytic_account': self.analytic_account_id.name})
        data.update({'show_up_totals': self.show_up_totals})
        data.update({'start_year_date': start_year_date})
        data.update({'end_year_date': end_year_date})
        data.update({'days_days': days.days})



        if self.group_totals == True:
            #print("!!!!!!!! >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> !!!!!!!!!")

            type_sql_query = """
                            select type.id type_id,
                             'Total Of '|| type.name account_name ,
                             sum(amount)  practical ,

                             round((( select  sum(planned_amount) from
                            crossovered_budget_lines crossbsubs
                             join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                             join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                             join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                             join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)
                             join  account_account_type typesubs on (accountsubs.user_type_id = typesubs.id)


                            where typesubs.id = type.id and analyticsubs.analytic_type = '"""+self.analytic_type+"""' and  date_from between '""" + start_year_date + """-01-01' and '""" + end_year_date + """-12-31'
            ) / 365) * """ + str(days.days + 1) + """,2)  planned_amount  ,
            sum(amount) -
            round(
            (( select  sum(planned_amount) from
                            crossovered_budget_lines crossbsubs
                             join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                             join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                             join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                             join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)
                             join  account_account_type typesubs on (accountsubs.user_type_id = typesubs.id)


                            where typesubs.id = type.id and analyticsubs.analytic_type = '"""+self.analytic_type+"""' and date_from between '""" + start_year_date + """-01-01' and '""" + end_year_date + """-12-31'
            ) / 365 * """ + str(days.days + 1) + """),2) deviation ,


            round((sum(amount) /

            ((( select  sum(planned_amount) from
                            crossovered_budget_lines crossbsubs
                             join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                             join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                             join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                             join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)
                             join  account_account_type typesubs on (accountsubs.user_type_id = typesubs.id)


                            where typesubs.id = type.id and analyticsubs.analytic_type = '"""+self.analytic_type+"""' and date_from between '""" + start_year_date + """-01-01' and '""" + end_year_date + """-12-31'
            ) / 365) * """ + str(days.days + 1) + """))*100,2) percentage



            from account_analytic_line line
             join account_analytic_account analytic on line.account_id = analytic.id
             join account_account account on line.general_account_id = account.id
             join account_account account_parent on (account.parent_id = account_parent.id)
             join  account_account_type type on (account.user_type_id = type.id)

             where account.parent_id in """ + str(accounts_parents) + """ and analytic.analytic_type = '"""+self.analytic_type+"""' and
             date between '""" + self.date_from + """' and '""" + self.date_to + """'  group by type.id ORDER BY type.name

                             """

            #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>type_sql_query ",type_sql_query)



            self._cr.execute(type_sql_query)
            data.update({'type_query_result': self._cr.dictfetchall()})
            data.update({'group_totals': self.group_totals})
            data.update({'accounts_group_parents': accounts_parents})
            #data.update({'group_totals_result_count': len(data['type_query_result'])})

            #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>QROUP TOTALS ",len(data['type_query_result']))

        if self.show_net_other_income == True:
            net_other_income_query = """

            select sum(debit-credit)
from account_move_line line
join account_account account on line.account_id = account.id
join account_account_type  type on account.user_type_id = type.id
join account_move move on line.move_id = move.id

where type.name = 'Other Income' and line.date <= '""" + self.date_to + """' and move.state = 'posted'"""
            #print(">>>>>>>>>>>>>>>>>>>>>QUERY ",net_other_income_query)
            self._cr.execute(net_other_income_query)
            result = self._cr.dictfetchall()

            if result[0]['sum'] != None:
                data.update({'net_other_income_query_result': result[0]['sum']})

            else:
                data.update({'net_other_income_query_result': 0})

            data.update({'show_net_other_income': self.show_net_other_income})





        return self.env.ref('account_budget_custom.action_analytic_budget_report').with_context(
            landscape=True).report_action(
            self, data=data)


class analyticBudgetReport(models.AbstractModel):
    _name = 'report.account_budget_custom.analytic_budget_report_tamplate'

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

    def get_parents_childs(self, date_from, date_to, parent_id,data_from):
        """
        Desc : Get budget accounts(childs) related to parent account,with budget data

        :param date_from:
        :param date_to:
        :param parent_id:
        :return:
        """

        #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>DATA ", date_from, date_to, parent_id,data_from['days_days'],data_from['start_year_date'], data_from['end_year_date'] )

        # get childs related to parent account with budget data

        sql_query = """

select
                 account.id ,
                 account.code ,
                 account.name ,
                 sum(amount)  practical ,

                 round((( select  sum(planned_amount) from
                crossovered_budget_lines crossbsubs
                 join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                 join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                 join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                 join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)
                 

                where accountsubs.id = account.id and analyticsubs.analytic_type = '"""+data_from['analytic_type']+"""' and date_from between '""" + data_from['start_year_date'] + """-01-01' and '""" + data_from['end_year_date'] + """-12-31'
) / 365) * """ + str(data_from['days_days'] + 1) + """,2)  planned_amount  ,
sum(amount) -
round(
(( select  sum(planned_amount) from
                crossovered_budget_lines crossbsubs
                 join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                 join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                 join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                 join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)
                 

                where accountsubs.id = account.id and analyticsubs.analytic_type = '"""+data_from['analytic_type']+"""' and date_from between '""" + data_from['start_year_date'] + """-01-01' and '""" + data_from['end_year_date'] + """-12-31'
) / 365 * """ + str(data_from['days_days'] + 1) + """),2) deviation ,


round((sum(amount) /

((( select  sum(planned_amount) from
                crossovered_budget_lines crossbsubs
                 join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                 join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                 join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                 join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)
                 

                where accountsubs.id = account.id and analyticsubs.analytic_type = '"""+data_from['analytic_type']+"""' and date_from between '""" + data_from['start_year_date'] + """-01-01' and '""" + data_from['end_year_date'] + """-12-31'
) / 365) * """ + str(data_from['days_days'] + 1) + """))*100,2) percentage



from account_analytic_line line
 join account_analytic_account analytic on line.account_id = analytic.id
 join account_account account on line.general_account_id = account.id
 join account_account account_parent on (account.parent_id = account_parent.id)

 where account.parent_id = """ + str(parent_id) + """ and analytic.analytic_type = '"""+data_from['analytic_type']+"""' and
 date between '""" + date_from + """' and '""" + date_to + """'  group by account.id

                    """

        #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>",sql_query)

        # Exceute query
        self._cr.execute(sql_query)

        # return result
        return self._cr.dictfetchall()

    def get_parents_analytics(self, date_from, date_to, parent_id,data_from):
        """
        Desc : Get all budget analytic accounts related to parent account
        :param date_from:
        :param date_to:
        :param parent_id:
        :return:
        """
        # parent query

        sql_query = """


select
                 analytic.id ,
                 analytic.code ,
                 analytic.name ,
                 sum(amount)  practical ,

                 round((( select  sum(planned_amount) from
                crossovered_budget_lines crossbsubs
                 join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                 join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                 join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                 join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)
                 

                where analyticsubs.id = analytic.id and analyticsubs.analytic_type = '"""+data_from['analytic_type']+"""' and date_from between '""" + data_from['start_year_date'] + """-01-01' and '""" + data_from['end_year_date'] + """-12-31'
) / 365) * """ + str(data_from['days_days'] + 1) + """,2)  planned_amount  ,
 sum(amount) -
round(
(( select  sum(planned_amount) from
                crossovered_budget_lines crossbsubs
                 join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                 join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                 join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                 join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)
                 

                where analyticsubs.id = analytic.id and analyticsubs.analytic_type = '"""+data_from['analytic_type']+"""' and date_from between '""" + data_from['start_year_date'] + """-01-01' and '""" + data_from['end_year_date'] + """-12-31'
) / 365 * """ + str(data_from['days_days'] + 1) + """),2) deviation ,


round((sum(amount) /

((( select  sum(planned_amount) from
                crossovered_budget_lines crossbsubs
                 join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                 join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                 join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                 join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)
                 

                where analyticsubs.id = analytic.id and analyticsubs.analytic_type = '"""+data_from['analytic_type']+"""' and date_from between '""" + data_from['start_year_date'] + """-01-01' and '""" + data_from['end_year_date'] + """-12-31'
) / 365) * """ + str(data_from['days_days'] + 1) + """))*100,2) percentage



from account_analytic_line line
 join account_analytic_account analytic on line.account_id = analytic.id
 join account_account account on line.general_account_id = account.id
 join account_account account_parent on (account.parent_id = account_parent.id)

 where account.parent_id = """ + str(parent_id) + """ and analytic.analytic_type = '"""+data_from['analytic_type']+"""' and
 date between '""" + date_from + """' and '""" + date_to + """'  group by analytic.id

    """



        # exceute query
        self._cr.execute(sql_query)

        # return result
        return self._cr.dictfetchall()

    def get_parents_analytics_net(self, date_from, date_to, parents_id, data_from):
        """
        Desc : Get all budget analytic accounts related to parent account
        :param date_from:
        :param date_to:
        :param parents_id:
        :return:
        """
        # parent query

        if len(parents_id) == 1:
            parents_id  = str(parents_id).replace(',','')

        sql_query = """


select
                 analytic.id ,
                 analytic.code ,
                 analytic.name ,
                 sum(amount)  practical ,

                 round((( select  sum(planned_amount) from
                crossovered_budget_lines crossbsubs
                 join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                 join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                 join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                 join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)


                where analyticsubs.id = analytic.id and analyticsubs.analytic_type = '"""+data_from['analytic_type']+"""' and date_from between '""" + data_from[
            'start_year_date'] + """-01-01' and '""" + data_from['end_year_date'] + """-12-31'
) / 365) * """ + str(data_from['days_days'] + 1) + """,2)  planned_amount  ,
 sum(amount) -
round(
(( select  sum(planned_amount) from
                crossovered_budget_lines crossbsubs
                 join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                 join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                 join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                 join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)


                where analyticsubs.id = analytic.id and analyticsubs.analytic_type = '"""+data_from['analytic_type']+"""' and date_from between '""" + data_from[
                        'start_year_date'] + """-01-01' and '""" + data_from['end_year_date'] + """-12-31'
) / 365 * """ + str(data_from['days_days'] + 1) + """),2) deviation ,


round((sum(amount) /

((( select  sum(planned_amount) from
                crossovered_budget_lines crossbsubs
                 join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                 join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                 join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                 join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)


                where analyticsubs.id = analytic.id and analyticsubs.analytic_type = '"""+data_from['analytic_type']+"""' and date_from between '""" + data_from[
                        'start_year_date'] + """-01-01' and '""" + data_from['end_year_date'] + """-12-31'
) / 365) * """ + str(data_from['days_days'] + 1) + """))*100,2) percentage



from account_analytic_line line
 join account_analytic_account analytic on line.account_id = analytic.id
 join account_account account on line.general_account_id = account.id
 join account_account account_parent on (account.parent_id = account_parent.id)

 where account.parent_id in """ + str(parents_id) + """ and analytic.analytic_type = '"""+data_from['analytic_type']+"""' and
 date between '""" + date_from + """' and '""" + date_to + """'  group by analytic.id order by analytic.code

    """
        #print(">>>>>>>>>>>>>>>>>>>>>>>>>>NEW QUERY ",sql_query)

        # exceute query
        self._cr.execute(sql_query)

        # return result
        return self._cr.dictfetchall()

    def get_cost_perc(self, date_from, date_to, data_from):
        #,data.get('accounts_group_parents')


        sql_query = """


select * ,result.Practical - result.Planned deviation, round( (result.Practical/case when result.Planned = 0 then 1 else result.Planned end)*100    ,2) perc from (


         select
 analytic.code ,
 analytic.name ,

  round(
  (

  case
  when COALESCE(sum(case when type.name = 'Expenses' then amount end),1) = 0 then 1
  else  COALESCE(sum(case when type.name = 'Expenses' then amount end),1) end)*100
  /
  COALESCE(sum(case when type.name = 'Income' then amount end),0)

  ,2) Practical

   ,

(
round(




      case when (( select  COALESCE(sum(case when typesubs.name = 'Expenses' then planned_amount end),0) from
                            crossovered_budget_lines crossbsubs
                             join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                             join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                             join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                             join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)
                             join  account_account_type typesubs on (accountsubs.user_type_id = typesubs.id)


                            where analyticsubs.id = analytic.id and analyticsubs.analytic_type = '"""+data_from['analytic_type']+"""' and  date_from between '""" + data_from[
                        'start_year_date'] + """-01-01' and '""" + data_from['end_year_date'] + """-12-31'
            ) / 365) * """ + str(data_from['days_days'] + 1) + """ = 0 then 1
else
(( select  COALESCE(sum(case when typesubs.name = 'Expenses' then planned_amount end),0) from
                            crossovered_budget_lines crossbsubs
                             join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                             join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                             join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                             join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)
                             join  account_account_type typesubs on (accountsubs.user_type_id = typesubs.id)


                            where analyticsubs.id = analytic.id and analyticsubs.analytic_type = '"""+data_from['analytic_type']+"""' and  date_from between '""" + data_from[
                        'start_year_date'] + """-01-01' and '""" + data_from['end_year_date'] + """-12-31'
            ) / 365) * """ + str(data_from['days_days'] + 1) + """

             end
/
           (  (( select  COALESCE(sum(case when typesubs.name = 'Income' then planned_amount end),0) from
                            crossovered_budget_lines crossbsubs
                             join account_budget_post postsubs on (crossbsubs.general_budget_id = postsubs.id)
                             join account_account accountsubs on (postsubs.account_id = accountsubs.id)
                             join account_account account_parensubst on (accountsubs.parent_id = account_parensubst.id)
                             join account_analytic_account analyticsubs on (crossbsubs.analytic_account_id = analyticsubs.id)
                             join  account_account_type typesubs on (accountsubs.user_type_id = typesubs.id)


                            where analyticsubs.id = analytic.id and analyticsubs.analytic_type = '"""+data_from['analytic_type']+"""' and  date_from between '""" + data_from[
            'start_year_date'] + """-01-01' and '""" + data_from['end_year_date'] + """-12-31'
            ) / 365) * """ + str(data_from['days_days'] + 1) + """ )


             ,2)* 100 ) Planned






           from account_analytic_line line
             join account_analytic_account analytic on line.account_id = analytic.id
             join account_account account on line.general_account_id = account.id
             join account_account account_parent on (account.parent_id = account_parent.id)
             join  account_account_type type on (account.user_type_id = type.id)

             where account.parent_id in """ + str(data_from.get('accounts_group_parents')).replace("[","(").replace("]",")") + """ and analytic.analytic_type = '"""+data_from['analytic_type']+"""'
              and date between '""" + date_from + """' and '""" + date_to + """' group by analytic.id order by analytic.code
        ) result """
        #print(">>>>>>>>>>>>>>>>>>>>>>>get_cost_perc ",sql_query)

        # exceute query
        self._cr.execute(sql_query)

        # return result
        return self._cr.dictfetchall()
