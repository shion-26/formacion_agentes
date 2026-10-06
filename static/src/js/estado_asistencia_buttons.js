/** @odoo-module **/
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

class EstadoAsistenciaButtons extends Component {
    static template = "formacion_agentes.EstadoAsistenciaButtons";
    static props = { ...standardFieldProps };

    get options() {
        return [
            { value: "asistio", label: "Asistió", icon: "fa-check-circle", colorClass: "cf-green" },
            { value: "no_asistio", label: "No asistió", icon: "fa-times-circle", colorClass: "cf-red" },
            { value: "justificado", label: "Justificado", icon: "fa-exclamation-circle", colorClass: "cf-orange" },
            { value: "no_programado", label: "No programado", icon: "fa-minus-circle", colorClass: "cf-blue" },
        ];
    }

    isSelected(value) {
        return this.props.record.data[this.props.name] === value;
    }

    onSelect(value) {
        this.props.record.update({ [this.props.name]: value });
    }
}

registry.category("fields").add("estado_asistencia_buttons", {
    component: EstadoAsistenciaButtons,
});
