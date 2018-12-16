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
import datetime
import os

class hr_employee_inhirit(osv.osv):
    _inherit = "hr.employee"
    _columns = {
        'image_attach': fields.char("image"),

    }

    #def _get_default_image(self, cr, uid, context=None):
    #    image_path = addons.get_module_resource('image_attach', 'static/src/img', 'fingerPrint.png')
    #    return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))
    def _get_default_image(self, cr, uid, context=None):
        image_path = addons.get_module_resource('hr', 'static/src/img', 'default_image.png')
        #return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))
        return image_path








    def clean(self , *files):
        
        save_path = addons.get_module_resource('image_attach', 'static/src/img/')
        for i in files :
            os.popen(''' 
            rm %s%s
         '''%(save_path,i))



    def set_image_local(self , cr , uid, employee_id , img_data , context=None):
        print "Employee>>>>>>>>>>>>>>>>>>>>>>>>",employee_id
        print "Self>>>>>>>>>>>>>>>>>>>>>>>>", self
        print "Context>>>>>>>>>>>>>>>>>>>>>>>>", context
        save_path = addons.get_module_resource('image_attach', 'static/src/img/emp_images')
        img_name = str(employee_id)+'_'+str(datetime.datetime.now())+".png"
        fileTosave = save_path+"/"+img_name
        fh = open(fileTosave, "wb")
        fh.write(img_data.decode('base64'))
        fh.close()
        val = '/image_attach/static/src/img/emp_images/'+img_name
        #self.remove_image(cr, uid , [employee_id])
        print "Path>>>",val
        if employee_id != 'null':
           cr.execute("update hr_employee set image_attach='"+val+"' where  id='"+str(employee_id)+"'")
        #result = cr.fetchone()
        #self.pool.get("hr.employee").write(cr , uid , [employee_id] , {'image_lc2' : val})
        return val



    def remove_image(self , cr , uid , ids , context={}):
        save_path = addons.get_module_resource('image_attach', 'static/src/img/emp_images')
        for employee in self.pool.get('hr.employee').read(cr,uid , ids , ['image_lc']):
            employee_image = employee['image_lc']
            image_path = save_path + '/'+ employee_image.split('/')[-1]
            try:
                os.remove(image_path)
            except: pass

    def read_img(self, cr, uid,emp_id , finger ,context={}):
        pass


