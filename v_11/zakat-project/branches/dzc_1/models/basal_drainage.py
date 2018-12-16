from odoo import fields, models, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError
from datetime import datetime, timedelta


class PlanningOfBasalDrainage(models.Model):
    _name = 'planning.basal.darinage'
    code = fields.Char(string='Ref')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    name = fields.Char(string="Program Description", size=256, required=True)
    order_date = fields.Date(string="Order Date", default=datetime.today())
    unit_of_admin_ids = fields.One2many(comodel_name='planning.basal.planning', inverse_name='name')
    # zakat_committee = fields.One2many(comodel_name='planning.basal.planning', inverse_name='name')
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('done', 'Done'), ('cancel', 'Cancel')],
        default='draft', string="Status")
    local_state_id = fields.Many2one('zakat.local.state', 'Local State')
    type = fields.Selection([('a_u', 'Administrative Unit '), ('z_c', 'Zakat Committee')], string="Type",default="a_u")

    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.sequence.number_next_actual

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('basal.drainage.sequence') or '/'
        plans = self.env['planning.basal.darinage'].search([('date_from','>=', vals['date_from']),('date_to','<=',vals['date_to']),('state','=','done'),('local_state_id','=',vals['local_state_id'])])
        print("||||||",plans)
        if plans:
            raise ValidationError(_('Sorry! You cannot make Plan  with same duration.'))

        return super(PlanningOfBasalDrainage, self).create(vals)

    @api.multi
    def confirm(self):
        if not self.unit_of_admin_ids:
            raise exceptions.UserError(_('Sorry! You must Enter at least Onr Adminstrative Unit'))
        else:
            self.write({'state': 'confirm'})

    @api.multi
    def save(self):
        self.write({'state': 'confirm'})

    @api.multi
    def approve(self):
        self.write({'state': 'done'})

    @api.multi
    def cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def draft(self):
        self.write({'state': 'draft'})



    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ('draft'):
                raise exceptions.UserError(_('Sorry! You Cannot Delete not Draft Plan .'))
        return models.Model.unlink(self)

    @api.constrains('date_from', 'date_to')
    def duration_vslidstion(self):
        for rec in self:
            if rec.date_from < rec.date_to:
                return True
            else:
                raise ValidationError(_("Start Date must be after the End Date"))

    @api.constrains('name_of_program')
    def name_validation(self):
        valid = 0
        for letter in self.name_of_program:
            if letter.isalpha() or letter.isdigit() or letter == ' ':
                valid += 1
        if valid == len(self.name_of_program):
            return True
        else:
            raise ValidationError(_("The name you entered is not valid"))


class BasalDrainagePlanning(models.Model):
    _name = 'planning.basal.planning'
    name = fields.Many2one('planning.basal.darinage')
    # Basal Drainage Planning fields
    admin_unit_id = fields.Many2one('zakat.admin.unit', 'Adminstrative Unit')
    no_of_families = fields.Float(string='Number of Families')
    excuting_actual = fields.Float(string='Excuting Acctual')
    persecnt = fields.Float(string='Percentage')
    committee = fields.Many2one('zakat.dzc1.committee', string="Committee")

    _sql_constraints = [
        ('unique_name_a_c', 'unique(name,admin_unit_id,committee)', _('You Cannot Have The Same Committee'))

    ]

    @api.multi
    def excuting_actual_compute(self):
        self.write({'excuting_actual': 5})

    @api.one
    def compute_percrntage(self):
        self.write({'persecnt': '50'})

    @api.constrains('no_of_families')
    def no_of_families_validate(self):
        for rec in self:
            if rec.no_of_families <= 0:
                raise ValidationError(_("No Of Families Must be greater than zero"))



class BasalDrinageOrder(models.Model):
    _name = 'basal.drainage.order'
    name = fields.Char(string='Ref')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    order_date = fields.Date(string="Order Date", default=datetime.today())
    program_id = fields.Many2one('basal.drainage.program' , 'Program')
    order_type = fields.Selection([('cash', 'Cash'), ('material', 'material')])
    families_ids = fields.One2many(comodel_name='basal.drainage.order.families', inverse_name='name')
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('approve', 'Approve'), ('done', 'Done'), ('cancel', 'Cancel')],
        default='draft', string="Status")
    products = fields.One2many(comodel_name='basal.drainage.order.families', inverse_name='order_id')
    local_state_id = fields.Many2one('zakat.local.state', 'Local State')
    voucher_id = fields.Many2one('account.voucher', ondelete="restrict")
    address_id = fields.Many2one('addresses','Address')
    
    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.sequence.number_next_actual

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('basal.drainage.order.sequence') or '/'
        return super(BasalDrinageOrder, self).create(vals)

    @api.multi
    def confirm(self):
        self.write({'state': 'confirm'})

    @api.multi
    def save(self):
        self.write({'state': 'confirm'})

    @api.multi
    def approve(self):
        self.write({'state': 'approve'})

    @api.multi
    def cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def done(self):
        if self.order_type == 'material':
            stock_creation = []
            product = []
            pick_type = self.env['stock.picking.type'].search([('id','=',1)])
            print("????????????",pick_type.default_location_src_id)

            for rec in self.families_ids:
                print(">>>>>>>>>>>>>>11")
                stock_creation = self.env['stock.picking'].create(
                    {
                    'partner_id': rec.fageer_id.id,
                    'location_id': 14,
                    'picking_type_id': 1,
                    # 'pick_type.default_location_src_id': 23,
                    # 'pick_type.default_location_dest_id': 23,
                    'location_dest_id': 9,

                    })
                # product = self.get_product_lines(self.products,stock_creation) 
                for rec in self.products:
                    stock_creation.move_lines.create({
                            'product_id': rec.product_id.id,
                            'name':'',
                            # 'product_qty': rec.product_qty,
                            # 'product_uom_id': 2,
                            'picking_id':stock_creation.id,
                            'product_uom':1,
                            'location_id': stock_creation.location_id.id,
                            'location_dest_id': 9,
                            'product_uom_qty' :rec.product_qty,
                        })
                    print("+++++\n\n",stock_creation.move_lines,"\n\n")
                print("!!!!!!!!!!!!",stock_creation)
                # lines_creation = self.env['stock.picking'].write(
                #     {
                #     'moves_lines':product,
                #     })

        self.write({'state': 'done'})
        admin_units = []
        for data in self.families_ids:
            admin_units.append(data.fageer_id.admin_unit)
        drainage_plans = self.env['planning.basal.darinage'].search(
            ['&', '&', ('state', '=', 'done'), ('date_from', '<=', self.order_date),
             ('date_to', '>=', self.order_date)])
        for x in admin_units:
            for xx in drainage_plans:
                for y in xx.unit_of_admin_ids:
                    if x == y.admin_unit_id:
                        y.excuting_actual += 1
                        y.persecnt = (y.excuting_actual / y.no_of_families) * 100
    
    @api.multi
    def get_product_lines(self,p , p_id):
        p_line = []
        print("-------------",p_id)
        for pr in p:
            p_line =  self.env['stock.move.line'].create({
            'product_id': pr.product_id.id,
            # 'product_qty': pr.product_qty,
            'product_uom_id': 1,
            'picking_id':p_id.id,
            'location_id': p_id.location_id.id,
            'location_dest_id': 9,
            # 'product_uom_qty' :1,
            })
            print("**********",p_line)
        return p_line


    @api.constrains('name_of_program')
    def name_validation(self):
        valid = 0
        for letter in self.name_of_program:
            if letter.isalpha() or letter.isdigit() or letter == ' ':
                valid += 1
        if valid == len(self.name_of_program):
            return True
        else:
            raise ValidationError(_("The name you entered is not valid"))

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ('draft'):
                raise exceptions.UserError(_('Sorry! You Cannot Delete not Draft Order .'))
        return models.Model.unlink(self)


class BasalDrainagePlanning(models.Model):
    _name = 'basal.drainage.order.families'
    name = fields.Many2one('basal.drainage.order', '')
    fageer_id = fields.Many2one('res.partner', 'Fageer')
    amount = fields.Float(string='Amount')
    status_class = fields.Selection(
        [('widow', 'widow'), ('divorced', 'Divorced'), ('aged', 'Aged'), ('disabled', 'Disabled'),
         ('limted_income' , 'Limited Income') , ('maytr', 'Maytr')])
    order_id = fields.Many2one(comodel_name='basal.drainage.order', string='dgvfgsvg')
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Integer(string='Product Quality')

    @api.constrains('product_qty')
    def qty_validation(self):
        if self.product_qty <= 0:
            raise ValidationError(_("Product Quantity MUST be greater Than Zero"))

    @api.constrains('amount')
    def qty_validation(self):
        if self.amount <= 0:
            raise ValidationError(_("Amount MUST be Greater Than Zero"))

class BasalDrainageProgram(models.Model):
    _name = 'basal.drainage.program'
    name = fields.Char(string='Pregram Name')
    support_type = fields.Selection([('cash' , 'Cash') , ('material' , 'Material')] , string='Support Type')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    account_id = fields.Many2one('account.account' , 'Accouont')
    analytic_account_id = fields.Many2one('account.analytic.account' , 'Analytic Account')
    journal_id = fields.Many2one('account.journal' , 'Journal')

