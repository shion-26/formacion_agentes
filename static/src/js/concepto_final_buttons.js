/** @odoo-module **/
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

class ConceptoFinalButtons extends Component {
    static template = "formacion_calidad.ConceptoFinalButtons";
    static props = { ...standardFieldProps };

    get options() {
        return [
            { value: "apto", label: "Apto", icon: "fa-check-circle", colorClass: "cf-green" },
            { value: "abandono", label: "Abandonó", icon: "fa-times-circle", colorClass: "cf-red" },
            { value: "no_inicia", label: "No inicia", icon: "fa-minus-circle", colorClass: "cf-orange" },
            { value: "renovar", label: "Por renovar", icon: "fa-refresh", colorClass: "cf-blue" },
        ];
    }

    isSelected(value) {
        return this.props.record.data[this.props.name] === value;
    }

    onSelect(value) {
        this.props.record.update({ [this.props.name]: value });
    }
}

registry.category("fields").add("concepto_final_buttons", {
    component: ConceptoFinalButtons,
});