<template>
  <div class="plataforma-layout" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    
    <BarraLateralPlataforma :is-open="isSidebarOpen" />
    
    <div class="plataforma-contenido" :class="{ 'shifted': isSidebarOpen }">
      
      <EncabezadoPlataforma
        titulo="Unidades de Medida"
        subtitulo="Gestión de estándares de medición para sensores"
        @toggle-sidebar="toggleSidebar"
        :is-sidebar-open="isSidebarOpen"
      />

      <div class="unidades-contenido">
        
        <div v-if="loading" class="alert-info">Cargando unidades...</div>
        <div v-else-if="error" class="alert-error">{{ error }}</div>
        
        <div v-else>
          <div class="unidades-header">
            <h3>Total de Unidades: {{ filteredUnidades.length }}</h3>
            
            <div class="search-and-actions">
              <input
                type="text"
                v-model="searchQuery"
                class="form-control-search"
                placeholder="Buscar por nombre, símbolo o magnitud..."
              >
              <button @click="openCreateModal" class="btn-primary-action">
                <i class="bi bi-plus-circle-fill"></i> Nueva Unidad
              </button>
            </div>
          </div>

          <div class="unidades-tabla-container">
            <table class="table table-striped table-hover">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nombre</th>
                  <th>Símbolo</th>
                  <th>Tipo de Magnitud</th>
                  <th>Descripción</th>
                  <th class="text-end">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="unidad in filteredUnidades" :key="unidad.id">
                  <td>{{ unidad.id }}</td>
                  <td>{{ unidad.nombre }}</td>
                  <td><span class="simbolo-badge">{{ unidad.simbolo }}</span></td>
                  <td>{{ unidad.magnitud_tipo }}</td>
                  <td>{{ unidad.descripcion || 'Sin descripción.' }}</td>
                  <td class="text-end">
                    <button @click="openEditModal(unidad)" class="btn-action btn-edit" title="Modificar">
                      <i class="bi bi-pencil"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            
            <div v-if="filteredUnidades.length === 0 && unidades.length > 0" class="alert-empty-data">
              No se encontraron unidades que coincidan con "{{ searchQuery }}".
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <ModalUnidadMedida
      v-if="mostrarModalCrear"
      :modo-edicion="false"
      @unidad-guardada="handleUnidadGuardada"
      @close="closeCreateModal"
    />
    <ModalUnidadMedida
      v-if="mostrarModalEditar"
      :modo-edicion="true"
      :unidad-data="unidadSeleccionada"
      @unidad-guardada="handleUnidadGuardada"
      @close="closeEditModal"
    />
  </div>
</template>

<script>
import BarraLateralPlataforma from '../plataforma/BarraLateralPlataforma.vue';
import EncabezadoPlataforma from '../plataforma/EncabezadoPlataforma.vue';
import ModalUnidadMedida from './ModalUnidadMedida.vue'; 
// 🚨 NOTA: Si usas un modal de eliminación, impórtalo aquí.

const API_BASE_URL = 'http://127.0.0.1:8001';

export default {
    name: 'VistaUnidadesMedida',
    components: {
        BarraLateralPlataforma,
        EncabezadoPlataforma,
        ModalUnidadMedida,
        // ... otros modales
    },
    data() {
        return {
            isDark: false,
            isSidebarOpen: true,
            loading: true,
            error: null,
            unidades: [], 
            
            mostrarModalCrear: false,
            mostrarModalEditar: false,
            unidadSeleccionada: null,
            // Estado para la búsqueda
            searchQuery: '',
        };
    },
    mounted() {
        this.cargarUnidades();
        this.detectarTemaSistema();
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', this.handleThemeChange);
        }
    },
    computed: {
        // 🚨 NUEVO: Propiedad computada para filtrar la lista
        filteredUnidades() {
            if (!this.searchQuery) {
                return this.unidades; // Si no hay búsqueda, devuelve la lista completa
            }
            
            const lowerQuery = this.searchQuery.toLowerCase();
            
            return this.unidades.filter(unidad => {
                // Busca en nombre, simbolo o magnitud
                return (
                    unidad.nombre.toLowerCase().includes(lowerQuery) ||
                    unidad.simbolo.toLowerCase().includes(lowerQuery) ||
                    (unidad.magnitud_tipo && unidad.magnitud_tipo.toLowerCase().includes(lowerQuery))
                );
            });
        }
    },
    beforeUnmount() { /* ... */ },
    methods: {
        // -----------------------------------------------------
        // 🚨 CONSUMO DE API (Sin permisos complejos)
        // -----------------------------------------------------
        async cargarUnidades() {
            this.loading = true;
            this.error = null;
            const token = localStorage.getItem('accessToken');
            
            if (!token) { this.$router.push('/'); return; }

            try {
                const response = await fetch(`${API_BASE_URL}/api/unidades`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                if (!response.ok) {
                    // Si el 403 ocurre aquí, significa que el backend SÍ tiene el problema de permisos que pusimos en espera
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Fallo al obtener unidades.');
                }
                
                this.unidades = await response.json();
                
            } catch (err) {
                this.error = err.message || 'Error de conexión al obtener unidades.';
            } finally {
                this.loading = false;
            }
        },
        
        // -----------------------------------------------------
        // MANEJO DE MODALES Y ACCIONES (CRUD)
        // -----------------------------------------------------
        
        // Creación
        openCreateModal() { this.mostrarModalCrear = true; },
        closeCreateModal() { this.mostrarModalCrear = false; },
        
        // Edición
        openEditModal(unidad) {
            this.unidadSeleccionada = unidad;
            this.mostrarModalEditar = true;
        },
        closeEditModal() {
            this.mostrarModalEditar = false;
            this.unidadSeleccionada = null;
        },
        
        // Recarga después de Crear/Editar
        handleUnidadGuardada() {
            this.closeCreateModal();
            this.closeEditModal();
            this.cargarUnidades(); // 🚨 Sincroniza con el backend
        },
     
        
        // -----------------------------------------------------
        // LÓGICA DE LAYOUT
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
// ----------------------------------------
// VARIABLES SCSS (Mínimas para el Layout)
// ----------------------------------------
$WIDTH-SIDEBAR: 280px; 
$WIDTH-CLOSED: 80px; 
$WHITE-SOFT: #F7F9FC; 
$DARK-BG-CONTRAST: #1E1E30; 
$LIGHT-TEXT: #E4E6EB;
$DARK-TEXT: #333333;
$SUBTLE-BG-DARK: #2B2B40; 
$PRIMARY-PURPLE: #8A2BE2;
$SUCCESS-COLOR: #1ABC9C;
$GRAY-COLD: #99A2AD;
$BLUE-MIDNIGHT: #1A1A2E; 
$SUBTLE-BG-LIGHT: #FFFFFF;
// ----------------------------------------
// LAYOUT Y POSICIONAMIENTO
// ----------------------------------------
.plataforma-layout {
    display: flex;
    min-height: 100vh;
    transition: background-color 0.3s;
    background-color: $WHITE-SOFT; 
}

.plataforma-contenido {
    margin-left: $WIDTH-CLOSED;
    flex-grow: 1;
    padding: 0; 
    transition: margin-left 0.3s ease-in-out;
    
    &.shifted { margin-left: $WIDTH-SIDEBAR; }
}

.unidades-contenido {
    padding: 20px 40px 40px 40px;
}

// ----------------------------------------
// ESTILOS DE LA TABLA Y HEADER
// ----------------------------------------
.unidades-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h3 { font-size: 1.4rem; font-weight: 600; }
    .btn-primary-action {
        background-color: $SUCCESS-COLOR;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: 600;
        i { margin-right: 5px; }
    }
    .search-and-actions {
        display: flex;
        gap: 15px;
        align-items: center;
    }
}
.form-control-search {
    padding: 10px 15px;
    border-radius: 8px;
    border: 1px solid #ddd;
    min-width: 300px;
    font-size: 0.95rem;
}
.unidades-tabla-container {
    width: 100%;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.table {
    width: 100%;
    margin-bottom: 0;
    
    th {
        font-size: 0.9rem;
        text-transform: uppercase;
        padding: 15px;
        color: $GRAY-COLD;
        background-color: $BLUE-MIDNIGHT; 
    }
    
    td {
        padding: 12px 15px;
        font-size: 0.95rem;
    }
    
    .simbolo-badge {
        font-weight: bold;
        padding: 4px 8px;
        border-radius: 4px;
        background-color: $PRIMARY-PURPLE;
        color: white;
    }
    
    .btn-action {
        background: none;
        border: none;
        color: $GRAY-COLD;
        font-size: 1rem;
        margin-left: 10px;
        &:hover { color: $PRIMARY-PURPLE; }
    }
}

// ----------------------------------------
// TEMAS (REACTIVIDAD Y MODO OSCURO)
// ----------------------------------------

.theme-light {
    background-color: $WHITE-SOFT; 
    color: $DARK-TEXT; 
    
    .table { border: 1px solid #ddd; background-color: #fff; }
    .table td { color: $DARK-TEXT; border-color: #eee; }
    .form-control-search {
        background-color: $SUBTLE-BG-LIGHT;
        border-color: #ddd;
        color: $DARK-TEXT;
    }
}

// 🚨 MODO OSCURO (CORRECCIÓN FINAL DE COLORES DE TEXTO Y FILAS)
.theme-dark {
    background-color: $DARK-BG-CONTRAST; 
    color: $LIGHT-TEXT;
    
    .plataforma-contenido { background-color: $DARK-BG-CONTRAST; }

    .table {
        background-color: $SUBTLE-BG-DARK;
        color: $LIGHT-TEXT; // Color heredado para todo
        border: 1px solid rgba($LIGHT-TEXT, 0.1);
        
        // Estilo de encabezados
        th { background-color: $BLUE-MIDNIGHT; color: $GRAY-COLD; border-bottom-color: rgba($LIGHT-TEXT, 0.1); }
        
        // 🚨 CRÍTICO: Forzar color blanco en celdas de datos para sobrescribir Bootstrap
        td { 
            color: $DARK-BG-CONTRAST !important; /* Asegura que el texto */
            border-color: rgba($LIGHT-TEXT, 0.05); 
        } 
        
        // 🚨 CRÍTICO 2: Sobrescribir las filas 'striped' de Bootstrap
        // Filas Impares (Alternativas)
        .table-striped > tbody > tr:nth-of-type(odd) > td {
            background-color: $BLUE-MIDNIGHT !important; 
        }
        // Filas Pares (Fondo base de la tabla)
        .table-striped > tbody > tr:nth-of-type(even) > td {
            background-color: $SUBTLE-BG-DARK !important; 
        }
        
        // 🚨 CRÍTICO 3: Sobrescribir el hover de Bootstrap
        .table-hover > tbody > tr:hover > td {
             background-color: rgba($LIGHT-TEXT, 0.1) !important;
        }
        
        
        
        // Aseguramos que el badge sea del color correcto en dark
        .simbolo-badge { color: $LIGHT-TEXT; } 
    }
    .form-control-search {
        background-color: $BLUE-MIDNIGHT; 
        border: 1px solid rgba($LIGHT-TEXT, 0.2); 
        color: $LIGHT-TEXT; 
        &::placeholder {
            color: $GRAY-COLD;
        }
    }
    .btn-action { color: $GRAY-COLD; }
}
</style>