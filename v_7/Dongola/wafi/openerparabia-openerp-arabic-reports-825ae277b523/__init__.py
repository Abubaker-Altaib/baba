from reportlab.pdfgen import textobject
from reportlab.pdfbase import pdfmetrics

# Import Arabic support dependencies
import arabic_reshaper
from bidi.algorithm import get_display


# Reference the original PDFTextObject to avoid infinite recursion
RLPDFTextObject = textobject.PDFTextObject


class BiDiPDFTextObject(RLPDFTextObject):
    '''
    Extend reportlab PDFTextObjct to support bidirectional text.
    '''

    def __init__(self, canvas, x=0, y=0):
        self._code = ['BT']    #no point in [] then append RGB
        self._canvas = canvas  #canvas sets this so it has access to size info
        self._fontname = self._canvas._fontname
        self._fontsize = self._canvas._fontsize
        self._leading = self._canvas._leading
        self._doc = self._canvas._doc
        self._colorsUsed = self._canvas._colorsUsed
        self._enforceColorSpace = getattr(canvas,'_enforceColorSpace',None)
        font = pdfmetrics.getFont(self._fontname)
        self._curSubset = -1
        self.setTextOrigin(x, y)
        self._textRenderMode = 0
        self._clipping = 0

    def getCode(self):
        "pack onto one line; used internally"
        self._code.append('ET')
        if self._clipping:
            self._code.append('%d Tr' % (self._textRenderMode^4))
        return ' '.join(self._code)

    def setTextRenderMode(self, mode):
        # After we start clipping we must not change the mode back
        # until after the ET
        assert mode in (0,1,2,3,4,5,6,7), "mode must be in (0,1,2,3,4,5,6,7)"
        if (mode & 4) != self._clipping:
            mode |= 4
            self._clipping = mode & 4
        if self._textRenderMode != mode:
            self._textRenderMode = mode
            self._code.append('%d Tr' % mode)

    def _formatText(self, text):
        # Add Arabic support
        try:
            text = type(text) == type(u'') and text or text.decode('utf8')
            reshaped_text = arabic_reshaper.reshape(text)
            text = get_display(reshaped_text)
        except UnicodeDecodeError, e:
            i, j = e.args[2:4]
            raise UnicodeDecodeError(
                *(e.args[:4] + ('%s\n%s==[%s]==%s' % (e.args[4],
                    text[max(i - 10, 0):i], text[i:j], text[j:j + 10]), )))

        # PDFTextObjct is an oldstyle class: can't use super()
        return RLPDFTextObject._formatText(self, text)


# Monkey-patch reportlab to replace its PDFTextObjct with BiDiPDFTextObject
textobject.PDFTextObject = BiDiPDFTextObject


# Italic DefaVu does not work in Arabic, so replace it with bold
from openerp.report.render.rml2pdf import customfonts

customfonts.CustomTTFonts += [
    ('Helvetica',"DejaVu Sans Bold", "DejaVuSans-Bold.ttf", 'italic'),
    ('Helvetica',"DejaVu Sans Bold", "DejaVuSans-Bold.ttf", 'bolditalic'),
]
