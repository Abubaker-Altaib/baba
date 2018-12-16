OpenERP Arabic Support
======================

***Note:*** This solution is for OpenERP 6.1. For OpenERP 7, there is
 a [better module-based solution](https://bitbucket.org/openerparabia/openerp-arabic-reports/).

This repository consists of a patch that fixes the Arabic language
support in [OpenERP](http://www.openerp.com/).

The patch is tested against a recent version of the 6.1 release
installed on Debian stable (Squeeze) using the Debian package
available on the
[OpenERP downloads page](http://www.openerp.com/downloads).

The patch specifically fixes two main issues by modifying the files
listed below (all paths are relative to `/usr/share/pyshared/`):

1. Incorrect Arabic language code, which breaks the Arabic translation
   on the web interface. This patch includes the patch suggested as a
   solution in
   [this bug report](https://bugs.launchpad.net/openobject-server/+bug/1019804),
   which affects the following files:

    - `openerp/tools/misc.py`
    - `openerp/tools/translate.py`

2. Missing Arabic characters in PDF reports. The patch modifies the
   following files in order to fix this issue:

    - `openerp/report/render/rml2pdf/__init__.py`
    - `openerp/report/render/rml2pdf/trml2pdf.py`
    - `reportlab/pdfgen/textobject.py`
    - `reportlab/platypus/paragraph.py`
    - `reportlab/rl_config.py`

These files belong to the following two packages:

- `openerp`
- `python-reportlab`

Steps
=====

1. Install `python-pyfribidi` and `ttf-dejavu` packages:

        $ sudo aptitude install python-pyfribidi ttf-dejavu

2. Download the patch:

        $ wget https://bitbucket.org/openerparabia/openerp-arabic-support/raw/tip/openerp-arabic-support.patch

    Alternatively, you can clone the repository, if you have the
    `mercurial` package installed:

        $ hg clone https://bitbucket.org/openerparabia/openerp-arabic-support

3. Apply the patch:

        $ sudo patch -d /usr/share/pyshared -p0 -N -r- -i $PWD/openerp-arabic-support.patch

    If successful, you should see the following output:

        patching file openerp/report/render/rml2pdf/__init__.py
        patching file openerp/report/render/rml2pdf/trml2pdf.py
        patching file openerp/tools/misc.py
        patching file openerp/tools/translate.py
        patching file reportlab/pdfgen/textobject.py
        patching file reportlab/platypus/paragraph.py
        patching file reportlab/rl_config.p

4. Restart the OpenERP server:

        $ sudo invoke-rc.d openerp restart
