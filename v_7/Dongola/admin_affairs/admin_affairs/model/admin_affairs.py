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

class admin_affairs_account(osv.osv):
    """To manage admin affairs account """
    _name = "admin_affairs.account"

    _description = 'Admin Affairs Account'

    _rec_name = "model_id"


    def _model_ids(self,cr,uid,context=None):
        List = []
        model_obj = self.pool.get("ir.model")
        search_ids = model_obj.search(cr,uid,[],context=context)
        for mo in model_obj.browse(cr,uid,search_ids,context=context):
            modules = mo.modules.split(',')
            flag = 'service' in modules or 'fleet' in modules
            flag = flag or 'admin_affairs' in modules or 'fuel_management' in modules 
            if flag:
                List.append( str(mo.id))
        return List


    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """ Returns views and fields for current model.
        @param cr: A database cursor
        @param user: ID of the user currently logged in
        @param view_id: list of fields, which required to read signatures
        @param view_type: defines a view type. it can be one of (form, tree, graph, calender, gantt, search, mdx)
        @param context: context arguments, like lang, time zone
        @param toolbar: contains a list of reports, wizards, and links related to current model

        @return: Returns a dictionary that contains definition for fields, views, and toolbars
        """
        if not context:
            context = {}
        res = super(admin_affairs_account, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)

        for field in res['fields']:
            if field == 'model_id':
                res['fields'][field]['domain'] = [('id','in',
                    self._model_ids(cr,uid,context=context)),('osv_memory','=',False)]
        return res

    _columns = {
        'model_id': fields.many2one('ir.model','Model',required=True),
        'journal_id': fields.property('account.journal', required=True,type='many2one', relation='account.journal',
                                      string='Journal', method=True, view_load=True),                        
        'account_id': fields.property('account.account',type='many2one', relation='account.account', 
                                      string='Account', method=True, view_load=True,required=True),
        'analytic_id': fields.property('account.analytic.account', type='many2one', relation='account.analytic.account',
                                       string='Analytic Account', method=True, view_load=True),
        'notes': fields.text('Notes', size=256 ), 

    }

    _sql_constraints = [
        ('model_uniq', 'unique(model_id)', _('The Model Must Be Unique For Each Service!')),
    ]
class  vehicle_category(osv.osv):
    """ To manage vehicle categories """
    _name = "vehicle.category"
    _columns = {
        'name': fields.char(string="Name" ,required=True),
        'license_cost': fields.float(string="License Cost"),
    }
    def _check_negative(self, cr, uid, ids, context=None):
        """ 
        Check the value of license cost,
        if greater than zero or not.

        @return: Boolean of True or False
        """
        count = 0
        for act in self.browse(cr, uid, ids, context):
            message = _("The Value Of ")
            if (act.license_cost < 0):
                message = message + _("License Cost") 
                count = count + 1
            message = message + _(" Must Be Positive Value!")
        if count > 0 :
            raise osv.except_osv(_('ValidateError'), _(message)) 
        return True
    _constraints = [
        (_check_negative, _(''), ['license_cost'])
    ]

