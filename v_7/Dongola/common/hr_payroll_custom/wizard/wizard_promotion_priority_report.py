# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################


from osv import fields, osv
import time

class promo_rec(osv.osv_memory):
    _name = "promo.rec"

    _columns = {
              'job_id': fields.many2many('hr.job','jobs_emp_rel','employee_job_comp','job_emps_id', 'Job Name',required=True ),
             'payroll_id': fields.many2one('hr.salary.scale', 'Salary Scale',required=True ),
#              'degree': fields.many2one('hr2.degree.names', 'Degree Name',required=True ),
             'degree': fields.many2one('hr.salary.degree', 'Degree Name',required=True ),
         'from': fields.date("Start Date", required= True),
            'year': fields.integer('Year', required=True),
        
       }
    _defaults = {
        'year': int(time.strftime('%Y')),
        
    }
  
    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids':[],
             'model': 'hr.employee',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'promo.rec',
            'datas': datas,
            }

promo_rec()
