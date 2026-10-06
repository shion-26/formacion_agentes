/** @odoo-module **/
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useInputField } from "@web/views/fields/input_field_hook";
import { Component, useState, useEffect } from "@odoo/owl";

class CharCounterText extends Component {
    static template = "formacion_calidad.CharCounterText";
    static props = {
        ...standardFieldProps,
        maxlength: { type: Number, optional: true },
        placeholder: { type: String, optional: true },
    };
    static defaultProps = {
        maxlength: 500,
    };

    setup() {
        this.state = useState({ length: 0 });

        useInputField({
            getValue: () => this.props.record.data[this.props.name] || "",
        });

        useEffect(
            (value) => {
                this.state.length = (value || "").length;
            },
            () => [this.props.record.data[this.props.name]]
        );
    }

    onInput(ev) {
        if (this.props.readonly) {
            return;
        }
        this.state.length = ev.target.value.length;
    }
}

registry.category("fields").add("char_counter_text", {
    component: CharCounterText,
    supportedTypes: ["text"],
    extractProps: ({ attrs, options }) => ({
        maxlength: (options && options.maxlength) || 500,
        placeholder: attrs.placeholder,
    }),
});
