<template>
  <div class="plataforma-layout" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    <BarraLateralPlataforma :is-open="isSidebarOpen" />
    <div class="plataforma-contenido" :class="{ 'shifted': isSidebarOpen }">
      
      <EncabezadoPlataforma 
        :titulo="proyecto.nombre || 'Cargando...'"
        :subtitulo="proyecto.descripcion || 'Monitoreo IoT'"
        @toggle-sidebar="toggleSidebar" :is-sidebar-open="isSidebarOpen"
      >
        <template #title-prefix>
            <button @click="goBack" class="btn-back"><i class="bi bi-arrow-left-circle-fill"></i></button>
        </template>
      </EncabezadoPlataforma>

      <div class="proyecto-detalle-contenido">
        
        <div class="summary-cards-container">
                        <TarjetaResumen 
                            v-for="card in summaryCards" 
                            :key="card.title" 
                            :card="card"
                            :is-dark="isDark"
                        />
                    </div>
                    
        <div class="dispositivos-header">
            <h2>Dispositivos del Proyecto ({{ totalRecords }})</h2>
            
            <div class="actions-group">
                <div class="search-box">
                    <i class="bi bi-search"></i>
                    <input 
                        type="text" 
                        v-model="searchQuery" 
                        @input="onSearchInput" 
                        placeholder="Buscar dispositivo..." 
                        class="form-control-search"
                    >
                </div>

                <button 
                    v-if="miRol === 'Propietario' || miRol === 'Colaborador'"
                    @click="openAddDeviceModal" 
                    class="btn-add-device"
                > 
                    <i class="bi bi-plus-circle-fill"></i> Nuevo Dispositivo
                </button>
            </div>
        </div>

        <div v-if="loading" class="alert-info">Cargando dispositivos...</div>
        <div v-else-if="dispositivos.length === 0" class="alert-empty-data">No se encontraron dispositivos.</div>
        
        <div v-else class="dispositivos-grid">
            <TarjetaDispositivo 
                v-for="dispositivo in dispositivos"
                :key="dispositivo.id" 
                :dispositivo="dispositivo"
                :is-dark="isDark"
                :mi-rol="miRol" 
                @edit-device="openEditDeviceModal"
                @open-delete-modal="openDeleteDeviceModal"
            />
        </div>

        <div class="pagination-controls" v-if="totalPages > 1">
            <button class="btn-page" :disabled="page === 1" @click="changePage(page - 1)">
                <i class="bi bi-chevron-left"></i>
            </button>
            <span class="page-info">Pág {{ page }} de {{ totalPages }}</span>
            <button class="btn-page" :disabled="page === totalPages" @click="changePage(page + 1)">
                <i class="bi bi-chevron-right"></i>
            </button>
        
                    
                </div>
            </div>
        </div>
        
        <ModalCrearDispositivo 
            v-if="mostrarModalCrearDispositivo"
            :proyecto-id="proyectoId"
            @dispositivo-creado="handleDeviceCreated"
            @close="closeAddDeviceModal"
        />

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
          :proyecto-id="proyectoId"
          @cancelar="closeDeleteDeviceModal"
          @confirmar="eliminarDispositivo(dispositivoEliminarId, proyectoId)"
      />
        </div>
</template>

<script>
// Importa tus componentes de Layout
import BarraLateralPlataforma from '../plataforma/BarraLateralPlataforma.vue';
import EncabezadoPlataforma from '../plataforma/EncabezadoPlataforma.vue';

// Componentes de la vista actual
import TarjetaResumen from './TarjetaResumen.vue';
import TarjetaDispositivo from './TarjetaDispositivo.vue';
import ModalCrearDispositivo from '../dispositivos/ModalCrearDispositivo.vue'; 
import ModalEditarDispositivo from '../dispositivos/ModalEditarDispositivo.vue'; 
import ModalEliminarDispositivo from '../dispositivos/ModalEliminarDispositivo.vue'; 
import debounce from 'lodash/debounce'; // npm install lodash
// const API_BASE_URL = 'http://127.0.0.1:8001';

export default {
    name: 'DetalleProyecto',
    components: {
        BarraLateralPlataforma,
        EncabezadoPlataforma,
        TarjetaResumen,
        TarjetaDispositivo,
        ModalCrearDispositivo,
        ModalEditarDispositivo, 
        ModalEliminarDispositivo,
    },
    data() {
        return {
            isDark: false,
            isSidebarOpen: true,
            loading: true,
            error: null,
            proyecto: {},
            miRol: '',
            dispositivos: [],
            // Estados de Modales
            mostrarModalCrearDispositivo: false,
            mostrarModalEditarDispositivo: false, 
            dispositivoSeleccionado: null,

            mostrarModalEliminarDispositivo: false,
            dispositivoEliminarId: null,
            dispositivoEliminarNombre: null,
            

            searchQuery: '',
            page: 1,
            limit: 6, // 6 tarjetas se ven bien
            totalPages: 1,
            totalRecords: 0,
            loading: true,
            resumenMetricas: {},
        };
    },
    computed: {
        proyectoId() { return this.$route.params.id; },
        summaryCards() {
            // Lógica de tarjetas
            const dispositivos = this.dispositivos || [];
            const activos = dispositivos.filter(d => d.habilitado).length;
            const total = dispositivos.length;
            // const resumen = this.resumenMetricas;
            return [
                { title: 'Total Dispositivos', value: total, icon: 'bi bi-tablet-fill', color: '#1ABC9C' },
                { title: 'Dispositivos Activos', value: activos, icon: 'bi bi-wifi', color: '#8A2BE2' },
                { title: 'Batería Promedio', value: 'N/A', icon: 'bi bi-battery-half', color: '#FFC107', isPlaceholder: true },
                { title: 'Última Actividad', value: 'Hace 2 min', icon: 'bi bi-activity', color: '#FF5733', isPlaceholder: true },
                // { title: 'Total Dispositivos', value: resumen.total_dispositivos || 0, icon: 'bi bi-tablet-fill', color: '#1ABC9C' },
                // { title: 'Sensores Conectados', value: resumen.total_sensores || 0, icon: 'bi bi-broadcast-pin', color: '#8A2BE2' },
                // // 🚨 Última Conexión basada en la DB
                // { title: 'Última Conexión', value: this.formatRelativeTime(resumen.ultima_conexion), icon: 'bi bi-clock-history', color: '#FFC107' },
                // // 🚨 Campos Activos
                // { title: 'Campos de Medición', value: resumen.campos_activos || 0, icon: 'bi bi-speedometer', color: '#FF5733' },
            ];
        }
    },created() {
        // Debounce para la búsqueda
        this.debouncedSearch = debounce(() => {
            this.page = 1;
            this.cargarDispositivos();
        }, 500);
    },
    mounted() {
        this.cargarDatosIniciales();
        this.cargarDetallesProyecto();
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
        // LÓGICA DE CARGA Y RECARGA
        // -----------------------------------------------------
         async cargarDatosIniciales() {
            await this.cargarProyecto();
            await this.cargarDispositivos();
        },

        async cargarProyecto() {
            const token = localStorage.getItem('accessToken');
            if (!token) return;
            try {
                const response = await fetch(`${API_BASE_URL}/api/proyectos/${this.$route.params.id}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    this.proyecto = data;
                    this.miRol = data.mi_rol; // Guardamos el rol
                }
            } catch (e) { console.error(e); }
        },

        // 2. Cargar Dispositivos (Paginados)
        async cargarDispositivos() {
            this.loading = true;
            const token = localStorage.getItem('accessToken');
            
            // Construir URL con params
            const params = new URLSearchParams({
                page: this.page,
                limit: this.limit,
                search: this.searchQuery
            });
            
            try {
                const response = await fetch(`${API_BASE_URL}/api/dispositivos/proyecto/${this.$route.params.id}?${params}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    // La API ahora devuelve { data, total, total_pages }
                    this.dispositivos = data.data.map(d => ({
                        ...d,
                        habilitado: d.habilitado === 1 || d.habilitado === true,
                        // ... (otros mapeos) ...
                    }));
                    this.totalRecords = data.total;
                    this.totalPages = data.total_pages;
                } else {
                    this.dispositivos = [];
                }
            } catch (e) {
                console.error(e);
            } finally {
                this.loading = false;
            }
        },
        
        onSearchInput() { this.debouncedSearch(); },
        
        changePage(newPage) {
            if (newPage >= 1 && newPage <= this.totalPages) {
                this.page = newPage;
                this.cargarDispositivos();
            }
        },
        async cargarDetallesProyecto() {
            this.loading = true;
            this.error = null;
            const token = localStorage.getItem('accessToken');
            
            if (!token || !this.proyectoId) { this.$router.push('/'); return; }

            try {
                // 1. Obtener detalles del proyecto
                const projResponse = await fetch(`${API_BASE_URL}/api/proyectos/${this.proyectoId}`, { headers: { 'Authorization': `Bearer ${token}` } });
                if (!projResponse.ok) { throw new Error('No se encontró el proyecto.'); }
                this.proyecto = await projResponse.json();
                
                // 2. Obtener lista de dispositivos
                const devResponse = await fetch(`${API_BASE_URL}/api/dispositivos/proyecto/${this.proyectoId}`, { headers: { 'Authorization': `Bearer ${token}` } });
                const devData = await devResponse.json();

                if (devResponse.status !== 200 && devResponse.status !== 404) { 
                     throw new Error('Fallo al obtener dispositivos.');
                } else if (devResponse.ok) {
                    //comprobar como llegan los datos
                    console.log('Dispositivos cargados:', devData);

                    
                    this.dispositivos = devData.map(d => ({
                        ...d,
                        habilitado: d.habilitado === 1 || d.habilitado === true, 
                        estado_texto: (d.habilitado === 1 || d.habilitado === true) ? 'Habilitado' : 'Deshabilitado',
                        ultima_lectura: '23.1°C / 78%',
                        porcentaje_carga: Math.floor(Math.random() * 100),
                    }));
                    console.log('Dispositivos procesados:', this.dispositivos);
                } else {
                    this.dispositivos = [];
                }
                //  const idsDispositivos = this.dispositivos.map(dispositivo => dispositivo.id);
                // // idsDispositivos ahora será un array de números, por ejemplo: [1, 2]

                // console.log('IDs de dispositivos para resumen:', idsDispositivos); // Mostrará [1, 2]

                // // 3. Verificar si hay IDs antes de hacer la llamada
                // if (idsDispositivos.length > 0) {
                //     const primerId = idsDispositivos[0]; // Obtener el primer ID del array (ej: 1)
                    
                //     // 4. Usar el primer ID en la llamada a la API
                //     const token = localStorage.getItem('accessToken');
                //     const resumenResponse = await fetch(`${API_BASE_URL}/api/dispositivos/${primerId}/resumen`, { 
                //         headers: { 'Authorization': `Bearer ${token}` } 
                //     });
                    
                //     // ... procesar resumenResponse ...
                    
                // } else {
                //     console.log('No hay IDs de dispositivos para obtener resumen.');
                //     // Manejar el caso donde no hay dispositivos
                // }

            } catch (err) {
                this.error = err.message || 'Error al cargar los detalles del proyecto.';
            } finally {
                this.loading = false;
            }
        },
        
        // -----------------------------------------------------
        // MANEJO DE EVENTOS DE DISPOSITIVOS
        // -----------------------------------------------------
        
        // Creación
        openAddDeviceModal() { this.mostrarModalCrearDispositivo = true; },
        closeAddDeviceModal() { this.mostrarModalCrearDispositivo = false; },
        handleDeviceCreated() {
            this.closeAddDeviceModal();
            this.cargarDatosIniciales(); 
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
            this.cargarDatosIniciales();
        },

        // Toggle Habilitado (Simulación)
        handleToggleHabilitado(dispositivoId, nuevoEstado) {
            console.log(`Simulando cambio de estado para ID ${dispositivoId} a ${nuevoEstado}`);
            this.cargarDatosIniciales(); 
        },
        
        // 🚨 FUNCIÓN LLAMADA POR EL BOTÓN DE LA PAPELERA (TarjetaDispositivo)
        openDeleteDeviceModal(dispositivoId, nombre) {
            this.dispositivoEliminarId = dispositivoId;
            this.dispositivoEliminarNombre = nombre;
            this.mostrarModalEliminarDispositivo = true;
        },
        
        closeDeleteDeviceModal() {
            this.mostrarModalEliminarDispositivo = false;
            this.dispositivoEliminarId = null;
            this.dispositivoEliminarNombre = null;
        },
        
        // 🚨 CRÍTICO: FUNCIÓN DE ELIMINACIÓN SEGURA CON JWT
        // DetalleProyecto.vue (dentro de methods)

        async eliminarDispositivo(dispositivoId, proyectoId) {
            this.loading = true; 
            const token = localStorage.getItem('accessToken');
            
            // 🚨 CRÍTICO: Obtenemos el ID del dueño del proyecto (usado para la validación de propiedad en el backend)
            const usuarioId = this.proyecto.usuario_id; 

            // 🚨 CONSTRUCCIÓN DE LA URL CORREGIDA: Usa el prefijo /api y las variables dinámicas
            const url = `${API_BASE_URL}/api/dispositivos/?id=${dispositivoId}&proyecto_id=${proyectoId}&usuario_id=${usuarioId}`; 

            if (!token || !usuarioId) {
                alert("Error: Sesión no válida o faltan datos de usuario.");
                this.closeDeleteDeviceModal();
                return;
            }

            try {
                const response = await fetch(url, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` },
                });

                const data = await response.json();

                // Manejo de errores de la API (403, 500)
                if (!response.ok || data.status === 'error') {
                    if (response.status === 403) {
                        throw new Error(data.detail || "No tiene permisos para eliminar este dispositivo.");
                    }
                    throw new Error(data.message || 'Fallo al eliminar el dispositivo.');
                }

                // 4. ÉXITO
                alert(data.message || 'Dispositivo eliminado exitosamente.');
                this.closeDeleteDeviceModal();
                
                // Recargar la lista para que la tarjeta desaparezca
                this.cargarDatosIniciales(); 

            } catch (err) {
                alert('Error al eliminar: ' + err.message);
                this.closeDeleteDeviceModal();
            } finally {
                this.loading = false;
            }
        },

        // -----------------------------------------------------
        // LÓGICA DE LAYOUT Y NAVEGACIÓN
        // -----------------------------------------------------
        goBack() { this.$router.push('/mis-proyectos'); },
        toggleSidebar() { this.isSidebarOpen = !this.isSidebarOpen; },
        handleThemeChange(event) { this.isDark = event.matches; },
        detectarTemaSistema() {
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                this.isDark = true;
            } else {
                this.isDark = false;
            }
        },
        // 🚨 CRÍTICO: Función de formateo de tiempo (simulada)
    formatRelativeTime(isoString) {
        if (!isoString) return 'N/A';
        // En una app real, usarías librerías como Moment.js o Day.js
        // Por ahora:
        return 'Hace X minutos';
    }
        
    }
};
</script>


<style scoped lang="scss">
// ----------------------------------------
// VARIABLES DE LA PALETA "IoT SPECTRUM"
// ----------------------------------------
// $WIDTH-SIDEBAR: 280px; 
// $WIDTH-CLOSED: 80px; 
// $WHITE-SOFT: #F7F9FC; 
// $BLUE-MIDNIGHT: #1A1A2E;
// $DARK-BG-CONTRAST: #1E1E30; // Fondo general oscuro
// $DARK-TEXT: #333333;
// $LIGHT-TEXT: #E4E6EB;
// $PRIMARY-PURPLE: #8A2BE2;
// $SUCCESS-COLOR: #1ABC9C;
// $MAINTENANCE-COLOR: #FFC107; // Amarillo
// $GRAY-COLD: #99A2AD;
// $SUBTLE-BG-LIGHT: #FFFFFF; // <-- DEBE ESTAR AQUÍ


// ----------------------------------------
// LAYOUT PRINCIPAL Y CONTENIDO
// ----------------------------------------
// .plataforma-layout {
//     display: flex;
//     min-height: 100vh;
//     transition: background-color 0.3s;
// }

// .plataforma-contenido {
//     position: relative; /* Necesario para que el contenido de los hijos se posicione */
//     margin-left: $WIDTH-CLOSED;
//     flex-grow: 1;
//     padding: 0; 
//     transition: margin-left 0.3s ease-in-out;
    
//     &.shifted {
//         margin-left: $WIDTH-SIDEBAR;
//     }
// }

.proyecto-detalle-contenido {
    padding: 20px 40px 40px 40px; 
}

// Estilo del botón Volver
.btn-back {
    background: none;
    border: none;
    color: $DARK-TEXT; /* Color en modo claro */
    font-size: 1.4rem;
    margin-right: 15px;
    cursor: pointer;
    transition: color 0.2s;
    
    &:hover {
        color: $PRIMARY-PURPLE;
    }
}


// ------------------------------------
// SECCIÓN 1: TARJETAS DE RESUMEN (Componente TarjetaResumen.vue)
// ------------------------------------
.summary-cards-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 40px;
}

.summary-card {
    padding: 20px;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    
    .icon-box {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        justify-content: center;
        align-items: center;
        color: white;
        font-size: 1.2rem;
        float: right; /* Alinea a la derecha para el diseño */
        margin-left: 10px;
    }
    .value {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0;
        clear: both; /* Limpia el float del icono */
    }
    .title {
        font-size: 0.9rem;
        color: $GRAY-COLD;
        margin-top: 5px;
    }
}

// ------------------------------------
// SECCIÓN 2: HEADER DE DISPOSITIVOS
// ------------------------------------
.dispositivos-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    
    h2 {
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    .actions-group {
        display: flex;
        gap: 15px;
    }
}
.form-control-search {
    padding: 8px 12px;
    border-radius: 8px;
    border: 1px solid #ccc;
    // Estilos adaptados en el tema
}
.btn-add-device {
    background-color: $SUCCESS-COLOR;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 3px 6px rgba($SUCCESS-COLOR, 0.3);
    i { margin-right: 5px; }
}
.actions-group {
    display: flex; gap: 10px; align-items: center;
    
    .search-box {
        position: relative;
        input {
            padding: 8px 10px 8px 35px; border-radius: 20px; border: 1px solid #ddd;
            font-size: 0.9rem; width: 200px; transition: width 0.3s;
            &:focus { width: 250px; border-color: #8A2BE2; }
        }
        i { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #999; }
    }
}
.pagination-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    margin-top: 40px;
    padding-bottom: 20px;
    
    .btn-page {
        background-color: transparent;
        border: 1px solid #8A2BE2;
        color: #8A2BE2;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 5px;
        
        &:hover:not(:disabled) {
            background-color: #8A2BE2;
            color: white;
        }
        &:disabled {
            border-color: #ccc;
            color: #ccc;
            cursor: not-allowed;
        }
    }
    
    .page-info {
        font-weight: 500;
        color: #99A2AD;
    }
}
// ------------------------------------
// SECCIÓN 3: GRID DE DISPOSITIVOS
// ------------------------------------
.dispositivos-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
}

// ------------------------------------
// ESTILOS DE TEMA (MODO CLARO/OSCURO)
// ------------------------------------

// MODO CLARO (Default)
.theme-light {
    background-color: $WHITE-SOFT;
    color: $DARK-TEXT;
    
    .btn-back { color: $DARK-TEXT; }
    
    .summary-card {
        background-color: $SUBTLE-BG-LIGHT;
    }
    .form-control-search {
        background-color: $SUBTLE-BG-LIGHT;
        border-color: #ddd;
        color: $DARK-TEXT;
    }
}

// MODO OSCURO
.theme-dark {
    background-color: $DARK-BG-CONTRAST; 
    color: $LIGHT-TEXT;
    
    .btn-back { color: $LIGHT-TEXT; }
    .dispositivos-header h2 { color: $LIGHT-TEXT; }
    
    .summary-card {
        background-color: $BLUE-MIDNIGHT;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
    }
    .summary-card .title {
        color: $GRAY-COLD;
    }
    
    .form-control-search {
        background-color: $BLUE-MIDNIGHT;
        border-color: rgba($LIGHT-TEXT, 0.2);
        color: $LIGHT-TEXT;
    }
}
</style>