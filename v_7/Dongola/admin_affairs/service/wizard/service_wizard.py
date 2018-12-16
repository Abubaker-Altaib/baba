# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from openerp.osv import osv, fields
import time
from datetime import datetime
# Service Report Class

class service_wiz(osv.osv_memory):
    """ To manage services reports """
    _name = "service.wiz"

    _description = "Service Report"

    _columns = {
        'company_id':fields.many2one('res.company','Company',required=True), 
        'date_from':fields.date('Date From', required=True,), 
        'date_to':fields.date('  Date To', required=True),
        'category':fields.selection([('contract', 'Contract'),('env_safety', 'Environment & Safety'),('hospitality','Hospitality'),('occasion','Occasion'),('hall','Hall'),('building','Building'),('media','Media'),('public_relation','Public Relation'),('general','General')], 'Category'),
        'service_type':fields.many2one('fleet.service.type','Service Type'),
        'department':fields.many2one('hr.department', 'Department',),
        'partner_id':fields.many2one('res.partner', 'Partner',),
        'state':fields.selection([('executed', 'Executed Requests'),('all','All Requests')], 'State',required=True),
    }

    _defaults = {
        'state': 'all',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'service.wiz', context=c),
    }

    def onchange_cato(self,cr,uid,ids,category):
        """ 
        Get domain for service types according to category.

        @return: list of months
        """
        serv_obj =self.pool.get('fleet.service.type')
        domain = category and [('category','=',category)] or []
        values ={}
        ser_name = serv_obj.search(cr, uid,domain )
        for serv in serv_obj.browse(cr, uid, ser_name):
            values.update({serv.name : serv.name})
        if values:
            return {'domain':{'service_type':[('name','in',values),('category','!=','service')]}}
        else:
            return {'domain':{'service_type':[('name','=',None),('category','!=','service')]}}

    def print_report(self, cr, uid, ids, context=None):
        """ 
        Print report.

        @return: Dictionary of print attributes
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'fleet.vehicle.log.contract',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'service.report',
            'datas': datas,
            }

