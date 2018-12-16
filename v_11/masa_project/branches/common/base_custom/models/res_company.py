# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import models, fields, api , exceptions


class ResCompany(models.Model):
    _inherit = 'res.company'

    report_style_id =  fields.Many2one('report.style', string='Report Style')

 
class ReportStyle(models.Model):
    """
    This class for reports style attributes .
    """
    _name = 'report.style'
    _description = 'Report Style'
    
    name =  fields.Char(string='Name',)
    header_color = fields.Char(string='Headder Color', default="white")
    odd_row_color = fields.Char(string='Odd Row Color', default="white")
    even_row_color = fields.Char(string='Even Row Color', default="white")
    border_color =  fields.Char(string='Table Border Color', default="black")

    page_fount = fields.Selection([
        ('Amiri', 'Amiri'),
        ('Droid Arabic Kufi', 'Droid Arabic Kufi'),
        ],string="Page Font",default="Amiri"
        )
    table_fount = fields.Selection([
        ('Amiri', 'Amiri'),
        ('Droid Arabic Kufi', 'Droid Arabic Kufi'),
        ],string="Table Font",default="Amiri"
        )
    header_fount = fields.Selection([
        ('Amiri', 'Amiri'),
        ('Droid Arabic Kufi', 'Droid Arabic Kufi'),
        ],string="Hedar  Font",default="Amiri"
        )
