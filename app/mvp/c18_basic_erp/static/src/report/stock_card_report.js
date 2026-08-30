/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

export class C18StockCardReport extends Component {
    static template = "c18_basic_erp.StockCardReport";
    static props = ["*"];

    setup() {
        this.action = useService("action");
        this.state = useState({
            loading: true,
            data: null,
            productId: null,
            dateFrom: null,
            dateTo: null,
        });
        onWillStart(() => this.fetchData());
    }

    async fetchData() {
        this.state.loading = true;
        try {
            const data = await rpc("/c18_basic_erp/report/stock_card", {
                product_id: this.state.productId,
                date_from: this.state.dateFrom,
                date_to: this.state.dateTo,
            });
            this.state.data = data;
            this.state.productId = data.product_id;
            this.state.dateFrom = data.date_from;
            this.state.dateTo = data.date_to;
        } finally {
            this.state.loading = false;
        }
    }

    onProductChange(ev) {
        this.state.productId = ev.target.value || null;
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

    get productOptions() {
        return this.state.data?.filters?.product_options || [];
    }

    openDocument(row) {
        if (!row.res_model || !row.res_id) {
            return;
        }
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: row.res_model,
            res_id: row.res_id,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("c18_stock_card_report", C18StockCardReport);
