<template>
  <div class="plataforma-layout" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    
    <BarraLateralPlataforma :is-open="isSidebarOpen" />
    
    <div class="plataforma-contenido" :class="{ 'shifted': isSidebarOpen }">
      
      <EncabezadoPlataforma 
        :titulo="dispositivo.nombre || 'Cargando Dispositivo...'"
        :subtitulo="'Tipo: ' + (dispositivo.tipo || 'N/A')"
        @toggle-sidebar="toggleSidebar" 
        :is-sidebar-open="isSidebarOpen"
      >
        
      </EncabezadoPlataforma>

      <div class="detalle-dispositivo-contenido">
        
        <div v-if="loading" class="alert-info">Cargando sensores...</div>
        <div v-else-if="error" class="alert-error">{{ error }}</div>
        
        <div v-else>
            <div class="sensores-header">
                <h3>Sensores Conectados ({{ sensores.length }})</h3>
                <button @click="openCreateSensorModal" class="btn-primary-action">
                    <i class="bi bi-plus-circle-fill"></i> Agregar Sensor
                </button>
            </div>
            
            <div class="sensores-grid">
                <TarjetaSensor 
                    v-for="sensor in sensores" 
                    :key="sensor.id"
                    :sensor="sensor"
                    :is-dark="isDark"
                    @edit-sensor="openEditSensorModal"
                    @delete-sensor="confirmarEliminacionSensor" />
            
            </div>
            
            <div v-if="sensores.length === 0" class="alert-empty-data">
                Este dispositivo no tiene sensores registrados.
            </div>
        </div>
      </div>
    </div>
    
    <ModalCrearSensor 
        v-if="mostrarModalCrearSensor"
        :dispositivo-id="dispositivoId"
        @sensor-creado="handleSensorCreated"
        @close="closeCreateSensorModal"
    />
<ModalEditarSensor 
    v-if="mostrarModalEditarSensor"
    :sensor-id="sensorSeleccionado" 
    @sensor-actualizado="handleSensorUpdated"
    @close="closeEditSensorModal"
/>
<ModalEliminarSensor 
    v-if="mostrarModalEliminarSensor"
    :sensor-id="sensorEliminarId"
    :sensor-nombre="sensorEliminarNombre"
    @cancelar="cancelarEliminacionSensor"
    @confirmar="ejecutarEliminacionSensor"
/>


    </div>
</template>

<script>
// Componentes de Layout
import BarraLateralPlataforma from '../plataforma/BarraLateralPlataforma.vue';
import EncabezadoPlataforma from '../plataforma/EncabezadoPlataforma.vue';

// Componentes de la vista actual

import TarjetaSensor from '../sensores/TarjetaSensor.vue'; 
import ModalCrearSensor from '../sensores/ModalCrearSensor.vue'; 
import ModalEditarSensor from '../sensores/ModalEditarSensor.vue'; 
import ModalEliminarSensor from '../sensores/ModalEliminarSensor.vue';

const API_BASE_URL = 'http://127.0.0.1:8001';

export default {
    name: 'DetalleDispositivo',
    components: {
        BarraLateralPlataforma,
        EncabezadoPlataforma,
       
        TarjetaSensor, 
        ModalCrearSensor,
        ModalEditarSensor, 
        ModalEliminarSensor,
    },
    data() {
        return {
            isDark: false, 
            isSidebarOpen: true, 
            loading: true, 
            error: null,
            dispositivo: { nombre: null, tipo: null, dispositivo_id: null },
            sensores: [],
            mostrarModalCrearSensor: false,
            mostrarModalEditarSensor: false, 
            sensorSeleccionado: null,
            mostrarModalEliminarSensor: false, 
            sensorEliminarId: null,
            sensorEliminarNombre: null,
            
        };
    },
    computed: {
        dispositivoId() { return this.$route.params.id; },
       
    },
    mounted() {
        this.cargarDetalles();
        this.detectarTemaSistema();
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', this.handleThemeChange);
        }
    },
    beforeUnmount() { 
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', this.handleThemeChange);
        }
    },
    methods: {
        // -----------------------------------------------------
        // CONSUMO DE API: Cargar Detalles y Sensores
        // -----------------------------------------------------
        async cargarDetalles() {
            this.loading = true;
            this.error = null;
            const token = localStorage.getItem('accessToken');
            
            if (!token || !this.dispositivoId) { this.$router.push('/'); return; }

            try {
                // 1. Obtener detalles del dispositivo (para el encabezado)
                const dispResponse = await fetch(`${API_BASE_URL}/api/dispositivos/${this.dispositivoId}`, { headers: { 'Authorization': `Bearer ${token}` } });
                if (!dispResponse.ok) { throw new Error('Dispositivo no encontrado o acceso denegado.'); }
                
                const dispositivoData = await dispResponse.json();
                this.dispositivo = { ...this.dispositivo, ...dispositivoData };
                
                // 2. Obtener lista de sensores
                const sensorResponse = await fetch(`${API_BASE_URL}/api/sensores/dispositivo/${this.dispositivoId}`, { headers: { 'Authorization': `Bearer ${token}` } });
                const sensorData = await sensorResponse.json();

                if (sensorResponse.status === 404) { this.sensores = []; }
                else if (!sensorResponse.ok) { throw new Error('Fallo al obtener sensores.'); }
                else {
                    this.sensores = sensorData.map(s => ({
                        ...s,
                        habilitado: s.habilitado === 1 || s.habilitado === true, 
                        total_campos: s.total_campos || 0 // Asegura que el contador existe
                    }));
                }

            } catch (err) {
                this.error = err.message || 'Error al cargar los detalles.';
            } finally {
                this.loading = false;
            }
        },
        
        // -----------------------------------------------------
        // GESTIÓN DE MODALES Y ACCIONES
        // -----------------------------------------------------
        
        // Creación
        openCreateSensorModal() { this.mostrarModalCrearSensor = true; },
        closeCreateSensorModal() { this.mostrarModalCrearSensor = false; },
        handleSensorCreated() {
            this.closeCreateSensorModal();
            this.cargarDetalles(); // Recargar para mostrar el nuevo sensor
        },
   

// ...
openEditSensorModal(sensor) {
    // 1. Almacena el ID
    this.sensorSeleccionado = sensor.id; 
    // 2. Abre el modal
    this.mostrarModalEditarSensor = true;
},

closeEditSensorModal() {
    // Solo cierra la bandera de visualización, la limpieza se hace en el updated
    this.mostrarModalEditarSensor = false; 
    // Mantenemos el sensorSeleccionado por ahora, se limpia en handleUpdated
},
// DetalleDispositivo.vue (métodos)
// DetalleDispositivo.vue
// DetalleDispositivo.vue (métodos)
handleSensorUpdated(data) {
    // 1. Limpieza y cierre
    this.mostrarModalEditarSensor = false;
    this.sensorSeleccionado = null;
    
    let updatedSensorData = Array.isArray(data) ? data[0] : data;

    // 🚨 CORRECCIÓN CRÍTICA: Añadir el campo 'total_campos' si falta (para que el TarjetaSensor no falle)
    if (!updatedSensorData.total_campos) {
        // Busca el objeto original en el array para obtener el conteo de campos existente
        const originalSensor = this.sensores.find(s => s.id === updatedSensorData.id);
        updatedSensorData.total_campos = originalSensor ? originalSensor.total_campos : 0;
    }
    
    // 2. Actualización local
    const index = this.sensores.findIndex(s => s.id === updatedSensorData.id);

    if (index !== -1) {
        // Actualiza el sensor directamente en el array local (splice)
        this.sensores.splice(index, 1, updatedSensorData);
    } else {
        // Fallback: Recarga total si el sensor no se encuentra
        this.cargarDetalles();
    }
},
// ...
        // Eliminación
        confirmarEliminacionSensor(sensorId, nombre) {
            this.sensorEliminarId = sensorId;
            this.sensorEliminarNombre = nombre;
            this.mostrarModalEliminarSensor = true;
        },
        cancelarEliminacionSensor() {
            this.mostrarModalEliminarSensor = false;
            this.sensorEliminarId = null;
            this.sensorEliminarNombre = null;
        },
        async ejecutarEliminacionSensor(sensorId) {
            const token = localStorage.getItem('accessToken');
            try {
                const response = await fetch(`${API_BASE_URL}/api/sensores/${sensorId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` },
                });

                if (!response.ok) { throw new Error('Fallo al eliminar el sensor.'); }

                alert('Sensor eliminado exitosamente.');
                this.cancelarEliminacionSensor();
                this.cargarDetalles(); // Recargar la lista
            } catch (err) {
                alert('Error: ' + err.message);
                this.cancelarEliminacionSensor();
            }
        },
        
        // -----------------------------------------------------
        // LÓGICA DE LAYOUT Y NAVEGACIÓN
        // -----------------------------------------------------
        goBack() { 
            // Vuelve a la vista de detalle de proyecto. Asume que el proyecto ID está en el dispositivo.
            this.$router.push(`/detalle-proyecto/${this.dispositivo.proyecto_id}`); 
        },
        toggleSidebar() { this.isSidebarOpen = !this.isSidebarOpen; },
        handleThemeChange(event) { this.isDark = event.matches; },
        detectarTemaSistema() {
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                this.isDark = true;
            } else {
                this.isDark = false;
            }
        }
    }
};
</script>
<style scoped lang="scss">
// ----------------------------------------
// VARIABLES DE LA PALETA "IoT SPECTRUM"
// ----------------------------------------
$WIDTH-SIDEBAR: 280px; 
$WIDTH-CLOSED: 80px; 
$WHITE-SOFT: #F7F9FC; 
$DARK-BG-CONTRAST: #1E1E30; 
$LIGHT-TEXT: #E4E6EB;
$DARK-TEXT: #333333;
$PRIMARY-PURPLE: #8A2BE2;
$SUCCESS-COLOR: #1ABC9C;
$GRAY-COLD: #99A2AD;
$SUBTLE-BG-LIGHT: #FFFFFF;
$DANGER-COLOR: #FF5733;

// ----------------------------------------
// LAYOUT PRINCIPAL Y CONTENIDO
// ----------------------------------------
.plataforma-layout {
    display: flex;
    min-height: 100vh;
    transition: background-color 0.3s;
}

.plataforma-contenido {
    position: relative;
    margin-left: $WIDTH-CLOSED;
    flex-grow: 1;
    padding: 0; 
    transition: margin-left 0.3s ease-in-out;
    
    &.shifted {
        margin-left: $WIDTH-SIDEBAR;
    }
}

.detalle-dispositivo-contenido {
    padding: 20px 40px 40px 40px; /* Padding debajo del encabezado */
}

// Estilo del botón Volver (Usado en el slot #title-prefix)
.btn-back {
    background: none;
    border: none;
    color: $DARK-TEXT;
    font-size: 1.4rem;
    margin-right: 15px;
    cursor: pointer;
    transition: color 0.2s;
    
    &:hover {
        color: $PRIMARY-PURPLE;
    }
}


// ------------------------------------
// HEADER DE SENSORES Y ACCIONES
// ------------------------------------
.sensores-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    
    h3 {
        font-size: 1.5rem;
        font-weight: 600;
        // Color adaptado en el tema
    }
    
    .btn-primary-action {
        background-color: $SUCCESS-COLOR;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: 600;
        i { margin-right: 5px; }
    }
}

// ------------------------------------
// GRID DE SENSORES
// ------------------------------------
.sensores-grid {
    display: grid;
    /* Dos columnas para tarjetas de sensores */
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); 
    gap: 20px;
}

// Estilo para el mensaje de datos vacíos
.alert-empty-data {
    padding: 20px;
    border-radius: 8px;
    margin-top: 20px;
    text-align: center;
    font-style: italic;
    background-color: rgba($PRIMARY-PURPLE, 0.1);
    color: $PRIMARY-PURPLE;
}


// ------------------------------------
// ESTILOS DE TEMA (MODO CLARO/OSCURO)
// ------------------------------------

// MODO CLARO (Default)
.theme-light {
    background-color: $WHITE-SOFT;
    color: $DARK-TEXT;
    
    .btn-back { color: $DARK-TEXT; }
    .sensores-header h3 { color: $DARK-TEXT; }
}

// MODO OSCURO
.theme-dark {
    background-color: $DARK-BG-CONTRAST; 
    color: $LIGHT-TEXT;
    
    .btn-back { color: $LIGHT-TEXT; }
    .plataforma-contenido { background-color: $DARK-BG-CONTRAST; }
    .sensores-header h3 { color: $LIGHT-TEXT; }

    .alert-info {
        background-color: rgba($LIGHT-TEXT, 0.1);
        color: $LIGHT-TEXT;
    }
    .alert-error {
        background-color: rgba($DANGER-COLOR, 0.2);
        color: $LIGHT-TEXT;
    }
}
</style>