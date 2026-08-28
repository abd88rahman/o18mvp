from docutils.core import publish_parts

from odoo import fields, models
from odoo.modules.module import get_module_resource


class HelpGuide(models.Model):
    _name = 'c18.help.guide'
    _description = 'Help Guide Viewer'
    _order = 'filename'

    name = fields.Char(required=True)
    filename = fields.Char(required=True, help='Nama file .rst relatif ke static/docs/ modul ini.')
    content = fields.Html(compute='_compute_content', readonly=True, sanitize=False)

    def _compute_content(self):
        # File .rst dibaca & di-render on-the-fly tiap kali form dibuka - tidak
        # ditulis ulang, tidak ada file HTML perantara yang disimpan.
        for rec in self:
            rec.content = rec._render_rst()

    def _render_rst(self):
        self.ensure_one()
        rst_path = get_module_resource('c18_help', 'static', 'docs', self.filename)
        with open(rst_path, encoding='utf-8') as f:
            rst_source = f.read()
        parts = publish_parts(
            source=rst_source, writer_name='html5',
            settings_overrides={'input_encoding': 'utf-8', 'report_level': 5},
        )
        # parts['stylesheet'] sudah termasuk tag <style>...</style> sendiri (docutils
        # menyiapkannya buat ditaruh di <head>), jangan dibungkus <style> lagi.
        return f"{parts['stylesheet']}{parts['html_body']}"
