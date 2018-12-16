import smtplib
from osv import osv, fields


class smtplib_mail(osv.osv):

      _name = 'smtplib.mail'

      def smtp_send_email(self,address):


	sender = ''
	receivers = address

	message = """ Dear Mr/Mrs: 
		      Technical Support Department strongly apologize for this inconvenience and they want to tell you that Your Custodies will
                      been released from You Today According to your agreement  ... 

	"""


	smtpObj = smtplib.SMTP(host='smtp.gmail.com', port=587)
	smtpObj.ehlo()
	smtpObj.starttls()
	smtpObj.ehlo()
	smtpObj.login(user="", password="")
	smtpObj.sendmail(sender, receivers, message)         
	print "Successfully sent email to :",receivers
        return True
       

