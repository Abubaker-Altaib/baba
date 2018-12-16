# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from datetime import datetime
from dateutil import relativedelta
from itertools import groupby
from operator import itemgetter
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class productCategory(models.Model):
    _inherit = "product.category"

    products_type = fields.Selection([('stationery', 'Stationery'), ('others', 'Others')])


    # @api.constrains('name')
    # def check_category_name(self):
    #     if not all(x.isalpha() or x.isspace() for x in self.name):
    #         raise UserError(_(" Category name should not contains symbols or numbers "))

    _sql_constraints = [('stock_category_name_uniq', 'unique (name)', _('category name must be unique.')),]

class stockMove(models.Model):
    _inherit = "stock.move"

    product_uom = fields.Many2one(
        'product.uom', 'Unit of Measure', required=True, states={'done': [('readonly', True)]})


    @api.constrains('product_uom_qty')
    def positive(self):
        if self.product_uom_qty <= 0.0:
            raise UserError(_("Initial Demand must not be less than one"))

    def _action_assign(self):
        """ Reserve stock moves by creating their stock move lines. A stock move is
        considered reserved once the sum of `product_qty` for all its move lines is
        equal to its `product_qty`. If it is less, the stock move is considered
        partially available.
        """
        assigned_moves = self.env['stock.move']
        partially_available_moves = self.env['stock.move']
        for move in self.filtered(lambda m: m.state in ['confirmed', 'waiting', 'partially_available']):
            if move.location_id.usage in ('supplier', 'inventory', 'production', 'customer') \
                    or move.product_id.type == 'consu':
                # create the move line(s) but do not impact quants
                if move.product_id.tracking == 'serial' and (
                            move.picking_type_id.use_create_lots or move.picking_type_id.use_existing_lots):
                    for i in range(0, int(move.product_qty - move.reserved_availability)):
                        self.env['stock.move.line'].create(move._prepare_move_line_vals(quantity=1))
                else:
                    to_update = move.move_line_ids.filtered(lambda ml: ml.product_uom_id == move.product_uom and
                                                                       ml.location_id == move.location_id and
                                                                       ml.location_dest_id == move.location_dest_id and
                                                                       ml.picking_id == move.picking_id and
                                                                       not ml.lot_id and
                                                                       not ml.package_id and
                                                                       not ml.owner_id)
                    if to_update:
                        to_update[0].product_uom_qty += move.product_qty - move.reserved_availability
                    else:
                        self.env['stock.move.line'].create(
                            move._prepare_move_line_vals(quantity=move.product_qty - move.reserved_availability))
                assigned_moves |= move
            else:
                if not move.move_orig_ids:
                    if move.procure_method == 'make_to_order':
                        continue
                    # Reserve new quants and create move lines accordingly.
                    available_quantity = self.env['stock.quant']._get_available_quantity(move.product_id,
                                                                                         move.location_id)
                    if available_quantity <= 0:
                        continue
                    need = move.product_qty - move.reserved_availability
                    taken_quantity = move._update_reserved_quantity(need, available_quantity, move.location_id,
                                                                    strict=False)

                    if need == taken_quantity:
                        assigned_moves |= move
                    else:
                        partially_available_moves |= move

                else:
                    # Check what our parents brought and what our siblings took in order to
                    # determine what we can distribute.
                    # `qty_done` is in `ml.product_uom_id` and, as we will later increase
                    # the reserved quantity on the quants, convert it here in
                    # `product_id.uom_id` (the UOM of the quants is the UOM of the product).
                    move_lines_in = move.move_orig_ids.filtered(lambda m: m.state == 'done').mapped('move_line_ids')
                    keys_in_groupby = ['location_dest_id', 'lot_id', 'result_package_id', 'owner_id']

                    def _keys_in_sorted(ml):
                        return (ml.location_dest_id.id, ml.lot_id.id, ml.result_package_id.id, ml.owner_id.id)

                    grouped_move_lines_in = {}
                    for k, g in groupby(sorted(move_lines_in, key=_keys_in_sorted), key=itemgetter(*keys_in_groupby)):
                        qty_done = 0
                        for ml in g:
                            qty_done += ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
                        grouped_move_lines_in[k] = qty_done
                    move_lines_out_done = (move.move_orig_ids.mapped('move_dest_ids') - move) \
                        .filtered(lambda m: m.state in ['done']) \
                        .mapped('move_line_ids')
                    # As we defer the write on the stock.move's state at the end of the loop, there
                    # could be moves to consider in what our siblings already took.
                    moves_out_siblings = move.move_orig_ids.mapped('move_dest_ids') - move
                    moves_out_siblings_to_consider = moves_out_siblings & (assigned_moves + partially_available_moves)
                    reserved_moves_out_siblings = moves_out_siblings.filtered(
                        lambda m: m.state in ['partially_available', 'assigned'])
                    move_lines_out_reserved = (reserved_moves_out_siblings | moves_out_siblings_to_consider).mapped(
                        'move_line_ids')
                    keys_out_groupby = ['location_id', 'lot_id', 'package_id', 'owner_id']

                    def _keys_out_sorted(ml):
                        return (ml.location_id.id, ml.lot_id.id, ml.package_id.id, ml.owner_id.id)

                    grouped_move_lines_out = {}
                    for k, g in groupby(sorted(move_lines_out_done, key=_keys_out_sorted),
                                        key=itemgetter(*keys_out_groupby)):
                        qty_done = 0
                        for ml in g:
                            qty_done += ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
                        grouped_move_lines_out[k] = qty_done
                    for k, g in groupby(sorted(move_lines_out_reserved, key=_keys_out_sorted),
                                        key=itemgetter(*keys_out_groupby)):
                        grouped_move_lines_out[k] = sum(
                            self.env['stock.move.line'].concat(*list(g)).mapped('product_qty'))
                    available_move_lines = {key: grouped_move_lines_in[key] - grouped_move_lines_out.get(key, 0) for key
                                            in grouped_move_lines_in.keys()}
                    # pop key if the quantity available amount to 0
                    available_move_lines = dict((k, v) for k, v in available_move_lines.items() if v)

                    if not available_move_lines:
                        continue
                    for move_line in move.move_line_ids.filtered(lambda m: m.product_qty):
                        if available_move_lines.get((move_line.location_id, move_line.lot_id,
                                                     move_line.result_package_id, move_line.owner_id)):
                            available_move_lines[(move_line.location_id, move_line.lot_id, move_line.result_package_id,
                                                  move_line.owner_id)] -= move_line.product_qty
                    for (location_id, lot_id, package_id, owner_id), quantity in available_move_lines.items():
                        need = move.product_qty - sum(move.move_line_ids.mapped('product_qty'))
                        taken_quantity = move._update_reserved_quantity(need, quantity, location_id, lot_id, package_id,
                                                                        owner_id)
                        if need - taken_quantity == 0.0:
                            assigned_moves |= move
                            break
                        partially_available_moves |= move
        # Not Make State Assigned if context key value 'state_change' = False
        partially_available_moves.write({'state': 'partially_available'})
        if self._context.get('state_change', True) == True:
            assigned_moves.write({'state': 'assigned'})
            self.mapped('picking_id')._check_entire_pack()
        else:
            return


class stockPicking(models.Model):
    _inherit = "stock.picking"

    purchase_requisition_id = fields.Many2one('purchase.requisition', readonly=1)
    department_id = fields.Many2one('hr.department', readonly=1,
                                    default=lambda self: self.env['hr.employee'].search(
                                        [('user_id', '=', self.env.user.id)]).department_id.id or False)
    products_type = fields.Selection([('stationery', 'Stationery'), ('others', 'Others')], required=0)
    # order_staionary = fields.Boolean(compute="_show_staionary_order_button",default=False)
    # order_others = fields.Boolean(compute="_show_others_order_button",default=False)
    order_staionary = fields.Boolean(default=False)
    order_others = fields.Boolean(default=False)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, readonly=1)
    back_order_id = fields.Many2one('stock.picking', readonly=1)
    is_outgoing_order = fields.Boolean(default=False)
    show_st_resp_validate = fields.Boolean(default=False)
    note = fields.Text('Note')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('waiting_payment', 'Waiting Requestion Picking'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        )


    def action_cancel_draft(self):
        if self.purchase_requisition_id or self.back_order_id:
            raise UserError(_("You can't make picking draft when Purchase Requisition aleardy created"))
        if self.back_order_id:
            raise UserError(_("You can't make picking draft when Backorder aleardy created"))
        #invisible stock responsible validate button
        self.show_st_resp_validate = False

        self.do_unreserve()
        for line in self.mapped('move_lines'):
            line.state = 'draft'
        self.mapped('move_line_ids').unlink()
        self.with_context(requistion_false=True)._show_purchase_button()
        self.state = 'draft'

    #when purchase picking done
    @api.multi
    def button_validate(self):
        self.ensure_one()

        if self.purchase_id.requisition_id.id != False:
            picking_id =  self.search([('purchase_requisition_id','=',self.purchase_id.requisition_id.id)])
            if picking_id:
                picking_id.state = "waiting"

        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some lines to move'))

        # If no lots when needed, raise error
        picking_type = self.picking_type_id
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        no_quantities_done = all(
            float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids)
        no_reserved_quantities = all(
            float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in
            self.move_line_ids)
        if no_reserved_quantities and no_quantities_done:
            raise UserError(_(
                'You cannot validate a transfer if you have not processed any quantity. You should rather cancel the transfer.'))

        if picking_type.use_create_lots or picking_type.use_existing_lots:
            lines_to_check = self.move_line_ids
            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(
                    lambda line: float_compare(line.qty_done, 0,
                                               precision_rounding=line.product_uom_id.rounding)
                )

            for line in lines_to_check:
                product = line.product_id
                if product and product.tracking != 'none':
                    if not line.lot_name and not line.lot_id:
                        raise UserError(_('You need to supply a lot/serial number for %s.') % product.display_name)
                    elif line.qty_done == 0:
                        raise UserError(_(
                            'You cannot validate a transfer if you have not processed any quantity for %s.') % product.display_name)

        if no_quantities_done:
            view = self.env.ref('stock.view_immediate_transfer')
            wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
            return {
                'name': _('Immediate Transfer?'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.immediate.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
            view = self.env.ref('stock.view_overprocessed_transfer')
            wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.overprocessed.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        # Check backorder should check for other barcodes
        if self._check_backorder():
            return self.action_generate_backorder_wizard()
        self.action_done()
        return


    def _show_purchase_button(self):
        """
        Show purchase button for stock manager or who create record based on products_type selection
        :return:
        """
        check = False
        if self.products_type == 'stationery' and self.state in ('waiting', 'confirmed'):
            for line in self.move_lines:
                if line.product_uom_qty > line.reserved_availability:
                    check = True
                    # self.order_staionary = True
            self.order_staionary = check
        else:
            self.order_staionary = False

        if self.products_type == 'others' and self.state in (
        'waiting', 'confirmed') and self.env.user.id == self.user_id.id:
            for line in self.move_lines:
                if line.product_uom_qty > line.reserved_availability:
                    check = True
                    # self.order_others = True
            self.order_others = check

        else:
            self.order_others = False
        ## if context have key requistion_false = True then make all purchase button invisible
        if self._context.get('requistion_false', False) == True:
            self.order_others = False
            self.order_staionary = False

    def create_purchase_requesetion(self):
        """
        call wizard to create purchase requesition
        :return:
        """
        if self._context.get('requestion_create', True) == True:
            view = self.env.ref('stock_custom.view_stock_requestion_create')
            wiz = self.env['stock.requestion.create'].create({'picking_id': self.id,
                                                              'product_requesiton_ids': [self.__create_products(line) for line
                                                                                         in
                                                                                         self.move_lines if (
                                                                                         line.product_uom_qty - line.reserved_availability > 0)]
                                                              })

            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.requestion.create',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

    def __create_products(self, product):
        """

        :param product:
        :return:
        """
        product_memory = (0, 6, {
            'product_id': product.product_id.id,
            'initial_demand': product.product_uom_qty - product.reserved_availability,

        })
        return product_memory

    def validate_manager(self):
        """
        validate order from who create record to stock manager
        :return:
        """
        self.action_confirm()

    def validate_stock_backorder(self):
        """
        create backorder from picking
        :return:
        """
        moves = self.mapped('move_lines').filtered(lambda moves: moves.quantity_done == 0)
        if moves:
            raise UserError(
                _("must all done not zero"))

        moves = self.mapped('move_lines').filtered(lambda moves: moves.product_uom_qty > moves.quantity_done)

        if moves:
            created_picking = self.env['stock.picking'].create({
                'partner_id': self.partner_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'scheduled_date': self.scheduled_date,
                'department_id': self.department_id.id,
                'products_type': self.products_type,
                'owner_id': self.owner_id.id,
                'picking_type_id': self.picking_type_id.id,
                'move_lines': [self.__create_picking_move_lines(m) for m in
                               moves if m.product_uom_qty > m.quantity_done]
            })
            # created_picking.validate_manager()

            list_of_done = [line.quantity_done for line in self.move_lines]
            #
            self.do_unreserve()

            count = 0
            for line in self.move_lines:
                line.product_uom_qty = list_of_done[count]
                line.reserved_availability = list_of_done[count]
                line.quantity_done = list_of_done[count]
                count += 1

            self.with_context(state_change=False).action_assign()

            self.back_order_id = created_picking.id
            self.validate_stock_responsible()
        else:
            raise UserError(
                _("moves initial and done is equal ,no need to create backorder!! ,plz press Validate Button "))

    def validate_stock_no_backorder(self):
        """
        create backorder from picking and set state for product cancel
        :return:
        """
        moves = self.mapped('move_lines').filtered(lambda moves: moves.quantity_done == 0)
        if moves:
            raise UserError(
                _("must all done not zero"))

        moves = self.mapped('move_lines').filtered(lambda moves: moves.product_uom_qty > moves.quantity_done)

        if moves:
            created_picking = self.env['stock.picking'].create({
                'partner_id': self.partner_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'scheduled_date': self.scheduled_date,
                'department_id': self.department_id.id,
                'products_type': self.products_type,
                'owner_id': self.owner_id.id,
                'picking_type_id': self.picking_type_id.id,
                'move_lines': [self.__create_picking_move_lines(m) for m in
                               moves if m.product_uom_qty > m.quantity_done]
            })
            created_picking.action_cancel()
            # created_picking.validate_manager()

            list_of_done = [line.quantity_done for line in self.move_lines]
            #
            self.do_unreserve()

            count = 0
            for line in self.move_lines:
                line.product_uom_qty = list_of_done[count]
                line.reserved_availability = list_of_done[count]
                line.quantity_done = list_of_done[count]
                count += 1

            self.with_context(state_change=False).action_assign()

            self.back_order_id = created_picking.id
            self.validate_stock_responsible()
        else:
            raise UserError(
                _("moves initial and done is equal ,no need to create backorder!! ,plz press Validate Button "))



    def __create_picking_move_lines(self, product):
        """

        :param product:
        :return:
        """
        product_memory = (0, 6, {
            'name': product.name,
            'date_expected': product.date_expected,
            'picking_type_id': product.picking_type_id.id,
            'location_id': product.location_id.id,
            'location_dest_id': product.location_dest_id.id,
            # 'product_type':product.product_type.id,
            'product_id': product.product_id.id,
            'product_uom_qty': product.product_uom_qty - product.quantity_done,
            'picking_type_id': product.picking_type_id.id,
            'product_uom': product.product_uom.id
            # 'stock_exchange_line': product.id,
        })
        return product_memory

    @api.multi
    def validate_stock_responsible(self):
        """ Check availability of picking moves.
        validate stock responsible and run backorder wizard if done  != initialdemand
        @return: True
        """
        if self._context.get('backorder_create', True) == True:
            moves = self.mapped('move_lines')

            if moves.filtered(lambda moves: moves.quantity_done > moves.product_uom_qty):
                raise UserError(
                    _(
                        "Error !! , Product done Greater than Product Initial Demand , Kindly make Product done equal or less than product Initial Demand"))

            if moves.filtered(lambda moves: moves.quantity_done == 0):
                raise UserError(
                    _("Error!! , All Product done must not be Zero ! , Plz enter all product done"))

            if moves.filtered(lambda moves: moves.product_uom_qty > moves.quantity_done):
                view = self.env.ref('stock_custom.view_backorder_create')
                wiz = self.env['stock.backorder.create'].create({'picking_id': self.id})
                return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.backorder.create',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                }

        for line in self.move_lines:
            if line.product_uom_qty != line.reserved_availability:
                raise UserError(_("You Can't Validate unless all Products initial = reserved"))
        self.state = "assigned"
        self.filtered(lambda picking: picking.state == 'draft').action_confirm()
        moves = self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
        if not moves:
            raise UserError(_('Nothing to check the availability for.'))
        moves.with_context(state_change=True)._action_assign()

        return True

    @api.multi
    def button_validate_custom(self):
        """
        validate picking order for service manager
        :return:
        """
        self.ensure_one()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some lines to move'))

        # If no lots when needed, raise error
        picking_type = self.picking_type_id
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        no_quantities_done = all(
            float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids)
        no_reserved_quantities = all(
            float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in
            self.move_line_ids)
        if no_reserved_quantities and no_quantities_done:
            raise UserError(_(
                'You cannot validate a transfer if you have not processed any quantity. You should rather cancel the transfer.'))

        if no_quantities_done:
            view = self.env.ref('stock.view_immediate_transfer')
            wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
            return {
                'name': _('Immediate Transfer?'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.immediate.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
            view = self.env.ref('stock.view_overprocessed_transfer')
            wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.overprocessed.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        # Check backorder should check for other barcodes
        if self._check_backorder():
            return self.action_generate_backorder_wizard()
        # self.action_done()
        return

    @api.multi
    def validate_stock(self):
        """ Check availability of picking moves.
        This has the effect of changing the state and reserve quants on available moves, and may
        also impact the state of the picking as it is computed based on move's states.
        @return: True
        """
        self.show_st_resp_validate=True
        # to save done quantity and returnt after delete when do self.do_unreserve

        list_of_done = [line.quantity_done for line in self.move_lines]

        self.do_unreserve()
        self.with_context(state_change=False).action_assign()
        count = 0
        for line in self.move_lines:
            line.quantity_done = list_of_done[count]
            count += 1
        # To show Purchase button
        self._show_purchase_button()

    @api.depends('move_type', 'move_lines.state', 'move_lines.picking_id')
    @api.one
    def _compute_state(self):
        ''' State of a picking depends on the state of its related stock.move
        - Draft: only used for "planned pickings"
        - Waiting: if the picking is not ready to be sent so if
          - (a) no quantity could be reserved at all or if
          - (b) some quantities could be reserved and the shipping policy is "deliver all at once"
        - Waiting another move: if the picking is waiting for another move
        - Ready: if the picking is ready to be sent so if:
          - (a) all quantities are reserved or if
          - (b) some quantities could be reserved and the shipping policy is "as soon as possible"
        - Done: if the picking is done.
        - Cancelled: if the picking is cancelled
        '''
        if not self.move_lines:
            self.state = 'draft'
        elif any(move.state == 'draft' for move in self.move_lines):  # TDE FIXME: should be all ?
            self.state = 'draft'
        elif all(move.state == 'cancel' for move in self.move_lines):
            self.state = 'cancel'
        elif all(move.state in ['cancel', 'done'] for move in self.move_lines):
            self.state = 'done'
        else:
            relevant_move_state = self.move_lines._get_relevant_state_among_moves()
            if relevant_move_state == 'partially_available':
                params = self._context.get('params', False)
                if params:
                    action = self.env['ir.actions.act_window'].search(
                        [('id', '=', self._context.get('params')['action'])])
                    if action.xml_id == 'stock_custom.stock_picking_action_custom':
                        self.state = 'confirmed'
                    else:
                        self.state = 'assigned'
            else:
                self.state = relevant_move_state

    @api.model
    def create(self, vals):
        # TDE FIXME: clean that brol
        defaults = self.default_get(['name', 'picking_type_id'])
        if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get('picking_type_id',
                                                                                          defaults.get(
                                                                                              'picking_type_id')):
            vals['name'] = self.env['stock.picking.type'].browse(
                vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()

        # TDE FIXME: what ?
        # As the on_change in one2many list is WIP, we will overwrite the locations on the stock moves here
        # As it is a create the format will be a list of (0, 0, dict)
        if vals.get('move_lines') and vals.get('location_id') and vals.get('location_dest_id'):
            for move in vals['move_lines']:
                if len(move) == 3:
                    move[2]['location_id'] = vals['location_id']
                    move[2]['location_dest_id'] = vals['location_dest_id']

        vals.update(is_outgoing_order=False)
        res = models.Model.create(self, vals)
        params = self._context.get('params', False)
        # if from spicific action run  ._autoconfirm_picking with context key planned_picking
        if params:
            action = self.env['ir.actions.act_window'].search([('id', '=', self._context.get('params')['action'])])
            if action.xml_id == 'stock_custom.stock_picking_action_custom':
                res.is_outgoing_order=True
                res.with_context({'planned_picking': True})._autoconfirm_picking()
            else:
                res._autoconfirm_picking()
        # res.state = 'conf'
        return res

class stockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    cost_lines = fields.One2many(
        'stock.landed.cost.lines', 'cost_id', 'Cost Lines', readonly=1,
        copy=True, states={'draft': [('readonly', False)]})
    date = fields.Date(
        'Date', default=fields.Date.context_today, readonly=1,
        copy=False, required=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    account_journal_id = fields.Many2one(
        'account.journal', 'Account Journal', readonly=1,
        required=True, states={'draft': [('readonly', False)]})
    picking_ids = fields.Many2many(
        'stock.picking', string='Pickings', readonly=1,
        copy=False, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('done', 'Posted'),
        ('cancel', 'Cancelled')], 'State', default='draft',
        copy=False, readonly=True, track_visibility='onchange')

    def stock_responible_validate(self):
        """

        :return:
        """
        if any(cost.state != 'draft' for cost in self):
            raise UserError(_('Only draft landed costs can be validated'))
        if any(not cost.valuation_adjustment_lines for cost in self):
            raise UserError(_('No Cost lines. You should maybe recompute the landed costs.'))
        if not self._check_sum():
            raise UserError(_('Cost and adjustments lines do not match. You should maybe recompute the landed costs.'))

        self.state = 'validated'

    @api.multi
    def button_validate(self):
        """

        :return:
        """
        if any(not cost.valuation_adjustment_lines for cost in self):
            raise UserError(_('No Cost lines. You should maybe recompute the landed costs.'))
        if not self._check_sum():
            raise UserError(_('Cost and adjustments lines do not match. You should maybe recompute the landed costs.'))

        for cost in self:
            move = self.env['account.move']
            move_vals = {
                'journal_id': cost.account_journal_id.id,
                'date': cost.date,
                'ref': cost.name,
                'line_ids': [],
            }
            for line in cost.valuation_adjustment_lines.filtered(lambda line: line.move_id):
                # Prorate the value at what's still in stock
                cost_to_add = (line.move_id.remaining_qty / line.move_id.product_qty) * line.additional_landed_cost

                new_landed_cost_value = line.move_id.landed_cost_value + line.additional_landed_cost
                line.move_id.write({
                    'landed_cost_value': new_landed_cost_value,
                    'value': line.move_id.value + cost_to_add,
                    'remaining_value': line.move_id.remaining_value + cost_to_add,
                    'price_unit': (line.move_id.value + new_landed_cost_value) / line.move_id.product_qty,
                })
                # `remaining_qty` is negative if the move is out and delivered proudcts that were not
                # in stock.
                qty_out = 0
                if line.move_id._is_in():
                    qty_out = line.move_id.product_qty - line.move_id.remaining_qty
                elif line.move_id._is_out():
                    qty_out = line.move_id.product_qty
                move_vals['line_ids'] += line._create_accounting_entries(move, qty_out)

            move = move.create(move_vals)
            cost.write({'state': 'done', 'account_move_id': move.id})
            move.post()
        return True


#inherit stock_Warehouse view 
class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    # @api.constrains('name')
    # def check_warehouse_name(self):
    #     if not all(x.isalpha() or x.isspace() for x in self.name):
    #         raise UserError(_(" warehouse name should not contains symbols or numbers "))

    # @api.constrains('code')
    # def check_warehouse_name(self):
    #     if not all(x.isalpha() or x.isspace() for x in self.code):
    #         raise UserError(_(" code name should not contains symbols or numbers "))



#inherit stock_location view 
class Location(models.Model):
    _inherit = "stock.location"

    # @api.constrains('name')
    # def check_Location_name(self):
    #     if not all(x.isalpha() or x.isspace() for x in self.name):
    #         raise UserError(_(" Location name should not contains symbols or numbers "))

    @api.constrains('posx','posy','posz')
    def posative(self):
        if self.posx < 0 or self.posy < 0 or self.posz < 0  :
            raise UserError(_(" this field should not be negative values "))
        #if self.posx == 0 and self.posy == 0 and self.posz == 0  :
        #    raise UserError(_(" this field should not be  all zero"))

    _sql_constraints = [
        ('stock_location_uniq', 'unique (name)', _('location name must be unique.')),]



#inherit stockpickingtype view 
class stockpickingtype(models.Model):
    _inherit = 'stock.picking.type'

    _sql_constraints = [
        ('stock_picking_uniq', 'unique (name)', _('picking name must be unique.')),]


#inherit stockpickingtype view 
class productsupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    @api.constrains('delay')
    def delay_constrains(self):
        if self.delay <  0:
            raise UserError(_(" Delivery Lead Time should not be negative values "))


    @api.constrains('date_start','date_end')
    def date_constrains(self):
        if self.date_start and self.date_end:
            if self.date_start >= self.date_end :
                raise UserError(_(" date_start must be smaller than date_end"))

    @api.constrains('price')
    def price_constrains(self):
         if self.price <= 0.0 :
             raise UserError(_(" price should not be negative values"))


    @api.constrains('min_qty')
    def min_qty_constrains(self):
        if self.min_qty <  0.0:
            raise UserError(_(" minimal quantaty should not be negative values "))

  
#inherit stockpickingtype view 
class producttemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('standard_price','list_price')
    def standard_cost_constrains(self):
        if self.standard_price < 0 or self.list_price < 0 :
            raise UserError(_("Price/Cost must be greater than zero"))

    @api.constrains('default_code')
    def check_default_code(self):
        """
        Constraint to prevent default code to have sympol
        """
        if self.default_code:
            if not all(x.isalpha() or x.isspace() or x.isdigit() for x in self.default_code):
                raise UserError(_(" Internal Reference should not contains symbols "))

    # @api.constrains('name')
    # def check_product_name(self):
    #     if not all(x.isalpha() or x.isspace() for x in self.name):
    #         raise UserError(_(" product name should not contains symbols or numbers "))


class productProduct(models.Model):
    """docstring for productProduct"""
    _inherit = 'product.product'

    @api.constrains('standard_price','lst_price')
    def standard_cost_constrains(self):
        if self.standard_price < 0 or self.lst_price < 0 :
            raise UserError(_("Price/Cost must be greater than zero"))



class stockLandedCostLines(models.Model):
    """docstring for stockLandedCostLines"""
    _inherit = "stock.landed.cost.lines"

    @api.constrains('price_unit')
    def price_unit_constrains(self):
        if self.price_unit <= 0:
            raise UserError(_("Cost must be greater than zero"))



class stock_scrap(models.Model):
    _inherit = 'stock.scrap'

    @api.constrains('scrap_qty')
    def scrap_qty_constrains(self):
        if self.scrap_qty <= 0.0:
             raise UserError(_("Quantaty must not be less than one"))



class StocksInventoryLines(models.Model):
    """docstring for stock inventory line"""
    _inherit = "stock.inventory.line"

    @api.constrains('product_qty')
    def product_qty_constrains(self):
        if self.product_qty < 0:
          raise UserError(_("Real Quantity can not be negative!!"))

