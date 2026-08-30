/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

export class C18GeneralLedgerReport extends Component {
    static template = "c18_basic_erp.GeneralLedgerReport";
    static props = ["*"];

    setup() {
        this.action = useService("action");
        // drill-down dari Buku Bantu (subsidiary_ledger_report.js) buka report
        // ini dengan account_id/partner_id sudah terisi lewat params action
        const params = this.props.action?.params || {};
        this.state = useState({
            loading: true,
            data: null,
            accountId: params.account_id || null,
            dateFrom: null,
            dateTo: null,
            costCenterId: null,
            partnerId: params.partner_id || null,
        });
        onWillStart(() => this.fetchData());
    }

    async fetchData() {
        this.state.loading = true;
        try {
            const data = await rpc("/c18_basic_erp/report/general_ledger", {
                account_id: this.state.accountId,
                date_from: this.state.dateFrom,
                date_to: this.state.dateTo,
                cost_center_id: this.state.costCenterId,
                partner_id: this.state.partnerId,
            });
            this.state.data = data;
            this.state.accountId = data.account_id;
            this.state.dateFrom = data.date_from;
            this.state.dateTo = data.date_to;
        } finally {
            this.state.loading = false;
        }
    }

    onAccountChange(ev) {
        this.state.accountId = ev.target.value || null;
        // ganti akun = reset partner (opsi partner tergantung akun yg dipilih)
        this.state.partnerId = null;
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

    onCostCenterChange(ev) {
        this.state.costCenterId = ev.target.value || null;
        this.fetchData();
    }

    onPartnerChange(ev) {
        this.state.partnerId = ev.target.value || null;
        this.fetchData();
    }

    get accountOptions() {
        return this.state.data?.filters?.account_options || [];
    }

    get partnerOptions() {
        return this.state.data?.filters?.partner_options || [];
    }

    get costCenterOptions() {
        return this.state.data?.filters?.cost_center_options || [];
    }

    openDocument(row) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: row.res_model,
            res_id: row.res_id,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("c18_general_ledger_report", C18GeneralLedgerReport);
