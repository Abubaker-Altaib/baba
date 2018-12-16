# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from datetime import datetime
from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp import netsvc

#--------------------------------------------------
# Sale Order Class Inherit
#--------------------------------------------------
class sale_order(osv.osv): 
    """Inherited to add archive_picking_ids many2many field to the sale"""
    _inherit = "sale.order"
    _columns = {
      'archive_picking_id': fields.many2one('stock.picking','Arhcived Pickings', readonly=True),
    }

#--------------------------------------------------
# Stock Picking Class Inherit
#--------------------------------------------------
class stock_archive(osv.osv): 
    """Inherited to add archive_id field to the Picking"""
    _inherit = "stock.picking"
    _columns = {
        'archive_id': fields.many2one('stock.archive','Archive'),
    }

#---------------------------------------------------
# Stock Archive Class
#---------------------------------------------------
class stock_archive(osv.osv): 
    """This model group many stock picking and replace by one picking"""
    _name = "stock.archive"
    _description = "Stock Picking Archiving"

    _columns = {
        'name': fields.char('Name', size=256, readonly=True, ),
        'description': fields.char('Description', size=256, readonly=True, states={'draft':[('readonly', False)]}),
        'date': fields.date('Date'),
        'sale_only': fields.boolean('Sale Only',readonly=True, states={'draft': [('readonly', False)]}),      
        'location_id': fields.many2one('stock.location','Location', readonly=True, states={'draft':[('readonly', False)]}),
        'date_from': fields.date('Date From', readonly=True, states={'draft':[('readonly', False)]},),
        'date_to': fields.date('Date To', readonly=True, states={'draft':[('readonly', False)]},),
        'picking_ids': fields.many2many('stock.picking','stock_archive_picking_id_rel', 'stock_archive_id', 'picking_id','Picking',),
        'new_picking_ids': fields.one2many('stock.picking', 'archive_id', 'New Picking'),       
        'picking_state': fields.selection([('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancelled')], 'Picking State' , readonly=True, states={'draft':[('readonly', False)]}),
        'picking_type': fields.selection([('out', 'Out Picking'), ('in', 'In Picking'), ('internal', 'Internal')], 'Picking Type' , readonly=True, states={'draft':[('readonly', False)]}),
        'state': fields.selection([('draft','Draft'),('confirmed','Confirmed'), ('done','Done'), ('cancel', 'Cancelled')], 'State', readonly=True, select=True),
        'summary': fields.text('Summary'),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
    }

    _defaults = {
        'name':'/',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'picking_type': 'out',
        'state': 'draft',
        'sale_only':True,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'stock.archive', context=c)
    }

    def get_picking(self, cr, uid, ids, context=None):
        """
        Get All picking belong to archive criteria
        @return: dictionary of values
        """
        if context is None:
            context = {}
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        for record in self.browse(cr, uid, ids, context):
            #Make date_to time at last hour in date
            date_to = datetime.strptime(record.date_to,'%Y-%m-%d')
            domain =[('type', '=', record.picking_type), ('date','>=', record.date_from ),('date','<=', record.date_to)]
            if record.picking_state in ('cancel', 'done'):
                domain.append(('state','=', record.picking_state))
            elif record.picking_state == 'draft':
                domain.append(('state','not in', ('cancel', 'done')))
            first_picking_ids = picking_obj.search(cr, uid , domain , context=context)
            if not first_picking_ids:
                #Skip this loop and start from begining
                continue
            query_condition = ""
            if record.sale_only:
                query_condition += " AND p.sale_id IS NOT NULL "
            #Get Seleted picking from stock move with location id = archive location id
            cr.execute("""select distinct(p.id) AS picking_id
			  FROM stock_move m,stock_picking p
			  WHERE m.picking_id = p.id """ + query_condition + """
			  AND m.location_id =%s 
                          AND p.id in %s
			  """,(record.location_id.id, tuple(first_picking_ids), ) )
            res = cr.dictfetchall()
            picking_ids = [line['picking_id'] for line in res]
            self.write(cr, uid, [record.id],{'picking_ids':[(5, 0, [picking.id for picking in record.picking_ids])]})
            if picking_ids:
                self.write(cr, uid, ids,{'picking_ids':[(6, 0, picking_ids)]})

        return True

    def _prepare_order_line_move(self, cr, uid, order,state, move, picking_id, context=None):
        return {
            'name'         : order.name,
            'picking_id'   : picking_id,
            'product_id'   : move['product_id'],
            'date'         : order.date_to,
            'date_expected': order.date_to,
            'product_qty'  : move['product_qty'],
            'product_uom'  : move['product_uom'],
            'product_uos_qty': move['product_qty'],
            'product_uos'  : move['product_uom'],
            'location_id'  : order.location_id.id,
            'location_dest_id': move['location_dest_id'],
            'state'        : state,
            'company_id': order.company_id.id,
            #'price_unit': line.product_id.standard_price or 0.0
        }

    def _prepare_order_picking(self, cr, uid, order, state, context=None):
        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
        return {
            'name': pick_name,
            'origin': order.name,
            'date': order.date_to,
            'type': order.picking_type,
            'state': state,
            #'move_type': order.picking_pstock_multi_company/solicy,
            'archive_id': order.id,
	    #'stock_journal_id':18,
            #'note': order.note,
            'company_id': order.company_id.id,
        }

    def archive_picking(self, cr, uid, ids, context=None):
        """
        group many Archive picking and replace by one picking
        @return: dictionary of values
        """
        if context is None:
            context = {}
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        sale_obj = self.pool.get('sale.order')
        wf_service = netsvc.LocalService("workflow")
        for record in self.browse(cr, uid, ids, context):
            if not record.picking_ids:
                raise osv.except_osv(_('Error!'),_('You cann\'t generate archive without stock picking'))
            picking_group = []
            draft_picking = [picking.id for picking in record.picking_ids if picking.state not in ('cancel','done')]
            done_picking = [picking.id for picking in record.picking_ids if picking.state == 'done']
            cancel_picking = [picking.id for picking in record.picking_ids if picking.state == 'cancel']
            picking_group.append((draft_picking,'draft'))
            picking_group.append((done_picking,'done'))
            picking_group.append((cancel_picking,'cancel'))
            picking_ids= [picking.id for picking in record.picking_ids] 
            for picking_ids in picking_group:
                sale_list = picking_obj.read(cr,uid, picking_ids[0],['sale_id'],context )
                sale_ids = [line['sale_id'][0] for line in sale_list if line['sale_id']]
                move_ids = move_obj.search(cr, uid, [('picking_id' , 'in', picking_ids[0])], context=context)
                if move_ids:
                    cr.execute(""" select product_id, sum(product_qty) As product_qty, product_uom, location_dest_id
				   FROM stock_move 
				   WHERE id in %s
				   Group by product_id, product_uom, location_dest_id  """,(tuple(move_ids),))
                    res = cr.dictfetchall()
                    picking_id = picking_obj.create(cr, uid, self._prepare_order_picking(cr, uid, record, picking_ids[1],  context=context))
                    for move in res:
                        move_id = move_obj.create(cr, uid, self._prepare_order_line_move(cr, uid, record, picking_ids[1], move, picking_id, context=context))
                    if sale_ids:
                        cr.execute("""update sale_order set archive_picking_id=%s where id in %s""",(picking_id, tuple(sale_ids)))
            self.write(cr, uid, [record.id], {'state': 'confirmed'}, context)

        return True

    def set_to_draft(self, cr, uid, ids, context=None):
	"""
        Set Status field to draft
        @return: True
        """
        for record in self.browse(cr, uid, ids, context):
            self.write(cr, uid, [record.id], {'state': 'draft'}, context)
            picking_ids = [picking.id for picking in record.new_picking_ids]
            cr.execute(""" update stock_picking set state = 'draft' where id in %s  """,(tuple(picking_ids),))
            self.pool.get('stock.picking').unlink(cr, uid, picking_ids, context)
        return True

    def unlink_picking(self, cr, uid, ids, context=None):
	"""
        Remove_old_picking
        @return: True
        """
        picking_obj = self.pool.get('stock.picking')
        for record in self.browse(cr, uid, ids, context):
            picking_ids = [picking.id for picking in record.picking_ids]
            #Summarize of these picking before delete it
            res = {}
            picking_data = picking_obj.read(cr, uid, picking_ids ,['name'], context)
            for line in picking_data:
                res.update({line['id']:line['name']})
            self.write(cr, uid, [record.id], {'state': 'done', 'summary': str(res)}, context)
            cr.execute(""" update stock_picking set state = 'draft' where id in %s  """,(tuple(picking_ids),))
            #self.pool.get('stock.picking').unlink(cr, uid, picking_ids, context)
            cr.execute("""delete from stock_move where picking_id in %s """,(tuple( picking_ids), ))
            cr.execute("""delete from stock_picking where id in %s """,(tuple( picking_ids), ))

        return True

    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  self._name
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        new_id = super(stock_archive, self).create(cr, user, vals, context)
        return new_id


