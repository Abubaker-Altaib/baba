# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from odoo import models, fields, api , _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError


####################################### Budget Custom Reports ##################################################################


class BudgetReportMain(models.TransientModel):
    _inherit = 'budget.custom.report.main'
    #Used in wizard to choose date type in reports
    date_option = fields.Selection([
        ('greg', 'Gregorian'),
        ('isl', 'Islamic'),
        ('both', 'Both'),],string='Date Option',default='greg',required=True,)

    def print_report(self):
        """
        :param date: string off gregorian date
        :return: string off hijry date
        :rtype: string
        """
        data = {}
        data.update({'date_option': self.date_option})
        return super(BudgetReportMain,self).print_report(data)

