# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from datetime import date, datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
from committe.models import committe_model
import time


class commites_wizard(osv.osv_memory):
    """ To manage the creation of commites wizards """
    _name = "commites_wizard"

    _description = "commites wizard"

    _columns = {
        'details_type': fields.selection(committe_model.hr_commite.types_list, 'Type', track_visibility="always"),
        'company_id': fields.many2one('res.company', string='Company', required=True),
        'process_type': fields.selection([('promotion', 'Promotion'), ('isolate', 'Isolataion')], 'Category'),
        'date_from': fields.date('Date Form'),
        'date_to': fields.date('Date To'),
    }

    def _check_date(self, cr, uid, ids, context=None):
        """
        Check the value of date_from if greater than date_to or not.

        @return: Boolean of True or False
        """
        for act in self.browse(cr, uid, ids, context):
            if act.date_from > act.date_to:
                raise osv.except_osv(_(''), _("Start Date Must Be Less Than End Date!"))
        return True

    _constraints=[(_check_date, _(''), []),]

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'commites_wizard', context=c),
        'date_from': time.strftime('%Y-%m-%d'),
        'date_to': time.strftime('%Y-%m-%d'),
    }

    def create_type(self, cr, uid, ids, context=None):
        committe_obj = self.pool.get('hr.committe')
        committe_details_obj = self.pool.get('hr.committe.details')
        new_id = 0
        for rec in self.browse(cr, uid, ids, context=context):
            type_obj = self.pool.get(rec.details_type)
            domain = [('is_committe', '=', True), (
                'state', '=', 'draft'), ('committe_id', '=', False), ('committe_details_id', '=', False),
                ('company_id', '=', rec.company_id.id),
                ('date', '>=', rec.date_from), ('date', '<=', rec.date_to), ]
            if rec.details_type == 'hr.movements.degree':
                domain+= [('process_type','=',rec.process_type)]
            type_ids = type_obj.search(cr, uid, domain)
            if type_ids:
                new_id = committe_obj.create(
                    cr, uid, {'details_type': rec.details_type, 'company_id': rec.company_id.id,
                              })

                for x in type_obj.browse(cr, uid, type_ids):
                    line = {'employee_id': x.employee_id.id,
                            'reference_object': rec.details_type + ',' + str(x.id),
                            'parent': new_id}
                    line_id = committe_details_obj.create(cr, uid, line)
                    committe_obj.write(
                        cr, uid, [new_id], {'committe_details_ids_manageral': [(4, line_id)]})
                    x.write({'committe_id': new_id,
                             'committe_details_id': line_id})
            if not type_ids:
                raise orm.except_orm(_('Warning'), _("No Record to create")) 
            

        if new_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'hr.committe',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': new_id,
                #'view_id': form_view_id,
                'target': 'current',
            }

        return {}
