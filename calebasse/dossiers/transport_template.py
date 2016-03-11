# -*- coding: utf-8 -*-

import os
import tempfile

#import cairo
#import pango
##import pangocairo

from ..pdftk import PdfTk


class TransportTemplate(object):
    fields = {
            'NOM_BENEFICIAIRE': {
                'pos': (302, 172),
            },
            'PRENOM_BENEFICIAIRE': {
                'pos': (136, 186),
            },
            'DATE': {
                'pos': (530, 582),
                'size': 7,
            },
            'LIEU': {
                'pos': (591, 583),
                'size': 7,
            },
            'IDENTIFICATION_ETABLISSEMENT': {
                'type': 'multiline',
                'pos': (510, 638),
            },
            'NIR_ASSURE': {
                'pos': (325, 781),
                'size': 10,
            },
            'NIR_KEY_ASSURE': {
                'pos': (527, 781),
                'size': 10,
            },
            'NOM_ASSURE': {
                'pos': (492, 805),
            },
            'CODE_ORGANISME_1': {
                'pos': (328, 832),
                'size': 10,
            },
            'CODE_ORGANISME_2': {
                'pos': (357, 832),
                'size': 10,
            },
            'CODE_ORGANISME_3': {
                'pos': (401, 832),
                'size': 10,
            },
            'ADRESSE_BENEFICIAIRE': {
                'pos': (94, 873),
            },
            'SITUATION_CHOICE_1': {
                'pos': (386, 241),
                'type': 'bool',
            },
            'SITUATION_CHOICE_2': {
                'pos': (386, 262),
                'type': 'bool',
            },
            'SITUATION_CHOICE_3': {
                'pos': (711, 240),
                'type': 'bool',
            },
            'SITUATION_CHOICE_4': {
                'pos': (711, 259),
                'type': 'bool',
            },
            'SITUATION_DATE': {
                'pos': (606, 280),
                'size': 8,
            },
            'TRAJET_TEXT': {
                'pos': (84, 320),
                'size': 8,
            },
            'TRAJET_CHOICE_1': {
                'pos': (193, 375),
                'type': 'bool',
            },
            'TRAJET_CHOICE_2': {
                'pos': (441, 375),
                'type': 'bool',
            },
            'TRAJET_CHOICE_3': {
                'pos': (711, 376),
                'type': 'bool',
            },
            'TRAJET_NUMBER': {
                'pos': (308, 383),
                'size': 8,
            },
            'PC_CHOICE_1': {
                'pos': (564, 410),
                'type': 'bool',
            },
            'PC_CHOICE_2': {
                'pos': (638, 410),
                'type': 'bool',
            },
            'MODE_CHOICE_1': {
                'pos': (320, 473),
                'type': 'bool',
            },
            'MODE_CHOICE_2': {
                'pos': (320, 488),
                'type': 'bool',
            },
            'MODE_CHOICE_3': {
                'pos': (320, 504),
                'type': 'bool',
            },
            'MODE_CHOICE_4': {
                'pos': (564, 517),
                'type': 'bool',
            },
            'MODE_CHOICE_5': {
                'pos': (638, 517),
                'type': 'bool',
            },
            'MODE_CHOICE_6': {
                'pos': (320, 536),
                'type': 'bool',
            },
            'CDTS_CHOICE_1': {
                'pos': (400, 552),
                'type': 'bool',
            },
            'CDTS_CHOICE_2': {
                'pos': (661, 552),
                'type': 'bool',
            },
    }

    def __init__(self, template_path=None, prefix='tmp', suffix=''):
        self.prefix = prefix
        self.suffix = suffix
        self.template_path = template_path

    def draw_field(self, ctx, field, value, size=9):
        _type = field.get('type', 'text')
        size = field.get('size', size)
        if _type == 'bool':
            x, y = field['pos']
            if value:
                ctx.move_to(x, y - 10)
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
                ctx.rectangle(x - 2, y - 2, width + 4, height + 4)
                ctx.fill()
                ctx.set_source_rgb(0, 0, 0)
                ctx.rectangle(x - 2, y - 2, width + 4, height + 4)
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
                            'size': size,
                    }
                    self.draw_field(ctx, sub, v, 7)
                y += field['lineheight']

    def draw_grid(self, ctx):
        ctx.set_source_rgb(0, 0, 0)
        for i in range(0, 827, 100):
            ctx.move_to(i, 5)
            ctx.show_text(str(i // 100));
            ctx.move_to(i, 0)
            ctx.line_to(i, 1169)
            ctx.stroke()
        for i in range(0, 1169, 100):
            ctx.move_to(0, i-5)
            ctx.show_text(str(i // 100))
            ctx.move_to(0, i)
            ctx.line_to(827, i)
            ctx.stroke()

    def generate(self, content, delete=True):
        width, height = 827, 1169
        with tempfile.NamedTemporaryFile(prefix=self.prefix,
                suffix=self.suffix, delete=False) as temp_out_pdf:
            try:
                overlay = tempfile.NamedTemporaryFile(prefix='overlay',
                        suffix='.pdf')
                surface = cairo.PDFSurface(overlay.name, width, height)
                ctx = cairo.Context(surface)
                ctx.set_source_rgb(0, 0, 0)
                for key, value in content.iteritems():
                    field = self.fields[key]
                    self.draw_field(ctx, field, value)
                ctx.show_page()
                surface.finish()
                pdftk = PdfTk()
                pdftk.background(overlay.name, self.template_path,
                    temp_out_pdf.name)
                overlay.close()
                return temp_out_pdf.name
            except:
                if delete:
                    try:
                        os.unlink(temp_out_pdf.name)
                    except:
                        pass
                raise
