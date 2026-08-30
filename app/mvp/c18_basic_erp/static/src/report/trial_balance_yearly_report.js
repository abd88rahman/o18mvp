/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { Component, onWillStart, useState } from "@odoo/owl";

const MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];

export class C18TrialBalanceYearlyReport extends Component {
    static template = "c18_basic_erp.TrialBalanceYearlyReport";
    static props = ["*"];

    setup() {
        this.monthLabels = MONTH_LABELS;
        this.state = useState({
            loading: true,
            data: null,
            year: null,
            costCenterId: null,
            hideZero: true,
        });
        onWillStart(() => this.fetchData());
    }

    async fetchData() {
        this.state.loading = true;
        try {
            const data = await rpc("/c18_basic_erp/report/trial_balance_yearly", {
                year: this.state.year,
                cost_center_id: this.state.costCenterId,
                hide_zero: this.state.hideZero,
            });
            this.state.data = data;
            this.state.year = data.year;
        } finally {
            this.state.loading = false;
        }
    }

    onYearChange(ev) {
        this.state.year = ev.target.value || null;
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

registry.category("actions").add("c18_trial_balance_yearly_report", C18TrialBalanceYearlyReport);
