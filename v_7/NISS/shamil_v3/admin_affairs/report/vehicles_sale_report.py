# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw


class vehicles_sale_report(report_sxw.rml_parse):

    
    def __init__(self, cr, uid, name, context):
        self.context = context
        super(vehicles_sale_report, self).__init__(cr, uid, name, context)
        sale_type = {
            'pension' : unicode('معاشيين', 'utf-8') ,
            'public' : unicode('عامة', 'utf-8'),
        }
        self.localcontext.update({
            'line': self._get_sale,
            'lines': self._get_lines,
            'sale_type':sale_type,
        })

    def _get_sale(self, data):
        res=[]
        sale_ids=[]
        sales=[]
        sale_obj = self.pool.get('vehicle.sale')
        line_obj = self.pool.get('vehicle.sale.lines')
        ttype=str(data['form']['type'])
        sale_type=str(data['form']['sale_type'])
        start_date=data['form']['start_date']
        end_date=data['form']['end_date']

        if start_date and end_date:
            if sale_type == 'pension':
                sale_ids= sale_obj.search(self.cr, self.uid, [('state', '=', 'confirm'),('sale_type', '=', 'pension'),('sale_date', '>=', start_date),('sale_date', '<=', end_date)])
            elif sale_type == 'public':
                sale_ids= sale_obj.search(self.cr, self.uid, [('state', '=', 'confirm'),('sale_type', '=', 'public'),('sale_date', '>=', start_date),('sale_date', '<=', end_date)])
            else:
                sale_ids= sale_obj.search(self.cr, self.uid, [('state', '=', 'confirm'),('sale_date', '>=', start_date),('sale_date', '<=', end_date)])
        elif start_date and not end_date:
            if sale_type == 'pension':
                sale_ids= sale_obj.search(self.cr, self.uid, [('state', '=', 'confirm'),('sale_type', '=', 'pension'),('sale_date', '>=', start_date)])
            elif sale_type == 'public':
                sale_ids= sale_obj.search(self.cr, self.uid, [('state', '=', 'confirm'),('sale_type', '=', 'public'),('sale_date', '>=', start_date)])
            else:
                sale_ids= sale_obj.search(self.cr, self.uid, [('state', '=', 'confirm'),('sale_date', '>=', start_date)])       
        elif not start_date and end_date:
            if sale_type == 'pension':
                sale_ids= sale_obj.search(self.cr, self.uid, [('state', '=', 'confirm'),('sale_type', '=', 'pension'),('sale_date', '<=', end_date)])
            elif sale_type == 'public':
                sale_ids= sale_obj.search(self.cr, self.uid, [('state', '=', 'confirm'),('sale_type', '=', 'public'),('sale_date', '<=', end_date)])
            else:
                sale_ids= sale_obj.search(self.cr, self.uid, [('state', '=', 'confirm'),('sale_date', '<=', end_date)])
        else:
            if sale_type == 'pension':
                sale_ids= sale_obj.search(self.cr, self.uid, [('state', '=', 'confirm'),('sale_type', '=', 'pension')])
            elif sale_type == 'public':
                sale_ids= sale_obj.search(self.cr, self.uid, [('state', '=', 'confirm'),('sale_type', '=', 'public')])
            else:
                sale_ids= sale_obj.search(self.cr, self.uid, [('state', '=', 'confirm')])

        for sale in sale_ids:
            if ttype == 'model':
                model_ids=data['form']['model_ids']
                if model_ids:
                    res_ids= line_obj.search(self.cr, self.uid, [('model_id', 'in', model_ids),('sale_id','=',sale)])
                else:
                    res_ids= line_obj.search(self.cr, self.uid, [('sale_id','=',sale)])

                if res_ids:
                    sales.append(sale)

            elif ttype == 'type':
                type_ids=data['form']['type_ids']
                if type_ids:
                    res_ids= line_obj.search(self.cr, self.uid, [('vehicle_type', 'in', type_ids),('sale_id','=',sale)])
                else:
                    res_ids= line_obj.search(self.cr, self.uid, [('sale_id','=',sale)])
                if res_ids:
                    sales.append(sale)
        res=sale_obj.browse(self.cr, self.uid, sales)
        
        return res

    def _get_lines(self, data,sale_id):
        res=[]
        line_obj = self.pool.get('vehicle.sale.lines')
        ttype=str(data['form']['type'])

        for sale in [sale_id.id]:
            if ttype == 'model':
                model_ids=data['form']['model_ids']
                if model_ids:
                    res_ids= line_obj.search(self.cr, self.uid, [('model_id', 'in', model_ids),('sale_id','=',sale)])
                else:
                    res_ids= line_obj.search(self.cr, self.uid, [('sale_id','=',sale)])
                res=line_obj.browse(self.cr, self.uid, res_ids)

            elif ttype == 'type':
                type_ids=data['form']['type_ids']
                if type_ids:
                    res_ids= line_obj.search(self.cr, self.uid, [('vehicle_type', 'in', type_ids),('sale_id','=',sale)])
                else:
                    res_ids= line_obj.search(self.cr, self.uid, [('sale_id','=',sale)])
                res=line_obj.browse(self.cr, self.uid, res_ids)
        return res


report_sxw.report_sxw('report.vehicles_sale_report.report', 'vehicle.sale',
                      'addons/admin_affairs/report/vehicles_sale_report.rml', parser=vehicles_sale_report, header=True)
