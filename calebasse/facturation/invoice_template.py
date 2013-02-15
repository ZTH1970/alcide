# -*- coding: utf-8 -*-

import os
import tempfile

import cairo
import pango
import pangocairo
import pyPdf
from StringIO import StringIO

from ..pdftk import PdfTk


class InvoiceTemplate(object):
    fields = {
            'NUM_FINESS': {
                'type': 'text',
                'pos': (380, 72),
            },
            'NUM_LOT': {
                'type': 'text',
                'pos': (570, 85),
            },
            'NUM_FACTURE': {
                'type': 'text',
                'pos': (570, 96),
            },
            'NUM_ENTREE': {
                'type': 'text',
                'pos': (570, 107),
            },
            'ABSENCE_SIGNATURE': {
                'type': 'bool',
                'pos': (672.5, 130),
            },
            'IDENTIFICATION_ETABLISSEMENT': {
                'type': 'multiline',
                'pos': (45, 85),
            },
            'DATE_ELABORATION': {
                'type': 'text',
                'pos': (720, 58),
            },
            'NOM_BENEFICIAIRE': {
                'pos': (150, 144),
            },
            'NIR_BENEFICIAIRE': {
                'pos': (130, 163),
            },
            'DATE_NAISSANCE_RANG': {
                'pos': (350 ,163),
            },
            'CODE_ORGANISME': {
                'pos': (170, 175),
            },
            'DATE_ENTREE': {
                'pos': (92, 187),
            },
            'DATE_SORTIE': {
                'pos': (360, 187),
            },
            'NOM_ASSURE': {
                'pos': (530, 144),
            },
            'NIR_ASSURE': {
                'pos': (520, 163),
            },
            'ADRESSE_ASSURE': {
                'pos': (460, 177),
            },
            'TABLEAU1': {
                'type': 'array',
                'size': 6,
                'y': 323,
                'lineheight': 12,
                'cols': [
                    38,
                    65,
                    91.5,
                    114,
                    172,
                    240,
                    303,
                    333,
                    414.5] },
            'TABLEAU2': {
                'type': 'array',
                'size': 6,
                'y': 323,
                'lineheight': 12,
                'x': 395.5,
                'cols': [
                    38,
                    65,
                    91.5,
                    114,
                    172,
                    240,
                    303,
                    333,
                    414.5] },
            'SOUS_TOTAL1': {
                    'pos': (340, 475),
            },
            'SOUS_TOTAL2': {
                    'pos': (740, 475),
            },
            'TOTAL': {
                    'pos': (330, 500),
            },
            'COUNTER': {
                    'pos': (800, 570),
            },
            'SUBTITLE': {
                    'pos': (300, 50),
                    'size': 10,
                    'border': True,
            },
    }

    def __init__(self, template_path=None, prefix='tmp', suffix=''):
        self.prefix = prefix
        self.suffix = suffix
        self.template_path = template_path

    def draw_field(self, ctx, field, value, size=7):
        _type = field.get('type', 'text')
        size = field.get('size', size)
        if _type == 'bool':
            x, y = field['pos']
            if value:
                ctx.move_to(x, y-10)
                pangocairo_context = pangocairo.CairoContext(ctx)
                pangocairo_context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

                layout = pangocairo_context.create_layout()
                font = pango.FontDescription("Georgia %s" % size)
                layout.set_font_description(font)

                layout.set_text(u'\u2714')
                pangocairo_context.update_layout(layout)
                pangocairo_context.show_layout(layout)
        if _type in ('text', 'multiline'):
            x, y = field['pos']
            ctx.move_to(x, y)
            pangocairo_context = pangocairo.CairoContext(ctx)
            pangocairo_context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

            layout = pangocairo_context.create_layout()
            font = pango.FontDescription("Georgia Bold %s" % size)
            layout.set_font_description(font)

            layout.set_text(unicode(value))
            pangocairo_context.update_layout(layout)
            if field.get('border'):
                a, b, width, height = layout.get_pixel_extents()[1]
                ctx.save()
                ctx.set_source_rgb(1, 1, 1)
                ctx.rectangle(x-2, y-2, width+4, height+4)
                ctx.fill()
                ctx.set_source_rgb(0, 0, 0)
                ctx.rectangle(x-2, y-2, width+4, height+4)
                ctx.set_line_width(0.1)
                ctx.stroke()
                ctx.restore()
            ctx.move_to(x, y)
            pangocairo_context.show_layout(layout)
        if _type == 'array':
            field = field.copy()
            y = field['y']
            offset = field.get('x', 0)
            for row in value:
                for x, v in zip(field['cols'], row):
                    sub = {
                            'pos': (offset+x, y),
                            'size': size,
                    }
                    self.draw_field(ctx, sub, v, 7)
                y += field['lineheight']

    def generate(self, content, delete=True):
        width, height = 842,595
        with tempfile.NamedTemporaryFile(prefix=self.prefix,
                suffix=self.suffix, delete=False) as temp_out_pdf:
            try:
                overlay = tempfile.NamedTemporaryFile(prefix='overlay',
                        suffix='.pdf')
                surface = cairo.PDFSurface (overlay.name, width, height)
                ctx = cairo.Context (surface)
                ctx.set_source_rgb(0, 0, 0)
                for key, value in content.iteritems():
                    field = self.fields[key]
                    self.draw_field(ctx, field, value)
                ctx.show_page()
                surface.finish()
                pdftk = PdfTk()
                pdftk.background(overlay.name, self.template_path, temp_out_pdf.name)
                overlay.close()
                return temp_out_pdf.name
            except:
                if delete:
                    try:
                        os.unlink(temp_out_pdf.name)
                    except:
                        pass
                raise
