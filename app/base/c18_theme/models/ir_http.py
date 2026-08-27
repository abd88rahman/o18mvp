from odoo import models
from odoo.tools import config


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    # brand_name/brand_logo/brand_favicon dibaca dari odoo.conf (bukan hardcode
    # atau dari database) - lihat erd/base/01-branding-atribut.md.
    # Odoo otomatis menyimpan key custom yang tidak dikenal core lewat
    # config.get(), tanpa perlu register option baru.

    @classmethod
    def _erp_brand_name(cls):
        return config.get('brand_name', 'Odoo')

    @classmethod
    def _erp_brand_logo(cls):
        return config.get('brand_logo', 'logo_odoo.png')

    @classmethod
    def _erp_brand_favicon(cls):
        return config.get('brand_favicon', 'favicon_odoo.png')

    def _get_session_info(self):
        # sisi client (OWL/JS) tidak bisa baca odoo.conf langsung - diselipkan
        # lewat session_info supaya JS bisa akses session.erp_brand_name.
        session_info = super()._get_session_info()
        session_info['erp_brand_name'] = self._erp_brand_name()
        return session_info
