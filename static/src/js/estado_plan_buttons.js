/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

class EstadoPlanButtons extends Component {
    static template = "formacion_agentes.EstadoPlanButtons";
    static props = { ...standardFieldProps };

    get options() {
        return [
            { value: "activo", label: "Activo", colorClass: "cf-green" },
            { value: "ejecucion", label: "En ejecución", colorClass: "cf-orange" },
            { value: "finalizado", label: "Finalizado", colorClass: "cf-blue" },
            { value: "cancelado", label: "Cancelado", colorClass: "cf-red" },
        ];
    }

    isSelected(value) {
        return this.props.record.data[this.props.name] === value;
    }

    onSelect(value) {
        this.props.record.update({ [this.props.name]: value });
    }
}

registry.category("fields").add("estado_plan_buttons", {
    component: EstadoPlanButtons,
});