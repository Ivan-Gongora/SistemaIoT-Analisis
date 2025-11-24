<template>
    <div class="proyecto-tarjeta" :class="{ 'theme-dark': isDark, 'theme-light': !isDark, 'active': proyecto.activo }">
        <div class="card-header">
            <div class="icon-box" :style="{ background: iconGradient }">
                <i :class="proyecto.icono || 'fas fa-box'"></i>
            </div>
            
            <span class="status-dot"></span>
        </div>

        <div class="card-body">
            <router-link :to="{ name: 'DetalleProyecto', params: { id: proyecto.id } }" style="text-decoration: none; color: inherit;">
            <h2 class="proyecto-titulo"  style="cursor: pointer;">
                {{ proyecto.nombre }}
            </h2>
            </router-link>
            <p class="proyecto-tipo-estado">
                <span class="tag-tipo">{{ proyecto.tipo_industria || 'General' }}</span> 
                <span class="tag-estado">{{ statusText }}</span>
            </p>
            <p class="proyecto-descripcion">{{ proyecto.descripcion }}</p>
            
            <div class="metricas-container">
                
                <div class="metrica metrica-dispositivos">
                    <i class="fas fa-tablet-alt"></i>
                    <span>Dispositivos</span>
                    <span class="count">{{ dispositivos_count !== null ? dispositivos_count : 0 }}</span>
                </div>
                
                <div class="metrica metrica-sensores">
                    <i class="fas fa-signal"></i>
                    <span>Sensores</span>
                    <span class="count">{{ sensores_count !== null ? sensores_count : 0 }}</span>
                </div>
            </div>
            
           <div class="card-footer">
                <span class="ultima-actualizacion">
                    <i class="fas fa-clock"></i> Última actualización
                    <span class="time-ago">{{ proyecto.ultima_actualizacion || 'N/A' }}</span>
                </span>
                
                <div class="acciones">
                    <button 
                        v-if="proyecto.mi_rol === 'Propietario' || proyecto.mi_rol === 'Colaborador'"
                        @click="toggleState" 
                        class="btn-accion btn-toggle-state" 
                        :class="{'btn-pause': proyecto.activo}" 
                        :title="toggleAction"
                    >
                        <i :class="toggleIcon"></i> 
                        {{ toggleAction }}
                    </button>
                    
                    <button 
                        v-if="proyecto.mi_rol === 'Propietario'"
                        class="btn-accion btn-share" 
                        @click="openShareModal" 
                        title="Invitar usuarios"
                    >
                        <i class="bi bi-share"></i>
                    </button>
                    
                    <button 
                        v-if="proyecto.mi_rol === 'Propietario'"
                        class="btn-accion btn-detalle" 
                        @click="editProject(proyecto)" 
                        title="Editar proyecto"
                    >
                        <i class="bi bi-pencil"></i>
                    </button>

                    <button 
                        v-if="proyecto.mi_rol === 'Propietario'"
                        class="btn-accion btn-eliminar" 
                        @click="deleteProject" 
                        title="Eliminar proyecto"
                    >
                        <i class="bi bi-trash"></i>
                    </button>
                    
                    <span class="role-badge" :class="proyecto.mi_rol.toLowerCase()">
                        {{ proyecto.mi_rol }}
                    </span>
                </div>
            </div>
        
        </div>
    </div>
</template>

<script>
// Lista de colores vibrantes para asignación automática (sacados de la paleta moderna)
const PROJECT_COLORS = [
    'linear-gradient(45deg, #A300FF, #6F00FF)', // Morado/Violeta
    'linear-gradient(45deg, #1ABC9C, #00C853)', // Verde Menta/Éxito
    'linear-gradient(45deg, #FFA500, #FF8C00)', // Naranja/Ambar
    'linear-gradient(45deg, #1E90FF, #00BFFF)', // Azul Cielo
    'linear-gradient(45deg, #FF69B4, #FF1493)', // Rosa
];

// Función para obtener un color basado en el ID (para que siempre sea el mismo color para el mismo ID)
const getColorForId = (id) => {
    // Si el ID es 0, usa el primer color. Si es 5, vuelve a usar el primer color.
    return PROJECT_COLORS[id % PROJECT_COLORS.length];
};

export default {
    name: 'TarjetaProyecto',
    props: {
        proyecto: {
            type: Object,
            required: true
        },
        isDark: {
            type: Boolean,
            required: true}
    },
    data() {
        return {
            // 🚨 NUEVOS DATOS: Usaremos valores nulos para simular que la API no los tiene aún
            dispositivos_count: null, 
            sensores_count: null,
        };
    },
    computed: {
        // 🚨 Genera el color de la caja de icono basado en el ID del proyecto
        iconGradient() {
            return getColorForId(this.proyecto.id);
        },
        // 🚨 Determina la acción y el icono del botón principal
        toggleAction() {
            return this.proyecto.activo ? 'Pausar' : 'Activar';
        },
        toggleIcon() {
            // Opción Bootstrap Icons: bi-pause-fill (o bi-pause) y bi-play-fill (o bi-play)
            return this.proyecto.activo ? 'bi bi-pause' : 'bi bi-play-fill';
        },
        // 🚨 Determina el texto del estado principal
        statusText() {
            return this.proyecto.activo ? 'Activo' : 'Inactivo';
        }
    },
    mounted() {
        // ... (lógica de detección de tema) ...
        // if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        //     this.isDark = true;
        // }
        
        // 🚨 Si la API tuviera los datos, los asignarías aquí:
        // this.dispositivos_count = this.proyecto.dispositivos_count;
        // this.sensores_count = this.proyecto.sensores_count;
    },
    methods: {
        // 🚨 Método que se dispara al presionar Pausar/Activar
        toggleState() {
            // Emitimos el evento 'toggle-activo' al componente padre (MisProyectos.vue)
            this.$emit('toggle-activo', this.proyecto.id); 
            // La lógica para cambiar el estado (activo: true/false) se hará en el padre.
        },
        openShareModal() {
            // Emitimos el evento 'open-share-modal' al componente padre (MisProyectos.vue)
            this.$emit('open-share-modal', this.proyecto.id); 
        },
        editProject() {
            // 🚨 CRÍTICO: Emitir el objeto de proyecto completo
            this.$emit('edit-project', this.proyecto); 
        },
        deleteProject() {
            // Emite evento para que el padre abra el modal de confirmación
            this.$emit('confirmar-eliminar', this.proyecto.id);
        },
        verDetalle(id) {
        // Usa el router para navegar a la ruta con el ID
        this.$router.push(`/detalle-proyecto/${id}`);
    },
    }
}
</script>

<style scoped lang="scss">
// ----------------------------------------
// VARIABLES DE ESTILO PROFESIONAL (PALETA DE DISPOSITIVO)
// ----------------------------------------
// $PRIMARY-PURPLE: #8A2BE2;   // Azul Violeta (Acento Principal)
// $SUCCESS-COLOR: #1ABC9C;    // Verde de Éxito
// $BLUE-MIDNIGHT: #1A1A2E;    // Fondo Oscuro de Contraste (Métricas)
// $DARK-TEXT: #333333;        // Texto en Modo Claro
// $LIGHT-TEXT: #E4E6EB;       // Texto en Modo Oscuro
// $SUBTLE-BG-DARK: #2B2B40;   // Fondo de Tarjeta en Modo Oscuro
// $SUBTLE-BG-LIGHT: #FFFFFF;  // Fondo de Tarjeta en Modo Claro
// $WHITE-SOFT: #F7F9FC;       // Fondo de Página en Modo Claro
// $GRAY-COLD: #99A2AD;        // Subtítulos y Divisores
// $DANGER-COLOR: #e74c3c;     // Rojo para Eliminar
// $WARNING-COLOR: #FFC107;    // Amarillo/Naranja para Pausar
// $LIGHT-BG-CARD: #F0F2F5;    // Fondo Claro de Tarjeta
// $SUBTLE-BG-CARD: #FAFAFA;   // Fondo Muy Sutil de Tarjeta
// ----------------------------------------
// ESTILOS BASE DE LA TARJETA
// ----------------------------------------
.proyecto-tarjeta {
    border-radius: 16px; 
    padding: 24px; 
    margin-bottom: 20px;
    transition: all 0.3s ease-in-out;
    cursor: pointer;
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08); 
}

// ----------------------------------------
// TÍTULOS Y CABECERA
// ----------------------------------------
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center; /* CRÍTICO: Alinea verticalmente los ítems */
    margin-bottom: 12px;
}
.icon-box {
    width: 48px; height: 48px; 
    border-radius: 12px;
    display: flex; justify-content: center; align-items: center; /* CRÍTICO: Centra el ÍCONO dentro de la caja */
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2); 
    
    i { 
        font-size: 1.4rem; 
        color: $LIGHT-BG-CARD;
    }
}
.status-dot { 
    width: 10px; height: 10px;
    border-radius: 50%;
    /* No necesita margen superior ya que align-items: center lo centra */
}

.proyecto-titulo { font-size: 1.4rem; font-weight: 700; margin-bottom: 4px; }
.proyecto-tipo-estado {
    font-size: 0.8rem; 
    margin-bottom: 15px;
    
    .tag-tipo { /* Etiqueta de Industria (Ej: Agricultura Precisión) */
        font-weight: 500; 
        padding: 2px 7px; 
        border-radius: 4px;
        margin-right: 8px; 
        color: $PRIMARY-PURPLE; /* Texto del acento principal */
        background-color: rgba($PRIMARY-PURPLE, 0.15); /* Fondo púrpura muy sutil */
    }
}
.proyecto-descripcion {
    font-size: 0.85rem; 
    margin-bottom: 20px;
    line-height: 1.5;
    height: 3.5em; 
    overflow: hidden;
    opacity: 0.8;
}

// ----------------------------------------
// MÉTRICAS (Dispositivos / Sensores)
// ----------------------------------------
.metricas-container {
  display: flex;
    gap: 12px;
    margin-bottom: 20px;
    padding-top: 10px;
    .metrica {
        flex: 1;
        padding: 10px 12px; /* Espaciado más compacto */
        border-radius: 8px; 
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        transition: background-color 0.2s;
        background-color: $BLUE-MIDNIGHT;
        i { 
            font-size: 1rem; 
            margin-bottom: 6px;
            color: $PRIMARY-PURPLE; 
        }
        
        /* Etiqueta (Dispositivos / Sensores) */
        span:first-of-type { 
            font-size: 0.8rem;
            opacity: 0.9;
            margin-bottom: 2px; /* Espacio sutil entre la etiqueta y el contador */
        }
        
        /* Contador (el número grande '0') */
        .count {
            font-size: 1.8rem; 
            font-weight: 700;
            line-height: 1; /* CRÍTICO: Eliminar el espacio extra de línea */
            padding-bottom: 2px;
        }
    }
}

// ----------------------------------------
// FOOTER Y ACCIONES
// ----------------------------------------
.card-footer {
    display: flex;
    flex-wrap: wrap; /* Permite que los elementos pasen a la siguiente línea si es necesario */
    justify-content: space-between;
    align-items: center; 
    font-size: 0.8rem;
    padding-top: 15px; 
    border-top: 1px solid rgba($GRAY-COLD, 0.3); 
    
    .ultima-actualizacion {
        display: flex;
        align-items: center;
        margin-bottom: 10px; /* Espacio para separar la línea de tiempo de la fila de botones */
        width: 100%; /* Ocupa todo el ancho */
        
        /* Estilos de la hora (HACE 2 minutos) */
        .time-ago { 
            font-weight: 600; 
            margin-left: 5px; 
            margin-right: auto; /* Mueve el tiempo al inicio y el resto se justifica a la derecha */
        }
    }

    .acciones {
        display: flex;
        align-items: center;
        gap: 8px; 
        margin-left: auto; /* Justifica este grupo a la derecha */
    }
    
    .btn-accion {
        border: none;
        padding: 5px;
        transition: color 0.2s;
        
        // Botón Pausar/Activar
        &.btn-toggle-state { 
            border-radius: 8px; 
            padding: 8px 15px;
            font-weight: 600;
            
            &.btn-pause { /* Estado Pausado */
                background-color: $WARNING-COLOR; 
                color: $DARK-TEXT; 
            }
            &:not(.btn-pause) { /* Estado Activar/Play */
                background-color: $SUCCESS-COLOR;
                color: $LIGHT-TEXT;
            }
        }
        
        // Botones Icono (Share, Edit, Delete)
        &.btn-share, &.btn-detalle, &.btn-eliminar {
            width: 32px; height: 32px;
            border-radius: 6px;
            display: flex; justify-content: center; align-items: center;
            
            i { font-size: 0.9rem; }
        }
    }
}

// ----------------------------------------
// TEMAS (APLICACIÓN DE COLORES DE PALETA)
// ----------------------------------------

// MODO OSCURO (DARK MODE)
.theme-dark {
    background-color: $SUBTLE-BG-DARK; /* Fondo de Tarjeta */
    color: $LIGHT-TEXT;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);

    .proyecto-titulo, .proyecto-descripcion { color: $LIGHT-TEXT; }
    .proyecto-tipo-estado { color: rgba($LIGHT-TEXT, 0.7); }
    
    // Métricas en Dark Mode
    .metrica {
        background-color: $BLUE-MIDNIGHT; /* Fondo de métrica más oscuro que la tarjeta */
        border-color: rgba($LIGHT-TEXT, 0.1); 
        
        .count { color: $LIGHT-TEXT; } /* Valor numérico claro */
    }
    
    // Botones de Icono
    .btn-accion {
        color: $LIGHT-TEXT;
        
        &.btn-share, &.btn-detalle, &.btn-eliminar {
            background-color: rgba($LIGHT-TEXT, 0.1); /* Fondo sutil */
            color: $GRAY-COLD; 
            
            &:hover {
                background-color: rgba($PRIMARY-PURPLE, 0.3);
                color: $LIGHT-TEXT;
            }
        }
    }
}

// MODO CLARO
.theme-light {
    background-color: $SUBTLE-BG-CARD;
    color: $DARK-TEXT;
    
    .metrica {
        background-color: $WHITE-SOFT;
        border-color: rgba($DARK-TEXT, 0.1);
        color: $DARK-TEXT;
        
        .count { color: $DARK-TEXT; }
    }
    
    // Botones de Icono
    .btn-accion {
        color: $DARK-TEXT;
        
        &.btn-share, &.btn-detalle, &.btn-eliminar {
            background-color: rgba($DARK-TEXT, 0.05);
            color: $DARK-TEXT;
            
            &:hover {
                background-color: rgba($PRIMARY-PURPLE, 0.1);
                color: $PRIMARY-PURPLE;
            }
        }
    }
}
</style>