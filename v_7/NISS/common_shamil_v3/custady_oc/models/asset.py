# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv,fields
from openerp.tools.translate import _

#----------------------------------------------------------
# Asset_Asset (Inherit)
#----------------------------------------------------------
class account_asset_asset(osv.Model):
    
    STATE_SELECTION = [
		('draft', 'New'),
		('released', 'Released'),
		('assigned', 'Assigned'),
        ('damage', 'Damage'),
	   ]	

    _inherit = "account.asset.asset"

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
    ]

    _columns = {
        'executing_agency': fields.selection(USERS_SELECTION, 'Executing Agency', select=True, help='Department Which this request will executed it'),
    }

    _defaults = {

        'executing_agency': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to,

    }


#----------------------------------------------------------
# asset_custody (Inherit)
#----------------------------------------------------------
class asset_custody(osv.osv):

    _inherit = "asset.custody"


    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
                     ]
    _columns = {
        'executing_agency': fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),
    }

    _defaults = {
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,    
    }


#----------------------------------------------------------
# Custody Return Type inherit
#----------------------------------------------------------
class custody_return_type(osv.osv):
    _inherit = "custody.return.type"

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
    ]
    
    _columns = {
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', required=True, select=True,help='Department Which this request will executed it'),
    }

    _defaults = {
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,    
    }


#----------------------------------------------------------
# Custody Configuration(Office & Types & Models)
#----------------------------------------------------------
class custody_configuration(osv.osv):
    _inherit = "custody.configuration"
    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
    ]
    _columns = {
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', select=True,help='Department Which this request will executed it'),
    
    }

    _defaults = {
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,    
    }
     

#----------------------------------------------------------
# Office_Office inherit
#----------------------------------------------------------
class office_office(osv.osv):
    _inherit = "office.office"
    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
    ]
    _columns = {
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', select=True,help='Department Which this request will executed it'),
     
    }

    _defaults = {
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,    
    }


#----------------------------------------------------------
# asset_custody_line inherit
#----------------------------------------------------------
class asset_custody_line(osv.osv):
    _inherit = "asset.custody.line"
    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
    ]
    _columns = {
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', select=True,help='Department Which this request will executed it'),
     
    }

    _defaults = {
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,    
    }


#----------------------------------------------------------
# history_custody_line inherit
#----------------------------------------------------------
class history_custody_line(osv.osv):
    _inherit = "history.custody.line"
    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
    ]
    _columns = {
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', select=True,help='Department Which this request will executed it'),
     
    }

    _defaults = {
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,    
    }


#----------------------------------------------------------
# asset_custody_detail inherit
#----------------------------------------------------------
class asset_custody_detail(osv.osv_memory):
    _inherit = "asset.custody.detail"
    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
    ]
    _columns = {
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', select=True,help='Department Which this request will executed it'),
     
    }


#----------------------------------------------------------
# asset_custody_management inherit
#----------------------------------------------------------
class asset_custody_management(osv.osv_memory):
    _inherit = "asset.custody.management"
    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
    ]
    _columns = {
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', select=True,help='Department Which this request will executed it'),
     
    }


#----------------------------------------------------------
# asset_custody_personal inherit
#----------------------------------------------------------
class asset_custody_personal(osv.osv_memory):
    _inherit = "asset.custody.personal"
    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
    ]
    _columns = {
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', select=True,help='Department Which this request will executed it'),
     
    }


#----------------------------------------------------------
# asset_custody_sum inherit
#----------------------------------------------------------
class asset_custody_sum(osv.osv_memory):
    _inherit = "asset.custody.sum"
    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
    ]
    _columns = {
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', select=True,help='Department Which this request will executed it'),
     
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
