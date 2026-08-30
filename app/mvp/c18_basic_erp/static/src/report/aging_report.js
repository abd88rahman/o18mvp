/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

// 1 komponen dipakai buat 2 varian (Piutang/Hutang), pola sama seperti
// C18SubsidiaryLedgerReport - action registry beda tag, param agingType beda.
export class C18AgingReport extends Component {
    static template = "c18_basic_erp.AgingReport";
    static props = ["*"];

    setup() {
        this.action = useService("action");
        this.agingType = this.props.action?.params?.aging_type || "receivable";
        this.state = useState({
            loading: true,
            data: null,
            dateTo: null,
            hideZero: true,
        });
        onWillStart(() => this.fetchData());
    }

    async fetchData() {
        this.state.loading = true;
        try {
            const data = await rpc("/c18_basic_erp/report/aging", {
                aging_type: this.agingType,
                date_to: this.state.dateTo,
                hide_zero: this.state.hideZero,
            });
            this.state.data = data;
            this.state.dateTo = data.date_to;
        } finally {
            this.state.loading = false;
        }
    }

    onDateChange(ev) {
        this.state.dateTo = ev.target.value || null;
        this.fetchData();
    }

    onHideZeroChange(ev) {
        this.state.hideZero = ev.target.checked;
        this.fetchData();
    }

    get title() {
        return this.agingType === "payable" ? "Umur Hutang" : "Umur Piutang";
    }

    // buka Buku Besar dgn akun kontrol + partner ini sudah terisi
    openGeneralLedger(row) {
        this.action.doAction({
            type: "ir.actions.client",
            tag: "c18_general_ledger_report",
            params: {
                account_id: row.account_id ?? null,
                partner_id: row.partner_id,
            },
        });
    }
}

registry.category("actions").add("c18_aging_report_receivable", C18AgingReport);
registry.category("actions").add("c18_aging_report_payable", C18AgingReport);
