# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class hr_config_settings(osv.osv_memory):

    _inherit = 'hr.config.settings'

    _columns = {
              'age_pension' :fields.integer("Age Pension", required= True),
    }

    def get_default_age_pension(self, cr, uid, fields, context=None):
        return {'age_pension': 65}

    def set_default_age_pension(self, cr, uid, ids, context=None):
        company_obj= self.pool.get('res.company')
        config = self.browse(cr, uid, ids[0], context)
        age_pension= config and config.age_pension
        company_ids = company_obj.search(cr,uid,[])
        company_obj.write(cr, uid, company_ids, {'age_pension': age_pension})
        return True
