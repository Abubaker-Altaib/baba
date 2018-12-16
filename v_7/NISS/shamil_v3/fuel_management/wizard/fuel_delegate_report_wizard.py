# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv, fields
from openerp.tools.translate import _
from lxml import etree
from openerp.osv.orm import setup_modifiers
import openerp.addons.decimal_precision as dp
import time
import datetime

#-----------------------------------------
#   Fuel Delegate report wizard
#-----------------------------------------

class fuel_delegate_report_wizard(osv.osv_memory):
    _name = "fuel.delegate.report.wizard"

    _columns = {
        'type': fields.selection([('delegate', 'Fuel Delegate'), ('location', 'Location'), ('fuel_type', 'Fuel Type')], 'type'),
        'delegate_ids': fields.many2many('fuel.delegate', 'fuel_delegate_report_rel', 'delegate_id', 'report_id', 'Fuel Delegates'),
		'location_ids': fields.many2many('stock.location', 'fuel_delegate_location_report_rel', 'location_id', 'report_id', 'locations'),
		'fuel_type_ids': fields.many2many('product.product', 'fuel_delegate_product_report_rel', 'product_id', 'report_id', 'Fuels'),
    	'fuel_type': fields.selection([('gasoline','Gasoline'),('diesel', 'Diesel'),('electric', 'Electric'), ('hybrid', 'Hybrid')],'Fuel type') ,
    }

    def print_report(self, cr, uid, ids, context={}):

        data = {'form': self.read(cr, uid, ids, [])[0]}
        
        return {'type': 'ir.actions.report.xml', 'report_name': 'fuel_delegate_reports', 'datas': data}
