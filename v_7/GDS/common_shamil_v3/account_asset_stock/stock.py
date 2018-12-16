# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields
from tools.translate import _
import time
from lxml import etree

#----------------------------------------------------------
# product_product (Inherit)
#----------------------------------------------------------


class product_product(osv.Model):

    _inherit = "product.product"

    _columns = {
        'asset': fields.boolean('Asset'),
        'asset_category_id': fields.many2one('account.asset.category', 'Asset Category'),
        'asset_location_id': fields.many2one('account.asset.location', 'Asset Location'),
        'Asset_id': fields.one2many('account.asset.asset', 'product_id', 'Asset', readonly=True),
        'is_serializable': fields.boolean('Serializable'),
    }

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        ids = []
        if 'picking_out_assets' in context and 'picking_id' in context:
            for move in context['move_ids']:
                if move[2] and move[2]['product_id']: 
                    ids.append(move[2]['product_id'])
            args.append(('id', 'in', ids))

        return super(product_product, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)

#----------------------------------------------------------
# stock_location (Inherit)
#----------------------------------------------------------


class stock_location(osv.Model):

    _inherit = "stock.location"

    _columns = {
        'is_serializable': fields.boolean('Serializable'),
    }


#----------------------------------------------------------
# product_category (Inherit)
#----------------------------------------------------------


class product_category(osv.Model):

    _inherit = "product.category"

    _columns = {
        'is_serializable': fields.boolean('Serializable'),
    }


class stock_line_copy(osv.Model):
    _name = "stock.partial.picking.line.copy"

    _columns = {
        'product_id': fields.integer('Product'),
        'quantity': fields.integer('Quantity'),
        'picking_id': fields.many2one('stock.partial.picking.copy', 'Picking', ondelete='CASCADE'),
        'serials': fields.many2many('stock.partial.picking.line.serail', 'lines_serials_copy_rel2', 'line_id', 'serial_id', string='Serials', ondelete='CASCADE'),
    }


class stock_line_serail(osv.Model):
    _name = "stock.partial.picking.line.serail"
    _rec_name = "name"
    _columns = {
        'name': fields.char('Serial', required=True),
    }

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _('The Name Must Be Unique For Each Serial!')),
    ]



class stock_partial_picking_copy(osv.Model):
    _name = "stock.partial.picking.copy"

    _columns = {
        'date': fields.datetime('Date'),
        'move_ids': fields.one2many('stock.partial.picking.line.copy', 'picking_id', 'Product Moves'),
        'picking_id': fields.many2one('stock.picking', 'Picking', ondelete='CASCADE'),
    }

#----------------------------------------------------------
# stock_partial_picking_asset
#----------------------------------------------------------


class stock_partial_picking_asset(osv.osv_memory):
    _name = "stock.partial.picking.asset"
    _description = "Exchange Picking Processing Wizard"

    def _is_serial(self, cr, uid, ids, name, args, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.product_id.is_serializable:
                result[rec.id] = True
            else:
                result[rec.id] = False
        return result

    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'asset_id': fields.many2one('account.asset.asset', 'Asset'),
        'serial': fields.char('Serial Number', size=256),
        'office_id': fields.many2one('office.office', string='office'),
        'picking_id': fields.many2one('stock.picking', 'Stock Order'),
        'stock_partial_id': fields.many2one('stock.partial.picking', 'Stock Order'),
        'is_serializable': fields.function(_is_serial, type="boolean", string='Serializable'),
        'stock_move_id': fields.many2one('stock.move', 'Stock Move'),
        #'stock_out_asset_id': fields.many2one('stock.picking.out.asset','Stock Out Asset'),
    }

    def onchange_asset(self, cr, uid, ids, asset_id, product_id, context={}):
        """
        Method returns the default serial based on given asset_id
        """
        asset_obj = self.pool.get('account.asset.asset')
        if asset_id and product_id:
            return {'value': {'serial': asset_obj.browse(cr, uid, asset_id).serial}}
        return {'value': {}}

    def onchange_product(self, cr, uid, ids, product_id, context={}):
        """
        Method returns change other field to False when product_id changed
        """
        is_serializable = False
        if product_id:
            is_serializable = self.pool.get('product.product').browse(cr,uid,product_id).is_serializable
        return {'value': {'serial': False, 'asset_id': False, 'office_id': False,'is_serializable':is_serializable}}

    def onchange_serial(self, cr, uid, ids, serial, product_id, picking_out_assets, context={}):
        """
        Method returns the default asset_id based on the given serial
        """
        asset_obj = self.pool.get('account.asset.asset')
        asset_ids = []
        value = []
        if serial and product_id:
            idss = []
            st=['released','draft']
            for asset_line in picking_out_assets:
                if asset_line[2] and asset_line[2]['asset_id']: 
                    idss.append(asset_line[2]['asset_id'])
            asset_ids = asset_obj.search(
                cr, uid, [('product_id', '=', product_id), ('serial', '=', serial), ('id','not in',idss),('state_rm','in',st)])
        if asset_ids:
            return {'value': {'asset_id': asset_ids[0]}}
        else:
            raise osv.except_osv(_('Error!'), _(
                'this serial is already delivered  ') )
 
        return {'value': {'asset_id': False}}


#----------------------------------------------------------
# Stock Picking Out Asset
#----------------------------------------------------------

class stock_picking_out_asset(osv.Model):
    _name = "stock.picking.out.asset"

    def _is_serial(self, cr, uid, ids, name, args, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.product_id.is_serializable:
                result[rec.id] = True
            else:
                result[rec.id] = False
        return result

    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'asset_id': fields.many2one('account.asset.asset', 'Asset'),
        'serial': fields.char('Serial Number', size=256),
        'office_id': fields.many2one('office.office', string='office'),
        'picking_id': fields.many2one('stock.picking', 'Stock Order'),
        #'stock_partial_id': fields.many2one('stock.partial.move','Stock Order'),
        'is_serializable': fields.function(_is_serial, type="boolean", string='Serializable'),
        'stock_move_id': fields.many2one('stock.move', 'Stock Move'),
        'state': fields.selection([('draft', 'Draft'), ('delivered', 'Delivered')], 'State',  select=True),

    }

    _defaults = {
        'state': 'draft',
    }

    def onchange_asset(self, cr, uid, ids, asset_id, product_id, context={}):
        """
        Method returns the default serial basedon given asset_id
        """
        asset_obj = self.pool.get('account.asset.asset')
        if asset_id and product_id:
            return {'value': {'serial': asset_obj.browse(cr, uid, asset_id).serial}}
        return {'value': {}}

    def onchange_serial(self, cr, uid, ids, serial, product_id, context={}):
        """
        Method returns the default asset_id based on the given serial
        """
        asset_obj = self.pool.get('account.asset.asset')
        asset_ids = []
        value = []
        if serial and product_id:
            asset_ids = asset_obj.search(
                cr, uid, [('product_id', '=', product_id), ('serial', '=', serial)])
        if asset_ids:
            return {'value': {'asset_id': asset_ids[0]}}
        return {'value': {'asset_id': False}}


class stock_partial_picking_line(osv.TransientModel):
    _inherit = "stock.partial.picking.line"

    _columns = {
        'serials': fields.many2many('stock.partial.picking.line.serail', 'line_serials_rel', 'line_id', 'serial_id', string='Serials', ondelete='CASCADE'),
        'type': fields.char(string='Type', store=True),
    }


class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"

    def _partial_asset_out_for(self, cr, uid, picking_out_assets, move_ids, picking_id, context=None):
        partial_asset_list = []
        picking_out_asset = self.pool.get('stock.picking.out.asset')
        for m in move_ids:
            product = self.pool.get('product.product').browse(
                cr, uid, m['product_id'])
            picking_asset_idss = picking_out_asset.search(cr, uid, [('stock_move_id', '=', m['move_id']),
                                                                    ('state', '=', 'draft'), ('picking_id', '=', picking_id)], context=context)
            if picking_asset_idss:
                for line in picking_out_asset.browse(cr, uid, picking_asset_idss):
                    partial_asset_move = {
                        'product_id': line.product_id.id,
                        'picking_id': line.picking_id.id,
                        'office_id': line.office_id.id,
                        'asset_id': line.asset_id.id,
                        'stock_move_id': line.stock_move_id.id,
                        'serial': line.serial,
                    }
                    partial_asset_list.append(partial_asset_move)
            else:
                for x in range(0, int(m['quantity'])):
                    partial_asset_move = {
                        'product_id': m['product_id'],
                        #'picking_id': picking_id,
                        'office_id': False,
                        'asset_id': False,
                        'stock_move_id': m['move_id'],
                        'serial': False,
                        'is_serializable': product.is_serializable,
                    }
                    partial_asset_list.append(partial_asset_move)
        return partial_asset_list

    def check_asset_lines(self, cr, uid, ids, context=None):
        """
        Method that check if office and serial and asset
        """
        for rec in self.browse(cr, uid, ids, context):
            if rec.picking_out_assets:
                for line in rec.picking_out_assets:
                    if line.product_id.is_serializable and not line.serial:
                        raise osv.except_osv(_('Error!'), _(
                            'Please enter office or asset for asset line with product %s ') % (line.product_id.name))
                     

    def all_int(self, l):
        for i in l:
            if type(i) != int:
                return False
        return True

    def onchange_move_ids(self, cr, uid, ids, move_ids, context=None):
        new_move_ids = []
        for move in move_ids:
            if move[2]:
                if 'serials' in move[2]:

                    if True:
                        if self.all_int(move[2]['serials']):
                            move[2]['serials'] = [
                                [6, False, move[2]['serials']]]
            new_move_ids.append(move)
        return {
            'value': {
                'move_ids': new_move_ids
            },
        }

    def do_partial(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context):
            lines = []
            if rec.picking_id.type != 'in' :
                continue
            for line in rec.move_ids:
                if line.product_id.is_serializable and not rec.picking_id.stock_journal_id.need_visit :
                    if len(line.serials) != line.quantity:
                        raise osv.except_osv(_('Sorry!'),
                                             _('Please set the right Serials for the product %s ' % (line.product_id.name,)))

            context['do_partial'] = True
        picking_out_asset = self.pool.get('stock.picking.out.asset')
        self.save(cr, uid, ids, context=context)
        value = super(stock_partial_picking, self).do_partial(
            cr, uid, ids, context=context)
        
        if not rec.picking_id.stock_journal_id.need_visit:
            self.create_asset(cr, uid, ids, context=None)

        try:
            copy_obj = self.pool.get('stock.partial.picking.copy')
            is_exist = copy_obj.search(
                cr, uid, [('picking_id', '=', context['active_id'])])
            copy_obj.unlink(cr, uid, is_exist)
        except:
            pass
        return value

    def default_get(self, cr, uid, fields, context=None):
        value = super(stock_partial_picking, self).default_get(
            cr, uid, fields, context=context)
        if context and 'active_ids' in context and len(context['active_ids']) == 1 and 'move_ids' in value:
            copy_obj = self.pool.get('stock.partial.picking.copy')
            line_obj = self.pool.get('stock.partial.picking.line')
            product_obj = self.pool.get('product.product')
            is_exist = copy_obj.search(
                cr, uid, [('picking_id', 'in', context['active_ids'])])
            if is_exist:
                is_exist = is_exist[0]
                is_exist = copy_obj.browse(cr, uid, is_exist, context=context)
                old_values = {i['product_id']: (i['quantity'], i['serials'])
                              for i in is_exist.move_ids}
                for move in value['move_ids']:
                    if move['product_id'] in old_values.keys():
                        move['quantity'] = old_values[move['product_id']][0]
                        move['serials'] = [
                            i.id for i in old_values[move['product_id']][1]]

            for move in value['move_ids']:
                move['type'] = context['default_type']
                is_serializable = product_obj.read(
                    cr, uid, move['product_id'], ['is_serializable'])
                is_serializable = ['is_serializable']
                if not is_serializable:
                    move['type'] = 'not'

            ####################### for picking out############
            picking = self.pool.get('stock.picking').browse(
                cr, uid, context['active_ids'][0], context=context)
            asset_moves = self._partial_asset_out_for(
                cr, uid, picking.picking_out_assets, value['move_ids'], picking.id, context=context)
            value.update(picking_out_assets=asset_moves)
            value.update(type=picking.type)
        return value

    def save(self, cr, uid, ids, context=None):
        copy_obj = self.pool.get('stock.partial.picking.copy')
        is_exist = copy_obj.search(
            cr, uid, [('picking_id', 'in', context['active_ids'])])
        copy_obj.unlink(cr, uid, is_exist)
        copy_obj = self.pool.get('stock.partial.picking.copy')
        asset_partial_obj = self.pool.get('stock.partial.picking.asset')
        picking_out_asset = self.pool.get('stock.picking.out.asset')

        for rec in self.browse(cr, uid, ids, context):
            lines = []
            asset_lines = [x.id for x in rec.picking_out_assets]
            for line in rec.move_ids:
                move_line = line
                serials = [(4, i.id, False) for i in line.serials]
                lines.append(
                    (0, 0, {"product_id": line.product_id, "quantity": line.quantity, 'serials': serials}))

                ################# for picking out assets ##############

                if move_line.product_id.custody and rec.type == 'out':
                    unlink_idss = asset_partial_obj.search(cr, uid, [(
                        'stock_move_id', '=', move_line.move_id.id), ('id', 'not in', asset_lines)])
                    asset_partial_obj.unlink(cr, uid, unlink_idss)
                    idss = asset_partial_obj.search(
                        cr, uid, [('stock_move_id', '=', move_line.move_id.id)])
                    asset_line_dic = []
                    if (not idss and move_line.quantity > 0) or (len(idss) != int(move_line.quantity)):
                        raise osv.except_osv(_('Error'), _(
                            'The product %s should has asset lines equal to its recieved quantity') % (move_line.product_id.name))

                    else:
                        self.check_asset_lines(cr, uid, ids, context=context)
                        picking_asset_idss = picking_out_asset.search(cr, uid, [('stock_move_id', '=', move_line.move_id.id),
                                                                                ('state', '=', 'draft')], context=context)
                        if picking_asset_idss:
                            picking_out_asset.unlink(
                                cr, uid, picking_asset_idss)

                        for asset_line in asset_partial_obj.browse(cr, uid, idss):
                            asset_line_dic = {
                                'product_id': asset_line.product_id.id,
                                'picking_id': context['active_ids'][0],
                                'office_id': asset_line.office_id.id,
                                'asset_id': asset_line.asset_id.id,
                                'stock_move_id': asset_line.stock_move_id.id,
                                'serial': asset_line.serial,
                                'state': 'draft',
                            }
                            """if 'do_partial'in context and context['do_partial']:
                                asset_line_dic['state'] = 'delivered'"""

                            picking_out_asset.create(
                                cr, uid, asset_line_dic, context=context)

            copy_obj.create(cr, uid, {'picking_id': rec.picking_id.id,
                                      'move_ids': lines})

        return True

    def un_save(self, cr, uid, ids, context=None):
        copy_obj = self.pool.get('stock.partial.picking.copy')
        is_exist = copy_obj.search(
            cr, uid, [('picking_id', '=', context['active_id'])])
        copy_obj.unlink(cr, uid, is_exist)
        return True

    def create_asset(self, cr, uid, ids, context=None):
        asset_ids = []
        asset_obj = self.pool.get('account.asset.asset')
        asset_history_obj = self.pool.get('account.asset.history')
        asset_custody_obj = self.pool.get('asset.custody')
        product_obj = self.pool.get('product.product')
        asset_custody_line_obj = self.pool.get('asset.custody.line')
        name = ''
        for rec in self.browse(cr, uid, ids, context):
            if rec.picking_id.type != 'in':
                continue
            #name = rec.product_id.name
            for line in rec.move_ids:
                if line.product_id.custody:
                    serials = [x.name for x in line.serials]
                    if not (line.product_id.asset_category_id or line.product_id.asset_location_id):
                        raise osv.except_osv(_('Sorry!'),
                                             _('Please set the asset category and location for the product %s ' % (line.product_id.name,)))
                    for new_asset in range(0, int(line.quantity)):
                        # add +1 for naming perpose
                        asset_id = asset_obj.create(cr, uid, {'name': line.product_id.name + str(new_asset + 1),
                                                              'category_id': line.product_id.asset_category_id.id,
                                                              'purchase_date': time.strftime('%Y-%m-%d'),
                                                              'state': 'confirmed',
                                                              'state_rm': 'draft',
                                                              'asset_type': 'custody',
                                                              'location_id': line.product_id.asset_location_id.id,
                                                              'product_id': line.product_id.id,
                                                              'stock_location_id': line.location_id.id,
                                                              'serial': line.product_id.is_serializable and serials[new_asset] or False,
                                                              'asset_log_ids': [(0, 0, {'date': time.strftime('%Y-%m-%d'),
                                                                                        'state': 'purchase',                                                      'picking_id':rec.picking_id.id,
                                                                                        })],
                                                              'executing_agency':rec.picking_id.executing_agency,
                                                              'custody_type':rec.picking_id.custody_type,
                                                              'request_date':rec.picking_id.date_done,
                                                              'time_scale':'constant',
                                                              'picking_id':rec.picking_id.id,
                                                              }, context=context)
                        asset_ids.append(asset_id)
                        # asset_history_obj.create(cr, uid, {'type': 'initial',
                        #                                    'asset_id': asset_id,
                        #                                    'state': 'draft',
                        #                                    }, context=context)

        # if len(asset_ids) >= 1:
        #     custody_id = asset_custody_obj.create(cr, uid, {
        #         'name': name,
        #         'type': 'request',
        #         'stock': 'True',
        #         'date': time.strftime('%Y-%m-%d'),
        #         #'custody_type': rec.custody_type,
        #     })

            return True

    _columns = {
        'picking_out_assets': fields.one2many('stock.partial.picking.asset', 'stock_partial_id', 'Assets'),
        'type': fields.selection([('in', 'In'), ('out', 'Out'), ('internal', 'Internal')], 'Type'),

    }


#----------------------------------------------------------
# Stock Picking (Inherit)
#----------------------------------------------------------

class stock_picking(osv.Model):

    _inherit = "stock.picking"

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        res = super(stock_picking, self).do_partial(
            cr, uid, ids, partial_datas, context=None)
        #self.create_asset(cr, uid, ids, context=None)
        self.update_asset(cr, uid, ids, context=None)

        return res

    def update_asset(self, cr, uid, ids, context=None):
        asset_ids = []
        custody_ids = []
        asset_obj = self.pool.get('account.asset.asset')
        asset_history_obj = self.pool.get('account.asset.history')
        asset_custody_obj = self.pool.get('asset.custody')
        product_obj = self.pool.get('product.product')
        asset_custody_line_obj = self.pool.get('asset.custody.line')
        asset_log_obj = self.pool.get('asset.log')
        picking_out_asset = self.pool.get('stock.picking.out.asset')
        name = ''
        for rec in self.browse(cr, uid, ids, context):

            if rec.type != 'out':
                return
            name = rec.name
            for asset_line in rec.picking_out_assets:
                if asset_line.state == 'draft' and asset_line.is_serializable:
                    write_dict = {
                        'office_id': asset_line.office_id.id,
                        'department_id': rec.department_id and rec.department_id.id or False,
                        'employee_id': rec.employee_to and rec.employee_to.id or False,
                        'state_rm': 'assigned',
                        'custody_type': rec.custody_type,
                        'request_date': rec.date,
                        'picking_id': rec.id,
                    }
                    log_dict = {
                        'date': rec.date,
                        'picking_id':rec.id,
                        'department_id': rec.department_id and rec.department_id.id or False,
                        'employee_id': rec.employee_to and rec.employee_to.id or False,
                        'asset_id': asset_line.asset_id and asset_line.asset_id.id or False,
                        'office_id': asset_line.office_id and asset_line.office_id.id or False,
                        'state': 'recieved'
                    }

                    asset_obj.write(cr, uid, [asset_line.asset_id.id], write_dict, context=context)
                    asset_log_obj.create(cr, uid, log_dict, context=context)
                    asset_custody_obj.create(cr, uid, {
                        'name': name,
                        'type': 'request',
                        'stock': 'True',
                        'date': time.strftime('%Y-%m-%d'),
                        'custody_type': asset_line.asset_id.custody_type,
                    })

                    picking_out_asset.write(cr, uid, [asset_line.id], {'state': 'delivered'})

        return True

    def create_asset(self, cr, uid, ids, context=None):
        asset_ids = []
        custody_ids = []
        asset_obj = self.pool.get('account.asset.asset')
        asset_history_obj = self.pool.get('account.asset.history')
        asset_custody_obj = self.pool.get('asset.custody')
        product_obj = self.pool.get('product.product')
        asset_custody_line_obj = self.pool.get('asset.custody.line')
        name = ''
        for rec in self.browse(cr, uid, ids, context):

            if rec.type != 'out':
                return
            name = rec.name
            for line in rec.move_lines:
                if line.product_id.asset:
                    if not (line.product_id.asset_category_id or line.product_id.asset_location_id):
                        raise osv.except_osv(_('Sorry!'),
                                             _('Please set the asset category and location for the product %s ' % (line.product_id.name,)))
                    for new_asset in range(1, int(line.product_uos_qty + 1)):
                        asset_id = asset_obj.create(cr, uid, {'name': line.product_id.name + str(new_asset),
                                                              'category_id': line.product_id.asset_category_id.id,
                                                              'purchase_date': time.strftime('%Y-%m-%d'),
                                                              'state': 'draft',
                                                              'state_rm': 'assigned',
                                                              'asset_type': 'custody',
                                                              'location_id': line.product_id.asset_location_id.id,
                                                              'product_id': line.product_id.id,
                                                              'stock_location_id': line.location_id.id,
                                                              }, context=context)
                        asset_ids.append(asset_id)
                        asset_history_obj.create(cr, uid, {'type': 'initial',
                                                           'asset_id': asset_id,
                                                           'state': 'draft',
                                                           }, context=context)
                        custody_id = asset_custody_obj.create(cr, uid, {
                            'name': name,
                            'type': 'request',
                            'stock': 'True',
                            'date': time.strftime('%Y-%m-%d'),
                            'custody_type': asset_obj.browse(cr, uid, asset_id).custody_type,
                        })
                        custody_ids.append(custody_id)

            return custody_ids
        '''if len(asset_ids) >= 1:
            custody_id = asset_custody_obj.create(cr, uid, {
                'name': name,
                'type': 'request',
                'stock': 'True',
                'date': time.strftime('%Y-%m-%d'),
                'custody_type': rec.custody_type,
            })

            return custody_id'''

    _columns = {
        'picking_out_assets': fields.one2many('stock.picking.out.asset', 'picking_id', 'Assets'),

    }


#----------------------------------------------------------
# Stock Picking Out (Inherit)
#----------------------------------------------------------


class stock_picking_out(osv.Model):

    _inherit = "stock.picking.out"

    _columns = {
        'picking_out_assets': fields.one2many('stock.picking.out.asset', 'picking_id', 'Assets'),

    }

#---------------------------------
# exchange order (Inherit)
#---------------------------------


class exchange_order(osv.Model):
    _inherit = "exchange.order"

    '''def _prepare_order_line_move(self, cr, uid, order, line, picking_id,product_qty ,context=None):
        """
        Prepare the dict of values to create the new stock move for a
        exchange order line. This method may be overridden to implement custom
        move generation (making sure to call super() to establish a clean extension chain).
        @param browse_record order: exchange.order record 
        @param browse_record line: exchange.order.line record 
        @param int picking_id: ID of stock  picking 
        @param product_qty : product qty(this is used for returning products including service)
        @return: dict of values to create() the stock move
        """

        res = super(exchange_order, self)._prepare_order_line_move(cr, uid, order, line, picking_id,product_qty ,context=None)
        print "---------------_prepare_order_line_move22222211111111111111",line.product_id.custody
        if line.product_id.custody and order.ttype == 'other' :
            print "---------------_prepare_order_line_move222222", range(0,int(product_qty)), int(picking_id)
            asset_picking_dict = {
                'product_id': line.product_id.id,
                'picking_id': int(picking_id),
                'office': False,
                'asset_id': False,
            }
            #frac,whole = math.mod(product_qty)
            piching_out_asset_obj = self.pool.get('stock.picking.out.asset')
            for x in range(0,int(product_qty)):
                print "-----------------x", x, asset_picking_dict
                piching_out_asset_obj.create(cr, uid, asset_picking_dict, context=context)
        return res'''


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
