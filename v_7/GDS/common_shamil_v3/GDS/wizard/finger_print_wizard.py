# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from datetime import date ,datetime
from openerp.osv import osv, fields , orm
from openerp.tools.translate import _
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from openerp import tools
from itertools import groupby
from operator import itemgetter
import subprocess
import urllib2
import json
from openerp import addons
from openerp.addons.GDS.models.gutil import shell , xyt_path 
import os
import random



class attendance_wizerd(osv.osv_memory):
    _name = "finger.print"

    _columns = {
    'hand':fields.selection([('right', 'Right'),
                                   ('left', 'Left'),
                                   ], 'Select hand',
                                   required=True,),
    'finger':fields.selection([('thumb', 'الإبهام'),
                                   ('Index', 'السبابة'),
                                   ('middle_finger', 'الوسطى'),
                                   ('ring_finger', 'البنصر'),
                                   ('Pinkie', 'الخنصر'),
                                   ], 'Select Finger',
                                   required=True,),
    }

    def client_confirm(self, cr, uid, ids, context={}):
        data = self.read(cr, uid, ids, [], context=context)[0]
        finger = str(data['hand'])+"_"+str(data['finger'])
        print "####### ", finger
        return {
            'type' : 'ir.actions.client',
            'tag' : 'bio_request',
            'params' : {
            'finger' : finger ,
            },
        }

    def get_xyt_name(self , employee_id , finger):
        xyt_name = addons.get_module_resource('GDS', 'static/src/img/xyt_finger_print') +"/" +str(employee_id)+"_"+finger+".xyt"
        return xyt_name

    def get_random(self):
        func = {
            1 : lambda : str(int(random.random() * 100 )),
            2 : lambda : chr(random.randrange(65,90)) ,
            3 : lambda : chr(random.randrange(97,122)) ,
        }
        return func[1]()+func[2]()+func[3]()+func[random.randrange(1 ,4)]()


    def clean(self , *files):
        
        save_path = addons.get_module_resource('GDS', 'static/src/img/')
        for i in files :
            print i
            os.popen(''' 
            rm %s%s
         '''%(save_path,i))

    def fingerprint_search(self , cr , uid , img_data , finger , context=None):
        matched_ids = False
        save_path = addons.get_module_resource('GDS', 'static/src/img/')
        new_name = self.get_random()
        img_name = new_name+'.png'
        fileTosave = save_path+img_name
        fh = open(fileTosave, "wb")
        fh.write(img_data.decode('base64'))
        fh.close()
        xyt_name = save_path +'/'+new_name
        shell.execute('mindtct' , fileTosave , xyt_name)
        match_result = os.popen(''' 
            /opt/bio/bin/bozorth3 -A outfmt=g -T 30 -p %s.xyt /opt/gds/common_shamil_v3/GDS/static/src/img/xyt_finger_print/*_%s.xyt
         '''%(xyt_name,finger)).read().strip()
        if match_result:
            matched_ids = []
            for matched_file_result in match_result.split():
                matched_file_result = matched_file_result.split('/')[-1]
                matched_id = matched_file_result.split('_')[0]
                matched_ids.append(int(matched_id))
        self.clean(img_name)
        return matched_ids


    def Verivecation(self, cr, uid, ids, context=None):
        '''user = self.pool.get('res.users').browse(cr, uid, uid, context = context)
        if not user.company_id.comparison_percentage:
                raise osv.except_osv(_('ERROR'), _('please configure Comparison Percentage on config settings'))

        comparison_percentage = user.company_id.comparison_percentage'''

        data = self.read(cr, uid, ids, [], context=context)[0]

        finger_bitmap = str(data['hand'])+"_"+str(data['finger'])
        #raise osv.except_osv(_('Hey !'), _(emp.str(data['finger'])))

        NitgenRequest = {
        "Quality": 60,
        "TimeOut": 10
        }
        json_data = json.dumps(NitgenRequest)
        url = 'http://localhost:9101/bioenable/capture'
        req = urllib2.Request(url, json_data, {'Content-Type': 'application/json'})
        sending_request = urllib2.urlopen(req)
        response = sending_request.read()
        data = json.loads(response)
        #raise Warning(data)
        if not data['BitmapData']:
            raise osv.except_osv(_('Hey !'), _(" please put your Finger to captuer it "))  

        bitmap = data['BitmapData']


        emp_object = self.pool.get('hr.employee')
        employees = emp_object.search(cr , uid , [])
        Similarity = 0
        verfied_emp_object = None
        test =""
        for emp in emp_object.browse(cr , uid , employees):
            bitmap_hand_fingers = {
            'right_thumb':emp.right_thumb,
            'right_Index':emp.right_Index,
            'right_middle_finger':emp.right_middle_finger,
            'right_ring_finger':emp.right_ring_finger,
            'right_Pinkie':emp.right_Pinkie,

            'left_thumb':emp.left_thumb,
            'left_Index':emp.left_Index,
            'left_middle_finger':emp.left_middle_finger,
            'left_ring_finger':emp.left_ring_finger,
            'left_Pinkie':emp.left_Pinkie,
            }
            if bitmap_hand_fingers[finger_bitmap]:

                fileTosave = "C:/xampp/htdocs/finger/ref.png"
                fh = open(fileTosave, "wb")
                fh.write(bitmap_hand_fingers[finger_bitmap].decode('base64'))
                fh.close()

                fileTosave = "C:/xampp/htdocs/finger/new.png"
                fh = open(fileTosave, "wb")
                fh.write(bitmap.decode('base64'))
                fh.close()

                ping_process = subprocess.Popen([r"C:/Users/ayman/Downloads/Sample/bin/Debug/Sample.exe"],stdout=subprocess.PIPE)
                stdout = ping_process.stdout.read()
                #raise Warning(float(stdout.split('=',1)[1]))
                if float(stdout.split('=',1)[1]) > 60 :
                    if float(stdout.split('=',1)[1]) > Similarity:
                        verfied_emp_object = emp 
                        Similarity = float(stdout.split('=',1)[1]) #Similarity score between Scanned Finger and The Refrence Fingerprint = 63.718

        if verfied_emp_object : 
            ctx = (context or {}).copy()
            return {
                'view_type':'form',
                'view_mode':'tree,form',
                'res_model':'payment.record',
                'view_id':False,
                'type':'ir.actions.act_window',
                'domain':[('employee_id','=',verfied_emp_object.id),('state','=','draft')],
                'context':ctx,
            }
            #raise Warning(test)
        else:
            raise osv.except_osv(_('Opss  !'), _(" It seems that person not found or maby is not registerd "))
    



