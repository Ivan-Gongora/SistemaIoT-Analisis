<template>
  <div class="plataforma-layout" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    
    <BarraLateralPlataforma :is-open="isSidebarOpen" />
    
    <div class="plataforma-contenido" :class="{ 'shifted': isSidebarOpen }">
      
      <EncabezadoPlataforma 
        titulo="Mis Proyectos" 
        subtitulo="Gestión de todos tus ecosistemas IoT"
        @toggle-sidebar="toggleSidebar" 
        :is-sidebar-open="isSidebarOpen"
      />
      
      <div class="vista-proyectos-contenido">
        <MisProyectos :is-dark="isDark"/> 
      </div>
      
    </div>
  </div>
</template>

<script>
// Ajusta las rutas según donde tengas tus archivos de plataforma
import BarraLateralPlataforma from '../plataforma/BarraLateralPlataforma.vue';
import EncabezadoPlataforma from '../plataforma/EncabezadoPlataforma.vue';
import MisProyectos from '../proyecto/MisProyectos.vue'; 

export default {
  name: 'VistaMisProyectos',
  components: {
    BarraLateralPlataforma,
    EncabezadoPlataforma,
    MisProyectos
  },
  data() {
    return {
      isDark: false,
      isSidebarOpen: true, 
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


.vista-proyectos-contenido {
    padding: 0 40px 40px 40px; 
}

// Estilos de tema para el fondo
.theme-light { background-color: $WHITE-SOFT; }
.theme-dark { background-color: $DARK-BG-CONTRAST; }
</style>