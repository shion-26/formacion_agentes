/** @odoo-module **/
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { formatDate, formatDateTime } from "@web/views/fields/formatters";
import { Component } from "@odoo/owl";

class ReadonlyRelatedPlaceholder extends Component {
    static template = "formacion_agentes.ReadonlyRelatedPlaceholder";
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
    };

    get fieldType() {
        return this.props.record.fields[this.props.name].type;
    }

    get rawValue() {
        return this.props.record.data[this.props.name];
    }

    get displayValue() {
        const value = this.rawValue;

        if (value === false || value === undefined || value === null || value === "") {
            return "";
        }

        switch (this.fieldType) {
            case "many2one":
                return value[1] || "";
            case "date":
                return formatDate(value);
            case "datetime":
                return formatDateTime(value);
            case "selection": {
                const options = this.props.record.fields[this.props.name].selection || [];
                const match = options.find((option) => option[0] === value);
                return match ? match[1] : value;
            }
            default:
                return value;
        }
    }
}

registry.category("fields").add("readonly_related_placeholder", {
    component: ReadonlyRelatedPlaceholder,
    supportedTypes: ["char", "many2one", "date", "datetime", "selection", "integer"],
    extractProps: ({ attrs }) => ({
        placeholder: attrs.placeholder,
    }),
});
