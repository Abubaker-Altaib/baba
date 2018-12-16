# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw

class enrich_report(report_sxw.rml_parse):
    """ To manage enrich report """

    def set_context(self, objects, data, ids,report_type=None):
        """
        Return report data in object.
        
        @param objects: object to return
        @param data: extra data
        @param report_type: record id
        @return: super set context
        """
        return super(enrich_report, self).set_context(objects,  data,  ids, 
                         report_type=report_type)

report_sxw.report_sxw('report.enrich_report.report','payment.enrich','addons/admin_affairs/report/enrich_report.rml',parser=enrich_report, header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
