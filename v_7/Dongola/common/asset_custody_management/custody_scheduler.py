# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
import tools
from osv import osv, fields
import decimal_precision as dp
from tools.translate import _
import netsvc


class custody_scheduler(osv.osv):

      _name = 'custody.scheduler'
      

      def custody_release_scheduler(self, cr, uid,context=None):
          custody_obj = self.pool.get("account.asset.asset")
          smtplib_mail_obj = self.pool.get("smtplib.mail")

          custody_ids =  custody_obj.search(cr ,uid ,[('state','=','open'),('create_release_order','=','False'),('period_type','=','temp'),('expacted_return_date','<=', time.strftime('%Y-%m-%d') )])
          for custody_id in custody_ids :
              order_id = custody_obj.create_release_order(cr, uid , [custody_id] , context)
              #smtplib_mail_obj.smtp_send_email("")
          return True
