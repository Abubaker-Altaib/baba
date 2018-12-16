#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from odoo.report.report_sxw import report_sxw
from odoo import api, models, fields, _
from odoo.api import Environment
from cStringIO import StringIO
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    report_type = fields.Selection(selection_add=[("xlsx", "xlsx")])


class ReportXlsx(report_sxw):

    def create(self, cr, uid, ids, data, context=None):
        self.env = Environment(cr, uid, context)
        report_obj = self.env['ir.actions.report.xml']
        report = report_obj.search([('report_name', '=', self.name[7:])])
        if report.ids:
            self.title = report.name
            if report.report_type == 'xlsx':
                return self.create_xlsx_report(ids, data, report)
        return super(ReportXlsx, self).create(cr, uid, ids, data, context)

    def create_xlsx_report(self, ids, data, report):
        self.parser_instance = self.parser(
            self.env.cr, self.env.uid, self.name2, self.env.context)
        objs = self.getObjects(
            self.env.cr, self.env.uid, ids, self.env.context)
        self.parser_instance.set_context(objs, data, ids, 'xlsx')
        file_data = StringIO()
        workbook = xlsxwriter.Workbook(file_data)
        self.generate_xlsx_report(workbook, data, objs)
        workbook.close()
        file_data.seek(0)
        return (file_data.read(), 'xlsx')

    def generate_xlsx_report(self, workbook, data, objs):
        raise NotImplementedError()


class arab_fund_wiz_report(models.TransientModel):
    _name = 'wiz.arab.fund.report'

    date_from = fields.Date(sting="From Date", required=True)
    date_to = fields.Date(string="To Date", required=True)
    portfolio_id = fields.Many2one('finance.portfolio', string="Portfolio")

    @api.multi
    def print_report(self):
        datas = {
            'ids': '',
            'model': '',
            'context': {
                'start_date': self.date_from,
                'end_date': self.date_to,
                'portfolio': self.portfolio_id.id, },
        }

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'microfinance.arab_fund_report.xlsx',
            'datas': datas,
        }

    class ArabFundXlsxReport(ReportXlsx):
        _name = 'report.microfinance.arab_fund_report.xlsx'

        def generate_xlsx_report(self, workbook, data, objs):
            """
            Create xlsx file and get report information
            :return:
            """

            row = 11
            col = 1
            row1 = 11
            col1 = 1
            type = []
            serial = 1
            print ">>>>>>>>>>>>>>>>>>>>>>>>", data
            # Here to create the page
            worksheeta =  workbook.add_worksheet('تعريفات'.decode('utf-8','ignore'))
            worksheet = workbook.add_worksheet('طلبات التمويل'.decode('utf-8','ignore'))
            worksheet1 = workbook.add_worksheet('الدفعة الأولى'.decode('utf-8', 'ignore'))
            # To change the dircation of the page
            worksheeta.right_to_left()
            worksheet.right_to_left()
            worksheet1.right_to_left()
            # Format for The Worksheet Date
            date_time = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm AM/PM'})
            date_and_time = datetime.datetime.now()

            header_format = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '000080',
                'font_name': 'Arabic transparent',
                'font_size': 18,
                'font_color': 'white', })
            title_format = workbook.add_format(
                {
                    'bold': 1,
                    'align': 'right',
                    'fg_color': '94c3be',
                    'font_name': 'Arabic transparent',
                    'align': 'center',
                    'valign': 'vcenter',
                    'font_color': 'white',
                    'num_format': 'dd/mm/yyyy',

                })

            title_format2 = workbook.add_format(
                {
                    'bold': 1,
                    'align': 'left',
                    'fg_color': '94c3be',
                    'font_name': 'Arabic transparent',
                    'align': 'center',
                    'valign': 'vcenter',
                    'font_color': 'white',

                })
            font_style = workbook.add_format(
                {
                    'align': 'center',
                    'font_name': 'Arabic transparent',
                    'valign': 'vcenter',
                    'font_size': 14,
                })

            font_style_title = workbook.add_format(
                {
                    'align': 'right',
                    'font_name': 'Arabic transparent',
                    'valign': 'vcenter',
                    'font_size': 14,
                })
            title_def = workbook.add_format({
                'bold': True,
                'font_color': '000080',
                'underline':True,
                'fg_color': 'fefefe',
                'font_name': 'Arabic transparent',
                'font_size': 14,
                 })
            def_word = workbook.add_format({

                'fg_color': 'fefefe',
                'font_name': 'Arabic transparent',
                'font_size': 14,
                'valign': 'vcenter',
                'text_wrap': True,

            })

            font_style_title1 = workbook.add_format(
                {
                    'align': 'center',
                    'bold': 1,
                    'border': 1,
                    'fg_color': '94c3be',
                    'font_name': 'Arabic transparent',
                    'valign': 'vcenter',
                    'font_size': 14,
                    'font_color': 'white',
                    'text_wrap': True,
                })
            worksheet.set_row(0, 30)
            worksheet.set_row(0, 30)
            worksheet.set_row(9, 35)
            worksheet.set_row(10, 35)
            worksheet.set_column('B:B', 20.60)
            worksheet.set_column('C:C', 10.10)
            worksheet.set_column('D:D', 10.20)
            worksheet.set_column('E:E', 20.11)
            worksheet.set_column('F:F', 30.35)
            worksheet.set_column('G:G', 20.0)
            worksheet.set_column('P:P', 10.99)
            worksheet.set_column('A:A', 20.35)
            worksheet1.set_row(0, 30)
            worksheet1.set_row(0, 30)
            worksheet1.set_row(9, 35)
            worksheet1.set_row(10, 35)
            worksheet1.set_column('B:B', 10.10)
            worksheet1.set_column('C:C', 10.10)
            worksheet1.set_column('D:D', 20.60)
            worksheet1.set_column('E:E', 20.11)
            worksheet1.set_column('F:F', 10.26)
            worksheet1.set_column('G:G', 20.0)
            worksheet1.set_column('P:P', 10.99)
            worksheet1.set_column('A:A', 20.35)
            worksheet1.set_column('H:H', 30.55)
            worksheet1.set_column('I:I', 10.17)
            worksheeta.set_row(1, 30)
            worksheeta.set_row(3, 30)
            worksheeta.set_row(5, 30)
            worksheeta.set_row(7, 30)


            worksheeta.merge_range('A1:M1', 'طلبات التمويل'.decode('utf-8','ignore'), title_def)
            worksheeta.merge_range('A2:M2',
                                   'هي المشاريع / الطلبات المقدمة من المسثمرين و التي يسعى المقترض(إسم المقترض) إلى تمويلهامن قرض االحساب الخاص أو أي حساب أخر'.decode('utf-8','ignore'),def_word)
            worksheeta.merge_range('A3:M3', 'الجهات الوسيطة'.decode('utf-8','ignore'),title_def)
            worksheeta.merge_range('A4:M4','هي مؤسسات التمويل (بنوك, مؤسسات التمويل الأصغر , صناديق تمويليه, مؤسسات ضمان التمويل, أو أي مؤسسسه تمويليه أخرى)و التي تقترض من الحساب الخاص بغرض تمويل المشروعات الصغيرة و المتوسطة'.decode('utf-8','ignore'),def_word)
            worksheeta.merge_range('A5:M5', 'التكلفة الكلية للمشروع'.decode('utf-8','ignore'),title_def)
            worksheeta.merge_range('A6:M6', 'إجمالي قيمة الأصول (الموجودات) الثابتة و المتداولة'.decode('utf-8', 'ignore'),def_word)
            worksheeta.merge_range('A8:M8', 'هو القطاع الأقرب لي طبيعة المشروع و يشمل'.decode('utf-8', 'ignore'),def_word)
            worksheeta.merge_range('A7:M7', 'قطاع المشروع'.decode('utf-8', 'ignore'),title_def)
            worksheeta.write('B9', 'صناعي'.decode('utf-8', 'ignore'),def_word)
            worksheeta.write('A9','1',def_word)
            worksheeta.write('B10', 'خدمات'.decode('utf-8', 'ignore'),def_word)
            worksheeta.write('A10', '2',def_word)
            worksheeta.write('B11', 'حرفي'.decode('utf-8', 'ignore'),def_word)
            worksheeta.write('A11', '3',def_word)
            worksheeta.write('B12', 'تجاري'.decode('utf-8', 'ignore'),def_word)
            worksheeta.write('A12', '4',def_word)
            worksheeta.write('B13', 'تعدين'.decode('utf-8', 'ignore'),def_word)
            worksheeta.write('A13', '5',def_word)
            worksheeta.write('B14', 'بنية تحتية'.decode('utf-8', 'ignore'),def_word)
            worksheeta.write('A14', '6',def_word)
            worksheeta.merge_range('B15:D15', 'خدمات مالية'.decode('utf-8', 'ignore'),def_word)
            worksheeta.write('A15', '7',def_word)
            worksheeta.merge_range('B16:D16', 'زراعي / حيواني'.decode('utf-8', 'ignore'),def_word)
            worksheeta.write('A16', '8',def_word)
            worksheeta.merge_range('B17:D17', 'تكنولوجيا المعلومات'.decode('utf-8', 'ignore'),def_word)
            worksheeta.write('A17', '9',def_word)
            worksheeta.write('B18', 'أخرى'.decode('utf-8', 'ignore'),def_word)
            worksheeta.write('A18', '10',def_word)

            ################################## Geting Report Information ##########################33
            orders = []
            order_ids = self.env['finance.order'].search([
                ('date', '>=', data['context']['start_date']),
                ('date', '<=', data['context']['end_date'])])
            if not order_ids:
                raise UserError(_("There Is No data !!!"))
            for order_id in order_ids:
                orders.append(order_id.id)
            # Getting data from orders     
            individual_orders = self.env['finance.individual.order'].search([('order_id', 'in', orders)])
            group_orders = self.env['finance.group.order'].search([('order_id', 'in', orders)])

           
            for group_ids in group_orders:
                for names in group_ids.group_id.member_ids:
                    worksheet.write(row, col, names.name, font_style_title)
                    if names.gender == 'male':
                        worksheet.write(row, col + 8, '1', font_style)
                        worksheet.write(row, col + 9, '0', font_style)
                    elif names.gender == 'female':
                        worksheet.write(row, col + 9, '1', font_style)
                        worksheet.write(row, col + 8, '0', font_style)
                    worksheet.write(row, col + 1, group_ids.order_id.sector_id.name, font_style)
                    worksheet.write(row, col + 2, group_ids.order_id.project_status, font_style)
                    project_name = []
                    if not group_ids.order_id.visit_id.product_id.project_ids:
                        worksheet.write(row, col + 3, ' ')
                    elif group_ids.order_id.visit_id.approve_ids:
                        for pro in group_ids.order_id.visit_id.approve_ids:
                            project_name.append(pro.project_id.name)
                        text = u", ".join(project_name)
                        worksheet.write(row, col + 3, text,
                                        font_style)

                    worksheet.write(row, col + 4,
                                    group_ids.order_id.company_id.name + ' - ' + group_ids.state_id.name,
                                    font_style)
                    worksheet.write(row, col + 5, group_ids.order_id.type, font_style)
                    donw_payment = 0
                    approve_amount = 0
                    if not group_ids.order_id.visit_id.approve_ids:
                        for downpayments in group_ids.order_id.visit_id.approve_ids:
                            donw_payment += downpayments.downpayment
                            approve_amount += downpayments.approve_amount
                        worksheet.write(row, col + 12, '0', font_style)
                        worksheet.write(row, col + 14, '0', font_style)
                        worksheet.write(row, col + 14, approve_amount, font_style)
                    else:
                        for downpayments in group_ids.order_id.visit_id.approve_ids:
                            donw_payment += downpayments.downpayment
                            approve_amount += downpayments.approve_amount
                        worksheet.write(row, col + 12, donw_payment,
                                        font_style)
                        worksheet.write(row, col + 10,
                                        approve_amount + donw_payment,
                                        font_style)
                        worksheet.write(row, col + 14, approve_amount,
                                        font_style)

                    row += 1

            for ind_id in individual_orders:
                worksheet.write(row, col, ind_id.order_id.partner_id.name, font_style)
                worksheet.write(row, col + 1, ind_id.order_id.sector_id.name, font_style)
                worksheet.write(row, col + 2, ind_id.order_id.project_status, font_style)
                project_name = []
                if not ind_id.order_id.visit_id.product_id.project_ids:
                    worksheet.write(row, col + 3, ' ')
                elif ind_id.order_id.visit_id.approve_ids:
                    for pro in ind_id.order_id.visit_id.approve_ids:
                        project_name.append(pro.project_id.name)
                    text = u", ".join(project_name)
                    worksheet.write(row, col + 3, text, font_style)
                worksheet.write(row, col + 4,
                                ind_id.order_id.company_id.name + ' - ' + ind_id.order_id.state_id.name, font_style)
                worksheet.write(row, col + 5, ind_id.order_id.partner_id.gender, font_style)
                if ind_id.order_id.partner_id.gender == 'male':
                    worksheet.write(row, col + 8, '1', font_style)
                    worksheet.write(row, col + 9, '0', font_style)
                elif ind_id.order_id.partner_id.gender == 'female':
                    worksheet.write(row, col + 9, '1', font_style)
                    worksheet.write(row, col + 8, '0', font_style)
                donw_payment = 0
                approve_amount = 0
                if not ind_id.order_id.visit_id.approve_ids:
                    for downpayments in ind_id.order_id.visit_id.approve_ids:
                        donw_payment += downpayments.downpayment
                        approve_amount += downpayments.approve_amount
                    worksheet.write(row, col + 12, '0', font_style)
                    worksheet.write(row, col + 14, '0', font_style)
                else:
                    for downpayments in ind_id.order_id.visit_id.approve_ids:
                        donw_payment += downpayments.downpayment
                        approve_amount += downpayments.approve_amount
                    worksheet.write(row, col + 12, donw_payment, font_style)
                    worksheet.write(row, col + 10, donw_payment +approve_amount,font_style)
                    worksheet.write(row, col + 14, approve_amount, font_style)

                row += 1

            ################################################## Sheet 2 First payment Report ################

            #based on portfolio and approved state from individual order
            for individual in individual_orders.search([('portfolio_id', '=', data['context']['portfolio']),
                                              ('state', '=', 'approved')]):
                worksheet1.write(row1, col1, serial, font_style)
                worksheet1.write(row1, col1 + 1, individual.name, font_style)
                worksheet1.write(row1, col1 + 2, individual.order_id.partner_id.name, font_style)
                worksheet1.write(row1, col1 + 3, individual.order_id.sector_id.name, font_style)
                worksheet1.write(row1, col1 + 4, individual.order_id.project_status, font_style)
                project_name = []
                if not individual.order_id.visit_id.product_id.project_ids:
                    worksheet1.write(row1, col1 + 5, ' ')
                elif individual.order_id.visit_id.approve_ids:
                    for pro in individual.order_id.visit_id.approve_ids:
                        project_name.append(pro.project_id.name)
                    text = u", ".join(project_name)
                    worksheet1.write(row1, col1 + 5, text, font_style)
                worksheet1.write(row1, col1 + 6,individual.order_id.company_id.name + ' - ' + individual.order_id.state_id.name, font_style)
                worksheet1.write(row1, col1 + 7, individual.order_id.partner_id.gender, font_style)
                if individual.order_id.partner_id.gender == 'male':
                    worksheet1.write(row1, col1 + 10, '1', font_style)
                    worksheet1.write(row1, col1 + 11, '0', font_style)
                elif individual.order_id.partner_id.gender == 'female':
                    worksheet1.write(row1, col1 + 11, '1', font_style)
                    worksheet1.write(row1, col1 + 10, '0', font_style)
                donw_payment = 0
                approve_amount = 0
                if not individual.order_id.visit_id.approve_ids:
                    for downpayments in individual.order_id.visit_id.approve_ids:
                        donw_payment += downpayments.downpayment
                        approve_amount += downpayments.approve_amount
                    worksheet1.write(row1, col1 + 14, '0', font_style)
                    worksheet1.write(row1, col1 + 16, '0', font_style)
                    worksheet1.write(row1, col1 + 18, '0', font_style)
                else:
                    for downpayments in individual.order_id.visit_id.approve_ids:
                        donw_payment += downpayments.downpayment
                        approve_amount += downpayments.approve_amount
                    worksheet1.write(row1, col1 + 14, donw_payment, font_style)
                    worksheet1.write(row1, col1 + 12,
                                     approve_amount + donw_payment ,
                                     font_style)
                    worksheet1.write(row1, col1 + 16, approve_amount, font_style)
                    worksheet1.write(row1, col1 + 18,
                                     approve_amount,
                                     font_style)

                row1 += 1
                serial += 1
            # based on portfolio and approved state from group order
            for group in group_orders.search([('order_id', 'in', orders),('portfolio_id', '=',data['context']['portfolio']),('state', '=', 'approved')]):
                for allname in group.group_id.member_ids:
                    worksheet1.write(row1, col1, serial, font_style)
                    worksheet1.write(row1, col1 + 1, group.name, font_style)
                    worksheet1.write(row1, col1 + 2, allname.name, font_style)
                    if allname.gender == 'male':
                        worksheet1.write(row1, col1 + 10, '1', font_style)
                        worksheet1.write(row1, col1 + 11, '0', font_style)
                    elif allname.gender == 'female':
                        worksheet1.write(row1, col1 + 11, '1', font_style)
                        worksheet1.write(row1, col1 + 10, '0', font_style)
                    worksheet1.write(row1, col1 + 3, group.order_id.sector_id.name, font_style)
                    worksheet1.write(row1, col1 + 4, group.order_id.project_status, font_style)
                    project_name = []
                    if not group.order_id.visit_id.product_id.project_ids:
                        worksheet1.write(row1, col1 + 5, ' ')
                    elif group.order_id.visit_id.approve_ids:
                        for pro in group.order_id.visit_id.approve_ids:
                            project_name.append(pro.project_id.name)
                        text = u", ".join(project_name)
                        worksheet1.write(row1, col1 + 5, text,
                                         font_style)

                    worksheet1.write(row1, col1 + 6,
                                     group.order_id.company_id.name + ' - ' + group.state_id.name,
                                     font_style)
                    worksheet1.write(row1, col1 + 7, group.order_id.type, font_style)
                    donw_payment = 0
                    approve_amount = 0
                    if not group.order_id.visit_id.approve_ids:
                        for downpayments in group.order_id.visit_id.approve_ids:
                            donw_payment += downpayments.downpayment
                            approve_amount += downpayments.approve_amount
                        worksheet1.write(row1, col1 + 12, '0', font_style)
                        worksheet1.write(row1, col1 + 14, '0',
                                         font_style)
                    else:
                        for downpayments in group.order_id.visit_id.approve_ids:
                            donw_payment += downpayments.downpayment
                            approve_amount += downpayments.approve_amount
                        worksheet1.write(row1, col1 + 14,donw_payment,
                                         font_style)
                        worksheet1.write(row1, col1 + 12,
                                         approve_amount + donw_payment,
                                         font_style)
                        worksheet1.write(row1, col1 + 16, approve_amount , font_style)
                        worksheet1.write(row1, col1 + 18, approve_amount,
                                         font_style)
                    row1 += 1
                    serial += 1
            ####################################################################################
            worksheet.merge_range('A1:S1', 'الصندوق العربي للإنماء الأقتصادي و الإجتماعي'.decode('utf-8', 'ignore'), header_format)
            worksheet.write('E2', 'طلبات التمويل من'.decode('utf-8', 'ignore'), title_format2)
            worksheet.write('F2', data['context']['start_date'], title_format)
            worksheet.write('G2', 'إلى'.decode('utf-8', 'ignore'), title_format2)
            worksheet.merge_range('H2:I2', data['context']['end_date'], title_format)
            worksheet.write('A3', 'التاريخ'.decode('utf-8', 'ignore'),font_style)
            worksheet.merge_range('B3:D3', date_and_time, date_time)
            worksheet.write('A4', 'إتفاقية قرض رقم'.decode('utf-8', 'ignore'), font_style)
            worksheet.write('A5', 'إسم الجهه المقترضه'.decode('utf-8', 'ignore'), font_style)
            worksheet.merge_range('B5:D5', self.env.user.company_id.name, font_style)
            worksheet.write('A6', 'إسم الجهه الوسيطه'.decode('utf-8', 'ignore'),font_style)
            worksheet.write('A7', 'رقم طلب السحب'.decode('utf-8', 'ignore'), font_style)
            worksheet.write('B10', 'إسم المقترض'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.write('C10', 'قطاع المشروع'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.write('D10', 'مشروع جديد / قائم'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.write('E10', 'نشاط المشروع المنتج / الخدمه'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.write('F10', 'موقع المشروع المحافظه / الولاية'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.write('G10', 'نوع مالك المشروع'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.merge_range('B11:G11', ' ', font_style_title1)
            worksheet.write('R11', ' ', font_style_title1)
            worksheet.merge_range('H10:I10', 'عدد العماله القائمة'.decode('utf-8', 'ignore'),font_style_title1)
            worksheet.write('H11', 'رجل'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.write('I11', 'إمرأة'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.merge_range('J10:K10', 'عدد العماله الجديدة'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.write('J11', 'رجل'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.write('K11', 'إمرأة'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.merge_range('L10:M10', 'التكلفه الكليه للمشروع'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.write('L11', 'عملة محلية'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.write('M11', 'دولار'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.merge_range('N10:O10', 'مساهمة المستثمر'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.write('N11', 'عملة محلية'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.write('O11', 'دولار'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.merge_range('P10:Q10', 'قيمة التمويل من قرض الحساب الخاص'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.write('P11', 'عملة محلية'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.write('Q11', 'دولار'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet.write('R10', 'الملاحظات'.decode('utf-8', 'ignore'), font_style_title1)

            ################################################ First Payment Sheet ####################################
            worksheet1.merge_range('A1:S1', 'الصندوق العربي للإنماء الأقتصادي و الإجتماعي'.decode('utf-8', 'ignore'),
                                  header_format)
            worksheet1.write('E2', 'الدفعة الأولى'.decode('utf-8', 'ignore'), title_format2)
            worksheet1.write('F2', data['context']['start_date'], title_format)
            worksheet1.write('G2', 'إلى'.decode('utf-8', 'ignore'), title_format2)
            worksheet1.merge_range('H2:I2', data['context']['end_date'], title_format)
            worksheet1.write('A3', 'التاريخ'.decode('utf-8', 'ignore'), font_style)
            worksheet1.merge_range('B3:D3', date_and_time, date_time)
            worksheet1.write('A4', 'إتفاقية قرض رقم'.decode('utf-8', 'ignore'), font_style)
            worksheet1.write('A5', 'إسم الجهه المقترضه'.decode('utf-8', 'ignore'), font_style)
            worksheet1.merge_range('B5:D5', self.env.user.company_id.name, font_style)
            worksheet1.write('A6', 'إسم الجهه الوسيطه'.decode('utf-8', 'ignore'), font_style)
            worksheet1.write('A7', 'رقم طلب السحب'.decode('utf-8', 'ignore'), font_style)
            worksheet1.write('B10', 'تسلسل'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('C10','مرحع القرض'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('D10', 'إسم المقترض'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('E10', 'قطاع المشروع'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('F10', 'مشروع جديد / قائم'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('G10', 'نشاط المشروع المنتج / الخدمه'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('H10', 'موقع المشروع المحافظه / الولاية'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('I10', 'نوع مالك المشروع'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.merge_range('B11:I11', ' ', font_style_title1)
            worksheet1.merge_range('J10:K10', 'عدد العماله القائمة'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('J11', 'رجل'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('K11', 'إمرأة'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.merge_range('L10:M10', 'عدد العماله الجديدة'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('L11', 'رجل'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('M11', 'إمرأة'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.merge_range('N10:O10', 'التكلفه الكليه للمشروع'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('N11', 'عملة محلية'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('O11', 'دولار'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.merge_range('P10:Q10', 'مساهمة المستثمر'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('P11', 'عملة محلية'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('Q11', 'دولار'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.merge_range('R10:S10', 'قيمة التمويل من قرض الحساب الخاص'.decode('utf-8', 'ignore'),
                                  font_style_title1)
            worksheet1.write('R11', 'عملة محلية'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('S11', 'دولار'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.merge_range('T10:U10', 'المصروف من الدفعة الأولى'.decode('utf-8', 'ignore'),
                                   font_style_title1)
            worksheet1.write('T11', 'عملة محلية'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('U11', 'دولار'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('V10', 'الملاحظات'.decode('utf-8', 'ignore'), font_style_title1)
            worksheet1.write('V11', ' ', font_style_title1)
            workbook.close()
    ArabFundXlsxReport('report.microfinance.arab_fund_report.xlsx',
                       'finance.order')
