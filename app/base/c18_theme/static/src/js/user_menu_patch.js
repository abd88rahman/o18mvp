import { registry } from "@web/core/registry";

// Hapus item user menu yang mengarah ke ekosistem odoo.com / tidak relevan.
// Sisakan: shortcuts, profile (Preferences), log_out.
// Item asli terdaftar di addons/web/static/src/webclient/user_menu/user_menu_items.js
// (registry category "user_menuitems") - lihat erd/base/01-branding-atribut.md poin 6.
const userMenuRegistry = registry.category("user_menuitems");

["documentation", "support", "odoo_account", "install_pwa"].forEach((id) => {
    if (userMenuRegistry.contains(id)) {
        userMenuRegistry.remove(id);
    }
});
