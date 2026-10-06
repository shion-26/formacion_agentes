/** @odoo-module **/
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { parseInteger } from "@web/views/fields/parsers";
import { useInputField } from "@web/views/fields/input_field_hook";
import { Component } from "@odoo/owl";

class RequiredIntegerField extends Component {
    static template = "formacion_agentes.RequiredIntegerField";
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
    };

    setup() {
        useInputField({
            getValue: () => this.formattedValue,
            parse: (v) => parseInteger(v),
        });
    }

    get value() {
        return this.props.record.data[this.props.name];
    }

    get formattedValue() {
        return this.value ? String(this.value) : "";
    }
}

registry.category("fields").add("required_integer", {
    component: RequiredIntegerField,
    supportedTypes: ["integer"],
    extractProps: ({ attrs }) => ({
        placeholder: attrs.placeholder,
    }),
});
