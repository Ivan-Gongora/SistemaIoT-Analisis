<template>
  <div class="sidebar-plataforma" :class="{ 'theme-dark': isDark, 'theme-light': !isDark, 'closed': !isOpen }">
    
    <div class="logo-container" @click="redirigirAPlataforma" style="cursor: pointer;">
      <div class="logo-icon">⚡</div>
      <div class="logo-text" v-if="isOpen"> <h1 class="mb-0">IoT Central</h1>
        <p class="mb-0">Centro Tecnológico QROo</p>
      </div>
    </div>
    
    <div class="usuario-perfil" v-if="isOpen"> 
      <div class="avatar-container">
        <i class="bi bi-person-circle"></i>
      </div>
      <div class="info-texto">
        <p class="nombre">{{ nombre || 'Usuario' }}</p>
        <p class="rol">{{ tipo_usuario || 'Invitado' }}</p>
      </div>
    </div>
    <div class="usuario-perfil-closed" v-else>
        <div class="avatar-container-closed">
            <i class="bi bi-person-circle"></i>
        </div>
    </div>


    <h6 class="nav-heading" v-if="isOpen">NAVEGACIÓN</h6> 
    <div class="menu-navegacion">
      <ul class="nav flex-column">
        
        <li class="nav-item">
          <router-link to="/plataforma" class="nav-link gradient-link" exact-active-class="active" title="Panel de Control">
            <i class="bi bi-grid-fill icon-space"></i> 
            <span v-if="isOpen">Panel de Control</span>
            <span v-else class="tooltip-text">Panel de Control</span>
          </router-link>
        </li>
        
        <li class="nav-item" v-for="item in menuItems" :key="item.path">
          <router-link :to="item.path" class="nav-link" active-class="active-sub" :title="item.label">
            <i :class="item.icon" class="icon-space"></i> 
            <span v-if="isOpen">{{ item.label }}</span> 
            <span v-else class="tooltip-text">{{ item.label }}</span>
          </router-link>
        </li>
      </ul>
    </div>
    
    <div class="configuracion-inferior mt-auto">
      <hr class="divider">
      
      <router-link to="/configuracion" class="nav-link-bottom" title="Configuración">
        <i class="bi bi-gear-fill icon-space"></i> 
        <span v-if="isOpen">Configuración</span> 
        <span v-else class="tooltip-text">Configuración</span>
      </router-link>
      
      <a href="#" @click.prevent="cerrarSesion" class="nav-link-bottom" title="Cerrar Sesión">
        <i class="bi bi-box-arrow-right icon-space"></i> 
        <span v-if="isOpen">Cerrar Sesión</span> 
        <span v-else class="tooltip-text">Cerrar Sesión</span>
      </a>
    </div>
  </div>
</template>

<script>
// Asegúrate de que Font Awesome (u otro ícono pack) esté incluido en tu proyecto
export default {
  name: 'BarraLateralPlataforma',
  props: {
    isOpen: { 
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      // Estado para la detección de modo oscuro
      isDark: false, 
      
      nombre: '',
      tipo_usuario: '', // Usaremos tipo_usuario directamente
      
    // 🚨 ÍCONOS CORREGIDOS A BOOTSTRAP ICONS (bi bi-...)
      menuItems: [
                // Grupo 1: Administración y Gestión
                { path: '/mis-proyectos', label: 'Mis Proyectos', icon: 'bi bi-folder-fill' }, 
                { path: '/dispositivos', label: 'Dispositivos', icon: 'bi bi-tablet-fill' }, 
                { path: '/sensores', label: 'Sensores', icon: 'bi bi-graph-up' }, 
                { path: '/unidades', label: 'Unidades de Medida', icon: 'bi bi-rulers' }, 
                
                // 🚨 SEPARADOR VIRTUAL (Para agrupar Análisis)
                // Se usa una ruta vacía o un elemento sin etiqueta para crear una separación visual
                { path: '', label: '', icon: 'divider-space' }, 

                // Grupo 2: Análisis y Reportes
                // Datos Históricos (Tu vista actual de reportes)
                {path: '/tiempo-real', label: 'Datos en Tiempo Real', icon: 'bi bi-clock-history' },

                { path: '/reportes', label: 'Datos Históricos', icon: 'bi bi-bar-chart-line-fill' }, 

                {path: '/menu-gestion-datos-energeticos', label: 'Gestión de Datos Energéticos', icon: 'bi bi-lightning-fill' },
                 
                // Análisis Avanzado
                { path: '/analisis', label: 'Análisis Avanzado', icon: 'bi bi-funnel-fill' }, 
                
                // Predicción de Gastos (Función Gemini)
                { path: '/prediccion-gastos', label: 'Predicción de Gastos', icon: 'bi bi-robot' }, 

                 // Reportes Generados
                { path: '/reportes-generados', label: 'Reportes Generados', icon: 'bi bi-file-earmark-bar-graph' }, 
            ]
    };
  },
  mounted() {
    // 1. Cargar datos del usuario
    const resultado = JSON.parse(localStorage.getItem('resultado'));
    if (resultado && resultado.usuario) {
      this.nombre = resultado.usuario.nombre + ' ' + resultado.usuario.apellido;
      this.tipo_usuario = resultado.usuario.tipo_usuario; // Asumo que este campo existe en el usuario
    }
    
    // 2. Inicializar la detección de tema
    this.detectarTemaSistema();
    
    // 3. Añadir listener para cambios de tema
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', this.handleThemeChange);
    }
  },
   beforeUnmount() { // 👈 CORRECCIÓN A beforeUnmount
    // Limpiar el listener al destruir el componente
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', this.handleThemeChange);
    }
  },
  methods: {
    redirigirAPlataforma() {
      this.$router.push('/plataforma');
    },
    cerrarSesion() {
      // Lógica de logout: Eliminar token/datos y redirigir
      localStorage.removeItem('accessToken'); // O 'currentUser', o 'resultado'
      this.$router.push('/');
    },
    handleThemeChange(event) {
      this.isDark = event.matches;
    },
    detectarTemaSistema() {
      // Detección inicial
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
// VARIABLES DE LA PALETA "IoT SPECTRUM"
// ----------------------------------------
// $PRIMARY-PURPLE: #8A2BE2; // Azul Violeta
// $ACCENT-COLOR: #7B1FA2;  // Morado para iconos y acentos sutiles

// // GRADIENTE PRINCIPAL (Panel de Control)
// $GRADIENT: linear-gradient(to right, #6F00FF, #A300FF);

// // COLORES BASE
// $WHITE-SOFT: #F7F9FC;  // Fondo Claro
// $BLUE-MIDNIGHT: #1A1A2E; // Fondo Oscuro de la barra
// $DARK-TEXT: #333333; // Texto en Modo Claro
// $LIGHT-TEXT: #E4E6EB;  // Texto en Modo Oscuro
// $SUBTLE-BG-DARK: #2B2B40; // Fondo sutil para Modo Oscuro (tarjeta de perfil)
// $SUBTLE-BG-LIGHT: #FFFFFF; // Fondo sutil para Modo Claro (tarjeta de perfil)
// $GRAY-COLD: #99A2AD; // Subtítulos y divisores en modo oscuro
// $GRAY-DIVIDER-LIGHT: #ddd; // Divisores en modo claro
// $WIDTH-SIDEBAR: 280px; 
// $WIDTH-CLOSED: 80px; // Ancho para modo colapsado

// ----------------------------------------
// ESTRUCTURA BASE
// ----------------------------------------
.sidebar-plataforma {
    width: $WIDTH-SIDEBAR;
    height: 100vh;
    position: fixed; 
    top: 0;
    left: 0;
    padding: 25px 20px;
    background-color: $WHITE-SOFT; 
    transition: width 0.3s ease-in-out, background-color 0.3s, color 0.3s;
    overflow-y: auto; 
    overflow-x: hidden; /* CRÍTICO: Evitar barra de scroll horizontal */
    z-index: 1000;
    box-sizing: border-box;
     /* Estilo para Webkit (Chrome, Safari, Edge) */
    &::-webkit-scrollbar {
        width: 0px; /* Ancho de la barra (0 para ocultar) */
        background: transparent; /* Hace el fondo transparente */
    }

    /* Estilo para la "pista" de la barra (opcional pero ayuda a anular) */
    &::-webkit-scrollbar-track {
        background: transparent;
    }
    
    /* Estilo para Firefox (Experimental en CSS estándar) */
    scrollbar-width: none; /* 'none' oculta, 'thin' la hace delgada */
    // 🚨 ESTADO CERRADO/COLAPSADO
    &.closed {
        width: $WIDTH-CLOSED;
        padding: 25px 0; /* Ajustar padding lateral */
        
        span { opacity: 0; transition: opacity 0.1s; }
        
        // Centralizar todos los elementos en el estado cerrado
        .nav-link, .nav-link-bottom, .usuario-perfil-closed {
             justify-content: center;
             align-items: center;
        }
    }
}

// ----------------------------------------
// LOGO Y PERFIL
// ----------------------------------------
.logo-container {
    display: flex;
    align-items: center;
    margin-bottom: 40px;
    cursor: pointer;
    
    .logo-icon {
        font-size: 30px;
        margin-right: 10px;
        color: $PRIMARY-PURPLE; 
        padding: 5px 8px; 
        border-radius: 8px;
        background: $GRADIENT;
        color: $SUBTLE-BG-LIGHT;
        box-shadow: 0 4px 8px rgba(138, 43, 226, 0.4);
    }
    .logo-text {
        h1 {
            font-size: 1.25rem;
            font-weight: 700;
            line-height: 1.2;
        }
        p {
            font-size: 0.8rem;
            margin-top: -3px;
        }
    }
}

.usuario-perfil { /* Tarjeta de perfil en estado ABIERTO */
    display: flex;
    align-items: center;
    padding: 15px;
    border-radius: 12px;
    width: 100%;
    margin-bottom: 30px;
    transition: background-color 0.3s;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);

    .avatar-container {
        width: 50px;
        height: 50px;
        margin-right: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        
        i {
            font-size: 30px;
            color: $PRIMARY-PURPLE;
            background-color: rgba($PRIMARY-PURPLE, 0.1); 
            border-radius: 50%;
            padding: 10px;
        }
    }
    .info-texto {
        .nombre {
            font-weight: 600;
            line-height: 1.2;
            margin: 0;
        }
        .rol {
            font-size: 0.8rem;
            margin: 0;
            opacity: 0.75;
        }
    }
}

.usuario-perfil-closed { /* Contenedor para el avatar en estado COLAPSADO */
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%; 
    height: 60px; 
    margin-bottom: 30px;
}
.avatar-container-closed { /* ESTILOS DEL AVATAR COLAPSADO */
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    
    i {
        font-size: 24px;
        color: $PRIMARY-PURPLE;
    }
}


// ----------------------------------------
// NAVEGACIÓN Y LINKS
// ----------------------------------------
.nav-heading { /* TÍTULO DE SECCIÓN */
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 10px 0;
    margin-left: 10px;
    margin-bottom: 5px;
}

.menu-navegacion {
    width: 100%;
    flex-grow: 1;

    .nav-item { margin-bottom: 5px; }

    .nav-link, .nav-link-bottom { /* ESTILO BASE DEL LINK */
        display: flex;
        align-items: center;
        padding: 10px 15px;
        border-radius: 8px;
        transition: background-color 0.2s, color 0.2s;
        text-decoration: none;
        font-weight: 500;
        margin-bottom: 5px;
        position: relative; 

        .icon-space {
            width: 25px; 
            margin-right: 10px;
            text-align: center;
            transition: margin-right 0.3s;
        }
        
        // Ajuste de margen para el estado colapsado
        .sidebar-plataforma.closed & .icon-space {
            margin-right: 0;
        }

        &.active-sub {
            font-weight: 600;
            color: $ACCENT-COLOR;
        }
        
        &.gradient-link { 
            color: #fff;
            background: $GRADIENT;
            box-shadow: 0 4px 10px rgba(138, 43, 226, 0.3); 
            font-weight: bold;
            
            &:hover { opacity: 0.95; }
            &.active { background: $GRADIENT; }
        }
    }
    
    // ESTILO CRÍTICO para el link activo
    .router-link-exact-active:not(.gradient-link),
    .active-sub.router-link-active {
        font-weight: 600;
        color: $ACCENT-COLOR;
    }

    // 🚨 TOOLTIP PARA ESTADO COLAPSADO
    .nav-link:hover:not(.gradient-link) {
        .sidebar-plataforma.closed &::after {
            content: attr(title); 
            position: absolute;
            left: $WIDTH-CLOSED + 5px; 
            top: 50%;
            transform: translateY(-50%);
            background-color: rgba($BLUE-MIDNIGHT, 0.95); 
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            z-index: 100;
            white-space: nowrap;
            pointer-events: none;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
        }
    }
}

.configuracion-inferior { /* ESTILOS DEL FOOTER */
    width: 100%;
    margin-top: auto; /* Empuja el footer hacia abajo */

    .divider {
        border: none;
        height: 1px;
        margin: 20px 0;
        opacity: 0.5;
    }

    .nav-link-bottom {
        display: flex;
        align-items: center;
        padding: 10px 15px;
        border-radius: 8px;
        text-decoration: none;
        margin-bottom: 5px;
        font-size: 0.95rem;

        .icon-space {
            width: 25px; 
            margin-right: 10px;
            text-align: center;
        }
    }
}

// ----------------------------------------
// TEMAS (Detección de Sistema Operativo)
// ----------------------------------------

// MODO OSCURO
.theme-dark {
    background-color: $BLUE-MIDNIGHT; 
    color: $LIGHT-TEXT;
    
    .nav-heading, .logo-text p { color: $GRAY-COLD; }
    .divider { border-color: #3e3e4f; }
    
    .usuario-perfil { background-color: $SUBTLE-BG-DARK; }

    .nav-link, .nav-link-bottom {
        color: $LIGHT-TEXT;
        &:hover { background-color: #3e3e4f; }
        
        &.active-sub {
            color: $LIGHT-TEXT; 
            background-color: rgba($PRIMARY-PURPLE, 0.2); 
        }
    }
    .nav-link:not(.gradient-link) i, .nav-link-bottom i {
        color: $GRAY-COLD;
    }
    
    .nav-link-bottom {
        color: $GRAY-COLD;
    }
}

// MODO CLARO
.theme-light {
    background-color: $WHITE-SOFT;
    color: $DARK-TEXT;
    box-shadow: 2px 0 5px rgba(0, 0, 0, 0.05);
    
    .usuario-perfil { background-color: $SUBTLE-BG-LIGHT; }

    .nav-link {
        color: $DARK-TEXT;
        &:hover { background-color: #eef1f6; }
        &.active-sub { color: $ACCENT-COLOR; }
    }
    .nav-link-bottom {
        color: $DARK-TEXT;
        &:hover { background-color: #eef1f6; }
    }
}
</style>