
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
                'department_id' : fields.many2one('hr.department','Department'),
                'operation_date': fields.date('Operation Date'),
                'operation_type' : fields.selection([('release','Release'),('replace','Replace')] , 'Operation Type'),
                'rel_custody_ids':fields.one2many('rel.custody.lines', 'wizard_id' , 'Items'),    
                'rep_custody_ids':fields.one2many('rep.custody.lines', 'wizard_id' , 'Items'),                            
                }
    
    _defaults = {
           
                'operation_type' : 'release' ,
                'operation_date': lambda *a: time.strftime('%Y-%m-%d'),
 
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
        operation_type = ""
        department_obj = self.pool.get('hr.department')
        department_condition = ""
        
        department_ids = department_obj.search(cr,uid,[('id','child_of',department_id)])
        if len(department_ids) == 1:
                department_condition = " and cust.department_id in (%s)"%department_ids[0]
        else:
                department_ids = tuple(department_ids)
                department_condition = " and cust.department_id in %s"%str(department_ids)
        cr.execute("""select distinct cust.code as serial , 
                              cust.department_id as department , 
                              cust.current_employee as employee_id ,  
                              cust.id as cust_id 
                            from  account_asset_asset cust
                            left join  asset_logs alog  on (cust.id = alog.custody_log_id)
                            left join hr_employee emp on (emp.id = cust.current_employee)
                            left join hr_department dept on (dept.id = cust.department_id)
                            where cust.state='open'
                                """ + department_condition  + "order by cust.current_employee desc ",)
        
        res = cr.dictfetchall()
        #values = {}
        #wizard_id = self.pool['create.custody.release.request'].create(cr, uid, values)
        for record in res :
            result.append({ 'custody_id' : record['cust_id'],
                            'name' : record['serial'],
                            'employee_id' : record['employee_id'] or False , 
                            'operation_type' : operation_type,
                            'return_this' : False , })
        return {'value': { 'rel_custody_ids': result , 'rep_custody_ids' : result }}


    




    def create_release_order(self, cr, uid, ids, context=None):
        """
        Button function to create release order for custody
 
        @return: release Request Id
        """        
        release_obj = self.pool.get('custody.release.order')
        release_lines_obj = self.pool.get('custody.release.lines')
        wf_service = netsvc.LocalService("workflow") 
        wizard = self.browse(cr,uid,ids)
        check = False
        for obj in self.browse(cr,uid,ids):
             
            if not obj.rel_custody_ids :
                  raise  osv.except_osv(_('Erorr'), _('This Department havent Custody Now...') )
            else :
               for line in obj.rel_custody_ids: 
                   if not line.custody_id : 
                      raise  osv.except_osv(_('Erorr'), _('This Department havent Custody Now...') )
                   if line.return_this :
                      check = True
               if check == False :
                  raise  osv.except_osv(_('Erorr'), _('You Must Be Check The Custody(s) that you want to returned ') )   
            

               order_id = release_obj.create(cr, uid, {
                                                                  'department_id' : obj.department_id.id, 
                                                                   })
               for record_lines in obj.rel_custody_ids:
                   if record_lines.return_this :
                      release_lines_obj.create(cr, uid, {   'release_order_id': order_id,
                                                            'custody_id': record_lines.custody_id.id,
                                                            'name' : record_lines.name ,
                                                            'employee_id': record_lines.employee_id.id, 
                                                            'release_date': obj.operation_date,})

               wf_service.trg_validate(uid, 'custody.release.order', order_id, 'draft_confirm', cr)
        
              

              
        return order_id
       
    def custody_assign(self, cr, uid, ids, context=None):
        custody_obj = self.pool.get('account.asset.asset')
        asset_log_obj = self.pool.get('asset.logs')
        for rec in self.browse(cr,uid,ids):
            if not rec.rep_custody_ids :
	       raise  osv.except_osv(_('Bad Action'), _('Make Sure You filled the items corretly...') )
	    else :
	       for line in rec.rep_custody_ids: 
		   if not line.new_employee_id :
                      
		      raise  osv.except_osv(_('Erorr'), _('Please Add The New Employee whom will get this product or delete the item ...') )
                   custody_id = custody_obj.search(cr,uid,[('id' , '=' , line.custody_id.id )])
                   res = {

                                                         'state' : 'open' ,
                                                         'department_id' :  rec.department_id.id , 
                                                         'current_employee' :  line.new_employee_id.id  ,
                                                         'period_type' : False,
                                                         'expacted_return_date' : False, }

                   custody_obj.write(cr,uid, custody_id,res, context=context) 
                   lines_res = {
					      'custody_log_id' : custody_id[0] ,
					      'department_id' : rec.department_id.id,
					      'action_type' : 'reassign' ,
                                              'action_date' : rec.operation_date ,
					      'employee_id' : line.new_employee_id.id,
						 }
                  
                   asset_log_obj.create(cr,uid,lines_res)
        return True









class rel_custody_lines(osv.osv_memory):
    """
    """






    

    _description="Loading Custody From Assets Log"
    _name = "rel.custody.lines"
    _columns = {
        'name' : fields.char('Serial Code' , size=256 ,readonly=True),
        'custody_id' : fields.many2one('account.asset.asset', "Custody" ,),
        'employee_id' :  fields.many2one('hr.employee' , "Employee" ,), 
        'wizard_id' : fields.many2one('create.custody.release.request', string="Wizard"),
        'return_this' : fields.boolean('Return This'),
        } 

    _order = "employee_id desc,name desc"

    

class rep_custody_lines(osv.osv_memory):
    """
    """






    

    _description="Loading Custody From Assets Log"
    _name = "rep.custody.lines"
    _columns = {
        'name' : fields.char('Serial Code' , size=256 ,readonly=True),
        'custody_id' : fields.many2one('account.asset.asset', "Custody" ,),
        'employee_id' :  fields.many2one('hr.employee' , "Employee" ,), 
        'new_employee_id' :  fields.many2one('hr.employee' , "New Employee" ,),
        'wizard_id' : fields.many2one('create.custody.release.request', string="Wizard"),
        } 

    _order = "employee_id desc,name desc"

    



    
        







