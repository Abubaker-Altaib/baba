# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api, fields, models, _
from odoo.osv import expression
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.config import config
import operator
from dateutil.relativedelta import relativedelta
from odoo.addons.hijri_datepicker.models import date_log


class AccountFiscalyear(models.Model):
    _inherit = "account.fiscalyear"

   
    calender_type = fields.Selection([('hijri', 'Hijri'), ('gregorian', 'Gregorian')],
                                     'Calender Type', track_visibility='onchange', default='hijri')

    # _sql_constraints = [('fiscal_name_uniq', 'unique(name,company_id,state)', _(
    #     'The Fiscal Year name must be unique per company and state!')), ]

   

    def no_monthes(self, start_date, end_date, calender_type='gregorian'):
        if calender_type == 'gregorian':
            count = 0
            while start_date < end_date:
                count += 1
                start_date = start_date + relativedelta(months=1)
            return count
        else:
            count = 0
            hjry_start_date = date_log.gregorian_to_hijri(self, start_date)
            hjry_end_date = date_log.gregorian_to_hijri(self, end_date)
            while date_log.hijri_to_gregorian(self, hjry_start_date) < date_log.hijri_to_gregorian(self, hjry_end_date):
                count += 1
                hjry_start_date = date_log.hijri_next_month(self, hjry_start_date)

    @api.multi
    def create_period(self, interval=1):
        period_obj = self.env['account.period']
        for fy in self:
            fy.period_ids.unlink()
            ds = datetime.strptime(fy.date_start, '%Y-%m-%d').date()
            date_stop = datetime.strptime(fy.date_stop, '%Y-%m-%d').date()
            # stop creating the opening period
            # current_year= "%s %s" % (_('Opening Period'), ds.strftime('%Y'))
            # check_period_name=period_obj.search([('name', 'like',current_year)])
            # if(check_period_name):
            #     current_year= "%s %s" % (_('Opening Period 2'), ds.strftime('%Y'))
            # period_obj.create({
            #         'name': current_year,
            #         'code': ds.strftime('00/%Y'),
            #         'date_start': ds,
            #         'date_stop': ds,
            #         'special': True,
            #         'fiscalyear_id': fy.id,
            #     })

            #no_monthes = self.no_monthes(ds, date_stop, fy.calender_type)

            #interval_length = no_monthes / interval
            # for period in self.get_periods(ds, date_stop, fy.calender_type)
            index = 1
            if fy.calender_type == 'gregorian':
                while ds < date_stop:
                    de = ds + date_log.relativedelta(months=interval, days=-1)

                    if de > date_stop:
                        de = date_stop

                    period_obj.create({
                        'name': '%02d/' % int(index) + ds.strftime('%Y'),
                        'code': '%02d/' % int(index) + ds.strftime('%Y'),
                        'date_start': ds.strftime('%Y-%m-%d'),
                        'date_stop': de.strftime('%Y-%m-%d'),
                        'fiscalyear_id': fy.id,
                    })
                    ds = ds + relativedelta(months=interval)
                    index += 1
            else:
                while ds < date_stop:
                    ds = date_log.gregorian_to_hijri(self, ds)
                    hjry_end_date = date_log.hijri_next_month(self, ds, 1, interval)

                    de = date_log.hijri_to_gregorian(self, hjry_end_date)

                    if de > date_stop:
                        de = date_stop

                    de = date_log.gregorian_to_hijri(self, de)

                    period_obj.create({
                        'name': '%02d/' % int(index) + ds['year'],
                        'code': '%02d/' % int(index) + ds['year'],
                        'date_start': date_log.hijri_to_gregorian(self, ds),
                        'date_stop': date_log.hijri_to_gregorian(self, de),
                        'fiscalyear_id': fy.id,
                    })
                    ds = date_log.hijri_next_month(self, ds, 0, interval)
                    ds = date_log.hijri_to_gregorian(self, ds)
                    index += 1
        return True

class AccountPeriod(models.Model):
    _inherit = "account.period"
    
    calender_type = fields.Selection([('hijri', 'Hijri'),
                                      ('meladi', 'Meladi')],
                                     'Calender Type', related='fiscalyear_id.calender_type', store=True,
                                     track_visibility='onchange')