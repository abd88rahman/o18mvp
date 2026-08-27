from lxml import html as lxml_html

import odoo
from odoo import http
from odoo.http import request
from odoo.tools.misc import file_open
from odoo.tools.translate import _
from odoo.addons.base.models.ir_qweb import render as qweb_render
from odoo.addons.web.controllers.database import Database

# Belum smoke test - lihat erd/base/01-branding-atribut.md poin 5 & "Catatan
# Teknis Penting" utk latar belakang desain (kenapa render statis, bukan
# ir.ui.view/ORM, dan kenapa c18_theme wajib ada di server_wide_modules).

GATE_SESSION_KEY = 'erp_db_manager_unlocked'
GATE_TEMPLATE_PATH = 'c18_theme/static/src/public/database_manager_gate.qweb.html'


class ErpDatabase(Database):

    def _erp_render_gate(self, error=None):
        with file_open(GATE_TEMPLATE_PATH, 'r') as fd:
            template_str = fd.read()

        def load(template_name):
            return (lxml_html.document_fromstring(template_str), template_name)

        return qweb_render('database_manager_gate', {'error': error}, load)

    @http.route('/web/database/manager', type='http', auth='none', methods=['GET', 'POST'], csrf=False)
    def manager(self, **kw):
        if request.session.get(GATE_SESSION_KEY):
            return super().manager(**kw)

        master_pwd = kw.get('master_pwd')
        if master_pwd:
            try:
                odoo.service.db.check_super(master_pwd)
                request.session[GATE_SESSION_KEY] = True
                return super().manager(**kw)
            except odoo.exceptions.AccessDenied:
                return self._erp_render_gate(error=_('Master Password salah.'))

        return self._erp_render_gate()
