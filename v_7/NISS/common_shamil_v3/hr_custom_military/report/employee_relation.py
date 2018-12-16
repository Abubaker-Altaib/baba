import time
from report import report_sxw
import calendar
from datetime import datetime
import pooler
from dateutil.relativedelta import relativedelta


def to_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date()


class employee_relation(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.context = context
        print "--------------------context", context,name
        super(employee_relation, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'datas': self.get_relation_record,
            'get_list':self._get_list
        })
    def _get_list(self, data):
        if self.context['active_model']=='hr.employee':
            return data

        newlist = [x.id for x in data]
        obj = self.pool.get(self.context['active_model'])
        static = obj.browse(self.cr, self.uid, newlist)

        self.context['active_model_ids'] = [x.id for x in static]
        newlist = [x.employee_id for x in static]
        return newlist
        

    def get_relation_record(self, data):
        relation_obj = self.pool.get('hr.employee.family')
        translation_obj = self.pool.get('ir.translation')
        state = {'draft': 'Draft','approved':'Approved',
                            'approvewfees':'Approvedd with fees',
                            'rejectedwfees':'Rejected with fees',
                            'rejected': 'Rejected','stopped': 'Stopped'
                            }
        
        
        res = []
        if self.context['active_model']=='hr.employee':
            relation_ids = relation_obj.search(self.cr, self.uid, [('employee_id','=',data.id), ('state','=','approved')])

        if self.context['active_model']!='hr.employee':
            relation_ids = self.context['active_model_ids']

        
        if relation_ids:
            datee = time.strftime('%Y-%m-%d')
            dt = datetime.strptime(datee, '%Y-%m-%d')
            count = 0
            for rec in relation_obj.browse(self.cr, self.uid, relation_ids):
                count += 1
                key = rec.state
                birthdate = datetime.strptime(rec.birth_date, '%Y-%m-%d')
                date = relativedelta(dt,birthdate)
                old = date.years
                if key:
                    key = state[key]
                    translation_ids = translation_obj.search(
                        self.cr, self.uid, [('src','=', key), ('lang', '=', 'ar_SY')])
                    translation_recs = translation_obj.read(
                        self.cr, self.uid, translation_ids, [])
                    key = translation_recs and translation_recs[0]['value'] or key
                dicts = {
                'relation_name': rec.relation_name,
                'relation_id': rec.relation_id.name,
                'birth_date': rec.birth_date,
                'comments': rec.comments,
                'state': key,
                'old': old,
                'count': count,
                }

                res.append(dicts)

        
        return res

report_sxw.report_sxw('report.employee_relation_renewal', 'hr.employee',
                      'addons/hr_custom_military/report/employee_relation.rml', parser=employee_relation, header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
