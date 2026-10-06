/** @odoo-module **/
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

class EstadoProgramacionButtons extends Component {
    static template = "formacion_agentes.EstadoProgramacionButtons";
    static props = { ...standardFieldProps };

    get options() {
        return [
            { value: "programada", label: "Programada", colorClass: "cf-green" },
            { value: "revision", label: "En revisión", colorClass: "cf-orange" },
            { value: "aprobada", label: "Aprobada", colorClass: "cf-blue" },
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

registry.category("fields").add("estado_programacion_buttons", {
    component: EstadoProgramacionButtons,
});
