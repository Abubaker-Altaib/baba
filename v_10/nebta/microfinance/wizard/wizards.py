# -*- coding: utf-8 -*-
# Author : Mudathir Ahmed
# Part of Odoo. See LICENSE file for full copyright and licensing details.



from odoo import api, models, fields, exceptions, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


#########################General Instruction Apply for all wizard and render Here##############################
##vis and visvalue list to show and hide and write filters in report based on user choice
##filters list to collect domains that user want and report shows based on fillters domain
## Wizard model collect user choices and then send them to model render then render make search in models and show report ##information         
class wiz_portfolio_states_wizard(models.TransientModel):
    _name = 'wiz.portfolio.report.states'

    report_type = fields.Selection([('all', 'All Portfolios'), ('one', 'One Portfolio')], string="Report Type")
    portfolio_name = fields.Many2one('finance.portfolio', string='Portfolio')
    customer_id = fields.Many2many('res.partner', string='Customer')
    portfolio_id = fields.Many2many('finance.portfolio', string="Portfolio")

    """formula = fields.Selection([('all', 'All Formula'),('fixed_murabaha', 'Fixed Murabaha'), ('dec_murabaha', 'Decremental Murabaha'),
                                ('salam', 'Salam'), ('ejara', 'Ejara'), ('gard_hassan', 'Gard Hassan'),
                                ('estisnaa', 'Estisnaa'), ('mugawla', 'Mugawla'), ('mudarba', 'Mudarba'),
                                ('musharka', 'Musharka'), ('muzaraa', 'Muzaraa')], string='Formula')"""
    formula = fields.Many2many('finance.formula', string='Formulas')
    company_id = fields.Many2many('res.company', string="Branch", )
    sector_id = fields.Many2many('finance.sector', string='Sector')
    type = fields.Selection([('all', 'All Types'), ('individual', 'Individual'), ('group', 'Group')], default='all',
                            required=1)
    user_id = fields.Many2many('res.users', string="Officer", )

    start_date = fields.Date('Start Date', required=1)
    end_date = fields.Date('End Date', required=1, )

    def print_report(self):
        vis = [1, 1, 1, 1, 1, 1, 1, 1]
        visvalue = [0, 0, 0, 0, 0, 0, 0, 0]
        # filters = [('due_date', '>=', self.start_date),('due_date', '<=', self.end_date)]

        # order_filters = ['|', '&', ('first_due_date', '>=', self.start_date), ('first_due_date', '<=', self.end_date)]
        # order_filters += ['&', ('last_due_date', '>=', self.start_date), ('last_due_date', '<=', self.end_date)]

        portfolio_state_query = """
                                   select

		sum(amount_before_profit)
		 total_asl ,
		sum(profit_amount)
		 total_profit ,


		sum((case when inst.state = 'done' then  amount_before_profit
		 when   inst.receive_amount > 0 and inst.receive_amount < amount_before_profit then inst.receive_amount
		  when inst.receive_amount > 0 and inst.receive_amount > amount_before_profit then amount_before_profit else 0 END))
		  sdad_asl
		,sum((case when inst.state = 'done' then  profit_amount
		when inst.receive_amount > 0 and inst.receive_amount > amount_before_profit then inst.receive_amount - amount_before_profit  else 0 END))
		 sdad_profit
		,


		sum((case when inst.state = 'adverse' and inst.receive_amount <= inst.amount_before_profit then  amount_before_profit - receive_amount else 0 END))
		  adverse_asl
		,
		sum((case when inst.state = 'adverse' and inst.receive_amount <= inst.amount_before_profit then  profit_amount
		 when inst.state = 'adverse' and inst.receive_amount > inst.amount_before_profit then  (amount_before_profit + profit_amount) - receive_amount else 0 END))
		adverse_profit

		,
		sum((case when inst.state = 'adverse' or inst.state = 'done' or inst.state = 'delay' then  amount_before_profit else 0 END))
		  mostahag_asl
		,
		sum((case when inst.state = 'adverse' or inst.state = 'done' or inst.state = 'delay' then  profit_amount else 0 END))
		  mostahag_profit

		  ,

		sum((case when inst.state = 'adverse' and inst.receive_amount <= inst.amount_before_profit then  amount_before_profit - receive_amount else 0 END))
		  mhfaza_fe_khatar_asl
		  ,
		sum((case when inst.state = 'adverse' and inst.receive_amount <= inst.amount_before_profit then  profit_amount
		 when inst.state = 'adverse' and inst.receive_amount > inst.amount_before_profit then  (amount_before_profit + profit_amount) - receive_amount else 0 END))
		  mhfaza_fe_khatar_profit

from finance_installments inst join finance_approval app on inst.approval_id = app.id
			       join finance_visit vis on app.visit_id=vis.id
			       join finance_order ord on vis.order_id = ord.id
			       join res_partner partner on ord.partner_id = partner.id
			       join res_company company on ord.company_id = company.id
			       join res_users users on ord.user_id = users.id
			       join finance_portfolio portf on ord.portfolio_id = portf.id
			       join finance_sector sector on ord.sector_id=sector.id where
                    """

        mehfaza_fe_khatar = """ select sum(receive_amount) receive_amount,sum(mhfaza_fe_khatar_asl) mhfaza_fe_khatar_asl,sum(mhfaza_fe_khatar_profit) mhfaza_fe_khatar_profit from
(select

	count(*) over ( partition by app.id ) as count,
	app.id approval_id ,
	 inst.id inst_id,
	 inst.installment_no,
	 inst.amount_before_profit,
	 inst.profit_amount,
	 inst.amount,
	 inst.receive_amount,
	 inst.state,
	 (case when inst.state in ('adverse','delay') and inst.receive_amount <= inst.amount_before_profit then  amount_before_profit - receive_amount else 0 END)
		  mhfaza_fe_khatar_asl
		,
		(case when inst.state in ('adverse','delay') and inst.receive_amount <= inst.amount_before_profit then  profit_amount
		 when inst.state in ('adverse','delay') and inst.receive_amount > inst.amount_before_profit then  (inst.amount_before_profit + inst.profit_amount) - inst.receive_amount else 0 END)
		 mhfaza_fe_khatar_profit


from finance_installments inst join finance_approval app on inst.approval_id = app.id
			       join finance_visit vis on app.visit_id=vis.id
			       join finance_order ord on vis.order_id = ord.id
			       join res_partner partner on ord.partner_id = partner.id
			       join res_company company on ord.company_id = company.id
			       join res_users users on ord.user_id = users.id
			       join finance_portfolio portf on ord.portfolio_id = portf.id
			       join finance_sector sector on ord.sector_id=sector.id
where app.state ='in_progress' and inst.state in ('adverse','delay') and


 """
        mehfaza_fe_khatar_conditions = """  order by app.id,installment_no,inst.id
) as p_in_danger where count != 1 or(count = 1 and state = 'adverse') """

        individual_cus_count = """SELECT count(finance_order.id) FROM finance_order WHERE  (((finance_order.first_due_date >= '""" + self.start_date + """')  AND
       (finance_order.first_due_date <= '""" + self.end_date + """'))  OR
       ((finance_order.last_due_date >= '""" + self.start_date + """')  AND
       (finance_order.last_due_date <= '""" + self.end_date + """')))  AND
       (finance_order.type in ('individual'))
"""

        group_cus_count = """SELECT sum(finance_group_order.female)+sum(finance_group_order.male) FROM finance_order  join finance_group_order on finance_group_order.order_id=finance_order.id WHERE
        (((finance_order.first_due_date >= '""" + self.start_date + """')  AND
               (finance_order.first_due_date <= '""" + self.end_date + """'))  OR
               ((finance_order.last_due_date >= '""" + self.start_date + """')  AND
               (finance_order.last_due_date <= '""" + self.end_date + """')))  AND
               (finance_order.type in ('group'))"""

        query_conditions = """ """

        if self.customer_id:
            customer_report_ids = []
            customers = []

            for client in self.customer_id:
                customer_report_ids.append(client.id)
                customers.append(client.name)

            if len(customer_report_ids) == 1:
                portfolio_state_query += "partner.id in " + str(tuple((customer_report_ids))).replace(",", "") + " and "
                mehfaza_fe_khatar += "partner.id in " + str(tuple((customer_report_ids))).replace(",", "") + " and "
                query_conditions += "AND partner_id in " + str(tuple((customer_report_ids))).replace(",", "") + " "
            else:
                portfolio_state_query += "partner.id in " + str(tuple((customer_report_ids))) + " and "
                mehfaza_fe_khatar += "partner.id in " + str(tuple((customer_report_ids))) + " and "
                query_conditions += "AND partner_id in " + str(tuple((customer_report_ids))) + " "

            # order_filters.append(('partner_id', 'in', self.customer_id.ids))

            vis[1] = "['" + "','".join(customers) + "']"
            visvalue[1] = len(self.customer_id)

        if [line.id for line in self.formula] != []:
            ids = []
            for line in self.formula:
                if (line.code == 'murabaha' or line.code == 'buying_murabaha'):
                    ids.append('fixed_murabaha')
                    ids.append('dec_murabaha')
                else:
                    ids.append(line.code)
                visvalue[2] += 1

            if len(ids) == 1:
                portfolio_state_query += "app.formula in " + str(tuple((ids))).replace(",", "").replace("(u",
                                                                                                        "(") + " and "
                mehfaza_fe_khatar += "app.formula in " + str(tuple((ids))).replace(",", "").replace("(u",
                                                                                                    "(") + " and "
                query_conditions += "AND formula in " + str(tuple((ids))).replace(",", "").replace("(u", "(")
            else:
                portfolio_state_query += "app.formula in " + str(tuple((ids))).replace("(u", "(").replace("u'",
                                                                                                          "'") + " and "
                mehfaza_fe_khatar += "app.formula in " + str(tuple((ids))).replace("(u", "(").replace("u'",
                                                                                                      "'") + " and "
                query_conditions += "AND formula in " + str(tuple((ids))).replace("(u", "(").replace("u'", "'")

            # filters.append(('approval_id.visit_id.order_id.formula', 'in', ids))
            # order_filters.append(('formula', 'in', ids))
            s = ''
            for line in self.formula:
                s += '"' + line.name + '"'
            vis[2] = "[" + s.replace('""', '","') + "]"

        if self.company_id:
            companies = []
            company_report_ids = []
            for company in self.company_id:
                company_report_ids.append(company.id)
                companies.append(company.name)

            if len(company_report_ids) == 1:
                portfolio_state_query += "company.id in " + str(tuple((company_report_ids))).replace(",", "") + " and "
                mehfaza_fe_khatar += "company.id in " + str(tuple((company_report_ids))).replace(",", "") + " and "
                query_conditions += "AND company_id in " + str(tuple((company_report_ids))).replace(",", "")
            else:
                portfolio_state_query += "company.id in " + str(tuple((company_report_ids))) + " and "
                mehfaza_fe_khatar += "company.id in " + str(tuple((company_report_ids))) + " and "
                query_conditions += "AND company_id in " + str(tuple((company_report_ids)))

            # filters.append(('approval_id.visit_id.order_id.company_id', 'in', self.company_id.ids))
            # order_filters.append(('company_id', 'in', self.company_id.ids))

            vis[3] = "['" + "','".join(companies) + "']"
            visvalue[3] = len(self.company_id)

        if self.sector_id:
            sector_report_ids = []
            sectors = []
            for sector in self.sector_id:
                sector_report_ids.append(sector.id)
                sectors.append(sector.name)
            if len(sector_report_ids) == 1:
                portfolio_state_query += "sector.id in " + str(tuple((sector_report_ids))).replace(",", "") + " and "
                mehfaza_fe_khatar += "sector.id in " + str(tuple((sector_report_ids))).replace(",", "") + " and "
                query_conditions += "AND sector_id in " + str(tuple((sector_report_ids))).replace(",", "")
            else:
                portfolio_state_query += "sector.id in " + str(tuple((sector_report_ids))) + " and "
                mehfaza_fe_khatar += "sector.id in " + str(tuple((sector_report_ids))) + " and "
                query_conditions += "AND sector_id in " + str(tuple((sector_report_ids)))

            # filters.append(('approval_id.visit_id.order_id.sector_id', 'in', self.sector_id.ids))
            # order_filters.append(('sector_id', 'in', self.sector_id.ids))

            vis[4] = "['" + "','".join(sectors) + "']"
            visvalue[4] = len(self.sector_id)

        if (self.type == 'all'):

            portfolio_state_query += "ord.type in ('individual','group') and "
            mehfaza_fe_khatar += "ord.type in ('individual','group') and "
            # query_conditions += "AND type in ('individual','group')"

            # order_filters.append(('type', 'in', ['individual', 'group']))
            vis[5] = ['individual', 'group']
            visvalue[5] += 0
        else:
            portfolio_state_query += "ord.type in ('" + str(self.type) + "') and "
            mehfaza_fe_khatar += "ord.type in ('" + str(self.type) + "') and "
            # query_conditions += "AND type in ('"+str(self.type)+"') "


            # order_filters.append(('type', 'in', [self.type]))
            vis[5] = str([self.type]).replace("u", "")
            visvalue[5] += 1

        if self.user_id:
            user_report_ids = []
            users = []
            for user in self.user_id:
                user_report_ids.append(user.id)
                users.append(user.name)
            if len(user_report_ids) == 1:
                portfolio_state_query += "users.id in " + str(tuple((user_report_ids))).replace(",", "") + " and "
                mehfaza_fe_khatar += "users.id in " + str(tuple((user_report_ids))).replace(",", "") + " and "
                query_conditions += "AND user_id in " + str(tuple((user_report_ids))).replace(",", "")
            else:
                portfolio_state_query += "users.id in " + str(tuple((user_report_ids))) + " and "
                mehfaza_fe_khatar += "users.id in " + str(tuple((user_report_ids))).replace(",", "") + " and "
                query_conditions += "AND user_id in " + str(tuple((user_report_ids)))

            # order_filters.append(('user_id', 'in', self.user_id.ids))

            vis[6] = "['" + "','".join(users) + "']"
            visvalue[6] = len(self.user_id)

        if self.portfolio_id:
            portf_report_ids = []
            portfolios = []
            for portfolio in self.portfolio_id:
                portf_report_ids.append(portfolio.id)
                portfolios.append(portfolio.name)
            if len(portf_report_ids) == 1:
                portfolio_state_query += "portf.id in " + str(tuple((portf_report_ids))).replace(",", "") + " and "
                mehfaza_fe_khatar += "portf.id in " + str(tuple((portf_report_ids))).replace(",", "") + " and "
                query_conditions += "AND portfolio_id in " + str(tuple((portf_report_ids))).replace(",", "")
            else:
                portfolio_state_query += "portf.id in " + str(tuple((portf_report_ids))) + " and "
                mehfaza_fe_khatar += "portf.id in " + str(tuple((portf_report_ids))) + " and "
                query_conditions += "AND portfolio_id in " + str(tuple((portf_report_ids)))

            # filters.append(('approval_id.visit_id.order_id.portfolio_id', 'in', self.portfolio_id.ids))
            # order_filters.append(('portfolio_id', 'in', self.portfolio_id.ids))

            vis[7] = "['" + "','".join(portfolios) + "']"
            visvalue[7] = len(self.portfolio_id)

        portfolio_state_query += "inst.due_date >= '" + self.start_date + "' and "
        mehfaza_fe_khatar += "inst.due_date >= '" + self.start_date + "' and "

        portfolio_state_query += "inst.due_date <= '" + self.end_date + "'"
        mehfaza_fe_khatar += "inst.due_date <= '" + self.end_date + "'"

        self._cr.execute(portfolio_state_query)
        result = self._cr.fetchall()

        customer_count = 0
        total_asl = 0
        total_profit = 0
        sdad_asl = 0
        sdad_profit = 0
        adverse_asl = 0
        adverse_profit = 0
        mostahag_asl = 0
        mostahag_profit = 0
        mhfaza_fe_khatar_profit = 0
        mhfaza_fe_khatar_asl = 0
        standing_asl = 0
        standing_profit = 0
        adverse_asl_percentage_total = 0
        adverse_profit_percentage_total = 0
        adverse_asl_profit_percentage_total = 0
        adverse_asl_percentage_standing = 0
        adverse_profit_percentage_standing = 0
        adverse_asl_profit_percentage_standing = 0
        order_ids = []

        total_asl = result[0][0] or 0
        total_profit = result[0][1] or 0

        sdad_asl = result[0][2] or 0

        sdad_profit = result[0][3] or 0

        adverse_asl = result[0][4] or 0

        adverse_profit = result[0][5] or 0

        mostahag_asl = result[0][6] or 0
        mostahag_profit = result[0][7] or 0

        # mhfaza Fe khatar
        mehfaza_fe_khatar += mehfaza_fe_khatar_conditions

        self._cr.execute(mehfaza_fe_khatar)
        result = self._cr.fetchall()

        mhfaza_fe_khatar_asl = result[0][1] or 0

        mhfaza_fe_khatar_profit = result[0][2] or 0

        # to get customer count from selected order

        individual_cus_count += query_conditions
        self._cr.execute(individual_cus_count)
        result = self._cr.fetchall()
        individual_cus_count = result[0][0] or 0

        group_cus_count += query_conditions

        self._cr.execute(group_cus_count)
        result = self._cr.fetchall()

        group_cus_count = result[0][0] or 0

        customer_count = individual_cus_count + group_cus_count

        standing_asl = total_asl - sdad_asl
        standing_profit = total_profit - sdad_profit
        if (total_asl != 0):
            adverse_asl_percentage_total = round((adverse_asl / total_asl) * 100, 2)
        if (total_profit != 0):
            adverse_profit_percentage_total = round((adverse_profit / total_profit) * 100, 2)
        if ((total_profit + total_profit) != 0):
            adverse_asl_profit_percentage_total = round(
                (adverse_asl + adverse_profit) / (total_asl + total_profit) * 100, 2)
        if (standing_asl != 0):
            adverse_asl_percentage_standing = round((adverse_asl / standing_asl) * 100, 2)
        if (standing_profit != 0):
            adverse_profit_percentage_standing = round((adverse_profit / standing_profit) * 100, 2)
        if ((standing_asl + standing_profit) != 0):
            adverse_asl_profit_percentage_standing = round(
                (adverse_asl + adverse_profit) / (standing_asl + standing_profit) * 100, 2)

        datas = {
            'ids': '',
            'model': '',  # wizard model name
            # 'filters': filters,
            'vis': vis,
            'visvalue': visvalue,
            'date_start': self.start_date,
            'date_end': self.end_date,
            'customer_count': customer_count,
            'total_asl': total_asl,
            'total_profit': total_profit,
            'sdad_asl': sdad_asl,
            'sdad_profit': sdad_profit,
            'adverse_asl': adverse_asl,
            'adverse_profit': adverse_profit,
            'mostahag_asl': mostahag_asl,
            'mostahag_profit': mostahag_profit,
            'mhfaza_fe_khatar_profit': mhfaza_fe_khatar_profit,
            'mhfaza_fe_khatar_asl': mhfaza_fe_khatar_asl,
            'standing_asl': standing_asl,
            'standing_profit': standing_profit,
            'adverse_asl_percentage_total': adverse_asl_percentage_total,
            'adverse_profit_percentage_total': adverse_profit_percentage_total,
            'adverse_asl_profit_percentage_total': adverse_asl_profit_percentage_total,
            'adverse_asl_percentage_standing': adverse_asl_percentage_standing,
            'adverse_profit_percentage_standing': adverse_profit_percentage_standing,
            'adverse_asl_profit_percentage_standing': adverse_asl_profit_percentage_standing,

        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'microfinance.portfolio_state_report_document',  # module name.report template name
            'datas': datas,
        }


class ReportClassName(models.AbstractModel):
    _name = 'report.microfinance.portfolio_state_report_document'

    @api.model
    def render_html(self, docids, data):
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'finance.portfolio',
            'date_start': data['date_start'],
            'date_end': data['date_end'],
            'vis': data['vis'],
            'visvalue': data['visvalue'],
            'customer_count': data['customer_count'],
            'total_asl': data['total_asl'],
            'total_profit': data['total_profit'],
            'sdad_asl': data['sdad_asl'],
            'sdad_profit': data['sdad_profit'],
            'adverse_asl': data['adverse_asl'],
            'adverse_profit': data['adverse_profit'],
            'mostahag_asl': data['mostahag_asl'],
            'mostahag_profit': data['mostahag_profit'],
            'mhfaza_fe_khatar_profit': data['mhfaza_fe_khatar_profit'],
            'mhfaza_fe_khatar_asl': data['mhfaza_fe_khatar_asl'],
            'standing_asl': data['standing_asl'],
            'standing_profit': data['standing_profit'],
            'adverse_asl_percentage_total': data['adverse_asl_percentage_total'],
            'adverse_profit_percentage_total': data['adverse_profit_percentage_total'],
            'adverse_asl_profit_percentage_total': data['adverse_asl_profit_percentage_total'],
            'adverse_asl_percentage_standing': data['adverse_asl_percentage_standing'],
            'adverse_profit_percentage_standing': data['adverse_profit_percentage_standing'],
            'adverse_asl_profit_percentage_standing': data['adverse_asl_profit_percentage_standing'],
        }
        return self.env['report'].render('microfinance.portfolio_state_report_document', docargs)


class wiz_requests_wizard(models.TransientModel):
    _name = 'wiz.requests.report'

    report_type = fields.Selection([('1', 'All'),
                                    ('2', 'One Customer'),
                                    ('3', 'Formula'),
                                    ('4', 'Company'),
                                    ('5', 'Sector'),
                                    ('6', 'Finance Type'),
                                    ('7', 'Officer')], string="Report Type", required=1, default='1')
    customer_id = fields.Many2one('res.partner', string='Customer')

    formula = fields.Selection([('fixed_murabaha', 'Fixed Murabaha'), ('dec_murabaha', 'Decremental Murabaha'),
                                ('salam', 'Salam'), ('ejara', 'Ejara'), ('gard_hassan', 'Gard Hassan'),
                                ('estisnaa', 'Estisnaa'), ('mugawla', 'Mugawla'), ('mudarba', 'Mudarba'),
                                ('musharka', 'Musharka'), ('muzaraa', 'Muzaraa')], string='Formula')
    company_id = fields.Many2one('res.company', string="Branch", )
    sector_id = fields.Many2one('finance.sector', string='Sector')
    type = fields.Selection([('individual', 'Individual'), ('group', 'Group')])
    user_id = fields.Many2one('res.users', string="Officer", )

    start_date = fields.Date('Start Date', required=1, )
    end_date = fields.Date('End Date', required=1, )

    def print_requests(self):
        vis = [1, 1, 1, 1, 1, 1, 1]
        filters = []
        filters.append(('date', '>=', self.start_date))
        filters.append(('date', '<=', self.end_date))
        # if(self.report_type == '2' ):
        #    filters.append(('partner_id', '=', self.customer_id.id))
        if (self.report_type == '1'):
            vis[0] = 1

        if (self.report_type == '2'):
            vis[1] = self.customer_id.name
            filters.append(('partner_id', 'in', [self.customer_id.id]))

        if (self.report_type == '3'):
            vis[2] = self.formula
            filters.append(('formula', 'in', [self.formula]))

        if (self.report_type == '4'):
            vis[3] = self.company_id.name
            filters.append(('company_id', 'in', [self.company_id.id]))
        if (self.report_type == '5'):
            vis[4] = self.sector_id.name
            filters.append(('sector_id', 'in', [self.sector_id.id]))
        if (self.report_type == '6'):
            vis[5] = self.type
            filters.append(('type', 'in', [self.type]))
        if (self.report_type == '7'):
            vis[6] = self.user_id.name
            filters.append(('user_id', 'in', [self.user_id.id]))

        docs = self.env['finance.order'].search(filters)
        row = 1

        datas = {
            'ids': '',
            'model': '',  # wizard model name
            'context': {'start_date': self.start_date, 'end_date': self.end_date},
            'filters': filters,
            'vis': vis,
            'date_start': self.start_date,
            'date_end': self.end_date
        }
        dic = {
            'type': 'ir.actions.report.xml',
            'report_name': 'microfinance.requests_report_document',  # module name.report template name
            'datas': datas,
            'data': 'asdasda'

        }
        return dic


class ReportClassName(models.AbstractModel):
    _name = 'report.microfinance.requests_report_document'

    @api.model
    def render_html(self, docids, data):
        report_info = []

        docs = self.env['finance.order'].search([])
        row = 1
        for doc in docs:
            row += 1

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'finance.order',
            'docs': docs,
            'vis': data['vis'],
            'date_start': data['date_start'],
            'date_end': data['date_end']
        }

        return self.env['report'].render('microfinance.requests_report_document', docargs)


class ReportClassName(models.AbstractModel):
    _name = 'report.microfinance.approvals_approve_report_document'

    @api.model
    def render_html(self, docids, data):
        docs = self.env['finance.approval'].search([('id', '=', docids[0])])
        vis = [1, 1]
        for doc in docs:
            vis[0] = doc.visit_id.order_id.partner_id.code
            vis[1] = doc.visit_id.order_id.partner_id.name
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'finance.approval',
            'docs': docs,
            'vis': vis,
            'visvalue': [1, 1]
        }

        return self.env['report'].render('microfinance.approvals_approve_report_document', docargs)


class ReportClassName(models.AbstractModel):
    _name = 'report.microfinance.requests_obligation_report_document'

    @api.model
    def render_html(self, docids, data):
        report_info = []

        vis = [1, 1]
        docs = self.env['finance.individual.order'].search([('id', '=', docids[0])])
        for doc in docs:
            vis[0] = doc.partner_id.code
            vis[1] = doc.partner_id.name
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'finance.individual.order',
            'docs': docs,
            'vis': vis,
            'visvalue': [1, 1]

        }

        return self.env['report'].render('microfinance.requests_obligation_report_document', docargs)


class wiz_requests_advance_wizard(models.TransientModel):
    _name = 'wiz.requests.advance.report'

    report_type = fields.Selection([('1', 'All'),
                                    ('2', 'One Customer'),
                                    ('3', 'Formula'),
                                    ('4', 'Company'),
                                    ('5', 'Sector'),
                                    ('6', 'Finance Type'),
                                    ('7', 'Officer')], string="Report Type", required=1, default='1')
    customer_id = fields.Many2many('res.partner', string='Customer')
    formula = fields.Many2many('finance.formula', string='Formulas')
    company_id = fields.Many2many('res.company', string="Branch", )
    sector_id = fields.Many2many('finance.sector', string='Sector')
    type = fields.Selection([('all', 'All Types'), ('individual', 'Individual'), ('group', 'Group')], default='all',
                            required=1)
    user_id = fields.Many2many('res.users', string="Officer", )

    start_date = fields.Date('Start Date', required=1, )
    end_date = fields.Date('End Date', required=1, )

    def print_requests(self):
        # 0 zero 1 one 2 many
        vis = [1, 1, 1, 1, 1, 1, 1]
        visvalue = [0, 0, 0, 0, 0, 0, 0]
        filters = [('date', '>=', self.start_date), ('date', '<=', self.end_date)]

        if self.customer_id:
            filters.append(('partner_id', 'in', self.customer_id.ids))
            customers = [c.name for c in self.customer_id]
            vis[1] = "['" + "','".join(customers) + "']"
            visvalue[1] = len(self.customer_id)

        if [line.id for line in self.formula] != []:
            ids = []
            for line in self.formula:
                if (line.code == 'murabaha' or line.code == 'buying_murabaha'):
                    ids.append('fixed_murabaha')
                    ids.append('dec_murabaha')
                visvalue[2] += 1
            filters.append(('formula', 'in', ids))
            s = ''
            for line in self.formula:
                s += '"' + line.name + '"'
            vis[2] = "[" + s.replace('""', '","') + "]"

        if self.company_id:
            filters.append(('company_id', 'in', self.company_id.ids))
            companies = [c.name for c in self.company_id]
            vis[3] = "['" + "','".join(companies) + "']"
            visvalue[3] = len(self.company_id)

        if self.sector_id:
            filters.append(('sector_id', 'in', self.sector_id.ids))
            sectors = [c.name for c in self.sector_id]
            vis[4] = "['" + "','".join(sectors) + "']"
            visvalue[4] = len(self.sector_id)

        if (self.type == 'all'):
            filters.append(('type', 'in', ['individual', 'group']))
            vis[5] = ['individual', 'group']
            visvalue[5] += 0
        else:
            filters.append(('type', 'in', [self.type]))
            vis[5] = str([self.type]).replace("u", "")
            visvalue[5] += 1

        if self.env.user.has_group('microfinance.group_officer') and not self.env.user.has_group(
                'microfinance.group_general_manager') \
                and not self.env.user.has_group('microfinance.group_operation_manager') \
                and not self.env.user.has_group('microfinance.group_branch_manager') \
                and not self.env.user.has_group('microfinance.group_supervisor'):
            filters.append(('user_id', '=', self.env.user.id))
            users = self.env.user.name
            vis[6] = "['" + users + "']"
            visvalue[6] = 2
        else:
            if self.user_id:
                filters.append(('user_id', 'in', self.user_id.ids))
                users = [c.name for c in self.user_id]
                vis[6] = "['" + "','".join(users) + "']"
                visvalue[6] = len(self.user_id)
                # filters.append(('user_id', '=', 19))

        datas = {
            'ids': '',
            'context': {'start_date': self.start_date, 'end_date': self.end_date},
            'filters': filters,
            'vis': vis,
            'date_start': self.start_date,
            'date_end': self.end_date,
            'visvalue': visvalue
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'microfinance.requests_advance_report_document',
            'datas': datas,
        }


class ReportClassName(models.AbstractModel):
    _name = 'report.microfinance.requests_advance_report_document'

    @api.model
    def render_html(self, docids, data):
        docs = self.env['finance.order'].search(data['filters'])
	
        if not docs:
            raise exceptions.ValidationError(_('No Data!!'))
	
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'finance.order',
            'docs': docs,
            'vis': data['vis'],
            'date_start': data['date_start'],
            'date_end': data['date_end'],
            'visvalue': data['visvalue']
        }
        return self.env['report'].render('microfinance.requests_advance_report_document', docargs)


class wiz_approvals_advance_wizard(models.TransientModel):
    _name = 'wiz.approvals.advance.report'

    approval_ids = fields.Many2many('finance.approval', string="Approval")
    customer_id = fields.Many2many('res.partner', string='Customer')

    formula = fields.Many2many('finance.formula', string='Formulas')
    company_id = fields.Many2many('res.company', string="Branch", )
    sector_id = fields.Many2many('finance.sector', string='Sector')
    type = fields.Selection([('all', 'All Types'), ('individual', 'Individual'), ('group', 'Group')], default='all',
                            required=1)
    portfolio_id = fields.Many2many('finance.portfolio', string="Portfolio")
    user_id = fields.Many2many('res.users', relation='user_rel', string="Officer", )
    approval_user_id = fields.Many2many('res.users', relation='appuser_rel', string="Approved By")

    approve_amount_select = fields.Selection(
        [('equal', 'Equal'), ('more_than', 'More Than'), ('more_than_eq', 'More Than and Equal'),
         ('less_than', 'Less Than'), ('less_than_eq', 'Less Than and Equal'), ('between', 'Between')])
    approve_amount_f = fields.Float(string='Approve Amount First')
    approve_amount_s = fields.Float(string='Approve Amount Second')
    start_date = fields.Date('Start Date', required=1, )
    end_date = fields.Date('End Date', required=1, )

    def print_approvals(self):

        vis = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        visvalue = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        filters = []
        filters.append(('visit_id.date', '>=', self.start_date))
        filters.append(('visit_id.date', '<=', self.end_date))

        if self.approve_amount_select != False:
            if self.approve_amount_select == 'equal':
                filters.append(('approve_amount', '=', self.approve_amount_f))
                vis[7] = str(['Equal ', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'more_than':
                filters.append(('approve_amount', '>', self.approve_amount_f))
                vis[7] = str(['More Than ', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'more_than_eq':
                filters.append(('approve_amount', '>=', self.approve_amount_f))
                vis[7] = str(['More Than and Equal', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'less_than':
                filters.append(('approve_amount', '<', self.approve_amount_f))
                vis[7] = str(['Less Than ', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'less_than_eq':
                filters.append(('approve_amount', '>=', self.approve_amount_f))
                vis[7] = str(['Less Than and Equal', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'between':
                filters.append(('approve_amount', '>=', self.approve_amount_f))
                filters.append(('approve_amount', '<=', self.approve_amount_s))
                vis[7] = str(['Between ' + str(self.approve_amount_f) + ' and ' + str(self.approve_amount_s)]).replace(
                    "u", "")
            if self.approve_amount_select == 'equal':
                visvalue[7] = 1
            else:
                visvalue[7] = 2
        if [line.id for line in self.approval_ids] != []:
            ids = []
            for line in self.approval_ids:
                ids.append(line.id)
                visvalue[1] += 1
            filters.append(('id', 'in', ids))
            s = ''
            for line in self.approval_ids:
                s += '"' + line.name + '"'
            vis[1] = "[" + s.replace('""', '","') + "]"

        if [line.id for line in self.formula] != []:
            ids = []
            for line in self.formula:
                if (line.code == 'murabaha' or line.code == 'buying_murabaha'):
                    ids.append('fixed_murabaha')
                    ids.append('dec_murabaha')
                visvalue[2] += 1
            filters.append(('formula', 'in', ids))
            s = ''
            for line in self.formula:
                s += '"' + line.name + '"'
            vis[2] = "[" + s.replace('""', '","') + "]"

        if [line.id for line in self.company_id] != []:
            ids = []
            for line in self.company_id:
                ids.append(line.id)
                visvalue[3] += 1
            filters.append(('visit_id.order_id.company_id', 'in', ids))
            s = ''
            for line in self.company_id:
                s += '"' + line.name + '"'
            vis[3] = "[" + s.replace('""', '","') + "]"

        if [line.id for line in self.sector_id] != []:
            ids = []
            for line in self.sector_id:
                ids.append(line.id)
                visvalue[4] += 1
            filters.append(('visit_id.order_id.sector_id', 'in', ids))
            s = ''
            for line in self.sector_id:
                s += '"' + line.name + '"'
            vis[4] = "[" + s.replace('""', '","') + "]"

        if (self.type == 'all'):
            filters.append(('visit_id.order_id.type', 'in', ['individual', 'group']))
            vis[5] = ['individual', 'group']
            visvalue[5] += 0
        else:
            filters.append(('visit_id.order_id.type', 'in', [self.type]))
            vis[5] = str([self.type]).replace("u", "")
            visvalue[5] += 1

        if self.env.user.has_group('microfinance.group_officer') and not self.env.user.has_group(
                'microfinance.group_general_manager') \
                and not self.env.user.has_group('microfinance.group_operation_manager') \
                and not self.env.user.has_group('microfinance.group_branch_manager') \
                and not self.env.user.has_group('microfinance.group_supervisor'):
            filters.append(('visit_id.order_id.user_id', '=', self.env.user.id))
            users = self.env.user.name
            vis[6] = "['" + users + "']"
            visvalue[6] = 1
        else:
            if [line.id for line in self.user_id] != []:
                ids = []
                for line in self.user_id:
                    ids.append(line.id)
                    visvalue[6] += 1
                filters.append(('visit_id.user_id', 'in', ids))
                s = ''
                for line in self.user_id:
                    s += '"' + line.name + '"'
                vis[6] = "[" + s.replace('""', '","') + "]"

        if [line.id for line in self.approval_user_id] != []:
            ids = []
            for line in self.approval_user_id:
                ids.append(line.id)
                visvalue[8] += 1
            filters.append(('user_id', 'in', ids))
            s = ''
            for line in self.approval_user_id:
                s += '"' + line.name + '"'
            vis[8] = "[" + s.replace('""', '","') + "]"

        if [line.id for line in self.portfolio_id] != []:
            ids = []
            for line in self.portfolio_id:
                ids.append(line.name)
                visvalue[9] += 1
            filters.append(('visit_id.order_id.portfolio_id', 'in', ids))
            s = ''
            for line in self.portfolio_id:
                s += '"' + line.name + '"'
            vis[9] = "[" + s.replace('""', '","') + "]"

        docs = self.env['finance.approval'].search(filters)

        # if report will show empty then show message
        if not docs:
            raise exceptions.ValidationError(
                _('No Data!!'))

        datas = {
            'ids': '',
            'model': '',  # wizard model name
            'context': {'start_date': self.start_date, 'end_date': self.end_date},
            'filters': filters,
            'vis': vis,
            'date_start': self.start_date,
            'date_end': self.end_date,
            'visvalue': visvalue
        }
        dic = {
            'type': 'ir.actions.report.xml',
            'report_name': 'microfinance.approvals_advance_report_document',  # module name.report template name
            'datas': datas,

        }
        return dic


class ReportClassName(models.AbstractModel):
    _name = 'report.microfinance.approvals_advance_report_document'

    @api.model
    def render_html(self, docids, data):
        docs = self.env['finance.approval'].search(data['filters'])

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'finance.approval',
            'docs': docs,
            'vis': data['vis'],
            'date_start': data['date_start'],
            'date_end': data['date_end'],
            'visvalue': data['visvalue']
        }

        return self.env['report'].render('microfinance.approvals_advance_report_document', docargs)


class ReportClassName(models.AbstractModel):
    _name = 'report.microfinance.visit_sign_report_document'

    @api.model
    def render_html(self, docids, data):
        visvalue = [1]
        vis = [1]
        docs = self.env['finance.approval'].search([('visit_id', '=', docids[0])])
        order_name = 1
        branch = ''
        for doc in docs:
            vis[0] = doc.visit_id.name
            order_name = doc.visit_id.order_id.name
            branch = doc.visit_id.order_id.company_id.name
        # datetime_now get cuurent time - 2 hours , so we add 2 hours
        hours = relativedelta(hours=2)
        current_date = datetime.strftime(datetime.now() + hours, '%Y-%m-%d %H:%M:%S')

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'finance.visit',
            'docs': docs,
            'vis': vis,
            'visvalue': visvalue,
            'order_name': order_name,
            'branch': branch,
            'current_date': current_date
        }

        return self.env['report'].render('microfinance.visit_sign_report_document', docargs)


class ReportClassName(models.AbstractModel):
    _name = 'report.microfinance.approval_sign_report_document'

    @api.model
    def render_html(self, docids, data):
        visvalue = [1]
        vis = [1]
        docs = self.env['finance.approval'].search([('id', '=', docids[0])])
        order_name = ''
        branch = ''
        for doc in docs:
            vis[0] = doc.visit_id.name
            order_name = doc.visit_id.order_id.name
            branch = doc.visit_id.order_id.company_id.name

        # datetime_now get cuurent time - 2 hours , so we add 2 hours
        hours = relativedelta(hours=2)
        current_date = datetime.strftime(datetime.now() + hours, '%Y-%m-%d %H:%M:%S')

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'finance.approval',
            'docs': docs,
            'vis': vis,
            'visvalue': visvalue,
            'order_name': order_name,
            'branch': branch,
            'current_date': current_date
        }

        return self.env['report'].render('microfinance.approval_sign_report_document', docargs)


class ReportClassName(models.AbstractModel):
    _name = 'report.microfinance.approval_payments_sign_report_document'

    @api.model
    def render_html(self, docids, data):
        visvalue = [1]
        vis = [1]
        docs = self.env['finance.approval'].search([('id', '=', docids[0])])
        order_name = ''
        branch = ''
        for doc in docs:
            vis[0] = doc.visit_id.name
            order_name = doc.visit_id.order_id.name
            branch = doc.visit_id.order_id.company_id.name

        # datetime_now get cuurent time - 2 hours , so we add 2 hours
        hours = relativedelta(hours=2)
        current_date = datetime.strftime(datetime.now() + hours, '%Y-%m-%d %H:%M:%S')

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'finance.approval',
            'docs': docs,
            'vis': vis,
            'visvalue': visvalue,
            'order_name': order_name,
            'branch': branch,
            'current_date': current_date
        }

        return self.env['report'].render('microfinance.approval_payments_sign_report_document', docargs)


class wiz_visit_advance_wizard(models.TransientModel):
    _name = 'wiz.visit.advance.report'

    approval_ids = fields.Many2many('finance.approval', string="Approval")
    customer_id = fields.Many2many('res.partner', string='Customer')

    formula = fields.Many2many('finance.formula', string='Formulas')
    company_id = fields.Many2many('res.company', string="Branch", )
    sector_id = fields.Many2many('finance.sector', string='Sector')
    type = fields.Selection([('all', 'All Types'), ('individual', 'Individual'), ('group', 'Group')], default='all',
                            required=1)
    user_id = fields.Many2many('res.users', relation='user_relll', string="Officer", )
    approval_user_id = fields.Many2many('res.users', relation='appuser_relll', string="Approved By")

    approve_amount_select = fields.Selection(
        [('equal', 'Equal'), ('more_than', 'More Than'), ('more_than_eq', 'More Than and Equal'),
         ('less_than', 'Less Than'), ('less_than_eq', 'Less Than and Equal'), ('between', 'Between')])
    approve_amount_f = fields.Float(string='Approve Amount First')
    approve_amount_s = fields.Float(string='Approve Amount Second')
    start_date = fields.Date('Start Date', required=1, )
    end_date = fields.Date('End Date', required=1, )

    def print_visit(self):
        vis = [1, 1, 1, 1, 1, 1, 1, 1, 1]
        visvalue = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        filters = [('visit_id.date', '>=', self.start_date), ('visit_id.date', '<=', self.end_date)]
        if self.approve_amount_select != False:
            if self.approve_amount_select == 'equal':
                filters.append(('approve_amount', '=', self.approve_amount_f))
                vis[7] = str(['Equal ', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'more_than':
                filters.append(('approve_amount', '>', self.approve_amount_f))
                vis[7] = str(['More Than ', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'more_than_eq':
                filters.append(('approve_amount', '>=', self.approve_amount_f))
                vis[7] = str(['More Than and Equal', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'less_than':
                filters.append(('approve_amount', '<', self.approve_amount_f))
                vis[7] = str(['Less Than ', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'less_than_eq':
                filters.append(('approve_amount', '>=', self.approve_amount_f))
                vis[7] = str(['Less Than and Equal', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'between':
                filters.append(('approve_amount', '>=', self.approve_amount_f))
                filters.append(('approve_amount', '<=', self.approve_amount_s))
                vis[7] = str(['Between ' + str(self.approve_amount_f) + ' and ' + str(self.approve_amount_s)]).replace(
                    "u", "")
            if self.approve_amount_select == 'equal':
                visvalue[7] = 1
            else:
                visvalue[7] = 2

        if self.approval_ids:
            filters.append(('id', 'in', self.approval_ids.ids))
            vis[1] = str([line.name for line in self.approval_ids]).replace("u", "")
            visvalue[1] = len(self.approval_ids)

        if self.formula:
            ids = []
            for line in self.formula:
                if (line.code == 'murabaha' or line.code == 'buying_murabaha'):
                    ids.append('fixed_murabaha')
                    ids.append('dec_murabaha')
            filters.append(('formula', 'in', ids))
            formulas = [c.name for c in self.formula]
            vis[2] = "['" + "','".join(formulas) + "']"
            visvalue[2] = len(self.formula)

        if self.company_id:
            filters.append(('visit_id.order_id.company_id', 'in', self.company_id.ids))
            companies = [c.name for c in self.company_id]
            vis[3] = "['" + "','".join(companies) + "']"
            visvalue[3] = len(self.company_id)

        if self.sector_id:
            filters.append(('visit_id.order_id.sector_id', 'in', self.sector_id.ids))
            sectors = [c.name for c in self.sector_id]
            vis[4] = "['" + "','".join(sectors) + "']"
            visvalue[4] = len(self.sector_id)

        if (self.type == 'all'):
            filters.append(('visit_id.order_id.type', 'in', ['individual', 'group']))
            vis[5] = ['individual', 'group']
            visvalue[5] += 0
        else:
            filters.append(('visit_id.order_id.type', 'in', [self.type]))
            vis[5] = str([self.type]).replace("u", "")
            visvalue[5] += 1

        if self.env.user.has_group('microfinance.group_officer') and not self.env.user.has_group(
                'microfinance.group_general_manager') \
                and not self.env.user.has_group('microfinance.group_operation_manager') \
                and not self.env.user.has_group('microfinance.group_branch_manager') \
                and not self.env.user.has_group('microfinance.group_supervisor'):
            filters.append(('user_id', '=', self.env.user.id))
            users = self.env.user.name
            vis[6] = "['" + users + "']"
            visvalue[6] = 2
        else:
            if self.user_id:
                filters.append(('user_id', 'in', self.user_id.ids))
                users = [c.name for c in self.user_id]
                vis[6] = "['" + "','".join(users) + "']"
                visvalue[6] = len(self.user_id)
        docs = self.env['finance.approval'].search(filters)
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>AAAA ", filters
        for doc in docs:
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", doc.id
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>bbbb "
        # =======================================================================
        # if [line.id for line in self.approval_user_id] != []:
        #     ids = []
        #     for line in self.approval_user_id:
        #         ids.append(line.id)
        #         visvalue[8] += 1
        #     filters.append(('user_id', 'in', ids))
        #     s = ''
        #     for line in self.approval_user_id:
        #         s += '"' + line.name + '"'
        #     vis[8] = "[" + s.replace('""', '","') + "]"
        # =======================================================================

        datas = {
            'ids': '',
            'model': '',  # wizard model name
            'context': {'start_date': self.start_date, 'end_date': self.end_date},
            'filters': filters,
            'vis': vis,
            'date_start': self.start_date,
            'date_end': self.end_date,
            'visvalue': visvalue
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'microfinance.visit_advance_report_document',  # module name.report template name
            'datas': datas,
        }


class ReportClassName(models.AbstractModel):
    _name = 'report.microfinance.visit_advance_report_document'

    @api.model
    def render_html(self, docids, data):
        docs = self.env['finance.approval'].search(data['filters'])
        if not docs:
            raise exceptions.ValidationError(_('No Data!!'))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'finance.approval',
            'docs': docs,
            'vis': data['vis'],
            'date_start': data['date_start'],
            'date_end': data['date_end'],
            'visvalue': data['visvalue']
        }

        return self.env['report'].render('microfinance.visit_advance_report_document', docargs)


class finance_approval_payment_state(models.Model):
    _name = 'finance.approval.payment.state'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")


class wiz_cheques_advance_wizard(models.TransientModel):
    _name = 'wiz.cheques.advance.report'

    approval_ids = fields.Many2many('finance.approval', string="Approval")
    customer_id = fields.Many2many('res.partner', string='Customer')

    formula = fields.Many2many('finance.formula', string='Formulas')
    company_id = fields.Many2many('res.company', string="Branch", )
    sector_id = fields.Many2many('finance.sector', string='Sector')
    type = fields.Selection([('all', 'All Types'), ('individual', 'Individual'), ('group', 'Group')], default='all',
                            required=1)

    state = fields.Many2many('finance.approval.payment.state', string='Cheaqu State')
    user_id = fields.Many2many('res.users', string="Officer", )
    portfolio_id = fields.Many2many('finance.portfolio', string="Portfolio")
    bank = fields.Many2many('account.journal', string="Banks", domain=[('type', '=', 'bank')])
    approve_amount_select = fields.Selection(
        [('equal', 'Equal'), ('more_than', 'More Than'), ('more_than_eq', 'More Than and Equal'),
         ('less_than', 'Less Than'), ('less_than_eq', 'Less Than and Equal'), ('between', 'Between')])
    approve_amount_f = fields.Float(string='Approve Amount ')
    approve_amount_s = fields.Float(string='Approve Amount Second')

    cheque_amount_select = fields.Selection(
        [('equal', 'Equal'), ('more_than', 'More Than'), ('more_than_eq', 'More Than and Equal'),
         ('less_than', 'Less Than'), ('less_than_eq', 'Less Than and Equal'), ('between', 'Between')])
    cheque_amount_f = fields.Float(string='Cheque Amount')
    cheque_amount_s = fields.Float(string='Cheque Amount Second')

    start_date = fields.Date('Cheque Start Date', required=1, )
    end_date = fields.Date('Cheque End Date', required=1, )

    def print_cheques(self):
        vis = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        visvalue = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        filters = []
        filters.append(('date', '>=', self.start_date))
        filters.append(('date', '<=', self.end_date))
        filters.append(('type', '=', 'check'))

        if self.approve_amount_select != False:
            if self.approve_amount_select == 'equal':
                filters.append(('approval_id.approve_amount', '=', self.approve_amount_f))
                vis[7] = str(['Equal ', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'more_than':
                filters.append(('approval_id.approve_amount', '>', self.approve_amount_f))
                vis[7] = str(['More Than ', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'more_than_eq':
                filters.append(('approval_id.approve_amount', '>=', self.approve_amount_f))
                vis[7] = str(['More Than and Equal', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'less_than':
                filters.append(('approval_id.approve_amount', '<', self.approve_amount_f))
                vis[7] = str(['Less Than ', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'less_than_eq':
                filters.append(('approval_id.approve_amount', '>=', self.approve_amount_f))
                vis[7] = str(['Less Than and Equal', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'between':
                filters.append(('approval_id.approve_amount', '>=', self.approve_amount_f))
                filters.append(('approval_id.approve_amount', '<=', self.approve_amount_s))
                vis[7] = str(['Between ' + str(self.approve_amount_f) + ' and ' + str(self.approve_amount_s)]).replace(
                    "u", "")
            if self.approve_amount_select == 'equal':
                visvalue[7] = 1
            else:
                visvalue[7] = 2

        if self.cheque_amount_select != False:
            if self.cheque_amount_select == 'equal':
                filters.append(('amount', '=', self.cheque_amount_f))
                vis[9] = str(['Equal ', self.cheque_amount_f]).replace("u", "")
            elif self.cheque_amount_select == 'more_than':
                filters.append(('amount', '>', self.cheque_amount_f))
                vis[9] = str(['More Than ', self.cheque_amount_f]).replace("u", "")
            elif self.cheque_amount_select == 'more_than_eq':
                filters.append(('amount', '>=', self.cheque_amount_f))
                vis[9] = str(['More Than and Equal', self.cheque_amount_f]).replace("u", "")
            elif self.cheque_amount_select == 'less_than':
                filters.append(('amount', '<', self.cheque_amount_f))
                vis[9] = str(['Less Than ', self.cheque_amount_f]).replace("u", "")
            elif self.cheque_amount_select == 'less_than_eq':
                filters.append(('amount', '>=', self.cheque_amount_f))
                vis[9] = str(['Less Than and Equal', self.cheque_amount_f]).replace("u", "")
            elif self.cheque_amount_select == 'between':
                filters.append(('amount', '>=', self.cheque_amount_f))
                filters.append(('amount', '<=', self.cheque_amount_s))
                vis[9] = str(['Between ' + str(self.cheque_amount_f) + ' and ' + str(self.cheque_amount_s)]).replace(
                    "u", "")
            if self.cheque_amount_select == 'equal':
                visvalue[9] = 1
            else:
                visvalue[9] = 2

        if [line.id for line in self.approval_ids] != []:
            ids = []
            for line in self.approval_ids:
                ids.append(line.id)
                visvalue[1] += 1
            filters.append(('approval_id.id', 'in', ids))
            s = ''
            for line in self.approval_ids:
                s += '"' + line.name + '"'
            vis[1] = "[" + s.replace('""', '","') + "]"

        if [line.id for line in self.formula] != []:
            ids = []
            for line in self.formula:
                if (line.code == 'murabaha' or line.code == 'buying_murabaha'):
                    ids.append('fixed_murabaha')
                    ids.append('dec_murabaha')
                visvalue[2] += 1
            filters.append(('approval_id.formula', 'in', ids))
            s = ''
            for line in self.formula:
                s += '"' + line.name + '"'
            vis[2] = "[" + s.replace('""', '","') + "]"

        if [line.id for line in self.company_id] != []:
            ids = []
            for line in self.company_id:
                ids.append(line.id)
                visvalue[3] += 1
            filters.append(('approval_id.visit_id.order_id.company_id', 'in', ids))
            s = ''
            for line in self.company_id:
                s += '"' + line.name + '"'
            vis[3] = "[" + s.replace('""', '","') + "]"

        if [line.id for line in self.sector_id] != []:
            ids = []
            for line in self.sector_id:
                ids.append(line.id)
                visvalue[4] += 1
            filters.append(('approval_id.visit_id.order_id.sector_id', 'in', ids))
            s = ''
            for line in self.sector_id:
                s += '"' + line.name + '"'
            vis[4] = "[" + s.replace('""', '","') + "]"

        if (self.type == 'all'):
            filters.append(('approval_id.visit_id.order_id.type', 'in', ['individual', 'group']))
            vis[5] = ['individual', 'group']
            visvalue[5] += 0
        else:
            filters.append(('approval_id.visit_id.order_id.type', 'in', [self.type]))
            vis[5] = str([self.type]).replace("u", "")
            visvalue[5] += 1

        if [line.code for line in self.state] != []:
            ids = []
            for line in self.state:
                ids.append(line.code)
                visvalue[11] += 1
            filters.append(('state', 'in', ids))
            s = ''
            for line in self.state:
                s += '"' + line.name + '"'
            vis[11] = "[" + s.replace('""', '","') + "]"

        if self.env.user.has_group('microfinance.group_officer') and not self.env.user.has_group(
                'microfinance.group_general_manager') \
                and not self.env.user.has_group('microfinance.group_operation_manager') \
                and not self.env.user.has_group('microfinance.group_branch_manager') \
                and not self.env.user.has_group('microfinance.group_supervisor'):
            filters.append(('approval_id.visit_id.order_id.user_id', '=', self.env.user.id))
            users = self.env.user.name
            vis[6] = "['" + users + "']"
            visvalue[6] = 2
        else:
            if [line.id for line in self.user_id] != []:
                ids = []
                for line in self.user_id:
                    ids.append(line.id)
                    visvalue[6] += 1
                filters.append(('approval_id.visit_id.order_id.user_id', 'in', ids))
                s = ''
                for line in self.user_id:
                    s += '"' + line.name + '"'
                vis[6] = "[" + s.replace('""', '","') + "]"

        if [line.id for line in self.portfolio_id] != []:
            ids = []
            for line in self.portfolio_id:
                ids.append(line.id)
                visvalue[10] += 1
            filters.append(('approval_id.visit_id.order_id.portfolio_id', 'in', ids))
            s = ''
            for line in self.portfolio_id:
                s += '"' + line.name + '"'
            vis[10] = "[" + s.replace('""', '","') + "]"

        if [line.id for line in self.bank] != []:
            ids = []
            for line in self.bank:
                ids.append(line.id)
                visvalue[12] += 1
            filters.append(('payment_id.journal_id', 'in', ids))
            s = ''
            for line in self.bank:
                s += '"' + line.name + '"'
            vis[12] = "[" + s.replace('""', '","') + "]"

        docs = self.env['finance.approval.payment'].search(filters)

        if not docs:
            raise exceptions.ValidationError(
                _('No Data!!'))

        datas = {
            'ids': '',
            'model': '',  # wizard model name
            'context': {'start_date': self.start_date, 'end_date': self.end_date},
            'filters': filters,
            'vis': vis,
            'date_start': self.start_date,
            'date_end': self.end_date,
            'visvalue': visvalue
        }
        dic = {
            'type': 'ir.actions.report.xml',
            'report_name': 'microfinance.cheques_advance_report_document',  # module name.report template name
            'datas': datas,

        }
        return dic


class ReportClassName(models.AbstractModel):
    _name = 'report.microfinance.cheques_advance_report_document'

    @api.model
    def render_html(self, docids, data):
        docs = self.env['finance.approval.payment'].search(data['filters'])
        row = 1
        for doc in docs:
            row += 1

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'finance.approval',
            'docs': docs,
            'vis': data['vis'],
            'date_start': data['date_start'],
            'date_end': data['date_end'],
            'visvalue': data['visvalue']
        }

        return self.env['report'].render('microfinance.cheques_advance_report_document', docargs)


class wiz_approvals_advance_done_wizard(models.TransientModel):
    _name = 'wiz.approvals.advance.done.report'

    approval_ids = fields.Many2many('finance.approval', string="Approval")
    customer_id = fields.Many2many('res.partner', string='Customer')

    formula = fields.Many2many('finance.formula', string='Formulas')
    company_id = fields.Many2many('res.company', string="Branch", )
    sector_id = fields.Many2many('finance.sector', string='Sector')
    type = fields.Selection([('all', 'All Types'), ('individual', 'Individual'), ('group', 'Group')], default='all',
                            required=1)
    portfolio_id = fields.Many2many('finance.portfolio', string="Portfolio")
    user_id = fields.Many2many('res.users', relation='user_rell', string="Officer", )
    approval_user_id = fields.Many2many('res.users', relation='appuser_rell', string="Approved By")

    approve_amount_select = fields.Selection(
        [('equal', 'Equal'), ('more_than', 'More Than'), ('more_than_eq', 'More Than and Equal'),
         ('less_than', 'Less Than'), ('less_than_eq', 'Less Than and Equal'), ('between', 'Between')],
        string='Standing Balance')
    approve_amount_f = fields.Float(string='Standing Balance First')
    approve_amount_s = fields.Float(string='Standing Balance Second')
    start_date = fields.Date('Start Date', required=1, )
    end_date = fields.Date('End Date', required=1, )

    def print_approvals(self):
        docs = self.env['finance.approval'].search([])
        vis = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        visvalue = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        filters = []
        filters.append(('done_date', '>=', self.start_date))
        filters.append(('done_date', '<=', self.end_date))
        filters.append(('state', '=', 'in_progress'))

        if self.approve_amount_select != False:
            if self.approve_amount_select == 'equal':
                filters.append(('standing_balance', '=', self.approve_amount_f))
                vis[7] = str(['Equal ', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'more_than':
                filters.append(('standing_balance', '>', self.approve_amount_f))
                vis[7] = str(['More Than ', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'more_than_eq':
                filters.append(('standing_balance', '>=', self.approve_amount_f))
                vis[7] = str(['More Than and Equal', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'less_than':
                filters.append(('standing_balance', '<', self.approve_amount_f))
                vis[7] = str(['Less Than ', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'less_than_eq':
                filters.append(('standing_balance', '>=', self.approve_amount_f))
                vis[7] = str(['Less Than and Equal', self.approve_amount_f]).replace("u", "")
            elif self.approve_amount_select == 'between':
                filters.append(('standing_balance', '>=', self.approve_amount_f))
                filters.append(('standing_balance', '<=', self.approve_amount_s))
                vis[7] = str(['Between ' + str(self.approve_amount_f) + ' and ' + str(self.approve_amount_s)]).replace(
                    "u", "")
            if self.approve_amount_select == 'equal':
                visvalue[7] = 1
            else:
                visvalue[7] = 2

        if [line.id for line in self.approval_ids] != []:
            ids = []
            for line in self.approval_ids:
                ids.append(line.id)
                visvalue[1] += 1
            filters.append(('id', 'in', ids))
            s = ''
            for line in self.approval_ids:
                s += '"' + line.name + '"'
            vis[1] = "[" + s.replace('""', '","') + "]"

        if [line.id for line in self.formula] != []:
            ids = []
            for line in self.formula:
                if (line.code == 'murabaha' or line.code == 'buying_murabaha'):
                    ids.append('fixed_murabaha')
                    ids.append('dec_murabaha')
                visvalue[2] += 1
            filters.append(('formula', 'in', ids))
            s = ''
            for line in self.formula:
                s += '"' + line.name + '"'
            vis[2] = "[" + s.replace('""', '","') + "]"

        if [line.id for line in self.portfolio_id] != []:
            ids = []
            for line in self.portfolio_id:
                ids.append(line.name)
                visvalue[9] += 1
            filters.append(('visit_id.order_id.portfolio_id', 'in', ids))
            s = ''
            for line in self.portfolio_id:
                s += '"' + line.name + '"'
            vis[9] = "[" + s.replace('""', '","') + "]"

        if [line.id for line in self.company_id] != []:
            ids = []
            for line in self.company_id:
                ids.append(line.id)
                visvalue[3] += 1
            filters.append(('visit_id.order_id.company_id', 'in', ids))
            s = ''
            for line in self.company_id:
                s += '"' + line.name + '"'
            vis[3] = "[" + s.replace('""', '","') + "]"

        if [line.id for line in self.sector_id] != []:
            ids = []
            for line in self.sector_id:
                ids.append(line.id)
                visvalue[4] += 1
            filters.append(('visit_id.order_id.sector_id', 'in', ids))
            s = ''
            for line in self.sector_id:
                s += '"' + line.name + '"'
            vis[4] = "[" + s.replace('""', '","') + "]"

        if (self.type == 'all'):
            filters.append(('visit_id.order_id.type', 'in', ['individual', 'group']))
            vis[5] = ['individual', 'group']
            visvalue[5] += 0
        else:
            filters.append(('visit_id.order_id.type', 'in', [self.type]))
            vis[5] = str([self.type]).replace("u", "")
            visvalue[5] += 1

        if self.env.user.has_group('microfinance.group_officer') and not self.env.user.has_group(
                'microfinance.group_general_manager') \
                and not self.env.user.has_group('microfinance.group_operation_manager') \
                and not self.env.user.has_group('microfinance.group_branch_manager') \
                and not self.env.user.has_group('microfinance.group_supervisor'):
            filters.append(('visit_id.order_id.user_id', '=', self.env.user.id))
            users = self.env.user.name
            vis[6] = "['" + users + "']"
            visvalue[6] = 2

        else:
            if [line.id for line in self.user_id] != []:
                ids = []
                for line in self.user_id:
                    ids.append(line.id)
                    visvalue[6] += 1
                filters.append(('visit_id.user_id', 'in', ids))
                s = ''
                for line in self.user_id:
                    s += '"' + line.name + '"'
                vis[6] = "[" + s.replace('""', '","') + "]"

        if [line.id for line in self.approval_user_id] != []:
            ids = []
            for line in self.approval_user_id:
                ids.append(line.id)
                visvalue[8] += 1
            filters.append(('user_id', 'in', ids))
            s = ''
            for line in self.approval_user_id:
                s += '"' + line.name + '"'
            vis[8] = "[" + s.replace('""', '","') + "]"

        docs = self.env['finance.approval'].search(filters)
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>AAAA ",filters
        for doc in docs:
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",doc.id
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>bbbb "
        if not docs:
            raise exceptions.ValidationError(
                _('No Data!!'))

        datas = {
            'ids': '',
            'model': '',  # wizard model name
            'context': {'start_date': self.start_date, 'end_date': self.end_date},
            'filters': filters,
            'vis': vis,
            'date_start': self.start_date,
            'date_end': self.end_date,
            'visvalue': visvalue
        }
        dic = {
            'type': 'ir.actions.report.xml',
            'report_name': 'microfinance.approvals_advance_done_report_document',  # module name.report template name
            'datas': datas,
        }

        return dic


class ReportClassName(models.AbstractModel):
    _name = 'report.microfinance.approvals_advance_done_report_document'

    @api.model
    def render_html(self, docids, data):
        docs = self.env['finance.approval'].search(data['filters'])

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'finance.approval',
            'docs': docs,
            'vis': data['vis'],
            'date_start': data['date_start'],
            'date_end': data['date_end'],
            'visvalue': data['visvalue']
        }

        return self.env['report'].render('microfinance.approvals_advance_done_report_document', docargs)
