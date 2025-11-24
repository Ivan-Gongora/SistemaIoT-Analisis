<template>
  <div class="mis-proyectos">
    
   <div class="proyectos-header-view">       
        <div class="left-group">
             <span class="count-total">
                <strong>{{ totalRecords }}</strong> ecosistemas
            </span>
        </div>

        <div class="actions-group">
            
            <div class="search-box" :class="{ 'theme-dark': isDark }">
                <i class="bi bi-search search-icon"></i>
                <input 
                    type="text" 
                    v-model="searchQuery" 
                    @input="onSearchInput" 
                    placeholder="Buscar proyectos..." 
                    class="search-input"
                >
            </div>

            <button class="btn-nuevo-proyecto" @click="mostrarModalCrear = true">
                <i class="bi bi-plus-lg icon-space"></i> Nuevo Proyecto
            </button>
            
        </div>
    </div>

    <div v-if="error" class="alerta-error">{{ error }}</div>
    
    <div v-else-if="loading" class="alerta-loading">
        <i class="bi bi-arrow-clockwise fa-spin"></i> Cargando proyectos...
    </div>
    
    <div v-else-if="proyectos.length > 0" class="proyectos-grid">
        <TarjetaProyecto 
            v-for="proyecto in proyectos" 
            :key="proyecto.id" 
            :proyecto="proyecto" 
            :is-dark="isDark"
            @toggle-activo="simularCambioEstado"
            @open-share-modal="openShareModal" 
            @edit-project="handleEditClick" 
            @confirmar-eliminar="confirmarEliminacion"
        />
    </div>
    
    <div v-else class="alerta-vacio">
        <i class="bi bi-box-fill"></i> No se encontraron proyectos que coincidan con la búsqueda.
    </div>

    <div class="pagination-controls" v-if="totalPages > 1">
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

    <ModalEliminarProyecto v-if="mostrarModalEliminar" @cancelar="cerrarModalEliminar" @confirmar="eliminar(proyectoEliminarId)" :proyecto-id="proyectoEliminarId" :usuario-id="id_usuario" />
    <ModalEditarProyecto v-if="mostrarModalEditar" :proyecto="proyectoSeleccionado" @updated="handleProyectoActualizado" @close="closeEditModal" />
    <ModalProyecto v-if="mostrarModalCrear" @creado="handleProyectoCreado" @cerrar="cerrarModalCrear" />
    <ModalCompartir v-if="mostrarModalCompartir" :proyecto-id="proyectoCompartirId" @cerrar="closeShareModal" />
    
  </div>
</template>

<script>
// Ajusta las rutas a tus modales
import TarjetaProyecto from './TarjetaProyecto.vue';
import ModalProyecto from './CrearProyecto.vue';
import ModalEliminarProyecto from './ModalEliminar.vue';
import ModalCompartir from './ModalCompartir.vue'; 
import ModalEditarProyecto from './ModalEditarProyecto.vue'; 
import debounce from 'lodash/debounce'; 
// const API_BASE_URL = 'http://127.0.0.1:8001'; 

export default {
    name: 'MisProyectos',
    components: {
        TarjetaProyecto, ModalProyecto, ModalEliminarProyecto, ModalCompartir, ModalEditarProyecto
    },
    props: {
        isDark: { type: Boolean, required: true }
    },
    data() {
        return {
            proyectos: [],
            loading: true,
            error: null,
            
            // Datos de Usuario
            id_usuario: null,
            
            // Estados de Modales
            mostrarModalEliminar: false, proyectoEliminarId: null,
            mostrarModalCrear: false,
            mostrarModalCompartir: false, proyectoCompartirId: null,
            mostrarModalEditar: false, proyectoSeleccionado: null,

            // 🚨 NUEVO: Estado de Paginación y Búsqueda
            searchQuery: '',
            page: 1,
            limit: 9, // 9 tarjetas se ven bien en grid de 3 columnas
            totalPages: 1,
            totalRecords: 0
        };
    },
    mounted() {
        this.cargarProyectos();
    },
    // Crear la función debounced una sola vez
    created() {
        this.debouncedSearch = debounce(() => {
            this.page = 1; // Reset a página 1 al buscar
            this.cargarProyectos();
        }, 500);
    },
    methods: {
        // -----------------------------------------------------------------------
        // LÓGICA DE CARGA Y FETCH
        // -----------------------------------------------------------------------
        // 🚨 Método input que llama al debounce
        onSearchInput() {
            this.debouncedSearch();
        },

        // 🚨 Método de Paginación
        changePage(newPage) {
            if (newPage >= 1 && newPage <= this.totalPages) {
                this.page = newPage;
                this.cargarProyectos();
            }
        },

        async cargarProyectos() {
            this.loading = true;
            this.error = null;
            const resultado = JSON.parse(localStorage.getItem('resultado'));
            const token = localStorage.getItem('accessToken'); 

            if (!resultado || !token) {
                this.$router.push('/');
                return;
            }

            this.id_usuario = resultado.usuario.id;
            
            // 🚨 Construir URL con Query Params
            const params = new URLSearchParams({
                page: this.page,
                limit: this.limit,
                search: this.searchQuery
            });
            
            const url = `${API_BASE_URL}/api/proyectos/usuario/${this.id_usuario}?${params.toString()}`;
            
            try {
                const response = await fetch(url, {
                    method: 'GET',
                    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
                });

                if (response.status === 401) {
                    this.$router.push('/'); return;
                }

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Error al obtener proyectos.');
                }

                // 🚨 La API ahora devuelve un objeto paginado { data, total, total_pages }
                const respuesta = await response.json();
                
                // Procesar los datos
                this.proyectos = respuesta.data.map(p => ({
                    ...p,
                    activo: p.activo !== undefined ? p.activo : true, 
                    estado_texto: p.activo ? 'Activo' : 'Pausado',
                    tipo_industria: p.tipo_industria || 'General',
                    icono: p.tipo_industria === 'Agricola' ? 'bi bi-tree-fill' : 'bi bi-house-fill',
                    dispositivos_count: 0, sensores_count: 0, ultima_actualizacion: 'Hace 2 min',
                }));

                // 🚨 Actualizar estado de paginación
                this.totalRecords = respuesta.total;
                this.totalPages = respuesta.total_pages;

            } catch (error) {
                this.error = 'Error: ' + error.message;
                this.proyectos = [];
            } finally {
                this.loading = false;
            }
        },
        
        // -----------------------------------------------------------------------
        // LÓGICA DE ELIMINACIÓN (JWT SEGURO)
        // -----------------------------------------------------------------------
        confirmarEliminacion(id) {
            this.proyectoEliminarId = id;
            this.mostrarModalEliminar = true;
        },

        async eliminar(id) {
            const token = localStorage.getItem('accessToken');
            const usuarioId = this.id_usuario; 
            const url = `${API_BASE_URL}/api/proyectos/${id}`; 

            if (!token || !usuarioId) {
                alert("Error: Sesión no válida.");
                this.cerrarModalEliminar();
                this.$router.push('/');
                return;
            }

            try {
                const response = await fetch(url, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` },
                });

                const data = await response.json();

                if (!response.ok || data.status === 'error') {
                    if (response.status === 403) {
                         throw new Error(data.detail || "No tiene permisos para eliminar este proyecto.");
                    }
                    throw new Error(data.message || 'Error al eliminar el proyecto.');
                }

                alert(data.message || 'Proyecto eliminado exitosamente.');
                
                // Actualizar el array local
                this.proyectos = this.proyectos.filter(p => p.id !== id);
                this.cerrarModalEliminar();

            } catch (err) {
                alert('Error: ' + err.message);
                this.cerrarModalEliminar();
            }
        }, 

        // -----------------------------------------------------------------------
        // LÓGICA DE CREACIÓN Y EDICIÓN
        // -----------------------------------------------------------------------
        
        handleProyectoCreado() {
            this.cargarProyectos(); 
            this.mostrarModalCrear = false;
        },
        
        handleProyectoActualizado() {
            this.closeEditModal(); 
            this.cargarProyectos(); 
        },

        // -----------------------------------------------------------------------
        // MANEJO DE MODALES AUXILIARES
        // -----------------------------------------------------------------------
        
        // Cierre de Modales
        cerrarModalCrear() { this.mostrarModalCrear = false; },
        closeEditModal() { this.mostrarModalEditar = false; this.proyectoSeleccionado = null; },
        closeShareModal() { this.mostrarModalCompartir = false; this.proyectoCompartirId = null; },
        cerrarModalEliminar() { this.mostrarModalEliminar = false; this.proyectoEliminarId = null; },

        // Apertura de Modales
        handleEditClick(proyecto) {
            this.proyectoSeleccionado = proyecto;
            this.mostrarModalEditar = true;
        },
        openShareModal(proyectoId) {
            this.proyectoCompartirId = proyectoId;
            this.mostrarModalCompartir = true;
        },
        
        // Simulación
        simularCambioEstado(proyectoId) {
            const index = this.proyectos.findIndex(p => p.id === proyectoId);
            if (index !== -1) {
                const nuevoEstado = !this.proyectos[index].activo;
                this.proyectos[index].activo = nuevoEstado;
                this.proyectos[index].estado_texto = nuevoEstado ? 'Activo' : 'Pausado';
            }
        },
    }
};
</script>


<style scoped lang="scss">
.mis-proyectos {
    padding-top: 20px;
    /* Espaciado lateral consistente */
    padding-left: 40px;
    padding-right: 40px;
    padding-bottom: 40px;
}

// ----------------------------------------
// BARRA DE HERRAMIENTAS UNIFICADA
// ----------------------------------------
.toolbar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    gap: 20px;
    flex-wrap: wrap; // Para móviles

    .left-group {
        display: flex;
        align-items: center;
        gap: 20px;
        flex-grow: 1;
    }
    
    .count-total {
        font-size: 0.95rem;
        color: $GRAY-COLD;
        white-space: nowrap;
        strong { color: $PRIMARY-PURPLE; }
    }
}
// ----------------------------------------
// HEADER Y ACCIONES UNIFICADAS
// ----------------------------------------
.proyectos-header-view {
    display: flex;
    justify-content: space-between; /* Izquierda <--- Espacio ---> Derecha */
    align-items: center;
    margin-bottom: 30px;
    flex-wrap: wrap; 
    gap: 20px; // Espacio si se envuelve en móviles

    // GRUPO IZQUIERDO (Contador)
    .left-group {
        .count-total {
            font-size: 1.1rem;
            font-weight: 500;
            color: $GRAY-COLD;
            
            strong { 
                color: $PRIMARY-PURPLE; 
                font-size: 1.2rem;
            }
        }
    }

    // GRUPO DERECHO (Buscador + Botón)
    .actions-group {
        display: flex;
        align-items: center;
        gap: 15px; /* Espacio entre el buscador y el botón */
        
        // BUSCADOR
        .search-box {
            position: relative;
            width: 280px; // Ancho fijo del buscador
            
            .search-icon {
                position: absolute;
                left: 15px;
                top: 50%;
                transform: translateY(-50%);
                color: $GRAY-COLD;
                font-size: 0.9rem;
            }
            
            .search-input {
                width: 100%;
                padding: 10px 15px 10px 40px; // Espacio a la izquierda para el icono
                border-radius: 10px;
                border: 1px solid $LIGHT-BORDER; // Variable global
                font-size: 0.9rem;
                outline: none;
                background-color: $WHITE;
                transition: all 0.2s ease;
                
                &:focus {
                    border-color: $PRIMARY-PURPLE;
                    box-shadow: 0 0 0 3px rgba($PRIMARY-PURPLE, 0.1);
                    width: 300px; // Efecto de expansión sutil al escribir
                }
            }
            
            // Tema Oscuro
            &.theme-dark .search-input {
                background-color: $DARK-INPUT-BG; // Variable global
                border-color: rgba($WHITE, 0.1);
                color: $LIGHT-TEXT;
                &:focus { border-color: $PRIMARY-PURPLE; }
            }
        }

        // BOTÓN NUEVO
        .btn-nuevo-proyecto {
            background: $SUCCESS-COLOR; // Variable global
            color: $WHITE;
            border: none;
            padding: 10px 24px;
            border-radius: 10px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: right;
            gap: 8px;
            white-space: nowrap; // Evita que el texto se rompa
            box-shadow: 0 4px 10px rgba($SUCCESS-COLOR, 0.3);
            transition: transform 0.2s;

            &:hover { transform: translateY(-2px); }
            &:active { transform: translateY(0); }
            
            .icon-space { font-size: 1.1rem; }
        }
    }
}
// ----------------------------------------
// GRID Y ALERTAS
// ----------------------------------------
.proyectos-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); 
    gap: 25px;
}

.alerta-vacio, .alerta-loading, .alerta-error {
    text-align: center;
    padding: 40px;
    border-radius: 12px;
    margin-top: 20px;
    font-weight: 500;
}

.alerta-vacio {
    background-color: rgba($GRAY-COLD, 0.1);
    color: $GRAY-COLD;
    border: 1px dashed $GRAY-COLD;
}

.alerta-error {
    background-color: rgba($DANGER-COLOR, 0.1);
    color: $DANGER-COLOR;
    border: 1px solid rgba($DANGER-COLOR, 0.2);
}

// ----------------------------------------
// PAGINACIÓN
// ----------------------------------------
.pagination-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    margin-top: 50px;
    padding-bottom: 30px;
    
    .btn-page {
        background: transparent;
        border: 1px solid $PRIMARY-PURPLE;
        color: $PRIMARY-PURPLE;
        padding: 8px 18px;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        display: flex; align-items: center; gap: 8px;
        
        &:hover:not(:disabled) {
            background-color: $PRIMARY-PURPLE;
            color: $WHITE;
        }
        &:disabled {
            border-color: $GRAY-COLD;
            color: $GRAY-COLD;
            cursor: not-allowed;
            opacity: 0.5;
        }
    }
    
    .page-info {
        font-weight: 500;
        color: $GRAY-COLD;
    }
}
</style>