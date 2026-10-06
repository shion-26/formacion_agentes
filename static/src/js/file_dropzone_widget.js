/** @odoo-module **/
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useRef } from "@odoo/owl";

class FileDropzone extends Component {
    static template = "formacion_calidad.FileDropzone";
    static props = {
        ...standardFieldProps,
        acceptedFormats: { type: String, optional: true },
    };

    setup() {
        this.fileInputRef = useRef("fileInput");
    }

    get filenameField() {
        return this.props.record.fields[this.props.name].related_field || null;
    }

    get currentFilename() {
        const guessedField = this.props.name + "_nombre";
        return this.props.record.data[guessedField] || null;
    }

    onZoneClick() {
        this.fileInputRef.el.click();
    }

    onDragOver(ev) {
        ev.preventDefault();
        ev.currentTarget.classList.add("fd_dragover");
    }

    onDragLeave(ev) {
        ev.currentTarget.classList.remove("fd_dragover");
    }

    onDrop(ev) {
        ev.preventDefault();
        ev.currentTarget.classList.remove("fd_dragover");
        const file = ev.dataTransfer.files[0];
        if (file) {
            this.readAndSetFile(file);
        }
    }

    onFileChange(ev) {
        const file = ev.target.files[0];
        if (file) {
            this.readAndSetFile(file);
        }
    }

    readAndSetFile(file) {
        const reader = new FileReader();
        reader.onload = () => {
            const base64 = reader.result.split(",")[1];
            const guessedField = this.props.name + "_nombre";
            const updateData = { [this.props.name]: base64 };
            if (guessedField in this.props.record.data) {
                updateData[guessedField] = file.name;
            }
            this.props.record.update(updateData);
        };
        reader.readAsDataURL(file);
    }

    onRemove(ev) {
        ev.stopPropagation();
        const guessedField = this.props.name + "_nombre";
        const updateData = { [this.props.name]: false };
        if (guessedField in this.props.record.data) {
            updateData[guessedField] = false;
        }
        this.props.record.update(updateData);
    }
}

registry.category("fields").add("file_dropzone", {
    component: FileDropzone,
});