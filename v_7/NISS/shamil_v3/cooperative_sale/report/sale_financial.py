# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import re
import pooler
from osv import fields, osv
import time
from report import report_sxw
from openerp.tools.translate import _

class sale_financial(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(sale_financial, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'check' : self.get_sale_order_check,
            'function' : self.get_sale_order_data,
            'function2' : self.get_sale_order_data2,
            'function3' : self.get_sale_order_data_total3,  
            #'show_discount':self._show_discount,
            #'copy':self.make_copy,
        })
        self.context = context
    #def make_copy(self,para):
        #return [{'no': 1,'text': 'ORIGINAL'},{'no': 2,'text': 'COPY',}]


# Method to get data      
    def get_sale_order_check(self,data):
           process_type = data['form']['process_type'] 
           order_lines = data['form']['order_cancel_lines']
           sale_order_obj=self.pool.get('sale.order')
           dic = []
           for print_record in order_lines :
                for obj in self.pool.get('sale.order').browse(self.cr, self.uid, [print_record], self.context):
                            if obj.print_financial == True :
                                raise osv.except_osv(_('Error!'), _('You can not print %s \nthis sale financial, you already print it!')% (obj.name))
           dic.append({ 'name': 'all'})
           return dic

# Method to get data      
    def get_sale_order_data(self,data):
           process_type = data['form']['process_type'] 
           order_lines = data['form']['order_cancel_lines']
           sale_order_obj=self.pool.get('sale.order')

           dic = []
           for print_record in order_lines :
                for obj in self.pool.get('sale.order').browse(self.cr, self.uid, [print_record], self.context):
                        if obj.payment_type == 'cash':
                            """if obj.print_financial == True :
    		                    raise osv.except_osv(_('Error!'), _('You can not print %s \nthis sale financial, you already print it!')% (obj.name))
                            else :"""
                            sale_id = sale_order_obj.invoice(self.cr,self.uid,[obj.id],self.context)
           for order_id in order_lines :
                self.cr.execute( """
                		        select                        
                                	distinct so.name as name ,
                                    so.id as id ,
                                    sum (l.price_unit * l.product_uom_qty ) as amount
                                
                                From sale_order so              
					                left join sale_order_line l on (so.id = l.order_id)
                                where so.payment_type='cash' and so.id =%s
                                group by so.name , so.id"""%order_id) 
                move = self.cr.dictfetchall()
                for line in move :
                    for obj in self.pool.get('sale.order').browse(self.cr, self.uid, [line['id']], self.context):
                        notes = ""
                        note = ""
                        """notes = ""
                        if obj.print_financial == True :
    		                raise osv.except_osv(_('Error!'), _('You can not print %s \nthis sale financial, you already print it!')% (obj.name))  
                        else :"""
                        if obj.financial_note :
                            note = obj.financial_note
                        u = self.pool.get('res.users').browse(self.cr, self.uid,self.uid).name
                        notes = note +'\n'+'Sale Financial Printed at : '+time.strftime('%Y-%m-%d %H:%M:%S') + ' by '+ u
                        sale_order_obj.write(self.cr ,self.uid , line['id'] , {'print_financial' : True ,'financial_note':notes},context = self.context)
                        #update_id = self.cr.execute( """ update sale_order set print_financial=True,financial_note=%s where id=%s""",(notes,line['id']))
                    dic.append({ 'name': line['name'],'id':line['id'],'amount': line['amount']
                                })
           return dic


# Method to get data      
    def get_sale_order_data2(self,data):
           process_type = data['form']['process_type'] 
           order_lines = data['form']['order_cancel_lines']
           sale_order_obj=self.pool.get('sale.order')

           dic = []
           for print_record in order_lines :
                for obj in self.pool.get('sale.order').browse(self.cr, self.uid, [print_record], self.context):
                        notes = ""
                        if obj.payment_type == 'up_cash':
                            """if obj.print_financial == True :
    		                    raise osv.except_osv(_('Error!'), _('You can not print %s \nthis sale financial, you already print it!')% (obj.name))
                            else :"""
                            sale_id = sale_order_obj.invoice(self.cr,self.uid,[obj.id],self.context)
           for order_id in order_lines :
                self.cr.execute( """
                		        select                        
                                	distinct so.name as name ,
                                    so.id as id , 
                                    sum (l.up_front * l.product_uom_qty) as amount
                                
                                From sale_order so              
					                left join sale_order_line l on (so.id = l.order_id)
                                where so.payment_type='up_cash' and so.id =%s
                                group by so.name,so.id"""%order_id) 
                move = self.cr.dictfetchall()
                for line in move :
                    for obj in self.pool.get('sale.order').browse(self.cr, self.uid, [line['id']], self.context):
                        notes =""
                        note =""
                        """notes = ""
                        if obj.print_financial == True :
    		                raise osv.except_osv(_('Error!'), _('You can not print %s \nthis sale financial, you already print it!')% (obj.name))  
                        else :"""
                        if obj.financial_note :
                            note = obj.financial_note
                        u = self.pool.get('res.users').browse(self.cr, self.uid,self.uid).name
                        notes = note +'\n'+'Sale Financial Printed at : '+time.strftime('%Y-%m-%d %H:%M:%S') + ' by '+ u
                        sale_order_obj.write(self.cr ,self.uid , line['id'] , {'print_financial' : True ,'financial_note':notes},context = self.context)
                            #update_id = self.cr.execute( """ update sale_order set print_financial=True,financial_note=%s where id=%s""",(notes,line['id']))
                    dic.append({ 'name': line['name'],'id':line['id'],'amount': line['amount']
                                })
           return dic


# Method to get data      
    def get_sale_order_data_total3(self,data):
           process_type = data['form']['process_type'] 
           order_lines = data['form']['order_cancel_lines']
           dic = []
           cash = 0
           up_cash = 0
           total = 0
           for order_id in order_lines :
                self.cr.execute( """
                		        select                        
                                    sum (l.price_unit * l.product_uom_qty ) as amount_cash
                                
                                From sale_order so              
					                left join sale_order_line l on (so.id = l.order_id)
                                where so.payment_type='cash' and so.id =%s"""%order_id) 
                move = self.cr.dictfetchall()
                self.cr.execute( """
                		        select                        
                                    sum (l.up_front * l.product_uom_qty) as amount_upcash
                                
                                From sale_order so              
					                left join sale_order_line l on (so.id = l.order_id)
                                where so.payment_type='up_cash' and so.id =%s"""%order_id) 
                move2 = self.cr.dictfetchall()
                for line in move :
                    if line['amount_cash'] != None :
                        cash += line['amount_cash']
                for line2 in move2 :
                    if line2['amount_upcash'] != None :
                        up_cash += line2['amount_upcash']
           total = cash+up_cash
           dic.append({'cash':cash,'up_front':up_cash,'total': total}) 
           return dic


report_sxw.report_sxw('report.sale.financial', 'sale.order', 'addons/cooperative_sale/report/sale_financial.rml', parser=sale_financial,header=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

