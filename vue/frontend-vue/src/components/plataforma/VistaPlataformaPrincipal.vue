<template>
  <div class="plataforma-layout" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    
    <BarraLateralPlataforma :is-open="isSidebarOpen" />
    
    <div class="plataforma-contenido" :class="{ 'shifted': isSidebarOpen }">
      
      <EncabezadoPlataforma @toggle-sidebar="toggleSidebar" :is-sidebar-open="isSidebarOpen" />
      
      <div class="dashboard-grid">
        <TarjetasPlataforma class="grid-item-cards" />
        
        <div class="grid-item-metrics">
            <EstadoSistema :is-dark="isDark" /> 
        </div>
        
        <div class="grid-item-activity">
            <ActividadReciente :is-dark="isDark" /> 
        </div>
    </div>

    </div>
  </div>
</template>

<script>
import BarraLateralPlataforma from './BarraLateralPlataforma.vue';
import EncabezadoPlataforma from './EncabezadoPlataforma.vue';
import TarjetasPlataforma from './TarjetasPlataforma.vue';
import EstadoSistema from './EstadoSistema.vue'; // 🚨 IMPORTAR
import ActividadReciente from './ActividadReciente.vue'; // 🚨 IMPORTAR

export default {
  name: 'VistaPlataformaPrincipal',
  components: {
    BarraLateralPlataforma,
    EncabezadoPlataforma,
    TarjetasPlataforma,
    EstadoSistema, 
    ActividadReciente, 
  },
  data() {
    return {
      isDark: false, 
      isSidebarOpen: true, // 🚨 NUEVO: Estado de la barra lateral
    };
  },
  mounted() {
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
    // 🚨 NUEVO MÉTODO: Cambia el estado del sidebar
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen;
    },
    handleThemeChange(event) {
      this.isDark = event.matches;
    },
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
// VARIABLES DEL LAYOUT
// ----------------------------------------
$WIDTH-SIDEBAR: 280px; 
$WIDTH-CLOSED: 80px; // Ancho del sidebar colapsado
$WHITE-SOFT: #F7F9FC; 
$DARK-BG-CONTRAST: #1E1E30; 
$BLUE-MIDNIGHT: #1A1A2E; 
$DARK-TEXT: #333333;      
$LIGHT-TEXT: #E4E6EB;     
$GRAY-COLD: #99A2AD;


// ----------------------------------------
// LAYOUT PRINCIPAL
// ----------------------------------------
.plataforma-layout {
  display: flex;
  width: 100%;
  min-height: 100vh;
  transition: background-color 0.3s;
  // 🚨 CRÍTICO: Establecer un fondo inicial (opcionalmente el más común: el claro)
  background-color: $WHITE-SOFT; 
}

.plataforma-contenido {
  // 🚨 CRÍTICO: Margen base (estado cerrado)
  margin-left: $WIDTH-CLOSED;
  flex-grow: 1;
  padding: 0; 
  transition: margin-left 0.3s ease-in-out; // 🚨 Transición suave
  
  // 🚨 CRÍTICO: Clase para el estado ABIERTO
  &.shifted {
    margin-left: $WIDTH-SIDEBAR;
  }
}

// ----------------------------------------
// DASHBOARD GRID (Distribución de Tarjetas y Módulos)
// ----------------------------------------

.dashboard-grid {
    // ...
    // Habilitar la rejilla de 2 columnas para los módulos inferiores
    display: grid; 
    
    // 🚨 AJUSTE DE COLUMNAS PARA MÓDULOS INFERIORES: 40% y 60%
    grid-template-columns: 2fr 3fr; /* Divide el espacio restante en 5 partes, 2 para la izquierda, 3 para la derecha */
    
    gap: 20px; 
    padding: 0 40px 40px 40px; 
}
/* 🚨 RE-ASIGNAR las áreas dentro del grid para que los elementos floten */
.grid-item-cards {
    /* La fila de las 4 tarjetas debe ocupar las 5 partes del ancho */
    grid-column: 1 / span 2; 
}

.grid-item-metrics {
    /* Estado del Sistema (ocupa 2/5 del ancho total) */
    grid-column: 1 / 2;
}

.grid-item-activity {
    /* Actividad Reciente (ocupa 3/5 del ancho total) */
    grid-column: 2 / 3;
}

/* Modificamos la distribución de los módulos inferiores si es necesario, 
   pero el error es en las variables. */

// ----------------------------------------
// ESTILOS DE MÓDULOS INFERIORES (TEMPORAL)
// ----------------------------------------
.modulo-estado {
    background-color: $BLUE-MIDNIGHT; 
    color: $LIGHT-TEXT; // 👈 Ahora usa la variable definida arriba
    padding: 25px;
    height: 300px;
    border-radius: 15px;
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.5);
}

.modulo-actividad {
    background-color: #fff;
    color: $DARK-TEXT;
    padding: 25px;
    height: 300px;
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}


// ----------------------------------------
// TEMAS (Para el fondo de la página)
// ----------------------------------------

// 🚨 1. MODO CLARO (theme-light) - Debe sobrescribir el oscuro si existe
.theme-light {
  background-color: $WHITE-SOFT; 
  .plataforma-contenido {
    background-color: $WHITE-SOFT;
  }
}

// 🚨 2. MODO OSCURO (theme-dark) - Aplicar solo si isDark = true
.theme-dark {
  background-color: $DARK-BG-CONTRAST;
  .plataforma-contenido {
    background-color: $DARK-BG-CONTRAST;
  }
}
</style>