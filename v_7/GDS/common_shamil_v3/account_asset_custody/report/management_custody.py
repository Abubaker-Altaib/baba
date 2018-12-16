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
            'get_depts':self._get_depts,
            'get_data':self._get_data,
            'get_filters':self._get_filters,
            'get_pro':self._get_pro,
            'get_total':self._get_total,
             
 
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
 
        '''if  data['office_id']:
            office=data['office_id'][1]
            result.append({
           'office': office,
              })'''
  
 
        
 
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
                        c.custody_type = 'management' and c.state_rm = 'assigned'
                          ''')


        all_data=self.cr.dictfetchall() 
 
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
           print data['office_ids']
           all_data=[x for x in all_data if x['office_id'] in data['office_ids']]

         

 
        return all_data


    def _get_depts(self,data):
        all_data=self._get_data(data)
 
        result=[]
        depts=[]
        deptss=[]
        dept_obj = self.pool.get('hr.department') 

        for c in all_data:
            depts.append(c['dept_id'])
        for b in depts:
            if not b in deptss :
                deptss.append(b) 
 
        for dept_id in deptss:
           

            deps=dept_obj.search(self.cr, self.uid, [('id','=',dept_id)])
            for x in  dept_obj.browse(self.cr,self.uid,deps):
                c=x.id
                dept_name=dept_name2=dept_name3=""
                dept_name=x.name
                if x.parent_id:
                    dept_name2=x.parent_id.name 
                if x.parent_id.parent_id:
                    dept_name3=x.parent_id.parent_id.name or None
                self.cr.execute('SELECT count(d.id) AS count from account_asset_asset AS d where d.product_id is not Null and  d.department_id=%s'%(c))
                
                res=self.cr.dictfetchall()
                result.append({
                'name1': dept_name,
                'name2': dept_name2 or None,
                'name3': dept_name3 or None,
                'dept_id':dept_id,
                'count':res[0]['count'],
 
                'all_data': all_data,
 

             
                     })
 
        return result       

    def _get_offices(self,data,dept_id):
        all_data=self._get_data(data)
 
        result=[]
        offices=[]
        officess=[]
        office_obj = self.pool.get('office.office') 
        all_data=[x for x in all_data if x['dept_id'] == dept_id]
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
                'dept_id':dept_id,
                'all_data': all_data,

             
                     })
 
        return result

    def _get_pro(self,office_id,all_data,cat_id,dept_id):
        result=[]
        all_data=[x for x in all_data if x['office_id']== office_id]
        all_data=[x for x in all_data if x['dept_id'] == dept_id ] 
        type_obj = self.pool.get('product.category') 
        product_obj = self.pool.get('product.template')  
        if cat_id==0:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',30)])
        if cat_id==1:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',39)])
        if cat_id==2:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',39)])
        if cat_id==3:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',39)])
        if cat_id==4:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',39)])
        if cat_id==5:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',39)])
        if cat_id==6:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',39)])
        if cat_id==7:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',39)])
        if cat_id==8:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',39)])


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
            'name': product_name,
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
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',1)])
        if cat_id==1:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',2)])
        if cat_id==2:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',3)])
        if cat_id==3:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',1)])
        if cat_id==4:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',2)])
        if cat_id==5:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',3)])
        if cat_id==6:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',1)])
        if cat_id==7:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',2)])
        if cat_id==8:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',1)])
        if cat_id==9:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',1)])
        if cat_id==10:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',1)])
        if cat_id==11:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',1)])
        if cat_id==12:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',1)])
        if cat_id==13:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',1)])
        if cat_id==14:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',1)])
        if cat_id==15:
               cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',1)])
        all_data=[x for x in all_data if x['cat_id'] in cat_ids ] 
        total=len(all_data)

        result.append({
 
            'total': total,


                 
                })
 
        
        return result 
   

               
report_sxw.report_sxw('report.asset.custody.management', 'asset.custody', 'addons/account_asset_custody/report/management_custody.rml' ,parser=asset_custody_management_reports ,header='custom landscape')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:department,
