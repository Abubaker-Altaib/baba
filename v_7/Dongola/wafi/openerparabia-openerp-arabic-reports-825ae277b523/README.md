OpenERP Arabic Reports
======================

*No more patches!*

This is an [OpenERP](http://www.openerp.com) module that
monkey-patches OpenERP's default report engine, ReportLab, to add
support for rendering Arabic text. After installing this module, all
RML reports will render Arabic text correctly. No more disconnected
Arabic letters that go from left to right!

This module does not change the layout of existing reports. The
reports will remain left-to-right. Arabic text in the reports will be
fixed, though. To change the layout of the reports, they need to be
redesigned.

**Module name:** Arabic Support in RML Reports.

Tested with OpenERP 7.0.

Credits
-------

This module is based on the
[patch by Mohammed Barsi](https://github.com/barsi/openerp-rtl), which
uses two pieces to implement Arabic support:

- [python-bidi](https://pypi.python.org/pypi/python-bidi/):
   Bi-directional (BiDi) layout implementation in pure python.

- [Python Arabic Reshaper](https://github.com/mpcabd/python-arabic-reshaper):
  reshape Arabic characters and replace them with their correct shapes
  according to their surroundings.

This module is contributed by Ahmad Khayyat from
[MGK IT Consulting](http://www.mgkitconsulting.com).
