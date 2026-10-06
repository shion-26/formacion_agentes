{
    'name': 'Formación Agentes',
    'summary': 'Gestiona la formación y certificación de agentes',
    'version': '1.0.0',
    'author': 'Custom',
    'website': 'https://example.com',
    'category': 'Human Resources',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'web',
        'hr',
    ],

    'data': [
        # Seguridad
        'security/formacion_security.xml',
        'security/ir.model.access.csv',

        # Secuencias
        'data/programacion_actividad_sequence.xml',

        # Vistas
        'views/registro_fi_views.xml',
        'views/registro_fi_report_views.xml',
        'views/acompanamiento_views.xml',
        'views/plan_intervencion_views.xml',
        'views/control_asistencia_views.xml',
        'views/programacion_actividad_views.xml',
        'views/programacion_actividad_report_views.xml',
        'views/actividad_ejecutada_views.xml',
        'views/training_campaign_views.xml',
        'views/training_group_views.xml',
        'views/training_group_session_views.xml',
        'views/training_trainer_views.xml',
        'views/training_entry_type_views.xml',
        'views/training_channel_views.xml',
        'views/training_role_views.xml',

        # Menús
        'views/menu.xml',
    ],

    'assets': {
        'web.assets_backend': [

            # CSS
            'formacion_agentes/static/src/css/formacion.css',

            # Barra de acciones reutilizable (Guardar / Limpiar)
            'formacion_agentes/static/src/js/fi_action_bar.js',
            'formacion_agentes/static/src/xml/fi_action_bar.xml',

            # Widget reutilizable: captura de horas 12h + AM/PM (training_time)
            'formacion_agentes/static/src/js/training_time_widget.js',
            'formacion_agentes/static/src/xml/training_time_widget.xml',

            # Widget reutilizable: textarea con contador de caracteres (char_counter_text)
            'formacion_agentes/static/src/js/char_counter_text_widget.js',
            'formacion_agentes/static/src/xml/char_counter_text_widget.xml',

            # Registro FI
            'formacion_agentes/static/src/js/concepto_final_buttons.js',
            'formacion_agentes/static/src/xml/concepto_final_buttons.xml',

            # Widget reutilizable: entero obligatorio que no se autocompleta
            # en 0 (muestra placeholder mientras no se haya ingresado un valor)
            'formacion_agentes/static/src/js/required_integer_widget.js',
            'formacion_agentes/static/src/xml/required_integer_widget.xml',
            'formacion_agentes/static/src/js/required_integer_validity.js',

            # Acompañamiento
            'formacion_agentes/static/src/js/quality_widgets.js',
            'formacion_agentes/static/src/xml/quality_widgets.xml',

            'formacion_agentes/static/src/js/mmss_time_widget.js',
            'formacion_agentes/static/src/xml/mmss_time_widget.xml',

            # Planes de Intervención
            'formacion_agentes/static/src/js/estado_plan_buttons.js',
            'formacion_agentes/static/src/xml/estado_plan_buttons.xml',

            'formacion_agentes/static/src/js/file_dropzone_widget.js',
            'formacion_agentes/static/src/xml/file_dropzone_widget.xml',

            # Control de Asistencia
            'formacion_agentes/static/src/js/estado_asistencia_buttons.js',
            'formacion_agentes/static/src/xml/estado_asistencia_buttons.xml',

            # Widget reutilizable: Selection que permanece visible (con
            # placeholder) y solo queda bloqueado con disabled real
            'formacion_agentes/static/src/js/selection_disabled_placeholder_widget.js',
            'formacion_agentes/static/src/xml/selection_disabled_placeholder_widget.xml',

            # Widget reutilizable: campos related/computed de solo lectura
            # con placeholder mientras no exista un participante
            'formacion_agentes/static/src/js/readonly_related_placeholder_widget.js',
            'formacion_agentes/static/src/xml/readonly_related_placeholder_widget.xml',

            # Programación de Actividades
            'formacion_agentes/static/src/js/estado_programacion_buttons.js',
            'formacion_agentes/static/src/xml/estado_programacion_buttons.xml',

            'formacion_agentes/static/src/js/estado_final_actividad_buttons.js',
            'formacion_agentes/static/src/xml/estado_final_actividad_buttons.xml',

            # Salto automático a Actividad Ejecutada al guardar con Estado final = Ejecutada
            'formacion_agentes/static/src/js/programacion_actividad_form_controller.js',

            # Actividades Ejecutadas
            'formacion_agentes/static/src/js/actividad_ejecutada_buttons.js',
            'formacion_agentes/static/src/xml/actividad_ejecutada_buttons.xml',

            'formacion_agentes/static/src/js/estado_ejecucion_buttons.js',
            'formacion_agentes/static/src/xml/estado_ejecucion_buttons.xml',
        ],
    },

    'installable': True,
    'application': True,
}