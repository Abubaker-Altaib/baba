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

class asset_custody_sum_reports(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(asset_custody_sum_reports, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_depts':self._get_depts,
            'get_office':self._get_office,
            'get_type':self._get_type,
            'get_type2':self._get_type2,
            'get_model':self._get_model,
        })

# GET EXECUTING AGENCY  

    def _get_agency(self,data):

        executing_agency= data['form']['executing_agency']
        


# GET DEPARTMENTS LIST 
    def _get_depts(self,data):
        result=[]
        department_ids= data['form']['department_ids']
        for dept in self.pool.get('hr.department').browse(self.cr,self.uid, department_ids):
             result.append({
                        'name': dept.name,
                        'dept_id': dept.id,
 
                         
                    })
        
         
        return result
 
    def _get_office(self,data,dept_id):

        result=[]
        department_id=dept_id
        executing_agency= data['form']['executing_agency']
 
        type_obj = self.pool.get('product.category')
        product_obj = self.pool.get('product.product')
        asset_obj=self.pool.get('account.asset.asset')
        office_obj = self.pool.get('office.office')
        office_ids =  office_obj.search(self.cr, self.uid, self.ids)
        
        if data['form']['office_ids']:
            office_ids=data['form']['office_ids']
        
 
        for office in office_obj.browse(self.cr,self.uid, office_ids):
            office_name=office.name
            office_id=office.id
            asset_ids=[]
            prod_ids=[]
            type_ids=[]

            asset_ids=  asset_obj.search(self.cr, self.uid, [('custody_type','=','management'),('office_id','=',office_id),('department_id','=',department_id)])
            if data['form']['cat_ids']:
                cat_ids=data['form']['cat_ids']
                type_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of', cat_ids)])
                prod_ids =  product_obj.search(self.cr, self.uid, [('categ_id','in',type_ids),('asset','=','True')])
                asset_ids =  asset_obj.search(self.cr, self.uid, [('id','in',asset_ids),('product_id','in',prod_ids)])
 
            if data['form']['product_ids']:
                product_ids=data['form']['product_ids']
                asset_ids =  asset_obj.search(self.cr, self.uid, [('id','in',asset_ids),('product_id','in',product_ids)])

            total_by_office=0
            for x in  asset_ids:
                total_by_office+=1
            result.append({
                        'total': total_by_office,
                        'name': office_name,
                        'off_id': office_id,
                        'dept_id':  dept_id,

                         
                    })
 
 
        return result    

    def _get_type2(self,data,off_id,dept_id):


        # used to return category name 
        # Computer totol of custodies by office and category
        # Used to eliminate catogries with no custioes moves in certain office

 
        executing_agency= data['form']['executing_agency']
 
        type_obj = self.pool.get('product.category')
        product_obj = self.pool.get('product.product')
        asset_obj=self.pool.get('account.asset.asset')
        result=[]
        office_id= off_id
        department_id= dept_id
        g_type_ids =  type_obj.search(self.cr, self.uid, [('executing_agency','=',executing_agency),('custody','=','True')])
  
        
        if data['form']['cat_ids']:
            cat_ids=data['form']['cat_ids'] 
            g_type_ids =  type_obj.search(self.cr, self.uid,[('id','in',cat_ids),('executing_agency','=',executing_agency),('custody','=','True')])

         

        category =  type_obj.browse(self.cr,self.uid, g_type_ids)
        for category in category:
            type_id=category.id
            type_ids=[]
            type_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of', type_id)])
            prod_ids =  product_obj.search(self.cr, self.uid, [('categ_id','in',type_ids),('asset','=','True')])
 
            total_by_type=0
            cus_ids =   asset_obj.search(self.cr, self.uid, [('product_id','in',prod_ids),('custody_type','=','management'),('office_id','=',office_id),('department_id','=',department_id)])
            if data['form']['product_ids']:
                product_id=data['form']['product_ids']
                cus_ids =  asset_obj.search(self.cr, self.uid, [('product_id','in',product_ids),('custody_type','=','management'),('office_id','=',office_id),('department_id','=',department_id)])
            for x in cus_ids:
                total_by_type+=1
            result.append({
                        'total': total_by_type,
                        'name': category.name,
                        't_id': type_id,
                        'dept_id': department_id,
                        'off_id': office_id,
 
                         
                    })
   

        return result
 
    def _get_type(self,data):

        executing_agency= data['form']['executing_agency']
        department_ids= data['form']['department_ids']
 
        asset_obj=self.pool.get('account.asset.asset')
        type_obj = self.pool.get('product.category')
        product_obj = self.pool.get('product.product')
        result=[]
        type_ids=[]

 
        type_ids =  type_obj.search(self.cr, self.uid, [('executing_agency','=',executing_agency),('custody','=','True')])
        
        if data['form']['cat_ids']:
            cat_ids=data['form']['cat_ids'] 
            type_ids =  type_obj.search(self.cr, self.uid,[('id','in',cat_ids)])

        if data['form']['product_ids']:
                product_ids=data['form']['product_ids'] 
 
 
                type_ids=[x.id in x for x in product_obj.browse(self.cr,self.uid, product_ids).categ_id ]
 

        for t_id in type_ids:
 
            ttype_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of', t_id)])
            product_ids= product_obj.search(self.cr, self.uid, [('categ_id','in',ttype_ids),('asset','=','True')])
 
            cus_ids =  asset_obj.search(self.cr, self.uid, [('department_id','in',department_ids),('custody_type','=','management'),('product_id','in',product_ids)])
             
            quantity_total=0                            # number of custody lines by category and department
            for x in cus_ids:
               quantity_total+=1
           
            new_type_ids =  type_obj.search(self.cr, self.uid, [('id','=',t_id)])
            category =  type_obj.browse(self.cr,self.uid, new_type_ids)
 
            for category in category:
                name= category.name

            result.append({
                        'type_name': category.name,
                        'total': quantity_total,
                         
                    })
 
        return result

    def _get_model(self,data,ty_id,off_id,dept_id):
        executing_agency= data['form']['executing_agency']
        type_obj = self.pool.get('product.category')
        product_obj = self.pool.get('product.product')
        department_id=dept_id
        type_id= ty_id
        office_id= off_id
        result=[]
        type_ids=[]
        type_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of', type_id)])
        asset_obj=self.pool.get('account.asset.asset')
        prod_ids =  product_obj.search(self.cr, self.uid, [('categ_id','in',type_ids),('asset','=','True')])
        if data['form']['product_ids']:
                product_ids=data['form']['product_ids'] 
                prod_ids =  product_obj.search(self.cr, self.uid, [('id','in',product_ids),('asset','=','True')])
        
        product =  product_obj.browse(self.cr,self.uid, prod_ids)
        for product in product:
            p_id=product.id
            cus_ids =  asset_obj.search(self.cr, self.uid, [('product_id','=',p_id),('custody_type','=','management'),('office_id','=',office_id),('department_id','=',department_id),])
            pro_total=0          # number of custody lines by category and office
 
            for x in cus_ids:
               pro_total+=1
            result.append({
                        'name': product.name,
                        'pro_total':pro_total,
                         
                    })
        
         
        return result


               
report_sxw.report_sxw('report.asset.custody.sum', 'asset.custody', 'addons/account_asset_custody/report/asset_custody.rml' ,parser=asset_custody_sum_reports ,header='custom landscape')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
