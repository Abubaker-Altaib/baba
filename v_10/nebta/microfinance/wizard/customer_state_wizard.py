from odoo import api, models, fields, exceptions, _
from datetime import datetime
from dateutil.relativedelta import *


class CustomerState(models.TransientModel):
    _name = 'wiz.customer.state.report'

    @api.multi
    @api.onchange('company_id')
    def related_officer(self):
        """domain to return officer in specific branch"""
        ids = []
        if self.company_id:
            user_ids = self.env['res.users'].search([('company_id', '=', self.company_id.id)])
            for user in user_ids:
                ids.append(user.id)
        return {
            'domain': {
                'user_id': [('id', 'in', ids)],
            }
        }

    company_id = fields.Many2one('res.company', string="Branch")
    user_id = fields.Many2one('res.users', string="Officer",required=False)
    date_from = fields.Date(sting="From Date", required=True)
    date_to = fields.Date(string="To Date", required=True)
    state = fields.Selection([('deserved', 'Deserved'), ('draft', 'Draft'), ('delay', 'Delay'), ('adverse', 'Adverse'), ('done', 'Done')],
                             string='State', required=True)
    sector_id = fields.Many2one('finance.sector', string='Sector')
    formula = fields.Selection([('murabaha','Murabaha'), ('buying_murabaha','Buying Murabaha'),
                                ('salam', 'Salam'), ('ejara','Ejara'), ('gard_hassan','Gard Hassan'),
                                ('estisnaa','Estisnaa'), ('mugawla','Mugawla'), ('mudarba','Mudarba'),
                                ('musharka','Musharka'), ('muzaraa','Muzaraa') ], string='Formula')

    def get_rsd(self, partner_id):
        self._cr.execute("""select (case
                        when sum(amount) >= sum(receive_amount) then sum(amount) - sum(receive_amount) 
                        when sum(amount) <= sum(receive_amount) then sum(receive_amount) - sum(amount)
                        end) resd from finance_installments where partner_id="""+str(partner_id))
        result = self._cr.dictfetchall()
        return result[0]['resd']

    @api.multi
    def print_report(self):
        datas = {
            'ids': '',
            'model': '',
            'context': {
                'state': self.state,
                'st': dict(self.fields_get(allfields=['state'])['state']['selection'])[self.state],
                'sector': self.sector_id.id,
                'formula': self.formula,
                'branch_name': self.company_id.name,
                'user_name': self.user_id.name,
                'sector_name': self.sector_id.name,
                'user_id': self.user_id.id,
                'company_id': self.company_id.id,
                'sector_id': self.sector_id.id,
                'start_date': self.date_from,
                'end_date': self.date_to,
            },
        }

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'microfinance.customer_state_report_temp',
            'datas': datas,
        }



class CustomerStateReport(models.AbstractModel):
    _name = 'report.microfinance.customer_state_report_temp'

    @api.model
    def render_html(self, docids, data):
        """
        :param data: Passed value form wizard
        :return: generating report
        """
        # To Compute Installment
        ###########################
        report = self.env['report']
        customer_report = report._get_report_from_name('microfinance.customer_state_report_temp')
        company = data['context']['branch_name']
        state = data['context']['state']
        st = data['context']['st']
        user_id = False
        company_id = False
        if data['context']['user_id']:
            user_id = "ord.user_id="+str(data['context']['user_id'])+" and "
        sector_id = False
        if data['context']['sector_id']:
            sector_id = "ord.sector_id=" + str(data['context']['sector_id']) + " and "
        if data['context']['company_id']:
            company_id = "ord.company_id="+str(data['context']['company_id'])+" and "
        formula = False
        if data['context']['formula']:
            formula = "app.formula_clone='" +str(data['context']['formula'])+ "' and "

        if state in['delay', 'draft', 'adverse']:
            self._cr.execute("""
              select usprt.name officer,se.name sector , comp.name company_name,part.id partner_id,part.name,part.code code,count(inst.installment_no) ins_no,(sum(inst.amount_before_profit) / count(inst.amount_before_profit)) orgin
             ,(sum(inst.profit_amount) / count(inst.profit_amount)) profit,(sum(inst.amount) / count(inst.amount)) amount , sum(app.insurance_amount) insurance, app.formula_clone formula
              from finance_installments inst join res_partner part on inst.partner_id = part.id join finance_approval app on app.id = inst.approval_id join finance_visit vi on vi.id = app.id
              join finance_order ord on vi.order_id = ord.id join res_company comp on ord.company_id = comp.id join res_users us on ord.user_id = us.id join finance_sector se on se.id = ord.sector_id
              join res_partner usprt on us.partner_id = usprt.id join finance_approval_payment apm on apm.approval_id = app.id where """ + (company_id or '') + (user_id or '') + (sector_id or '') + (formula or '') + """inst.state = '""" + state + """'
              group by part.id,ord.id,comp.id,app.id ,usprt.id,se.id having max(apm.date) >= '""" + data['context']['start_date'] + """' 
              and max(apm.date) <= '""" + data['context']['end_date'] + """' order by part.id limit 4000
                          """)
        elif state == 'deserved':
            states = ('delay', 'adverse')
            self._cr.execute("""
          select usprt.name officer,se.name sector , comp.name company_name,part.id partner_id,part.name,part.code code,count(inst.installment_no) ins_no,(sum(inst.amount_before_profit) / count(inst.amount_before_profit)) orgin
         ,(sum(inst.profit_amount) / count(inst.profit_amount)) profit,(sum(inst.amount) / count(inst.amount)) amount , sum(app.insurance_amount) insurance, app.formula_clone formula
          from finance_installments inst join res_partner part on inst.partner_id = part.id join finance_approval app on app.id = inst.approval_id join finance_visit vi on vi.id = app.id
          join finance_order ord on vi.order_id = ord.id join res_company comp on ord.company_id = comp.id join res_users us on ord.user_id = us.id join finance_sector se on se.id = ord.sector_id
          join res_partner usprt on us.partner_id = usprt.id join finance_approval_payment apm on apm.approval_id = app.id where """ + (company_id or '') + (user_id or '') + (sector_id or '') + (formula or '') + """ inst.state in """+str(states)+""" 
          group by part.id,ord.id,comp.id,app.id ,usprt.id,se.id having max(apm.date) >= '""" + data['context']['start_date'] + """' 
          and max(apm.date) <= '""" + data['context']['end_date'] + """' order by part.id limit 4000
                      """)
        elif state == 'done':
            self._cr.execute("""
                      select usprt.name officer,se.name sector , comp.name company_name,part.id partner_id,part.name,part.code code,count(inst.installment_no) ins_no,(sum(inst.amount_before_profit) / count(inst.amount_before_profit)) orgin
                     ,(sum(inst.profit_amount) / count(inst.profit_amount)) profit,(sum(inst.amount) / count(inst.amount)) amount , sum(app.insurance_amount) insurance, app.formula_clone formula
                      from finance_installments inst join res_partner part on inst.partner_id = part.id join finance_approval app on app.id = inst.approval_id join finance_visit vi on vi.id = app.id
                      join finance_order ord on vi.order_id = ord.id join res_company comp on ord.company_id = comp.id join res_users us on ord.user_id = us.id join finance_sector se on se.id = ord.sector_id
                      join res_partner usprt on us.partner_id = usprt.id join finance_approval_payment apm on apm.approval_id = app.id where """ + (company_id or '') + (user_id or '') + (sector_id or '') + (formula or '') + """ app.state ='""" +state+ """'
                      group by part.id,ord.id,comp.id,app.id ,usprt.id,se.id having max(apm.date) >= '""" + data['context']['start_date'] + """' 
                      and max(apm.date) <= '""" + data['context']['end_date'] + """' order by part.id limit 4000
                                  """)
        result = self._cr.dictfetchall()
        row = 0
        if len(result) > 0:
            row += 1
        if row == 0:
            raise exceptions.ValidationError(_("there is no data"))
        docs = self.env['wiz.customer.state.report']
        date_time = datetime.strftime(datetime.now() + relativedelta(hours=2), "%Y-%m-%d %I:%M %p")
        docargs = {
            'doc_ids': self.ids,
            'doc_model': customer_report.model,
            'com': data['context']['branch_name'],
            'st': st,
            'doc': docs,
            'state': data['context']['state'],
            'date_time': date_time,
            'us': data['context']['user_name'],
            'se': data['context']['sector_name'],
            'fo': data['context']['formula'],
            'res': result,
            'e_date': data['context']['end_date'],
            's_date': data['context']['start_date'],

        }

        return report.render('microfinance.customer_state_report_temp', docargs)


class OneCustomerStateReport(models.AbstractModel):
    _name = 'report.microfinance.one_customer_state_report_temp'


    @api.model
    def render_html(self, docids, data):
        """
        :param data: Passed value form wizard
        :return: generating report
        """
        report = self.env['report']
        one_customer_report = report._get_report_from_name('microfinance.one_customer_state_report_temp')
        installment_ids = self.env['finance.installments'].search([('partner_id', 'in', docids)])
        partner_ids = self.env['res.partner'].search([('id', 'in', docids)])
        finance_order = self.env['finance.order'].search([('partner_id','in',docids)])
        date_time = datetime.strftime(datetime.now() + relativedelta(hours=2), "%Y-%m-%d %I:%M %p")

        if len(installment_ids) == 0:
            raise exceptions.ValidationError(_("There is no data"))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': one_customer_report.model,
            'docs': installment_ids,
            'date_time': date_time,
            'customer_name': partner_ids.name,
            'phone': partner_ids.mobile,
            'phone2': partner_ids.phone3,
            'phone3': partner_ids.phone,
            'code': partner_ids.code,
            'project': finance_order.project_name,
            'formula': dict(finance_order.fields_get(allfields=['formula_clone'])['formula_clone']['selection'])[finance_order.formula_clone],
            'project_address': finance_order.project_address,
            'address_description': partner_ids.address_description,
            'company': finance_order.company_id.name,

        }

        return report.render('microfinance.one_customer_state_report_temp', docargs)







