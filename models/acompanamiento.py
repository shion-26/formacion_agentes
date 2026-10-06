import re
from datetime import date

from odoo import api, fields, models
from odoo.exceptions import ValidationError

HORA_RE = re.compile(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
MMSS_RE = re.compile(r"^[0-5][0-9]:[0-5][0-9]$")


class Acompanamiento(models.Model):
    _name = "acompanamiento"
    _description = "Acompañamiento - Monitoreo de Calidad"

    _sql_constraints = [
        (
            "unique_id_monitoreo",
            "unique(id_monitoreo)",
            "Ya existe un monitoreo registrado con este ID.",
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
    # REGISTRO
    # ==========================================================

    name = fields.Char(
        string="Nombre",
        compute="_compute_name",
        store=True,
    )

    # ==========================================================
    # INFORMACIÓN GENERAL
    # ==========================================================

    id_monitoreo = fields.Char(
        string="ID Monitoreo",
        required=True,
    )

    fecha_monitoreo = fields.Date(
        string="Fecha del monitoreo",
        required=True,
    )

    hora_inicio = fields.Char(
        string="Hora inicio"
    )

    hora_fin = fields.Char(
        string="Hora fin"
    )

    formador_evaluador_id = fields.Many2one(
        "training.trainer",
        string="Formador / Evaluador",
        related="participante_id.formador_id",
        store=True,
        readonly=True,
    )

    campania_id = fields.Many2one(
        "training.campaign",
        string="Campaña",
        related="participante_id.campania_id",
        store=True,
        readonly=True,
    )

    participante_id = fields.Many2one(
        "registro_fi",
        string="Agente evaluado",
        required=True,
    )

    grupo_formacion_id = fields.Many2one(
        "training.group.session",
        string="Grupo de formación",
        related="participante_id.grupo_formacion_id",
        store=True,
        readonly=True,
    )

    canal_id = fields.Many2one(
        "training.channel",
        string="Canal",
        required=True,
    )

    tipo_interaccion = fields.Selection(
        [
            ("entrada", "Entrada"),
            ("salida", "Salida"),
            ("seguimiento", "Seguimiento"),
        ],
        string="Tipo de interacción",
        required=True,
    )

    id_interaccion = fields.Char(
        string="ID interacción / Contacto"
    )

    # ==========================================================
    # EVALUACIÓN DE CALIDAD
    # ==========================================================

    score_calidad = fields.Integer(
        string="Score de calidad (%)",
        required=True,
        aggregator="avg",
    )

    nivel_calidad = fields.Selection(
        [
            ("excelente", "Excelente"),
            ("bueno", "Bueno"),
            ("regular", "Regular"),
            ("critico", "Crítico"),
        ],
        string="Nivel de calidad",
        compute="_compute_nivel_calidad",
        store=True,
        readonly=True,
    )

    resultado_evaluacion = fields.Selection(
        [
            ("aprobado", "Aprobado"),
            ("condicional", "Condicional"),
            ("no_aprobado", "No aprobado"),
        ],
        string="Resultado de la evaluación",
        required=True,
    )

    csat = fields.Integer(
        string="CSAT"
    )

    nivel_csat = fields.Selection(
        [
            ("malo", "Malo"),
            ("medio", "Medio"),
            ("bueno", "Bueno"),
        ],
        string="Nivel CSAT",
        compute="_compute_nivel_csat",
        store=True,
        readonly=True,
    )

    # ==========================================================
    # MÉTRICAS DE GESTIÓN
    # ==========================================================

    tiempo_gestion_total = fields.Char(
        string="Tiempo de gestión total",
        required=True,
    )

    tiempo_espera = fields.Char(
        string="Tiempo de espera"
    )

    tiempo_conversacion = fields.Char(
        string="Tiempo de conversación"
    )

    tiempo_post_gestion = fields.Char(
        string="Tiempo de post-gestión"
    )

    tmo = fields.Char(
        string="TMO"
    )

    duracion_gestion_segundos = fields.Integer(
        string="Duración gestión (segundos)",
        compute="_compute_duracion_gestion_segundos",
        store=True,
        aggregator="avg",
    )

    # ==========================================================
    # HALLAZGOS Y ALERTAS
    # ==========================================================

    alerta_critica = fields.Selection(
        [
            ("si", "Sí"),
            ("no", "No"),
        ],
        string="¿Se detectaron alertas críticas?",
        required=True,
    )

    cantidad_alertas_criticas = fields.Integer(
        string="Cantidad de alertas críticas"
    )

    cantidad_alertas_menores = fields.Integer(
        string="Cantidad de alertas menores"
    )

    # ==========================================================
    # FALLAS DETECTADAS
    # ==========================================================

    motivo_falla = fields.Selection(
        [
            ("procedimiento", "Procedimiento"),
            ("comunicacion", "Comunicación"),
            ("sistema", "Sistema"),
            ("otro", "Otro"),
        ],
        string="Motivo de la falla",
    )

    descripcion_fallas = fields.Text(
        string="Descripción de las fallas"
    )

    # ==========================================================
    # COACHING / RETROALIMENTACIÓN
    # ==========================================================

    fortalezas = fields.Text(
        string="Fortalezas identificadas"
    )

    oportunidades_mejora = fields.Text(
        string="Oportunidades de mejora"
    )

    compromisos_plan_accion = fields.Text(
        string="Compromisos / Plan de acción"
    )

    fecha_seguimiento = fields.Date(
        string="Fecha de seguimiento"
    )

    # ==========================================================
    # COMPUTE METHODS
    # ==========================================================

    @api.depends("id_monitoreo")
    def _compute_name(self):
        for record in self:
            record.name = record.id_monitoreo or "Nuevo"

    @api.depends("score_calidad")
    def _compute_nivel_calidad(self):
        for record in self:
            score = record.score_calidad

            if score >= 90:
                record.nivel_calidad = "excelente"
            elif score >= 80:
                record.nivel_calidad = "bueno"
            elif score >= 70:
                record.nivel_calidad = "regular"
            else:
                record.nivel_calidad = "critico"

    @api.depends("csat")
    def _compute_nivel_csat(self):
        for record in self:
            csat = record.csat

            if not csat:
                record.nivel_csat = False
            elif csat <= 2:
                record.nivel_csat = "malo"
            elif csat == 3:
                record.nivel_csat = "medio"
            else:
                record.nivel_csat = "bueno"

    @api.depends("tiempo_gestion_total")
    def _compute_duracion_gestion_segundos(self):
        for record in self:
            valor = (record.tiempo_gestion_total or "").strip()

            if MMSS_RE.match(valor):
                minutos, segundos = (int(x) for x in valor.split(":"))
                record.duracion_gestion_segundos = minutos * 60 + segundos
            else:
                record.duracion_gestion_segundos = 0

    @api.constrains(
        "id_monitoreo",
        "fecha_monitoreo",
        "hora_inicio",
        "hora_fin",
    )
    def _check_informacion_general(self):
        today = date.today()

        for record in self:

            # ID monitoreo
            if record.id_monitoreo and not record.id_monitoreo.strip():
                raise ValidationError(
                    "El ID de monitoreo no puede estar vacío."
                )

            # Fecha del monitoreo
            if record.fecha_monitoreo and record.fecha_monitoreo > today:
                raise ValidationError(
                    "La fecha del monitoreo no puede ser futura."
                )

            # Hora inicio
            if record.hora_inicio and not HORA_RE.match(record.hora_inicio.strip()):
                raise ValidationError(
                    "La hora de inicio debe tener el formato HH:MM (Ej: 08:30)."
                )

            # Hora fin
            if record.hora_fin and not HORA_RE.match(record.hora_fin.strip()):
                raise ValidationError(
                    "La hora de fin debe tener el formato HH:MM (Ej: 09:15)."
                )

            # Hora fin posterior a hora inicio
            if (
                record.hora_inicio
                and record.hora_fin
                and HORA_RE.match(record.hora_inicio.strip())
                and HORA_RE.match(record.hora_fin.strip())
            ):
                inicio_h, inicio_m = (int(x) for x in record.hora_inicio.strip().split(":"))
                fin_h, fin_m = (int(x) for x in record.hora_fin.strip().split(":"))

                if (fin_h, fin_m) <= (inicio_h, inicio_m):
                    raise ValidationError(
                        "La hora de fin debe ser posterior a la hora de inicio."
                    )

    @api.constrains(
        "tiempo_gestion_total",
        "tiempo_espera",
        "tiempo_conversacion",
        "tiempo_post_gestion",
    )
    def _check_formato_tiempos_gestion(self):
        campos = [
            ("tiempo_gestion_total", "Tiempo de gestión total"),
            ("tiempo_espera", "Tiempo de espera"),
            ("tiempo_conversacion", "Tiempo de conversación"),
            ("tiempo_post_gestion", "Tiempo de post-gestión"),
        ]

        for record in self:
            for field_name, label in campos:
                valor = getattr(record, field_name)

                if valor and not MMSS_RE.match(valor.strip()):
                    raise ValidationError(
                        f"El campo '{label}' debe tener el formato MM:SS "
                        "(Ej: 02:15)."
                    )

    @api.constrains("score_calidad", "csat")
    def _check_evaluacion_calidad(self):
        for record in self:

            # Score de calidad
            if record.score_calidad < 0 or record.score_calidad > 100:
                raise ValidationError(
                    "El score de calidad debe estar entre 0 y 100."
                )

            # CSAT
            if record.csat and (record.csat < 1 or record.csat > 5):
                raise ValidationError(
                    "El CSAT debe estar entre 1 y 5."
                )

    @api.onchange("alerta_critica")
    def _onchange_alerta_critica(self):
        if self.alerta_critica == "no":
            self.cantidad_alertas_criticas = 0
            self.cantidad_alertas_menores = 0
            self.motivo_falla = False
            self.descripcion_fallas = False

    @api.constrains(
        "alerta_critica",
        "cantidad_alertas_criticas",
        "cantidad_alertas_menores",
    )
    def _check_hallazgos_alertas(self):
        for record in self:

            if record.alerta_critica == "no" and (
                record.cantidad_alertas_criticas or record.cantidad_alertas_menores
            ):
                raise ValidationError(
                    "No puede registrar cantidad de alertas si no se detectaron "
                    "alertas críticas."
                )

            if record.cantidad_alertas_criticas < 0 or record.cantidad_alertas_menores < 0:
                raise ValidationError(
                    "La cantidad de alertas no puede ser negativa."
                )

    @api.constrains("alerta_critica", "motivo_falla", "descripcion_fallas")
    def _check_fallas_detectadas(self):
        for record in self:

            if record.alerta_critica == "no" and (
                record.motivo_falla or record.descripcion_fallas
            ):
                raise ValidationError(
                    "No puede registrar motivo ni descripción de fallas si no se "
                    "detectaron alertas críticas."
                )

    @api.constrains("fecha_seguimiento", "fecha_monitoreo")
    def _check_fecha_seguimiento(self):
        for record in self:

            if (
                record.fecha_seguimiento
                and record.fecha_monitoreo
                and record.fecha_seguimiento < record.fecha_monitoreo
            ):
                raise ValidationError(
                    "La fecha de seguimiento no puede ser anterior a la fecha "
                    "del monitoreo."
                )

    @api.constrains(
        "descripcion_fallas",
        "fortalezas",
        "oportunidades_mejora",
        "compromisos_plan_accion",
    )
    def _check_longitud_textos(self):
        campos = [
            ("descripcion_fallas", "Descripción de las fallas"),
            ("fortalezas", "Fortalezas identificadas"),
            ("oportunidades_mejora", "Oportunidades de mejora"),
            ("compromisos_plan_accion", "Compromisos / Plan de acción"),
        ]

        for record in self:
            for field_name, label in campos:
                valor = getattr(record, field_name)

                if valor and len(valor) > 500:
                    raise ValidationError(
                        f"El campo '{label}' no puede superar los 500 caracteres."
                    )

    @api.model
    def _asignar_canal_agente(self, participante, canal_id):
        if participante and canal_id and not participante.canal_id:
            participante.canal_id = canal_id

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            if vals.get("id_monitoreo"):
                vals["id_monitoreo"] = vals["id_monitoreo"].strip().upper()

            if vals.get("id_interaccion"):
                vals["id_interaccion"] = vals["id_interaccion"].strip().upper()

        records = super().create(vals_list)

        for record in records:
            self._asignar_canal_agente(record.participante_id, record.canal_id)

        return records

    def write(self, vals):

        if vals.get("id_monitoreo"):
            vals["id_monitoreo"] = vals["id_monitoreo"].strip().upper()

        if vals.get("id_interaccion"):
            vals["id_interaccion"] = vals["id_interaccion"].strip().upper()

        result = super().write(vals)

        if "canal_id" in vals or "participante_id" in vals:
            for record in self:
                self._asignar_canal_agente(record.participante_id, record.canal_id)

        return result
