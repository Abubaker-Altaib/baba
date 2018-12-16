import smtplib
from osv import osv, fields
#from django.utils.encoding import smart_str
#content = smart_str(content)

# class purchase_requisition(osv.Model):
# 
#       _inherit = 'purchase.requisition'
# 
#       def smtp_send_email(self, cr, uid, ids, context=None):
#         
#         
#         requesition = self.browse(cr, uid, ids)[0]
# #         email_template_obj = self.pool.get('email.template')
#         users = self.pool.get('res.users')
# #         template_ids = email_template_obj.search(cr, uid, [('model_id.model', '=','purchase.requisition')], context=context) 
#         subject = 'RFQ For ' + requesition.name
# # 
# #         if template_ids:
# #             values = email_template_obj.generate_email(cr, uid, template_ids[0], ids[0] , context=context)
# #             
# #             report_id = email_template_obj.browse(cr,uid,template_ids)[0].report_template.id
# #             
# #             if requesition.supplier_ids:
# # 
# #                for partner in requesition.supplier_ids:
# #                     values['subject'] = subject 
# #                     values['email_to'] = partner.email
# #                     #values['attachement_ids'] = [6,0,[report_id]]
# #                    values['body_html'] = "Dear " + partner.name + values['body_html']
# #                         This Message From """ + requesition.company_id.name + """ 
# # 
# #                         Kindly See attached file and feed us back about your perfoma invoice 
# #                         
# #                         \n Best Regard 
# #                         \n If you have any question, do not hesitate to contact us.
# #                         
# #                         \n Purchases Section \n
# #                          """  + users.browse(cr,uid,uid).name
# #                    values['body'] = "Dear " + partner.name + values['body']
# #                         This Message From """ + requesition.company_id.name + """ 
# # 
# #                         Kindly See attached file and feed us back about your perfoma invoice 
# #                         
# #                         \n Best Regard 
# #                         \n If you have any question, do not hesitate to contact us.
# #                         
# #                         \n Purchases Section \n
# #                          """  + users.browse(cr,uid,uid).name
# #                          
# #                     values['res_id'] = False
# #                     mail_mail_obj = self.pool.get('mail.mail')
# #                     msg_id = mail_mail_obj.create(cr, uid, values, context=context)
# #                     if msg_id:
# #                        mail_mail_obj.send(cr, uid, [msg_id], context=context)
# #         
# #         
# #         
#         ir_mail = self.pool.get('ir.mail_server')
# #         users = self.pool.get('res.users')
# #         receivers = []
# #         Subject = 'RFQ For ' + requesition.name
# #         
# #         
# #         
# #         
#         mail_id = ir_mail.search( cr, uid, [('smtp_host' , '=' , 'smtp.gmail.com')])
#         if mail_id :
#            for rec in ir_mail.browse(cr,uid,mail_id):
#                user_name = rec.smtp_user
#                password = rec.smtp_pass
#                #sender = rec.smtp_user
#  
#                smtpObj = smtplib.SMTP(host='smtp.gmail.com', port=587)
#                smtpObj.set_debuglevel(1)
#                smtpObj.ehlo()
#                smtpObj.starttls()                                
#                smtpObj.login(user=user_name, password=password)
#         for rec in self.browse(cr,uid,ids):
#                     for partner in rec.supplier_ids:
#                         Text = "Dear " + partner.name + """ ,,, \n
#                         This Message From """ + rec.company_id.name + """ 
#  
#                         Kindly See attached file and feed us back about your perfoma invoice 
#                          
#                         \n Best Regard 
#                         \n If you have any question, do not hesitate to contact us.
#                          
#                         \n Purchases Section \n
#                          """  + users.browse(cr,uid,uid).name
#                         message = 'Subject: %s\n\n%s' % (subject, Text)                        
#                      
#                         smtpObj.sendmail(user_name, partner.email ,  message)  
#         return True
#        
