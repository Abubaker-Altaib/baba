# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
import pooler
from report import report_sxw
from account_ntc.report import account_profit_loss
from account_custom.common_report_header import common_report_header
from tools.translate import _

class report_balancesheet_horizontal(report_sxw.rml_parse, common_report_header):
    def __init__(self, cr, uid, name, context=None):
        super(report_balancesheet_horizontal, self).__init__(cr, uid, name, context=context)
        self.obj_pl = account_profit_loss.report_pl_account_horizontal(cr, uid, name, context=context)
        self.result_sum_dr = 0.0
        self.result_sum_cr = 0.0
        self.result = {}
        self.res_bl = {}
        self.pl_bal = {} #nctr
        self.result_temp = []
        self.localcontext.update({
            'time': time,
            'get_lines': self.get_lines,
            'get_lines_another': self.get_lines_another,
            'get_company': self._get_company,
            'get_currency': self._get_currency,
            'sum_dr': self.sum_dr,
            'sum_cr': self.sum_cr,
            'get_data':self.get_data,
            'get_pl_balance':self.get_pl_balance,
            'get_fiscalyear': self._get_fiscalyear,
            'get_account': self._get_account,
            'get_start_period': self.get_start_period_br,
            #'get_end_period': self.get_end_period,
            #'get_sortby': self._get_sortby,
            'get_filter': self._get_filter,
            'get_journal': self._get_journal,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_company':self._get_company,
            'get_target_move': self._get_target_move,
            'get_filter_Trans':self._get_filter_Trans,
            'display_account':self._display_account,
            'get_multi_company': self._get_multi_company,
           
        })
        self.context = context

    def _get_account(self, data):
        """
        @return: browse record for the selected fiscalyear_id
        """
        if data.get('form', False) and data['form'].get('chart_account_id', False):
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['chart_account_id']).name
        return ''

    def _get_fiscalyear(self, data):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            return self.pool.get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).name
        return ''

    def _get_start_date(self, data):
        if data.get('form', False) and data['form'].get('date_from', False):
            return data['form']['date_from']
        return ''

    def _get_end_date(self, data):
        if data.get('form', False) and data['form'].get('date_to', False):
            return data['form']['date_to']
        return ''

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        self.result_selection = data['form'].get('display_account')
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(report_balancesheet_horizontal, self).set_context(objects, data, new_ids, report_type=report_type)

    def sum_dr(self):
        #if self.res_bl['type'] == _('Net Profit'):
            #self.result_sum_dr += self.res_bl['balance']*-1

        return self.result_sum_dr 

    def sum_cr(self):
        #if self.res_bl['type'] == _('Net Loss'):
            #self.result_sum_cr += self.res_bl['balance']
        return self.result_sum_cr

    def get_pl_balance(self):
        return self.obj_pl.pl_balance()

    def get_data(self,data):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)

        #Getting Profit or Loss Balance from profit and Loss report
        self.obj_pl.get_data(data)
        self.res_bl = self.obj_pl.final_result()
        self.pl_bal= self.obj_pl.pl_balance() # call of function already defineded in profit and loss 

        account_pool = db_pool.get('account.account')
        currency_pool = db_pool.get('res.currency')

        types = [
            'liability',
            'asset'
        ]

        ctx = self.context.copy()
        ctx['fiscalyear'] = data['form'].get('fiscalyear_id', False)

        if data['form']['filter'] == 'filter_period':
            ctx['period_from'] = data['form'].get('period_from', False)
            ctx['period_to'] =  data['form'].get('period_to', False)

        elif data['form']['filter'] == 'filter_date':
            ctx['date_from'] = data['form'].get('date_from', False)
            ctx['date_to'] =  data['form'].get('date_to', False)
        ctx['state'] = data['form'].get('target_move', 'all')
        cal_list = {}
        pl_dict = {}
        account_dict = {}
        account_id = data['form'].get('chart_account_id', False)
        account_ids = account_pool._get_children_and_consol(cr, uid, account_id, context=ctx)
        accounts = account_pool.browse(cr, uid, account_ids, context=ctx)
      
        if not self.res_bl:
            self.res_bl['type'] = _('Net Profit')
            self.res_bl['balance'] = 0.0

        if self.res_bl['type'] == _('Net Profit'):
            self.res_bl['type'] = _('Net Profit')
        else:
            self.res_bl['type'] = _('Net Loss')
        pl_dict  = {
            'code': self.res_bl['type'],
            'name': self.res_bl['type'],
            'level': False,
            'balance':self.res_bl['balance'],
        }#account.id in (311,310,392) or 
        for typ in types:
            accounts_temp = []
            for account in accounts:
                if   (account.user_type.report_type) and (account.user_type.report_type == typ) and ( ( account.id <> 4 and typ == 'liability' ) or (account.id <> 5 and typ == 'asset')  ):
                    account_dict = {
                        'id': account.id,
                        'code': account.code,
                        'name': account.name,
                        'level': account.level,
                        'balance':account.balance,
                       
                    }
                   
                    currency = account.currency_id and account.currency_id or account.company_id.currency_id
                    if typ == 'liability' and account.user_type.code == 'liability-TB' and (account.debit <> account.credit):
                        self.result_sum_dr += account.balance 
                    if typ == 'asset' and account.user_type.code == 'asset-TB' and (account.debit <> account.credit):
                        self.result_sum_cr += account.balance
                    if data['form']['regular_account'] and account.type == 'view':
                        continue
                    if data['form']['display_account'] == 'bal_movement':
                        if account.credit> 0 or account.debit> 0 or not currency_pool.is_zero(self.cr, self.uid, currency, account.balance):
                            accounts_temp.append(account_dict)
                    elif data['form']['display_account'] == 'bal_solde':
                        if not currency_pool.is_zero(self.cr, self.uid, currency, account.balance):
                            accounts_temp.append(account_dict)
                    else:
                        accounts_temp.append(account_dict)
                    #if account.id == data['form']['reserve_account_id']:
                        #pl_dict['level'] = account['level'] + 1
                       # accounts_temp.append(pl_dict)

            self.result[typ] = accounts_temp
            cal_list[typ]=self.result[typ]


        if cal_list:
            temp = {}
            pl_temp = {}
            pl_temp={
                          'id': '',
                          'code': '1111',
                          'name': 'profit and lost',
                          'level':False,
                          'balance':self.pl_bal,   
                             
                          'code1': '',
                          'name1': '',
                          'level1': False,
                          'balance1':'',
                             
                          }
            
            for i in range(0,max(len(cal_list['liability']),len(cal_list['asset']))):
                if i < len(cal_list['liability']) and i < len(cal_list['asset']):
                  
                    temp={
                          'id': cal_list['liability'][i]['id'],
                          'code': cal_list['liability'][i]['code'],
                          'name': cal_list['liability'][i]['name'],
                          'level': cal_list['liability'][i]['level'],
                          'balance':cal_list['liability'][i]['balance'],
                         
                          'id1': cal_list['asset'][i]['id'],
                          'code1': cal_list['asset'][i]['code'],
                          'name1': cal_list['asset'][i]['name'],
                          'level1': cal_list['asset'][i]['level'],
                          'balance1':cal_list['asset'][i]['balance'],
                         
                          }
                    self.result_temp.append(temp)
                else:
                    
                    if i < len(cal_list['asset']):
                    
                        temp={
                              'code': '',
                              'name': '',
                              'level': False,
                              'balance':False,
                             
                              'id1': cal_list['asset'][i]['id'],
                              'code1': cal_list['asset'][i]['code'],
                              'name1': cal_list['asset'][i]['name'],
                              'level1': cal_list['asset'][i]['level'],
                              'balance1':cal_list['asset'][i]['balance'],
                              
                          }
                        self.result_temp.append(temp)
               
                    elif  i < len(cal_list['liability']):
                        
                        temp={
                              'id': cal_list['liability'][i]['id'],
                              'code': cal_list['liability'][i]['code'],
                              'name': cal_list['liability'][i]['name'],
                              'level': cal_list['liability'][i]['level'],
                              'balance':cal_list['liability'][i]['balance'],   
                             
                              'code1': '',
                              'name1': '',
                              'level1': False,
                              'balance1':False,
                             
                          }
                        self.result_temp.append(temp)
            self.result_temp.append(pl_temp)
        return None

    def get_lines(self):

        return self.result_temp

    def get_lines_another(self, group):
        
        return self.result.get(group, [])

    def _display_account(self):
        if self.result_selection == 'bal_all':
            return _('All Accounts')
        elif self.result_selection == 'bal_movement':
            return _('With movements')
        else:
            return _('With balance is not equal to 0')

report_sxw.report_sxw('report.account.balancesheet.horizontal.ntc', 'account.account',
    'addons/account_ntc/report/account_balance_sheet_horizontal_ntc.rml',parser=report_balancesheet_horizontal,
    header=False)

#report_sxw.report_sxw('report.account.balancesheet.arabic', 'account.account',
#    'addons/account_arabic_reportsv6/report/account_balance_sheet.rml',parser=report_balancesheet_horizontal,
#    header='external')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
