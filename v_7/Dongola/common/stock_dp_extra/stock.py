# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Ian Li @ Elico Corp(<http://www.openerp.net.cn>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import decimal_precision as dp
from osv import fields, osv

#FIXME: Depend on stock
#TODO: 


class stock_move(osv.osv):
    """
    Inherit stock move model to set digits_compute is stock move Instead of Product
    Price in price_unit field.
    """

    _inherit = "stock.move"
    _name = "stock.move"

    _columns = {
        'price_unit': fields.float('Unit Price', digits_compute= dp.get_precision('Stock Move'), help="Technical field used to record the product cost set by the user during a picking confirmation (when average price costing method is used)"),
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
