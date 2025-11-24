<template>
  <div class="plataforma-layout" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    
    <BarraLateralPlataforma :is-open="isSidebarOpen" />
    
    <div class="plataforma-contenido" :class="{ 'shifted': isSidebarOpen }">
      
      <EncabezadoPlataforma 
        titulo="Dispositivos Generales"
        subtitulo="Vista global de la infraestructura IoT"
        @toggle-sidebar="toggleSidebar" 
        :is-sidebar-open="isSidebarOpen"
      />

      <div class="dispositivos-general-contenido">
        
        <div class="controls-header">
            <div class="total-info">
                <span class="count-badge">{{ totalRecords }}</span> Dispositivos encontrados
            </div>
            
            <div class="search-box">
                <i class="bi bi-search search-icon"></i>
                <input 
                    type="text" 
                    v-model="searchQuery" 
                    @input="onSearchInput" 
                    placeholder="Buscar por nombre o tipo..." 
                    class="search-input"
                >
            </div>
        </div>

        <div v-if="loading" class="alert-info">
            <i class="bi bi-arrow-clockwise fa-spin"></i> Cargando dispositivos...
        </div>
        <div v-else-if="error" class="alert-error">{{ error }}</div>
        
        <div v-else-if="dispositivos.length === 0" class="alert-empty">
            <i class="bi bi-box-fill"></i> No se encontraron dispositivos.
        </div>
        
        <div v-else>
          <div v-for="(dispositivos_lista, nombre_proyecto) in dispositivosAgrupados" :key="nombre_proyecto" class="proyecto-seccion">
            
            <div class="seccion-header">
                <h3>
                    <i class="bi bi-folder-fill me-2"></i> {{ nombre_proyecto }} 
                    <span class="count-tag">{{ dispositivos_lista.length }}</span>
                </h3>
                <span class="propietario-tag" v-if="dispositivos_lista[0]">
                    ID Propietario: {{ dispositivos_lista[0].propietario_id }}
                </span>
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

        <div class="pagination-controls" v-if="totalPages > 1 && !loading">
            <button 
                class="btn-page" 
                :disabled="page === 1" 
                @click="changePage(page - 1)"
            >
                <i class="bi bi-chevron-left"></i> Anterior
            </button>
            
            <span class="page-info">Página {{ page }} de {{ totalPages }}</span>
            
            <button 
                class="btn-page" 
                :disabled="page === totalPages" 
                @click="changePage(page + 1)"
            >
                Siguiente <i class="bi bi-chevron-right"></i>
            </button>
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
import debounce from 'lodash/debounce'; // 🚨 Asegúrate de tener lodash instalado
// const API_BASE_URL = 'http://127.0.0.1:8001';

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
            isSidebarOpen: true,
            loading: true,
            error: null,
            dispositivos: [],
            
            // 🚨 Estados de Paginación y Búsqueda
            searchQuery: '',
            page: 1,
            limit: 8, // Mostrar 12 por página
            totalPages: 1,
            totalRecords: 0,

            // Estados de Modales
            mostrarModalEditarDispositivo: false, 
            dispositivoSeleccionado: null,
            mostrarModalEliminarDispositivo: false,
            dispositivoEliminarId: null,
            dispositivoEliminarNombre: null,
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
    created() {
        // Crear la función debounced
        this.debouncedSearch = debounce(() => {
            this.page = 1;
            this.cargarDispositivosGlobales();
        }, 500);
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
// Evento de Input
        onSearchInput() {
            this.debouncedSearch();
        },

        // Cambio de Página
        changePage(newPage) {
            if (newPage >= 1 && newPage <= this.totalPages) {
                this.page = newPage;
                this.cargarDispositivosGlobales();
                // Scroll suave al inicio de la lista
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        },


        // -----------------------------------------------------
        // CONSUMO DE API: Cargar Dispositivos Globales
        // -----------------------------------------------------
        async cargarDispositivosGlobales() {
            this.loading = true;
            this.error = null;
            const token = localStorage.getItem('accessToken');
            
            if (!token) { this.$router.push('/'); return; }

            // 🚨 Construcción de URL con parámetros
            const params = new URLSearchParams({
                page: this.page,
                limit: this.limit,
                search: this.searchQuery
            });

            try {
                const response = await fetch(`${API_BASE_URL}/api/dispositivos/todos?${params}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                if (!response.ok) { 
                    const err = await response.json();
                    throw new Error(err.detail || 'Fallo al obtener dispositivos.'); 
                }
                
                // 🚨 Manejo de respuesta paginada { data, total, total_pages }
                const respuesta = await response.json();
                
                const devData = respuesta.data || [];
                this.totalRecords = respuesta.total || 0;
                this.totalPages = respuesta.total_pages || 1;

                // Mapeo de datos
                this.dispositivos = devData.map(d => ({
                    ...d,
                    habilitado: d.habilitado === 1 || d.habilitado === true, 
                    estado_texto: (d.habilitado === 1 || d.habilitado === true) ? 'Habilitado' : 'Deshabilitado',
                    // Datos visuales simulados o formateados
                    ultima_lectura: 'Reciente', 
                    porcentaje_carga: Math.floor(Math.random() * 100),
                }));

            } catch (err) {
                this.error = err.message;
                this.dispositivos = [];
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
            const proyectoId = this.dispositivoEliminarProyectoId; 
            const usuarioId = this.dispositivoEliminarPropietarioId; 
            const url = `${API_BASE_URL}/api/dispositivos/?id=${dispositivoId}&proyecto_id=${proyectoId}`;

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
.controls-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    flex-wrap: wrap;
    gap: 15px;
    
    .total-info {
        font-size: 1.1rem;
        font-weight: 500;
        color: $GRAY-COLD;
        .count-badge {
            background-color: $PRIMARY-PURPLE;
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-weight: 700;
            margin-right: 5px;
        }
    }

    .search-box {
        position: relative;
        .search-input {
            padding: 10px 15px 10px 40px;
            border-radius: 20px;
            border: 1px solid #ddd;
            width: 250px;
            font-size: 0.95rem;
            transition: all 0.3s;
            outline: none;
            
            &:focus {
                border-color: $PRIMARY-PURPLE;
                width: 300px;
                box-shadow: 0 0 0 3px rgba($PRIMARY-PURPLE, 0.1);
            }
        }
        .search-icon {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: $GRAY-COLD;
        }
    }
}

// SECCIÓN DE PROYECTO
.proyecto-seccion {
    margin-bottom: 40px;
    
    .seccion-header {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(150,150,150, 0.2);
        
        h3 {
            font-size: 1.3rem;
            font-weight: 600;
            margin: 0;
            display: flex;
            align-items: center;
            color: $PRIMARY-PURPLE;
            
            .count-tag {
                font-size: 0.8rem;
                background-color: rgba($PRIMARY-PURPLE, 0.1);
                padding: 2px 8px;
                border-radius: 6px;
                margin-left: 10px;
            }
        }
        
        .propietario-tag {
            margin-left: auto;
            font-size: 0.8rem;
            color: $GRAY-COLD;
            background: rgba(150,150,150, 0.1);
            padding: 4px 10px;
            border-radius: 20px;
        }
    }
}

.dispositivos-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 25px;
}

// 🚨 PAGINACIÓN
.pagination-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    margin-top: 50px;
    
    .btn-page {
        background: none;
        border: 1px solid $PRIMARY-PURPLE;
        color: $PRIMARY-PURPLE;
        padding: 8px 20px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.2s;
        display: flex; gap: 5px;
        
        &:hover:not(:disabled) {
            background-color: $PRIMARY-PURPLE;
            color: white;
        }
        &:disabled {
            border-color: $GRAY-COLD;
            color: $GRAY-COLD;
            cursor: not-allowed;
            opacity: 0.5;
        }
    }
    .page-info { font-weight: 600; color: $GRAY-COLD; }
}
// ----------------------------------------
// TEMAS (Para hacer visible el contenido)
// ----------------------------------------
.theme-light {
    background-color: $WHITE-SOFT;
    .seccion-header { color: $DARK-TEXT; border-bottom-color: #ddd; }
    .search-input {
        background-color: $SUBTLE-BG-LIGHT;
        border-color: #ddd;
        color: $DARK-TEXT;
    }
    .alert-info, .alert-empty { color: $GRAY-COLD; text-align: center; margin-top: 30px;}
}

.theme-dark {
    background-color: $DARK-BG-CONTRAST; 
    color: $LIGHT-TEXT;
    
    .seccion-header { color: $LIGHT-TEXT; border-bottom-color: rgba($LIGHT-TEXT, 0.1); }
    .propietario-tag { color: $GRAY-COLD; }
    .search-input {
        background-color: $BLUE-MIDNIGHT;
        border-color: rgba(255,255,255,0.1);
        color: $LIGHT-TEXT;
    }
    .alert-info, .alert-empty { color: $LIGHT-TEXT; text-align: center; margin-top: 30px;}
}
</style>