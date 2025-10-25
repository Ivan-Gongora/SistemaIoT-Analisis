<template>
    <div class="mis-proyectos">
        <div v-if="error" class="alerta-error">{{ error }}</div>
        <div v-else-if="loading" class="alerta-vacio">Cargando proyectos...</div>
        <div v-else-if="proyectos.length === 0" class="alerta-vacio">
             <i class="bi bi-box-fill"></i> Aún no cuentas con Proyectos. 
        </div>

        <div class="proyectos-header-view">
            <div class="proyectos-status-info">
                <span class="count-total">{{ proyectos.length }} ecosistemas</span>
                <span class="count-active" v-if="proyectosActivos > 0">+{{ proyectosActivos }} activos</span>
            </div>
            
            <button class="btn-nuevo-proyecto" @click="mostrarModalCrear = true">
                <i class="bi bi-plus icon-space"></i> Nuevo Proyecto
            </button>
        </div>

        <div class="proyectos-grid">
            <TarjetaProyecto 
                v-for="proyecto in proyectos" 
                :key="proyecto.id" 
                :proyecto="proyecto" 
                @toggle-activo="simularCambioEstado"
                @open-share-modal="openShareModal" 
                @edit-project="handleEditClick" 
                @confirmar-eliminar="confirmarEliminacion"
            />
        </div> 
        
        <ModalEliminarProyecto
            v-if="mostrarModalEliminar" 
            @cancelar="cerrarModalEliminar"
            @confirmar="eliminar(proyectoEliminarId)"
            :proyecto-id="proyectoEliminarId" 
            :usuario-id="id_usuario" 
        />
        <ModalEditarProyecto
            v-if="mostrarModalEditar"
            :proyecto="proyectoSeleccionado"
            @updated="handleProyectoActualizado" 
            @close="closeEditModal"
        />
        <ModalProyecto 
            v-if="mostrarModalCrear"
            @creado="handleProyectoCreado" 
            @cerrar="cerrarModalCrear"
        />
        <ModalCompartir
            v-if="mostrarModalCompartir"
            :proyecto-id="proyectoCompartirId"
            @cerrar="closeShareModal"
        />
    </div>
</template>

<script>
// Ajusta las rutas a tus modales
import TarjetaProyecto from './TarjetaProyecto.vue';
import ModalProyecto from './CrearProyecto.vue';
import ModalEliminarProyecto from './ModalEliminar.vue';
import ModalCompartir from './ModalCompartir.vue'; 
import ModalEditarProyecto from './ModalEditarProyecto.vue'; 


const API_BASE_URL = 'http://127.0.0.1:8001'; 

export default {
    name: 'MisProyectos',
    components: {
        TarjetaProyecto,
        ModalProyecto,
        ModalEliminarProyecto,
        ModalCompartir,
        ModalEditarProyecto
    },
    data() {
        return {
            proyectos: [],
            loading: true,
            mostrarModalEliminar: false,
            proyectoEliminarId: null,
            mostrarModalCrear: false,
            id_usuario: null,
            tipo_usuario: null,
            error: null,
            mostrarModalCompartir: false,
            proyectoCompartirId: null,
            mostrarModalEditar: false,
            proyectoSeleccionado: null,
        };
    },
    computed: {
        proyectosActivos() {
             // El computed property es correcto
             return this.proyectos.filter(p => p.activo).length; 
        }
    },
    mounted() {
        this.cargarProyectos();
    },
    methods: {
        // -----------------------------------------------------------------------
        // LÓGICA DE CARGA Y FETCH
        // -----------------------------------------------------------------------
        async cargarProyectos() {
            this.loading = true;
            this.error = null;
            const resultado = JSON.parse(localStorage.getItem('resultado'));
            const token = localStorage.getItem('accessToken'); 

            if (!resultado || !token) {
                this.error = 'Sesión no válida.';
                this.$router.push('/');
                return;
            }

            this.id_usuario = resultado.usuario.id;
            this.tipo_usuario = resultado.usuario.tipo_usuario;
            
            let url = `${API_BASE_URL}/api/proyectos`; 
            if (this.tipo_usuario !== 'admin') {
                url = `${API_BASE_URL}/api/proyectos/usuario/${this.id_usuario}`;
            }
            
            try {
                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`, 
                        'Content-Type': 'application/json'
                    }
                });

                if (response.status === 401) {
                    localStorage.removeItem('accessToken');
                    localStorage.removeItem('resultado');
                    this.$router.push('/');
                    return;
                }

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Error al obtener proyectos.');
                }

                const data = await response.json();
                
                // Mapeo y adición de datos simulados para la tarjeta
                this.proyectos = data.map(p => ({
                    ...p,
                    activo: p.activo !== undefined ? p.activo : true, 
                    estado_texto: p.activo ? 'Activo' : 'Pausado',
                    tipo_industria: p.tipo_industria || 'General', // Usa el valor de la DB, o 'General'
                    icono: p.tipo_industria === 'Agricola' ? 'bi bi-tree-fill' : 'bi bi-house-fill',
                    dispositivos_count: 0,
                    sensores_count: 0,
                    ultima_actualizacion: 'Hace 2 minutos',
                })); 
            } catch (error) {
                this.error = 'Error de conexión o API: ' + error.message;
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
            const url = `${API_BASE_URL}/api/proyectos/?id=${id}&usuario_id=${usuarioId}`; 

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
// ----------------------------------------
// VARIABLES SCSS 
// ----------------------------------------
$PRIMARY-PURPLE: #8A2BE2; 
$SUCCESS-COLOR: #1ABC9C; 
$LIGHT-TEXT: #E4E6EB;
$DARK-TEXT: #333333;

.mis-proyectos {
    padding-top: 20px;
}

.proyectos-header-view {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    padding-left: 5px; 

    .proyectos-status-info {
        font-size: 1.1rem;
        font-weight: 500;
        
        .count-active {
            color: $SUCCESS-COLOR; 
            font-weight: 700;
            margin-left: 10px;
        }
    }
    
    .btn-nuevo-proyecto {
        background: $SUCCESS-COLOR;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 0.95rem;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 10px rgba($SUCCESS-COLOR, 0.3);

        &:hover { opacity: 0.9; }
        .icon-space { margin-right: 8px; }
    }
}

.proyectos-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
    gap: 25px;
}

// Estilos de tema para la info de status
.theme-dark .proyectos-status-info .count-total { color: rgba(255, 255, 255, 0.8); }
.theme-light .proyectos-status-info .count-total { color: $DARK-TEXT; }

.alerta-error, .alerta-vacio {
    margin-top: 20px;
    padding: 15px;
    border-radius: 8px;
    background-color: #f8d7da;
    color: #721c24;
    font-weight: 600;
}
</style>