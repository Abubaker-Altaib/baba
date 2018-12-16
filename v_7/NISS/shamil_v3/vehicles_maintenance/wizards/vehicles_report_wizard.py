# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import time
from tools.translate import _


class vehicles_report(osv.osv_memory):
    """ To manage vehicles report wizard """

    _name = "vehicle.report.wizard"

    _columns = {
        'type': fields.selection([('movements', 'Movements'), ('maintes', 'Maintenances'), ('accidents', 'Accedents')], 'Type', required=True),
        'start_date': fields.date('Start Date', required=True),
        'end_date': fields.date('End Date', required=True),
        'departments_ids': fields.many2many('hr.department', 'vehicles_report_department_rel', 'vehicles_report_id', 'department_id', 'Departments'),
        'child_departments': fields.boolean('Child Departments'),
        'vehicles_ids': fields.many2many('fleet.vehicle', 'vehicles_report_vehicle_rel', 'vehicles_report_id', 'vehicle_id', 'Vehicles'),
    }

    _defaults = {
        'start_date': time.strftime('%Y-%m-%d'),
        'end_date': time.strftime('%Y-%m-%d'),
    }

    def department_change(self, cr, uid, ids, departments_ids, context=None):
        domain = [('state', '=', 'confirm')]
        print "..............departments_ids", departments_ids
        if departments_ids and departments_ids[0][2]:
            domain += ['|', ('department_id', 'in', departments_ids[0][2]),
                       ('department_id', 'child_of', departments_ids[0][2])]
        return {
            'vals': {
                'vehicles_ids': False
            },
            'domain': {
                'vehicles_ids': domain
            },
        }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]

        if data['departments_ids'] and data['child_departments']:
            new_departments_ids = data['departments_ids']
            department_obj = self.pool.get('hr.department')
            for dep in data['departments_ids']:
                new_departments_ids += department_obj.search(cr, uid, [(
                    'id', 'child_of', dep), ('id', 'not in', new_departments_ids)])
            data['departments_ids'] = new_departments_ids

        datas = {
            'ids': [],
            'model': 'fleet.vehicle',
            'form': data
        }
        if data['type'] == 'movements':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'vehicles_movements_report.report',
                'datas': datas,
            }
        if data['type'] == 'maintes':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'vehicles_maintes_report.report',
                'datas': datas,
            }
        if data['type'] == 'accidents':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'vehicles_accidents_report.report',
                'datas': datas,
            }
