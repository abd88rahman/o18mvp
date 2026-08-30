/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ErpHomeDashboard } from "@c18_theme/js/home_dashboard";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";
import { onWillStart, useState } from "@odoo/owl";

// c18_theme (base layer) sengaja tidak tahu menu/model c18_basic_erp - lihat
// komentar di home_dashboard.js. Breakdown count per form ditambah dari sini
// (c18_basic_erp, layer mvp) via OWL patch(), bukan edit langsung file
// c18_theme (pola sama dgn c18_theme/messaging_menu_patch.js yang nge-patch
// MessagingMenu punya modul mail).
patch(ErpHomeDashboard.prototype, {
    setup() {
        super.setup();
        this.dashboardActionService = useService("action");
        this.dashboardState = useState({ sections: null });
        onWillStart(async () => {
            this.dashboardState.sections = await rpc("/c18_basic_erp/dashboard/counts");
        });
    },

    get dashboardSectionList() {
        return this.dashboardState.sections ? Object.values(this.dashboardState.sections) : [];
    },

    openDashboardItem(xmlid) {
        if (xmlid) {
            this.dashboardActionService.doAction(xmlid);
        }
    },
});
