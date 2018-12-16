# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

import openerp
from openerp import tools
from openerp.modules.module import get_module_resource
from openerp.osv import fields,osv
from openerp.tools.translate import _

from openerp import netsvc

import subprocess
import urllib2
import json



class payment_payment(osv.osv):
    _name = "payment.record"

    _columns = {
    	'employee_id':fields.many2one('hr.employee', 'Employee' ,required=True , domain="[('state','=','approved')]"),
		'date': fields.date('Date', required=True, select=1),
        'hand':fields.selection([('right', 'Right'),
                                   ('left', 'Left'),
                                   ], 'Select hand',
                                   ),
		'finger_print': fields.selection([('thumb', 'Thumb'),#الاإبهام
                                   ('Index', 'Index'),#السبابة
                                   ('middle_finger', 'Middle Finger'),#الوسطى
                                   ('ring_finger', 'Ring Finger'),#البنصر
                                   ('Pinkie', 'Pinkie'),#الخنصر
                                   ], 'Select Finger',
                                   ),


		'department_id': fields.related('employee_id','department_id', type='many2one',relation='hr.department',string ='Department', store=True),
		'state' : fields.selection([('draft', 'Draft'), ('confirm', 'Confirm')  ,  ('received', 'Received'), ('done' , 'Done')],  'Status', required=True),
        'active': fields.boolean('Active'),
        'amount': fields.float('Amount'),
    }

    _defaults = {
        'state': 'draft',
        'active': True,
        'hand' : 'right' , 
        'finger_print':'thumb',
    }

    def _check_amount(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.amount <= 0 :
            return False
        return True

    _constraints = [
        (_check_amount, 'Amount must be Positive value , greater than zero !!', ['amount']),
    ]


    def set_to_draft(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for payment_id in ids:
            wf_service.trg_create(uid, 'payment.record', payment_id, cr)
        self.write(cr, uid, ids, {'state':'draft'})
        return True


    def confirm(self, cr, uid, ids, context={}):
        pay_object = self.browse(cr ,uid , ids )[0]
        finger = str(pay_object.hand)+"_"+str(pay_object.finger_print)
        print "fingeeeeeer ############# " , finger
        return {
            'type' : 'ir.actions.client',
            'tag' : 'finger_auth',
            'params' : {
                'finger' : finger ,
                'employee_id' : pay_object.employee_id.id ,
                'payment_id' : pay_object.id ,
                'state' : 'confirm' ,
            },
        }
        

    def do_receive(self, cr, uid, ids, context={}):
        pay_object = self.browse(cr ,uid , ids )[0]
        finger = str(pay_object.hand)+"_"+str(pay_object.finger_print)
        return {
            'type' : 'ir.actions.client',
            'tag' : 'finger_auth',
            'params' : {
                'finger' : finger ,
                'employee_id' : pay_object.employee_id.id ,
                'payment_id' : pay_object.id ,
                'state' : 'received' ,
            },
        }

    def do_done(self, cr, uid, ids, context={}):
        for rec in self.browse(cr, uid, ids, context):
            rec.write({'state':'done'})
        return True

    '''def Verivecation(self, cr, uid, ids, context=None):
        raise Warning("inside the method ")
        Verivecation = self.pool.get('finger.print').Verivecation(self, cr, uid, ids ,context)
        if Verivecation:
            self.write(cr, uid, ids, {'employee_id': [Verivecation]}, context=context)
        return True 
    '''
