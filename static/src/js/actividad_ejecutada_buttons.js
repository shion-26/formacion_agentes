/** @odoo-module **/
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

class ActividadEjecutadaButtons extends Component {
    static template = "formacion_agentes.ActividadEjecutadaButtons";
    static props = { ...standardFieldProps };

    get options() {
        return [
            { value: "si", label: "Sí, ejecutada", icon: "fa-check-circle", colorClass: "cf-green" },
            { value: "no", label: "No ejecutada", icon: "fa-times-circle", colorClass: "cf-red" },
        ];
    }

    isSelected(value) {
        return this.props.record.data[this.props.name] === value;
    }

    onSelect(value) {
        this.props.record.update({ [this.props.name]: value });
    }
}

registry.category("fields").add("actividad_ejecutada_buttons", {
    component: ActividadEjecutadaButtons,
});
