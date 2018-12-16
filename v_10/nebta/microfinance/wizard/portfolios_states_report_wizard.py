from odoo import api, models, fields, exceptions, _


class wiz_portfolio_states_wizard(models.TransientModel):
    _name = 'wiz.portfolio.report.states'

    report_type = fields.Selection([('all', 'All Portfolios'), ('one', 'One Portfolio')], string="Report Type")
    portfolio_name = fields.Many2one('finance.portfolio', string='Portfolio')
    customer_id = fields.Many2many('res.partner', string='Customer')
    portfolio_id = fields.Many2many('finance.portfolio', string="Portfolio",required=1 )

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
        filters = []
        filters.append(('due_date', '>=', self.start_date))
        filters.append(('due_date', '<=', self.end_date))

        if [line.id for line in self.customer_id] != []:
            ids = []
            for line in self.customer_id:
                ids.append(line.id)
                visvalue[1] += 1
            filters.append(('approval_id.visit_id.order_id.partner_id', 'in', ids))
            vis[1] = str([line.name for line in self.customer_id]).replace("u", "")

        if [line.id for line in self.formula] != []:
            ids = []
            for line in self.formula:
                ids.append(line.code)
                visvalue[2] += 1
            filters.append(('approval_id.visit_id.order_id.formula', 'in', ids))
            vis[2] = str([line.name for line in self.formula]).replace("u", "")

        if [line.id for line in self.company_id] != []:
            ids = []
            for line in self.company_id:
                ids.append(line.id)
                visvalue[3] += 1
            filters.append(('approval_id.visit_id.order_id.company_id', 'in', ids))
            vis[3] = str([line.name for line in self.company_id]).replace("u", "")

        if [line.id for line in self.sector_id] != []:
            ids = []
            for line in self.sector_id:
                ids.append(line.id)
                visvalue[4] += 1
            filters.append(('approval_id.visit_id.order_id.sector_id', 'in', ids))
            vis[4] = str([line.name for line in self.sector_id]).replace("u", "")

        if (self.type == 'all'):
            filters.append(('approval_id.visit_id.order_id.type', 'in', ['individual', 'group']))
            vis[5] = ['individual', 'group']
            visvalue[5] += 0
        else:
            filters.append(('approval_id.visit_id.order_id.type', 'in', [self.type]))
            vis[5] = str([self.type]).replace("u", "")
            visvalue[5] += 1

        if [line.id for line in self.user_id] != []:
            ids = []
            for line in self.user_id:
                ids.append(line.id)
                visvalue[6] += 1
            filters.append(('approval_id.visit_id.order_id.user_id', 'in', ids))
            vis[6] = str([line.name for line in self.user_id]).replace("u", "")

        if [line.id for line in self.portfolio_id] != []:
            ids = []
            for line in self.portfolio_id:
                ids.append(line.name)
                visvalue[7] += 1
            filters.append(('approval_id.visit_id.order_id.portfolio_id', 'in', ids))
            vis[7] = str([line.name for line in self.portfolio_id]).replace("u", "")


        customer_count = 0
        total_asl = 0
        total_profit = 0
        sdad_asl = 0
        sdad_profit = 0
        adverse_asl = 0
        adverse_profit = 0
        mostahag_asl = 0
        mostahag_profit = 0
        standing_asl = 0
        standing_profit = 0
        adverse_asl_percentage_total = 0
        adverse_profit_percentage_total = 0
        adverse_asl_profit_percentage_total = 0
        adverse_asl_percentage_standing = 0
        adverse_profit_percentage_standing = 0
        adverse_asl_profit_percentage_standing = 0
        order_ids = []
        docs = self.env['finance.installments'].search(filters)
        row = 0

        for doc in docs:
            row += 1
            order_ids.append(doc.approval_id.visit_id.order_id.id)

            total_asl += doc.amount_before_profit
            total_profit += doc.profit_amount
            if doc.state == 'done':
                sdad_asl += doc.amount_before_profit
                sdad_profit += doc.profit_amount
            if doc.state == 'adverse':
                adverse_asl += doc.amount_before_profit
                adverse_profit += doc.profit_amount
            if doc.due_date <= fields.Date.today():
                mostahag_asl += doc.amount_before_profit
                mostahag_profit += doc.profit_amount

        #to get customer count from selected order
        for doc in self.env['finance.order'].search([('id','in',order_ids)]):

            if (doc.type == 'individual'):
                customer_count += 1
            else:
                for count in self.env['finance.group.order'].search(
                        [('order_id', '=', doc.id)]):
                    customer_count += count.male + count.female


        if row == 0:
            raise exceptions.ValidationError(
                    _('No Data'))

        standing_asl =  total_asl - sdad_asl
        standing_profit = total_profit - sdad_profit
        if(total_asl != 0):
            adverse_asl_percentage_total = round((adverse_asl / total_asl) * 100,2)
            adverse_profit_percentage_total = round((adverse_profit / total_profit) * 100,2)
            adverse_asl_profit_percentage_total = round((adverse_asl + adverse_profit) / (total_asl + total_profit) * 100,2)
        if(standing_asl != 0):
            adverse_asl_percentage_standing = round((adverse_asl / standing_asl) * 100,2)
            adverse_profit_percentage_standing = round((adverse_profit / standing_profit) * 100,2)
            adverse_asl_profit_percentage_standing = round((adverse_asl + adverse_profit) / (standing_asl + standing_profit) * 100,2)

        print ">>>>>>>>>>>>>>>> Customer Count ", customer_count
        print ">>>>>>>>>>>>>>>> ajmaly altamweel sum of asl ", total_asl
        print ">>>>>>>>>>>>>>>> ajmaly altamweel sum of profit ", total_profit
        print ">>>>>>>>>>>>>>>> alsdad_asl",sdad_asl
        print ">>>>>>>>>>>>>>>> alsdad_profit",sdad_profit
        print ">>>>>>>>>>>>>>>> adverse_asl", adverse_asl
        print ">>>>>>>>>>>>>>>> adverse_profit", adverse_profit
        print ">>>>>>>>>>>>>>>> mostahag_asl", mostahag_asl
        print ">>>>>>>>>>>>>>>> mostahag_profit", mostahag_profit
        print ">>>>>>>>>>>>>>>> Standing_asl", standing_asl
        print ">>>>>>>>>>>>>>>> Standing_profit", standing_profit
        print ">>>>>>>>>>>>>>>> %Adverse Asl from  ajmaly", adverse_asl_percentage_total
        print ">>>>>>>>>>>>>>>> %Adverse Profit from  ajmaly", adverse_profit_percentage_total
        print ">>>>>>>>>>>>>>>> %Adverse Asl from  Standing", adverse_asl_percentage_standing
        print ">>>>>>>>>>>>>>>> %Adverse Profit from  Standing", adverse_profit_percentage_standing




        datas = {
            'ids': '',
            'model': '',  # wizard model name
            'filters': filters,
            'vis': vis,
            'visvalue': visvalue,
            'date_start': self.start_date,
            'date_end': self.end_date,
            'customer_count':customer_count,
            'total_asl':total_asl,
            'total_profit':total_profit ,
            'sdad_asl':sdad_asl ,
            'sdad_profit':sdad_profit,
            'adverse_asl':adverse_asl,
            'adverse_profit':adverse_profit,
            'mostahag_asl':mostahag_asl,
            'mostahag_profit':mostahag_profit,
            'standing_asl':standing_asl ,
            'standing_profit':standing_profit,
            'adverse_asl_percentage_total':adverse_asl_percentage_total,
            'adverse_profit_percentage_total':adverse_profit_percentage_total,
            'adverse_asl_profit_percentage_total':adverse_asl_profit_percentage_total,
            'adverse_asl_percentage_standing':adverse_asl_percentage_standing ,
            'adverse_profit_percentage_standing':adverse_profit_percentage_standing,
            'adverse_asl_profit_percentage_standing': adverse_asl_profit_percentage_standing ,

            }
        dic = {
            'type': 'ir.actions.report.xml',
            'report_name': 'microfinance.portfolio_state_report_document',  # module name.report template name
            'datas': datas,

        }
        return dic

class ReportClassName(models.AbstractModel):
    _name = 'report.microfinance.portfolio_state_report_document'

    @api.model
    def render_html(self, docids, data):

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'finance.portfolio',
            'date_start':data['date_start'],
            'date_end':data['date_end'],
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

    start_date = fields.Date('Start Date', required=1,)
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

    start_date = fields.Date('Start Date', required=1,)
    end_date = fields.Date('End Date', required=1, )

    def print_requests(self):
        # 0 zero 1 one 2 many
        vis = [1, 1, 1, 1, 1, 1, 1]
        visvalue = [0, 0, 0, 0, 0, 0, 0]
        filters = []
        filters.append(('date', '>=', self.start_date))
        filters.append(('date', '<=', self.end_date))

        if [line.id for line in self.customer_id] != []:
            ids = []
            for line in self.customer_id:
                ids.append(line.id)
                visvalue[1] += 1
            filters.append(('partner_id', 'in', ids))
            vis[1] = str([line.name for line in self.customer_id]).replace("u", "")


        if [line.id for line in self.formula] != []:
            ids = []
            for line in self.formula:
                ids.append(line.code)
                visvalue[2] += 1
            filters.append(('formula', 'in', ids))
            vis[2] = str([line.code for line in self.formula]).replace("u", "")

        if [line.id for line in self.company_id] != []:
            ids = []
            for line in self.company_id:
                ids.append(line.id)
                visvalue[3] += 1
            filters.append(('company_id', 'in', ids))
            vis[3] = str([line.name for line in self.company_id]).replace("u", "")

        if [line.id for line in self.sector_id] != []:
            ids = []
            for line in self.sector_id:
                ids.append(line.id)
                visvalue[4] += 1
            filters.append(('sector_id', 'in', ids))
            vis[4] = str([line.name for line in self.sector_id]).replace("u", "")

        if (self.type == 'all'):
            filters.append(('type', 'in', ['individual', 'group']))
            vis[5] = ['individual', 'group']
            visvalue[5] += 0
        else:
            filters.append(('type', 'in', [self.type]))
            vis[5] = str([self.type]).replace("u", "")
            visvalue[5] += 1

        if [line.id for line in self.user_id] != []:
            ids = []
            for line in self.user_id:
                ids.append(line.id)
                visvalue[6] += 1
            filters.append(('user_id', 'in', ids))
            vis[6] = str([line.name for line in self.user_id]).replace("u", "")

        docs = self.env['finance.order'].search(filters)
        row = 0
        for doc in docs:
            row += 1
        if row == 0:
            raise exceptions.ValidationError(
                _('No Data!!'))

        """for doc in docs:
            print ">>>>>>>>>>>>>>>>>>>><< row:", row , doc.partner_id.id ,\
                doc.partner_id.code, \
                doc.partner_id.name, \
                doc.partner_id.gender, \
                doc.date, \
                doc.project_name, \
                doc.project_address, \
                doc.amount, \
                doc.formula, \
                doc.sector_id.name, \
                doc.type, \
                doc.user_id.name, \
                doc.company_id.name
            row += 1
        """


        datas = {
            'ids': '',
            'model': '',  # wizard model name
            # 'form': ['fffffff'],
            'context': {'start_date': self.start_date, 'end_date': self.end_date},
            'filters': filters,
            'vis': vis,
            'date_start': self.start_date,
            'date_end': self.end_date,
            'visvalue': visvalue
        }
        dic = {
            'type': 'ir.actions.report.xml',
            'report_name': 'microfinance.requests_advance_report_document',  # module name.report template name
            'datas': datas,

        }
        return dic


class ReportClassName(models.AbstractModel):
    _name = 'report.microfinance.requests_advance_report_document'

    @api.model
    def render_html(self, docids, data):

        docs = self.env['finance.order'].search(data['filters'])

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'finance.order',
            'docs': docs,
            # 'test' : {'ok':1,'ok2':2,'ok3':3},
            # 'mmm':'mmm',
            # 'taxesHeader': taxesHeader.values(),
            # 'taxes':taxes.values(),
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
    user_id = fields.Many2many('res.users', relation='user_rel', string="Officer", )
    approval_user_id = fields.Many2many('res.users', relation='appuser_rel', string="Approved By")

    approve_amount_select = fields.Selection(
        [('equal', 'Equal'), ('more_than', 'More Than'), ('more_than_eq', 'More Than and Equal'),
         ('less_than', 'Less Than'), ('less_than_eq', 'Less Than and Equal'), ('between', 'Between')])
    approve_amount_f = fields.Float(string='Approve Amount First')
    approve_amount_s = fields.Float(string='Approve Amount Second')
    start_date = fields.Date('Start Date', required=1,)
    end_date = fields.Date('End Date', required=1, )

    def print_approvals(self):

        vis = [1, 1, 1, 1, 1, 1, 1, 1, 1]
        visvalue = [0, 0, 0, 0, 0, 0, 0, 0, 0]
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
            vis[1] = str([line.name for line in self.approval_ids]).replace("u", "")


        if [line.id for line in self.formula] != []:
            ids = []
            for line in self.formula:
                ids.append(line.code)
                visvalue[2] += 1
            filters.append(('formula', 'in', ids))
            vis[2] = str([line.code for line in self.formula]).replace("u", "")

        if [line.id for line in self.company_id] != []:
            ids = []
            for line in self.company_id:
                ids.append(line.id)
                visvalue[3] += 1
            filters.append(('visit_id.order_id.company_id', 'in', ids))
            vis[3] = str([line.name for line in self.company_id]).replace("u", "")

        if [line.id for line in self.sector_id] != []:
            ids = []
            for line in self.sector_id:
                ids.append(line.id)
                visvalue[4] += 1
            filters.append(('visit_id.order_id.sector_id', 'in', ids))
            vis[4] = str([line.name for line in self.sector_id]).replace("u", "")

        if (self.type == 'all'):
            filters.append(('visit_id.order_id.type', 'in', ['individual', 'group']))
            vis[5] = ['individual', 'group']
            visvalue[5] += 0
        else:
            filters.append(('visit_id.order_id.type', 'in', [self.type]))
            vis[5] = str([self.type]).replace("u", "")
            visvalue[5] += 1
        if [line.id for line in self.user_id] != []:
            ids = []
            for line in self.user_id:
                ids.append(line.id)
                visvalue[6] += 1
            filters.append(('visit_id.order_id.user_id', 'in', ids))
            vis[6] = str([line.name for line in self.user_id]).replace("u", "")

        if [line.id for line in self.approval_user_id] != []:
            ids = []
            for line in self.approval_user_id:
                ids.append(line.id)
                visvalue[8] += 1
            filters.append(('user_id', 'in', ids))
            vis[8] = str([line.name for line in self.approval_user_id]).replace("u", "")

        docs = self.env['finance.approval'].search(filters)

        #if report will show empty show message
        row = 0
        for doc in docs:
            row += 1
        if row == 0:
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

        return self.env['report'].render('microfinance.approvals_advance_report_document', docargs)


class ReportClassName(models.AbstractModel):
    _name = 'report.microfinance.visit_sign_report_document'

    @api.model
    def render_html(self, docids, data):
        visvalue = [1]
        vis = [1]
        docs = self.env['finance.approval'].search([('visit_id', '=', docids[0])])
        row = 1
        for doc in docs:
            vis[0] = doc.visit_id.name
            row += 1

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'finance.visit',
            'docs': docs,
            'vis': vis,
            'visvalue': visvalue
        }

        return self.env['report'].render('microfinance.visit_sign_report_document', docargs)


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
    start_date = fields.Date('Start Date', required=1,)
    end_date = fields.Date('End Date', required=1, )

    def print_visit(self):
        vis = [1, 1, 1, 1, 1, 1, 1, 1, 1]
        visvalue = [0, 0, 0, 0, 0, 0, 0, 0, 0]
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
            vis[1] = str([line.name for line in self.approval_ids]).replace("u", "")

        if [line.id for line in self.formula] != []:
            ids = []
            for line in self.formula:
                ids.append(line.code)
                visvalue[2] += 1
            filters.append(('formula', 'in', ids))
            vis[2] = str([line.code for line in self.formula]).replace("u", "")

        if [line.id for line in self.company_id] != []:
            ids = []
            for line in self.company_id:
                ids.append(line.id)
                visvalue[3] += 1
            filters.append(('visit_id.order_id.company_id', 'in', ids))
            vis[3] = str([line.name for line in self.company_id]).replace("u", "")

        if [line.id for line in self.sector_id] != []:
            ids = []
            for line in self.sector_id:
                ids.append(line.id)
                visvalue[4] += 1
            filters.append(('visit_id.order_id.sector_id', 'in', ids))
            vis[4] = str([line.name for line in self.sector_id]).replace("u", "")

        if (self.type == 'all'):
            filters.append(('visit_id.order_id.type', 'in', ['individual', 'group']))
            vis[5] = ['individual', 'group']
            visvalue[5] += 0
        else:
            filters.append(('visit_id.order_id.type', 'in', [self.type]))
            vis[5] = str([self.type]).replace("u", "")
            visvalue[5] += 1
        print "self.user_id", [line.id for line in self.user_id] != []
        if [line.id for line in self.user_id] != []:
            ids = []
            for line in self.user_id:
                ids.append(line.id)
                visvalue[6] += 1
            filters.append(('user_id', 'in', ids))
            vis[6] = str([line.name for line in self.user_id]).replace("u", "")

        if [line.id for line in self.approval_user_id] != []:
            ids = []
            for line in self.approval_user_id:
                ids.append(line.id)
                visvalue[8] += 1
            filters.append(('user_id', 'in', ids))
            vis[8] = str([line.name for line in self.approval_user_id]).replace("u", "")

        docs = self.env['finance.approval'].search(filters)


        row = 0
        for doc in docs:
            row += 1
        if row == 0:
            raise exceptions.ValidationError(
                _('No Data!!'))


        datas = {
            'ids': '',
            'model': '',  # wizard model name
            # 'form': ['fffffff'],
            'context': {'start_date': self.start_date, 'end_date': self.end_date},
            'filters': filters,
            'vis': vis,
            'date_start': self.start_date,
            'date_end': self.end_date,
            'visvalue': visvalue
        }
        dic = {
            'type': 'ir.actions.report.xml',
            'report_name': 'microfinance.visit_advance_report_document',  # module name.report template name
            'datas': datas,

        }
        return dic


class ReportClassName(models.AbstractModel):
    _name = 'report.microfinance.visit_advance_report_document'

    @api.model
    def render_html(self, docids, data):

        docs = self.env['finance.approval'].search(data['filters'])
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
    portfolio_id = fields.Many2many('finance.portfolio', string="Portfolio", )
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

    start_date = fields.Date('Cheque Start Date', required=1,)
    end_date = fields.Date('Cheque End Date', required=1, )

    def print_cheques(self):
        vis = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        visvalue = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        filters = []
        filters.append(('date', '>=', self.start_date))
        filters.append(('date', '<=', self.end_date))

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
            vis[1] = str([line.name for line in self.approval_ids]).replace("u", "")

        if [line.id for line in self.formula] != []:
            ids = []
            for line in self.formula:
                ids.append(line.code)
                visvalue[2] += 1
            filters.append(('approval_id.formula', 'in', ids))
            vis[2] = str([line.code for line in self.formula]).replace("u", "")

        if [line.id for line in self.company_id] != []:
            ids = []
            for line in self.company_id:
                ids.append(line.id)
                visvalue[3] += 1
            filters.append(('approval_id.visit_id.order_id.company_id', 'in', ids))
            vis[3] = str([line.name for line in self.company_id]).replace("u", "")

        if [line.id for line in self.sector_id] != []:
            ids = []
            for line in self.sector_id:
                ids.append(line.id)
                visvalue[4] += 1
            filters.append(('approval_id.visit_id.order_id.sector_id', 'in', ids))
            vis[4] = str([line.name for line in self.sector_id]).replace("u", "")

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
            vis[11] = str([line.code for line in self.state]).replace("u", "")

        print "self.user_id", [line.id for line in self.user_id] != []
        if [line.id for line in self.user_id] != []:
            ids = []
            for line in self.user_id:
                ids.append(line.id)
                visvalue[6] += 1
            filters.append(('approval_id.visit_id.order_id.user_id', 'in', ids))
            vis[6] = str([line.name for line in self.user_id]).replace("u", "")

        if [line.id for line in self.portfolio_id] != []:
            ids = []
            for line in self.portfolio_id:
                ids.append(line.id)
                visvalue[10] += 1
            filters.append(('approval_id.visit_id.order_id.portfolio_id', 'in', ids))
            vis[10] = str([line.name for line in self.portfolio_id]).replace("u", "")

        if [line.id for line in self.bank] != []:
            ids = []
            for line in self.bank:
                ids.append(line.id)
                visvalue[12] += 1
            filters.append(('payment_id.journal_id', 'in', ids))
            vis[12] = str([line.name for line in self.bank]).replace("u", "")


        docs = self.env['finance.approval.payment'].search(filters)

        row = 0
        for doc in docs:
            row += 1
        if row == 0:
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
    portfolio_id = fields.Many2many('finance.portfolio', string="Portfolio", )
    user_id = fields.Many2many('res.users', relation='user_rell', string="Officer", )
    approval_user_id = fields.Many2many('res.users', relation='appuser_rell', string="Approved By")

    approve_amount_select = fields.Selection(
        [('equal', 'Equal'), ('more_than', 'More Than'), ('more_than_eq', 'More Than and Equal'),
         ('less_than', 'Less Than'), ('less_than_eq', 'Less Than and Equal'), ('between', 'Between')],
        string='Standing Balance')
    approve_amount_f = fields.Float(string='Standing Balance First')
    approve_amount_s = fields.Float(string='Standing Balance Second')
    start_date = fields.Date('Start Date', required=1,)
    end_date = fields.Date('End Date', required=1, )

    def print_approvals(self):
        docs = self.env['finance.approval'].search([])
        vis = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        visvalue = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        filters = []
        filters.append(('done_date', '>=', self.start_date))
        filters.append(('done_date', '<=', self.end_date))
        filters.append(('state', '=', 'done'))

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
            vis[1] = str([line.name for line in self.approval_ids]).replace("u", "")


        if [line.id for line in self.formula] != []:
            ids = []
            for line in self.formula:
                ids.append(line.code)
                visvalue[9] += 1
            filters.append(('formula', 'in', ids))
            vis[9] = str([line.code for line in self.formula]).replace("u", "")

        if [line.id for line in self.portfolio_id] != []:
            ids = []
            for line in self.portfolio_id:
                ids.append(line.name)
                visvalue[9] += 1
            filters.append(('visit_id.order_id.portfolio_id', 'in', ids))
            vis[9] = str([line.name for line in self.portfolio_id]).replace("u", "")

        if [line.id for line in self.company_id] != []:
            ids = []
            for line in self.company_id:
                ids.append(line.id)
                visvalue[3] += 1
            filters.append(('visit_id.order_id.company_id', 'in', ids))
            vis[3] = str([line.name for line in self.company_id]).replace("u", "")

        if [line.id for line in self.sector_id] != []:
            ids = []
            for line in self.sector_id:
                ids.append(line.id)
                visvalue[4] += 1
            filters.append(('visit_id.order_id.sector_id', 'in', ids))
            vis[4] = str([line.name for line in self.sector_id]).replace("u", "")

        if (self.type == 'all'):
            filters.append(('visit_id.order_id.type', 'in', ['individual', 'group']))
            vis[5] = ['individual', 'group']
            visvalue[5] += 0
        else:
            filters.append(('visit_id.order_id.type', 'in', [self.type]))
            vis[5] = str([self.type]).replace("u", "")
            visvalue[5] += 1

        if [line.id for line in self.user_id] != []:
            ids = []
            for line in self.user_id:
                ids.append(line.id)
                visvalue[6] += 1
            filters.append(('visit_id.user_id', 'in', ids))
            vis[6] = str([line.name for line in self.user_id]).replace("u", "")

        if [line.id for line in self.approval_user_id] != []:
            ids = []
            for line in self.approval_user_id:
                ids.append(line.id)
                visvalue[8] += 1
            filters.append(('user_id', 'in', ids))
            vis[8] = str([line.name for line in self.approval_user_id]).replace("u", "")

        docs = self.env['finance.approval'].search(filters)

        row = 0
        for doc in docs:
            row += 1
        if row == 0:
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

        return self.env['report'].render('microfinance.approvals_advance_done_report_document', docargs)
