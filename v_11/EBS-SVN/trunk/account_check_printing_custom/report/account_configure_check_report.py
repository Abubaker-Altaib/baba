# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import models
#import pooler
#from report.interface import report_rml
from odoo.tools.translate import _
from datetime import datetime
from odoo.report import report_sxw

class report_check_custom(report_sxw.rml_parse):
    def create_xml(self, datas):
        self.env = pooler.get_pool(cr.dbname)
        voucher = self.env['account.voucher'].browse(datas['form']['payment_id'][0])
        xml = '''<?xml version="1.0" encoding="UTF-8" ?>
                <report><page size='A4_portrait' >'''
        dimension = voucher.pay_now == 'pay_now' and voucher.pay_journal_id.check_dimension or voucher.journal_id.check_dimension
        if not dimension: raise UserError(_('Error !'), _("Please configure check dimension"))
        #Date
        xml = xml + "<date_spacer>" + str(dimension.date_h)  +"mm</date_spacer>"
        dot = "."
        for s in range(dimension.date_w):
            dot = dot + "."
        date = str(datetime.strptime(voucher.date,'%Y-%m-%d').strftime('%d/%m/%Y'))
        xml = xml + "<date_dot>" + dot+"</date_dot><date>"+ date  +"</date>"
        #Name 
        xml = xml + "<name_spacer>" + str(dimension.name_h)  +"mm</name_spacer>"        
        dot = "."
        for s in range(dimension.name_w):
            dot = dot + "."
        xml = xml + "<name_dot>" + dot+"</name_dot><name>" + voucher.partner_id.name +"</name>"

        #Amount
        xml = xml + "<amount_spacer>" + str(dimension.amount_h)  +"mm</amount_spacer>"
        dot = "."
        for s in range(dimension.amount_w):
            dot = dot + "."
        xml = xml + "<amount_dot>" + dot+"</amount_dot><amount>"  + voucher.amount_in_word +"</amount>"

        #Number
        xml = xml + "<number_spacer>" + str(dimension.number_h)  +"mm</number_spacer>"
        dot = "."
        for s in range(dimension.number_w):
            dot = dot + "."
        xml = xml + "<number_dot>" + dot+"</number_dot><number>" + str(voucher.amount) +"</number>"

        xml = xml + "<font_size>"+ str(dimension.font_size) + "</font_size></page></report>"
        print xml
        return xml


report_sxw.report_sxw('report.account.print.check', 'account.payment', 'addons/account_check_printing_custom/report/account_configure_check_report.xsl', parser=report_check_custom, header=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
