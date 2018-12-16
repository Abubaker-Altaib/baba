from openerp.osv import fields,osv


class gds_res_partner(osv.Model):

    _name = "res.partner"
    _inherit = "res.partner"

    _columns = {
        'omda' : fields.boolean("Omda") ,
        'shikh' : fields.boolean('shikh') ,
    }

 