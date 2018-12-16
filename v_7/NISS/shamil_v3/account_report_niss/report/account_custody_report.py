# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
from account_custom.common_report_header import common_report_header as common_header
from account.report.common_report_header import common_report_header as custom_common_header

class account_employee_custody(report_sxw.rml_parse, common_header, custom_common_header):

    def set_context(self, objects, data, ids, report_type=None):
        obj_move = self.pool.get('account.move.line')
        new_ids = ids
        self.custody_state = data['form']['custody_state']
        self.target_move = data['form']['target_move']
        self.partner = data['form']['partner_id']
        self.date_from = data['form']['date_from']
        self.date_to = data['form']['date_to']
        self.currency = data['form']['currency_id']
        self.partner_details = {}
        objects = self.pool.get('account.move.line').browse(self.cr, self.uid, new_ids)
        return super(account_employee_custody, self).set_context(objects, data, ids, report_type=report_type)

    def __init__(self, cr, uid, name, context=None):
        super(account_employee_custody, self).__init__(cr, uid, name, context=context)
        self.sum_amount = 0.0
        self.context = context
        self.localcontext.update({
            'lines': self.lines,
            'get_date_from': self.get_date_from,
            'get_date_to': self.get_date_to,
            'get_end_date_from': self.get_end_date_from,
            'get_end_date_to': self.get_end_date_to,
            'get_custody_state': self._get_custody_state,
            'get_target_move': self._get_target_move,
            'balance':self.balance,
            'get_currency':self.get_currency,
            'get_partner':self._get_partner,
            'partner_data':self._partner_data,
            'get_report_type': self._get_report_type,
            'get_department': self._get_department,
    })

    def _get_partner(self, data, return_type = 'id_only'):
        report_line_obj = self.pool.get('custody.report.line')
        line_ids = data['form']['report_line_ids']
        partner_ids = [-1]
        if line_ids and data['form']['report_type'] in ['grouped', 'name_only']:
            partner_ids = [line.partner_id and line.partner_id.id or -1 for line in report_line_obj.browse(self.cr, self.uid, line_ids) ]
            partner_ids.append(0)
            partner_ids = list(set(partner_ids))
            where_clause = " and p.id in " + str(tuple(partner_ids))
            sql_query = """SELECT  p.id as id, coalesce(degree.id,0) as d_id, p.name as name,p.code as code, 
                                   degree.name as degree_name ,d.name as department_name
                             FROM   res_partner p
                             lEFT JOIN res_users u on (p.id = u.partner_id)
                             LEFT  JOIN resource_resource r on (u.id = r.user_id)
                             LEFT JOIN hr_employee h on (h.resource_id = r.id)
                             LEFT JOIN hr_salary_degree degree on (h.degree_id = degree.id)
                             LEFT JOIN hr_department d ON  h.department_id = d.id 
                             WHERE 1=1 """ + where_clause + " order by d_id desc"
            self.cr.execute(sql_query )
            res = self.cr.dictfetchall()
            if return_type <> 'id_only' :
                return res
            partner_ids =[ line['id'] for line in res]
        return partner_ids
    '''
SELECT  p.name as name,p.code as code,d.name as department_name, degree.name as degree_name 
                             FROM   res_partner p
                             LEFT JOIN res_users u on (p.id = u.partner_id)
                             LEFT  JOIN resource_resource r on (u.id = r.user_id)
                             LEFT JOIN hr_employee h on (h.resource_id = r.id)
                             LEFT JOIN hr_salary_degree degree on (h.degree_id = degree.id)
                             LEFT JOIN hr_department d ON  p.department_id = d.id 
                             WHERE p.id = %s 
    '''
    def _partner_data(self, data, partner_id):
        sql_query = """SELECT  p.name as name,p.code as code,d.name as department_name \
                             FROM   res_partner p
                             LEFT JOIN hr_department d ON  p.department_id = d.id \
                             WHERE p.id = %s  """%partner_id
        self.cr.execute(sql_query )
        res = []
        res = self.cr.dictfetchall()
        if partner_id == -1:
            res.append({ 'name': 'بدون موظف', 'code' : '' ,'department_name': '' }) 
        return res[0]

    def _get_custody_state(self, data):
        return data['form']['custody_state']

    def _get_report_type(self, data):
        return data['form']['report_type']

    def get_date_from(self, data):
        return data['form']['date_from']

    def get_date_to(self, data):
        return data['form']['date_to']

    def get_end_date_from(self, data):
        return data['form']['end_date_from']

    def get_end_date_to(self, data):
        return data['form']['end_date_to']

    def get_target_move(self, data):
        return data['form']['target_move']

    def _get_department(self, data):
        return data['form']['department_id']

    def lines(self, data, partner_id):
        report_line_obj = self.pool.get('custody.report.line')
        line_ids = data['form']['report_line_ids']
        voucher_line_ids = []
        if line_ids:
            voucher_line_ids = [line.voucher_line_id.id for line in report_line_obj.browse(self.cr, self.uid, line_ids)]
        voucher_line_ids.append(-1)
        voucher_line_ids.append(-2)
        where_clause = " and l.id in " + str(tuple(voucher_line_ids))
        if partner_id:
            if partner_id == -1 :
                where_clause += " and  l.res_partner_id is NuLL"
            else:
                where_clause += " and p.id = %s"%partner_id

        #if self.date_from:
        #     where_clause += " and v.date >= '" + self.date_from + "'"
        #if self.date_to:
        #     where_clause += " and v.date <= '" + self.date_to + "'"
        #if self.custody_state =='removed':
        #    where_clause += " and l.custody_state = 'removed' "
        #if self.custody_state =='not removed':
        #    where_clause += " and l.custody_state = 'not removed' "
        sql_query = """SELECT l.custody_end_date as end_date, l.amount as amount,\
                                    substring(v.chk_seq ,length(v.chk_seq)-5, 6 ) AS chk_seq\
                                    ,substring(v.number,length(v.number)-12, 13 ) as ref,l.permission as permission, \
                                    l.name AS name, v.date AS date , p.name as emp_name,p.code as emp_code, \
                                    c.name as currency_name \
                             FROM   account_voucher_line l INNER JOIN account_voucher v ON  l.voucher_id = v.id \
                             left JOIN res_partner p ON  l.res_partner_id = p.id \
                             INNER JOIN res_currency c ON  v.currency_id = c.id \
                             WHERE 1=1  """ + where_clause + " ORDER BY v.date "

        '''if data['form']['group_report'] and data['form']['custody_state'] :
            partner_ids = self._get_partner(data)
            #where_clause = " and l.res_partner_id in " + str(tuple(partner_ids))
            sql_query = """SELECT sum(ml.debit ) AS amount, p.id as emp_name,max(p.code) as emp_code\
                                   
                             FROM   account_voucher_line l INNER JOIN account_voucher v ON  l.voucher_id = v.id \
                             left JOIN res_partner p ON  l.res_partner_id = p.id \
                             INNER JOIN res_currency c ON  v.currency_id = c.id \
                             INNER JOIN account_move_line ml ON  ml.voucher_line_id = l.id \
                             WHERE 1=1 and ml.credit = 0  """ + where_clause + "  group by p.id, p.name  ORDER BY p.code "'''

        self.cr.execute(sql_query )


        res = self.cr.dictfetchall()

        self.sum_amount = 0
        for line in res:
            self.sum_amount+=line['amount']
        print"rrrrrrrrrrrrrr",res
        return res

    def get_currency(self):
        return self.currency and self.currency[1] or False

    def balance(self):
        return self.sum_amount

report_sxw.report_sxw('report.employee.custody', 'account.account', 'addons/account_report_niss/report/account_custody_report.rml', parser= account_employee_custody, header='external')



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
