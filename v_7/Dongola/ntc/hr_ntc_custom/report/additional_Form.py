import time
from report import report_sxw
import calendar
import datetime
import pooler
import math

class additional_form_report(report_sxw.rml_parse):
    globals()['total_net']=0.0
    globals()['no_data'] = False


    def __init__(self, cr, uid, name, context):
        super(additional_form_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._get_line,
            'line1':self._get_line2,
            'user':self._get_user,
            
        })
        globals()['total_net']=0.0
        globals()['no_data'] = False
    

    def _get_user(self,data, header=False):
        if header:
            return self.pool.get('res.company').browse(self.cr, self.uid, data['form']['company_id'][0]).logo
        else:
            return self.pool.get('res.users').browse(self.cr, self.uid, self.uid).name

    def _get_line(self,record):
        result = []
        lines = {}
        additional_obj = self.pool.get('hr.additional.allowance')
        additional_rec = additional_obj.browse(self.cr, self.uid,record['active_id'])
        result += additional_rec.line_ids
        for line in additional_rec.line_ids:
            for d in line.allowance_detail_ids:
                lines['date'] = d.date
                if d.flage:
                    lines['add_work_day'] = u'-'
                    lines['work_hour'] = u'-'
                    lines['add_holiday'] = d.dayofweek
                    lines['work_holiday'] = d.hour
                else:
                    lines['add_work_day'] = d.dayofweek
                    lines['work_hour'] = d.hour
                    lines['add_holiday'] = u'-'
                    lines['work_holiday'] = u'-'
                lines['reason'] = additional_rec.work_need
                lines['comment'] = additional_rec.work_resons
        
        return result

    def _get_line2(self,record):
        result = []
        lines = {}
        additional_obj = self.pool.get('hr.additional.allowance')
        #additional_rec = additional_obj.browse(self.cr, self.uid,record['active_id'])
        #result += additional_rec.line_ids
        #for line in record:
        for d in record.allowance_detail_ids:
            lines = {}
            lines['date'] = d.date
            if d.flage:
                lines['add_work_day'] = u'-'
                lines['work_hour'] = u'-'
                lines['add_holiday'] = d.dayofweek
                lines['work_holiday'] = d.hour
            else:
                lines['add_work_day'] = d.dayofweek
                lines['work_hour'] = d.hour
                lines['add_holiday'] = u'-'
                lines['work_holiday'] = u'-'
            lines['reason'] = record.additional_allowance_id.work_need
            lines['comment'] = record.additional_allowance_id.work_resons or u''
            result.append(lines)
        
        return result

    


    
    def _total(self,data,bank_id):
        return globals()['total_net']

        
report_sxw.report_sxw('report.additional_form', 'hr.additional.allowance', 'addons/hr_ntc_custom/report/additional_Form.rml' ,parser=additional_form_report,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


