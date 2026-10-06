import base64
import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError

HORA_RE = re.compile(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")

CAMPOS_PROGRAMACION_COMPLETA = (
    "id_actividad",
    "fecha_programada",
    "hora_inicio",
    "hora_fin",
    "tipo_actividad",
    "modalidad",
    "formador_id",
    "grupo_formacion_id",
    "campania_id",
    "canal_id",
    "objetivo",
    "contenido",
    "participantes_esperados",
    "grupo_objetivo",
    "lugar",
    "fecha_registro",
)


class ProgramacionActividades(models.Model):
    _name = "programacion.actividad"
    _description = "Programación de Actividades"

    _sql_constraints = [
        (
            "unique_id_actividad",
            "unique(id_actividad)",
            "Ya existe una actividad registrada con este ID.",
        ),
    ]

    def action_guardar(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    def action_limpiar(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "target": "current",
        }

    # ==================================================
    # REGISTRO
    # ==================================================

    name = fields.Char(
        string="Nombre",
        compute="_compute_name",
        store=True,
    )

    @api.depends("id_actividad")
    def _compute_name(self):
        for record in self:
            record.name = record.id_actividad or "Nueva actividad"

    @api.depends("create_uid")
    def _compute_registrado_por(self):
        for record in self:
            record.registrado_por = (
                record.create_uid.name
                if record.create_uid
                else self.env.user.name
            )

    # ==================================================
    # 1. INFORMACIÓN GENERAL DE LA ACTIVIDAD
    # ==================================================

    id_actividad = fields.Char(
        string="ID Actividad",
    )

    fecha_programada = fields.Date(
        string="Fecha programada",
        required=True,
    )

    hora_inicio = fields.Char(
        string="Hora inicio programada",
        required=True,
    )

    hora_fin = fields.Char(
        string="Hora fin programada",
        required=True,
    )

    duracion = fields.Char(
        string="Duración programada",
        compute="_compute_duracion",
        store=True,
        readonly=True,
    )

    duracion_minutos = fields.Integer(
        string="Duración programada (minutos)",
        compute="_compute_duracion_minutos",
        store=True,
        aggregator="sum",
    )

    tipo_actividad = fields.Selection(
        [
            ("induccion", "Inducción"),
            ("formacion", "Formación"),
            ("refuerzo", "Refuerzo"),
            ("coaching", "Coaching"),
            ("retroalimentacion", "Retroalimentación"),
            ("otro", "Otro"),
        ],
        string="Tipo de actividad",
        required=True,
    )

    modalidad = fields.Selection(
        [
            ("presencial", "Presencial"),
            ("virtual", "Virtual"),
            ("hibrida", "Híbrida"),
        ],
        string="Modalidad",
        required=True,
    )

    formador_id = fields.Many2one(
        "training.trainer",
        string="Formador responsable",
        required=True,
    )

    grupo_formacion_id = fields.Many2one(
        "training.group.session",
        string="Grupo de formación",
        required=True,
    )

    campania_id = fields.Many2one(
        "training.campaign",
        string="Campaña",
        required=True,
    )

    canal_id = fields.Many2one(
        "training.channel",
        string="Canal",
        required=True,
    )

    # ==================================================
    # 2. DETALLE DE LA ACTIVIDAD
    # ==================================================

    objetivo = fields.Text(
        string="Objetivo de la actividad",
        required=True,
    )

    contenido = fields.Text(
        string="Contenido / Temas a tratar",
        required=True,
    )

    metodologia = fields.Selection(
        [
            ("teorica", "Teórica"),
            ("practica", "Práctica"),
            ("mixta", "Mixta"),
            ("taller", "Taller"),
            ("simulacion", "Simulación"),
        ],
        string="Metodología",
    )

    recursos = fields.Text(
        string="Recursos / Materiales requeridos"
    )

    # ==================================================
    # 3. PARTICIPANTES PROGRAMADOS
    # ==================================================

    participantes_esperados = fields.Integer(
        string="Participantes esperados",
        required=True,
    )

    grupo_objetivo = fields.Selection(
        [
            ("nuevo_ingreso", "Nuevo ingreso"),
            ("activos", "Activos"),
            ("reentrenamiento", "Reentrenamiento"),
            ("todos", "Todos"),
        ],
        string="Grupo objetivo",
        required=True,
    )

    criterio_seleccion = fields.Text(
        string="Criterio de selección"
    )

    lista_participantes = fields.Binary(
        string="Lista de participantes"
    )

    lista_participantes_nombre = fields.Char(
        string="Nombre del archivo"
    )

    # ==================================================
    # 4. LUGAR / PLATAFORMA
    # ==================================================

    lugar = fields.Selection(
        [
            ("sala", "Sala de capacitación"),
            ("teams", "Microsoft Teams"),
            ("meet", "Google Meet"),
            ("zoom", "Zoom"),
            ("otro", "Otro"),
        ],
        string="Lugar / Plataforma",
        required=True,
    )

    enlace = fields.Char(
        string="Enlace / Ubicación"
    )

    # ==================================================
    # 5. ESTADO Y CONTROL
    # ==================================================

    estado_programacion = fields.Selection(
        [
            ("programada", "Programada"),
            ("revision", "En revisión"),
            ("aprobada", "Aprobada"),
            ("cancelada", "Cancelada"),
        ],
        string="Estado de la programación",
        required=True,
    )

    registrado_por = fields.Char(
        string="Registrado por",
        compute="_compute_registrado_por",
        store=True,
    )

    fecha_registro = fields.Date(
        string="Fecha de registro",
        required=True
    )

    observaciones = fields.Text(
        string="Observaciones generales"
    )

    # ==================================================
    # 6. CONFIRMACIÓN Y SEGUIMIENTO
    # ==================================================

    fecha_confirmacion = fields.Date(
        string="Fecha de confirmación"
    )

    confirmado_por = fields.Char(
        string="Confirmado por"
    )

    fecha_ejecucion = fields.Date(
        string="Fecha de ejecución real"
    )

    estado_final = fields.Selection(
        [
            ("ejecutada", "Ejecutada"),
            ("reprogramada", "Reprogramada"),
            ("cancelada", "Cancelada"),
            ("no_ejecutada", "No ejecutada"),
        ],
        string="Estado final",
    )

    observaciones_seguimiento = fields.Text(
        string="Observaciones de seguimiento"
    )

    @api.constrains(
        "objetivo",
        "contenido",
        "recursos",
        "criterio_seleccion",
        "observaciones",
        "observaciones_seguimiento",
    )
    def _check_longitud_textos(self):
        campos = [
            ("objetivo", "Objetivo de la actividad"),
            ("contenido", "Contenido / Temas a tratar"),
            ("recursos", "Recursos / Materiales requeridos"),
            ("criterio_seleccion", "Criterio de selección"),
            ("observaciones", "Observaciones generales"),
            ("observaciones_seguimiento", "Observaciones de seguimiento"),
        ]

        for record in self:
            for field_name, label in campos:
                valor = getattr(record, field_name)

                if valor and len(valor) > 500:
                    raise ValidationError(
                        f"El campo '{label}' no puede superar los 500 caracteres."
                    )

    @api.constrains("objetivo", "contenido", "recursos", "criterio_seleccion")
    def _check_texto_no_vacio(self):
        campos = [
            ("objetivo", "Objetivo de la actividad"),
            ("contenido", "Contenido / Temas a tratar"),
            ("recursos", "Recursos / Materiales requeridos"),
            ("criterio_seleccion", "Criterio de selección"),
        ]

        for record in self:
            for field_name, label in campos:
                valor = getattr(record, field_name)

                if valor and not valor.strip():
                    raise ValidationError(
                        f"El campo '{label}' no puede contener únicamente "
                        "espacios en blanco."
                    )

    @api.constrains("participantes_esperados")
    def _check_participantes_esperados(self):
        for record in self:
            if record.participantes_esperados <= 0:
                raise ValidationError(
                    "Los participantes esperados deben ser mayores que cero."
                )

    @api.constrains("lista_participantes", "lista_participantes_nombre")
    def _check_lista_participantes(self):
        allowed_extensions = (".xlsx", ".xls", ".csv")
        max_size_bytes = 5 * 1024 * 1024

        for record in self:

            if not record.lista_participantes:
                continue

            file_size = len(base64.b64decode(record.lista_participantes))
            if file_size > max_size_bytes:
                raise ValidationError(
                    "La lista de participantes no puede superar los 5 MB."
                )

            if (
                record.lista_participantes_nombre
                and not record.lista_participantes_nombre.lower().endswith(
                    allowed_extensions
                )
            ):
                raise ValidationError(
                    "La lista de participantes debe ser Excel (.xls/.xlsx) o CSV."
                )

    @api.model
    def _calcular_total_minutos(self, hora_inicio, hora_fin):
        if not (
            hora_inicio
            and hora_fin
            and HORA_RE.match(hora_inicio)
            and HORA_RE.match(hora_fin)
        ):
            return 0

        inicio_h, inicio_m = (int(x) for x in hora_inicio.split(":"))
        fin_h, fin_m = (int(x) for x in hora_fin.split(":"))

        total_minutos = (fin_h * 60 + fin_m) - (inicio_h * 60 + inicio_m)

        return total_minutos if total_minutos > 0 else 0

    @api.model
    def _calcular_duracion(self, hora_inicio, hora_fin):
        total_minutos = self._calcular_total_minutos(hora_inicio, hora_fin)

        if not total_minutos:
            return False

        horas, minutos = divmod(total_minutos, 60)
        partes = []

        if horas:
            partes.append(f"{horas} hora" + ("s" if horas != 1 else ""))

        if minutos or not horas:
            partes.append(f"{minutos} minuto" + ("s" if minutos != 1 else ""))

        return " y ".join(partes)

    @api.depends("hora_inicio", "hora_fin")
    def _compute_duracion(self):
        for record in self:
            record.duracion = self._calcular_duracion(record.hora_inicio, record.hora_fin)

    @api.depends("hora_inicio", "hora_fin")
    def _compute_duracion_minutos(self):
        for record in self:
            record.duracion_minutos = self._calcular_total_minutos(
                record.hora_inicio, record.hora_fin
            )

    @api.constrains("hora_inicio", "hora_fin")
    def _check_horas_programadas(self):
        for record in self:

            if record.hora_inicio and not HORA_RE.match(record.hora_inicio):
                raise ValidationError(
                    "La hora de inicio programada debe tener el formato HH:MM."
                )

            if record.hora_fin and not HORA_RE.match(record.hora_fin):
                raise ValidationError(
                    "La hora de fin programada debe tener el formato HH:MM."
                )

            if (
                record.hora_inicio
                and record.hora_fin
                and HORA_RE.match(record.hora_inicio)
                and HORA_RE.match(record.hora_fin)
            ):
                inicio_h, inicio_m = (int(x) for x in record.hora_inicio.split(":"))
                fin_h, fin_m = (int(x) for x in record.hora_fin.split(":"))

                if (fin_h, fin_m) <= (inicio_h, inicio_m):
                    raise ValidationError(
                        "La hora de fin programada debe ser posterior a la hora "
                        "de inicio programada."
                    )

    # ==================================================
    # 6. CONFIRMACIÓN Y SEGUIMIENTO
    # ==================================================

    @api.constrains("fecha_confirmacion", "fecha_programada", "estado_programacion")
    def _check_fecha_confirmacion(self):
        for record in self:

            if not record.fecha_confirmacion:
                continue

            if not record.estado_programacion:
                raise ValidationError(
                    "No puede registrar una fecha de confirmación si la "
                    "actividad aún no ha sido programada."
                )

            if record.estado_programacion == "cancelada":
                raise ValidationError(
                    "No puede confirmar una actividad cuya programación fue "
                    "cancelada."
                )

            if (
                record.fecha_programada
                and record.fecha_confirmacion < record.fecha_programada
            ):
                raise ValidationError(
                    "La fecha de confirmación no puede ser anterior a la "
                    "fecha programada."
                )

    @api.constrains("fecha_confirmacion", "confirmado_por")
    def _check_confirmado_por(self):
        for record in self:

            if record.confirmado_por and not record.confirmado_por.strip():
                raise ValidationError(
                    "El campo 'Confirmado por' no puede contener únicamente "
                    "espacios en blanco."
                )

            if record.fecha_confirmacion and not record.confirmado_por:
                raise ValidationError(
                    "Debe indicar quién confirmó la actividad cuando se "
                    "registra una fecha de confirmación."
                )

            if record.confirmado_por and not record.fecha_confirmacion:
                raise ValidationError(
                    "Debe indicar la fecha de confirmación cuando se "
                    "registra quién confirmó la actividad."
                )

    @api.constrains("fecha_ejecucion", "fecha_programada")
    def _check_fecha_ejecucion(self):
        for record in self:
            if (
                record.fecha_ejecucion
                and record.fecha_programada
                and record.fecha_ejecucion < record.fecha_programada
            ):
                raise ValidationError(
                    "La fecha de ejecución real no puede ser anterior a la "
                    "fecha programada."
                )

    @api.constrains("estado_final", "fecha_ejecucion")
    def _check_estado_final(self):
        for record in self:

            if record.estado_final == "ejecutada":
                if not record.fecha_ejecucion:
                    raise ValidationError(
                        "Debe indicar la fecha de ejecución real cuando el "
                        "estado final es 'Ejecutada'."
                    )
            elif record.fecha_ejecucion:
                raise ValidationError(
                    "La fecha de ejecución real solo puede registrarse "
                    "cuando el estado final es 'Ejecutada'."
                )

    @api.onchange("estado_final")
    def _onchange_estado_final(self):
        if self.estado_final != "ejecutada":
            self.fecha_ejecucion = False

    def _programacion_esta_completa(self):
        self.ensure_one()

        if not all(self[campo] for campo in CAMPOS_PROGRAMACION_COMPLETA):
            return False

        return bool(self._calcular_duracion(self.hora_inicio, self.hora_fin))

    @api.model
    def _vals_programacion_completa(self, vals):
        if not all(vals.get(campo) for campo in CAMPOS_PROGRAMACION_COMPLETA):
            return False

        return bool(
            self._calcular_duracion(vals.get("hora_inicio"), vals.get("hora_fin"))
        )

    @api.onchange(*CAMPOS_PROGRAMACION_COMPLETA)
    def _onchange_programacion_completa(self):
        if not self.estado_programacion and self._programacion_esta_completa():
            self.estado_programacion = "programada"

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            vals["id_actividad"] = vals.get("id_actividad") or self.env[
                "ir.sequence"
            ].next_by_code("programacion.actividad.id_actividad")

            if not vals.get("estado_programacion") and self._vals_programacion_completa(vals):
                vals["estado_programacion"] = "programada"

        records = super().create(vals_list)

        records.filtered(
            lambda r: r.estado_final == "ejecutada"
        )._crear_actividad_ejecutada_automatica()

        return records

    def write(self, vals):

        result = super().write(vals)

        if "estado_programacion" not in vals:
            for record in self.filtered(lambda r: not r.estado_programacion):
                if record._programacion_esta_completa():
                    record.estado_programacion = "programada"

        if vals.get("estado_final") == "ejecutada":
            self.filtered(
                lambda r: r.estado_final == "ejecutada"
            )._crear_actividad_ejecutada_automatica()

        return result

    def _crear_actividad_ejecutada_automatica(self):
        ActividadEjecutada = self.env["actividad.ejecutada"]

        for record in self:

            if ActividadEjecutada.search_count(
                [("programacion_id", "=", record.id)]
            ):
                continue

            ActividadEjecutada.create({
                "programacion_id": record.id,
                "fecha_ejecucion": record.fecha_ejecucion,
                "hora_inicio_real": "",
                "hora_fin_real": "",
                "tema_contenido": "",
                "objetivo_actividad": "",
                "participantes_asistentes": 0,
                "actividad_ejecutada": "si",
            })

    def unlink(self):
        ejecutadas = self.env["actividad.ejecutada"].search(
            [("programacion_id", "in", self.ids)]
        )

        if ejecutadas:
            ids_actividad = ", ".join(
                filter(None, ejecutadas.mapped("id_actividad"))
            ) or ", ".join(map(str, ejecutadas.ids))

            raise ValidationError(
                "No se puede eliminar esta Programación de Actividades "
                "porque ya tiene una Actividad Ejecutada registrada "
                f"({ids_actividad}). Primero elimine esa Actividad "
                "Ejecutada, o archive esta Programación en su lugar."
            )

        return super().unlink()