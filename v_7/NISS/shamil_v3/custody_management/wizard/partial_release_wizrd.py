# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
import time
from openerp.tools.translate import _
from openerp import netsvc



class create_custody_release_request(osv.osv_memory):
    """ 
    Class to Create Custody Release Request From wizard """

    _description='Create Custody Release Request'
    _name = 'create.custody.release.request'
    _columns = {
                'department_id' : fields.many2one('hr.department','Department',required=True ),
                'release_date': fields.date('Release Date', readonly=True),
                'custody_ids':fields.one2many('custody.lines', 'wizard_id' , 'Items'),                
                }
    
    _defaults = {
                'release_date': lambda *a: time.strftime('%Y-%m-%d'),
                }

    def change_department(self, cr, uid, ids ,department_id , context=None):
        """ 
        To get default values for the object.

        @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        res ={}
        result = []
        department_obj = self.pool.get('hr.department')
        department_condition = ""
        department_ids = department_obj.search(cr,uid,[('id','child_of',department_id)])
        if len(department_ids) == 1:
                department_condition = " and cust.department_id in (%s)"%department_ids[0]
        else:
                department_ids = tuple(department_ids)
                department_condition = " and cust.department_id in %s"%str(department_ids)
        cr.execute("""select distinct cust.serial as serial , 
                              cust.department_id as department , 
                              cust.current_user as employee_id ,  
                              cust.id as cust_id 
                            from  custody_custody cust
                            left join  asset_logs alog  on (cust.id = alog.custody_log_id)
                            left join hr_employee emp on (emp.id = cust.current_user)
                            left join hr_department dept on (dept.id = cust.department_id)
                            where cust.in_stock=%s
                                """ + department_condition  + "order by cust.current_user desc ", (False,))
        
        res = cr.dictfetchall()

        for record in res :
            result.append({ 'custody_id' : record['cust_id'],
                            'name' : record['serial'],
                            'employee_id' : record['employee_id'] or False , 
        
                            'return_this' : False , })
        return {'value': { 'custody_ids': result }}

    

    def create_release_order(self, cr, uid, ids, context=None):
        """
        Button function to create release order for custody
 
        @return: Purchase Requestion Id
        """        
        release_obj = self.pool.get('custody.release.order')
        release_lines_obj = self.pool.get('custody.release.lines')
        wf_service = netsvc.LocalService("workflow") 
        wizard = self.browse(cr,uid,ids)
        check = False
        for obj in self.browse(cr,uid,ids):
             
            if not obj.custody_ids :
                  raise  osv.except_osv(_('Erorr'), _('This Department havent Custody Now...') )
            else :
               for line in obj.custody_ids: 
                   if not line.custody_id : 
                      raise  osv.except_osv(_('Erorr'), _('This Department havent Custody Now...') )
                   if line.return_this :
                      check = True
               if check == False :
                  raise  osv.except_osv(_('Erorr'), _('You Must Be Check The Custody(s) that you want to returned ') )   
            
               for record in self.browse(cr,uid,ids) :
                   order_id = release_obj.create(cr, uid, {
                                                                  'department_id' : record.department_id.id, 
                                                                   })
               for record_lines in record.custody_ids:
                   if record_lines.return_this :
                      release_lines_obj.create(cr, uid, {   'release_order_id': order_id,
                                                                  
                                                                  'custody_id': record_lines.custody_id.id,
                                                                  'name' : record_lines.name ,
                                                                  'employee_id': record_lines.employee_id.id, 
                                                                  'release_date': record.release_date,})

               wf_service.trg_validate(uid, 'custody.release.order', order_id, 'draft_confirm', cr)
        
              

              
        return order_id
       

class custody_lines(osv.osv_memory):
    """
    """

    _description="Loading Custody From Assets Log"
    _name = "custody.lines"
    _columns = {
        'name' : fields.char('Serial Code' , size=32 ,readonly=True),
        'custody_id' : fields.many2one('custody.custody', "Custody" , readonly=True),
        'employee_id' :  fields.many2one('hr.employee' , "Employee" , readonly=True ), 
        'wizard_id' : fields.many2one('create.custody.release.request', string="Wizard"),
        'return_this' : fields.boolean('Return This'),
        } 
    _order = "employee_id desc,name desc"
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
