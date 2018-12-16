# -*- coding: utf-8 -*-

from openerp.osv import osv, fields , orm

class payment_receive_line(osv.osv_memory):
    _name = "payment.receive.line"

    _columns = {
      'payment_record_id' : fields.many2one('payment.record') ,
      'receive_id':fields.many2one('payment.receive'),
      'amount' : fields.related('payment_record_id'  , 'amount' , type='float' , string="Amount") ,
      'date' : fields.related('payment_record_id'  , 'date' , type='date' , string="Date") ,
      'state' : fields.related('payment_record_id'  , 'state' , type='char' , string="State") ,
    }

    def confirm(self, cr, uid, ids, context={}):
      obj = self.browse(cr , uid , ids)[0]
      return self.pool.get('payment.record').do_receive(cr , uid ,[obj.payment_record_id.id])

    def do_done(self, cr, uid, ids, context={}):
      obj = self.browse(cr , uid , ids)[0]
      return self.pool.get('payment.record').do_done(cr , uid ,[obj.payment_record_id.id])



class payment_receive(osv.osv_memory):
    _name = "payment.receive"

    _columns = {
      'employee_id':fields.many2one('hr.employee', 'Employee',  required=True,domain="[('state','=','approved')]"),
      'military_no': fields.char('Military Number',size=64),
      'emp_code': fields.char('Employee Code',size=64),
      'camp': fields.char('Camp Name',size=64), 
      'line_ids':fields.one2many('payment.receive.line' ,'receive_id'),
      'state' : fields.selection([('draft', 'Draft'), ('confirm', 'Confirm')]),
      'hand':fields.selection([('right', 'Right'),
                                   ('left', 'Left'),
                                   ], 'Select hand',  required=True,),
    'finger':fields.selection([('thumb', 'الإبهام'),
                                   ('Index', 'السبابة'),
                                   ('middle_finger', 'الوسطى'),
                                   ('ring_finger', 'البنصر'),
                                   ('Pinkie', 'الخنصر'),
                                   ], 'Select Finger',  required=True,),
    }

    _defaults = {
      'state' : 'draft'  ,
    }

    def on_change_employee(self , cr , uid , ids ,emp_id ,  context=None):
      self.reset(cr , uid , ids , context)
      if emp_id:
        emps = self.pool.get('hr.employee').read(cr , uid , [emp_id] , ['emp_code' , 'camp' , 'Military_ID'])
        emp = emps[0]
        return {
          'value' : {
            'emp_code' : emp['emp_code'] ,
            'camp' : emp['camp'] ,
            'military_no' : emp['Military_ID'] ,
          }
        }
      return {}


    def on_change_emp_code(self , cr , uid , ids ,emp_code ,  context=None):
      res = {'value' : {}}
      emp_id = self.pool.get('hr.employee').search(cr , uid , [('emp_code' , '=' , emp_code) , ('state' , '=' , 'approved')])
      print "######################### emp_id " , emp_id
      if len(emp_id) > 0:
        res['value']['employee_id'] = emp_id[0] 
      else :
        return {
          'value' : {
            'employee_id' : None ,
            'camp' : False ,
            'military_no' : False ,
          }
        }
      return res



    def on_change_military_no(self , cr , uid , ids ,military_no ,  context=None):
      res = {'value' : {}}
      emp_id = self.pool.get('hr.employee').search(cr , uid , [('Military_ID' , '=' , military_no)])
      if emp_id:
        res['value']['employee_id'] = emp_id[0] 
      else :
        return {}
      return res


    def get_payment_record(self , cr , uid , ids , context=None):
      res = {}
      obj = self.browse(cr , uid , ids)[0]
      pay_ids = self.pool.get('payment.record').search(cr , uid , 
        [('employee_id' , '=' , obj.employee_id.id ) , ('state' , '!=' , 'done')])
      lines = []
      for pay_id in pay_ids:
        line = (0,0,{'payment_record_id' : pay_id})
        lines.append(line)
      self.write(cr , uid , ids , {'line_ids' : lines})
      self.pool.get('payment.record').write(cr ,uid , pay_ids , {'hand' : obj.hand , 'finger_print' :obj.finger})
      return res




    def reset(self , cr , uid , ids , context):
      obj = self.browse(cr , uid , ids)
      if obj :
        obj = obj[0]
        line_obj = self.pool.get("payment.receive.line")
        line_ids = line_obj.search(cr , uid , [('receive_id' , '=' , obj.id)])
        line_obj.unlink(cr , uid , line_ids)
        self.write(cr, uid, ids, {'state': 'draft'})

    def confirm_rec(self, cr, uid, ids, context={}):
      self.reset(cr , uid , ids , context)
      self.get_payment_record(cr , uid , ids)
      pay_object = self.browse(cr ,uid , ids )[0]
      finger = str(pay_object.hand)+"_"+str(pay_object.finger)
      return {
            'type' : 'ir.actions.client',
            'tag' : 'payment_recieve',
            'params' : {
                'employee_id' : pay_object.employee_id.id ,
                'payment_receive_id' : pay_object.id ,
                'finger' : finger ,
                'state' : 'confirm' ,   
            },
        }