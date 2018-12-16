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

class order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'function' : self.get_sale_order_data,
            'line':self._getdetails, 
            'get_sum_items' : self._get_sum_of_items,
            #'show_discount':self._show_discount,
            #'copy':self.make_copy,
        })
        self.context = context

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
                        if obj.print_order == True :

    		               raise osv.except_osv(_('Error!'), _('You can not print %s \nthis sale order, you already print it!')% (obj.name))  
           for order_id in order_lines :
                self.cr.execute( """
                		select                        
                                	distinct so.name as name ,
					                so.id as id ,
                                	so.date_order as date_order,
                                	emp.name_related as employee,
                                	d.name as degree,
                                	emp.emp_code as code,
					                emp.otherid as other_id ,
                                    shop.name as shop, 
                                    so.amount_total as total
                                
                                From sale_order so
                    
                                	left join res_company comp on (so.company_id=comp.id)
                                	left join hr_employee emp on (so.employee_id=emp.id)
                                	left join hr_salary_scale scale on (emp.payroll_id = scale.id)
                                    left join hr_salary_degree d on (d.id = emp.degree_id )
                                	left join sale_shop shop on (shop.id= so.shop_id)
                                	left join sale_category cat on (so.category_id=cat.id)
					                left join sale_order_line l on (so.id = l.order_id)
                            where so.id =%s"""%order_id) 
                move = self.cr.dictfetchall()

                for line in move :
                    for obj in self.pool.get('sale.order').browse(self.cr, self.uid, [line['id']], self.context):
                        notes = ""
                        note = ""
                        """if obj.print_order == True :
    		                raise osv.except_osv(_('Error!'), _('You can not print %s \nthis sale order, you already print it!')% (obj.name))  
                        else :"""
                        if obj.note :
                            note = obj.note
                        u = self.pool.get('res.users').browse(self.cr, self.uid,self.uid).name
                        notes = note +'\n'+'Sale order Printed at : '+time.strftime('%Y-%m-%d %H:%M:%S') + ' by '+ u
                        sale_order_obj.write(self.cr ,self.uid , line['id'] , {'print_order' : True ,'note':notes},context = self.context)
                        #update_id = self.cr.execute( """ update sale_order set print_order=True,note=%s where id=%s""",(notes,line['id']))
                    dic.append({ 'total' : line['total'] , 'name': line['name'], 'code' : line['code'] ,'date_order': line['date_order'],'employee':line['employee'],
                                  'id':line['id'],'other_id':line['other_id'],'shop':line['shop'],'degree':line['degree']
                                }) 

           return dic


    def _get_sum_of_items(self,data):
        order_ids = data['form']['order_cancel_lines']

        condition = ""
        if len(order_ids) == 1:
                condition = " where so.id in (%s)"%order_ids[0]
        else:
                order_ids = tuple(order_ids)
                condition = " where so.id in %s"%str(order_ids) 

        self.cr.execute("""
                SELECT 
                  p.name_template as name ,
				  cast(sum(line.product_uos_qty) as integer) as qty 

                FROM sale_order_line line 
		             left join sale_order so on (line.order_id = so.id)
		             left join product_product p on (line.product_id = p.id)
                     
                                                    
                     """ + condition  + """ group by p.name_template """)
        res = self.cr.dictfetchall()
        return res




    def _getdetails(self,ref):
           #data_product= data['form']['product_id']
           #where_condition = ""
           #where_condition += data_product and "f.product_id=%s"%data_product[0] or ""
           #where_condition += ref and " and r.id=%s"%ref or ""
           #date1 = data['form']['from_date'] 
           #date2 = data['form']['to_date'] 
           ref = ref[0]
           ref_typle = tuple(ref)
           self.cr.execute("""
                SELECT 
                  p.name_template as detail_name ,
				  l.product_uos_qty as qty 

                FROM sale_order so 
		            left join sale_order_line l on (l.order_id = so.id)
		            left join product_product p on (l.product_id = p.id)
                where so.id =%s order by p.name_template"""%ref_typle[0])
           res = self.cr.dictfetchall()

           return res







    #def make_copy(self,para):
        #return [{'no': 1,'text': 'ORIGINAL'},{'no': 2,'text': 'COPY',}]

    """def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('sale.order').browse(self.cr, self.uid, ids, self.context):
            if obj.state != 'done' :
		            raise osv.except_osv(_('Error!'), _('You can not print this order, This order not approved yet!')) 
            #if obj.payment_type == 'cash' :
                #if obj.invoice_ids[0].state == 'draft':
		            #raise osv.except_osv(_('Error!'), _('You can not print this order, first go and pay !'))
            if obj.print_order == True :
		            raise osv.except_osv(_('Error!'), _('You already printed this order ,,, check adminstrator!'))
            if obj.note == False :
                note=""
            else :
                note = obj.note
            u = self.pool.get('res.users').browse(self.cr, self.uid,self.uid).name
            notes = note +'\n'+'Sale order Printed at : '+time.strftime('%Y-%m-%d %H:%M:%S') + ' by '+ u
            self.pool.get('sale.order').write(self.cr, self.uid, ids, {'print_order':True,'note':notes})
        return super(order, self).set_context(objects, data, ids, report_type=report_type)
# generate the text of origin and copy



    def _show_discount(self, uid, context=None):
        cr = self.cr
        try: 
            group_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'group_discount_per_so_line')[1]
        except:
            return False
        return group_id in [x.id for x in self.pool.get('res.users').browse(cr, uid, uid, context=context).groups_id]"""

report_sxw.report_sxw('report.sale.order.custom', 'sale.order', 'addons/cooperative_sale/report/sale_order.rml', parser=order,header=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

