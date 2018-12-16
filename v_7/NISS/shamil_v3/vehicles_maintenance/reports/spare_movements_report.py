# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw


class spare_movements_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.context = context
        self.total = {'month1': 0, 'month2': 0}
        super(spare_movements_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'line': self._getdata,
        })

    def _getdata(self, data):
        """
        @return: dictionary of report data
        """
        lines = {}
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        locations_ids = data['form']['locations_ids']

        picking_in_obj = self.pool.get('stock.picking.in')
        picking_out_obj = self.pool.get('stock.picking.out')

        stock_move_obj = self.pool.get('stock.move')

        domain = [('maintenance','=', True), ('state', '=', 'done')]
        if start_date:
            domain.append(('date', '>=', start_date))

        if end_date:
            domain.append(('date', '<=', end_date))
        picking_in_ids = picking_in_obj.search(self.cr, self.uid, domain)
        picking_out_ids = picking_out_obj.search(self.cr, self.uid, domain)

        all_picking_ids = picking_in_ids + picking_out_ids

        all_move_ids = stock_move_obj.search(
            self.cr, self.uid, [('picking_id', 'in', all_picking_ids)])

        move_list = []
        for move in stock_move_obj.browse(self.cr, self.uid, all_move_ids):
            if locations_ids:
                if move.location_id.id not in locations_ids and move.location_dest_id.id not in locations_ids:
                    continue
            if not move.location_id.is_maintenance_location and not move.location_dest_id.is_maintenance_location:
                continue
            
            move_list.append(move)

        return move_list


report_sxw.report_sxw('report.spare_movements_report.report', 'stock.move',
                      'addons/vehicles_maintenance/reports/spare_movements_report.rml', parser=spare_movements_report, header=True)
