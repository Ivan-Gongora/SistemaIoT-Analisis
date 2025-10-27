<template>
  <div class="modulo-actividad-reciente" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    
    <h3 class="modulo-titulo">Actividad Reciente</h3>
    <p class="modulo-subtitulo">Eventos del sistema en tiempo real (Por el momento son datos fijos)</p>
    
   <div class="event-list">
  <div v-for="(event, index) in recentEvents" :key="index" class="event-item">
    
    <i :class="getIconClass(event.type)" class="event-icon"></i>
    
    <div class="event-details">
      <p class="event-title">{{ event.title }}</p>
      <p class="event-source">{{ event.source }}</p>
    </div>
    <span class="event-time">{{ event.time }}</span>
  </div>
</div>
  </div>
</template>

<script>
export default {
    name: 'ActividadReciente',
    props: {
        isDark: {
            type: Boolean,
            required: true
        }
    },
    data() {
        return {
            // Datos simulados (futura API de eventos)
            recentEvents: [
                { type: 'new', title: 'Nuevo dispositivo conectado', source: 'Sensor Temperatura Sala', time: 'Hace 2 minutos' },
                { type: 'alert', title: 'Alerta de batería baja', source: 'Sensor Industrial A1', time: 'Hace 15 minutos' },
                { type: 'report', title: 'Reporte generado', source: 'Análisis Semanal Industrial', time: 'Hace 30 minutos' },
                { type: 'error', title: 'Fallo de conexión crítico', source: 'Gateway Principal', time: 'Hace 1 hora' },
            ]
        };
    },
    // ActividadReciente.vue <script> (Añadir a methods)

methods: {
    // 🚨 NUEVA FUNCIÓN: Mapea el tipo de evento al ícono y color de Bootstrap
    getIconClass(type) {
        switch (type) {
            case 'new':
                return 'bi bi-plus-circle-fill text-success'; // Para nuevo registro
            case 'alert':
                return 'bi bi-exclamation-triangle-fill text-warning'; // Para alertas (batería, etc.)
            case 'report':
                return 'bi bi-file-earmark-bar-graph-fill text-info'; // Para reportes generados
            case 'error':
                return 'bi bi-x-octagon-fill text-danger'; // Para fallos críticos
            default:
                return 'bi bi-info-circle-fill';
        }
    },
    
}
}
</script>

<style scoped lang="scss">
// ----------------------------------------
// VARIABLES DE LA PALETA
// ----------------------------------------
// $LIGHT-TEXT: #E4E6EB;
// $DARK-TEXT: #333333;
// $GRAY-COLD: #99A2AD;
// $SUCCESS-COLOR: #1ABC9C;
// $ALERT-COLOR: #c69a13; 
// $ERROR-COLOR: #E74C3C;
// $INFO-COLOR: #8A2BE2;
// $SUBTLE-BG-LIGHT: #FFFFFF;
// $BLUE-MIDNIGHT: #1A1A2E; 
// $BG-CARD-DARK: #2B2B40; // Fondo de la tarjeta en modo oscuro

// ----------------------------------------
// ESTILOS PRINCIPALES DEL MÓDULO
// ----------------------------------------
.modulo-actividad-reciente {
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    height: 100%;
    transition: background-color 0.3s;
}

.modulo-titulo { font-size: 1.4rem; font-weight: 600; margin-bottom: 5px; }

.modulo-subtitulo {
    font-size: 0.9rem;
    margin-bottom: 20px;
    padding-bottom: 5px;
    border-bottom: 1px solid; 
}

// ----------------------------------------
// LISTA DE EVENTOS
// ----------------------------------------
.event-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.event-item {
    display: grid;
    grid-template-columns: 10px 1fr auto; /* Punto, Detalles, Tiempo */
    gap: 10px;
    align-items: center;
}

// ActividadReciente.vue <style> (Fragmento)

// ----------------------------------------
// LISTA DE EVENTOS
// ----------------------------------------

.event-item {
    display: grid;
    // 🚨 Reducimos el tamaño de la primera columna para el ícono
    grid-template-columns: 25px 1fr auto; 
    gap: 10px;
    align-items: center;
}

// 🚨 NUEVA CLASE: Estilo del Ícono
.event-icon {
    font-size: 1.1rem; /* Asegura un tamaño visible */
    text-align: center;
    width: 25px;
}


.event-details {
    .event-title { font-weight: 500; margin: 0; font-size: 0.95rem; }
    .event-source { font-size: 0.8rem; margin: 0; }
}

.event-time { font-size: 0.8rem; text-align: right; }

// ----------------------------------------
// TEMAS
// ----------------------------------------
.theme-light {
    background-color: $SUBTLE-BG-LIGHT;
    color: $DARK-TEXT;
    .modulo-subtitulo { border-bottom-color: #ddd; }
    .event-source, .event-time { color: $GRAY-COLD; }
}

.theme-dark {
    background-color: $BG-CARD-DARK; /* Fondo de tarjeta un poco más claro que el fondo de la página */
    color: $LIGHT-TEXT;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
    
    .modulo-titulo { color: $LIGHT-TEXT; }
    .modulo-subtitulo { border-bottom-color: rgba($LIGHT-TEXT, 0.1); }
    .event-details .event-source, .event-time { color: $GRAY-COLD; }
}
</style>