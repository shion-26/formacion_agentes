/** @odoo-module **/
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

class EstadoEjecucionButtons extends Component {
    static template = "formacion_agentes.EstadoEjecucionButtons";
    static props = { ...standardFieldProps };

    get options() {
        return [
            { value: "oportuna", label: "Oportuna", colorClass: "cf-green" },
            { value: "retraso", label: "Con retraso", colorClass: "cf-orange" },
            { value: "reprogramada", label: "Reprogramada", colorClass: "cf-blue" },
            { value: "cancelada", label: "Cancelada", colorClass: "cf-red" },
        ];
    }

    isSelected(value) {
        return this.props.record.data[this.props.name] === value;
    }

    onSelect(value) {
        this.props.record.update({ [this.props.name]: value });
    }
}

registry.category("fields").add("estado_ejecucion_buttons", {
    component: EstadoEjecucionButtons,
});
