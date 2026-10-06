/** @odoo-module **/
import { markup } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { escape } from "@web/core/utils/strings";
import { patch } from "@web/core/utils/patch";
import { Record } from "@web/model/relational_model/record";

const REQUIRED_INTEGER_FIELDS = {
};

function isUnsetRequired(record, fieldName) {
    return (
        fieldName in record.activeFields &&
        !record._isInvisible(fieldName) &&
        record._isRequired(fieldName) &&
        !record.data[fieldName]
    );
}

patch(Record.prototype, {
    _checkValidity(options = {}) {
        const extraFieldNames = REQUIRED_INTEGER_FIELDS[this.resModel];
        if (!extraFieldNames) {
            return super._checkValidity(options);
        }

        const { silent, displayNotification, removeInvalidOnly } = options;

        if (removeInvalidOnly) {
            const result = super._checkValidity(options);
            for (const fieldName of extraFieldNames) {
                if (!isUnsetRequired(this, fieldName)) {
                    this._invalidFields.delete(fieldName);
                }
            }
            return result;
        }

        if (silent) {
            const nativeIsValid = super._checkValidity({ silent: true });
            return nativeIsValid && !extraFieldNames.some((f) => isUnsetRequired(this, f));
        }

        super._checkValidity({ removeInvalidOnly: false });

        for (const fieldName of extraFieldNames) {
            if (isUnsetRequired(this, fieldName)) {
                this._invalidFields.add(fieldName);
            } else {
                this._invalidFields.delete(fieldName);
            }
        }

        const isValid = !this._invalidFields.size;

        if (!isValid && displayNotification) {
            if (this._closeInvalidFieldsNotification) {
                this._closeInvalidFieldsNotification();
            }
            const items = [...this._invalidFields].map(
                (fieldName) => `<li>${escape(this.fields[fieldName].string || fieldName)}</li>`
            );
            this._closeInvalidFieldsNotification = this.model.notification.add(
                markup(`<ul>${items.join("")}</ul>`),
                { title: _t("Invalid fields: "), type: "danger" }
            );
        }

        return isValid;
    },
});
