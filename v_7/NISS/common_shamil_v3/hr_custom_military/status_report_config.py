# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from datetime import datetime
import time
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class status_report_line(osv.Model):
    _name = "status_report_line"
    _columns = {
        'name' : fields.char('Name'),
        'model_id' : fields.many2one('ir.model',string='Model'),
        'state' : fields.char('Done State'),
        'tabel' : fields.char('Tabel Name')
    }

class status_report(osv.Model):
    _name = "status_report"

    _columns = {
        'start_date': fields.datetime('Start Date'),
        'end_date': fields.datetime('End Date'),
        
        'name' : fields.char('Name'),
        
        'lines_ids': fields.many2many('status_report_line', string="Lines"),
    }
    
    def print_report(self, cr, uid, ids, context={}):
        data = {'form': self.read(cr, uid, ids, [])[0]}
        return {'type': 'ir.actions.report.xml', 'report_name': 'sys_status.report', 'datas': data}
            
