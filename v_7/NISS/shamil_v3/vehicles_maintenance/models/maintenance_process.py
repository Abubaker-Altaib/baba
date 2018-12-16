# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from mx import DateTime
import time
from datetime import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import netsvc
from dateutil.relativedelta import relativedelta
from openerp.addons.account_voucher.account_voucher import resolve_o2m_operations


class machine_type(osv.Model):
    _name = "machine.type"
    _columns = {
        'name': fields.char('Machine Type'),
    }

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'The damage name must be unique!'),
    ]

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
        return True
    _constraints = [
        (_check_spaces, '', ['name'])
    ]
    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            if rec.damage_lines_ids:
                raise osv.except_osv(
                    _(''), _("can not delete record linked with other record"))
        return super(maintenance_damage, self).unlink(cr, uid, ids, context=context)

class wheel_type(osv.Model):
    _name = "wheel.type"
    _columns = {
        'name': fields.char('wheel Type'),
    }

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'The damage name must be unique!'),
    ]

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
        return True
    _constraints = [
        (_check_spaces, '', ['name'])
    ]
    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            if rec.damage_lines_ids:
                raise osv.except_osv(
                    _(''), _("can not delete record linked with other record"))
        return super(maintenance_damage, self).unlink(cr, uid, ids, context=context)

#--------------------------
#   Inherit Vehicle Accident
#--------------------------

class  vehicle_accident(osv.osv):
    """ To manage vehicle Accident process """
    _inherit = "vehicle.accident"
    _columns = {
        'maintenance_id': fields.many2one('maintenance.request','Maintenance Request'),
    }

    def create_maintenance(self,cr,uid,ids,context=None):
        """
        Mehtod that create maintenace request.

        @return: Boolean True
        """
        print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>maintenace_request"
        maintenace_obj=self.pool.get("maintenance.request")
        date=time.strftime('%Y-%m-%d')
        today = datetime.strptime(date,"%Y-%m-%d")
        for rec in self.browse(cr, uid, ids, context):
            check=rec.check_to_maintenace()
            if check:
                vals={
                'default_out_source':True,
                'default_vehicle_id':rec.vehicle_id.id,
                'default_company_id':rec.company_id.id,
                'accident_id':rec.id,
                }
                dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vehicles_maintenance', 'maintenances_request_with_footer')
                return {
                        'name': _('Maintenace Request'),
                        'view_type': 'form',
                        'view_id': view_id,
                        'view_mode': 'form',
                        'res_model': 'maintenance.request',
                        'type': 'ir.actions.act_window',
                        'context' : vals,
                        'target': 'new',
                    }
        return True

    def check_to_Done(self,cr,uid,ids,context=None):
        """
        Mehtod that check go to Done state constraints .

        @return: Boolean True
        """

        for rec in self.browse(cr, uid, ids, context):
            if not rec.maintenance_id: 
                raise osv.except_osv(_('ValidateError'), _("There Is NO maintenace request refrence to this accident."))
                return False
        return True

class maintenance_damage(osv.Model):
    _name = "maintenance.damage"
    _columns = {
        'name': fields.char('Damage'),
        'damage_lines_ids': fields.many2many('maintenance.damage.line', 'maintenance_damage_line_damage_rel', 'damage_id', 'damage_line_id', string='Damages'),
        'company_id': fields.many2one('res.company','company'),
    }
    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company
    _defaults={
        'company_id' : _default_company,
        }

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'The damage name must be unique!'),
    ]

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
        return True
    _constraints = [
        (_check_spaces, '', ['name'])
    ]

    # def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
    #     """
    #     @param name: Object name to search
    #     @param args: List of tuples specifying search criteria
    #     @param operator: Operator for search criterion
    #     @param limit: Max number of records to return
    #     @return: Super name_search method 
    #     """
    #     if context is None:
    #         context = {}
    #     if 'damage_lines_ids' in context:
    #         damage_ids = resolve_o2m_operations(cr, uid, self.pool.get('maintenance.damage.line'),
    #                                             context.get('damage_lines_ids'), ["damage_id"], context)
    #         args.append(('id', 'not in', [isinstance(
    #             d['damage_id'], tuple) and d['damage_id'][0] or d['damage_id'] for d in damage_ids]))

    #     return super(maintenance_damage, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            if rec.damage_lines_ids:
                raise osv.except_osv(
                    _(''), _("can not delete record linked with other record"))
        return super(maintenance_damage, self).unlink(cr, uid, ids, context=context)

class maintenance_damage_line(osv.Model):
    _name = "maintenance.damage.line"

    def _get_job_state(self, cr, uid, ids, field, args, context):
        res = {}
        for rec in self.browse(cr, uid, ids, context=context):
            job_state = False
            if rec.job_ids:
                job_state = rec.job_ids[0].state
            res[rec.id] = job_state
        return res

    _columns = {
        'department_id': fields.related('process_id', 'department_id', string='Maintenance Department', type="many2one", relation='maintenance.department', store=True),
        # 'damage_id': fields.many2one('maintenance.damage', string='Damage'),
        'damages_ids': fields.many2many('maintenance.damage', 'maintenance_damage_line_damage_rel', 'damage_line_id', 'damage_id', string='Damages'),
        'process_id': fields.many2one('maintenance.request', string='Process'),
        'job_ids': fields.one2many('maintenance.job', 'damage_line_id', string='Jobs'),
        'job_ref': fields.char('Referance'),
        'job_state': fields.function(_get_job_state, type="char", store=True),
    }

    def unlink(self, cr, uid, ids, context=None):
        """
        @return: super unlink() method
        """
        for rec in self.browse(cr, uid, ids):
            for job in rec.job_ids:
                job.unlink()
        return super(maintenance_damage_line, self).unlink(cr, uid, ids, context=context)

    def open_record(self,  cr, uid, ids, context=None):
        rec = self.browse(cr, uid, ids)[0]

        rec_datetime = rec.process_id.recieve_datetime
        rec_datetime = datetime.strptime(rec_datetime, '%Y-%m-%d %H:%M:%S')

        current_datetime = time.strftime('%Y-%m-%d %H:%M:%S')
        current_datetime = datetime.strptime(
            current_datetime, '%Y-%m-%d %H:%M:%S')

        if rec_datetime > current_datetime:
            raise osv.except_osv(_('Invalid Action Error'), _(
                'can not create a job before the recieve datetime'))
        if not rec.job_ids:
            if rec.process_id.state != 'process':
                raise osv.except_osv(_('Invalid Action Error'), _(
                    'can not create a job before start process in this vehicle'))
            job_id = self.pool.get('maintenance.job').create(cr, uid, {'start_datetime': time.strftime('%Y-%m-%d %H:%M:%S'),
                                                                       'damage_line_id': rec.id,
                                                                       'damages_ids': [[6, False,[x.id for x in rec.damages_ids] ]],
                                                                       'company_id': rec.process_id.company_id.id,
                                                                       'vehicle_id': rec.process_id.vehicle_id.id,
                                                                       'process_ref': rec.process_id.ref,
                                                                       'odometer': rec.process_id.odometer,
                                                                       'odometer_unit': rec.process_id.odometer_unit})
        rec = self.browse(cr, uid, ids)[0]
        job_id = rec.job_ids and rec.job_ids[0].id or False
        job_ref = rec.job_ids and rec.job_ids[0].ref or False
        rec.write({'job_ref': job_ref})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.job',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': job_id,
            'target': 'current',
        }

    def reset(self,  cr, uid, ids, context=None):
        rec = self.browse(cr, uid, ids)[0]
        rec.write({'job_ref': False})
        job_id = rec.job_ids and rec.job_ids or []
        for job in rec.job_ids:
            job.unlink()


class maintenance_job(osv.Model):
    _name = "maintenance.job"
    _rec_name = 'ref'

    _columns = {
        'ref': fields.char('Referance'),
        # 'damage_id': fields.many2one('maintenance.damage', string='Damage'),
        'damages_ids': fields.many2many('maintenance.damage', 'maintenance_job_damage', string='Damages'),
        'vehicle_id': fields.many2one('fleet.vehicle', 'Vehicle'),
        'start_datetime': fields.datetime('Start Datetime'),
        'end_datetime': fields.datetime('End Datetime'),
        'job_time': fields.char('Job Period'),
        'spares_ids': fields.one2many('maintenance.spare', 'job_id', string='Spares'),
        'damage_line_id': fields.many2one('maintenance.damage.line', string='Damage Line'),
        'company_id': fields.many2one('res.company', string='Company'),
        'process_ref': fields.char('Process Referance'),
        'eng_ids': fields.many2many('hr.employee', 'maintenance_job_engs', 'job_id', 'employee_id', 'Engineers'),
        'state': fields.selection([('draft', 'Draft'), ('requested', 'Stock Requested'), ('need_manager', 'Need Manager'), ('recieved', 'Spares Recieved'), 
                ('return','Waiting for the return of the store'),('done', 'Done'), ('canceled', 'Canceled')], string="State"),
        'odometer': fields.float('Odometer',digits=(6, 2)),
        'odometer_unit': fields.selection([('kilometers', 'Kilometers'), ('miles', 'Miles')], 'Odometer Unit', help='Unit of the odometer '),
        'maintenance_department_id': fields.related('damage_line_id', 'department_id', string='Department', type="many2one", relation='maintenance.department', store=True),
        #'comments': fields.integer('Comments'),
        'comments': fields.text('Comments'),
        'report_log': fields.text('Report Log'),
        'exchange_order_id': fields.many2one('exchange.order', string='Exchange Order'),
        'exchange_order_ids': fields.one2many('exchange.order', 'job_id', string='Exchange Order', readonly=True),
        'stock_picking_in_ids': fields.one2many('stock.picking.in', 'job_id', string='Returned Spares'),
        'picking_id': fields.many2one('stock.picking.in', string='Returned Spares'),
        'purchase_requestion_id': fields.related('exchange_order_id', 'purchase_requestion_id', string='Purchase Requestion', type="many2one", relation='ireq.m', store=True),


    }

    _defaults = {
        'state': 'draft',
    }

    def unlink(self, cr, uid, ids, context=None):
        """
        @return: super unlink() method
        """
        for rec in self.browse(cr, uid, ids):
            if rec.state != 'draft':
                raise osv.except_osv(_('Invalid Action Error'), _(
                    'can not delete this request before set to draft all it\'s jobs'))
        return super(maintenance_job, self).unlink(cr, uid, ids, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Override copy function to edit default value.

        @param default : default vals dict
        @return: super copy() method
        """
        raise osv.except_osv(_('Warning!'), _('You cannot duplicate record.'))
        return super(maintenance_job, self).copy(cr, uid, id, default, context)

    def create(self, cr, uid, vals, context=None):
        """
        Method thats overwrite the create method and naming the job by adding its sequence to the ref.

        @param vals: Values that have been entered
        @return: super create method
        """
        vals.update({'ref': self.pool.get('ir.sequence').get(
            cr, uid, 'maintenance.job')})
        return super(maintenance_job, self).create(cr, uid, vals, context=context)

    def get_datetime(self, str):
        return datetime.strptime(str, "%Y-%m-%d %H:%M:%S")

    def check_valid(self, cr, uid, ids, vehicle_id, constraints, product_id, start_datetime, quantity, odometer, odometer_unit):
        start_datetime = self.get_datetime(start_datetime)
        products_ids = filter(lambda x: x.product_id.id ==
                              product_id.id, vehicle_id.maintenance_spare_ids)
        user_obj = self.pool.get('res.users')
        for con in constraints:
            need_m = con.need_maintenance_manager_approve and user_obj.has_group(cr, uid, 'vehicles_maintenance.maintenance_manager')
            if need_m:
                continue
            if con.type == 'months':
                if quantity > con.constraint:
                    return False
                if not products_ids:
                    continue
                last_check = start_datetime - relativedelta(months=con.count)
                last_check_products = filter(lambda x: self.get_datetime(
                    x.start_datetime) >= last_check, products_ids)
                if not last_check_products:
                    continue
                last_check_sum = sum([x.quantity for x in last_check_products])
                if (last_check_sum + quantity) <= con.constraint:
                    continue
                return False
            if con.type == 'counter':
                if quantity > con.constraint:
                    return False
                if not products_ids:
                    continue
                last_check_sum = sum([x.quantity for x in products_ids])
                if (last_check_sum + quantity) <= con.constraint:
                    continue
                return False
            if con.type == 'distance':
                last = products_ids and [
                    max(products_ids, key=lambda x: self.get_datetime(x.start_datetime))] or False
                last_odometer = 0
                if last:
                    last = last[0]
                    last_odometer = last.job_id.odometer
                    if last.job_id.odometer_unit == 'miles':
                        last_odometer *= 1.609344
                current_odometer = odometer
                if odometer_unit == 'miles':
                    current_odometer *= 1.609344

                con_odometer = con.constraint
                if con.odometer_unit == 'miles':
                    con_odometer *= 1.609344
                if (current_odometer - last_odometer) >= con_odometer:
                    continue

                return False
        return True
    def need_manager(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            for spare in rec.spares_ids:
                product_id = spare.product_id
                constraints = product_id.spare_constraints_ids
                if constraints:
                    user_obj = self.pool.get('res.users')
                    for con in constraints:
                        if con.need_maintenance_manager_approve: 
                            return True
        return False

    def to_need_manager(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'need_manager'})

    def request(self, cr, uid, ids, context=None):
        exchange_order_obj = self.pool.get('exchange.order')
        exchange_line_obj = self.pool.get('exchange.order.line')
        wf_service = netsvc.LocalService("workflow")
        for rec in self.browse(cr, uid, ids, context=context):
            if not rec.spares_ids:
                raise osv.except_osv(_('Error'), _('You should Enter Spares'))

            for spare in rec.spares_ids:
                product_id = spare.product_id
                constraints = product_id.spare_constraints_ids
                # when product name changed the new name reflect in name_template field not name field 
                if constraints:
                    if not self.check_valid(cr, uid, ids, rec.vehicle_id, constraints, product_id, rec.start_datetime, spare.quantity, spare.job_id.odometer, spare.job_id.odometer_unit):
                        raise osv.except_osv(_('Invalid Action Error'), _(
                            'constraint in requesting product ' + product_id.name_template))
            lines = []
            for line in rec.spares_ids:
                onchange_vals = exchange_line_obj.product_id_change(cr, uid, [], line.product_id.id, line.quantity, False, date_order=False,
                                                                    name=False, price_unit=False, notes=False)
                lines_dict = {'product_id': line.product_id.id, 'product_qty': line.quantity,
                              'approved_qty': line.quantity, 'name': onchange_vals['value']['name'],
                              'price_unit': onchange_vals['value']['price_unit'],
                              'product_uom': onchange_vals['value']['product_uom'], 'state': 'draft',
                              'maintenance_spare_id': line.id,
                              }
                lines.append([0, False, lines_dict])

            new_id = exchange_order_obj.create(
                cr, uid, {'ttype': 'other', 'maintenance': True,
                          'job_id': rec.id, 'maintenance_department_id': rec.maintenance_department_id.id,
                          'location_id': rec.maintenance_department_id.location_dest_id.id,
                          'location_dest_id': rec.maintenance_department_id.stock_location_id.id,
                          'department_id': rec.maintenance_department_id.department_id.id,
                          'order_line': lines,
                          'maintenace_exchange_type': 'job'})
            wf_service.trg_validate(uid, 'exchange.order', new_id, 'exchange_maintenance_approve', cr)

            self.write(cr, uid, [rec.id], {'state': 'requested', 'exchange_order_id': new_id})
        

        return True

    def done(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context):
            rec_datetime = rec.start_datetime
            rec_datetime = datetime.strptime(rec_datetime, '%Y-%m-%d %H:%M:%S')

            current_datetime = time.strftime('%Y-%m-%d %H:%M:%S')
            current_datetime = datetime.strptime(
                current_datetime, '%Y-%m-%d %H:%M:%S')
            if rec_datetime > current_datetime:
                raise osv.except_osv(_('Invalid Action Error'), _(
                    'Recieve Datetime can not be greater than current datetime'))
            period = str(current_datetime - rec_datetime)
            rec.write({'job_time': period, 'end_datetime': current_datetime})
        self.write(cr, uid, ids, {'state': 'done'})

    def cancel(self, cr, uid, ids, context=None):

        wf_service = netsvc.LocalService("workflow")
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state == 'requested' and rec.exchange_order_id:
                #check = [x.id for x in rec.exchange_order_ids if x.state != 'cancel']
                #if check:
                raise osv.except_osv(_('Invalid Action Error'), _(
                'You must cancel the exchange order first'))
            

            '''if rec.purchase_requestion_id and rec.purchase_requestion_id.state != 'cancel':
                raise osv.except_osv(_('Invalid Action Error'), _(
                    'can not cancel related with purchase requestion order cancel it first'))'''
        return self.write(cr, uid, ids, {'state': 'canceled'})


    def return_fnc(self, cr, uid, ids, context=None):
        """
        Method that create stock picking in with the amount of the recieved spares
         to return it to the stock
        """

        wf_service = netsvc.LocalService("workflow")
        for rec in self.browse(cr, uid, ids, context=context):
            lines = []
            if rec.state == 'recieved':
                for line in rec.spares_ids:
                    if line.recieved_quantity != 0:
                        
                        lines_dict = {
                                'name': line.product_id.name[:250],
                                #'picking_id': picking_id,
                                'product_id': line.product_id.id,
                                'product_qty': line.recieved_quantity,
                                'product_uom': line.product_id.uom_id.id,
                                'product_uos_qty':line.recieved_quantity,
                                'product_uos':  line.product_id.uom_id.id,
                                'location_id': rec.damage_line_id.department_id.location_dest_id.id ,
                                'location_dest_id': rec.damage_line_id.department_id.stock_location_id.id,
                                #'exchange_line_id': line.id,
                                'tracking_id': False,
                                'state': 'draft',
                                'note': '',
                                'price_unit': line.product_id.standard_price or 0.0,
                                'move_type': 'one',
                            }            
    
                        lines.append([0, False, lines_dict])

                if lines:
                    piking_dict = {
                                'name': '/',
                                #'origin': order.name,
                                #'request': order.id,
                                'date': time.strftime('%Y-%m-%d'),
                                'type': 'in',
                                'state': 'draft',
                                #'exchange_id': order.id,
                                'job_id': rec.id,
                                'maintenance': True,
                                'note': '',
                                'department_id':rec.damage_line_id.department_id.department_id.id,
                                #'stock_journal_id':order.stock_journal_id and order.stock_journal_id.id,
                                'invoice_state': 'none',
                                'move_lines': lines,
                                'state': 'draft'
                            }
                    new_id = self.pool.get('stock.picking.in').create(cr, uid, piking_dict, context)
                    wf_service.trg_validate(uid, 'stock.picking', new_id, 'button_confirm', cr)
                    self.write(cr, uid, ids, {'state': 'return','picking_id':new_id})
                    continue
                else:
                    self.write(cr, uid, ids, {'state': 'canceled'})

        return True


class maintenance_spare(osv.Model):
    _name = "maintenance.spare"

    def _get_damages(self, cr, uid, ids, field, args, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context=context):
            res[rec.id] = [ [6, False, [x.id for x in rec.job_id.damages_ids] ] ]
        
        return res
    _columns = {
        'product_id': fields.many2one('product.product', string='Spare'),
        'quantity': fields.integer('Quantity'),
        'recieved_quantity': fields.integer('Recievesd Quantity'),
        'job_id': fields.many2one('maintenance.job', 'Job'),
        'vehicle_id': fields.related('job_id', 'vehicle_id', string='Vehicle', type="many2one", relation='fleet.vehicle', store=True),
        'process_ref': fields.related('job_id', 'process_ref', string='Process Referance', type="char", store=True),
        'start_datetime': fields.related('job_id', 'start_datetime', string='Start Datetime', type="datetime", store=True),
        'end_datetime': fields.related('job_id', 'end_datetime', string='End Datetime', type="datetime", store=True),
        #'damage_id': fields.related('job_id', 'damage_id', string='Damage', type="many2one", relation='maintenance.damage', store=True),
        'damages_ids': fields.function(_get_damages, type="many2many", relation="maintenance.damage", string="Damages"),
        'job_state': fields.related('job_id', 'state', string='state', type="selection", selection=[('draft', 'Draft'), ('requested', 'Stock Requested'), ('done', 'Done'), ('canceled', 'Canceled')], store=False),
    }

    _sql_constraints = [
        ('check_quantity_bigger_than_zero', "CHECK(quantity > 0)",
         _("The Quantity Must Be Bigger than Zero")),
    ]


class fleet_vehicle(osv.Model):
    _name = "fleet.vehicle"
    _inherit = "fleet.vehicle"
    _columns = {
        'maintenance_spare_ids': fields.one2many('maintenance.spare', 'vehicle_id', string="Maintenances",  domain=[('job_state', '=', 'done')]),
        'odometer': fields.float('Odometer',digits=(6, 2)),
        'machine_type': fields.many2one('machine.type', 'Machine Type'),
        'wheel_type': fields.many2one('wheel.type', 'Wheel Type'),

    }


class maintenance_request(osv.Model):
    _name = "maintenance.request"
    _rec_name = 'ref'

    def _get_recieve_datetime(self, cr, uid, ids, args, fields, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context=context):
            res[rec.id] = False
            try:
                recieve_time = rec.recieve_time
                hour = int(recieve_time)
                min = recieve_time - hour
                min = 60 * min
                hour = "%02d" %(hour,)
                min = "%02d" %(min,)

                recieve_time = ' '+hour+':'+min+':00'

                recieve_datetime = rec.recieve_date + recieve_time
                res[rec.id] = recieve_datetime
            except:
                pass
        return res
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'ref': fields.char('Referance'),
        'vehicle_id': fields.many2one('fleet.vehicle', 'Vehicle'),

        'odometer': fields.float('Odometer',digits=(6, 2)),
        'odometer_unit': fields.selection([('kilometers', 'Kilometers'), ('miles', 'Miles')], 'Odometer Unit', help='Unit of the odometer '),

        'vehicle_id_employee_id': fields.related('vehicle_id', 'employee_id', string='Requester', type="many2one", relation='hr.employee', store=True),

        'vehicle_id_department_id': fields.related('vehicle_id', 'department_id', string='Requester Department', type="many2one", relation='hr.department', store=True),

        'vehicle_id_vin_sn': fields.related('vehicle_id', 'vin_sn', string='Chassis Number', type="char", store=True),
        'request_datetime': fields.datetime('Request Datetime'),
        'recieve_datetime': fields.function(_get_recieve_datetime, type='datetime', string='Recieve Datetime'),
        'recieve_date': fields.date('Recieve Date'),
        'recieve_time': fields.float('Recieve time'),
        'end_datetime': fields.datetime('End Datetime'),
        'maintenance_time': fields.char('Maintenance Period'),
        'description': fields.text('Description'),
        'department_id': fields.many2one('maintenance.department', 'Maintenance Department'),
        'damage_lines_ids': fields.one2many('maintenance.damage.line', 'process_id', string="Damages"),
        'company_id': fields.many2one('res.company', string='Company', required=True),
        'state': fields.selection([('draft', 'Draft'), ('requested', 'Waiting Reciption'), ('in_reciption', 'In Reciption'), ('process', 'Progress'), ('done', 'Done'), ('canceled', 'Canceled')], string="State"),
        'out_source':fields.boolean(string='out source'),

        'machine_type': fields.related('vehicle_id', 'machine_type', string='Machine Type', type="many2one", relation='machine.type', store=True),
        'wheel_type': fields.related('vehicle_id', 'wheel_type', string='Wheel Type', type="many2one", relation='wheel.type', store=True),
   }

    def _get_emp(self, cr, uid, ids, context=None):
        emp_id = False
        emp_id = self.pool.get('hr.employee').search(
            cr, uid, [('user_id', '=', uid)])
        emp_id = emp_id and emp_id[0] or False
        return emp_id
    _defaults = {
        'employee_id': _get_emp,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'maintenance.request', context=c),
        'state': 'draft',
    }

    def _check_date(self, cr, uid, ids, context=None):
        """
        Check the value of request_datetime if greater than expiration_date or not.

        @return: Boolean of True or False
        """
        for act in self.browse(cr, uid, ids, context):
            if act.odometer < 0:
                 raise osv.except_osv(
                    _('Error'), _("Odometer should be equal to or more than zero"))
            if ((act.request_datetime > act.recieve_datetime) and act.recieve_datetime):
                raise osv.except_osv(
                    _(''), _("Request Datetime Must Be Less Than Recieve Datetime!"))
        return True

    _constraints = [
        (_check_date, _(''), ['request_datetime', 'recieve_datetime', 'odometer', 'recieve_date', 'recieve_time']), ]

    def create(self, cr, uid, vals, context=None):
        """
        Method thats overwrite the create method and naming the request by adding its sequence to the ref.

        @param vals: Values that have been entered
        @return: super create method
        """
        vals.update({'ref': self.pool.get('ir.sequence').get(
            cr, uid, 'maintenance.request')})
        vals['description'] = vals['description'].strip()
        if not vals['description']:
                raise osv.except_osv(
                    _('Error'), _("You should write description"))

        new_id = super(maintenance_request, self).create(
            cr, uid, vals, context=context)
        for rec in self.browse(cr , uid , [new_id]):
            if not rec.odometer_unit:
                rec.write({'odometer_unit': rec.vehicle_id.odometer_unit})
            if not rec.odometer:
                rec.write({'odometer': rec.vehicle_id.odometer})
            if rec.out_source:
                self.pool.get('vehicle.accident').write(cr , uid , [context['accident_id']] , {'maintenance_id' : new_id})
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        
        if 'description' in vals:
            vals['description'] = vals['description'].strip()
            if not vals['description']:
                raise osv.except_osv(
                    _('Error'), _("You should write description"))
        new_id = super(maintenance_request, self).write(
            cr, uid, ids, vals, context=context)
        rec = self.browse(cr, uid, ids[0])
        if rec.state != 'draft':
            if 'odometer_unit' in vals:
                rec.vehicle_id.write({'odometer_unit': vals['odometer_unit']})
            if 'odometer' in vals:
                rec.vehicle_id.write({'odometer': vals['odometer']})

        if 'vehicle_id' in vals:
            vehicle_obj = self.pool.get('fleet.vehicle')
            vehicle_rec = vehicle_obj.browse(cr, uid, vals['vehicle_id'])
            rec.write({'odometer_unit': vehicle_rec.odometer_unit})
            rec.write({'odometer': vehicle_rec.odometer})

        return new_id

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Override copy function to edit default value.

        @param default : default vals dict
        @return: super copy() method
        """
        raise osv.except_osv(_('Warning!'), _('You cannot duplicate record.'))
        return super(maintenance_request, self).copy(cr, uid, id, default, context)

    def unlink(self, cr, uid, ids, context=None):
        """
        @return: super unlink() method
        """
        for rec in self.browse(cr, uid, ids):
            if rec.state != 'draft':
                raise osv.except_osv(_('Invalid Action Error'), _(
                            'You can not delete record not in the draft state'))
            for line in rec.damage_lines_ids:
                for job in line.job_ids:
                    if job.state != 'draft':
                        raise osv.except_osv(_('Invalid Action Error'), _(
                            'can not delete this request before set to draft all it\'s jobs'))
                line.unlink()
        return super(maintenance_request, self).unlink(cr, uid, ids, context=context)

    def done(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context):
            for line in rec.damage_lines_ids:
                if not line.job_ids:
                    raise osv.except_osv(_('Invalid Action Error'), _(
                        'can not complete this request before all damages have completed jobs'))
                for job in line.job_ids:
                    if job.state != 'done':
                        raise osv.except_osv(_('Invalid Action Error'), _(
                            'can not complete this request before complete all it\'s jobs'))
            rec_datetime = rec.recieve_datetime
            rec_datetime = datetime.strptime(rec_datetime, '%Y-%m-%d %H:%M:%S')

            current_datetime = time.strftime('%Y-%m-%d %H:%M:%S')
            current_datetime = datetime.strptime(
                current_datetime, '%Y-%m-%d %H:%M:%S')
            if rec_datetime > current_datetime:
                raise osv.except_osv(_('Invalid Action Error'), _(
                    'Recieve Datetime can not be greater than current datetime'))
            period = str(current_datetime - rec_datetime)
            rec.write({'maintenance_time': period,
                       'end_datetime': current_datetime})
        self.write(cr, uid, ids, {'state': 'done'})

    def cancel(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for rec in self.browse(cr, uid, ids, context=context):
            for line in rec.damage_lines_ids:
                for job in line.job_ids:
                    if job.state == 'done':
                        raise osv.except_osv(_('Invalid Action Error'), _(
                            'can not cancel job in done state'))
                    wf_service.trg_validate(
                        uid, 'maintenance.job', job.id, 'cancel', cr)
        return self.write(cr, uid, ids, {'state': 'canceled'})

    def draft(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for rec in self.browse(cr, uid, ids, context=context):
            for line in rec.damage_lines_ids:
                for job in line.job_ids:
                    wf_service.trg_validate(
                        uid, 'maintenance.job', job.id, 'draft', cr)
        return self.write(cr, uid, ids, {'state': 'draft'})

    def requested(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'requested', 'request_datetime': time.strftime('%Y-%m-%d %H:%M:%S'), 'recieve_datetime': False})
    
    def in_reciption(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            if rec.odometer_unit:
                rec.vehicle_id.write({'odometer_unit': rec.odometer_unit})
            if rec.odometer:
                rec.vehicle_id.write({'odometer': rec.odometer})
            if not rec.odometer_unit:
                rec.write({'odometer_unit': rec.vehicle_id.odometer_unit})
            if not rec.odometer:
                rec.write({'odometer': rec.vehicle_id.odometer})
        return self.write(cr, uid, ids, {'state': 'in_reciption'})


class product_product(osv.Model):
    _name = "product.product"
    _inherit = "product.product"

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        """
        Method that overwrites name_search method Search for employee (only employees 
        that requested trainings) and their display name.

        @param name: Object name to search
        @param args: List of tuples specifying search criteria
        @param operator: Operator for search criterion
        @param limit: Max number of records to return
        @return: Super name_search method 
        """
        if context is None:
            context = {}

        if 'default_spare_ok' in context:
            ids = []
            ids = self.search(cr, uid, [('name', operator, name)]+ args, limit=limit, context=context)
            ids += self.search(cr, uid, [('e_name', operator, name)]+ args, limit=limit, context=context)
            ids += self.search(cr, uid, [('t_number', operator, name)]+ args, limit=limit, context=context)
            ids += self.search(cr, uid, [('default_code', operator, name)]+ args, limit=limit, context=context)
            ids = list(set(ids))
            args.append(('id','in',ids))

            if 'spares_ids' in context:
                idss = []
                product_ids = resolve_o2m_operations(cr, uid, self.pool.get('maintenance.spare'),
                                                     context.get('spares_ids'), ["product_id"], context)
                args.append(('id', 'not in', [isinstance(
                    d['product_id'], tuple) and d['product_id'][0] or d['product_id'] for d in product_ids]))

                '''if 'vehicle_id' in context and context['vehicle_id']:
                    vehicle_category = self.pool.get('fleet.vehicle').browse(cr, uid, context['vehicle_id'], context).type.id
                    if vehicle_category:
                        #idss = self.search(cr, uid, [('vehicle_category','=',vehicle_category)])
                        idss = self.search(cr, uid, [('vehicle_category_ids','in',[vehicle_category])])'''
                #args.append(('id','in',idss))
            if ids :
                result = self.name_get(cr, uid, ids, context=context)
                return result
            else:
                return []
        else:
            return super(product_product, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)


class stock_location(osv.Model):
    _name = "stock.location"
    _inherit = "stock.location"
    _columns = {
        'is_maintenance_location': fields.boolean('Maintenance Loaction'),
    }
