from osv import fields,osv
import tools

class vehicles_fuel_details_report(osv.osv):
    _name = "vehicles.fuel.details.report"
    _description = "Purchases Orders"
    _auto = False
    _columns = {
        'date': fields.date('Order Date', readonly=True, help="Date on which this document has been created"),
        'name': fields.char('Year',size=64,required=False, readonly=True),
        'day': fields.char('Day', size=128, readonly=True),
        'product_id':fields.many2one('product.product', 'Product', readonly=True),
        'emp_id' :fields.many2one('hr.employee', 'Employee', readonly=True),
        'department_id':fields.many2one('hr.department', 'Department',readonly=True ),
        'car': fields.many2one('account.asset.asset', 'Car Name',readonly=True),
        'code': fields.related('car', 'plate_no', type='char', relation='account.asset.asset', string='Car Number', readonly=True, store=True),    
        'product_uom' : fields.many2one('product.uom', 'Reference UoM', required=True),
        'company_id':fields.many2one('res.company', 'Company', readonly=True),
        'user_id':fields.many2one('res.users', 'Responsible', readonly=True),
        'quantity': fields.float('Quantity', readonly=True),
        'nbr': fields.integer('# of Lines', readonly=True),
        'month':fields.selection([('01','January'), ('02','February'), ('03','March'), ('04','April'), ('05','May'), ('06','June'),
                          ('07','July'), ('08','August'), ('09','September'), ('10','October'), ('11','November'), ('12','December')],'Month',readonly=True),
        'category_id': fields.many2one('product.category', 'Category', readonly=True)

    }
    _order = 'name desc'
    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'vehicles_fuel_details_report')
        cr.execute("""
            create or replace view vehicles_fuel_details_report as (
                select
                    min(l.id) as id,
                    s.date as date,
                    to_char(s.date, 'YYYY') as name,
                    to_char(s.date, 'MM') as month,
                    to_char(s.date, 'YYYY-MM-DD') as day,
                    s.department_id,
                    s.car,
                    s.code,
                    s.emp_id as emp_id,
                    s.create_uid as user_id,
                    s.company_id as company_id,
                    l.product_id,
                    t.categ_id as category_id,
                    t.uom_id as product_uom,
                    sum(l.product_qty/u.factor*u2.factor) as quantity,
                    count(*) as nbr

                from vehicles_fuel_details s
                    left join fuel_details_lines l on (s.id=l.fuel_id)
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    left join product_uom u on (u.id=l.product_uom)
                    left join product_uom u2 on (u2.id=t.uom_id)
                where l.product_id is not null
                group by
                    s.company_id,
                    s.create_uid,
                    s.emp_id,
                    l.product_qty,
                    u.factor,
                    l.product_uom,
                    s.department_id,
                    s.code,
                    s.car,
                    l.product_id,
                    t.categ_id,
                    s.date,
                    to_char(s.date, 'YYYY'),
                    to_char(s.date, 'MM'),
                    to_char(s.date, 'YYYY-MM-DD'),
                    u.uom_type, 
                    u.category_id,
                    t.uom_id,
                    u.id,
                    u2.factor
            )
        """)
vehicles_fuel_details_report()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: