from odoo import api, fields, models
from odoo.exceptions import ValidationError


class TrainingGroupSession(models.Model):
    _name = "training.group.session"
    _description = "Grupo de formación real (grupo base + número)"
    _order = "codigo_grupo"
    _rec_name = "codigo_grupo"

    _sql_constraints = [
        (
            "unique_grupo_base_numero",
            "unique(grupo_base_id, numero_grupo)",
            "Ya existe un grupo real registrado con este número para el "
            "grupo base seleccionado.",
        ),
        (
            "unique_codigo_grupo",
            "unique(codigo_grupo)",
            "Ya existe un grupo real registrado con este código.",
        ),
    ]

    grupo_base_id = fields.Many2one(
        "training.group",
        string="Grupo base",
        required=True,
    )

    numero_grupo = fields.Integer(
        string="Número de grupo",
        required=True,
    )

    codigo_grupo = fields.Char(
        string="Código del grupo",
        compute="_compute_codigo_grupo",
        store=True,
    )

    participantes_ids = fields.One2many(
        "registro_fi",
        "grupo_formacion_id",
        string="Participantes",
    )

    acompanamientos_ids = fields.One2many(
        "acompanamiento",
        "grupo_formacion_id",
        string="Acompañamientos",
    )

    asistencias_ids = fields.One2many(
        "control.asistencia",
        "grupo_formacion_id",
        string="Control de asistencia",
    )

    actividades_ejecutadas_ids = fields.One2many(
        "actividad.ejecutada",
        "grupo_formacion_id",
        string="Registros de actividades ejecutadas",
    )

    # ==========================================================
    # INDICADORES (agregados por grupo real)
    # ==========================================================

    participantes_inscritos = fields.Integer(
        string="Participantes inscritos",
        compute="_compute_indicadores",
        store=True,
    )

    participantes_aptos = fields.Integer(
        string="Participantes aptos",
        compute="_compute_indicadores",
        store=True,
    )

    porcentaje_certificacion = fields.Float(
        string="% Certificados",
        compute="_compute_indicadores",
        store=True,
        aggregator="avg",
    )

    horas_hombre = fields.Integer(
        string="Horas hombre",
        compute="_compute_indicadores",
        store=True,
    )

    promedio_evaluacion = fields.Float(
        string="Promedio de evaluación",
        compute="_compute_indicadores",
        store=True,
        aggregator="avg",
    )

    # ==========================================================
    # INDICADORES DE CALIDAD (Libro 2 - Acompañamiento)
    # ==========================================================

    meta_calidad = fields.Float(
        string="Meta esperada de calidad (%)",
        default=90.0,
    )

    calidad_promedio = fields.Float(
        string="Calidad promedio",
        compute="_compute_indicadores_calidad",
        store=True,
        aggregator="avg",
    )

    nivel_cumplimiento = fields.Float(
        string="Nivel de cumplimiento (%)",
        compute="_compute_indicadores_calidad",
        store=True,
        aggregator="avg",
    )

    csat_respuestas = fields.Integer(
        string="Respuestas CSAT",
        compute="_compute_indicadores_calidad",
        store=True,
    )

    csat_satisfaccion = fields.Float(
        string="% Satisfacción CSAT",
        compute="_compute_indicadores_calidad",
        store=True,
        aggregator="avg",
    )

    # ==========================================================
    # INDICADORES DE ASISTENCIA (Libro 4 - Control de Asistencia)
    # ==========================================================

    sesiones_programadas = fields.Integer(
        string="Sesiones programadas",
        compute="_compute_indicadores_asistencia",
        store=True,
    )

    sesiones_asistidas = fields.Integer(
        string="Sesiones asistidas",
        compute="_compute_indicadores_asistencia",
        store=True,
    )

    porcentaje_asistencia = fields.Float(
        string="% Asistencia",
        compute="_compute_indicadores_asistencia",
        store=True,
        aggregator="avg",
    )

    # ==========================================================
    # INDICADORES DE EJECUCIÓN (Libro 6 - Actividades Ejecutadas)
    # ==========================================================

    total_actividades_ejecutadas_registro = fields.Integer(
        string="Total actividades registradas",
        compute="_compute_indicadores_ejecucion",
        store=True,
    )

    actividades_ejecutadas = fields.Integer(
        string="Actividades ejecutadas",
        compute="_compute_indicadores_ejecucion",
        store=True,
    )

    porcentaje_ejecucion = fields.Float(
        string="% Ejecución",
        compute="_compute_indicadores_ejecucion",
        store=True,
        aggregator="avg",
    )

    actividades_oportunas = fields.Integer(
        string="Actividades oportunas",
        compute="_compute_indicadores_ejecucion",
        store=True,
    )

    porcentaje_oportunidad = fields.Float(
        string="% Oportunidad",
        compute="_compute_indicadores_ejecucion",
        store=True,
        aggregator="avg",
    )

    tiempo_promedio_minutos = fields.Float(
        string="Tiempo promedio (minutos)",
        compute="_compute_indicadores_ejecucion",
        store=True,
        aggregator="avg",
    )

    @api.depends("grupo_base_id", "numero_grupo")
    def _compute_codigo_grupo(self):

        for record in self:

            if record.grupo_base_id and record.numero_grupo:

                record.codigo_grupo = (
                    f"{record.grupo_base_id.name}-{record.numero_grupo}"
                )

            else:

                record.codigo_grupo = False

    @api.depends(
        "participantes_ids.estado_final",
        "participantes_ids.horas_formacion",
        "participantes_ids.nota_final",
    )
    def _compute_indicadores(self):

        for record in self:

            participantes = record.participantes_ids
            inscritos = len(participantes)
            aptos = len(participantes.filtered(lambda p: p.estado_final == "apto"))

            participantes.flush_model(["nota_final"])
            evaluados = participantes
            if participantes:
                self.env.cr.execute(
                    "SELECT id FROM registro_fi "
                    "WHERE id = ANY(%s) AND nota_final IS NOT NULL",
                    (participantes.ids,),
                )
                evaluados_ids = {row[0] for row in self.env.cr.fetchall()}
                evaluados = participantes.filtered(
                    lambda p, ids=evaluados_ids: p.id in ids
                )

            record.participantes_inscritos = inscritos
            record.participantes_aptos = aptos

            record.porcentaje_certificacion = (
                round((aptos / inscritos) * 100) if inscritos else 0.0
            )

            record.horas_hombre = sum(participantes.mapped("horas_formacion"))

            record.promedio_evaluacion = (
                sum(evaluados.mapped("nota_final")) / len(evaluados)
                if evaluados
                else 0.0
            )

    @api.depends(
        "acompanamientos_ids.score_calidad",
        "acompanamientos_ids.nivel_csat",
        "meta_calidad",
    )
    def _compute_indicadores_calidad(self):

        for record in self:

            acompanamientos = record.acompanamientos_ids
            total_monitoreos = len(acompanamientos)

            record.calidad_promedio = (
                sum(acompanamientos.mapped("score_calidad")) / total_monitoreos
                if total_monitoreos
                else 0.0
            )

            record.nivel_cumplimiento = (
                (record.calidad_promedio / record.meta_calidad) * 100
                if record.meta_calidad
                else 0.0
            )

            respuestas = acompanamientos.filtered(lambda a: a.nivel_csat)
            satisfechas = respuestas.filtered(lambda a: a.nivel_csat == "bueno")

            record.csat_respuestas = len(respuestas)

            record.csat_satisfaccion = (
                (len(satisfechas) / len(respuestas)) * 100
                if respuestas
                else 0.0
            )

    @api.depends("asistencias_ids.estado_asistencia")
    def _compute_indicadores_asistencia(self):

        for record in self:

            asistencias = record.asistencias_ids

            programadas = asistencias.filtered(
                lambda a: a.estado_asistencia != "no_programado"
            )
            asistidas = asistencias.filtered(
                lambda a: a.estado_asistencia == "asistio"
            )

            record.sesiones_programadas = len(programadas)
            record.sesiones_asistidas = len(asistidas)

            record.porcentaje_asistencia = (
                (len(asistidas) / len(programadas)) * 100
                if programadas
                else 0.0
            )

    @api.depends(
        "actividades_ejecutadas_ids.actividad_ejecutada",
        "actividades_ejecutadas_ids.estado_ejecucion",
        "actividades_ejecutadas_ids.duracion_real_minutos",
    )
    def _compute_indicadores_ejecucion(self):

        for record in self:

            actividades = record.actividades_ejecutadas_ids
            total = len(actividades)

            ejecutadas = actividades.filtered(
                lambda a: a.actividad_ejecutada == "si"
            )
            oportunas = ejecutadas.filtered(
                lambda a: a.estado_ejecucion == "oportuna"
            )

            record.total_actividades_ejecutadas_registro = total
            record.actividades_ejecutadas = len(ejecutadas)

            record.porcentaje_ejecucion = (
                (len(ejecutadas) / total) * 100
                if total
                else 0.0
            )

            record.actividades_oportunas = len(oportunas)

            record.porcentaje_oportunidad = (
                (len(oportunas) / len(ejecutadas)) * 100
                if ejecutadas
                else 0.0
            )

            record.tiempo_promedio_minutos = (
                sum(ejecutadas.mapped("duracion_real_minutos")) / len(ejecutadas)
                if ejecutadas
                else 0.0
            )

    @api.constrains("numero_grupo")
    def _check_numero_grupo(self):
        for record in self:
            if record.numero_grupo <= 0:
                raise ValidationError(
                    "El número de grupo debe ser mayor que cero."
                )

    @api.constrains("meta_calidad")
    def _check_meta_calidad(self):
        for record in self:
            if record.meta_calidad <= 0:
                raise ValidationError(
                    "La meta de calidad debe ser mayor que cero."
                )
