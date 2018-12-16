# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from mx import DateTime
import time
from datetime import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import netsvc
import openerp.addons.decimal_precision as dp
class maintenance_departments(osv.Model):
    _name = "maintenance.department"
    _columns = {
        'name': fields.char('Name'),
        'department_id': fields.many2one('hr.department','Department'),
        'stock_location_id': fields.many2one('stock.location', 'Location'),
        'location_dest_id': fields.many2one('stock.location', 'Customer Location'),
        'company_id': fields.many2one('res.company', string='Company', required=True),
        'damage_lines_ids': fields.one2many('maintenance.damage.line', 'department_id', 'Damage Lines'),
    }
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'maintenance.department', context=c),
    }

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ','')) <= 0):
                raise osv.except_osv(_('ValidateError'), _("name must not be spaces"))
        return True
    _constraints = [
        (_check_spaces, '', ['name'])
    ]

    _sql_constraints = [
        ('maintenance_departments_name_uniqe', 'unique(name)', 'you can not create same name !'),
        ('maintenance_department_uniq', 'unique (name,stock_location_id,company_id)', 'The name and Location must be unique per company !')
    ]

    def name_get(self, cr, uid, ids, context=None):
        return ids and [(item.id, "%s-%s" % (item.name, item.stock_location_id.name)) for item in self.browse(cr, uid, ids, context=context)] or []

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            if rec.damage_lines_ids:
                raise osv.except_osv(
                    _(''), _("can not delete record linked with other record"))
        return super(maintenance_departments, self).unlink(cr, uid, ids, context=context)