
# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw

class residence_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        self.counter = 0
        super(residence_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'lines':self.lines,
            'states':self.get_states,
            'locals':self.get_locals,
            'degrees':self.get_degrees,
            'counter':self.get_counter,
            'get_count_state':self.get_count_state,
            'get_count_local_state':self.get_count_local_state,
            'get_count_local_state_degree':self.get_count_local_state_degree,
            'get_count_state_degree':self.get_count_state_degree,
            'get_count_all':self.get_count_all,
            'get_count_degree':self.get_count_degree,
            'sum_name':unicode('الإجمالي', 'utf-8')
        })
    def get_count_degree(self, degree):
        degrees = filter(lambda x :x['degree_id'][0] ==  degree, self.emps_names)
        return len(degrees)
    def get_count_all(self):
        return len(self.emps_names)
    def get_count_state(self, state):
        states = filter(lambda x :x['living_state'][0] ==  state, self.emps_names)
        return len(states)
    def get_count_local_state(self, local,state):
        states = filter(lambda x :x['living_local'][0] ==  local and x['living_state'][0] ==  state, self.emps_names)
        return len(states)
    def get_count_state_degree(self, state, degree):
        states = filter(lambda x :x['living_state'][0] ==  state and x['degree_id'][0] ==  degree, self.emps_names)
        return len(states)
    def get_count_local_state_degree(self, local,state, degree):
        states = filter(lambda x :x['living_local'][0] ==  local and x['living_state'][0] ==  state and x['degree_id'][0] ==  degree, self.emps_names)
        return len(states)
    def get_counter(self):
        self.counter += 1
        return self.counter
    def get_states(self):
        return self.states_name
    def get_locals(self,data,state):
        localss_name=[]
        location_obj= self.pool.get('hr.employee.location.state')
        for local in location_obj.browse(self.cr, self.uid,self.local_ids):
            if local.parent_id.id == state['id']:
                localss_name.append({'name':local.name,'id':local.id})
        return localss_name
    def get_degrees(self):
        return self.degrees_name
    def lines(self,data):
        degree_obj = self.pool.get('hr.salary.degree')
        location_obj= self.pool.get('hr.employee.location.state')
        emps_obj = self.pool.get('hr.employee')

        degree_ids = data['form']['degree_ids']
        state_ids = data['form']['state_ids']
        local_ids = data['form']['local_ids']

        if not degree_ids:
            degree_ids = degree_obj.search(self.cr, self.uid, [])
        
        if not state_ids:
            state_ids = location_obj.search(self.cr, self.uid, [('type','=','state')])

        if not local_ids:
            local_ids = location_obj.search(self.cr, self.uid, [('type','=','local')])

        self.degrees_name = degree_obj.read(self.cr, self.uid, degree_ids, ['name'])

        self.states_name = location_obj.read(self.cr, self.uid, state_ids, ['name'])

        self.localss_name = location_obj.read(self.cr, self.uid, local_ids, ['name'])
        self.local_ids = local_ids

        if data['form']['type'] == 'state':
            emps_ids = emps_obj.search(self.cr, self.uid, [('living_state','in',state_ids), ('degree_id','in',degree_ids), ])
            self.emps_names = emps_obj.read(self.cr, self.uid, emps_ids, ['living_state','degree_id'])
        else:
            emps_ids = emps_obj.search(self.cr, self.uid, [('living_state','in',state_ids),('living_local','in',local_ids), ('degree_id','in',degree_ids), ])
            self.emps_names = emps_obj.read(self.cr, self.uid, emps_ids, ['living_state','living_local','degree_id'])
        return True
        


report_sxw.report_sxw('report.residence_state_report','hr.employee','addons/hr_custom_military/report/residence_state_report.mako',parser=residence_report,header=False)
