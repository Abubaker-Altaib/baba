#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from tools.translate import _
from datetime import timedelta,date
from osv import fields,osv

# Fuel plan report  
# Report to print Fuel plan in a specific month and year.

class fuel_plan_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.cr =cr
        self.uid = uid
        self.context = context
        super(fuel_plan_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line1':self._getdata1,
            'line3':self._getdata3,
            'line4':self._getdata5,
        })

    def _getdata(self,data):
        month= data['form']['month']
        year= data['form']['year']
        department = data['form']['department_id']
        department_obj = self.pool.get('hr.department')

        if department:
            department_id = department[0]
            department_ids = [department_id]
            department_ids.append(department_obj.search(self.cr,self.uid,[('id','child_of',department_id)]))
        
        fuel_plan         = self.pool.get('fuel.plan')
        fuel_quantity     = self.pool.get('fuel.quantity')
        fuel_qty_line     = self.pool.get('fuel.qty.line')
        fleet_vehicle     = self.pool.get('fleet.vehicle')
        hr_department     = department_obj
        hr_employee       = self.pool.get('hr.employee')
        resource_resource = self.pool.get('resource.resource')
        product_product   = self.pool.get('product.product')
        product_template  = self.pool.get('product.template')

        account = fuel_plan.search(self.cr, self.uid, [('type_plan','=','constant_fuel'),
            ('month','=',str(month)),('year','=',str(year)),])
        all_lines =[]
        lines = {}
        for plan in fuel_plan.browse(self.cr, self.uid,account, context=self.context):
            for quantity in fuel_quantity.browse(self.cr, self.uid,plan.quantity_ids, context=self.context):
                if department:
                        if not (quantity.id.department_id.id in department_ids):
                            continue

                lines["quantity"]      =  quantity.id.fuel_qty
                lines["plan_type"]     =  quantity.id.plan_type
                lines_ids=fuel_qty_line.search(self.cr, self.uid, [('qty_id','=',quantity.id.id)])
                
                for line in fuel_qty_line.browse(self.cr, self.uid,lines_ids, context=self.context):
                    #print("---------------------------line",line,line.product_id.fuel_type)
                    lines["product_qty"]        =  line.product_qty
                    lines["product_cost"]       =  line.price_unit   * line.product_qty
                    lines["spent_qty_cost"]     =  line.price_unit * line.spent_qty
                    lines["spent_qty"]          =  line.spent_qty
                    lines["vehicles_name"]      =  "/"
                    lines["vehicles_type"]      =  "/"
                    lines['department_name']    = line.department_id.name
                    if line.vehicles_id:
                        lines["vehicles_name"]      =  line.vehicles_id.name
                        lines["vehicles_type"]      =  line.vehicles_id.type
                    lines["fuel_type"]          =  line.product_id.fuel_type
                    lines["product_name"]       =  line.product_id.product_tmpl_id.name

                    lines["diesel_product_qty"]        =  0 
                    lines["diesel_product_cost"]       =  0 
                    lines["diesel_spent_qty_cost"]     =  0 
                    lines["diesel_spent_qty"]          =  0  
                    lines["diesel_product_name"]       =  "\\"
                    lines["diesel_fuel_type"]          =  u"ﺩﻳﺰﻝ"
                    lines["gasoline_product_qty"]        =  0 
                    lines["gasoline_product_cost"]       =  0 
                    lines["gasoline_spent_qty_cost"]     =  0 
                    lines["gasoline_spent_qty"]          =  0  
                    lines["gasoline_product_name"]       =  "\\"
                    lines["gasoline_fuel_type"]          =  u"ﺟﺎﺯﻭﻟﻴﻦ"


                    lines["electric_product_qty"]        =  0 
                    lines["electric_product_cost"]       =  0 
                    lines["electric_spent_qty_cost"]     =  0 
                    lines["electric_spent_qty"]          =  0  
                    lines["electric_product_name"]       =  "\\"
                    lines["electric_fuel_type"]          =  u"كهرباء"


                    lines["hybrid_product_qty"]        =  0 
                    lines["hybrid_product_cost"]       =  0 
                    lines["hybrid_spent_qty_cost"]     =  0 
                    lines["hybrid_spent_qty"]          =  0  
                    lines["hybrid_product_name"]       =  "\\"
                    lines["hybrid_fuel_type"]          =  u"هجين"

                    sum = self._getdata4(data,line.department_id.id)
                    for su in sum :
                        if su['fuel_type'] == u'gasoline':
                            lines["gasoline_product_qty"]        =  su['product_qty'] 
                            lines["gasoline_product_cost"]       =  su['product_cost'] 
                            lines["gasoline_spent_qty_cost"]     =  su['spent_qty_cost'] 
                            lines["gasoline_spent_qty"]          =  su['spent_qty']  
                            lines["gasoline_product_name"]       =  su['product_name'] 
                            lines["gasoline_fuel_type"]          =  u'ﺟﺎﺯﻭﻟﻴﻦ'

                        elif su['fuel_type'] == u'diesel':
                            lines["diesel_product_qty"]        =  su['product_qty'] 
                            lines["diesel_product_cost"]       =  su['product_cost'] 
                            lines["diesel_spent_qty_cost"]     =  su['spent_qty_cost'] 
                            lines["diesel_spent_qty"]          =  su['spent_qty']  
                            lines["diesel_product_name"]       =  su['product_name'] 
                            lines["diesel_fuel_type"]          =  u'ﺩﻳﺰﻝ'

                        elif su['fuel_type'] == u'electric':
                            lines["electric_product_qty"]        =  su['product_qty'] 
                            lines["electric_product_cost"]       =  su['product_cost'] 
                            lines["electric_spent_qty_cost"]     =  su['spent_qty_cost'] 
                            lines["electric_spent_qty"]          =  su['spent_qty']  
                            lines["electric_product_name"]       =  su['product_name'] 
                            lines["electric_fuel_type"]          =  u'كهرباء'

                        elif su['fuel_type'] == u'hybrid':
                            lines["hybrid_product_qty"]        =  su['product_qty'] 
                            lines["hybrid_product_cost"]       =  su['product_cost'] 
                            lines["hybrid_spent_qty_cost"]     =  su['spent_qty_cost'] 
                            lines["hybrid_spent_qty"]          =  su['spent_qty']  
                            lines["hybrid_product_name"]       =  su['product_name'] 
                            lines["hybrid_fuel_type"]          =  u'هجين'

                            

                all_lines.append(lines)
                lines ={}

        for i in all_lines:
            if i["plan_type"] == u'extra_fuel' :
              i["plan_type"] = u'ﺇﺿﺎﻓﻲ'

            if i["plan_type"] == u'fixed_fuel' :
              i["plan_type"] = u'ﺛﺎﺑﺖ'

            #print("----------------------i[vehicles_type]",i["vehicles_type"])
            if i["vehicles_type"] == u'truck':
              i["vehicles_type"] = u'ﺷﺎﺣﻨﺔ'

            if i["vehicles_type"] == u'bus':
              i["vehicles_type"] = u'ﺑﺎﺹ'

            if i["vehicles_type"] == u'car':
              i["vehicles_type"] = u'ﺳﻴﺎﺭﺓ'

            if i["vehicles_type"] == u'generator' :
              i["vehicles_type"] = u'ﻣﻮﻟﺪ'

            if i["fuel_type"] == u'gasoline':
              i["fuel_type"] = u'ﺟﺎﺯﻭﻟﻴﻦ'

            if i["fuel_type"] == u'diesel' :
              i["fuel_type"] = u'ﺩﻳﺰﻝ'
              



        new_all_lines = []
        new_line=[]
        exist=[]
        for line in all_lines:
            if not line['department_name'] in exist:
                exist.append(line['department_name'])
                for m in all_lines:
                    if m['department_name'] == line['department_name']:
                        new_line.append(m)
                new_all_lines.append(new_line)
                new_line=[]

        return new_all_lines


        ########################################################################################

    def _getdata4(self,data,department=None):
            month= data['form']['month']
            year= data['form']['year']
            department_obj = self.pool.get('hr.department')
            

            fuel_plan         = self.pool.get('fuel.plan')
            fuel_quantity     = self.pool.get('fuel.quantity')
            fuel_qty_line     = self.pool.get('fuel.qty.line')
            fleet_vehicle     = self.pool.get('fleet.vehicle')
            hr_department     = self.pool.get('hr.department')
            hr_employee       = self.pool.get('hr.employee')
            resource_resource = self.pool.get('resource.resource')
            product_product   = self.pool.get('product.product')
            product_template  = self.pool.get('product.template')

            account = fuel_plan.search(self.cr, self.uid, [('type_plan','=','constant_fuel'),
                ('month','=',str(month)),('year','=',str(year)),])
            all_lines =[]
            lines = {}
            for plan in fuel_plan.browse(self.cr, self.uid,account, context=self.context):
                for quantity in fuel_quantity.browse(self.cr, self.uid,plan. quantity_ids, context=self.context):
                    #if department:
                    if not quantity.id.department_id.id == department:
                        continue
                    lines_ids=fuel_qty_line.search(self.cr, self.uid, [('qty_id','=',quantity.id.id)])
                    
                    for line in fuel_qty_line.browse(self.cr, self.uid,lines_ids, context=self.context):
                        lines["product_qty"]        =  line.product_qty
                        lines["product_cost"]       =  line.price_unit   * line.product_qty
                        lines["spent_qty_cost"]     =  line.price_unit * line.spent_qty
                        lines["spent_qty"]          =  line.spent_qty
                        lines["product_name"]       =  line.product_id.product_tmpl_id.name
                        lines["fuel_type"]          =  line.product_id.fuel_type
                        all_lines.append(lines)
                        lines ={}
            

            new_all_lines =[]
            new_lines = {}
            conunted = []
            for i in all_lines:
                new_lines['product_qty']    = 0
                new_lines['product_cost']   = 0
                new_lines['spent_qty_cost'] = 0
                new_lines['spent_qty']      = 0
                if not(i["fuel_type"] in conunted):
                    conunted.append(i["fuel_type"])

                    for m in all_lines:
                        if m["fuel_type"] != i["fuel_type"] :
                            continue
                        new_lines['product_qty']    += m['product_qty']
                        new_lines['product_cost']   += m['product_cost']
                        new_lines['spent_qty_cost'] += m['spent_qty_cost']
                        new_lines['spent_qty']      += m['spent_qty']
                        new_lines['product_name']    = m['product_name']
                        new_lines['fuel_type']       = m['fuel_type']

                    new_all_lines.append(new_lines)
                    new_lines={}


            return new_all_lines

        #############################################################################################


    def _getdata5(self,data):
            month= data['form']['month']
            year= data['form']['year']
            department = data['form']['department_id']
            if department:
                return []
            

            department_obj = self.pool.get('hr.department')
            

            fuel_plan         = self.pool.get('fuel.plan')
            fuel_quantity     = self.pool.get('fuel.quantity')
            fuel_qty_line     = self.pool.get('fuel.qty.line')
            fleet_vehicle     = self.pool.get('fleet.vehicle')
            hr_department     = self.pool.get('hr.department')
            hr_employee       = self.pool.get('hr.employee')
            resource_resource = self.pool.get('resource.resource')
            product_product   = self.pool.get('product.product')
            product_template  = self.pool.get('product.template')

            account = fuel_plan.search(self.cr, self.uid, [('type_plan','=','constant_fuel'),
                ('month','=',str(month)),('year','=',str(year)),])
            all_lines =[]
            lines = {}
            for plan in fuel_plan.browse(self.cr, self.uid,account, context=self.context):
                for quantity in fuel_quantity.browse(self.cr, self.uid,plan. quantity_ids, context=self.context):
                    
                    lines_ids=fuel_qty_line.search(self.cr, self.uid, [('qty_id','=',quantity.id.id)])
                    
                    for line in fuel_qty_line.browse(self.cr, self.uid,lines_ids, context=self.context):
                        lines["product_qty"]        =  line.product_qty
                        lines["product_cost"]       =  line.price_unit   * line.product_qty
                        lines["spent_qty_cost"]     =  line.price_unit * line.spent_qty
                        lines["spent_qty"]          =  line.spent_qty
                        lines["product_name"]       =  line.product_id.product_tmpl_id.name
                        lines["fuel_type"]          =  line.product_id.fuel_type
                        all_lines.append(lines)
                        lines ={}
            

            new_all_lines =[]
            new_lines = {}
            conunted = []
            for i in all_lines:
                new_lines['product_qty']    = 0
                new_lines['product_cost']   = 0
                new_lines['spent_qty_cost'] = 0
                new_lines['spent_qty']      = 0
                if not(i["fuel_type"] in conunted):
                    conunted.append(i["fuel_type"])

                    for m in all_lines:
                        if m["fuel_type"] != i["fuel_type"] :
                            continue
                        new_lines['product_qty']    += m['product_qty']
                        new_lines['product_cost']   += m['product_cost']
                        new_lines['spent_qty_cost'] += m['spent_qty_cost']
                        new_lines['spent_qty']      += m['spent_qty']
                        new_lines['product_name']    = m['product_name']
                        new_lines['fuel_type']       = m['fuel_type']

                    new_all_lines.append(new_lines)
                    new_lines={}


            return new_all_lines

        #############################################################################################




    def _getdata1(self,data):
        month= data['form']['month']
        year= data['form']['year']
        res = {}
        res["month"] = month
        res["year"] = year
        return [res]
                       

    def _getdata3(self,data):
        """This function return the department name """
        department    = data['form']['department_id']
        department_id = department and department[0] or 0
        hr_department = self.pool.get('hr.department')
        h = hr_department.browse(self.cr,self.uid,[department_id],context=self.context)
        res={}
        res["department_name"] = "اﻟﻜﻞ"
        try:
            if len(h) == 1:
                res["department_name"]=h[0].name
        except Exception:
            res["department_name"] = "اﻟﻜﻞ"

        return [res]

report_sxw.report_sxw('report.fix_fule_plan.report', 'fuel.plan', 'addons/fuel_management/report/fuel_plan_report.rml' ,parser=fuel_plan_report,header=False)