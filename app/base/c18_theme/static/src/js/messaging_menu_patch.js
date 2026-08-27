import { MessagingMenu } from "@mail/core/public_web/messaging_menu";
import { patch } from "@web/core/utils/patch";

// Hapus tile "Install Odoo" di dropdown messaging menu. Ini BUKAN pesan chat
// asli dari OdooBot, melainkan item sintetis dari getter canPromptToInstall
// (addons/mail/static/src/core/web/messaging_menu_patch.js) yang terkait
// prompt install PWA - lihat erd/base/01-branding-atribut.md poin 7.
patch(MessagingMenu.prototype, {
    get canPromptToInstall() {
        return false;
    },
});
