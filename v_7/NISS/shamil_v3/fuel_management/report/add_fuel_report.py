import time
from report import report_sxw
import calendar
import datetime
import pooler

class add_fuel_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.context = context
        super(add_fuel_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'records':self.get_record,
            'to_arabic':self._to_arabic
            })

    def _to_arabic(self, data):
        dict_types = dict([('other','Other'),('permanent','Permanent'),('temporary','Temporary'),('moving','Moving'),('additional','Additional')])
        key = dict_types[data]
        if self.context and 'lang' in self.context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                self.cr, self.uid, [('module','=','fuel_management'),('type','=', 'selection'),('src','ilike', key), ('lang', '=', self.context['lang'])], context=self.context)
            translation_recs = translation_obj.read(
                self.cr, self.uid, translation_ids, [], context=self.context)
            key = translation_recs and translation_recs[0]['value'] or key
        
        return key
#------------------------------- line----------------------------------   

    def get_record(self,data):
        dist_obj=self.pool.get('vehicle.dest')
        res=[]
        wiz=data['form']
        if wiz['type'] in ['other','moving']:
            if wiz['purpose_id']:
                self.cr.execute('SELECT a.name AS ref, a.vehicle_id AS car, '\
                    'v.vin_sn As body_num , v.license_plate, '\
                    'a.order_date ,a.go_date ,a.back_date,'\
                    'a.add_qty , a.purpose_id ,p.name AS purpose ,'\
                    'a.distance_id , d.start_place,d.end_place '\
                    'FROM additional_fuel a '\
                    'left join fleet_vehicle v on (a.vehicle_id=v.id) '\
                    'left join additional_fuel_purpose p on (a.purpose_id=p.id) '\
                    'left join fuel_distance d on (a.distance_id=d.id) '\
                    'WHERE   a.add_type=%s and  a.state=%s and a.purpose_id=%s'\
                    'AND (COALESCE(a.go_date,a.back_date) BETWEEN %s AND  %s) ',(wiz['type'],wiz['state'] and wiz['state'] or 'done' ,wiz['purpose_id'][0],wiz['start_date'],wiz['end_date']))
                res = self.cr.dictfetchall()
                for vd in res:
                    sp=dist_obj.browse(self.cr ,self.uid, vd['start_place']).name
                    ep=dist_obj.browse(self.cr ,self.uid, vd['end_place']).name
                    vd['distination']= sp + '-' + ep
            else:
                self.cr.execute('SELECT a.name AS ref, a.vehicle_id AS car, '\
                    'v.vin_sn As body_num , v.license_plate, '\
                    'a.order_date ,a.go_date ,a.back_date,'\
                    'a.add_qty , a.purpose_id ,p.name AS purpose,'\
                    'a.distance_id , d.start_place,d.end_place '\
                    'FROM additional_fuel a '\
                    'left join fleet_vehicle v on (a.vehicle_id=v.id) '\
                    'left join additional_fuel_purpose p on (a.purpose_id=p.id) '\
                    'left join fuel_distance d on (a.distance_id=d.id) '\
                    'WHERE   a.add_type=%s and  a.state=%s '\
                    'AND (COALESCE(a.go_date,a.back_date) BETWEEN %s AND  %s) ',(wiz['type'],wiz['state'] and wiz['state'] or 'done',wiz['start_date'],wiz['end_date']))
                res = self.cr.dictfetchall()
                for vd in res:
                    sp=dist_obj.browse(self.cr ,self.uid, vd['start_place']).name
                    ep=dist_obj.browse(self.cr ,self.uid, vd['end_place']).name
                    vd['distination']= sp + '-' + ep
        elif wiz['type'] in ['permanent','additional']:
            self.cr.execute('SELECT a.name AS ref, a.vehicle_id AS car, '\
                'v.vin_sn As body_num , v.license_plate, '\
                'a.order_date ,v.fuel_type,'\
                'a.add_qty '\
                'FROM additional_fuel a '\
                'left join fleet_vehicle v on (a.vehicle_id=v.id) '\
                'WHERE a.add_type=%s and a.state=%s ',(wiz['type'],wiz['state'] and wiz['state'] or 'done' ))
            res = self.cr.dictfetchall()
        else:
            self.cr.execute('SELECT a.name AS ref, a.vehicle_id AS car, '\
                'v.vin_sn As body_num , v.license_plate, '\
                'a.order_date ,v.fuel_type,'\
                'a.add_qty ,a.start_date ,a.end_date '\
                'FROM additional_fuel a '\
                'left join fleet_vehicle v on (a.vehicle_id=v.id) '\
                'WHERE a.add_type=%s and a.state=%s '\
                'AND (COALESCE(a.start_date,a.end_date) BETWEEN %s AND  %s) ',(wiz['type'],wiz['state'] and wiz['state'] or 'done',wiz['start_date'],wiz['end_date'] ))
            res = self.cr.dictfetchall()
        return res


report_sxw.report_sxw('report.add_fuel_report', 'hr.secret.report.process', 'addons/fuel_management/report/add_fuel_report.rml' ,parser=add_fuel_report, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
