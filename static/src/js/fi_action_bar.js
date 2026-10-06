/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class FiActionBar extends Component {
    static template = "formacion_agentes.FiActionBar";
    static props = ["*"];

    async onClickGuardar() {
        const saved = await this.props.record.save();

        if (saved) {
            await this.env.services.action.restore();
        }
    }

    async onClickLimpiar() {
        const resModel = this.props.record.resModel;

        await this.props.record.discard();

        await this.env.services.action.doAction({
            type: "ir.actions.act_window",
            res_model: resModel,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("view_widgets").add("fi_action_bar", {
    component: FiActionBar,
});
