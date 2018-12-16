# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from datetime import datetime

class open_extension_period_wizard(osv.osv_memory):
    """
    Model to create new special period as supplementary period
    """
    _name = "open.extension.period.wizard"

    _description = 'Open Extension Period'

    _columns = {
        'date_start': fields.date('Start of Period', required=True),
        'date_stop': fields.date('End of Period', required=True),
    }

    def action_open_extension_period(self, cr, uid, ids, context=None):
        """
        Workflow function change record state to 'open_ext_period'.
        
        @return: boolean True
        """
        if context is None: context = {}
        period_obj = self.pool.get('account.period')
        fy_pool = self.pool.get('account.fiscalyear')
        form = self.read(cr, uid, ids, context=context)[0]
        fy_pool.write(cr, uid, context['active_ids'] , {'state':'open_ext_period'}, context=context)
        for fy in fy_pool.browse(cr, uid, context['active_ids'], context=context):
            if  form['date_start'] <= fy.date_stop:
                raise orm.except_orm(_('UserError'), _('Supplementary period shouldn\'t be within or before the fiscal year you want to close!'))
            ds = datetime.strptime(form['date_start'], '%Y-%m-%d')
            vals = {
                'name': "%s %s/%s" % (ds.strftime('%m/%Y'),_('Ex'), fy.name),
                'code': "%s %s/%s" % (ds.strftime('%Y'),_('Ex'), fy.name),
                'date_start': form['date_start'],
                'date_stop': form['date_stop'],
                'fiscalyear_id': fy.id,
                'special' : True,
            }
            period_obj.create(cr, uid, vals, context=context)
            return {'type':'ir.actions.act_window_close'}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
