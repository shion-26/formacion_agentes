/** @odoo-module **/
import { registry } from "@web/core/registry";
import { formView } from "@web/views/form/form_view";
import { FormController } from "@web/views/form/form_controller";
import { useService } from "@web/core/utils/hooks";

export class ProgramacionActividadFormController extends FormController {
    setup() {
        super.setup();
        this.orm = useService("orm");
    }

    async onRecordSaved(record) {
        await super.onRecordSaved(...arguments);

        if (record.data.estado_final !== "ejecutada") {
            return;
        }

        const resId = record.resId;
        const orm = this.orm;
        const actionService = this.env.services.action;

        setTimeout(async () => {
            const ejecutadas = await orm.searchRead(
                "actividad.ejecutada",
                [["programacion_id", "=", resId]],
                ["id"],
                { limit: 1, order: "id desc" }
            );

            if (ejecutadas.length) {
                actionService.doAction({
                    type: "ir.actions.act_window",
                    res_model: "actividad.ejecutada",
                    res_id: ejecutadas[0].id,
                    views: [[false, "form"]],
                    target: "current",
                });
            }
        }, 0);
    }
}

registry.category("views").add("programacion_actividad_form", {
    ...formView,
    Controller: ProgramacionActividadFormController,
});
