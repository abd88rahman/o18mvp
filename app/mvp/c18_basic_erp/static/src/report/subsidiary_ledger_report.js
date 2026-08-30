/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

// 1 komponen dipakai buat 2 varian (Piutang/Hutang) - action registry beda
// tag, param ledgerType beda, sisanya sama persis. Lihat erd/mvp/09 poin 5.
export class C18SubsidiaryLedgerReport extends Component {
    static template = "c18_basic_erp.SubsidiaryLedgerReport";
    static props = ["*"];

    setup() {
        this.action = useService("action");
        this.ledgerType = this.props.action?.params?.ledger_type || "receivable";
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
            const data = await rpc("/c18_basic_erp/report/subsidiary_ledger", {
                ledger_type: this.ledgerType,
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
        return this.ledgerType === "payable" ? "Buku Bantu Hutang" : "Buku Bantu Piutang";
    }

    // buka Buku Besar dgn akun kontrol + partner ini sudah terisi
    openGeneralLedger(row) {
        this.action.doAction({
            type: "ir.actions.client",
            tag: "c18_general_ledger_report",
            params: {
                account_id: this.state.data.account_id ?? null,
                partner_id: row.partner_id,
            },
        });
    }
}

registry.category("actions").add("c18_subsidiary_ledger_receivable", C18SubsidiaryLedgerReport);
registry.category("actions").add("c18_subsidiary_ledger_payable", C18SubsidiaryLedgerReport);
