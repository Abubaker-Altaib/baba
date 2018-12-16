# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##########################################################################

from openerp.osv import fields,osv
import time
import netsvc
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class product_product(osv.osv):
    "Inherits product.product to add spare type filed"
    _inherit = "product.product"   
    _columns = {
        'spare_type': fields.selection([('regular','Regular'),('emergency','Emergency')],'Spare type') ,
	}

#----------------------------------------
# Class maintenance category
#----------------------------------------
class maintenance_category(osv.Model):

    _name = "maintenance.category"
    _description = "Maintenance Category"

    _columns = {
    'name': fields.char('Name', size=64, required=True),
    'account_id': fields.many2one('account.account', 'Account',),
    'pro_journal_id': fields.property('account.journal', 
            type='many2one', 
            relation='account.journal',
            string='Project Journal', 
            method=True, 
            view_load=True), 
                       
    'pro_account_id': fields.property('account.account',
            type='many2one', 
            relation='account.account',
            string='Project Account', 
            method=True, 
            view_load=True),           
    'analytic_id':  fields.many2one('account.analytic.account' , "Analytic Account"),
          }

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'maintenance category must be unique !'),
        ]
