# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from report import report_sxw
import calendar
import datetime
import pooler
import math
import xlwt

from openerp.osv import fields,orm,osv
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.tools.translate import _
from . payroll_report_bank import  payroll_report_bank

from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render


_column_sizes = [
    ('total', 30),
    ('employee_code', 30),
    ('employee_name', 30),
    ('no', 8),
]

class hr_payroll_main_archive(orm.Model):
    _inherit = 'hr.payroll.main.archive'

    def _report_xls_fields(self, cr, uid, context=None):
        res = [
            'total',
            'employee_code',
            'employee_name', 
            'no',
           
        ]

        return res

    def _report_xls_template(self, cr, uid, context=None):
        """
        Template updates, e.g.

        my_change = {
            'move_name':{
                'header': [1, 20, 'text', _render("_('My Move Title')")],
                'lines': [1, 0, 'text', _render("l['move_name'] != '/' and l['move_name'] or ('*'+str(l['move_id']))")],
                'totals': [1, 0, 'text', None]},
        }
        return my_change
        """
        return {}



class payroll_report_bank_xls_parser(payroll_report_bank):


    def __init__(self, cr, uid, name, context):
        super(payroll_report_bank_xls_parser, self).__init__(cr, uid, name, context=context)
        archive_obj = self.pool.get('hr.payroll.main.archive')
        self.context = context
        wanted_list = archive_obj._report_xls_fields(cr, uid, context)
        template_changes = archive_obj._report_xls_template(cr, uid, context)
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list': wanted_list,
            'template_changes': template_changes,
        })


class payroll_report_bank_xls(report_xls):
    column_sizes = [x[1] for x in _column_sizes]

    def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
        super(payroll_report_bank_xls, self).__init__(name, table, rml, parser, header, store)
        # XLS Template Holidays Items
        self.col_specs_lines_template = {
        
        'total': {
                'lines': [1, 0, 'number', _render("l['total']")],
                'totals': [1, 0, 'number', None]},
        
        'employee_code': {
                'lines': [1, 0, 'number', _render("l['employee_code']")],
                'totals': [1, 0, 'number', None]},

        'employee_name': {
                'lines': [1, 0, 'text', _render("l['employee_name']")],
                'totals': [1, 0, 'text', None]},

        'bank_name': {
                'lines': [1, 0, 'text', _render("l['bank_name']")],
                'totals': [1, 0, 'text', None]},
        'name': {
                'lines': [1, 0, 'text', _render("l['name']")],
                'totals': [1, 0, 'text', None]},
        'no': {
                'lines': [1, 0, 'number', _render("l['no']")],
                'totals': [1, 0, 'number', None]},
            
            }


    def _data_lines(self,data,bank_id, ws, _p, row_pos, xlwt, _xs):

        wanted_list = self.wanted_list
        print "------------------wanted_list", wanted_list
        col_specs_lines_template = self.col_specs_lines_template

        # Column Header Row
        cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        c_hdr_cell_style = xlwt.easyxf(cell_format)
        c_hdr_cell_style_right = xlwt.easyxf(cell_format + _xs['right'])
        c_hdr_cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        c_hdr_cell_style_decimal = xlwt.easyxf(cell_format + _xs['right'], num_format_str = report_xls.decimal_format)

        c_specs = [
        ('total', 1, 0, 'text', (u'الاجمالي'), None, c_hdr_cell_style),
        ('employee_code', 1, 0, 'text', (u'رقم الحساب'), None, c_hdr_cell_style),
        ('employee_name', 1, 0, 'text', (u'الموظف'), None, c_hdr_cell_style),
        ('no', 1, 0, 'text', _('#'), None, c_hdr_cell_style_right),                  
        ]  

        c_hdr_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, c_hdr_data)

        data_list = {}
        data_list['form'] = data
        bank_data = _p.line(data_list,bank_id)

        for l in bank_data:

            c_specs = map(lambda x: self.render(x, self.col_specs_lines_template, 'lines'), wanted_list)
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)
            row_pos + 1

        total = _p.line1(data_list,bank_id)
       
        c_specs = [
            ('total', 1, 0, 'number', (total), None, c_hdr_cell_style),
            ('name', 3, 0, 'text', (u'الاجمالي'), None, c_hdr_cell_style),                  
        ]  
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)
        row_pos + 1




        return row_pos + 1



    def generate_xls_report(self, _p, _xs, data, objects, wb):
        self.col_specs_lines_template.update(_p.template_changes)
        wanted_list = _p.wanted_list
        self.wanted_list = wanted_list
        bank_dict = _p.line9(data)
        for bank in bank_dict:
            sheet_name = _(bank['bank_name'])
            sheet_name = sheet_name[:31].replace('/', '-')
            ws = wb.add_sheet(sheet_name.encode('utf-8'))
            ws.panes_frozen = True
            ws.remove_splits = True
            ws.portrait = 0 # Landscape
            ws.fit_width_to_pages = 1
            row_pos = 0
            
            # set print header/footer
            ws.header_str = self.xls_headers['standard']
            ws.footer_str = self.xls_footers['standard']

            # Title
            if data['type'] == '1': 
                report_name="كشف البنك للمرتبات"
            else:
                report_name="كشف البنك للحوافز"
            cell_style = xlwt.easyxf(_xs['xls_title']+ _xs['center'])
            title =  ' - '.join([report_name,str(data['month'])])
            title =  ' - '.join([title,str(data['year'])])
            c_specs = [
                ('title', 7, 2, 'text', title),
            ]       
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)

            # write empty row to define column sizes
            c_sizes = self.column_sizes
            c_specs = [('empty%s'%i, 1, c_sizes[i], 'text', None) for i in range(0,len(c_sizes))]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, set_column_size=True) 

            # Data
            row_pos = self._data_lines(data,bank['bank_id'], ws, _p, row_pos, xlwt, _xs)

            row_pos += 1


payroll_report_bank_xls('report.payroll.report.bank.xls', 'hr.payroll.main.archive',
    parser=payroll_report_bank_xls_parser)


