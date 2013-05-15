# -*- coding: utf-8 -*-

import os
import tempfile

import cairo
import pango
import pangocairo

from ..pdftk import PdfTk


class TransportTemplate(object):
    fields = {
            'NOM_BENEFICIAIRE': {
                'pos': (302, 186),
            },
            'PRENOM_BENEFICIAIRE': {
                'pos': (136, 200),
            },
            'DATE': {
                'pos': (532, 597),
                'size': 8,
            },
            'LIEU': {
                'pos': (596, 597),
            },
            'IDENTIFICATION_ETABLISSEMENT': {
                'type': 'multiline',
                'pos': (510, 652),
            },
            'NIR_ASSURE': {
                'pos': (325, 800),
                'size': 10,
            },
            'NIR_KEY_ASSURE': {
                'pos': (527, 800),
                'size': 10,
            },
            'NOM_ASSURE': {
                'pos': (492, 825),
            },
            'CODE_ORGANISME_1': {
                'pos': (328, 850),
                'size': 10,
            },
            'CODE_ORGANISME_2': {
                'pos': (357, 850),
                'size': 10,
            },
            'CODE_ORGANISME_3': {
                'pos': (401, 850),
                'size': 10,
            },
            'ADRESSE_BENEFICIAIRE': {
                'pos': (92, 891),
            },
            'SITUATION_CHOICE_1': {
                'pos': (393, 264),
                'type': 'bool',
            },
            'SITUATION_CHOICE_2': {
                'pos': (393, 280),
                'type': 'bool',
            },
            'SITUATION_CHOICE_3': {
                'pos': (719, 264),
                'type': 'bool',
            },
            'SITUATION_CHOICE_4': {
                'pos': (719, 280),
                'type': 'bool',
            },
            'SITUATION_DATE': {
                'pos': (610, 299),
                'size': 8,
            },
            'TRAJET_TEXT': {
                'pos': (84, 340),
                'size': 8,
            },
            'TRAJET_CHOICE_1': {
                'pos': (201, 396),
                'type': 'bool',
            },
            'TRAJET_CHOICE_2': {
                'pos': (454, 396),
                'type': 'bool',
            },
            'TRAJET_CHOICE_3': {
                'pos': (719, 396),
                'type': 'bool',
            },
            'TRAJET_CHOICE_4': {
                'pos': (201, 419),
                'type': 'bool',
            },
            'TRAJET_NUMBER': {
                'pos': (305, 409),
                'size': 8,
            },
            'PC_CHOICE_1': {
                'pos': (567, 435),
                'type': 'bool',
            },
            'PC_CHOICE_2': {
                'pos': (642, 435),
                'type': 'bool',
            },
            'MODE_CHOICE_1': {
                'pos': (321, 484),
                'type': 'bool',
            },
            'MODE_CHOICE_2': {
                'pos': (321, 499),
                'type': 'bool',
            },
            'MODE_CHOICE_3': {
                'pos': (321, 515),
                'type': 'bool',
            },
            'MODE_CHOICE_4': {
                'pos': (568, 528),
                'type': 'bool',
            },
            'MODE_CHOICE_5': {
                'pos': (642, 528),
                'type': 'bool',
            },
            'MODE_CHOICE_6': {
                'pos': (321, 546),
                'type': 'bool',
            },
            'CDTS_CHOICE_1': {
                'pos': (404, 565),
                'type': 'bool',
            },
            'CDTS_CHOICE_2': {
                'pos': (567, 563),
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
                            'pos': (offset + x, y),
                            'size': size,
                    }
                    self.draw_field(ctx, sub, v, 7)
                y += field['lineheight']

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
