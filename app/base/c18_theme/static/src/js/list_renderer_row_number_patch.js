/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";

// Odoo tidak punya kolom nomor baris bawaan di list view manapun (dicek
// langsung ke source core - list_renderer.js/.xml, tidak ada konsep index
// baris sama sekali). Ditambah GLOBAL di sini (bukan per-view) supaya
// konsisten di seluruh app, bukan cuma modul c18_basic_erp - makanya
// letaknya di c18_theme (base layer), pola sama dgn messaging_menu_patch.js
// (patch komponen core, bukan edit file aslinya).
// Matikan "magic column width" (heuristik lebar per tipe field, sering
// timpang - lihat diskusi user). Static property di CLASS-nya sendiri
// (bukan .prototype) - dibaca via "renderer.constructor.useMagicColumnWidths"
// di column_width_hook.js. Sisa lebar dibagi rata via CSS table-layout:fixed
// (list_view_tweaks.scss), kolom # tetap fix krn sudah punya width eksplisit.
patch(ListRenderer, {
    useMagicColumnWidths: false,
});

patch(ListRenderer.prototype, {
    get nbCols() {
        return super.nbCols + 1;
    },

    getGroupNameCellColSpan(group) {
        return super.getGroupNameCellColSpan(group) + 1;
    },

    getGroupPagerCellColspan(group) {
        return super.getGroupPagerCellColspan(group) + 1;
    },

    // "list" di sini bisa list utama (ungrouped) atau list.group saat grouped -
    // t-set="list" diteruskan otomatis oleh QWeb t-call ke RecordRow, sudah
    // dicek langsung ke source (web.ListRenderer.Rows).
    getRowNumber(list, record) {
        return (list.offset || 0) + list.records.indexOf(record) + 1;
    },
});
