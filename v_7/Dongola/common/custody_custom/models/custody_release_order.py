
from openerp.osv import fields, osv
from openerp import netsvc






class custody_release_order(osv.Model):


      _inherit = "custody.release.order"
      
      _columns = {
                  'state' : fields.selection([('draft','Draft'),('confirm','Confirmed'),('approve','Approved'),('approve_ghrm','GHRM Approved'),('verify' , 'Verified'),('release', 'Released'),('cancel','Cancelled')] , 'State' ),
                 }
      
      
      
      def approve(self,cr,uid,ids,context=None):
          for order in self.browse(cr, uid, ids, context=context):
              if not order.custody_lines:
                 raise osv.except_osv(_('Error !'), _('You Can not Confirm this order without items'))
          self.write(cr,uid,ids,{'state' : 'approve' },context=context)
          return True
      
      
      def approve_ghrm(self,cr,uid,ids,context=None):
          for order in self.browse(cr, uid, ids, context=context):
              if not order.custody_lines:
                 raise osv.except_osv(_('Error !'), _('You Can not Confirm this order without items'))
          self.write(cr,uid,ids,{'state' : 'approve_ghrm' },context=context)
          return True
      
      
      
      
      
      
      
      def action_prepare_incoming_shipment(self ,cr ,uid ,ids ,context=None):
        """
        inherit action_done function in stock picking class 
        and create custodies depend on some conditions 

        @return: True
        """

        pick , moves = super(custody_release_order, self).action_prepare_incoming_shipment(cr, uid, ids, context=context)

        picking_obj = self.pool.get('stock.picking')
        product_temp = self.pool.get('product.product')

        for rec in self.browse(cr,uid,ids):
            if len(moves) == 1:
                cat_id = product_temp.browse(cr ,uid ,moves[0]['product_id']).categ_id.id                
                pick['department_id'] = rec.department_id.id
                pick['category_id'] = cat_id
                pick['location_dest_id'] = rec.location_id.id

                 
            
            

        return pick , moves
