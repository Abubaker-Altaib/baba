# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

import openerp
from openerp import tools
from openerp.modules.module import get_module_resource
from openerp.osv import fields,osv
from openerp.tools.translate import _
import json
from openerp import netsvc

from openerp import addons
import subprocess
import urllib2
import json
import base64
from  gutil import shell
import datetime
import os

save_path = '/opt/gds/common_shamil_v3/GDS/static/src/img/emp_finger_print/'

class employee_payment_action(osv.osv_memory):

    _name = "employee.payment.action"

    def link_payments(self, cr, uid, ids, context={}):
        employee = self.pool.get('hr.employee')
        payment_record = self.pool.get('payment.record')
        if 'active_ids' in context and context['active_ids']:
            flag = False
            for rec in context['active_ids']:
                emp_code = payment_record.browse(cr,uid,rec ).employee_code
                if emp_code : 
                    employee_id = employee.search(cr,uid,[('emp_code','=',emp_code)])
                    if employee_id:
                        employee_id = employee_id[0]
                        payment_record.write(cr , uid ,rec, {'employee_id':employee_id})
                    else:
                        flag = True
                else:
                    flag = True
            if flag :
                print'some field dosen\'t proceeced '
                '''
                The under line if un hashed if the value of flag become true then he will not process the other records 'odoo framework!' 
                raise osv.except_osv(_('UserError'),_('some payments record not processed because they did not have employee Code or \n The enterd code dosen\'t match any employee code' ))
                '''

        return True
class hr_district(osv.osv):
    _name = "hr.district"
    _columns = {
        'name':fields.char('District'),#الحى

    }

class hr_managiral_unit(osv.osv):
    _name = "hr.managiral_unit"
    _columns = {
        'name':fields.char('Managiral Unit'),#الوحدة الإدارية

    }
class hr_local(osv.osv):
    _name = "hr.local"
    _columns = {
        'name':fields.char('Local'),#المحلية

    }

class hr_state(osv.osv):
    _name = "hr.state"
    _columns = {
        'name':fields.char('Name'),#الولاية

    }

class hr_tribe(osv.osv):
    _name = "hr.tribe"
    _columns = {
        'name':fields.char('Tribe'),#القبيلة

    }
class hr_abdominal(osv.osv):
    _name = "hr.abdominal"
    _columns = {
        'name':fields.char('Abdominal'),#البطن

    }
class hr_discounted_house(osv.osv):
    _name = "hr.discounted.house"
    _columns = {
        'name':fields.char('Discounted House'),#خشم البيت

    }
class hr_employee_inhirit(osv.osv):
    _inherit = "hr.employee"
    _columns = {
        'mother_name' : fields.char('Mother') ,
		'payments_ids':fields.one2many('payment.record', 'employee_id', string='Payments'),
        'hand':fields.selection([('right', 'Right'),
                                   ('left', 'Left'),
                                   ], 'Select hand',
                                   required=True,),

        'finger':fields.selection([('thumb', 'Thumb'),#الاإبهام
                                   ('Index', 'Index'),#السبابة
                                   ('middle_finger', 'Middle Finger'),#الوسطى
                                   ('ring_finger', 'Ring Finger'),#البنصر
                                   ('Pinkie', 'Pinkie'),#الخنصر
                                   ], 'Select Finger',
                                   required=True,),

    
        'right_thumb_lc': fields.char("Thumb",
            help="This field holds employee Finger Print Image, limited to 1024x1024px."),
        'right_Index_lc': fields.char("Index",
            help="This field holds employee Finger Print Image, limited to 1024x1024px."),
        'right_middle_finger_lc': fields.char("Middle Finger",
            help="This field holds employee Finger Print Image, limited to 1024x1024px."),
        'right_ring_finger_lc': fields.char("Ring Finger",
            help="This field holds employee Finger Print Image, limited to 1024x1024px."),
        'right_Pinkie_lc': fields.char("Pinkie",
            help="This field holds employee Finger Print Image, limited to 1024x1024px."),

        'left_thumb_lc': fields.char("Thumb",
            help="This field holds employee Finger Print Image, limited to 1024x1024px."),
        'left_Index_lc': fields.char("Index",
            help="This field holds employee Finger Print Image, limited to 1024x1024px."),
        'left_middle_finger_lc': fields.char("Middle Finger",
            help="This field holds employee Finger Print Image, limited to 1024x1024px."),
        'left_ring_finger_lc': fields.char("Ring Finger",
            help="This field holds employee Finger Print Image, limited to 1024x1024px."),
        'left_Pinkie_lc': fields.char("Pinkie",
            help="This field holds employee Finger Print Image, limited to 1024x1024px."),
        'image_lc': fields.char("image"),

        'Military_ID':fields.char('Military ID'),#الرقم العسكري

        'camp':fields.char('Camp'),#المعسكر
        'camp_date':fields.date('Camp Date'),#تاريخ دخول المعسكر
        'camp_end_date':fields.date('Camp End Date'),#تاريخ التخريج

        #place of birth
        'pl_state':fields.many2one('hr.state', string="State"),#الولاية
        'local':fields.many2one('hr.local',string="Local"),#المحلية
        'managiral_unit':fields.many2one('hr.managiral_unit',string="Managiral Unit"),#الوحدة الإدارية
        'district':fields.many2one('hr.district',string="District"),#الحى

        #Tribe
        'tribe':fields.many2one('hr.tribe',string="Tribe"),#القبيلة
        'abdominal':fields.many2one('hr.abdominal' , string="Abdominal"),#البطن
        'discounted_house':fields.many2one('hr.discounted.house' , string="Discounted House"),#خشم البيت

        #omda
        'omda_name':fields.char('Omda Name'),#اسم العمدة
        'omda_phone':fields.char('Phone'),#رقم الهاتف
        'omda_address':fields.char('Address'),#العنوان
        'omda_address2':fields.char('Address2'),#مكان الإقامة
        'omda_national_number':fields.char('National Number'),#الرقم الوطنى

        #shakih
        'sh_name':fields.char('Shakh Name'),#اسم الشيخ
        'sh_phone':fields.char('Phone'),#رقم الهاتف
        'sh_address':fields.char('Address'),#العنوان
        'sh_address2':fields.char('Address2'),#مكان الإقامة
        'sh_national_number':fields.char('National Number'),#الرقم الوطنى

        #The nearest closest
        'ne_name':fields.char('Nearest Name'),#الاسم
        'ne_phone':fields.char('Phone'),#رقم الهاتف
        'ne_address':fields.char('Address'),#العنوان
        'ne_address2':fields.char('Address2'),#مكان الإقامة
        'ne_national_number':fields.char('National Number'),#الرقم الوطنى


    }

    def _get_default_image(self, cr, uid, context=None):
        image_path = addons.get_module_resource('GDS', 'static/src/img', 'fingerPrint.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))




    def register_finger_print (self, cr, uid, ids, context=None):
        emp_object = self.browse(cr ,uid , ids )[0]
        finger = str(emp_object.hand)+"_"+str(emp_object.finger)
        return {
            'type' : 'ir.actions.client',
            'tag' : 'finger_print_store',
            'params' : {
                'finger' : finger ,
                'employee_id' : emp_object.id ,
            },
        }


    def process_bio(self, cr, uid,emp_id ,  img_data , img_name, finger, payment_id , state ,
        model_name="payment.record" ,context={}):
        '''
        print "########### state " , state
        print "########### model " , model_name
        print "########### payment_id " , payment_id
        self.create_img(cr , uid , img_data , img_name )
        ref_data = self.read(cr , uid, emp_id,[finger])[finger]
        self.create_img(cr , uid , ref_data , 'ref.png' )'''
        save_path = addons.get_module_resource('GDS', 'static/src/img/emp_finger_print')
        img_name = str(emp_id)+"_"+"new.png"
        fileTosave = save_path+"/"+img_name
        fh = open(fileTosave, "wb")
        fh.write(img_data.decode('base64'))
        fh.close()
        xyt_name = addons.get_module_resource('GDS', 'static/src/img/xyt_finger_print') + "/new"
        shell.execute('mindtct' , fileTosave , xyt_name)

        new_xyt = xyt_name + '.xyt'
        emp_xyt = addons.get_module_resource('GDS', 'static/src/img/xyt_finger_print') +"/"+ str(emp_id) + "_"+finger+".xyt"
        degree = shell.execute('bozorth' , emp_xyt , new_xyt)
        try :
            degree = float(degree)
            if degree >= 30 :
                self.pool.get(model_name).write(cr, uid, [payment_id], {'state': state})
                return 0
        except :
            return 1
        return 1


    def compare_bio(self):
        print "############# compare"
        url = "http://192.168.56.101:8082/bio/mach"
        req = urllib2.Request(url)
        sending_request = urllib2.urlopen(req)
        response = sending_request.read()
        return response

    def clean(self , *files):
        
        save_path = addons.get_module_resource('GDS', 'static/src/img/')
        for i in files :
            os.popen(''' 
            rm %s%s
         '''%(save_path,i))


    def create_img(self,  cr, uid , employee_id , img_data , finger , context=None):
        fp = self.pool.get('finger.print')

        compare = fp.fingerprint_search(cr , uid , img_data , finger)
        if compare :
            return False
        save_path = addons.get_module_resource('GDS', 'static/src/img/emp_finger_print')
        img_name = str(employee_id)+"_"+finger+".png"
        fileTosave = save_path+"/"+img_name
        fh = open(fileTosave, "wb")
        fh.write(img_data.decode('base64'))
        fh.close()
        field = finger+'_lc'
        field_val = '/GDS/static/src/img/emp_finger_print/'+img_name
        self.pool.get('hr.employee').write(cr , uid , [employee_id] , {field : field_val})
        xyt_name = addons.get_module_resource('GDS', 'static/src/img/xyt_finger_print') + "/"+str(employee_id)+"_"+finger
        shell.execute('mindtct' , fileTosave , xyt_name)
        self.clean('xyt_finger_print/*.brw' , 'xyt_finger_print/*.dm' , 'xyt_finger_print/*.hcm' , 'xyt_finger_print/*.lcm' ,'xyt_finger_print/*.lfm' , 'xyt_finger_print/*.qm' ,'xyt_finger_print/*.min')
        return img_name

    def set_image_local(self , cr , uid, employee_id , img_data , context=None):
        save_path = addons.get_module_resource('GDS', 'static/src/img/emp_images')
        img_name = str(employee_id)+'_'+str(datetime.datetime.now())+".png"
        fileTosave = save_path+"/"+img_name
        fh = open(fileTosave, "wb")
        fh.write(img_data.decode('base64'))
        fh.close()
        val = '/GDS/static/src/img/emp_images/'+img_name
        #self.remove_image(cr, uid , [employee_id])
        self.pool.get("hr.employee").write(cr , uid , [employee_id] , {'image_lc' : val})
        return True



    def remove_image(self , cr , uid , ids , context={}):
        save_path = addons.get_module_resource('GDS', 'static/src/img/emp_images')
        for employee in self.pool.get('hr.employee').read(cr,uid , ids , ['image_lc']):
            employee_image = employee['image_lc']
            image_path = save_path + '/'+ employee_image.split('/')[-1]
            try:
                os.remove(image_path)
            except: pass

    def read_img(self, cr, uid,emp_id , finger ,context={}):
        pass


    def load_payments(self, cr, uid, ids, context={}):
        '''payment_record = self.pool.get('payment.record')
        emp_obj = self.browse(cr,uid,ids )[0]

        payment_records = payment_record.search(cr,uid,[('employee_code','=',emp_obj.emp_code)])
        
        for payment_line in payment_records:
            payment_record.write(cr , uid , payment_line , {'employee_id':emp_obj.id})'''
    	
        return True

'''class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
              'comparison_percentage':fields.float('Comparison Percentage'),

    }
'''

'''class hr_config_settings_inherit(osv.osv_memory):

    _inherit = 'hr.config.settings'
    _columns = {
              'comparison_percentage':fields.related('company_id','comparison_percentage',type='float', string='Comparison Percentage',store=True),
              }

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        """Method that updates related fields of the company.
           @param company_id: Id of company
           @return: Dictionary of values 
        """
        values =super(hr_config_settings_inherit,self).onchange_company_id(cr, uid, ids, company_id, context=context)
        #values = {}
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            values['value']['comparison_percentage']=company.comparison_percentage
            
        return values
'''

'''class hr_config_settings(osv.osv_memory):

    _inherit = 'hr.config.settings'

    _columns = {
              'comparison_percentage' :fields.integer("Comparison Percentage", required= True),
    }

    def get_default_comparison_percentage(self, cr, uid, fields, context=None):
        return {'age_pension': 50}

    def set_default_age_pension(self, cr, uid, ids, context=None):
        company_obj= self.pool.get('res.company')
        config = self.browse(cr, uid, ids[0], context)
        age_pension= config and config.age_pension
        company_ids = company_obj.search(cr,uid,[])
        company_obj.write(cr, uid, company_ids, {'age_pension': age_pension})
        return True
'''
