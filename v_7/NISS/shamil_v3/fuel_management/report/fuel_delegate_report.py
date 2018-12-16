import time
from report import report_sxw
import calendar
import datetime
import pooler

class fuel_delegate_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.context = context
        super(fuel_delegate_report, self).__init__(cr, uid, name, context)
        records = dict()
        records = self.get_record()
        self.localcontext.update({'delegate':records,'to_arabic':self._to_arabic})

#------------------------------- line----------------------------------   
    def _to_arabic(self, data):
        dict_types = dict([('delegate', 'Fuel Delegate'), ('location', 'Location'), ('fuel_type', 'Fuel Type')])
        key = dict_types[data]
        if self.context and 'lang' in self.context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                self.cr, self.uid, [('module','=','fuel_management'),('type','=', 'selection'),('src','ilike', key), ('lang', '=', self.context['lang'])], context=self.context)
            translation_recs = translation_obj.read(
                self.cr, self.uid, translation_ids, [], context=self.context)
            key = translation_recs and translation_recs[0]['value'] or key
        
        return key

    def get_record(self):
        res=[]
        result={}
        data = self.pool.get('fuel.delegate.report.wizard').browse(self.cr , self.uid , [self.context['active_id']])[0]
        result['type']=data.type
        if data.type == 'delegate':
            for delegate in data.delegate_ids:
                res.append({
                    'name' : delegate.employee_id.name,
                    'degree':delegate.degree_id.name,
                    'department' : delegate.department_id.name,
                    'code' : delegate.emp_code,
                    'delegates' : self._get_delegate_lines(delegate), 
                    'location':self._get_location(data.location_ids),
                })
        elif data.type == 'location':
            for location in data.location_ids:
                res.append({
                    'name' : location.name,
                    'locations':self._get_location(data.location_ids),
                })
        elif data.type == 'fuel_type':
            for fuel in data.fuel_type_ids:
                res.append({
                    'name' : fuel.name,
                    'fuel_types':self._get_fuel_type(data.fuel_type_ids),
                })
        result['data']=res
        return result

    def _get_fuel_type(self,fuels):
        res=[]
        line_obj = self.pool.get('fuel.delegate.lines')
        for fuel in fuels:
            line_ids = line_obj.search(self.cr, self.uid, [('product_id','=',fuel.id),('state','=','confirm')])
            if line_ids:
                for line in line_obj.browse(self.cr,self.uid,line_ids):
                    res.append(line)
        return res

    def _get_location(self,location):
        res=[]
        line_obj = self.pool.get('fuel.delegate.lines')
        for loc in location:
            line_ids = line_obj.search(self.cr, self.uid, [('location_id','=',loc.id),('state','=','confirm')])
            if line_ids:
                for line in line_obj.browse(self.cr,self.uid,line_ids):
                    res.append(line)
        return res

    def _get_delegate_lines(self,delegate):
        res=[]
        delegate_obj=self.pool.get('fuel.delegate')
        for line in delegate.line_id:
            res.append(line)
        return res

report_sxw.report_sxw('report.fuel_delegate_reports', 'fuel.delegate', 'addons/fuel_management/report/fuel_delegate_report.mako' ,parser=fuel_delegate_report, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
