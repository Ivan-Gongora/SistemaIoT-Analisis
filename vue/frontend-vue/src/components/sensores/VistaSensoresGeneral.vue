<template>
  <div class="plataforma-layout" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    
    <BarraLateralPlataforma :is-open="isSidebarOpen" />
    
    <div class="plataforma-contenido" :class="{ 'shifted': isSidebarOpen }">
      
      <EncabezadoPlataforma 
        titulo="Sensores (Global)"
        subtitulo="Vista de todos los sensores agrupados por proyecto y dispositivo"
        @toggle-sidebar="toggleSidebar" 
        :is-sidebar-open="isSidebarOpen"
      />

      <div class="sensores-general-contenido">
        
        <div v-if="loading" class="alert-info">Cargando todos los sensores...</div>
        <div v-else-if="error" class="alert-error">{{ error }}</div>
        <div v-else-if="Object.keys(sensoresAgrupados).length === 0" class="alert-empty">
          <i class="bi bi-box-fill"></i> No se encontraron sensores.
        </div>
        
        <div v-else>
          <section 
            v-for="(proyectoData, nombreProyecto) in sensoresAgrupados" 
            :key="nombreProyecto" 
            class="proyecto-seccion"
          >
            <h2 class="proyecto-titulo"><i class="bi bi-folder2-open"></i> {{ nombreProyecto }}</h2>

            <div 
              v-for="(dispositivoData, nombreDispositivo) in proyectoData.dispositivos" 
              :key="nombreDispositivo" 
              class="dispositivo-subseccion"
            >
              <h3 class="dispositivo-titulo"><i class="bi bi-tablet-fill"></i> {{ nombreDispositivo }}</h3>
              
              <div class="lista-sensores-container">
                <div class="lista-header">
                  <div class="col-sensor">Sensor</div>
                  <div class="col-tipo">Tipo</div>
                  <div class="col-campos">Campos</div>
                  <div class="col-estado">Estado</div>
                  <div class="col-acciones">Acciones</div>
                </div>
                <div class="lista-body">
    
    <router-link 
        v-for="sensor in dispositivoData.sensores" 
        :key="sensor.id" 
        :to="{ name: 'DetalleSensor', params: { id: sensor.id } }"
        custom
        v-slot="{ navigate }"
    >
        <div 
            class="lista-fila" 
            @click="navigate" 
            role="link" 
            style="cursor: pointer;"
        >
            <div class="col-sensor">{{ sensor.nombre }}</div>
            <div class="col-tipo">{{ sensor.tipo }}</div>
            <div class="col-campos">{{ sensor.total_campos }}</div>
            <div class="col-estado">
                <span class="status-badge" :class="sensor.habilitado ? 'active' : 'inactive'">
                    {{ sensor.habilitado ? 'Activo' : 'Inactivo' }}
                </span>
            </div>
            <div class="col-acciones">
                <button @click.stop="navigateToSensorDetail(sensor.id)" class="btn-action btn-view" title="Ver Campos">
                    <i class="bi bi-eye-fill"></i>
                </button>
                <button @click.stop="openEditSensorModal(sensor)" class="btn-action btn-edit" title="Modificar">
                    <i class="bi bi-pencil"></i>
                </button>
                <button @click.stop="confirmarEliminacionSensor(sensor.id, sensor.nombre)" class="btn-action btn-delete" title="Eliminar">
                              <i class="bi bi-trash"></i>
                </button>
            </div>
        </div>
    </router-link>

</div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
    <!-- Modales -->
     </div> <ModalEditarSensor 
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
 @confirmar="ejecutarEliminacionSensor(sensorEliminarId)"
 />
</template>

<script>
// Componentes de Layout
import BarraLateralPlataforma from '../plataforma/BarraLateralPlataforma.vue';
import EncabezadoPlataforma from '../plataforma/EncabezadoPlataforma.vue';
// Importamos los modales si los vamos a usar aquí
import ModalEditarSensor from './ModalEditarSensor.vue'; 
import ModalEliminarSensor from './ModalEliminarSensor.vue';
const API_BASE_URL = 'http://127.0.0.1:8001';

export default {
    name: 'VistaSensoresGeneral',
    components: {
        BarraLateralPlataforma,
        EncabezadoPlataforma,
        ModalEditarSensor,
        ModalEliminarSensor,
    },
    data() {
        return {
            isDark: false,
            isSidebarOpen: true,
            loading: true,
            error: null,
            sensores: [], // La lista plana de la API
            
            // Estados de Modales
            mostrarModalEditarSensor: false,
            sensorSeleccionado: null,

            mostrarModalEliminarSensor: false,
            sensorEliminarId: null,
            sensorEliminarNombre: null,
        };
    },
    computed: {
        //  Agrupación Doble (Proyecto -> Dispositivo -> Sensores)
        sensoresAgrupados() {
            const grupos = {};

            for (const sensor of this.sensores) {
                const proyecto = sensor.nombre_proyecto || 'Proyecto Desconocido';
                const dispositivo = sensor.nombre_dispositivo || 'Dispositivo Desconocido';

                if (!grupos[proyecto]) {
                    grupos[proyecto] = { nombre: proyecto, dispositivos: {} };
                }
                
                if (!grupos[proyecto].dispositivos[dispositivo]) {
                    grupos[proyecto].dispositivos[dispositivo] = { nombre: dispositivo, sensores: [] };
                }
                
                grupos[proyecto].dispositivos[dispositivo].sensores.push(sensor);
            }
            return grupos;
        }
    },
    mounted() {
        this.cargarSensoresGlobales();
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
        async cargarSensoresGlobales() {
            this.loading = true;
            this.error = null;
            const token = localStorage.getItem('accessToken');
            
            if (!token) { this.$router.push('/'); return; }

            try {
                const response = await fetch(`${API_BASE_URL}/api/sensores/todos`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || 'Fallo al obtener la lista global de sensores.');
                }
                
                // Mapeo (la API ya envía los datos procesados por la consulta)
                this.sensores = data;

            } catch (err) {
                this.error = err.message || 'Error al cargar los sensores globales.';
            } finally {
                this.loading = false;
            }
        },
        
        // --- Navegación ---
        navigateToSensorDetail(sensorId) {
            // Navega a la vista de campos de este sensor
            this.$router.push(`/detalle-sensor/${sensorId}`);
        },

        // --- Lógica de Modales ---
        openEditSensorModal(sensor) {
            this.sensorSeleccionado = sensor.id;
            this.mostrarModalEditarSensor = true;
        },
        closeEditSensorModal() {
            this.mostrarModalEditarSensor = false;
            this.sensorSeleccionado = null;
        },
        handleSensorUpdated() {
            this.closeEditSensorModal();
            this.cargarSensoresGlobales(); // Recargar todo
        },
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

                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.message || data.detail || 'Fallo al eliminar el sensor.');
                }
                
                alert('Sensor eliminado exitosamente.');
                this.cancelarEliminacionSensor();
                this.cargarSensoresGlobales(); // Recargar la vista

            } catch (err) {
                alert('Error al eliminar: ' + err.message);
                this.cancelarEliminacionSensor();
            }
        },

        // --- Lógica de Layout ---
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
// VARIABLES
// ----------------------------------------
// $WIDTH-SIDEBAR: 280px; 
// $WIDTH-CLOSED: 80px; 
// $WHITE-SOFT: #F7F9FC; 
// $DARK-BG-CONTRAST: #1E1E30; 
// $LIGHT-TEXT: #E4E6EB;
// $DARK-TEXT: #333333;
// $SUBTLE-BG-DARK: #2B2B40; 
// $PRIMARY-PURPLE: #8A2BE2;
// $SUCCESS-COLOR: #1ABC9C;
// $ERROR-COLOR: #E74C3C;
// $GRAY-COLD: #99A2AD;
// $BLUE-MIDNIGHT: #1A1A2E; 
// $SUBTLE-BG-LIGHT: #FFFFFF;

// // ----------------------------------------
// // LAYOUT
// // ----------------------------------------
// .plataforma-layout {
//     display: flex;
//     min-height: 100vh;
//     transition: background-color 0.3s;
// }
// .plataforma-contenido {
//     margin-left: $WIDTH-CLOSED;
//     flex-grow: 1;
//     padding: 0; 
//     transition: margin-left 0.3s ease-in-out;
//     &.shifted { margin-left: $WIDTH-SIDEBAR; }
// }
.sensores-general-contenido {
    padding: 20px 40px 40px 40px; 
}

// ----------------------------------------
// ESTILOS DE AGRUPACIÓN (NUEVO)
// ----------------------------------------
.proyecto-seccion {
    margin-bottom: 35px;
    .proyecto-titulo {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 10px;
        padding-bottom: 5px;
        border-bottom: 2px solid $PRIMARY-PURPLE;
        display: inline-block;
    }
}

.dispositivo-subseccion {
    margin-bottom: 20px;
    padding-left: 15px;
    .dispositivo-titulo {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 15px;
        color: $GRAY-COLD;
        i {
            font-size: 1.1rem;
            margin-right: 8px;
        }
    }
}

// ----------------------------------------
// ESTILOS DE LISTA INTERACTIVA (Reutilizado)
// ----------------------------------------
.lista-sensores-container {
    background-color: $SUBTLE-BG-LIGHT;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    overflow: hidden;
    border: 1px solid #eee;
}

// Definición de las columnas (Grid)
.lista-header, .lista-fila {
    display: grid;
    // 5 columnas: Sensor, Tipo, Campos, Estado, Acciones
    grid-template-columns: 1.5fr 1fr 0.5fr 0.5fr 0.5fr; 
    align-items: center;
    padding: 12px 20px;
    gap: 15px;
}

.lista-header {
    background-color: $BLUE-MIDNIGHT; 
    color: $GRAY-COLD;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
}

.lista-fila {
    font-size: 0.95rem;
    border-bottom: 1px solid #eee; 
    transition: background-color 0.2s ease-out;

    .col-acciones {
        justify-self: end;
        opacity: 0;
        transition: opacity 0.2s ease-out;
    }
    &:hover {
        .col-acciones { opacity: 1; }
    }
}
.lista-body .lista-fila:last-child {
    border-bottom: none;
}

// --- Columnas ---
.col-sensor { font-weight: 600; }
.col-tipo { font-style: italic; color: $GRAY-COLD; }
.col-campos { font-weight: 700; text-align: center; }

.status-badge {
    font-size: 0.75rem;
    padding: 3px 8px;
    border-radius: 4px;
    font-weight: 600;
    &.active { background-color: rgba($SUCCESS-COLOR, 0.2); color: $SUCCESS-COLOR; }
    &.inactive { background-color: rgba($ERROR-COLOR, 0.2); color: $ERROR-COLOR; }
}
.btn-action {
    background: none; border: none;
    color: $GRAY-COLD;
    font-size: 1rem;
    margin-left: 10px;
    &:hover { color: $PRIMARY-PURPLE; }
}


// ----------------------------------------
// TEMAS
// ----------------------------------------
.theme-light {
    background-color: $WHITE-SOFT; 
    color: $DARK-TEXT; 
}
.theme-dark {
    background-color: $DARK-BG-CONTRAST; 
    color: $LIGHT-TEXT;
    
    .plataforma-contenido { background-color: $DARK-BG-CONTRAST; }
    .proyecto-titulo { border-bottom-color: $PRIMARY-PURPLE; }
    .dispositivo-titulo { color: $GRAY-COLD; }

    .lista-sensores-container {
        background-color: $SUBTLE-BG-DARK;
        border-color: rgba($LIGHT-TEXT, 0.1);
    }
    .lista-fila {
        border-bottom-color: rgba($LIGHT-TEXT, 0.1);
        color: $LIGHT-TEXT;
        &:hover { background-color: rgba($LIGHT-TEXT, 0.05); }
    }
    .col-tipo { color: $GRAY-COLD; }
    .btn-action { color: $GRAY-COLD; }
}
</style>