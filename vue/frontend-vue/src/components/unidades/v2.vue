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

          <div class="magnitud-groups-container">
            
            <section v-for="(unidadesGrupo, magnitud) in unidadesAgrupadas" :key="magnitud" class="magnitud-group">
              
              <h4 class="magnitud-titulo">{{ magnitud }}</h4>
              
              <div class="unidades-pills-grid">
                <div
                  v-for="unidad in unidadesGrupo"
                  :key="unidad.id"
                  class="unidad-pill"
                  @click="openEditModal(unidad)"
                  title="Clic para editar"
                >
                  <span class="pill-simbolo">{{ unidad.simbolo }}</span>
                  <div class="pill-info">
                    <span class="pill-nombre">{{ unidad.nombre }}</span>
                    <span class="pill-descripcion">{{ unidad.descripcion }}</span>
                  </div>
                </div>
              </div>
            </section>
          </div>
          
          <div v-if="filteredUnidades.length === 0 && unidades.length > 0" class="alert-empty-data">
            No se encontraron unidades que coincidan con "{{ searchQuery }}".
          </div>
          <div v-if="unidades.length === 0" class="alert-empty-data">
            No hay unidades de medida registradas.
          </div>
        </div>
      </div>
    </div>
    
    <ModalUnidadMedida
      v-if="mostrarModalCrear"
      :is-dark="isDark"
      :modo-edicion="false"
      @unidad-guardada="handleUnidadGuardada"
      @close="closeCreateModal"
    />
    <ModalUnidadMedida
      v-if="mostrarModalEditar"
      :is-dark="isDark"
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
        },
        // 2. 🚨 NUEVO: Agrupa las unidades filtradas por 'magnitud_tipo'
        unidadesAgrupadas() {
            return this.filteredUnidades.reduce((groups, unidad) => {
                const magnitud = unidad.magnitud_tipo || 'Sin Categoría';
                if (!groups[magnitud]) {
                    groups[magnitud] = [];
                }
                groups[magnitud].push(unidad);
                return groups;
            }, {});
        }
        
    },
    
 beforeUnmount() { 
       if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', this.handleThemeChange);
        }
    },
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
// ESTILOS DE HEADER (Buscador y Botón)
// ----------------------------------------
.unidades-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px; // Más espacio
  
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

// ----------------------------------------
// 🚨 NUEVOS ESTILOS: GRUPO DE MAGNITUD
// ----------------------------------------
.magnitud-groups-container {
  width: 100%;
}

.magnitud-group {
  margin-bottom: 35px;
}

.magnitud-titulo {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 15px;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}

.unidades-pills-grid {
  display: grid;
  // Columnas auto-ajustables
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 15px;
}

// ----------------------------------------
// 🚨 NUEVOS ESTILOS: PÍLDORA DE UNIDAD (Reemplaza la fila <tr>)
// ----------------------------------------
.unidad-pill {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border-radius: 10px;
  background-color: $SUBTLE-BG-LIGHT;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #eee;
  cursor: pointer;
  transition: all 0.2s ease-out;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 12px rgba(0, 0, 0, 0.1);
    border-color: $PRIMARY-PURPLE;
  }

  .pill-simbolo {
    font-weight: bold;
    padding: 8px 12px;
    border-radius: 8px;
    background-color: $PRIMARY-PURPLE;
    color: white;
    font-size: 1rem;
    margin-right: 15px;
    min-width: 45px; // Ancho mínimo
    text-align: center;
  }

  .pill-info {
    display: flex;
    flex-direction: column;
    overflow: hidden; // Evita que el texto largo rompa el layout
  }

  .pill-nombre {
    font-size: 1rem;
    font-weight: 600;
  }

  .pill-descripcion {
    font-size: 0.85rem;
    color: $GRAY-COLD;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

// ----------------------------------------
// TEMAS (REACTIVIDAD Y MODO OSCURO)
// ----------------------------------------

.theme-light {
  background-color: $WHITE-SOFT;
  color: $DARK-TEXT;
  .form-control-search {
    background-color: $SUBTLE-BG-LIGHT; // <-- Corregido (era guion bajo)
    border-color: #ddd;
    color: $DARK-TEXT;
  }
}

.theme-dark {
  background-color: $DARK-BG-CONTRAST;
  color: $LIGHT-TEXT;
  
  .plataforma-contenido { background-color: $DARK-BG-CONTRAST; }

  .magnitud-titulo {
    color: $LIGHT-TEXT;
    border-bottom-color: rgba($LIGHT-TEXT, 0.1);
  }

  .unidad-pill {
    background-color: $SUBTLE-BG-DARK;
    border-color: rgba($LIGHT-TEXT, 0.1);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    
    &:hover {
      border-color: $PRIMARY-PURPLE;
    }

    .pill-simbolo {
      background-color: $PRIMARY-PURPLE;
      color: $LIGHT-TEXT;
    }
    .pill-nombre {
      color: $LIGHT-TEXT;
    }
    .pill-descripcion {
      color: $GRAY-COLD;
    }
  }

  .form-control-search {
    background-color: $BLUE-MIDNIGHT;
    border: 1px solid rgba($LIGHT-TEXT, 0.2);
    color: $LIGHT-TEXT;
    &::placeholder { color: $GRAY-COLD; }
  }
}
</style>