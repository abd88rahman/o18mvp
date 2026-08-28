import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { user } from "@web/core/user";

// Landing page saat app icon ERP diklik - lihat erd/base/02-tema-menu.md.
// Tanpa ini, webclient auto-drill ke action pertama yang ditemukan di
// pohon menu (form Jurnal Umum), yang membingungkan sebagai first-impression.
// Sengaja generic/tanpa quick-link ke menu spesifik c18_basic_erp - c18_theme
// adalah base layer, tidak boleh tahu menu/action milik modul app/mvp
// (lihat 3-layer addons_path di erd/base).
export class ErpHomeDashboard extends Component {
    static template = "c18_theme.HomeDashboard";
    static props = ["*"];

    setup() {
        // "user" bukan service (useService), melainkan singleton dari
        // @web/core/user - beda dari "company" di bawah yang memang service.
        this.user = user;
        this.company = useService("company").currentCompany;
    }
}

registry.category("actions").add("c18_theme_home_dashboard", ErpHomeDashboard);
