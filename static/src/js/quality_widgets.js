/** @odoo-module **/
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

// ============================
// NIVEL DE CALIDAD
// ============================
class NivelCalidadButtons extends Component {
    static template = "formacion_calidad.NivelCalidadButtons";
    static props = { ...standardFieldProps };

    get options() {
        return [
            { value: "excelente", label: "Excelente (90 - 100%)", colorClass: "cf-green" },
            { value: "bueno", label: "Bueno (80 - 89%)", colorClass: "cf-lime" },
            { value: "regular", label: "Regular (70 - 79%)", colorClass: "cf-orange" },
            { value: "critico", label: "Crítico (< 70%)", colorClass: "cf-red" },
        ];
    }

    isSelected(value) {
        return this.props.record.data[this.props.name] === value;
    }

    onSelect(value) {
        if (this.props.readonly) {
            return;
        }
        this.props.record.update({ [this.props.name]: value });
    }
}

registry.category("fields").add("nivel_calidad_buttons", {
    component: NivelCalidadButtons,
});

// ============================
// CSAT (1 a 5)
// ============================
class CsatButtons extends Component {
    static template = "formacion_calidad.CsatButtons";
    static props = { ...standardFieldProps };

    get options() {
        return [1, 2, 3, 4, 5];
    }

    isSelected(value) {
        return this.props.record.data[this.props.name] === value;
    }

    onSelect(value) {
        this.props.record.update({ [this.props.name]: value });
    }
}

registry.category("fields").add("csat_buttons", {
    component: CsatButtons,
});

// ============================
// ALERTA CRÍTICA (Sí / No)
// ============================
class AlertaCriticaButtons extends Component {
    static template = "formacion_calidad.AlertaCriticaButtons";
    static props = { ...standardFieldProps };

    get options() {
        return [
            { value: "si", label: "Si", colorClass: "cf-red" },
            { value: "no", label: "No", colorClass: "cf-green" },
        ];
    }

    isSelected(value) {
        return this.props.record.data[this.props.name] === value;
    }

    onSelect(value) {
        this.props.record.update({ [this.props.name]: value });
    }
}

registry.category("fields").add("alerta_critica_buttons", {
    component: AlertaCriticaButtons,
});