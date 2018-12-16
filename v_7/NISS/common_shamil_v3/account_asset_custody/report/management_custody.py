# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
import pooler
import copy
from report import report_sxw
import pdb
import re
from osv import fields, osv
from openerp.tools.translate import _

class asset_custody_management_reports(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(asset_custody_management_reports, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_office':self._get_offices,
            'get_data':self._get_data,
            'get_filters':self._get_filters,
            'get_pro':self._get_pro,
            'get_total':self._get_total,
            'get_name': self._get_name
             
 
        })


    def _get_filters(self,data):
        dep_obj = self.pool.get('hr.department') 
        pro_obj = self.pool.get('product.product') 
        office_obj = self.pool.get('office.office') 
        type_obj = self.pool.get('product.category')
        result=[]
        if  data['department_id']:
            department=data['department_id'][1]
 
            result.append({
 
            'department': department,
                 
                })
  
        if  data['product_id']:
            product=data['product_id'][1]
            result.append({
 
            'product': product,
                 
                })
  
        if  data['cat_id']:
            cat=data['cat_id'][1]
            result.append({ 
            'cat': cat,
                 
                })
 
        if  data['office_ids']:
            offices=data['office_ids']
            result.append({
           'offices': offices,
              })
  
 
        
 
        return result 
    def _get_data(self,data):

        all_data=[]
        self.cr.execute('''
                        SELECT c.request_date AS date ,c.executing_agency as agency ,p.name as product ,p.id as product_id \
                        ,pp.id as cat_id , pp.name as cat  ,
                        ppp.name as office ,ppp.id as office_id ,\
                        pppp.id as dept_id , pppp.name as dept
                        FROM account_asset_asset c 
                        LEFT JOIN product_template p ON (c.product_id=p.id)
                        LEFT JOIN product_category pp ON (p.categ_id=pp.id)
                        LEFT JOIN office_office ppp ON (c.office_id=ppp.id)
 
                        LEFT JOIN hr_department pppp ON (c.department_id=pppp.id)
                        where
                        c.custody_type = 'management' and c.asset_type = 'custody' ''')


        all_data=self.cr.dictfetchall() 

        if data['executing_agency']:
            all_data=[x for x in all_data if x['agency']==data['executing_agency']]
        
        type_obj = self.pool.get('product.category') 
        department_obj = self.pool.get('hr.department')                               
        # FILTERS 

        if data['product_id']:
           all_data=[x for x in all_data if x['product_id']==data['product_id'][0]]
        if data['cat_id']:
           cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',data['cat_id'][0])])
 
           all_data=[x for x in all_data if x['cat_id'] in cat_ids]
        if data['department_id']:
           department_ids =  department_obj.search(self.cr, self.uid, [('id', 'child_of',data['department_id'][0])])
 
           all_data=[x for x in all_data if x['dept_id'] in department_ids]
        if data['office_ids']:
           all_data=[x for x in all_data if x['office_id'] in data['office_ids']]

         

        return all_data

    def _get_offices(self,data):
        all_data=self._get_data(data)
 
        result=[]
        offices=[]
        officess=[]
        office_obj = self.pool.get('office.office') 

        for c in all_data:
            offices.append(c['office_id'])
        for b in offices:
            if not b in officess :
                officess.append(b) 
 
        for off_id in officess:
            offs=office_obj.search(self.cr, self.uid, [('id','=',off_id)])
            for x in  office_obj.browse(self.cr,self.uid,offs):
               office_name=x.name
 
 
               result.append({
                'name': office_name,
                'office_id':off_id,
                'all_data': all_data,

             
                     })
 
        return result
    def _get_pro(self,office_id,all_data,cat_id):
        result=[]
        if office_id:
            all_data=[x for x in all_data if x['office_id']== office_id]
        type_obj = self.pool.get('product.category') 
        product_obj = self.pool.get('product.product')  
        if cat_id==0:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[24])])
        if cat_id==1:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[33])])
        if cat_id==2:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[42])])
        if cat_id==3:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[37])])
        if cat_id==4:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[39])])
        if cat_id==5:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[46])])
        if cat_id==6:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[30])])
        if cat_id==7:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[73])])
        if cat_id==8:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[95])])


        pros=[]
        pross=[]
        all_data=[x for x in all_data if x['cat_id'] in cat_ids ] 
        for c in all_data:
           pros.append(c['product_id'])
        for b in pros:
           if not b in pross :
               pross.append(b) 
        for product_id in pross:
          total=0
          pos=product_obj.search(self.cr, self.uid, [('id','=',product_id)])
          for x in  product_obj.browse(self.cr,self.uid,pos):
            product_name=x.name
          qty=[x for x in all_data if x['product_id']== product_id ] 
          total=len(qty)

          result.append({
            'name': product_name.encode('utf-8'),
            'qty': total,


                 
                })
 
    
               
        all_data=[x for x in all_data if x['cat_id'] in cat_ids ] 
        
                                                       
 
        return result
       
    def _get_total(self,data,cat_id):
        type_obj = self.pool.get('product.category') 
        all_data=self._get_data(data)
        total=0
        result=[]
        if cat_id==0:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[24])])
        if cat_id==1:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[33])])
        if cat_id==2:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[42])])
        if cat_id==3:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[37])])
        if cat_id==4:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[39])])
        if cat_id==5:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[46])])
        if cat_id==6:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[30])])
        if cat_id==7:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[73])])
        if cat_id==8:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[95])])
        if cat_id==9:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[34])])
        if cat_id==10:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[35])])
        if cat_id==11:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[43])])
        if cat_id==12:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[44])])
        if cat_id==13:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[45])])
        if cat_id==14:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[74])])
        if cat_id==15:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',[75])])
        all_data=[x for x in all_data if x['cat_id'] in cat_ids ] 
        total=len(all_data)

        result.append({
 
            'total': total,


                 
                })
 
        
        return result 

    def _get_name(self, data):
        name = (data == 'tech' and 'فرع اﻹمداد الفني') or \
        (data == 'admin' and 'ادارة المهام') or \
        (data == 'arms' and 'ادارة السلاح') or ""
        return name
   

               
report_sxw.report_sxw('report.asset.custody.management', 'asset.custody', 'addons/account_asset_custody/report/management_custody.rml' ,parser=asset_custody_management_reports ,header='custom landscape')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:department,
