# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError, AccessError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class StatePercentageReport(models.TransientModel):
    _name = "state.percentage.wizard"

    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    state = fields.Many2many('zakat.state')

    @api.one
    @api.constrains('date_from', 'date_to')
    def validDate(self):
        if self.date_from:
            if self.date_to:
                if self.date_from < self.date_to:
                    print("this is the date from ,,,,,  ", self.date_from)
                else:
                    raise ValidationError(_("Date is no right"))

    def print_report(self, data):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'dzc2.project.request',
            'form': data
        }
        return self.env.ref('dzc_2.new_report_ho').report_action(self, data=datas)


class StatePercentageReportAbstract(models.AbstractModel):
    _name = 'report.dzc_2.state_per_rerport'

    @api.model
    def get_report_values(self, docids, data):
        if data['form']['date_from'] and data['form']['date_to'] and data['form']['state']:
            year_from = str(datetime.strptime(data['form']['date_from'], '%Y-%m-%d').year) + "-01-01"
            year_to = str(datetime.strptime(data['form']['date_to'], '%Y-%m-%d').year) + "-12-31"
            states = data['form']['state']
            list_of_plan_idss = self.env['dzc2.project.planning'].search(
                ['&', ('duration_from', '>=', year_from), ('duration_to', '<=', year_to)])
            if not list_of_plan_idss:
                raise UserError(_("Sorry ! There is no data to display."))
            plan_ids = []
            budget = []
            total = []
            state_persent = 0.0
            total_persent = 0.0
            for x in list_of_plan_idss:
                for i in x.plan_ids:
                    if i.state_plan_ids.id in states:
                        state_persent = i.execute_from_projects / x.total_execued_projects * 100
                        total_persent += state_persent
                        budget.append({'state': i.state_plan_ids.name, 'percentage': state_persent})
                        print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-", budget)
                if len(budget) != 0:
                    print("this is the = ", len(budget))
                    total.append({'total_per': total_persent})
                    plan_ids.append(
                        {'year': datetime.strptime(x.duration_from, "%Y-%m-%d").year, 'bud': budget, 'total': total})
                    print("==========------------00000000000=============", plan_ids)
                budget = []
                total_persent = 0
        elif data['form']['date_from'] and data['form']['date_to'] and not data['form']['state']:
            year_from = str(datetime.strptime(data['form']['date_from'], '%Y-%m-%d').year) + "-01-01"
            year_to = str(datetime.strptime(data['form']['date_to'], '%Y-%m-%d').year) + "-12-31"
            list_of_plan_idss = self.env['dzc2.project.planning'].search(
                ['&', ('duration_from', '>=', year_from), ('duration_to', '<=', year_to)])
            if not list_of_plan_idss:
                raise UserError(_("Sorry ! There is no data to display."))
            plan_ids = []
            budget = []
            total = []
            state_persent = 0.0
            total_persent = 0.0
            for x in list_of_plan_idss:
                for i in x.plan_ids:
                    state_persent = i.execute_from_projects / x.total_execued_projects * 100
                    total_persent += state_persent
                    budget.append({'state': i.state_plan_ids.name, 'percentage': state_persent})
                    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-", budget)
                if len(budget) != 0:
                    print("this is the = ", len(budget))
                    total.append({'total_per': total_persent})
                    plan_ids.append(
                        {'year': datetime.strptime(x.duration_from, "%Y-%m-%d").year, 'bud': budget, 'total': total})
                    print("==========------------00000000000=============", plan_ids)
                budget = []
                total_persent = 0
        # elif data['form']['date_from'] and not data['form']['date_to'] and data['form']['state'] :
        #     year_from = str(datetime.strptime(data['form']['date_from'], '%Y-%m-%d').year)+"-01-01"
        #     states = data['form']['state']
        #     list_of_plan_idss = self.env['dzc2.project.planning'].search([('duration_from','>=',year_from)])
        #     if not list_of_plan_idss:
        #         raise UserError(_("Sorry ! There is no data to display."))
        #     plan_ids = []
        #     budget = []
        #     total = []
        #     total_persent = 0.0
        #     for x in list_of_plan_idss:
        #         for i in x.plan_ids:
        #             if i.state_plan_ids.id in states:
        #                 total_persent += i.share_from_projects
        #                 budget.append({'state':i.state_plan_ids.name,'percentage':i.share_from_projects})
        #         if len(budget)!=0:
        #             total.append({'total_per':total_persent })
        #             plan_ids.append({'year':datetime.strptime(x.duration_from,"%Y-%m-%d").year,'bud':budget , 'total':total})
        #         budget = []
        #         total_persent = 0
        # elif data['form']['date_to'] and not data['form']['date_from'] and data['form']['state'] :
        #     year_to = str(datetime.strptime(data['form']['date_to'], '%Y-%m-%d').year)+"-12-31"
        #     states = data['form']['state']
        #     list_of_plan_idss = self.env['dzc2.project.planning'].search([('duration_to','<=',year_to)])
        #     if not list_of_plan_idss:
        #         raise UserError(_("Sorry ! There is no data to display."))
        #     plan_ids = []
        #     budget = []
        #     total = []
        #     total_persent = 0.0
        #     for x in list_of_plan_idss:
        #         for i in x.plan_ids:              
        #             if i.state_plan_ids.id in states:
        #                 total_persent += i.share_from_projects
        #                 budget.append({'state':i.state_plan_ids.name,'percentage':i.share_from_projects})
        #         if len(budget)!=0:
        #             total.append({'total_per':total_persent })
        #             plan_ids.append({'year':datetime.strptime(x.duration_from,"%Y-%m-%d").year,'bud':budget , 'total':total})
        #         budget = []
        #         total_persent = 0
        # elif not data['form']['date_from'] and not data['form']['date_to'] and data['form']['state'] :
        #     states = data['form']['state']
        #     list_of_plan_idss = self.env['dzc2.project.planning'].search([('duration_from','>=',"1000-01-01")])
        #     if not list_of_plan_idss:
        #         raise UserError(_("Sorry ! There is no data to display."))
        #     plan_ids = []
        #     budget = []
        #     total = []
        #     total_persent = 0.0
        #     for x in list_of_plan_idss:
        #         for i in x.plan_ids:              
        #             if i.state_plan_ids.id in states:
        #                 total_persent += i.share_from_projects
        #                 budget.append({'state':i.state_plan_ids.name,'percentage':i.share_from_projects})
        #         if len(budget)!=0:
        #             total.append({'total_per':total_persent })
        #             plan_ids.append({'year':datetime.strptime(x.duration_from,"%Y-%m-%d").year,'bud':budget , 'total':total})
        #         budget = []
        #         total_persent = 0
        # elif data['form']['date_to'] and not data['form']['date_from'] and not data['form']['state'] :
        #     year_from = str(datetime.strptime(data['form']['date_to'], '%Y-%m-%d').year)+"-12-31"
        #     list_of_plan_idss = self.env['dzc2.project.planning'].search([('duration_to','<=',year_from)])
        #     if not list_of_plan_idss:
        #         raise UserError(_("Sorry ! There is no data to display."))
        #     plan_ids = []
        #     budget = []
        #     total = []
        #     total_persent = 0.0
        #     for x in list_of_plan_idss:
        #         for i in x.plan_ids:
        #             total_persent += i.share_from_projects
        #             budget.append({'state':i.state_plan_ids.name,'percentage':i.share_from_projects})
        #         if len(budget)!=0:
        #             total.append({'total_per':total_persent }) 
        #             plan_ids.append({'year':datetime.strptime(x.duration_from,"%Y-%m-%d").year,'bud':budget , 'total':total})
        #         budget = []
        #         total_persent = 0
        # elif data['form']['date_from'] and not data['form']['date_to'] and not data['form']['state'] :
        #     year_from = str(datetime.strptime(data['form']['date_from'], '%Y-%m-%d').year)+"-01-01"
        #     list_of_plan_idss = self.env['dzc2.project.planning'].search([('duration_from','>=',year_from)])
        #     if not list_of_plan_idss:
        #         raise UserError(_("Sorry ! There is no data to display."))
        #     plan_ids = []
        #     budget = []
        #     total = []
        #     total_persent = 0.0
        #     for x in list_of_plan_idss:
        #         for i in x.plan_ids:
        #             total_persent += i.share_from_projects
        #             budget.append({'state':i.state_plan_ids.name,'percentage':i.share_from_projects})
        #         if len(budget)!=0:
        #             total.append({'total_per':total_persent })                    
        #             plan_ids.append({'year':datetime.strptime(x.duration_from,"%Y-%m-%d").year,'bud':budget , 'total':total})
        #         budget = []
        #         total_persent = 0
        # elif not data['form']['date_from'] and not data['form']['date_to'] and not data['form']['state'] :
        #     list_of_plan_idss = self.env['dzc2.project.planning'].search([('duration_from','>=',"1000-01-01")])
        #     if not list_of_plan_idss:
        #         raise UserError(_("Sorry ! There is no data to display."))
        #     plan_ids = []
        #     budget = []
        #     total = []
        #     total_persent = 0.0
        #     for x in list_of_plan_idss:
        #         for i in x.plan_ids:
        #             total_persent += i.share_from_projects
        #             budget.append({'state':i.state_plan_ids.name,'percentage':i.share_from_projects})
        #         if len(budget)!=0:
        #             total.append({'total_per':total_persent })
        #             plan_ids.append({'year':datetime.strptime(x.duration_from,"%Y-%m-%d").year,'bud':budget , 'total':total})
        #         budget = []
        #         total_persent = 0
        else:
            raise UserError(_("unknown exception that won\'t happen"))
        docargs = {
            'doc_ids': [],
            'doc_model': 'dzc2.project.budget.planning',
            'docs': plan_ids,
        }
        return docargs


################### State status report ############
class StateStatusReport(models.TransientModel):
    _name = "state.status.wizard"

    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    state = fields.Many2many('zakat.state')

    @api.constrains('date_from', 'date_to')
    def date_validation(self):
        if self.date_from:
            if self.date_to:
                if self.date_from > self.date_to:
                    raise ValidationError(_("Sorry ! End Date Can not be Previous Than Start ."))

    def print_report(self, data):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'dzc2.project.budget.planning',
            'form': data
        }
        return self.env.ref('dzc_2.state_status_report').report_action(self, data=datas)


class StateStatusReport(models.AbstractModel):
    _name = 'report.dzc_2.state_status_rerport'

    @api.model
    def get_report_values(self, docids, data):
        if data['form']['date_from'] and data['form']['date_to'] and data['form']['state']:
            year_from = str(datetime.strptime(data['form']['date_from'], '%Y-%m-%d').year) + "-01-01"
            year_to = str(datetime.strptime(data['form']['date_to'], '%Y-%m-%d').year) + "-12-31"
            st = data['form']['state']
            list_of_plan_idss = self.env['dzc2.project.planning'].search(
                ['&', ('duration_from', '>=', year_from), ('duration_to', '<=', year_to), ('state', '=', 'done')])
            if len(list_of_plan_idss) != 0:
                plan_ids = []
                budget = []
                total = []
                plan_idsned = 0.0
                executed = 0.0
                performance = 0.0
                u = 0
                for x in list_of_plan_idss:
                    budget = []
                    u = 0
                    plan_idsned = 0.0
                    executed = 0.0
                    performance = 0.0
                    total = []
                    for i in x.plan_ids:
                        u += 1
                        if i.state_plan_ids.id in st:
                            plan_idsned += i.share_from_projects
                            executed += i.execute_from_projects
                            performance += i.performance
                            budget.append({'index': u, 'state': i.state_plan_ids.name,
                                           'share_from_projects': i.share_from_projects,
                                           'execute_from_projects': i.execute_from_projects,
                                           'performance': i.performance})
                    total.append({'plan_idsned': plan_idsned, 'executed': executed, 'performance': performance})
                    plan_ids.append(
                        {'year': datetime.strptime(x.duration_from, "%Y-%m-%d").year, 'bud': budget, 'total': total})
            else:
                raise UserError(_("Sorry ! There is no data to display."))
        elif data['form']['date_from'] and data['form']['date_to'] and not data['form']['state']:
            year_from = str(datetime.strptime(data['form']['date_from'], '%Y-%m-%d').year) + "-01-01"
            year_to = str(datetime.strptime(data['form']['date_to'], '%Y-%m-%d').year) + "-12-31"
            list_of_plan_idss = self.env['dzc2.project.planning'].search(
                ['&', ('duration_from', '>=', year_from), ('duration_to', '<=', year_to), ('state', '=', 'done')])
            if len(list_of_plan_idss) != 0:
                plan_ids = []
                budget = []
                total = []
                plan_idsned = 0.0
                executed = 0.0
                performance = 0.0
                u = 0

                for x in list_of_plan_idss:
                    budget = []
                    u = 0
                    plan_idsned = 0.0
                    executed = 0.0
                    performance = 0.0
                    total = []
                    for i in x.plan_ids:
                        u += 1
                        if i.state_plan_ids.id:
                            plan_idsned += i.share_from_projects
                            executed += i.execute_from_projects
                            performance += i.performance
                            budget.append({'index': u, 'state': i.state_plan_ids.name,
                                           'share_from_projects': i.share_from_projects,
                                           'execute_from_projects': i.execute_from_projects,
                                           'performance': i.performance})
                    total.append({'plan_idsned': plan_idsned, 'executed': executed, 'performance': performance})
                    plan_ids.append(
                        {'year': datetime.strptime(x.duration_from, "%Y-%m-%d").year, 'bud': budget, 'total': total})
            else:
                raise UserError(_("Sorry ! There is no data to display."))

        elif data['form']['date_to'] and not data['form']['date_from']:
            raise ValidationError(_("Please Enter From Date."))

        elif data['form']['date_from'] and not data['form']['date_to']:
            raise ValidationError(_("Please Enter To Date."))

        elif not data['form']['date_from'] and not data['form']['date_to'] and data['form']['state']:
            list_of_plan_idss = self.env['dzc2.project.planning'].search([('state', '=', 'done')])
            if len(list_of_plan_idss) != 0:
                st = data['form']['state']
                plan_ids = []
                budget = []
                total = []
                plan_idsned = 0.0
                executed = 0.0
                performance = 0.0
                u = 0
                for x in list_of_plan_idss:
                    budget = []
                    u = 0
                    plan_idsned = 0.0
                    executed = 0.0
                    performance = 0.0
                    total = []
                    for i in x.plan_ids:
                        u += 1
                        if i.state_plan_ids.id in st:
                            plan_idsned += i.share_from_projects
                            executed += i.execute_from_projects
                            performance += i.performance
                            budget.append({'index': u, 'state': i.state_plan_ids.name,
                                           'share_from_projects': i.share_from_projects,
                                           'execute_from_projects': i.execute_from_projects,
                                           'performance': i.performance})
                    total.append({'plan_idsned': plan_idsned, 'executed': executed, 'performance': performance})
                    plan_ids.append(
                        {'year': datetime.strptime(x.duration_from, "%Y-%m-%d").year, 'bud': budget, 'total': total})
            else:
                raise UserError(_("Sorry ! There is no data to display."))

        else:
            list_of_plan_idss = self.env['dzc2.project.planning'].search([('state', '=', 'done')])
            if len(list_of_plan_idss) != 0:
                plan_ids = []
                budget = []
                total = []
                plan_idsned = 0.0
                executed = 0.0
                performance = 0.0
                u = 0
                for x in list_of_plan_idss:
                    budget = []
                    u = 0
                    plan_idsned = 0.0
                    executed = 0.0
                    performance = 0.0
                    total = []

                    for i in x.plan_ids:
                        u += 1
                        if i.state_plan_ids.id:
                            plan_idsned += i.share_from_projects
                            executed += i.execute_from_projects
                            performance += i.performance
                            budget.append({'index': u, 'state': i.state_plan_ids.name,
                                           'share_from_projects': i.share_from_projects,
                                           'execute_from_projects': i.execute_from_projects,
                                           'performance': i.performance})
                    total.append({'plan_idsned': plan_idsned, 'executed': executed, 'performance': performance})
                    plan_ids.append(
                        {'year': datetime.strptime(x.duration_from, "%Y-%m-%d").year, 'bud': budget, 'total': total})
            else:
                raise UserError(_("Sorry ! There is no data to display."))

        # if len(budget)!= 0:
        #     plan_ids.append({'year':datetime.strptime(x.duration_from,"%Y-%m-%d").year,'bud':budget , 'total':total})
        #     budget = []

        # else:
        #     raise ValidationError(_("Sorry ! There is no data to display."))

        docargs = {
            'doc_ids': [],
            'doc_model': 'dzc2.project.budget.planning',
            'docs': plan_ids,
        }
        return docargs


#######################################################
# Executed projects in states
##################################################
class StateExecuteReport(models.TransientModel):
    _name = 'state.executed.projects.wizard'

    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    state = fields.Many2many('zakat.state')
    projects = fields.Many2many('dzc2.project', domain="[('view_type','=','normal')]")

    @api.constrains('date_from', 'date_to')
    def date_validation(self):
        if self.date_from:
            if self.date_to:
                if self.date_from > self.date_to:
                    raise ValidationError(_("Sorry ! End Date Can not be Previous Than Start ."))

    def print_report(self, data):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'dzc2.project',
            'form': data
        }
        return self.env.ref('dzc_2.state_executed_projects_report').report_action(self, data=datas)


class StateExecutedReport(models.AbstractModel):
    _name = 'report.dzc_2.state_executed_projects'

    @api.model
    def get_report_values(self, docids, data):
        plan_ids2 = []

        # if data['form']['date_to'] and not data['form']['date_from']:
        #     raise ValidationError(_("Please Enter (From) Date."))

        # elif data['form']['date_from'] and not data['form']['date_to']:
        #     raise ValidationError(_("Please Enter (To) Date."))

        if data['form']['date_from'] and data['form']['date_to'] and data['form']['state'] and data['form']['projects']:
            year_from = ""
            year_to = ""
            year_from = str(datetime.strptime(data['form']['date_from'], '%Y-%m-%d').year) + "-01-01"
            year_to = str(datetime.strptime(data['form']['date_to'], '%Y-%m-%d').year) + "-12-31"
            st = data['form']['state']
            pro = data['form']['projects']

            list_of_years = self.env['dzc2.project.planning'].search(
                ['&', ('duration_from', '>=', year_from), ('duration_to', '<=', year_to), ('state', '=', 'done'),
                 ('plan_ids.state_plan_ids.id', 'in', st)])
            if len(list_of_years) != 0:
                persents = []
                sums = []
                total = []
                executed = 0.0
                performance = 0.0
                all_plan_idsned = 0.0
                all_pesentages = 0.0

                for l in list_of_years:
                    requests = self.env['dzc2.project.request'].search(
                        ['&', ('date', '>=', l.duration_from), ('date', '<=', l.duration_to), ('state', '=', 'done'),
                         ('project_conf.id', 'in', pro)])
                    for s in st:
                        total = []
                        sums = []
                        u = 0
                        all_plan_idsned = 0.0
                        all_pesentages = 0.0

                        for p in pro:
                            u += 1
                            plan_idsned = 0.0
                            state_persent = 0.0

                            for x in requests:
                                if x.project_state.id == s and x.project_conf.id == p:
                                    plan_idsned += 1
                                    plan_ids = self.env['dzc2.project.budget.planning'].search(
                                        [('state_plan_ids.id', '=', s)])
                                    for pp in plan_ids:
                                        if pp.execute_from_projects > 0.0:
                                            state_persent = plan_idsned / pp.execute_from_projects * 100
                                        else:
                                            continue

                            project = self.env['dzc2.project'].search([('id', '=', p)])

                            total.append({'index': u, 'total_pers': plan_idsned, 'persentage': state_persent,
                                          'project': project.name})

                            all_plan_idsned += plan_idsned
                            all_pesentages += state_persent

                        state = self.env['zakat.state'].search([('id', '=', s)])
                        sums.append({'plan_idsned_sum': all_plan_idsned, 'persent_sum': all_pesentages})
                        plan_ids2.append(
                            {'year': datetime.strptime(l.duration_from, "%Y-%m-%d").year, 'state': state.name,
                             'total': total, 'sumation': sums})

            else:
                raise UserError(_("Sorry ! There is no data to display."))


        ################################################################################
        # Only Date
        ###############################################################################
        elif data['form']['date_from'] and data['form']['date_to'] and not data['form']['state'] and not data['form'][
            'projects']:
            year_from = ""
            year_to = ""
            year_from = str(datetime.strptime(data['form']['date_from'], '%Y-%m-%d').year) + "-01-01"
            year_to = str(datetime.strptime(data['form']['date_to'], '%Y-%m-%d').year) + "-12-31"
            sta = data['form']['company_id']
            st = self.env['zakat.state'].search([('company_id', '=', sta[0])])
            pro = self.env['dzc2.project'].search([('view_type', '=', 'normal')])

            list_of_years = self.env['dzc2.project.planning'].search(
                ['&', ('duration_from', '>=', year_from), ('duration_to', '<=', year_to), ('state', '=', 'done')])
            print("uuuuuuuuuuuuuuuuuuuuuuuuuuuuu", list_of_years)
            if len(list_of_years) != 0:

                persents = []
                sums = []
                total = []
                executed = 0.0
                performance = 0.0
                all_plan_idsned = 0.0
                all_pesentages = 0.0

                for l in list_of_years:
                    requests = self.env['dzc2.project.request'].search(
                        ['&', ('date', '>=', l.duration_from), ('date', '<=', l.duration_to), ('state', '=', 'done')])

                    for s in st:
                        sums = []
                        total = []

                        u = 0
                        all_plan_idsned = 0.0
                        all_pesentages = 0.0

                        for p in pro:
                            u += 1
                            plan_idsned = 0.0
                            state_persent = 0.0
                            for x in requests:
                                if x.project_state.id == s.id and x.project_conf.id == p.id:

                                    plan_idsned += 1
                                    plan_ids = self.env['dzc2.project.budget.planning'].search(
                                        [('state_plan_ids.id', '=', s.id)])
                                    for pp in plan_ids:
                                        if pp.execute_from_projects > 0.0:

                                            state_persent = plan_idsned / pp.execute_from_projects * 100
                                        else:
                                            continue

                            project = self.env['dzc2.project'].search([('id', '=', p.id)])

                            total.append({'index': u, 'total_pers': plan_idsned, 'persentage': state_persent,
                                          'project': project.name})
                            all_plan_idsned += plan_idsned
                            all_pesentages += state_persent
                        state = self.env['zakat.state'].search([('id', '=', s.id)])
                        sums.append({'plan_idsned_sum': all_plan_idsned, 'persent_sum': all_pesentages})
                        plan_ids2.append(
                            {'year': datetime.strptime(l.duration_from, "%Y-%m-%d").year, 'state': state.name,
                             'total': total, 'sumation': sums})

            else:
                raise UserError(_("Sorry ! There is no data to display."))


        ####################################################################################3
        # Dates and states only
        ####################################################################################

        elif data['form']['date_from'] and data['form']['date_to'] and data['form']['state'] and not data['form'][
            'projects']:
            year_from = ""
            year_to = ""
            year_from = str(datetime.strptime(data['form']['date_from'], '%Y-%m-%d').year) + "-01-01"
            year_to = str(datetime.strptime(data['form']['date_to'], '%Y-%m-%d').year) + "-12-31"
            st = data['form']['state']
            pro = self.env['dzc2.project'].search([('view_type', '=', 'normal')])
            list_of_years = self.env['dzc2.project.planning'].search(
                ['&', ('duration_from', '>=', year_from), ('duration_to', '<=', year_to), ('state', '=', 'done'),
                 ('plan_ids.state_plan_ids.id', 'in', st)])
            if len(list_of_years) != 0:
                persents = []
                sums = []
                total = []
                executed = 0.0
                performance = 0.0
                all_plan_idsned = 0.0
                all_pesentages = 0.0

                for l in list_of_years:
                    requests = self.env['dzc2.project.request'].search(
                        ['&', ('date', '>=', l.duration_from), ('date', '<=', l.duration_to), ('state', '=', 'done')])
                    for s in st:
                        total = []
                        sums = []
                        u = 0
                        all_plan_idsned = 0.0
                        all_pesentages = 0.0

                        for p in pro:
                            u += 1
                            plan_idsned = 0.0
                            state_persent = 0.0

                            for x in requests:
                                if x.project_state.id == s and x.project_conf.id == p.id:
                                    plan_idsned += 1
                                    plan_ids = self.env['dzc2.project.budget.planning'].search(
                                        [('state_plan_ids.id', '=', s)])
                                    for pp in plan_ids:
                                        if pp.execute_from_projects > 0.0:
                                            state_persent = plan_idsned / pp.execute_from_projects * 100
                                        else:
                                            continue

                            project = self.env['dzc2.project'].search([('id', '=', p.id)])

                            total.append({'index': u, 'total_pers': plan_idsned, 'persentage': state_persent,
                                          'project': project.name})

                            all_plan_idsned += plan_idsned
                            all_pesentages += state_persent

                        state = self.env['zakat.state'].search([('id', '=', s)])
                        sums.append({'plan_idsned_sum': all_plan_idsned, 'persent_sum': all_pesentages})
                        plan_ids2.append(
                            {'year': datetime.strptime(l.duration_from, "%Y-%m-%d").year, 'state': state.name,
                             'total': total, 'sumation': sums})
            else:
                raise UserError(_("Sorry ! There is no data to display."))

        ####################################################################################3
        # Dates and Projects only
        ####################################################################################

        elif data['form']['date_from'] and data['form']['date_to'] and not data['form']['state'] and data['form'][
            'projects']:
            year_from = ""
            year_to = ""
            year_from = str(datetime.strptime(data['form']['date_from'], '%Y-%m-%d').year) + "-01-01"
            year_to = str(datetime.strptime(data['form']['date_to'], '%Y-%m-%d').year) + "-12-31"
            sta = data['form']['company_id']
            st = self.env['zakat.state'].search([('company_id', '=', sta[0])])
            pro = data['form']['projects']

            list_of_years = self.env['dzc2.project.planning'].search(
                ['&', ('duration_from', '>=', year_from), ('duration_to', '<=', year_to), ('state', '=', 'done')])
            if len(list_of_years) != 0:
                persents = []
                sums = []
                total = []
                executed = 0.0
                performance = 0.0
                all_plan_idsned = 0.0
                all_pesentages = 0.0

                for l in list_of_years:
                    requests = self.env['dzc2.project.request'].search(
                        ['&', ('date', '>=', l.duration_from), ('date', '<=', l.duration_to), ('state', '=', 'done')])
                    for s in st:

                        total = []
                        sums = []
                        u = 0
                        all_plan_idsned = 0.0
                        all_pesentages = 0.0

                        for p in pro:
                            u += 1
                            plan_idsned = 0.0
                            state_persent = 0.0

                            for x in requests:
                                if x.project_state.id == s.id and x.project_conf.id == p:
                                    plan_idsned += 1
                                    plan_ids = self.env['dzc2.project.budget.planning'].search(
                                        [('state_plan_ids.id', '=', s.id)])
                                    for pp in plan_ids:
                                        if pp.execute_from_projects > 0.0:
                                            state_persent = plan_idsned / pp.execute_from_projects * 100
                                        else:
                                            continue

                            project = self.env['dzc2.project'].search([('id', '=', p)])

                            total.append({'index': u, 'total_pers': plan_idsned, 'persentage': state_persent,
                                          'project': project.name})

                            all_plan_idsned += plan_idsned
                            all_pesentages += state_persent

                        state = self.env['zakat.state'].search([('id', '=', s.id)])
                        sums.append({'plan_idsned_sum': all_plan_idsned, 'persent_sum': all_pesentages})
                        plan_ids2.append(
                            {'year': datetime.strptime(l.duration_from, "%Y-%m-%d").year, 'state': state.name,
                             'total': total, 'sumation': sums})
            else:
                raise UserError(_("Sorry ! There is no data to display."))

        ##########################################################################
        # Projects and state only
        ############################################################################

        # elif not data['form']['date_from'] and not data['form']['date_to'] and data['form']['state'] and data['form']['projects']:
        #     year_from = ""
        #     year_to = ""
        #     st = data['form']['state']
        #     pro = data['form']['projects']

        #     list_of_years = self.env['dzc2.project.planning'].search( [('state','=','done') , ('plan_ids.state_plan_ids.id' ,'in' , st)])
        #     if len(list_of_years) != 0:
        #         persents = []
        #         sums = []
        #         total = []
        #         executed = 0.0
        #         performance = 0.0
        #         all_plan_idsned = 0.0
        #         all_pesentages = 0.0

        #         for l in list_of_years:
        #             requests = self.env['dzc2.project.request'].search( ['&',('date','>=',l.duration_from), ('date','<=',l.duration_to),('state' , '=' , 'done'),('project_conf.id' , 'in' , pro)])
        #             for s in st:
        #                 total = []
        #                 sums = []
        #                 u = 0
        #                 all_plan_idsned = 0.0
        #                 all_pesentages = 0.0

        #                 for p in pro:
        #                     u += 1 
        #                     plan_idsned = 0.0
        #                     state_persent = 0.0

        #                     for x in requests:
        #                         if x.project_state.id == s and x.project_conf.id == p:
        #                             plan_idsned += 1
        #                             plan_ids = self.env['dzc2.project.budget.planning'].search([('state_plan_ids.id','=', s)])
        #                             for pp in plan_ids:
        #                                 if pp.execute_from_projects > 0.0 :
        #                                     state_persent = plan_idsned / pp.execute_from_projects  * 100
        #                                 else:
        #                                     continue

        #                     project = self.env['dzc2.project'].search( [('id','=',p)])

        #                     total.append({'index': u ,'total_pers': plan_idsned , 'persentage' : state_persent , 'project' : project.name})

        #                     all_plan_idsned += plan_idsned
        #                     all_pesentages += state_persent

        #                 state = self.env['zakat.state'].search( [('id','=',s)])
        #                 sums.append({'plan_idsned_sum':all_plan_idsned ,'persent_sum':all_pesentages})
        #                 plan_ids2.append({'year':datetime.strptime(l.duration_from,"%Y-%m-%d").year,'state':state.name,'total': total , 'sumation':sums})
        # else:
        #     raise UserError(_("Sorry ! There is no data to display."))

        ################################################################################
        # Nothing inserted
        ####################################################################################

        # elif not data['form']['date_from'] and  not data['form']['date_to'] and not data['form']['state'] and not data['form']['projects']:
        #     year_from = ""
        #     year_to = ""
        #     sta = data['form']['company_id']
        #     st = self.env['zakat.state'].search([('company_id' , '=' , sta[0]) ])
        #     pro = self.env['dzc2.project'].search([('view_type','=','normal')])

        #     list_of_years = self.env['dzc2.project.planning'].search( [('state','=','done') ])
        #     if len(list_of_years) != 0 :
        #         persents = []
        #         sums = []
        #         total = []
        #         executed = 0.0
        #         performance = 0.0
        #         all_plan_idsned = 0.0
        #         all_pesentages = 0.0

        #         for l in list_of_years:
        #             requests = self.env['dzc2.project.request'].search( ['&',('date','>=',l.duration_from), ('date','<=',l.duration_to),('state' , '=' , 'done')])
        #             for s in st:
        #                 total = []
        #                 sums = []
        #                 u = 0
        #                 all_plan_idsned = 0.0
        #                 all_pesentages = 0.0

        #                 for p in pro:
        #                     plan_idsned = 0.0
        #                     state_persent = 0.0
        #                     u += 1 
        #                     for x in requests:
        #                         if x.project_state.id == s.id and x.project_conf.id == p.id:
        #                             plan_idsned += 1
        #                             plan_ids = self.env['dzc2.project.budget.planning'].search([('state_plan_ids.id','=', s.id)])
        #                             for pp in plan_ids:
        #                                 if pp.execute_from_projects > 0.0 :
        #                                     state_persent = plan_idsned / pp.execute_from_projects  * 100  
        #                                 else:
        #                                     continue

        #                     project = self.env['dzc2.project'].search( [('id','=',p.id)])

        #                     total.append({'index': u ,'total_pers': plan_idsned , 'persentage' : state_persent , 'project' : project.name})

        #                     all_plan_idsned += plan_idsned
        #                     all_pesentages += state_persent

        #                 state = self.env['zakat.state'].search( [('id','=',s.id)])
        #                 sums.append({'plan_idsned_sum':all_plan_idsned ,'persent_sum':all_pesentages})
        #                 plan_ids2.append({'year':datetime.strptime(l.duration_from,"%Y-%m-%d").year,'state':state.name,'total': total , 'sumation':sums})
        #     else:
        #         raise UserError(_("Sorry ! There is no data to display."))

        if len(plan_ids2) != 0:
            docargs = {
                'doc_ids': [],
                'doc_model': 'dzc2.project.reqest',
                'docs': plan_ids2,
            }
            return docargs


class localStatesPercantage(models.TransientModel):
    """docstring for localStatesPercantage"""
    _name = 'local.state.percantage.wizard'

    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    local_state = fields.Many2many('zakat.local.state')

    @api.one
    @api.constrains('date_from', 'date_to')
    def validDate(self):
        if self.date_from:
            if self.date_to:
                if self.date_from > self.date_to:
                    raise ValidationError(_("Sorry! Date From Must Be Before Date To"))

    def print_report(self, data):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': ['dzc2.project.request', 'dzc2.project.budget.planning'],
            'form': data
        }
        return self.env.ref('dzc_2.local_state_executed_projects').report_action(self, data=datas)


class localStatesPercantageAbstract(models.AbstractModel):
    """docstring for ClassName"""
    _name = 'report.dzc_2.local_state_per_report'

    @api.model
    def get_report_values(self, docids, data):
        if data['form']['date_from'] and data['form']['date_to'] and data['form']['local_state']:
            year_from = str(datetime.strptime(data['form']['date_from'], '%Y-%m-%d').year) + "-01-01"
            year_to = str(datetime.strptime(data['form']['date_to'], '%Y-%m-%d').year) + "-12-31"
            local_st = data['form']['local_state']
            list_of_plan_idss = self.env['dzc2.project.planning'].search(
                ['&', ('duration_from', '>=', year_from), ('duration_to', '<=', year_to)])
            lstate_num = 0.0
            lstate_per = 0.0
            total_per = 0.0
            total_num = 0
            lstate_requests = []
            rep_data = []
            index = 0
            for p in list_of_plan_idss:
                lstate_requests = []
                for l in local_st:
                    l_state = self.env['zakat.local.state'].search([('id', '=', l)])
                    state = l_state.state_id.id
                    l_name = l_state.local_name
                    list_of_requests = self.env['dzc2.project.request'].search(
                        ['&', ('date', '>=', p.duration_from), ('date', '<=', p.duration_to), '&',
                         ('project_local_state', '=', l), ('state', '=', 'done')])
                    lstate_num = len(list_of_requests)
                    total_num += lstate_num
                    plan_ids = self.env['dzc2.project.budget.planning'].search(
                        ['&', ('project_plan_ids', '=', p.id), ('state_plan_ids', '=', state)])
                    lstate_per = lstate_num / plan_ids.share_from_projects * 100
                    total_per += lstate_per
                    index += 1
                    lstate_requests.append(
                        {'local_state': l_name, 'num_of_projects': lstate_num, 'percantage': lstate_per,
                         'index': index})
                rep_data.append(
                    {'year': datetime.strptime(p.duration_from, "%Y-%m-%d").year, 'lstates': lstate_requests,
                     'total': total_per, 'total_num': total_num})
        elif data['form']['date_from'] and data['form']['date_to'] and not data['form']['local_state']:
            year_from = str(datetime.strptime(data['form']['date_from'], '%Y-%m-%d').year) + "-01-01"
            year_to = str(datetime.strptime(data['form']['date_to'], '%Y-%m-%d').year) + "-12-31"
            local_st = self.env['zakat.local.state'].search([])
            list_of_plan_idss = self.env['dzc2.project.planning'].search(
                ['&', ('duration_from', '>=', year_from), ('duration_to', '<=', year_to)])
            lstate_num = 0.0
            lstate_per = 0.0
            total_per = 0.0
            total_num = 0
            lstate_requests = []
            rep_data = []
            index = 0
            for p in list_of_plan_idss:
                lstate_requests = []
                for l in local_st:
                    l_state = self.env['zakat.local.state'].search([('id', '=', l.id)])
                    state = l_state.state_id.id
                    l_name = l_state.local_name
                    list_of_requests = self.env['dzc2.project.request'].search(
                        ['&', ('date', '>=', p.duration_from), ('date', '<=', p.duration_to), '&',
                         ('project_local_state', '=', l.id), ('state', '=', 'done')])
                    lstate_num = len(list_of_requests)
                    total_num += lstate_num
                    plan_ids = self.env['dzc2.project.budget.planning'].search(
                        ['&', ('project_plan_ids', '=', p.id), ('state_plan_ids', '=', state)])
                    lstate_per = lstate_num / plan_ids.share_from_projects * 100
                    total_per += lstate_per
                    index += 1
                    lstate_requests.append(
                        {'local_state': l_name, 'num_of_projects': lstate_num, 'percantage': lstate_per,
                         'index': index})
                rep_data.append(
                    {'year': datetime.strptime(p.duration_from, "%Y-%m-%d").year, 'lstates': lstate_requests,
                     'total': total_per, 'total_num': total_num})
        elif data['form']['date_to'] and not data['form']['date_from']:
            raise ValidationError(_("Please Enter From Date."))

        elif data['form']['date_from'] and not data['form']['date_to']:
            raise ValidationError(_("Please Enter To Date."))

        elif not data['form']['date_from'] and not data['form']['date_to'] and data['form']['local_state']:
            local_st = data['form']['local_state']
            list_of_plan_idss = self.env['dzc2.project.planning'].search([])
            lstate_num = 0.0
            lstate_per = 0.0
            total_per = 0.0
            total_num = 0
            lstate_requests = []
            rep_data = []
            index = 0
            for p in list_of_plan_idss:
                lstate_requests = []
                for l in local_st:
                    l_state = self.env['zakat.local.state'].search([('id', '=', l)])
                    state = l_state.state_id.id
                    l_name = l_state.local_name
                    list_of_requests = self.env['dzc2.project.request'].search(
                        ['&', ('date', '>=', p.duration_from), ('date', '<=', p.duration_to), '&',
                         ('project_local_state', '=', l), ('state', '=', 'done')])
                    lstate_num = len(list_of_requests)
                    total_num += lstate_num
                    plan_ids = self.env['dzc2.project.budget.planning'].search(
                        ['&', ('project_plan_ids', '=', p.id), ('state_plan_ids', '=', state)])
                    lstate_per = lstate_num / plan_ids.share_from_projects * 100
                    total_per += lstate_per
                    index += 1
                    lstate_requests.append(
                        {'local_state': l_name, 'num_of_projects': lstate_num, 'percantage': lstate_per,
                         'index': index})
                rep_data.append(
                    {'year': datetime.strptime(p.duration_from, "%Y-%m-%d").year, 'lstates': lstate_requests,
                     'total': total_per, 'total_num': total_num})

        else:
            local_st = self.env['zakat.local.state'].search([])
            list_of_plan_idss = self.env['dzc2.project.planning'].search([])
            lstate_num = 0.0
            lstate_per = 0.0
            total_per = 0.0
            total_num = 0
            lstate_requests = []
            rep_data = []
            index = 0
            for p in list_of_plan_idss:
                lstate_requests = []
                for l in local_st:
                    l_state = self.env['zakat.local.state'].search([('id', '=', l.id)])
                    state = l_state.state_id.id
                    l_name = l_state.local_name
                    list_of_requests = self.env['dzc2.project.request'].search(
                        ['&', ('date', '>=', p.duration_from), ('date', '<=', p.duration_to), '&',
                         ('project_local_state', '=', l.id), ('state', '=', 'done')])
                    lstate_num = len(list_of_requests)
                    total_num += lstate_num
                    plan_ids = self.env['dzc2.project.budget.planning'].search(
                        ['&', ('project_plan_ids', '=', p.id), ('state_plan_ids', '=', state)])
                    lstate_per = lstate_num / plan_ids.share_from_projects * 100
                    total_per += lstate_per
                    index += 1
                    lstate_requests.append(
                        {'local_state': l_name, 'num_of_projects': lstate_num, 'percantage': lstate_per,
                         'index': index})
                rep_data.append(
                    {'year': datetime.strptime(p.duration_from, "%Y-%m-%d").year, 'lstates': lstate_requests,
                     'total': total_per, 'total_num': total_num})
        if len(rep_data) != 0:
            docargs = {
                'doc_ids': [],
                'doc_model': ['dzc2.project.request', 'dzc2.project.budget.planning'],
                'docs': rep_data,
            }
            return docargs
        else:
            raise ValidationError(_("Sorry ! There is no data to display."))


class localStatesPercantage(models.TransientModel):
    """docstring for localStatesPercantage"""
    _name = 'local.state.percantage.wizard'

    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    local_state = fields.Many2many('zakat.local.state')

    @api.one
    @api.constrains('date_from', 'date_to')
    def validDate(self):
        if self.date_from:
            if self.date_to:
                if self.date_from > self.date_to:
                    raise ValidationError(_("Sorry! Date From Must Be Before Date To"))

    def print_report(self, data):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': ['dzc2.project.request', 'dzc2.project.budget.planning'],
            'form': data
        }
        return self.env.ref('dzc_2.local_state_executed_projects').report_action(self, data=datas)


class localStatesPercantageAbstract(models.AbstractModel):
    """docstring for ClassName"""
    _name = 'report.dzc_2.local_state_per_report'

    @api.model
    def get_report_values(self, docids, data):
        if data['form']['date_from'] and data['form']['date_to'] and data['form']['local_state']:
            year_from = str(datetime.strptime(data['form']['date_from'], '%Y-%m-%d').year) + "-01-01"
            year_to = str(datetime.strptime(data['form']['date_to'], '%Y-%m-%d').year) + "-12-31"
            local_st = data['form']['local_state']
            list_of_plan_idss = self.env['dzc2.project.planning'].search(
                ['&', ('duration_from', '>=', year_from), ('duration_to', '<=', year_to)])
            lstate_num = 0
            lstate_per = 0
            total_per = 0.0
            total_num = 0
            lstate_requests = []
            rep_data = []
            index = 0
            for p in list_of_plan_idss:
                lstate_requests = []
                total_per = 0.0
                total_num = 0.0

                for l in local_st:
                    l_state = self.env['zakat.local.state'].search([('id', '=', l)])
                    state = l_state.state_id.id
                    l_name = l_state.name
                    list_of_requests = self.env['dzc2.project.request'].search(
                        ['&', ('date', '>=', p.duration_from), ('date', '<=', p.duration_to), '&',
                         ('project_local_state', '=', l), ('state', '=', 'done')])
                    lstate_num = len(list_of_requests)
                    total_num += lstate_num
                    plan_ids = self.env['dzc2.project.budget.planning'].search(
                        ['&', ('project_plan_id', '=', p.id), ('state_plan_ids', '=', state)])
                    if plan_ids.share_from_projects > 0.0:
                        lstate_per = lstate_num / plan_ids.project_plan_id.total_execued_projects * 100
                    else:
                        continue
                    total_per += lstate_per
                    index += 1
                    lstate_requests.append(
                        {'local_state': l_name, 'num_of_projects': lstate_num, 'percantage': lstate_per,
                         'index': index})
                rep_data.append(
                    {'year': datetime.strptime(p.duration_from, "%Y-%m-%d").year, 'lstates': lstate_requests,
                     'total': total_per, 'total_num': total_num})
        elif data['form']['date_from'] and data['form']['date_to'] and not data['form']['local_state']:
            year_from = str(datetime.strptime(data['form']['date_from'], '%Y-%m-%d').year) + "-01-01"
            year_to = str(datetime.strptime(data['form']['date_to'], '%Y-%m-%d').year) + "-12-31"
            local_st = self.env['zakat.local.state'].search([])
            list_of_plan_idss = self.env['dzc2.project.planning'].search(
                ['&', ('duration_from', '>=', year_from), ('duration_to', '<=', year_to)])
            lstate_num = 0
            lstate_per = 0
            total_per = 0.0
            total_num = 0
            lstate_requests = []
            rep_data = []
            index = 0
            for p in list_of_plan_idss:
                lstate_requests = []
                total_per = 0.0
                total_num = 0.0
                for l in local_st:
                    l_state = self.env['zakat.local.state'].search([('id', '=', l.id)])
                    state = l_state.state_id.id
                    l_name = l_state.name
                    list_of_requests = self.env['dzc2.project.request'].search(
                        ['&', ('date', '>=', p.duration_from), ('date', '<=', p.duration_to), '&',
                         ('project_local_state', '=', l.id), ('state', '=', 'done')])
                    lstate_num = len(list_of_requests)
                    total_num += lstate_num
                    plan_ids = self.env['dzc2.project.budget.planning'].search(
                        ['&', ('project_plan_id', '=', p.id), ('state_plan_ids', '=', state)])
                    if plan_ids.share_from_projects > 0.0:
                        lstate_per = lstate_num / plan_ids.project_plan_id.total_execued_projects * 100
                    else:
                        continue
                    total_per += lstate_per
                    index += 1
                    lstate_requests.append(
                        {'local_state': l_name, 'num_of_projects': lstate_num, 'percantage': lstate_per,
                         'index': index})
                rep_data.append(
                    {'year': datetime.strptime(p.duration_from, "%Y-%m-%d").year, 'lstates': lstate_requests,
                     'total': total_per, 'total_num': total_num})
        # elif data['form']['date_to'] and not data['form']['date_from']:
        #     raise ValidationError(_("Please Enter From Date."))

        # elif data['form']['date_from'] and not data['form']['date_to']:
        #     raise ValidationError(_("Please Enter To Date."))

        # elif not data['form']['date_from'] and not data['form']['date_to'] and data['form']['local_state'] :
        #     local_st = data['form']['local_state']
        #     list_of_plan_idss = self.env['dzc2.project.planning'].search( [])
        #     lstate_num = 0
        #     lstate_per = 0
        #     total_per= 0.0
        #     total_num =0
        #     lstate_requests=[]
        #     rep_data = []
        #     index = 0
        #     for p in list_of_plan_idss:
        #         lstate_requests=[]
        #         total_per = 0.0
        #         total_num = 0.0
        #         for l in local_st:
        #             l_state = self.env['zakat.local.state'].search([('id','=',l)])
        #             state =l_state.state_id.id
        #             l_name = l_state.name
        #             list_of_requests = self.env['dzc2.project.request'].search( ['&',('date','>=',p.duration_from), ('date','<=',p.duration_to),'&',('project_local_state','=',l),('state','=','done')])
        #             lstate_num = len(list_of_requests)
        #             total_num+=lstate_num
        #             plan_ids = self.env['dzc2.project.budget.planning'].search(['&',('project_plan_id','=',p.id),('state_plan_ids','=',state)])
        #             if plan_ids.share_from_projects > 0.0:
        #                 lstate_per = lstate_num/plan_ids.share_from_projects*100
        #             else:
        #                 continue                    
        #             total_per += lstate_per
        #             index +=1
        #             lstate_requests.append({'local_state':l_name,'num_of_projects':lstate_num,'percantage':lstate_per,'index':index})
        #         rep_data.append({'year':datetime.strptime(p.duration_from,"%Y-%m-%d").year,'lstates':lstate_requests,'total':total_per,'total_num':total_num})

        # else:
        #     local_st = self.env['zakat.local.state'].search([])
        #     list_of_plan_idss = self.env['dzc2.project.planning'].search( [])
        #     lstate_num = 0
        #     lstate_per = 0
        #     total_per = 0.0
        #     total_num =0
        #     lstate_requests=[]
        #     rep_data =[]
        #     index = 0
        #     for p in list_of_plan_idss:
        #         lstate_requests=[]
        #         total_per = 0.0
        #         total_num = 0.0
        #         for l in local_st:
        #             l_state = self.env['zakat.local.state'].search([('id','=',l.id)])
        #             state =l_state.state_id.id
        #             l_name = l_state.name
        #             list_of_requests = self.env['dzc2.project.request'].search( ['&',('date','>=',p.duration_from), ('date','<=',p.duration_to),'&',('project_local_state','=',l.id),('state','=','done')])
        #             lstate_num = len(list_of_requests)
        #             total_num+=lstate_num
        #             plan_ids = self.env['dzc2.project.budget.planning'].search(['&',('project_plan_id','=',p.id),('state_plan_ids','=',state)])
        #             if plan_ids.share_from_projects > 0.0:
        #                 lstate_per = lstate_num/plan_ids.share_from_projects*100
        #             else:
        #                 continue
        #             total_per += lstate_per
        #             index+=1
        #             lstate_requests.append({'local_state':l_name,'num_of_projects':lstate_num,'percantage':lstate_per,'index':index})
        #         rep_data.append({'year':datetime.strptime(p.duration_from,"%Y-%m-%d").year,'lstates':lstate_requests,'total':total_per,'total_num':total_num})
        if len(rep_data) != 0:
            docargs = {
                'doc_ids': [],
                'doc_model': ['dzc2.project.request', 'dzc2.project.budget.planning'],
                'docs': rep_data,
            }
            return docargs
        else:
            raise ValidationError(_("Sorry ! There is no data to display."))


class DoneProjectDetails(models.TransientModel):
    _name = 'zakat.doneprojectdetail'

    date_from = fields.Date(string="From - To")
    date_to = fields.Date()
    project_ids = fields.Many2many('dzc2.project', string="Project")
    state_ids = fields.Many2many('zakat.state', string="State")

    def done_project_detail(self):
        """
        Call done_project_detail_action to print report
        :return: report
        """
        if self.date_from and self.date_to:
            if self.date_to < self.date_from:
                raise exceptions.ValidationError(_("Date From Must Be Greater Than Date To"))
        states = self.env['zakat.state'].search([])
        projects = self.env['dzc2.project'].search([])
        state_list = []
        project_list = []
        if self.state_ids:
            for state in self.state_ids:
                state_list.append(state.id)
        else:
            for x in states:
                print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^', x)
            for state in states:
                state_list.append(state.id)
        if self.project_ids:
            for project in self.project_ids:
                project_list.append(project.id)
        else:
            for x in projects:
                print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^', x)
            for project in projects:
                project_list.append(project.id)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", state_list)
        print("**********************************", project_list)
        datas = {
            'ids': [],
            'model': 'dzc2.project',
            'date_from': self.date_from,
            'date_to': self.date_to,
            'state': state_list,
            'project': project_list,

        }

        return self.env.ref('dzc_2.done_project_detail_report_action').report_action(self, data=datas)


class DoneProjectReport(models.AbstractModel):
    _name = 'report.dzc_2.done_project_detail_report'

    @api.model
    def get_report_values(self, docids, data):
        start = data['date_from']
        end = data['date_to']
        state_ids = data['state']
        project_ids = data['project']
        docs = self.env['dzc2.project.request'].search([])

        if start and end and state_ids and project_ids:
            docs = self.env['dzc2.project.request'].search(
                ['&', '&', '&', ('date', '>=', start),
                 ('date', '<=', end),
                 ('project_state', 'in', state_ids),
                 ('project_conf', 'in', project_ids)])

        elif start and end and state_ids:
            docs = self.env['dzc2.project.request'].search(
                ['&', '&', ('date', '>=', start),
                 ('date', '<=', end),
                 ('project_state', 'in', state_ids),
                 ])

        elif start and end and project_ids:
            docs = self.env['dzc2.project.request'].search(
                ['&', '&', ('date', '>=', start),
                 ('dtae', '<=', end),
                 ('project_conf', 'in', project_ids)])

        elif start and project_ids:
            docs = self.env['dzc2.project.request'].search(
                [('date', '>=', start),
                 ('project_conf', 'in', project_ids)])
        elif start and state_ids:
            docs = self.env['dzc2.project.request'].search(
                [('date', '>=', start),
                 ('project_state', 'in', state_ids)])
        elif state_ids and end:
            docs = self.env['dzc2.project.request'].search(
                [('project_state', 'in', state_ids),
                 ('date', '<=', end)])
        elif start and end:
            docs = self.env['dzc2.project.request'].search(
                ['&', '&', '&', ('date', '>=', start),
                 ('date', '<=', end)])
        elif project_ids and end:
            docs = self.env['dzc2.project.request'].search(
                [('project_conf', 'in', project_ids),
                 ('date', '<=', end)])

        elif state_ids and project_ids:
            docs = self.env['dzc2.project.request'].search(
                [('project_state', 'in', state_ids),
                 ('project_conf', 'in', project_ids)])

        elif state_ids:
            docs = self.env['dzc2.project.request'].search(
                [('project_state', 'in', state_ids)])
        elif start:
            docs = self.env['dzc2.project.request'].search(
                [('date', '>=', start)])
        elif end:
            docs = self.env['dzc2.project.request'].search(
                [('date', '<=', end)])
        elif project_ids:
            docs = self.env['dzc2.project.request'].search(
                [('project_conf', 'in', project_ids)])

        for x in docs:
            print(
                '================================================================================================================================================',
                x)
        if not docs:
            raise exceptions.ValidationError(_("Sory! There is no data"))
        report_list = []
        whol_total = 0
        report_values = []
        requsts = []
        request_states = []
        states_total = []
        for r in docs:
            if r.project_conf.id not in requsts:
                requsts.append(r.project_conf.id)
            if r.project_state.id not in request_states:
                request_states.append(r.project_state.id)
        index = 0
        for state_id in request_states:
            states_total.append({'state_id': state_id, 'state_total': 0})
        for p in project_ids:
            if p in requsts:
                index += 1
                project_name = ''
                total = 0
                proj_dict = {'project': '', 'states': [], 'total': '0', 'index': index}
                for s in state_ids:
                    if s in request_states:
                        state_name = '                    '
                        proj_num = 0
                        for r in docs:
                            if r.project_state.id == s and r.project_conf.id == p:
                                proj_num += 1
                                state_name = r.project_state.name
                                project_name = r.project_conf.name
                        proj_dict['states'].append({'state_name': state_name, 'proj_num': proj_num})
                        total += proj_num
                        for state in states_total:
                            if state['state_id'] == s:
                                state['state_total'] += proj_num
                                break
                proj_dict['project'] = project_name
                proj_dict['total'] = total
                whol_total += total
                report_values.append(proj_dict)
        report_list.append(report_values)
        report_list.append(states_total)
        report_list.append(whol_total)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'dzc2.project.request',
            'docs': report_list,

        }
        return docargs


# this is the analysis report
class ProjectAnalysis(models.TransientModel):
    _name = "project.analysis"

    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    local_state = fields.Many2many('zakat.local.state')
    project_type = fields.Many2many('dzc2.project')
    sectors = fields.Many2many('zakat.sectors')

    def print_report(self, data):
        self.ensure_one()
        [data] = self.read()
        sector = data['sectors']
        project_type = data['project_type']
        local_state = data['local_state']
        date_from = data['date_from']
        date_to = data['date_to']
        datas = {
            'ids': [],
            'model': ['dzc2.project.request', 'dzc2.project.budget.planning'],
            'form': data
        }
        # sectors
        print("\n\n\n\n\nhere in the print report method\n\n\n\n\n\n") 
        if sector and not project_type and not local_state:
            all_sectors = {}
            sector_list = []
            total_amount = 0
            total_num = 0
            l_s_name = " "
            cost = 0
            for x in sector:
                sect = self.env['dzc2.project.request'].search(
                    [('date', '>=', data['date_from']), ('date', '<=', data['date_to']), ('project_sectors', '=', x)])
                for sector in sect:
                    cost = cost + sector.part_cost
                    sector_name = sector.project_sectors.name
                if len(sect) == 0:
                    sector_name = self.env['zakat.sectors'].search([('id', '=', x)]).name
                sector_list.append({'sector': sector_name, 'cost': cost, 'count': len(sect)})
                total_amount = total_amount + cost
                cost = 0
                total_num = total_num + len(sect)
            all_sectors = {'type': 'القطاع', 'data': sector_list, 'total': total_amount, 'total_num': total_num}
            datas['form'] = all_sectors
            value = self.env.ref('dzc_2.project_analysis_simple_report_action').report_action(self, data=datas)
        # project type
        elif not sector and project_type and not local_state:
            all_states = {}
            state_list = []
            total_amount = 0
            total_num = 0
            l_s_name = " "
            cost = 0
            for x in project_type:
                l_s = self.env['dzc2.project.request'].search(
                    [('date', '>=', data['date_from']), ('date', '<=', data['date_to']),
                     ('project_conf.parent_ids', '=', x)])
                for s in l_s:
                    cost = cost + s.part_cost
                    l_s_name = s.project_conf.parent_ids.name
                if len(l_s) == 0:
                    l_s_name = self.env['dzc2.project'].search([('id', '=', x)]).name
                state_list.append({'sector': l_s_name, 'cost': cost, 'count': len(l_s)})
                total_amount = total_amount + cost
                cost = 0
                total_num = total_num + len(l_s)
            all_states = {'type': 'النوع', 'data': state_list, 'total': total_amount, 'total_num': total_num}
            datas['form'] = all_states
            value = self.env.ref('dzc_2.project_analysis_simple_report_action').report_action(self, data=datas)
        # local state
        elif not sector and not project_type and local_state:
            all_states = {}
            state_list = []
            total_amount = 0
            total_num = 0
            l_s_name = " "
            cost = 0
            for x in local_state:
                l_s = self.env['dzc2.project.request'].search(
                    [('date', '>=', data['date_from']), ('date', '<=', data['date_to']),
                     ('project_local_state', '=', x)])
                for s in l_s:
                    cost = cost + s.part_cost
                    l_s_name = s.project_local_state.name
                if len(l_s) == 0:
                    l_s_name = self.env['zakat.local.state'].search([('id', '=', x)]).name
                state_list.append({'sector': l_s_name, 'cost': cost, 'count': len(l_s)})
                total_amount = total_amount + cost
                cost = 0
                total_num = total_num + len(l_s)
            all_states = {'type': 'المحلية', 'data': state_list, 'total': total_amount, 'total_num': total_num}
            datas['form'] = all_states
            value = self.env.ref('dzc_2.project_analysis_simple_report_action').report_action(self, data=datas)
        # no sectors,just  project types and local states
        elif not sector and project_type and len(local_state)>1:
            data = {}
            all_data = []
            head = []
            sentdata = {}
            part_cost = 0
            total_cost = 0
            amount = 0 
            projects = self.env['dzc2.project.request'].search([('date','>=',date_from),('date','<=',date_to),('project_local_state','in',local_state)])
            print("\n\n\n\n","this is result :",projects,"\n\n\n\n")                        
            self._cr.execute('''
                                SELECT id,name,project_conf,project_local_state,part_cost,total_cost,project_sectors,date
                                FROM dzc2_project_request
                                WHERE project_local_state IN %s
                                AND date >= %s AND date <= %s
                                ''', [tuple(local_state),date_from,date_to])
            result = self._cr.fetchall()
            result.sort()            
            for x in local_state:
                for i in range(len(result)):
                    if self.env['zakat.local.state'].search([('id','=',result[i][3])]).id == x:
                        for t in project_type:
                            if self.env['dzc2.project'].search([('id','=',result[i][2])]).parent_ids.id == t:
                                total_cost = total_cost+result[i][4]
                                local_state_name = self.env['zakat.local.state'].search([('id','=',result[i][3])]).name
                                the_type = self.env['dzc2.project'].search([('id','=',result[i][2])]).parent_ids
                                amount = amount+1
                                sector = self.env['dzc2.project.request'].search([('project_sectors','=',result[i][6])])
                d = {'local_state':local_state_name,
                'project_type':the_type,
                'total_cost':total_cost,
                'amount':amount,
                'sector':sector,
                }
                total_cost = 0
                amount = 0 
                print("\n\n\n\n","this is D :",d,"\n\n\n\n")
                all_data.append(d)
            print("\n\n\n\n","this is all data :",all_data,"\n\n\n\n")
            value = self.env.ref('dzc_2.project_analysis_report_action').report_action(self, data=datas)
        # one local state and more than one project type
        elif not sector and len(project_type) > 1 and len(local_state) == 1:
            all_states = {}
            state_list = []
            total_amount = 0
            total_num = 0
            l_s_name = " "
            cost = 0
            for x in project_type:
                l_s = self.env['dzc2.project.request'].search(
                    [('date', '>=', data['date_from']), ('date', '<=', data['date_to'])
                        , ('project_conf.parent_ids', '=', x), ('project_local_state', '=', local_state[0])])
                for s in l_s:
                    cost = cost + s.part_cost
                    l_s_name = s.project_conf.parent_ids.name
                if len(l_s) == 0:
                    l_s_name = self.env['dzc2.project'].search([('id', '=', x)]).name
                state_list.append({'sector': l_s_name, 'cost': cost, 'count': len(l_s)})
                total_amount = total_amount + cost
                cost = 0
                total_num = total_num + len(l_s)
            all_states = {'type': 'النوع', 'data': state_list, 'total': total_amount, 'total_num': total_num}
            datas['form'] = all_states
            value = self.env.ref('dzc_2.project_analysis_simple_report_action').report_action(self, data=datas)
        # more than one local state and project type
        # elif not sector and project_type and len(local_state)>1:
        #     data = {}
        #     list_data = []
        #     # plans = self.env['dzc2.project.request'].search([('date', '>=', data['date_from']), ('date', '<=', data['date_to'])])
        #     print("\n\n\n\n\n\n\n\n\n\n::this is the project printed::\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        #     # data = {'type':type,'amount':amount,'quantaty':quantaty}
        #     # list_data.append(data)
        #     # datas = {'year':year,'data':list_data}
        #     value = self.env.ref('dzc_2.project_analysis_report_action').report_action(self, data=datas)
        else:
            raise ValidationError(_("enter some data "))
        return value


# this is analysis complicated abstract
class ProjectAnalysisAbstract(models.AbstractModel):
    _name = "report.dzc_2.project_analysis_template"

    @api.model
    def get_report_values(self, docids, data):
        docargs = {
            'doc_ids': [],
            'doc_model': ['dzc2.project.request', 'dzc2.project.budget.planning'],
            'docs': None,
        }
        return docargs


# this is analysis simple abstract
class ProjectAnalysisAbstract(models.AbstractModel):
    _name = "report.dzc_2.project_analysis_simple_template"

    @api.model
    def get_report_values(self, docids, data):
        docargs = {
            'doc_ids': [],
            'doc_model': ['dzc2.project.request', 'dzc2.project.budget.planning'],
            'docs': data['form'],
        }
        return docargs


class ProjectOwnershipReport(models.TransientModel):
    _name = "proj.own.wizard"
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    state = fields.Many2many('zakat.state')
    projects = fields.Many2many('dzc2.project')

    @api.one
    @api.constrains('date_from', 'date_to')
    def validDate(self):
        if self.date_from:
            if self.date_to:
                if self.date_from > self.date_to:
                    raise ValidationError(_("Date is no right"))

    def print_report(self, data):
        self.ensure_one()
        [form_values] = self.read()
        act_data = {
            'ids': [],
            'model': 'dzc2.project.request',
            'form': form_values
        }
        return self.env.ref('dzc_2.proj_pwn').report_action(self, data=act_data)


class ProjectOwnershipReport(models.AbstractModel):
    _name = 'report.dzc_2.proj_own_report'
    year_from = '----'
    year_to = '----'

    @api.model
    def get_report_values(self, docids, data):
        if data['form']['date_to']:
            year_to = datetime.strptime(data['form']['date_to'], '%Y-%m-%d')
        else:
            year_to = '----'
        if data['form']['date_from']:
            year_from = datetime.strptime(data['form']['date_from'], '%Y-%m-%d')
        else:
            year_from = '----'
        proj_filter = data['form']['projects']
        st = data['form']['state']
        if data['form']['date_from']:
            if data['form']['date_to']:
                if data['form']['state']:
                    if data['form']['projects']:
                        envi = ['&', '&', '&', ('state', '=', 'done'), ('project_state', 'in', st),
                                ('project_conf', 'in', proj_filter), '&', ('date', '>=', year_from),
                                ('date', '<=', year_to)]
                    else:
                        envi = ['&', '&', ('state', '=', 'done'), ('project_state', 'in', st), '&',
                                ('date', '>=', year_from), ('date', '<=', year_to)]
                else:
                    envi = ['&', ('state', '=', 'done'), '&', ('date', '>=', year_from), ('date', '<=', year_to)]
            else:
                if data['form']['state']:
                    if data['form']['projects']:
                        envi = ['&', '&', ('state', '=', 'done'), ('project_state', 'in', st), '&',
                                ('project_conf', 'in', proj_filter), ('date', '>=', year_from)]
                    else:
                        envi = ['&', '&', ('state', '=', 'done'), ('project_state', 'in', st),
                                ('date', '>=', year_from)]
                else:
                    if data['form']['projects']:
                        envi = ['&', '&', ('state', '=', 'done'), ('project_conf', 'in', proj_filter),
                                ('date', '>=', year_from)]
                    else:
                        envi = ['&', ('state', '=', 'done'), ('date', '>=', year_from)]
        else:
            if data['form']['date_to']:
                if data['form']['state']:
                    if data['form']['projects']:
                        envi = ['&', '&', ('state', '=', 'done'), ('project_state', 'in', st), '&',
                                ('project_conf', 'in', proj_filter), ('date', '<=', year_to)]
                    else:
                        envi = ['&', '&', ('state', '=', 'done'), ('project_state', 'in', st), ('date', '<=', year_to)]
                else:
                    envi = ['&', '&', ('state', '=', 'done'), ('project_conf', 'in', proj_filter),
                            ('date', '<=', year_to)]

            else:
                if data['form']['state']:
                    if data['form']['projects']:
                        envi = ['&', '&', ('state', '=', 'done'), ('project_state', 'in', st),
                                ('project_conf', 'in', proj_filter)]
                    else:
                        envi = ['&', ('state', '=', 'done'), ('project_state', 'in', st)]
                else:
                    if data['form']['projects']:
                        envi = ['&', ('state', '=', 'done'), ('project_conf', 'in', proj_filter)]
                    else:
                        envi = [('state', '=', 'done')]
        projects = self.env['dzc2.project.request'].search(envi)
        # if not projects:
        # raise ValidationError(_("Sorry ! There is no data to display."))
        report_records = []
        whole_report_records = []
        index = 0
        total = 0
        for x in projects:
            index += 1
            total += x.total_cost
            project = x.project_conf.name
            amount = x.total_cost
            state = x.project_local_state.name
            if x.type_of_project == 'service':
                if x.service_partner:
                    name = x.service_partner.faqeer_id.name
                    phone = x.service_partner.faqeer_id.phone
                    address = x.service_partner.state_id.name + '/' + x.service_partner.local_state_id.name + '/' + x.service_partner.village

            else:
                if x.type_of_project == 'individual_production':
                    name = x.individual_partner.faqeer_id.name
                    phone = x.individual_partner.faqeer_id.phone
                    address = x.individual_partner.state_id.name + '/' + x.individual_partner.local_state_id.name + '/' + x.individual_partner.village

                else:
                    if x.collective_partner:
                        name = x.collective_partner.faqeer_id.name
                        phone = x.collective_partner.faqeer_id.phone
                        address = x.collective_partner.state_id.name + '/' + x.collective_partner.local_state_id.name + '/' + x.collective_partner.village

            report_records.append(
                {'index': index, 'name': name, 'state': state, 'project': project, 'phone': phone, 'amount': amount,
                 'address': address})
        whole_report_records.append(report_records)
        if data['form']['date_from'] and data['form']['date_to']:
            whole_report_records.append(
                {'total': total, 'from': year_from.strftime('%Y-%m-%d'), 'to': year_to.strftime('%Y-%m-%d')})
        else:
            if data['form']['date_from']:
                whole_report_records.append({'total': total, 'from': year_from.strftime('%Y-%m-%d'), 'to': year_to})
            else:
                if data['form']['date_to']:
                    whole_report_records.append({'total': total, 'from': year_from, 'to': year_to.strftime('%Y-%m-%d')})
                else:
                    whole_report_records.append({'total': total, 'from': year_from, 'to': year_to})

        docargs = {
            'doc_ids': [],
            'doc_model': 'dzc2.project.request',
            'docs': whole_report_records
        }
        return docargs


class ProjectOwnershipReport(models.AbstractModel):
    _name = 'report.dzc_2.plan_datails'
    @api.model
    def get_report_values(self, docids, data):
        plan = self.env['dzc2.project.planning'].search([('id', 'in', docids)])  
        table = []
        for line in plan.plan_ids:
            table.append(
                {
                    'state':line.state_plan_ids.name,
                    'per':line.percentage,
                    'share_budget':line.share_from_budget,
                    'share_proj':line.share_from_projects,
                    'exc_proj':line.execute_from_projects,
                    'exc_budget':line.execute_from_budget,
                    'perf':round(line.performance,3)
                })
        report_values = {
            'name':plan.name,
            'from':plan.duration_from , 
            'to':plan.duration_to , 
            'budget':plan.total_budget ,
            'proj_num':plan.total_execued_projects,
            'fam_num':plan.total_project_target,
            'budget_excuted':plan.total_executed_budget,
            'states':table
        }
        docargs = {
            'doc_ids': [],
            'doc_model': 'dzc2.project.request',
            'docs': report_values
        }
        return docargs