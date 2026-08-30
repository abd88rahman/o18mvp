/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { Component, onWillStart, useState } from "@odoo/owl";

export class C18IncomeStatementReport extends Component {
    static template = "c18_basic_erp.IncomeStatementReport";
    static props = ["*"];

    setup() {
        this.state = useState({
            loading: true,
            data: null,
            dateFrom: null,
            dateTo: null,
            costCenterId: null,
            hideZero: true,
        });
        onWillStart(() => this.fetchData());
    }

    async fetchData() {
        this.state.loading = true;
        try {
            const data = await rpc("/c18_basic_erp/report/income_statement", {
                date_from: this.state.dateFrom,
                date_to: this.state.dateTo,
                cost_center_id: this.state.costCenterId,
                hide_zero: this.state.hideZero,
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

    onCostCenterChange(ev) {
        this.state.costCenterId = ev.target.value || null;
        this.fetchData();
    }

    onHideZeroChange(ev) {
        this.state.hideZero = ev.target.checked;
        this.fetchData();
    }

    get costCenterOptions() {
        return this.state.data?.filters?.cost_center_options || [];
    }
}

registry.category("actions").add("c18_income_statement_report", C18IncomeStatementReport);
