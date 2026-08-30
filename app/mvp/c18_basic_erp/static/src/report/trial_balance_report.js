/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { Component, onWillStart, useState } from "@odoo/owl";

// Report interaktif (bukan wizard tombol Generate) - pola diadopsi dari
// referensi odoo18_toso (c18_hr_payroll, komponen slip gaji): ganti field
// filter langsung fetchData() ulang, tanpa reload halaman/tombol terpisah.
// Lihat erd/mvp/09-laporan-keuangan.md poin 1 + bagian "Arsitektur Implementasi".
export class C18TrialBalanceReport extends Component {
    static template = "c18_basic_erp.TrialBalanceReport";
    static props = ["*"];

    setup() {
        this.state = useState({
            loading: true,
            data: null,
            dateTo: null,
            costCenterId: null,
            hideZero: true,
        });
        onWillStart(() => this.fetchData());
    }

    async fetchData() {
        this.state.loading = true;
        try {
            const data = await rpc("/c18_basic_erp/report/trial_balance", {
                date_to: this.state.dateTo,
                cost_center_id: this.state.costCenterId,
                hide_zero: this.state.hideZero,
            });
            this.state.data = data;
            // server yang tentukan default date_to kalau belum dipilih user -
            // sinkronkan balik ke state supaya input tanggal menunjukkan
            // nilai yang benar-benar sedang ditampilkan
            this.state.dateTo = data.date_to;
        } finally {
            this.state.loading = false;
        }
    }

    onDateChange(ev) {
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

registry.category("actions").add("c18_trial_balance_report", C18TrialBalanceReport);
