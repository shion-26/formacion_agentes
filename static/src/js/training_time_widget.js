/** @odoo-module **/
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState, onWillUpdateProps } from "@odoo/owl";

function pad2(value) {
    return String(value).padStart(2, "0");
}

function parseDigits(digits) {
    const minutesRaw = digits.length <= 2 ? digits : digits.slice(-2);
    const hoursRaw = digits.length <= 2 ? "" : digits.slice(0, -2);

    return {
        hours: hoursRaw === "" ? 0 : parseInt(hoursRaw, 10),
        minutes: parseInt(minutesRaw.padStart(2, "0"), 10),
    };
}

function to24Hours(hours12, meridiem) {
    const base = hours12 % 12;
    return meridiem === "PM" ? base + 12 : base;
}

function from24Hours(hours24) {
    const meridiem = hours24 >= 12 ? "PM" : "AM";
    const hours12 = hours24 % 12 === 0 ? 12 : hours24 % 12;
    return { hours12, meridiem };
}

class TrainingTimeField extends Component {
    static template = "formacion_calidad.TrainingTimeField";
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
    };

    setup() {
        this.state = useState({
            displayValue: "",
            meridiem: "AM",
            error: "",
        });

        this._syncFromRecord(this.props);

        onWillUpdateProps((nextProps) => this._syncFromRecord(nextProps));
    }

    _syncFromRecord(props) {
        const value = props.record.data[props.name];

        if (!value) {
            this.state.displayValue = "";
            this.state.meridiem = "AM";
            this.state.error = "";
            return;
        }

        const [hh, mm] = value.split(":");
        const { hours12, meridiem } = from24Hours(parseInt(hh, 10));

        this.state.displayValue = `${pad2(hours12)}:${mm}`;
        this.state.meridiem = meridiem;
        this.state.error = "";
    }

    onInput(ev) {
        // Mientras se escribe solo se permiten dígitos y ":".
        const cleaned = ev.target.value.replace(/[^0-9:]/g, "").slice(0, 5);
        this.state.displayValue = cleaned;
        ev.target.value = cleaned;
    }

    onKeydown(ev) {
        if (ev.key === "Enter") {
            ev.target.blur();
        }
    }

    onBlur() {
        this._commit();
    }

    setMeridiem(meridiem) {
        this.state.meridiem = meridiem;
        this._commit();
    }

    _commit() {
        const digits = this.state.displayValue.replace(/\D/g, "");

        if (!digits) {
            this.state.error = "";
            this.state.displayValue = "";
            this.props.record.update({ [this.props.name]: false });
            return;
        }

        if (digits.length > 4) {
            this.state.error = "Hora inválida. Usa el formato HH:MM.";
            return;
        }

        const { hours, minutes } = parseDigits(digits);

        if (hours < 0 || hours > 12 || minutes < 0 || minutes > 59) {
            this.state.error = "Hora inválida. Usa el formato HH:MM.";
            return;
        }

        this.state.error = "";
        this.state.displayValue = `${pad2(hours)}:${pad2(minutes)}`;

        const hours24 = to24Hours(hours, this.state.meridiem);
        this.props.record.update({
            [this.props.name]: `${pad2(hours24)}:${pad2(minutes)}`,
        });
    }
}

registry.category("fields").add("training_time", {
    component: TrainingTimeField,
    supportedTypes: ["char"],
    extractProps: ({ attrs }) => ({
        placeholder: attrs.placeholder,
    }),
});
