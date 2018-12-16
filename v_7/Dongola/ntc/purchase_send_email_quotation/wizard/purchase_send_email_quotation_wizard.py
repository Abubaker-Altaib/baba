# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
############################################################################

import time
from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
from openerp.osv.orm import browse_record, browse_null
from openerp.tools.translate import _
import smtplib
from osv import osv, fields
#from django.utils.encoding import smart_str
#content = smart_str(content)




class purchase_send_email_quotation_wizard(osv.osv_memory):
    
    
        
        
        
        
        
        
        
    def send_message(self, cr , uid ,ids, context=None):
        """ This Method for send Email For Suppliers """
        requesition_obj =  self.pool.get('purchase.requisition')
        requesition = requesition_obj.browse(cr, uid, context['request_id'] )
        subject = 'RFQ For ' + requesition.name
        ir_mail = self.pool.get('ir.mail_server')
        partner_obj = self.pool.get('res.partner')

        
        
        partner_ids = requesition_obj.get_partner_ids(cr, uid, ids, requesition, context=context)
        
        if context['server_mail_id'] :

          try :
           mail_rec = ir_mail.browse(cr,uid,context['server_mail_id'])
           user_name = str(mail_rec.smtp_user)
           password = mail_rec.smtp_pass
           smtp_host = str(mail_rec.smtp_host)
           smtp_port = mail_rec.smtp_port

           smtpObj = smtplib.SMTP(host=str(smtp_host),port=25)
           smtpObj.set_debuglevel(1)
           smtpObj.ehlo()
           smtpObj.starttls()                                
           smtpObj.login(user=user_name, password=password)
           for partner in partner_obj.browse(cr,uid,partner_ids):
               if partner.email :
                   Text = "Dear " + partner.name + """ ,,, \n
                            This Message From """ + requesition.company_id.name + """\n""" + context['message']
    
                   message = 'Subject: %s\n\n%s' % (subject, Text)                        
                         
                   smtpObj.sendmail(user_name, partner.email ,  message) 



          except ValueError:
                  print("Oops!  That Problem in Username Or Password .Recheck the Outgoing Mail Configration ...")
        return True
    
    
    def default_get(self, cr, uid, fields, context=None):
        """ 
        To get default values for the object.

        @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}

        req_obj = self.pool.get('purchase.requisition')
        users = self.pool.get('res.users')
        res ={}
        req_id = context.get('active_ids', [])
        
        req_rec = req_obj.browse(cr, uid, req_id, context=context)[0]
        users.browse(cr,uid,uid).id
        res.update({ 'company_id': req_rec.company_id.id,
                      'request_id' : req_rec.id  ,
                      'user_id' :    users.browse(cr,uid,uid).id  })
        
        return res   





    _columns = {

     'request_id' : fields.many2one('purchase.requisition' , 'Request' , required=True ,readonly=True ),
     'server_mail_id' :  fields.many2one('ir.mail_server' , 'Mail Server' , required=True ),
     'company_id' : fields.many2one('res.company','Company' ,readonly=True),
     'user_id' : fields.many2one('res.users' , 'User' , required=True ,readonly=True ),
     'message': fields.text('Notes', size=512 , required=True),


                }




    



    _name = "purchase.send.email.quotation.wizard"
    _description = "Purchase Send Email Quotation Wizard"

    


