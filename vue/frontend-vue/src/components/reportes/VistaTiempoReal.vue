<template>
  <div class="plataforma-layout" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    <BarraLateralPlataforma :is-open="isSidebarOpen" />
    
    <div class="plataforma-contenido" :class="{ 'shifted': isSidebarOpen }">
      <EncabezadoPlataforma 
        titulo="Monitor en Tiempo Real"
        subtitulo="Visualización de datos cada 5 segundos (una vez seleccionado el dispositivo y campos)"
        @toggle-sidebar="toggleSidebar" 
        :is-sidebar-open="isSidebarOpen"
      />

      <div class="reportes-contenido"> <div class="selector-container" :class="{ 'theme-dark': isDark }">
          <div class="form-group">
            <label>1. Seleccione un Proyecto:</label>
            <select v-model="proyectoSeleccionadoId" @change="cargarDispositivos" class="form-control">
              <option :value="null" disabled>
                {{ loadingProyectos ? 'Cargando proyectos...' : 'Seleccione un proyecto' }}
              </option>
              <option v-for="p in proyectos" :key="p.id" :value="p.id">{{ p.nombre }}</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>2. Seleccione un Dispositivo:</label>
            <select v-model="dispositivoSeleccionadoId" @change="cargarCampos" class="form-control" :disabled="!proyectoSeleccionadoId || loadingDispositivos">
              <option :value="null" disabled>
                {{ loadingDispositivos ? 'Cargando...' : 'Seleccione un proyecto' }}
              </option>
              <option v-for="d in dispositivos" :key="d.id" :value="d.id">{{ d.nombre }}</option>
            </select>
          </div>
        </div>
         
        
        <div class="campo-selector-container" :class="{ 'theme-dark': isDark }" v-if="campos.length > 0">
            <h4 class="selector-titulo">3. Seleccione los campos a graficar (1 o más)</h4>
            <div v-if="loadingCampos" class="loading-message">Cargando campos...</div>
            <div class="checkbox-grid">
                <div v-for="c in campos" :key="c.id" class="checkbox-item">
                    <input type="checkbox" :id="'campo-' + c.id" :value="c.id" v-model="camposSeleccionadosIds">
                    
                    <label :for="'campo-' + c.id">
                        <i :class="getIcon(c.magnitud_tipo)"></i> {{ c.nombre }} ({{ c.simbolo_unidad || 'N/A' }}) </label>

                </div>
            </div>
        </div>
        


        <div v-if="loadingCampos" class="alert-info">Cargando campos del dispositivo...</div>
        <div v-else-if="errorCampos" class="alert-error">{{ errorCampos }}</div>
        
       <div class="charts-grid-realtime" v-if="camposFiltrados.length > 0">
            <GraficoEnTiempoReal
                v-for="campo in camposFiltrados"
                :key="campo.id"
                :campo-id="campo.id"
                :titulo="campo.nombre"
                :is-dark="isDark"
                :simbolo-unidad="campo.simbolo_unidad || 'N/A' "
            />  
            </div>
                
        <div v-if="!loadingCampos && dispositivoSeleccionadoId && campos.length === 0" class="alert-empty-data">
          Este dispositivo no tiene campos de medición registrados.
        </div>
        
      </div>
    </div>
  </div>
</template>

<script>
// Componentes de Layout
import BarraLateralPlataforma from '../plataforma/BarraLateralPlataforma.vue';
import EncabezadoPlataforma from '../plataforma/EncabezadoPlataforma.vue';
// Componente hijo (El que hicimos en el prompt anterior)
import GraficoEnTiempoReal from '../graficos/GraficoEnTiempoReal.vue'; 


export default {
  name: 'VistaTiempoReal',
  components: {
    BarraLateralPlataforma,
    EncabezadoPlataforma,
    GraficoEnTiempoReal
  },
  data() {
    return {
      isDark: false, 
      isSidebarOpen: true, 
      proyectos: [],
      dispositivos: [],
      campos: [], // Todos los campos disponibles
      camposSeleccionadosIds: [], // 👈 AÑADIDO: Array para checkboxes
      proyectoSeleccionadoId: null,
      dispositivoSeleccionadoId: null,

      loadingProyectos: true,
      loadingDispositivos: false,
      loadingCampos: false,
      errorCampos: null,
      error: null,
    };
  },
  computed: {
    camposFiltrados() {
      return this.campos.filter(c => this.camposSeleccionadosIds.includes(c.id));
    }
  },
  mounted() {
    this.cargarProyectos();
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
    // --- Carga de Dropdowns (Exactamente igual a VistaReportes) ---
    async cargarProyectos() {
      this.loadingProyectos = true;
      this.error = null;
      const token = localStorage.getItem('accessToken');
      let usuarioId = null;
      const resultadoString = localStorage.getItem('resultado');
      
      if (resultadoString) {
        const resultado = JSON.parse(resultadoString);
        if (resultado && resultado.usuario && resultado.usuario.id) {
          usuarioId = resultado.usuario.id;
        }
      }
      if (!token || !usuarioId) { 
        this.error = "Error de autenticación. No se pudo encontrar el ID de usuario.";
        this.loadingProyectos = false;
        this.$router.push('/');
        return; 
      }

      try {
        const response = await fetch(`${API_BASE_URL}/api/proyectos/usuario/${usuarioId}`, { 
          headers: { 'Authorization': `Bearer ${token}` } 
        });
        if (response.status === 404) { this.proyectos = []; }
        if (!response.ok) { throw new Error('Fallo al cargar proyectos.'); }
        
        this.proyectos = await response.json();
        
        if (this.proyectos.length > 0) {
          this.proyectoSeleccionadoId = this.proyectos[0].id;
          await this.cargarDispositivos(); 
        }
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loadingProyectos = false;
      }
    },

    async cargarDispositivos() {
      this.loadingDispositivos = true;
      this.dispositivos = []; 
      this.campos = [];
      this.dispositivoSeleccionadoId = null;
      
      const token = localStorage.getItem('accessToken');
      if (!this.proyectoSeleccionadoId || !token) {
        this.loadingDispositivos = false;
        return;
      }
      
      try {
        const response = await fetch(`${API_BASE_URL}/api/dispositivos/proyecto/${this.proyectoSeleccionadoId}`, { 
          headers: { 'Authorization': `Bearer ${token}` } 
        });
        if (response.status === 404) { this.dispositivos = []; } 
        else if (response.ok) { this.dispositivos = await response.json(); }
        
        if (this.dispositivos.length > 0) {
          this.dispositivoSeleccionadoId = this.dispositivos[0].id;
          await this.cargarCampos(); 
        }
      } catch (err) {
        console.error(err);
      } finally {
        this.loadingDispositivos = false;
      }
    },
    
    // Carga la lista de campos (Idéntico a VistaReportes)
    async cargarCampos() {
      this.loadingCampos = true;
      this.errorCampos = null;
      this.campos = [];
      
      const token = localStorage.getItem('accessToken');
      if (!this.dispositivoSeleccionadoId || !token) {
        this.loadingCampos = false;
         return; 
      }

      try {
        const sensoresResponse = await fetch(`${API_BASE_URL}/api/sensores/dispositivo/${this.dispositivoSeleccionadoId}`, { 
          headers: { 'Authorization': `Bearer ${token}` } 
        });
        if (sensoresResponse.status === 404) { this.campos = []; this.loadingCampos = false; return; }
        
        const sensores = await sensoresResponse.json();
        let todosLosCampos = [];

        for (const sensor of sensores) {
          const camposResponse = await fetch(`${API_BASE_URL}/api/sensores/${sensor.id}/campos`, { 
            headers: { 'Authorization': `Bearer ${token}` } 
          });
          
          if (camposResponse.ok) {
            const camposData = await camposResponse.json();
            todosLosCampos.push(...camposData); 
          }
        }
        this.campos = todosLosCampos; 
        
      } catch (err) {
        console.error("Error al cargar campos:", err);
        this.errorCampos = 'Error al cargar los campos del dispositivo.';
      } finally {
        this.loadingCampos = false;
      }
    },
       getIcon(magnitudTipo) {
            if (!magnitudTipo) return 'bi bi-question-lg';
            const lowerMag = magnitudTipo.toLowerCase();
            
            if (lowerMag.includes('temperatura')) return 'bi bi-thermometer-half';
            if (lowerMag.includes('humedad')) return 'bi bi-droplet-half';
            if (lowerMag.includes('electricidad')) return 'bi bi-lightning-charge-fill';
            if (lowerMag.includes('potencia')) return 'bi bi-lightning';
            if (lowerMag.includes('energía')) return 'bi bi-battery-charging';
            if (lowerMag.includes('iluminación')) return 'bi bi-sun';
            if (lowerMag.includes('movimiento')) return 'bi bi-person-walking';
            
            return 'bi bi-speedometer2'; 
        },    
    // --- Layout y Tema ---
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
/* Reutilizamos los estilos de VistaReportes */

.reportes-contenido {
    padding: 0 40px 40px 40px;
}
.campo-selector-container {
    background-color: #FFFFFF; /* Fondo claro por defecto */
    padding: 20px 25px;
    border-radius: 12px;
    margin-bottom: 30px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    
    .selector-titulo {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 15px;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
    }
}
.selector-container {
    display: grid;
    /* 2 columnas (Proyecto y Dispositivo) */
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
    gap: 20px;
    padding: 25px; 
    border-radius: 12px;
    margin-bottom: 30px;
    transition: background-color 0.3s;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
.form-group {
    label { 
        font-weight: 600; 
        margin-bottom: 8px; 
        display: block; 
    }
    .form-control {
        width: 100%;
        padding: 10px 15px;
        border-radius: 8px;
        font-size: 1rem;
    }
}

.charts-grid-realtime {
    display: grid;
    /* 2 gráficos por fila */
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
}

/* ----------------------------------------
   TEMAS
   ---------------------------------------- */

/* TEMA CLARO */
.theme-light {
    background-color: $WHITE-SOFT; /* Fondo de la página */
    .selector-container {
        background-color: $SUBTLE-BG-LIGHT;
        color: $DARK-TEXT;
    }
    .form-control {
        background-color: $SUBTLE-BG-LIGHT;
        color: $DARK-TEXT;
        border: 1px solid #ccc;
    }
}

/* TEMA OSCURO */
.theme-dark {
    /* 🚨 CRÍTICO: Aplicar el fondo principal a toda el área de contenido */
    background-color: $DARK-BG-CONTRAST; 
    color: $LIGHT-TEXT;

    .plataforma-contenido {
        /* Asegura que el contenido también use el fondo principal */
        background-color: $DARK-BG-CONTRAST;
    }
    :global(.user-profile-card) { 
        background-color: $SUBTLE-BG-DARK !important;
        color: $LIGHT-TEXT !important;
        box-shadow: none;
    }
    .selector-container {
        background-color: $SUBTLE-BG-DARK; 
        color: $LIGHT-TEXT;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);

        .form-group label {
            color: $LIGHT-TEXT; 
        }
        
        .form-control {
            background-color: $BLUE-MIDNIGHT; 
            color: $LIGHT-TEXT;
            border: 1px solid rgba($LIGHT-TEXT, 0.2); 
            /* Reajustar la flecha para el modo oscuro */
            background-image: url('data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2212%22%20height%3D%2212%22%20viewBox%3D%220%200%2012%2012%22%3E%3Cpath%20fill%3D%22%23{$LIGHT-TEXT}%22%20d%3D%22M6%209L0%203h12z%22%2F%3E%3C%2Fsvg%3E');
        }
        .loading-message, .no-data-message {
            color: $GRAY-COLD;
        }
    }
}
/* ... (Importa tus estilos de tema .theme-dark y .theme-light) ... */
</style>