# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from openerp import tools
from itertools import groupby
from operator import itemgetter
import math


class operators_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.context = context
        super(operators_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'lines':self.lines,
        })

    def get_date(self,str):
        return datetime.strptime(str, "%Y-%m-%d")

    def get_move_lines(self, start_date, end_date, accounts):
        count = 0
        self.move_lines = {}
        self.rest = {}
        self.sum_debit = {}
        self.sum_credit = {}
        self.accounts = {}
        self.partners_names = {}
        account_move_line = self.pool.get('account.move.line')
        search_ids = account_move_line.search(self.cr,self.uid,[('account_id', 'in', accounts), ('partner_id','in',self.operators)])
        
        ids_start = ids_end = []
        
        if start_date != 'False' and end_date != 'False':
            ids_start = account_move_line.search(self.cr,self.uid,[('account_id', 'in', accounts), ('partner_id','in',self.operators),
            ('date','>=',start_date),('date','<=',end_date)])
            search_ids = []
        # if end_date != 'False':
        #     ids_end = account_move_line.search(self.cr,self.uid,[('account_id', 'in', accounts), ('partner_id','in',self.operators),
        #     ('date','<=',end_date)])
            search_ids = []
        all_ids = list(set(search_ids) | set(ids_start) | set(ids_end) )
        basic = account_move_line.browse(self.cr,self.uid,all_ids,context=self.context)
        for line in basic:
            self.accounts[line.account_id.id] = line.account_id.name
            self.partners_names[line.partner_id.id] = line.partner_id.name
            type = line.debit>0 and 'debit' or 'credit'
            
            #initialize caches
            self.move_lines[line.partner_id.id,line.account_id.id,type] = self.move_lines.get((line.partner_id.id,line.account_id.id,type),0)

            self.sum_debit[ line.partner_id.id] = self.sum_debit.get( line.partner_id.id , 0 )
            self.sum_credit[line.partner_id.id] = self.sum_credit.get(line.partner_id.id, 0 )


            #set caches
            
            if type == 'debit':
                self.sum_debit[ line.partner_id.id] += line.debit
                self.move_lines[line.partner_id.id,line.account_id.id,type] += line.debit

            if type == 'credit':
                self.sum_credit[line.partner_id.id] += line.credit
                self.move_lines[line.partner_id.id,line.account_id.id,type] += line.credit

            #self.rest[line.partner_id.id,line.account_id.id] += line.debit-line.credit
            #print ",,,,,,,,,,,,,,,,,,,,,,,",type,",,,,,,,,",line.debit+line.credit
            
        
    def lines(self,data):
        lines = []
        start_date = str(data['form']['start_date'])
        end_date = str(data['form']['end_date'])
        customers = data['form']['customer_ids']
        accounts = data['form']['account_ids']

        self.operators = customers
        if not self.operators:
            customer_obj = self.pool.get('res.partner')
            self.operators = customer_obj.search(self.cr, self.uid, [('customer','=',True)])
        if not self.operators:
            return []


        self.get_move_lines(start_date, end_date, accounts)

        sum_all = 0
        for partner in self.operators:
            if partner in self.partners_names:
                line = {'name'   :self.partners_names[partner],
                        'debit'  :0,
                        'credit' :0,
                        'rest'   :0,
                        'balance':0}
                lines.append(line)
            
            keys = filter(lambda x:x[0] == partner,self.move_lines)
            keys = [key[1] for key in keys]
            keys = list(set(keys))

            for key in keys:
                debit  = ( partner, key, 'debit')  in self.move_lines and self.move_lines[ ( partner, key, 'debit')  ] or 0
                credit = ( partner, key, 'credit') in self.move_lines and self.move_lines[ ( partner, key, 'credit') ] or 0
                
                line = {'name'   :self.accounts[key],
                        'debit'  :debit,
                        'credit' :credit,
                        'rest'   :0,
                        'balance':0}
                lines.append(line)
            
            
            if keys:
                debit = partner in self.sum_debit  and self.sum_debit[ partner ] or 0
                credit= partner in self.sum_credit and self.sum_credit[partner ] or 0

                rest = debit - credit
                #balance = rest < 0 and rest or 0

                #if rest < 0:
                #rest = 0
                
                rest     = math.fabs(rest)
                sum_all += rest

                line = {'name'   :'المجموع',
                        'debit'  :debit,
                        'credit' :credit,
                        'rest'   :rest,
                        'balance':rest}
                lines.append(line)

        line = {'name'   :'إجمالي المديونية',
                'debit'  :0,
                'credit' :0,
                'rest'   :0,
                'balance':sum_all}
        lines.append(line)
        return lines


report_sxw.report_sxw('report.operator_report.report', 'operator.report', 'addons/account_ntc/report/operators_report.rml' ,parser=operators_report,header=False )