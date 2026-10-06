/** @odoo-module **/
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

class EstadoFinalActividadButtons extends Component {
    static template = "formacion_agentes.EstadoFinalActividadButtons";
    static props = { ...standardFieldProps };

    get options() {
        return [
            { value: "ejecutada", label: "Ejecutada", colorClass: "cf-green" },
            { value: "reprogramada", label: "Reprogramada", colorClass: "cf-orange" },
            { value: "cancelada", label: "Cancelada", colorClass: "cf-red" },
            { value: "no_ejecutada", label: "No ejecutada", colorClass: "cf-gray" },
        ];
    }

    isSelected(value) {
        return this.props.record.data[this.props.name] === value;
    }

    onSelect(value) {
        this.props.record.update({ [this.props.name]: value });
    }
}

registry.category("fields").add("estado_final_actividad_buttons", {
    component: EstadoFinalActividadButtons,
});
