/** @odoo-module **/
import { registry } from "@web/core/registry";
import { SelectionField, selectionField } from "@web/views/fields/selection/selection_field";

export class SelectionDisabledPlaceholder extends SelectionField {
    static template = "formacion_agentes.SelectionDisabledPlaceholder";
}

registry.category("fields").add("selection_disabled_placeholder", {
    ...selectionField,
    component: SelectionDisabledPlaceholder,
});
