# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

{
    "name": "Voucher - Human Resources",
    "version": "0.1",
    "author": "NCTR",
    "website": "http://www.nctr.sd",
    "category": "Human Resources",
    "description": "Human Resources management for voucher",
    "depends": [
        'account_financial_ratification','hr_payroll_custom','hr_custom'
    ],
    "data" : [
	'hr_voucher_view.xml'
    ],
    'test': [],
}
