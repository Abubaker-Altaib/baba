# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.osv import fields, osv
from report import report_sxw
from datetime import datetime,timedelta

class hospitality_service(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(hospitality_service, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'copy_version':self.creat_copy,
            'main_data':self.main_data,
        })

        self.cr = cr
        self.uid = uid
        self.context = context
    def set_context(self, objects, data, id, report_type=None):
        for obj in self.pool.get('hospitality.service').browse(self.cr, self.uid, id,self.context):
           globals()['h_day']=obj.no_day
           globals()['h_id']=obj.id
        return super(hospitality_service, self).set_context(objects, data, id, report_type=report_type)
    
    def creat_copy(self):        
        copy=0
        res=[]    
        self.cr.execute("""SELECT 
  hos.company_id as company, 
  hos.date_of_execution as date_of_execution, 
  dep.name as department_id, 
  part.name as partner_id, 
  hos.name as name,
  orderr.service_qty as service_qty,
  ser_tpe.name as service_type
  FROM 
  public.hospitality_service as hos,
  res_partner as part,
  order_lines as orderr,
  hospitality_service_type as ser_tpe,
  hr_department as dep

 where
 hos.partner_id=part.id and   hos.id = orderr.order_id and ser_tpe.id=orderr.service_type
 and hos.department_id=dep.id and hos.id=%s """%globals()['h_id'] )
        result=self.cr.dictfetchall()
        ex_date=result[0]['date_of_execution']
        while copy < globals()['h_day'] :
             res.append({
                    'hosplity_no':1 ,
                    'date_of_execution':datetime.strptime(ex_date,"%Y-%m-%d")+timedelta(days=copy),
                    'department_id':result[0]['department_id'] ,
                    'partner_id':result[0]['partner_id'] ,
                    'name':result[0]['name'] ,
                    })
             copy+=1
        return res
    def main_data(self):
        listt=[]
        self.cr.execute("""SELECT 
  orderr.service_qty as service_qty,
  ser_tpe.name as service_type
  FROM 
  public.hospitality_service as hos,
  res_partner as part,
  order_lines as orderr,
  hospitality_service_type as ser_tpe,
  hr_department as dep

 where
 hos.partner_id=part.id and   hos.id = orderr.order_id and ser_tpe.id=orderr.service_type
 and hos.department_id=dep.id and hos.id=%s"""%globals()['h_id'] )
        result=self.cr.dictfetchall()
        for x in result:
            dic={'service_qty':x['service_qty'],'service_type':x['service_type']}
            listt.append(dic)
        print "MMMMMM",listt
        return listt
report_sxw.report_sxw('report.hospitality.request.report','hospitality.service','addons/services/report/hospitality_request.rml',parser=hospitality_service, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
