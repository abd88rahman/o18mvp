/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { Component, onWillStart, useState } from "@odoo/owl";

export class C18InventoryBalanceReport extends Component {
    static template = "c18_basic_erp.InventoryBalanceReport";
    static props = ["*"];

    setup() {
        this.state = useState({ loading: true, data: null });
        onWillStart(async () => {
            this.state.data = await rpc("/c18_basic_erp/report/inventory_balance", {});
            this.state.loading = false;
        });
    }
}

registry.category("actions").add("c18_inventory_balance_report", C18InventoryBalanceReport);
