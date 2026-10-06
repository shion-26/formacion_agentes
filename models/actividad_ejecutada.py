import base64
import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError

HORA_RE = re.compile(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")


class ActividadEjecutada(models.Model):
    _name = "actividad.ejecutada"
    _description = "Actividades Ejecutadas"

    _sql_constraints = [
        (
            "unique_id_actividad",
            "unique(id_actividad)",
            "Ya existe una actividad ejecutada registrada con este ID.",
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


    # ==========================================================
    # 1. INFORMACIÓN GENERAL
    # ==========================================================

    programacion_id = fields.Many2one(
        "programacion.actividad",
        string="Programación de origen",
        required=True,
        help="Actividad programada que se está ejecutando. La información "
        "general (ID, fecha programada, tipo, modalidad, formador, grupo, "
        "campaña, canal, metodología y participantes esperados) se toma "
        "de aquí para evitar que quede distinta a lo planeado.",
    )

    id_actividad = fields.Char(
        string="ID Actividad",
        related="programacion_id.id_actividad",
        store=True,
        readonly=True,
    )

    fecha_programada = fields.Date(
        string="Fecha programada",
        related="programacion_id.fecha_programada",
        store=True,
        readonly=True,
    )

    fecha_ejecucion = fields.Date(
        string="Fecha de ejecución",
    )

    hora_inicio_real = fields.Char(
        string="Hora inicio real",
        required=True,
    )

    hora_fin_real = fields.Char(
        string="Hora fin real",
        required=True,
    )

    duracion_real = fields.Char(
        string="Duración real",
        compute="_compute_duracion_real",
        store=True,
        readonly=True,
    )

    duracion_real_minutos = fields.Integer(
        string="Duración real (minutos)",
        compute="_compute_duracion_real_minutos",
        store=True,
        aggregator="sum",
    )

    modalidad = fields.Selection(
        related="programacion_id.modalidad",
        string="Modalidad",
        store=True,
        readonly=True,
    )

    grupo_formacion_id = fields.Many2one(
        "training.group.session",
        string="Grupo de formación",
        related="programacion_id.grupo_formacion_id",
        store=True,
        readonly=True,
    )

    tipo_actividad = fields.Selection(
        related="programacion_id.tipo_actividad",
        string="Tipo de actividad",
        store=True,
        readonly=True,
    )

    formador_id = fields.Many2one(
        "training.trainer",
        string="Formador / Responsable",
        related="programacion_id.formador_id",
        store=True,
        readonly=True,
    )

    campania_id = fields.Many2one(
        "training.campaign",
        string="Campaña",
        related="programacion_id.campania_id",
        store=True,
        readonly=True,
    )

    canal = fields.Many2one(
        "training.channel",
        string="Canal",
        related="programacion_id.canal_id",
        store=True,
        readonly=True,
    )

    # ==========================================================
    # 2. DETALLE DE LA ACTIVIDAD
    # ==========================================================

    tema_contenido = fields.Text(
        string="Tema / Contenido tratado",
        required=True,
    )

    objetivo_actividad = fields.Text(
        string="Objetivo de la actividad",
        required=True,
    )

    metodologia = fields.Selection(
        related="programacion_id.metodologia",
        string="Metodología utilizada",
        store=True,
        readonly=True,
    )

    recursos_materiales = fields.Text(
        string="Recursos / Materiales utilizados",
    )

    # ==========================================================
    # 3. PARTICIPACIÓN Y ASISTENCIA
    # ==========================================================

    participantes_programados = fields.Integer(
        string="Participantes programados",
        related="programacion_id.participantes_esperados",
        store=True,
        readonly=True,
    )

    participantes_asistentes = fields.Integer(
        string="Participantes asistentes",
        required=True,
    )

    participantes_ausentes = fields.Integer(
        string="Participantes ausentes",
        compute="_compute_participantes_ausentes",
        store=True,
        readonly=True,
    )

    porcentaje_asistencia = fields.Integer(
        string="% Asistencia",
        compute="_compute_porcentaje_asistencia",
        store=True,
        readonly=True,
    )

    registro_asistencia = fields.Binary(
        string="Registro de asistencia",
    )

    registro_asistencia_nombre = fields.Char(
        string="Nombre archivo asistencia",
    )

    observaciones_asistencia = fields.Text(
        string="Observaciones de asistencia",
    )

    # ==========================================================
    # 4. EVALUACIÓN DE LA ACTIVIDAD
    # ==========================================================

    cumplimiento_objetivo = fields.Selection(
        [
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
        ],
        string="Cumplimiento del objetivo",
    )

    calidad_actividad = fields.Selection(
        [
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
        ],
        string="Calidad de la actividad",
    )

    utilidad_aplicabilidad = fields.Selection(
        [
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
        ],
        string="Utilidad / Aplicabilidad",
    )

    comentarios_evaluacion = fields.Text(
        string="Comentarios generales de la evaluación",
    )


    # ==========================================================
    # 5. ESTADO DE EJECUCIÓN
    # ==========================================================

    actividad_ejecutada = fields.Selection(
        [
            ("si", "Sí, ejecutada"),
            ("no", "No ejecutada"),
        ],
        string="¿La actividad fue ejecutada?",
        required=True,
    )

    estado_ejecucion = fields.Selection(
        [
            ("oportuna", "Oportuna"),
            ("retraso", "Con retraso"),
            ("reprogramada", "Reprogramada"),
            ("cancelada", "Cancelada"),
        ],
        string="Estado de ejecución",
    )

    motivo_estado = fields.Selection(
        [
            ("clima", "Condiciones externas"),
            ("operacion", "Necesidad operativa"),
            ("inasistencia", "Inasistencia"),
            ("otro", "Otro"),
        ],
        string="Motivo",
    )

    observaciones_estado = fields.Text(
        string="Observaciones del estado",
    )

    # ==========================================================
    # 6. CIERRE Y REGISTRO
    # ==========================================================

    fecha_registro = fields.Date(
        string="Fecha de registro",
        required=True,
        default=fields.Date.today,
    )

    registrado_por = fields.Char(
        string="Registrado por",
        compute="_compute_registrado_por",
        store=True,
    )

    cargo_id = fields.Many2one(
        "training.role",
        string="Cargo",
    )

    finalizada = fields.Boolean(
        string="Finalizada",
        help="Marca que esta actividad ejecutada ya quedó cerrada, "
        "independientemente de si fue oportuna o con retraso.",
    )

    observaciones_generales = fields.Text(
        string="Observaciones generales",
    )

    @api.constrains(
        "tema_contenido",
        "objetivo_actividad",
        "recursos_materiales",
        "observaciones_asistencia",
        "comentarios_evaluacion",
        "observaciones_estado",
        "observaciones_generales",
    )
    def _check_longitud_textos(self):
        campos = [
            ("tema_contenido", "Tema / Contenido tratado"),
            ("objetivo_actividad", "Objetivo de la actividad"),
            ("recursos_materiales", "Recursos / Materiales utilizados"),
            ("observaciones_asistencia", "Observaciones de asistencia"),
            ("comentarios_evaluacion", "Comentarios generales de la evaluación"),
            ("observaciones_estado", "Observaciones del estado"),
            ("observaciones_generales", "Observaciones generales"),
        ]

        for record in self:
            for field_name, label in campos:
                valor = getattr(record, field_name)

                if valor and len(valor) > 500:
                    raise ValidationError(
                        f"El campo '{label}' no puede superar los 500 caracteres."
                    )

    @api.constrains("tema_contenido", "objetivo_actividad")
    def _check_texto_no_vacio(self):
        campos = [
            ("tema_contenido", "Tema / Contenido tratado"),
            ("objetivo_actividad", "Objetivo de la actividad"),
        ]

        for record in self:
            for field_name, label in campos:
                valor = getattr(record, field_name)

                if valor and not valor.strip():
                    raise ValidationError(
                        f"El campo '{label}' no puede contener únicamente "
                        "espacios en blanco."
                    )

    @api.depends("hora_inicio_real", "hora_fin_real")
    def _compute_duracion_real(self):
        for record in self:
            if (
                record.hora_inicio_real
                and record.hora_fin_real
                and HORA_RE.match(record.hora_inicio_real)
                and HORA_RE.match(record.hora_fin_real)
            ):
                inicio_h, inicio_m = (int(x) for x in record.hora_inicio_real.split(":"))
                fin_h, fin_m = (int(x) for x in record.hora_fin_real.split(":"))

                total_minutos = (fin_h * 60 + fin_m) - (inicio_h * 60 + inicio_m)

                if total_minutos > 0:
                    horas, minutos = divmod(total_minutos, 60)
                    partes = []

                    if horas:
                        partes.append(f"{horas} hora" + ("s" if horas != 1 else ""))

                    if minutos or not horas:
                        partes.append(f"{minutos} minuto" + ("s" if minutos != 1 else ""))

                    record.duracion_real = " y ".join(partes)
                else:
                    record.duracion_real = False
            else:
                record.duracion_real = False

    @api.depends("hora_inicio_real", "hora_fin_real")
    def _compute_duracion_real_minutos(self):
        for record in self:
            if (
                record.hora_inicio_real
                and record.hora_fin_real
                and HORA_RE.match(record.hora_inicio_real)
                and HORA_RE.match(record.hora_fin_real)
            ):
                inicio_h, inicio_m = (int(x) for x in record.hora_inicio_real.split(":"))
                fin_h, fin_m = (int(x) for x in record.hora_fin_real.split(":"))

                total_minutos = (fin_h * 60 + fin_m) - (inicio_h * 60 + inicio_m)

                record.duracion_real_minutos = total_minutos if total_minutos > 0 else 0
            else:
                record.duracion_real_minutos = 0

    @api.depends("create_uid")
    def _compute_registrado_por(self):
        for record in self:
            record.registrado_por = (
                record.create_uid.name
                if record.create_uid
                else self.env.user.name
            )

    @api.constrains("hora_inicio_real", "hora_fin_real")
    def _check_horas_reales(self):
        for record in self:

            if record.hora_inicio_real and not HORA_RE.match(record.hora_inicio_real):
                raise ValidationError(
                    "La hora de inicio real debe tener el formato HH:MM."
                )

            if record.hora_fin_real and not HORA_RE.match(record.hora_fin_real):
                raise ValidationError(
                    "La hora de fin real debe tener el formato HH:MM."
                )

            if (
                record.hora_inicio_real
                and record.hora_fin_real
                and HORA_RE.match(record.hora_inicio_real)
                and HORA_RE.match(record.hora_fin_real)
            ):
                inicio_h, inicio_m = (int(x) for x in record.hora_inicio_real.split(":"))
                fin_h, fin_m = (int(x) for x in record.hora_fin_real.split(":"))

                if (fin_h, fin_m) <= (inicio_h, inicio_m):
                    raise ValidationError(
                        "La hora de fin real debe ser posterior a la hora de "
                        "inicio real."
                    )

    @api.constrains("fecha_programada", "fecha_ejecucion")
    def _check_fecha_ejecucion(self):
        for record in self:

            if (
                record.fecha_programada
                and record.fecha_ejecucion
                and record.fecha_ejecucion < record.fecha_programada
            ):
                raise ValidationError(
                    "La fecha de ejecución no puede ser anterior a la fecha "
                    "programada."
                )

    @api.depends("participantes_programados", "participantes_asistentes")
    def _compute_participantes_ausentes(self):
        for record in self:
            record.participantes_ausentes = (
                record.participantes_programados - record.participantes_asistentes
            )

    @api.depends("participantes_programados", "participantes_asistentes")
    def _compute_porcentaje_asistencia(self):
        for record in self:
            if record.participantes_programados:
                record.porcentaje_asistencia = round(
                    (record.participantes_asistentes / record.participantes_programados)
                    * 100
                )
            else:
                record.porcentaje_asistencia = 0

    @api.constrains("participantes_programados", "participantes_asistentes")
    def _check_participantes(self):
        for record in self:

            if record.participantes_programados <= 0:
                raise ValidationError(
                    "Los participantes programados deben ser mayores que cero."
                )

            if record.participantes_asistentes < 0:
                raise ValidationError(
                    "Los participantes asistentes no pueden ser negativos."
                )

            if record.participantes_asistentes > record.participantes_programados:
                raise ValidationError(
                    "Los participantes asistentes no pueden ser mayores que los "
                    "participantes programados."
                )

    @api.constrains("registro_asistencia", "registro_asistencia_nombre")
    def _check_registro_asistencia(self):
        allowed_extensions = (".xlsx", ".xls", ".pdf", ".jpg", ".jpeg")
        max_size_bytes = 5 * 1024 * 1024

        for record in self:

            if not record.registro_asistencia:
                continue

            file_size = len(base64.b64decode(record.registro_asistencia))
            if file_size > max_size_bytes:
                raise ValidationError(
                    "El registro de asistencia no puede superar los 5 MB."
                )

            if (
                record.registro_asistencia_nombre
                and not record.registro_asistencia_nombre.lower().endswith(
                    allowed_extensions
                )
            ):
                raise ValidationError(
                    "El registro de asistencia debe ser Excel (.xls/.xlsx), PDF "
                    "o JPG."
                )