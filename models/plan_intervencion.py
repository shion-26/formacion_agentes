import base64

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PlanIntervencion(models.Model):
    _name = "plan_intervencion"
    _description = "Planes de Intervención"

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

    @api.depends("id_plan")
    def _compute_name(self):
        for record in self:
            record.name = record.id_plan or "Nuevo"

    # ==================================================
    # INFORMACIÓN GENERAL
    # ==================================================

    id_plan = fields.Char(
        string="ID Plan",
        required=True,
    )

    fecha_creacion = fields.Date(
        string="Fecha de creación",
        required=True,
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
        string="Participante / Agente",
        required=True,
    )

    formador_responsable_id = fields.Many2one(
        "training.trainer",
        string="Formador responsable",
        related="participante_id.formador_id",
        store=True,
        readonly=True,
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
        related="participante_id.canal_id",
        store=True,
        readonly=True,
    )

    tipo_intervencion = fields.Selection(
        [
            ("coaching", "Coaching"),
            ("reentrenamiento", "Reentrenamiento"),
            ("acompanamiento", "Acompañamiento"),
            ("plan_mejora", "Plan de mejora"),
        ],
        string="Tipo de intervención",
        required=True,
    )

    motivo_plan = fields.Selection(
        [
            ("calidad", "Baja calidad"),
            ("alertas", "Alertas críticas"),
            ("tmo", "TMO elevado"),
            ("cliente", "Quejas del cliente"),
            ("otro", "Otro"),
        ],
        string="Motivo del plan",
        required=True,
    )

    # ==================================================
    # DETALLE DEL PLAN
    # ==================================================

    fecha_inicio = fields.Date(
        string="Fecha de inicio",
        required=True,
    )

    fecha_fin_estimada = fields.Date(
        string="Fecha fin estimada",
        required=True,
    )

    fecha_fin_real = fields.Date(
        string="Fecha fin real"
    )

    estado_plan = fields.Selection(
        [
            ("activo", "Activo"),
            ("ejecucion", "En ejecución"),
            ("finalizado", "Finalizado"),
            ("cancelado", "Cancelado"),
        ],
        string="Estado del plan",
        required=True,
    )

    descripcion_plan = fields.Text(
        string="Descripción del plan",
        required=True,
    )

    horas_planificadas = fields.Integer(
        string="Horas planificadas",
        required=True,
    )

    horas_ejecutadas = fields.Integer(
        string="Horas ejecutadas"
    )

    porcentaje_avance = fields.Integer(
        string="% Avance / Cumplimiento",
        compute="_compute_porcentaje_avance",
        store=True,
        readonly=True,
    )

    # ==================================================
    # SEGUIMIENTO Y EVALUACIÓN
    # ==================================================

    criterio_evaluacion = fields.Selection(
        [
            ("calidad", "Calidad"),
            ("productividad", "Productividad"),
            ("procedimientos", "Procedimientos"),
            ("integral", "Integral"),
        ],
        string="Criterios de evaluación",
        required=True,
    )

    meta_esperada = fields.Integer(
        string="Meta esperada (%)",
        required=True,
    )

    resultado_obtenido = fields.Integer(
        string="Resultado obtenido (%)"
    )

    porcentaje_cumplimiento = fields.Integer(
        string="% Cumplimiento",
        compute="_compute_porcentaje_cumplimiento",
        store=True,
        readonly=True,
        aggregator="avg",
    )

    observaciones_formador = fields.Text(
        string="Observaciones del formador"
    )

    comentarios_participante = fields.Text(
        string="Comentarios del participante"
    )

    evidencias = fields.Binary(
        string="Evidencias"
    )

    evidencias_nombre = fields.Char(
        string="Nombre del archivo"
    )

    acciones_recomendaciones = fields.Text(
        string="Acciones / Recomendaciones"
    )

    # ==================================================
    # CIERRE DEL PLAN
    # ==================================================

    fecha_cierre = fields.Date(
        string="Fecha de cierre"
    )

    motivo_cierre = fields.Selection(
        [
            ("cumplimiento", "Cumplimiento de objetivos"),
            ("retiro", "Retiro del participante"),
            ("cancelado", "Cancelado"),
            ("otro", "Otro"),
        ],
        string="Motivo de cierre",
    )

    resultados_alcanzados = fields.Text(
        string="Resultados alcanzados"
    )

    lecciones_aprendidas = fields.Text(
        string="Lecciones aprendidas"
    )

    @api.constrains(
        "descripcion_plan",
        "observaciones_formador",
        "comentarios_participante",
        "acciones_recomendaciones",
        "resultados_alcanzados",
        "lecciones_aprendidas",
    )
    def _check_longitud_textos(self):
        campos = [
            ("descripcion_plan", "Descripción del plan"),
            ("observaciones_formador", "Observaciones del formador"),
            ("comentarios_participante", "Comentarios del participante"),
            ("acciones_recomendaciones", "Acciones / Recomendaciones"),
            ("resultados_alcanzados", "Resultados alcanzados"),
            ("lecciones_aprendidas", "Lecciones aprendidas"),
        ]

        for record in self:
            for field_name, label in campos:
                valor = getattr(record, field_name)

                if valor and len(valor) > 500:
                    raise ValidationError(
                        f"El campo '{label}' no puede superar los 500 caracteres."
                    )

    @api.depends("horas_planificadas", "horas_ejecutadas")
    def _compute_porcentaje_avance(self):
        for record in self:
            if record.horas_planificadas:
                record.porcentaje_avance = round(
                    (record.horas_ejecutadas / record.horas_planificadas) * 100
                )
            else:
                record.porcentaje_avance = 0

    @api.constrains("fecha_inicio", "fecha_fin_estimada", "fecha_fin_real")
    def _check_fechas_plan(self):
        for record in self:

            if (
                record.fecha_inicio
                and record.fecha_fin_estimada
                and record.fecha_fin_estimada < record.fecha_inicio
            ):
                raise ValidationError(
                    "La fecha fin estimada no puede ser anterior a la fecha de inicio."
                )

            if (
                record.fecha_inicio
                and record.fecha_fin_real
                and record.fecha_fin_real < record.fecha_inicio
            ):
                raise ValidationError(
                    "La fecha fin real no puede ser anterior a la fecha de inicio."
                )

    @api.constrains("horas_planificadas", "horas_ejecutadas")
    def _check_horas_plan(self):
        for record in self:

            if record.horas_planificadas <= 0:
                raise ValidationError(
                    "Las horas planificadas deben ser mayores a 0."
                )

            if record.horas_ejecutadas < 0:
                raise ValidationError(
                    "Las horas ejecutadas no pueden ser negativas."
                )

    @api.depends("meta_esperada", "resultado_obtenido")
    def _compute_porcentaje_cumplimiento(self):
        for record in self:
            if record.meta_esperada:
                record.porcentaje_cumplimiento = round(
                    (record.resultado_obtenido / record.meta_esperada) * 100
                )
            else:
                record.porcentaje_cumplimiento = 0

    @api.constrains("meta_esperada", "resultado_obtenido")
    def _check_seguimiento_evaluacion(self):
        for record in self:

            if record.meta_esperada < 0 or record.meta_esperada > 100:
                raise ValidationError(
                    "La meta esperada debe estar entre 0 y 100."
                )

            if record.resultado_obtenido and (
                record.resultado_obtenido < 0 or record.resultado_obtenido > 100
            ):
                raise ValidationError(
                    "El resultado obtenido debe estar entre 0 y 100."
                )

    @api.constrains("evidencias", "evidencias_nombre")
    def _check_evidencias(self):
        allowed_extensions = (".xlsx", ".xls", ".csv")
        max_size_bytes = 5 * 1024 * 1024

        for record in self:

            if not record.evidencias:
                continue

            file_size = len(base64.b64decode(record.evidencias))
            if file_size > max_size_bytes:
                raise ValidationError(
                    "El archivo de evidencias no puede superar los 5 MB."
                )

            if record.evidencias_nombre and not record.evidencias_nombre.lower().endswith(
                allowed_extensions
            ):
                raise ValidationError(
                    "El archivo de evidencias debe ser Excel (.xls/.xlsx) o CSV."
                )