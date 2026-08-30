/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { Component, onWillStart, useState } from "@odoo/owl";

// 1 komponen dipakai buat 2 varian (Sales/Purchase) - pola sama seperti
// C18SubsidiaryLedgerReport, param analysisType dari action.params.
export class C18AnalysisReport extends Component {
    static template = "c18_basic_erp.AnalysisReport";
    static props = ["*"];

    setup() {
        this.analysisType = this.props.action?.params?.analysis_type || "sales";
        this.state = useState({
            loading: true,
            data: null,
            groupBy: "partner",
            dateFrom: null,
            dateTo: null,
        });
        onWillStart(() => this.fetchData());
    }

    async fetchData() {
        this.state.loading = true;
        try {
            const data = await rpc("/c18_basic_erp/report/analysis", {
                analysis_type: this.analysisType,
                group_by: this.state.groupBy,
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

    onGroupByChange(ev) {
        this.state.groupBy = ev.target.value;
        this.fetchData();
    }

    onDateFromChange(ev) {
        this.state.dateFrom = ev.target.value || null;
        this.fetchData();
    }

    onDateToChange(ev) {
        this.state.dateTo = ev.target.value || null;
        this.fetchData();
    }

    get title() {
        return this.analysisType === "purchase" ? "Purchase Analysis" : "Sales Analysis";
    }

    get keyColumnLabel() {
        if (this.state.groupBy === "product") {
            return "Product";
        }
        if (this.state.groupBy === "period") {
            return "Period";
        }
        return this.analysisType === "purchase" ? "Vendor" : "Customer";
    }

    get showQty() {
        return this.state.groupBy !== "partner";
    }
}

registry.category("actions").add("c18_sales_analysis_report", C18AnalysisReport);
registry.category("actions").add("c18_purchase_analysis_report", C18AnalysisReport);
