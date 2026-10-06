/** @odoo-module **/
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState, onWillUpdateProps } from "@odoo/owl";

function pad2(value) {
    return String(value).padStart(2, "0");
}
function parseDigits(digits) {
    const padded = digits.padStart(4, "0");

    return {
        minutes: parseInt(padded.slice(0, 2), 10),
        seconds: parseInt(padded.slice(2, 4), 10),
    };
}

class MmssTimeField extends Component {
    static template = "formacion_calidad.MmssTimeField";
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
    };

    setup() {
        this.state = useState({
            digits: "",
            displayValue: "00:00",
            error: "",
        });

        this._syncFromRecord(this.props);

        onWillUpdateProps((nextProps) => this._syncFromRecord(nextProps));
    }

    _syncFromRecord(props) {
        const value = props.record.data[props.name];

        if (!value) {
            this.state.digits = "";
            this.state.displayValue = "00:00";
            this.state.error = "";
            return;
        }

        this.state.digits = value.replace(/\D/g, "").slice(-4);
        this.state.displayValue = value;
        this.state.error = "";
    }

    _formatDigits(digits) {
        const { minutes, seconds } = parseDigits(digits);
        return `${pad2(minutes)}:${pad2(seconds)}`;
    }

    _updateRecord(digits) {
        this.state.digits = digits;
        this.state.displayValue = this._formatDigits(digits);
        this.state.error = "";

        this.props.record.update({
            [this.props.name]: digits ? this._formatDigits(digits) : false,
        });
    }

    onFocus(ev) {
        ev.target.select();
    }

    onKeydown(ev) {
        if (ev.key === "Enter") {
            ev.target.blur();
            return;
        }

        if (
            ev.key === "Tab" ||
            ev.key === "Shift" ||
            ev.key === "Control" ||
            ev.key === "Alt" ||
            ev.key === "Meta" ||
            ev.key.startsWith("Arrow")
        ) {
            return;
        }

        ev.preventDefault();

        if (ev.key === "Backspace" || ev.key === "Delete") {
            this._updateRecord(this.state.digits.slice(0, -1));
            return;
        }

        if (!/^[0-9]$/.test(ev.key)) {
            return;
        }

        const candidate = (this.state.digits + ev.key).slice(-4);
        const { minutes, seconds } = parseDigits(candidate);

        if (minutes > 59 || seconds > 59) {
            this.state.error = "Formato inválido. Máximo 59:59.";
            return;
        }

        this._updateRecord(candidate);
    }
}

registry.category("fields").add("mmss_time", {
    component: MmssTimeField,
    supportedTypes: ["char"],
    extractProps: ({ attrs }) => ({
        placeholder: attrs.placeholder,
    }),
});
