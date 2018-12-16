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

class asset_custody_detail_reports(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(asset_custody_detail_reports, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_data':self._get_data,
            'get_office':self._get_office,
            
        })
# GET OFFICES LIST (USE TO FILTTER CUSTODIES BY OFFICE)

    def _get_office(self,data):
        department_obj = self.pool.get('hr.department') 
        office_obj = self.pool.get('office.office')
        asset_obj = self.pool.get('account.asset.asset')
        department_id= data['form']['department_id'][0]
        executing_agency= data['form']['executing_agency']
        department_ids =  department_obj.search(self.cr, self.uid, [('id', 'child_of', department_id)])
        office_ids=[]
        unique=[]      
        res=[]     

        if data['form']['office_ids']:
 
            office_idss=data['form']['office_ids']
            asset_ids = asset_obj.search(self.cr, self.uid, [('office_id','in',office_idss),('department_id','in',department_ids)]) 
            for asset in asset_obj.browse(self.cr,self.uid, asset_ids):
                if asset.office_id and asset.office_id not in office_ids :
                    office_ids.append(asset.office_id.id)
        else:
 
            asset_ids = asset_obj.search(self.cr, self.uid, [('department_id','in',department_ids)]) 
            for asset in asset_obj.browse(self.cr,self.uid, asset_ids):
                if asset.office_id and asset.office_id not in office_ids :
                    office_ids.append(asset.office_id.id)
        # return uniques
        for f_id in office_ids:
            asset_ids = asset_obj.search(self.cr, self.uid, [('department_id','in',department_ids),('office_id','=',f_id)]) 
            if asset_ids and  f_id not in unique:
                unique.append(f_id) 

        for office in office_obj.browse(self.cr,self.uid, unique):            
            res.append({'off_id':office.id,'name':office.name})
        return res

# FUNCTION TO GET DATA PASSSED TO THE REPORT 

    def _get_data(self,data,off_id):

        """ Finds the  custodies quantity by department and executing agency
        """
        office_id=off_id
 
        department_id= data['form']['department_id']
        executing_agency= data['form']['executing_agency']
        self.cr.execute("""
                select
                    min(off.name) as office,
                    min(mod.name) as model,
                    min(typ.name) as main_type ,
                    min(cus.executing_agency) as executing_agency,
                    min(emp.name_related) as emp,
                    min(cus.custody_type) as custody_type,
                    min(cus.name) as ref,
                    min(cus.request_date) as date                    
                    from account_asset_asset cus 
                    left join office_office off on (cus.office_id=off.id)
                    left join product_template mod on (cus.product_id=mod.id)
                    left join product_product modd on (cus.product_id=modd.id)
                    left join product_category typ on (cus.main_type=typ.id)
                    left join hr_employee emp on (cus.employee_id=emp.id)
                where  
                    (cus.department_id = %s) and (cus.executing_agency = %s) and (cus.office_id=%s ) and(cus.custody_type='management') and (modd.asset='True')  
                group by 
                     cus.id
                order by
                     date
                
               """,(department_id[0],executing_agency ,office_id))
        res = self.cr.dictfetchall()
 
        return res
   

               
report_sxw.report_sxw('report.asset.custody.detail', 'asset.custody', 'addons/account_asset_custody/report/detail_custody.rml' ,parser=asset_custody_detail_reports ,header='custom landscape')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
