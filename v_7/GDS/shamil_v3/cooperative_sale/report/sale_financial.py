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
                            else :
                                dic.append({ 'name': 'all'
                                             })
           return dic

# Method to get data      
    def get_sale_order_data(self,data):
           process_type = data['form']['process_type'] 
           order_lines = data['form']['order_cancel_lines']
           sale_order_obj=self.pool.get('sale.order')
           #company_id = data['form']['company_id']
           #category_id = data['form']['category_id']
           #location_id = data['form']['location_id']
           #payroll_id = data['form']['scale_id']
           #payment_type = data['form']['payment_type']
           #receive_state = data['form']['receive_state']
           #emp_id = data['form']['emp_id']
           #report_type = data['form']['report_type']
           #conditions = "and emp.payroll_id=%s"%payroll_id[0]
           #if company_id :
            #  		conditions = conditions + " and so.company_id=(%s)"%company_id[0] 
           #if category_id :
            #  		conditions = conditions + " and so.category_id=(%s)"%category_id[0] 
           #if location_id :
           #   		conditions = conditions + " and so.shop_id=(%s)"%location_id[0]
	       #if payment_type :
			#conditions = conditions + " and so.payment_type='%s'"%payment_type
           #if emp_id :
            #  		conditions = conditions + " and so.employee_id=(%s)"%emp_id[0]

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
           #company_id = data['form']['company_id']
           #category_id = data['form']['category_id']
           #location_id = data['form']['location_id']
           #payroll_id = data['form']['scale_id']
           #payment_type = data['form']['payment_type']
           #receive_state = data['form']['receive_state']
           #emp_id = data['form']['emp_id']
           #report_type = data['form']['report_type']
           #conditions = "and emp.payroll_id=%s"%payroll_id[0]
           #if company_id :
            #  		conditions = conditions + " and so.company_id=(%s)"%company_id[0] 
           #if category_id :
            #  		conditions = conditions + " and so.category_id=(%s)"%category_id[0] 
           #if location_id :
           #   		conditions = conditions + " and so.shop_id=(%s)"%location_id[0]
	       #if payment_type :
			#conditions = conditions + " and so.payment_type='%s'"%payment_type
           #if emp_id :
            #  		conditions = conditions + " and so.employee_id=(%s)"%emp_id[0]

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
                            note = obj.financial_notes
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
           #company_id = data['form']['company_id']
           #category_id = data['form']['category_id']
           #location_id = data['form']['location_id']
           #payroll_id = data['form']['scale_id']
           #payment_type = data['form']['payment_type']
           #receive_state = data['form']['receive_state']
           #emp_id = data['form']['emp_id']
           #report_type = data['form']['report_type']
           #conditions = "and emp.payroll_id=%s"%payroll_id[0]
           #if company_id :
            #  		conditions = conditions + " and so.company_id=(%s)"%company_id[0] 
           #if category_id :
            #  		conditions = conditions + " and so.category_id=(%s)"%category_id[0] 
           #if location_id :
           #   		conditions = conditions + " and so.shop_id=(%s)"%location_id[0]
	       #if payment_type :
			#conditions = conditions + " and so.payment_type='%s'"%payment_type
           #if emp_id :
            #  		conditions = conditions + " and so.employee_id=(%s)"%emp_id[0]
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


    """def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('sale.order').browse(self.cr, self.uid, ids, self.context):
            if obj.state != 'invoice' :
		            raise osv.except_osv(_('Error!'), _('You can not print this sale financial, This order not process yet!'))
            if obj.payment_type == 'installment' :
		            raise osv.except_osv(_('Error!'), _('You can not print this sale financial, This order have no Financial Process!'))  
            #if obj.payment_type == 'cash' :
                #if obj.invoice_ids[0].state == 'draft':
		            #raise osv.except_osv(_('Error!'), _('You can not print this order, first go and pay !'))
            if obj.print_financial == True :
		            raise osv.except_osv(_('Error!'), _('You already printed this sale financial ,,, check adminstrator!'))
            if obj.financial_note == False :
                note=""
            else :
                note = obj.financial_note
            u = self.pool.get('res.users').browse(self.cr, self.uid,self.uid).name
            notes = note +'\n'+'Sale Financial Printed at : '+time.strftime('%Y-%m-%d %H:%M:%S') + ' by '+ u
            self.pool.get('sale.order').write(self.cr, self.uid, ids, {'print_financial':True,'financial_note':notes})
        return super(sale_financial, self).set_context(objects, data, ids, report_type=report_type)
# generate the text of origin and copy



    def _show_discount(self, uid, context=None):
        cr = self.cr
        try: 
            group_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'group_discount_per_so_line')[1]
        except:
            return False
        return group_id in [x.id for x in self.pool.get('res.users').browse(cr, uid, uid, context=context).groups_id]"""

report_sxw.report_sxw('report.sale.financial', 'sale.order', 'addons/cooperative_sale/report/sale_financial.rml', parser=sale_financial,header=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

