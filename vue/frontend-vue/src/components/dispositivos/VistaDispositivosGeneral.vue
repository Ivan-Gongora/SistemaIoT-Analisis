<template>
  <div class="plataforma-layout" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    
    <BarraLateralPlataforma :is-open="isSidebarOpen" />
    
    <div class="plataforma-contenido" :class="{ 'shifted': isSidebarOpen }">
      
      <EncabezadoPlataforma 
        titulo="Dispositivos Generales"
        subtitulo="Vista de todos los dispositivos activos en la plataforma"
        @toggle-sidebar="toggleSidebar" 
        :is-sidebar-open="isSidebarOpen"
      />

      <div class="dispositivos-general-contenido">
        
        <div v-if="loading" class="alert-info">Cargando todos los dispositivos...</div>
        <div v-else-if="error" class="alert-error">{{ error }}</div>
        <div v-else-if="Object.keys(dispositivosAgrupados).length === 0" class="alert-empty">
          <i class="bi bi-box-fill"></i> No se encontraron dispositivos.
        </div>
        
        <div v-else>
          <div v-for="(dispositivos_lista, nombre_proyecto) in dispositivosAgrupados" :key="nombre_proyecto" class="proyecto-seccion">
            
            <div class="seccion-header">
                <h3><i class="bi bi-folder-fill me-2"></i> {{ nombre_proyecto }} ({{ dispositivos_lista.length }})</h3>
                <span class="propietario-tag">Propietario: {{ dispositivos_lista[0].propietario_id || 'N/A' }}</span>
            </div>

            <div class="dispositivos-grid">
              <TarjetaDispositivo 
                v-for="dispositivo in dispositivos_lista"
                :key="dispositivo.id"
                :dispositivo="dispositivo"
                :is-dark="isDark"
                @open-delete-modal="openDeleteDeviceModal"

                @edit-device="openEditDeviceModal"
                
              />
            </div>

          </div>
        </div>
      </div>
    </div>
        <ModalEditarDispositivo 
            v-if="mostrarModalEditarDispositivo"
            :dispositivo-actual="dispositivoSeleccionado"
            @dispositivo-actualizado="handleDeviceUpdated"
            @close="closeEditDeviceModal"
        />
        <ModalEliminarDispositivo 
          v-if="mostrarModalEliminarDispositivo"
    :dispositivo-id="dispositivoEliminarId"
    :dispositivo-nombre="dispositivoEliminarNombre"
    :proyecto-id="dispositivoEliminarProyectoId" 
    @cancelar="closeDeleteDeviceModal"
    @confirmar="eliminarDispositivo(dispositivoEliminarId)" 
      />
  </div>
</template>

<script>
import BarraLateralPlataforma from '../plataforma/BarraLateralPlataforma.vue';
import EncabezadoPlataforma from '../plataforma/EncabezadoPlataforma.vue';
import TarjetaDispositivo from '../proyecto/TarjetaDispositivo.vue'; // 🚨 Ruta corregida
import ModalEditarDispositivo from '../dispositivos/ModalEditarDispositivo.vue'; 
import ModalEliminarDispositivo from '../dispositivos/ModalEliminarDispositivo.vue'; 
const API_BASE_URL = 'http://127.0.0.1:8001';

export default {
    name: 'VistaDispositivosGeneral',
    components: {
        BarraLateralPlataforma,
        EncabezadoPlataforma,
        TarjetaDispositivo,
        ModalEditarDispositivo, 
        ModalEliminarDispositivo,
    },
    data() {
        return {
            isDark: false,
            isSidebarOpen: true,
            loading: true,
            error: null,
            dispositivos: [],
             mostrarModalEditarDispositivo: false, 
         

            mostrarModalEliminarDispositivo: false,
                // 🚨 NUEVAS VARIABLES DE ESTADO PARA LA ELIMINACIÓN
            dispositivoEliminarProyectoId: null, 
            dispositivoEliminarPropietarioId: null,
        };
    },
    computed: {
        // 🚨 Función crítica para agrupar dispositivos por proyecto
        dispositivosAgrupados() {
            return this.dispositivos.reduce((groups, dispositivo) => {
                const projectName = dispositivo.nombre_proyecto || 'Sin Proyecto';
                if (!groups[projectName]) {
                    groups[projectName] = [];
                }
                groups[projectName].push(dispositivo);
                return groups;
            }, {});
        }
    },
    mounted() {
        this.cargarDispositivosGlobales();
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
        // CONSUMO DE API: Cargar Dispositivos Globales
        // -----------------------------------------------------
        async cargarDispositivosGlobales() {
            this.loading = true;
            this.error = null;
            const token = localStorage.getItem('accessToken');
            
            if (!token) { this.$router.push('/'); return; }

            try {
                const response = await fetch(`${API_BASE_URL}/api/dispositivos/todos`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                const devData = await response.json();

                if (!response.ok) { throw new Error(devData.detail || 'Fallo al obtener la lista global de dispositivos.'); }
                
                // 🚨 Mapeo: Conversion de 0/1 a booleano y añadido de datos visuales
                this.dispositivos = devData.map(d => ({
                    ...d,
                    habilitado: d.habilitado === 1 || d.habilitado === true, 
                    estado_texto: (d.habilitado === 1 || d.habilitado === true) ? 'Habilitado' : 'Deshabilitado',
                    ultima_lectura: '23.1°C / 78%',
                    porcentaje_carga: Math.floor(Math.random() * 100),
                }));

            } catch (err) {
                this.error = err.message || 'Error al cargar los dispositivos globales.';
            } finally {
                this.loading = false;
            }
        },

        // Edición
        openEditDeviceModal(dispositivo) {
            this.dispositivoSeleccionado = dispositivo;
            this.mostrarModalEditarDispositivo = true;
        },
        closeEditDeviceModal() {
            this.mostrarModalEditarDispositivo = false;
            this.dispositivoSeleccionado = null;
        },
        handleDeviceUpdated() {
            this.closeEditDeviceModal();
            this.cargarDispositivosGlobales();
        },
        
        // VistaDispositivosGeneral.vue <script> (dentro de methods)

        openDeleteDeviceModal(dispositivoId, nombre) {
            this.dispositivoEliminarId = dispositivoId;
            this.dispositivoEliminarNombre = nombre;
            this.mostrarModalEliminarDispositivo = true;
            
            // 🚨 CRÍTICO: Encontrar el objeto completo del dispositivo en el array local
            const dispositivo = this.dispositivos.find(d => d.id === dispositivoId);
            
            if (dispositivo) {
                // Guardamos el proyectoId y Propietario ID en variables de estado
                this.dispositivoEliminarProyectoId = dispositivo.proyecto_id; 
                this.dispositivoEliminarPropietarioId = dispositivo.propietario_id;
            } else {
                // Si por alguna razón el dispositivo no está en el array local (nunca debería pasar)
                this.error = "Error interno: No se encontraron datos del dispositivo para eliminar.";
                this.mostrarModalEliminarDispositivo = false;
            }
        },

        closeDeleteDeviceModal() {
            this.mostrarModalEliminarDispositivo = false;
            this.dispositivoEliminarId = null;
            this.dispositivoEliminarNombre = null;
            
            // 🚨 LIMPIEZA ADICIONAL: Limpiar las variables de seguridad después de cerrar
            this.dispositivoEliminarProyectoId = null; 
            this.dispositivoEliminarPropietarioId = null;
        },
        // 🚨 CRÍTICO: FUNCIÓN DE ELIMINACIÓN SEGURA CON JWT
        // DetalleProyecto.vue (dentro de methods)

        // VistaDispositivosGeneral.vue (dentro de methods)
        // VistaDispositivosGeneral.vue <script> (dentro de methods)

        confirmarEliminacion(dispositivoId, nombre) {
            this.dispositivoEliminarId = dispositivoId;
            this.dispositivoEliminarNombre = nombre;
            this.mostrarModalEliminarDispositivo = true;
            
            // 🚨 CRÍTICO: Encontrar el objeto completo del dispositivo en el array local
            const dispositivo = this.dispositivos.find(d => d.id === dispositivoId);
            
            if (dispositivo) {
                // Guardamos el proyectoId y Propietario ID en variables de estado
                this.dispositivoEliminarProyectoId = dispositivo.proyecto_id; 
                this.dispositivoEliminarPropietarioId = dispositivo.propietario_id;
            } else {
                // Fallback si el dispositivo no se encuentra
                this.error = "Error interno: No se encontraron datos del dispositivo para eliminar.";
                this.mostrarModalEliminarDispositivo = false;
            }
        },
        // VistaDispositivosGeneral.vue <script> (dentro de methods)

        async eliminarDispositivo(dispositivoId) {
            this.loading = true; 
            const token = localStorage.getItem('accessToken');
            
            // Usamos las variables de estado guardadas en 'data()'
            const proyectoId = this.dispositivoEliminarProyectoId; 
            const usuarioId = this.dispositivoEliminarPropietarioId; 

            // 🚨 CONSTRUCCIÓN DE LA URL CORREGIDA Y SEGURA
            const url = `${API_BASE_URL}/api/dispositivos/?id=${dispositivoId}&proyecto_id=${proyectoId}&usuario_id=${usuarioId}`; 

            if (!token || !usuarioId || !proyectoId) {
                alert("Error: Faltan datos de seguridad (token/proyecto/dueño).");
                this.closeDeleteDeviceModal();
                this.loading = false;
                return;
            }

            try {
                const response = await fetch(url, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
                const data = await response.json();

                if (!response.ok || data.status === 'error') {
                    if (response.status === 403) {
                        throw new Error(data.detail || "No tiene permisos para eliminar este dispositivo.");
                    }
                    throw new Error(data.message || 'Fallo al eliminar el dispositivo.');
                }

                // 4. ÉXITO
                alert(data.message || 'Dispositivo eliminado exitosamente.');
                this.closeDeleteDeviceModal();
                this.cargarDispositivosGlobales(); // Recargar la lista para actualizar la vista
            } catch (err) {
                alert('Error al eliminar: ' + err.message);
                this.closeDeleteDeviceModal();
            } finally {
                this.loading = false;
            }
        },
        // -----------------------------------------------------
        // LÓGICA DEL LAYOUT (Heredada)
        // -----------------------------------------------------
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


.dispositivos-general-contenido {
    padding: 0 40px 40px 40px; 
}

// ----------------------------------------
// ESTILOS DE AGRUPACIÓN
// ----------------------------------------

.proyecto-seccion {
    margin-bottom: 30px;
    padding-bottom: 20px;
}

.seccion-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 5px;
    border-bottom: 1px solid; /* Se define el color en el tema */
    
    h3 {
        font-size: 1.6rem;
        font-weight: 600;
        i { margin-right: 10px; }
    }
    .propietario-tag {
        font-size: 0.85rem;
    }
}

.dispositivos-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
}

// ----------------------------------------
// TEMAS (Para hacer visible el contenido)
// ----------------------------------------
.theme-light {
    background-color: $WHITE-SOFT;
    .seccion-header { color: $DARK-TEXT; border-bottom-color: #ddd; }
}

.theme-dark {
    background-color: $DARK-BG-CONTRAST; 
    color: $LIGHT-TEXT;
    
    .seccion-header { color: $LIGHT-TEXT; border-bottom-color: rgba($LIGHT-TEXT, 0.1); }
    .propietario-tag { color: $GRAY-COLD; }
}
</style>