# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import fields, osv
import time
class injury_report(osv.osv_memory):
    _name = "injury.report"

    _columns = {
        'department_id': fields.many2many('hr.department','specific_dep_rel','injury_dept','dept_id', 'Department name',required=True ),
        'date_from' :fields.datetime("From", required=True),
        'date_to' :fields.datetime("TO", required=True),
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.injury',
             'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'injury.report',
            'datas': datas,
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
