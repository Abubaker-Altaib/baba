# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , models,_
from odoo.exceptions import ValidationError

class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"


    # @api.multi
    # @api.depends('rate_ids.rate')
    # def _compute_current_rate(self):
    #     super(Currency, self)._compute_current_rate()
    #     print("--------------------------===========================================================================-")
    #     for currency in self:
    #         company=self.env.user.company_id
    #         if company.currency_id == currency:
    #             if currency.rate > 1:
    #                 raise ValidationError(_("Main company Currency rate must be 1."))
    #             if len(currency.rate_ids) > 1:
    #                 raise ValidationError(_("Main company Currency must have one rate."))


    @api.multi
    @api.constrains('currency_id','rate')
    def validate_rate(self):
        print("--------------------------===========================================================================-")
        for rate in self:
            company=rate.company_id
            if company.currency_id == rate.currency_id:
                if rate.currency_id.rate > 1:
                    raise ValidationError(_("Main company Currency rate must be 1."))
                if len(rate.currency_id.rate_ids) > 1:
                    raise ValidationError(_("Main company Currency must have one rate."))
