/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { Component, onWillStart, useState } from "@odoo/owl";

export class C18EquityChangesReport extends Component {
    static template = "c18_basic_erp.EquityChangesReport";
    static props = ["*"];

    setup() {
        this.state = useState({
            loading: true,
            data: null,
            dateFrom: null,
            dateTo: null,
        });
        onWillStart(() => this.fetchData());
    }

    async fetchData() {
        this.state.loading = true;
        try {
            const data = await rpc("/c18_basic_erp/report/equity_changes", {
                date_from: this.state.dateFrom,
                date_to: this.state.dateTo,
            });
            this.state.data = data;
            this.state.dateFrom = data.date_from;
            this.state.dateTo = data.date_to;
        } finally {
            this.state.loading = false;
        }
    }

    onDateFromChange(ev) {
        this.state.dateFrom = ev.target.value || null;
        this.fetchData();
    }

    onDateToChange(ev) {
        this.state.dateTo = ev.target.value || null;
        this.fetchData();
    }
}

registry.category("actions").add("c18_equity_changes_report", C18EquityChangesReport);
