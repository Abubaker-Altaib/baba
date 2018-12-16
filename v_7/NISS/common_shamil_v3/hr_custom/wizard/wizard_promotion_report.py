# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################


from osv import osv , fields
import time

class promotion_report(osv.osv_memory):
    _name = "promotion.report"
    
    
    _columns = {
		 'fromm': fields.date("Start Date", required= True),
	     'to' : fields.date("End Date" ,required= True),
   		 }
    
    def check_prev(self, cr, uid, ids):
        for day in self.browse(cr, uid, ids):
            if day.fromm > day.to :
                return False
        return True
    
    _constraints = [
        (check_prev, 'Sorry , Start_date must be before End_date !', ['Start_date','end_date']),
                  ] 

    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.process.archive',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'promotion.report',
            'datas': datas,
            }

promotion_report()