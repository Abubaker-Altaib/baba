# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
import calendar
from datetime import datetime
import pooler
from openerp.tools.translate import _


def to_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date()


class fuel_in_details_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        print "........................ddddddddddddddddd"
        self.count = 0
        self.context = context
        super(fuel_in_details_report, self).__init__(cr, uid, name, context)
        self.h_deps_ids = []
        self.localcontext.update({
            'lines': self._get_lines,
            'get_count': self._get_count,
            'to_arabic': self._to_arabic,
            'get_name': self._get_name,
            'set_count': self._set_count,
        })

    def _get_name(self, data):
        key = _(data)
        department_obj = self.pool.get('hr.department')
        name = department_obj.name_get_custom(self.cr, self.uid, [data])[0][1]
        return name

    def _to_arabic(self, data):
        key = _(data)
        if self.context and 'lang' in self.context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                self.cr, self.uid, [('module', '=', 'hr_custom_military'), ('type', '=', 'selection'), ('src', 'ilike', key), ('lang', '=', self.context['lang'])], context=self.context)
            translation_recs = translation_obj.read(
                self.cr, self.uid, translation_ids, [], context=self.context)
            key = translation_recs and translation_recs[0]['value'] or key

        return key

    def _get_lines(self, data):
        date_from = data['date_from']
        date_to = data['date_to']
        locations_ids = data['locations_ids']
        product_id = data['product_id']
        company_id = data['company_id']

        conditions = " "
        conditions2 = " "

        if company_id:
            conditions += " and pick.company_id=(%s)" % company_id[0]

        if locations_ids:
            locations_ids += locations_ids
            locations_ids = tuple( locations_ids )
            conditions += " and move.location_dest_id in %s " % (locations_ids,)
        if product_id:
            conditions += " and pdc.id=(%s)" % product_id

        self.cr.execute("""
            select pick.id, pick.name, pick.stock_in_type,pdc.fuel_type, dest_location.name as recieve_location, 
            pick.deliver_fuel_product_qty as requested_qty, pick.fuel_product_qty as recieved_qty,
            (pick.deliver_fuel_product_qty - pick.fuel_product_qty ) as div_qty, pick.reason,  p_temp.standard_price, (move.product_qty*p_temp.standard_price) as sum_price 
            From stock_picking pick 
                left join stock_move move on (pick.id=move.picking_id)
                left join product_product pdc on (move.product_id=pdc.id)
                left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id) 
                left join product_category cat on (p_temp.categ_id=cat.id)
                left join stock_location dest_location on (dest_location.id = pick.fuel_location_dest_id)
            where (to_char(pick.date,'YYYY-mm-dd')>=%s and to_char(pick.date,'YYYY-mm-dd')<=%s) and pick.state = ('done') and pick.fuel_ok = True and pick.type = 'in'
            """ + conditions, (date_from, date_to))
        res = self.cr.dictfetchall()

        self.cr.execute("""
            select well.name, p_w.recieved_amount, p_w.picking_id from picking_well p_w
            left join fuel_well well on (p_w.well_id=well.id)""" )
        well_res = self.cr.dictfetchall()

        locations_dict_list = {}
        for rec in res:
            locations_dict_list[rec['recieve_location']] = locations_dict_list.get(rec['recieve_location'], 
            {'name': rec['recieve_location'], 'lines':[]})

            if well_res:
                rec['wells'] = filter(lambda x: x['picking_id']==rec['id'], well_res) or []

            locations_dict_list[rec['recieve_location']]['lines'].append(rec)
        
        return locations_dict_list


    def _get_count(self):
        self.count = self.count + 1
        return self.count
    
    def _set_count(self):
        self.count = 0
        return ''
                            
report_sxw.report_sxw('report.fuel.fuel_in_details.report', 'stock.picking.in',
                      'addons/fuel_niss/report/fuel_in_details_report.mako', parser=fuel_in_details_report, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
