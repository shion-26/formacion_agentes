from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date

class RegistroFI(models.Model):
    _name = "registro_fi"
    _description = "Registro Formación Inicial"
    _rec_name = "nombre_completo"

    _sql_constraints = [
        (
            "unique_participant_group",
            "unique(cedula, grupo_formacion_id)",
            "Ya existe un participante registrado con esta cédula en este grupo de formación.",
        ),
    ]

    name = fields.Char(
        string="Nombre",
        compute="_compute_name",
        store=True,
    )

    nombre_completo = fields.Char(
        string="Participante",
        compute="_compute_nombre_completo",
        store=True,
    )

    estado_registro = fields.Selection(
        [
            ("borrador", "Borrador"),
            ("parcial", "Parcial"),
            ("completo", "Completo"),
        ],
        string="Estado del registro",
        compute="_compute_estado_registro",
        store=True,
    )

    fecha_resumen = fields.Date(
        string="Fecha de registro",
        compute="_compute_fecha_resumen",
        store=True,
    )

    resumen_participante = fields.Char(
        string="Resumen participante",
        compute="_compute_resumen",
        store=True,
        readonly=True,
    )

    resumen_fecha = fields.Char(
        string="Resumen fecha",
        compute="_compute_resumen",
        store=True,
        readonly=True,
    )

    usuario_resumen = fields.Char(
        string="Usuario que registra",
        compute="_compute_usuario_resumen",
        store=True,
    )

    # ==========================================================
    # INFORMACIÓN PERSONAL
    # ==========================================================

    cedula = fields.Char(
        string="Cédula / ID",
        required=True,
    )

    nombre = fields.Char(
        string="Nombre completo",
        required=True,
    )

    fecha_nacimiento = fields.Date(
        string="Fecha de nacimiento",
        required=True,
    )

    edad = fields.Integer(
        string="Edad",
        compute="_compute_edad",
        store=True,
        readonly=True,
    )

    genero = fields.Selection(
        [
            ("masculino", "Masculino"),
            ("femenino", "Femenino"),
        ],
        string="Género",
        required=True,
    )

    # ==========================================================
    # INFORMACIÓN ACADÉMICA
    # ==========================================================

    campania_id = fields.Many2one(
        "training.campaign",
        string="Campaña",
        required=True,
    )

    grupo_base_id = fields.Many2one(
        "training.group",
        string="Grupo base",
        required=True,
    )

    numero_grupo = fields.Integer(
        string="Número de grupo",
        required=True,
    )

    grupo_formacion_id = fields.Many2one(
        "training.group.session",
        string="Grupo de formación",
        required=True,
        readonly=True,
    )

    formador_id = fields.Many2one(
        "training.trainer",
        string="Formador",
        required=True,
    )

    tipo_ingreso_id = fields.Many2one(
        "training.entry.type",
        string="Tipo de ingreso",
        required=True,
    )

    canal_id = fields.Many2one(
        "training.channel",
        string="Canal",
        help="Se asigna automáticamente con el primer Acompañamiento "
        "registrado para este agente; no es obligatorio al inscribirlo.",
    )

    codigo_grupo = fields.Char(
        string="Código del grupo",
        related="grupo_formacion_id.codigo_grupo",
        store=True,
        readonly=True,
    )

    fecha_ingreso = fields.Date(
        string="Fecha de ingreso",
        required=True,
    )

    # ==========================================================
    # RESULTADO FINAL
    # ==========================================================

    estado_final = fields.Selection(
        [
            ("apto", "Apto"),
            ("abandono", "Abandonó"),
            ("no_inicia", "No inicia"),
            ("renovar", "Por renovar"),
        ],
        string="Concepto final",
    )

    nota_final = fields.Integer(
        string="Nota evaluación final",
        help="Valor entre 0 y 100.",
    )

    horas_formacion = fields.Integer(
        string="Horas de formación recibidas",
        help="Total de horas cursadas.",
    )

    # ==========================================================
    # OBSERVACIONES
    # ==========================================================

    fecha_inicio = fields.Date(
        string="Fecha de inicio",
    )

    fecha_fin = fields.Date(
        string="Fecha de finalización",
    )

    observaciones = fields.Text(
        string="Observaciones",
    )

    # ==========================================================
    # ACOMPAÑAMIENTO (LIBRO 2)
    # ==========================================================

    acompanamientos_ids = fields.One2many(
        "acompanamiento",
        "participante_id",
        string="Acompañamientos",
    )

    tmo_promedio_segundos = fields.Integer(
        string="TMO promedio (segundos)",
        compute="_compute_tmo_promedio",
        store=True,
    )

    tmo_promedio = fields.Char(
        string="TMO promedio (mm:ss)",
        compute="_compute_tmo_promedio",
        store=True,
    )

    # ==========================================================
    # ASISTENCIA (LIBRO 4)
    # ==========================================================

    asistencias_ids = fields.One2many(
        "control.asistencia",
        "participante_id",
        string="Control de asistencia",
    )

    sesiones_programadas_agente = fields.Integer(
        string="Sesiones programadas (agente)",
        compute="_compute_asistencia_agente",
        store=True,
    )

    sesiones_asistidas_agente = fields.Integer(
        string="Sesiones asistidas (agente)",
        compute="_compute_asistencia_agente",
        store=True,
    )

    porcentaje_asistencia_agente = fields.Float(
        string="% Asistencia (agente)",
        compute="_compute_asistencia_agente",
        store=True,
    )


    # ==========================================================
    # COMPUTE METHODS
    # ==========================================================

    @api.depends("nombre")
    def _compute_name(self):
        for record in self:
            record.name = record.nombre or ""

    @api.depends("cedula", "nombre")
    def _compute_nombre_completo(self):
        for record in self:
            if record.cedula and record.nombre:
                record.nombre_completo = f"{record.cedula} - {record.nombre}"
            else:
                record.nombre_completo = record.nombre or ""

    @api.depends("fecha_nacimiento")
    def _compute_edad(self):
        today = fields.Date.today()

        for record in self:
            if record.fecha_nacimiento:
                born = record.fecha_nacimiento
                record.edad = (
                    today.year
                    - born.year
                    - ((today.month, today.day) < (born.month, born.day))
                )
            else:
                record.edad = 0

    @api.depends(
        "cedula",
        "nombre",
        "fecha_nacimiento",
        "genero",
        "campania_id",
        "grupo_base_id",
        "numero_grupo",
        "formador_id",
        "tipo_ingreso_id",
        "fecha_ingreso",
        "estado_final",
    )
    def _compute_estado_registro(self):

        for record in self:

            campos = [
                record.cedula,
                record.nombre,
                record.fecha_nacimiento,
                record.genero,
                record.campania_id,
                record.grupo_base_id,
                record.numero_grupo,
                record.formador_id,
                record.tipo_ingreso_id,
                record.fecha_ingreso,
                record.estado_final,
            ]

            llenos = sum(bool(campo) for campo in campos)

            if llenos == 0:
                record.estado_registro = "borrador"

            elif llenos < len(campos):
                record.estado_registro = "parcial"

            else:
                record.estado_registro = "completo"

    @api.depends("create_date")
    def _compute_fecha_resumen(self):

        today = fields.Date.today()

        for record in self:
            record.fecha_resumen = (
                fields.Date.to_date(record.create_date)
                if record.create_date
                else today
            )

    @api.depends("nombre", "fecha_resumen")
    def _compute_resumen(self):
        for record in self:

            record.resumen_participante = (
                record.nombre if record.nombre else "--"
            )

            if record.fecha_resumen:
                record.resumen_fecha = record.fecha_resumen.strftime("%d/%m/%Y")
            else:
                record.resumen_fecha = "--"

    @api.depends("create_uid")
    def _compute_usuario_resumen(self):

        for record in self:
            record.usuario_resumen = (
                record.create_uid.name
                if record.create_uid
                else self.env.user.name
            )

    @api.depends("acompanamientos_ids.duracion_gestion_segundos")
    def _compute_tmo_promedio(self):
        for record in self:

            acompanamientos = record.acompanamientos_ids
            total = len(acompanamientos)

            promedio_segundos = (
                round(
                    sum(acompanamientos.mapped("duracion_gestion_segundos"))
                    / total
                )
                if total
                else 0
            )

            record.tmo_promedio_segundos = promedio_segundos
            record.tmo_promedio = "{:02d}:{:02d}".format(
                promedio_segundos // 60, promedio_segundos % 60
            )

    @api.depends("asistencias_ids.estado_asistencia")
    def _compute_asistencia_agente(self):

        for record in self:

            asistencias = record.asistencias_ids

            programadas = asistencias.filtered(
                lambda a: a.estado_asistencia != "no_programado"
            )
            asistidas = asistencias.filtered(
                lambda a: a.estado_asistencia == "asistio"
            )

            record.sesiones_programadas_agente = len(programadas)
            record.sesiones_asistidas_agente = len(asistidas)

            record.porcentaje_asistencia_agente = (
                (len(asistidas) / len(programadas)) * 100
                if programadas
                else 0.0
            )

    @api.constrains(
        "cedula",
        "fecha_nacimiento",
        "fecha_ingreso",
        "nota_final",
        "horas_formacion",
        "fecha_inicio",
        "fecha_fin",
    )
    def _check_business_rules(self):
        today = date.today()

        for record in self:

            # Cédula
            if record.cedula:

                cedula = record.cedula.strip()

                if not cedula.isdigit():
                    raise ValidationError(
                        "La cédula solo puede contener números."
                    )

                if len(cedula) < 6 or len(cedula) > 15:
                    raise ValidationError(
                        "La cédula debe tener entre 6 y 15 dígitos."
                    )

            # Fecha de nacimiento
            if record.fecha_nacimiento:

                if record.fecha_nacimiento > today:
                    raise ValidationError(
                        "La fecha de nacimiento no puede ser futura."
                    )

                if record.edad > 100:
                    raise ValidationError(
                        "La edad del participante parece ser incorrecta."
                    )

            # Fecha de ingreso
            if record.fecha_ingreso:

                if record.fecha_ingreso > today:
                    raise ValidationError(
                        "La fecha de ingreso no puede ser futura."
                    )

                if (
                    record.fecha_nacimiento
                    and record.fecha_ingreso
                    and record.fecha_ingreso < record.fecha_nacimiento
                ):
                    raise ValidationError(
                        "La fecha de ingreso no puede ser anterior a la fecha de nacimiento."
                    )

            # Nota
            if record.nota_final < 0:
                raise ValidationError(
                    "La nota final no puede ser negativa."
                )

            if record.nota_final > 100:
                raise ValidationError(
                    "La nota final no puede ser mayor a 100."
                )

            # Horas
            if record.horas_formacion < 0:
                raise ValidationError(
                    "Las horas de formación no pueden ser negativas."
                )

            # Fechas de inicio y finalización
            if (
                record.fecha_inicio
                and record.fecha_fin
                and record.fecha_fin < record.fecha_inicio
            ):
                raise ValidationError(
                    "La fecha de finalización no puede ser anterior a la fecha de inicio."
                )

    @api.constrains("observaciones")
    def _check_longitud_textos(self):
        for record in self:
            if record.observaciones and len(record.observaciones) > 500:
                raise ValidationError(
                    "El campo 'Observaciones' no puede superar los 500 caracteres."
                )

    @api.model
    def _get_or_create_group_session(self, grupo_base_id, numero_grupo):
        session = self.env["training.group.session"].search(
            [
                ("grupo_base_id", "=", grupo_base_id),
                ("numero_grupo", "=", numero_grupo),
            ],
            limit=1,
        )

        if not session:
            session = self.env["training.group.session"].create(
                {
                    "grupo_base_id": grupo_base_id,
                    "numero_grupo": numero_grupo,
                }
            )

        return session

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            if vals.get("nombre"):
                vals["nombre"] = " ".join(
                    vals["nombre"].split()
                ).upper()

            if vals.get("cedula"):
                vals["cedula"] = vals["cedula"].strip()

            if vals.get("grupo_base_id") and vals.get("numero_grupo"):
                vals["grupo_formacion_id"] = self._get_or_create_group_session(
                    vals["grupo_base_id"], vals["numero_grupo"]
                ).id

        return super().create(vals_list)

    def write(self, vals):

        if vals.get("nombre"):
            vals["nombre"] = " ".join(
                vals["nombre"].split()
            ).upper()

        if vals.get("cedula"):
            vals["cedula"] = vals["cedula"].strip()

        if "grupo_base_id" in vals or "numero_grupo" in vals:

            for record in self:
                record_vals = dict(vals)

                grupo_base_id = vals.get("grupo_base_id", record.grupo_base_id.id)
                numero_grupo = vals.get("numero_grupo", record.numero_grupo)

                if grupo_base_id and numero_grupo:
                    record_vals["grupo_formacion_id"] = self._get_or_create_group_session(
                        grupo_base_id, numero_grupo
                    ).id

                super(RegistroFI, record).write(record_vals)

            return True

        return super().write(vals)
