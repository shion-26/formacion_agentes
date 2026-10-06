import calendar
import re
from datetime import date

from odoo import api, fields, models
from odoo.exceptions import ValidationError

HORA_RE = re.compile(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")


class ControlAsistencia(models.Model):
    _name = "control.asistencia"
    _description = "Control de Asistencia - Formación"

    _sql_constraints = [
        (
            "unique_id_sesion",
            "unique(id_sesion)",
            "Ya existe una sesión registrada con este ID.",
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

    @api.depends("id_sesion")
    def _compute_name(self):
        for record in self:
            record.name = record.id_sesion or "Nueva sesión"

    # ==================================================
    # 1. INFORMACIÓN GENERAL DE LA SESIÓN
    # ==================================================

    id_sesion = fields.Char(
        string="ID Sesión",
        required=True,
    )

    fecha_sesion = fields.Date(
        string="Fecha de la sesión",
        required=True,
    )

    hora_inicio = fields.Char(
        string="Hora inicio",
        required=True,
    )

    hora_fin = fields.Char(
        string="Hora fin",
        required=True,
    )

    duracion = fields.Char(
        string="Duración",
        compute="_compute_duracion",
        store=True,
        readonly=True,
    )

    tipo_sesion = fields.Selection(
        [
            ("induccion", "Inducción"),
            ("formacion", "Formación"),
            ("refuerzo", "Refuerzo"),
            ("coaching", "Coaching"),
            ("retroalimentacion", "Retroalimentación"),
        ],
        string="Tipo de sesión",
        required=True,
    )

    formador_id = fields.Many2one(
        "training.trainer",
        string="Formador",
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

    campania_id = fields.Many2one(
        "training.campaign",
        string="Campaña",
        related="participante_id.campania_id",
        store=True,
        readonly=True,
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

    # ==================================================
    # 2. INFORMACIÓN DEL PARTICIPANTE
    # ==================================================

    participante_id = fields.Many2one(
        "registro_fi",
        string="Participante / Agente",
        required=True,
    )

    cedula = fields.Char(
        string="Cédula / ID",
        related="participante_id.cedula",
        store=True,
        readonly=True,
    )

    cargo_id = fields.Many2one(
        "training.role",
        string="Cargo / Rol",
    )

    fecha_ingreso = fields.Date(
        string="Fecha de ingreso a la campaña",
        related="participante_id.fecha_ingreso",
        store=True,
        readonly=True,
    )

    antiguedad = fields.Char(
        string="Antigüedad en campaña",
        compute="_compute_antiguedad",
        store=True,
        readonly=True,
    )

    # ==================================================
    # 3. ASISTENCIA A LA SESIÓN
    # ==================================================

    estado_asistencia = fields.Selection(
        [
            ("asistio", "Asistió"),
            ("no_asistio", "No asistió"),
            ("justificado", "Justificado"),
            ("no_programado", "No programado"),
        ],
        string="Estado de asistencia",
        required=True,
    )

    motivo_inasistencia = fields.Selection(
        [
            ("incapacidad", "Incapacidad"),
            ("permiso", "Permiso"),
            ("vacaciones", "Vacaciones"),
            ("falla_tecnica", "Falla técnica"),
            ("otro", "Otro"),
        ],
        string="Motivo de inasistencia",
    )

    observaciones = fields.Text(
        string="Observaciones"
    )

    # ==================================================
    # 4. DETALLE DE LA SESIÓN
    # ==================================================

    tema = fields.Text(
        string="Tema / Contenido tratado",
        required=True,
    )

    objetivo = fields.Text(
        string="Objetivo de la sesión",
        required=True,
    )

    actividades = fields.Text(
        string="Actividades realizadas"
    )

    material_utilizado = fields.Char(
        string="Material / Recurso utilizado"
    )

    # ==================================================
    # 5. EVALUACIÓN RÁPIDA DE LA SESIÓN
    # ==================================================

    claridad = fields.Selection(
        [
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
        ],
        string="Claridad del contenido",
    )

    aplicabilidad = fields.Selection(
        [
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
        ],
        string="Aplicabilidad",
    )

    utilidad = fields.Selection(
        [
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
        ],
        string="Utilidad",
    )

    participacion = fields.Selection(
        [
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
        ],
        string="Participación del grupo",
    )

    observaciones_formador = fields.Text(
        string="Observaciones del formador"
    )

    @api.constrains(
        "observaciones",
        "tema",
        "objetivo",
        "actividades",
        "observaciones_formador",
    )
    def _check_longitud_textos(self):
        campos = [
            ("observaciones", "Observaciones"),
            ("tema", "Tema / Contenido tratado"),
            ("objetivo", "Objetivo de la sesión"),
            ("actividades", "Actividades realizadas"),
            ("observaciones_formador", "Observaciones del formador"),
        ]

        for record in self:
            for field_name, label in campos:
                valor = getattr(record, field_name)

                if valor and len(valor) > 500:
                    raise ValidationError(
                        f"El campo '{label}' no puede superar los 500 caracteres."
                    )

    @api.constrains("tema", "objetivo", "actividades", "material_utilizado")
    def _check_espacios_detalle_sesion(self):
        campos = [
            ("tema", "Tema / Contenido tratado"),
            ("objetivo", "Objetivo de la sesión"),
            ("actividades", "Actividades realizadas"),
            ("material_utilizado", "Material / Recurso utilizado"),
        ]

        for record in self:
            for field_name, label in campos:
                valor = getattr(record, field_name)

                if valor and not valor.strip():
                    raise ValidationError(
                        f"El campo '{label}' no puede contener únicamente espacios en blanco."
                    )

    @api.constrains("observaciones_formador")
    def _check_espacios_observaciones_formador(self):
        for record in self:
            if (
                record.observaciones_formador
                and not record.observaciones_formador.strip()
            ):
                raise ValidationError(
                    "El campo 'Observaciones del formador' no puede contener "
                    "únicamente espacios en blanco."
                )

    @api.constrains("material_utilizado")
    def _check_longitud_material_utilizado(self):
        for record in self:
            if record.material_utilizado and len(record.material_utilizado) > 200:
                raise ValidationError(
                    "El campo 'Material / Recurso utilizado' no puede superar "
                    "los 200 caracteres."
                )

    @api.depends("hora_inicio", "hora_fin")
    def _compute_duracion(self):
        for record in self:
            if (
                record.hora_inicio
                and record.hora_fin
                and HORA_RE.match(record.hora_inicio)
                and HORA_RE.match(record.hora_fin)
            ):
                inicio_h, inicio_m = (int(x) for x in record.hora_inicio.split(":"))
                fin_h, fin_m = (int(x) for x in record.hora_fin.split(":"))

                total_minutos = (fin_h * 60 + fin_m) - (inicio_h * 60 + inicio_m)

                if total_minutos > 0:
                    horas, minutos = divmod(total_minutos, 60)
                    partes = []

                    if horas:
                        partes.append(f"{horas} hora" + ("s" if horas != 1 else ""))

                    if minutos or not horas:
                        partes.append(f"{minutos} minuto" + ("s" if minutos != 1 else ""))

                    record.duracion = " y ".join(partes)
                else:
                    record.duracion = False
            else:
                record.duracion = False

    @api.depends("fecha_ingreso", "fecha_sesion")
    def _compute_antiguedad(self):
        for record in self:
            if not record.fecha_ingreso:
                record.antiguedad = False
                continue

            fecha_referencia = record.fecha_sesion or fields.Date.today()

            if fecha_referencia < record.fecha_ingreso:
                record.antiguedad = False
                continue

            years = fecha_referencia.year - record.fecha_ingreso.year
            months = fecha_referencia.month - record.fecha_ingreso.month
            days = fecha_referencia.day - record.fecha_ingreso.day

            if days < 0:
                months -= 1
                mes_anterior = fecha_referencia.month - 1 or 12
                anio_mes_anterior = (
                    fecha_referencia.year
                    if fecha_referencia.month > 1
                    else fecha_referencia.year - 1
                )
                days += calendar.monthrange(anio_mes_anterior, mes_anterior)[1]

            if months < 0:
                years -= 1
                months += 12

            partes = []

            if years:
                partes.append(f"{years} año" + ("s" if years != 1 else ""))

            if months:
                partes.append(f"{months} mes" + ("es" if months != 1 else ""))

            if days:
                partes.append(f"{days} día" + ("s" if days != 1 else ""))

            if not partes:
                partes.append("0 días")

            record.antiguedad = " y ".join(partes)

    @api.onchange("estado_asistencia")
    def _onchange_estado_asistencia(self):
        if self.estado_asistencia in ("asistio", "no_programado"):
            self.motivo_inasistencia = False

    @api.constrains("estado_asistencia", "motivo_inasistencia")
    def _check_motivo_inasistencia(self):
        for record in self:

            if (
                record.estado_asistencia in ("no_asistio", "justificado")
                and not record.motivo_inasistencia
            ):
                raise ValidationError(
                    "Debe indicar el motivo de inasistencia cuando el estado "
                    "de asistencia es 'No asistió' o 'Justificado'."
                )

            if (
                record.estado_asistencia in ("asistio", "no_programado")
                and record.motivo_inasistencia
            ):
                raise ValidationError(
                    "No puede registrar un motivo de inasistencia cuando el "
                    "estado de asistencia es 'Asistió' o 'No programado'."
                )

    @api.constrains(
        "estado_asistencia",
        "tema",
        "objetivo",
        "actividades",
        "material_utilizado",
    )
    def _check_detalle_sesion_no_aplica(self):
        for record in self:
            if record.estado_asistencia not in ("no_asistio", "no_programado"):
                continue

            if (
                record.tema
                or record.objetivo
                or record.actividades
                or record.material_utilizado
            ):
                raise ValidationError(
                    "No es posible registrar el detalle de la sesión (tema, "
                    "objetivo, actividades o material utilizado) cuando el "
                    "participante no asistió o la sesión no fue programada."
                )

    @api.constrains("id_sesion", "fecha_sesion", "hora_inicio", "hora_fin")
    def _check_informacion_general_sesion(self):
        today = date.today()

        for record in self:

            if record.id_sesion and not record.id_sesion.strip():
                raise ValidationError(
                    "El ID de sesión no puede estar vacío."
                )

            if record.fecha_sesion and record.fecha_sesion > today:
                raise ValidationError(
                    "La fecha de la sesión no puede ser futura."
                )

            if record.hora_inicio and not HORA_RE.match(record.hora_inicio):
                raise ValidationError(
                    "La hora de inicio debe tener el formato HH:MM."
                )

            if record.hora_fin and not HORA_RE.match(record.hora_fin):
                raise ValidationError(
                    "La hora de fin debe tener el formato HH:MM."
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
                        "La hora de fin debe ser posterior a la hora de inicio."
                    )

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            if vals.get("id_sesion"):
                vals["id_sesion"] = vals["id_sesion"].strip().upper()

        return super().create(vals_list)

    def write(self, vals):

        if vals.get("id_sesion"):
            vals["id_sesion"] = vals["id_sesion"].strip().upper()

        return super().write(vals)