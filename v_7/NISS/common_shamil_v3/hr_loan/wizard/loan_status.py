# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from osv import fields, osv
import time

class loan_status(osv.osv_memory):
    _name = "loan.status"
    _columns = {
		 'company_id': fields.many2one('res.company', 'Company',required=True ),
	         'loan': fields.many2one('hr.loan', 'Loan',required=True ),
		  'start_date': fields.date("Start Date", required= True),
	         'end_date' : fields.date("End Date" ,required= True),
   	}
    _defaults = {
       
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'loan.status', context=c), 
	
    }
    _sql_constraints = [
       	 	('date_check', 'CHECK ( start_date < end_date)', "The start date must be anterior to the end date."),
    ]

    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.employee.loan',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'loan.status',
            'datas': datas,
            }

loan_status()

