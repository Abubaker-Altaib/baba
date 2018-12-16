# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
import tools
from osv import osv, fields, orm
import decimal_precision as dp
from tools.translate import _
import netsvc


class a(osv.osv):

	def onchange_category(self , cr, uid , ids ,context=None) :
		  """
		   Onchange category load the image to item 

		  @return: 
				"""
                  custody_ids = self.pool.get('custody.custody').search(cr,uid,[('active' , '=' , True)])

                  for rec in self.pool.get('custody.custody').browse(cr ,uid ,custody_ids):
		      category_image = self.pool.get('custody.category').browse(cr , uid , [rec.category_id.id]).image
		      self.write(cr , uid , ids , { 'image_medium' : category_image } ,context=context )

		  return True
