<template>
  <div class="plataforma-layout" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">

    <BarraLateralPlataforma :is-open="isSidebarOpen" />

    <div class="plataforma-contenido" :class="{ 'shifted': isSidebarOpen }">

      <EncabezadoPlataforma
        titulo="Gestión de Datos Energéticos"
        subtitulo="Carga y selecciona tus conjuntos de datos de consumo eléctrico (lotes) para analizarlos."
        @toggle-sidebar="toggleSidebar"
        :is-sidebar-open="isSidebarOpen"
      />

      <div class="gestion-datos-contenido">
        
        <div class="gestion-grid">
          
          <div class="gestion-panel">
            <h2 class="panel-titulo">
              <i class="bi bi-cloud-upload-fill"></i>
              Cargar Lote de Datos (CSV)
            </h2>

            <div v-if="mensajeCarga" :class="['mensaje-carga', tipoMensajeCarga === 'success' ? 'mensaje-exito' : 'mensaje-error']">
              <i :class="tipoMensajeCarga === 'success' ? 'bi bi-check-circle-fill' : 'bi bi-exclamation-triangle-fill'"></i>
              {{ mensajeCarga }}
            </div>

            <div class="campo-lote-nombre">
              <label for="loteNombreInput">Nombre del Lote:</label>
              <div class="input-con-icono">
                <i class="bi bi-tag-fill"></i>
                <input
                  type="text"
                  id="loteNombreInput"
                  v-model="inputLoteNombre"
                  placeholder="Ej. Recibos Casa 2023"
                  class="input-lote"
                  :class="{'input-error': loteNombreVacio && !inputLoteNombre.trim()}"
                />
              </div>
              <p v-if="loteNombreVacio && !inputLoteNombre.trim()" class="error-texto">Por favor, ingresa un nombre para el lote.</p>
            </div>
            
            <label for="csvFile" class="boton-seleccionar-archivo">
              <i class="bi bi-file-earmark-spreadsheet-fill"></i>
              <span>{{ nombreArchivo || 'Seleccionar archivo CSV...' }}</span>
            </label>
            <input
              type="file"
              id="csvFile"
              ref="csvFileInput"
              @change="handleFileChange"
              accept=".csv"
              hidden
            />

            <p class="ayuda-texto-formato">
              Columnas requeridas: periodo, consumo_total_kwh, demanda_maxima_kw, costo_total, dias_facturados.
            </p>

            <button @click="subirCSV" :disabled="!archivoSeleccionado || isLoadingCarga || !inputLoteNombre.trim()" class="boton-cargar">
              <i class="bi bi-arrow-up-circle-fill"></i>
              {{ isLoadingCarga ? 'Cargando...' : 'Cargar y Procesar Datos' }}
            </button>
          </div>

          <div class="columna-derecha">
            
            <div class="gestion-panel seleccion-lotes-panel">
              <h2 class="panel-titulo">
                <i class="bi bi-check-square-fill"></i>
                Seleccionar Datos para Análisis
              </h2>

              <div v-if="isLoadingLotes" class="cargando-lotes">
                <div class="spinner"></div> Cargando lotes...
              </div>
              <div v-else-if="lotesDisponibles.length === 0" class="no-lotes">
                <i class="bi bi-info-circle-fill"></i> No tienes lotes de datos cargados.
              </div>
              
              <div v-else class="lista-lotes">
                <p class="ayuda-texto">Selecciona uno o más lotes para habilitar las herramientas:</p>
                <div
                  v-for="lote in lotesDisponibles"
                  :key="lote"
                  class="checkbox-lote"
                  @click="toggleLote(lote)"
                  :class="{ 'seleccionado': lotesSeleccionados.includes(lote) }"
                >
                  <i :class="lotesSeleccionados.includes(lote) ? 'bi bi-check-circle-fill' : 'bi bi-circle'"></i>
                  <label :for="`lote-${lote}`">{{ lote }}</label>
                  <input
            type="checkbox"
            :value="lote.nombre"
            v-model="lotesSeleccionadosNombres"
            :id="'lote-' + lote.id"
          />
                </div>
              </div>
              <div v-if="lotesError" class="mensaje-error">
                Error al cargar lotes: {{ lotesError }}
              </div>
            </div>

            <div class="gestion-panel herramientas-panel">
              <h2 class="panel-titulo">
                <i class="bi bi-tools"></i>
                Herramientas de Análisis
              </h2>
              
              <div v-if="lotesSeleccionados.length > 0" class="ayuda-texto-estado estado-ok">
                <i class="bi bi-check-circle-fill"></i>
                Lotes seleccionados. ¡Listo para analizar!
              </div>
              <div v-else class="ayuda-texto-estado estado-warn">
                 <i class="bi bi-exclamation-triangle-fill"></i>
                Selecciona al menos un lote de datos.
              </div>

              <div class="botones-herramientas">
                <!-- VistaSimuladorEnergetico -->
                <router-link :to="{ name: '', query: { lotes: lotesSeleccionados } }" custom v-slot="{ navigate }">
                  <button @click="navigate" :disabled="!lotesSeleccionados.length" class="boton-herramienta boton-primario">
                    <i class="bi bi-graph-up"></i>
                    Ir a Simulación de Escenario
                  </button>
                </router-link>
<!-- VistaResumenEstadistico -->
                <router-link :to="{ name: 'VistaResumenEstadistico', query: { lotes: lotesSeleccionados } }" custom v-slot="{ navigate }">
                  <button @click="navigate" :disabled="!lotesSeleccionados.length" class="boton-herramienta boton-secundario">
                    <i class="bi bi-clipboard-data-fill"></i>
                    Ver Análisis Descriptivo
                  </button>
                </router-link>
                
              </div>
            </div>
          </div> 
        </div> 
      </div> 
    </div>
   
  </div>
</template>

<script>
import BarraLateralPlataforma from '../plataforma/BarraLateralPlataforma.vue';
import EncabezadoPlataforma from '../plataforma/EncabezadoPlataforma.vue';



export default {
  name: 'VistaGestionDatosEnergeticos',
  components: {
    BarraLateralPlataforma,
    EncabezadoPlataforma,
  },
  data() {
    return {
      // Estado Layout y Tema
      isDark: false,
      isSidebarOpen: true,
      _themeMediaQuery: null,

      // Estado Carga CSV
      archivoSeleccionado: null,
      nombreArchivo: '',
      isLoadingCarga: false,
      mensajeCarga: '',
      tipoMensajeCarga: '', // 'success' o 'error'
      inputLoteNombre: '',
      loteNombreVacio: false,

      // Estado para la selección de lotes
      lotesDisponibles: [], 
      lotesSeleccionados: [], 
      isLoadingLotes: false,
      lotesError: null,
    };
  },
  mounted() {
    this.detectarTemaSistema();
    this._themeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    if (this._themeMediaQuery) {
      this._themeMediaQuery.addEventListener('change', this.handleThemeChange);
    }
    // 🎯 Llamar al endpoint GET /lotes_disponibles
    this.obtenerLotesUsuario();
  },
  unmounted() {
    if (this._themeMediaQuery) {
      this._themeMediaQuery.removeEventListener('change', this.handleThemeChange);
    }
  },
  methods: {
    // Métodos Layout y Tema
    toggleSidebar() { this.isSidebarOpen = !this.isSidebarOpen; },
    handleThemeChange(event) { this.isDark = event.matches; },
    detectarTemaSistema() {
       if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        this.isDark = true;
      } else {
        this.isDark = false;
      }
    },
    
    // --- Métodos de Carga CSV (POST /cargar-csv) ---
    handleFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        this.archivoSeleccionado = file;
        this.nombreArchivo = file.name;
        this.mensajeCarga = ''; 
        this.tipoMensajeCarga = '';
      } else {
        this.archivoSeleccionado = null;
        this.nombreArchivo = '';
      }
    },

    async subirCSV() {
      if (!this.inputLoteNombre.trim()) {
        this.mensajeCarga = "Por favor, ingresa un nombre para el conjunto de datos.";
        this.tipoMensajeCarga = 'error';
        this.loteNombreVacio = true;
        return;
      } else { this.loteNombreVacio = false; }

      if (!this.archivoSeleccionado) {
        this.mensajeCarga = "Por favor, selecciona un archivo CSV.";
        this.tipoMensajeCarga = 'error';
        return;
      }

      this.isLoadingCarga = true;
      this.mensajeCarga = '';
      this.tipoMensajeCarga = '';

      const token = localStorage.getItem('accessToken');
      if (!token) {
        this.mensajeCarga = "Error de autenticación. Inicia sesión.";
        this.tipoMensajeCarga = 'error';
        this.isLoadingCarga = false;
        this.$router.push('/');
        return;
      }

      const formData = new FormData();
      formData.append('file', this.archivoSeleccionado);
      formData.append('lote_nombre', this.inputLoteNombre.trim());

      const API_URL = `${API_BASE_URL}/api/energetico/cargar-csv`; // 🎯 Endpoint de carga

      try {
        const response = await fetch(API_URL, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        });

        const resultado = await response.json();

        if (response.ok) {
          this.mensajeCarga = resultado.message || "Datos cargados exitosamente.";
          this.tipoMensajeCarga = 'success';
          await this.obtenerLotesUsuario(); // Refrescar la lista de lotes
          this.archivoSeleccionado = null;
          this.nombreArchivo = '';
          this.inputLoteNombre = '';
          if (this.$refs.csvFileInput) { this.$refs.csvFileInput.value = null; }
        } else {
           if (response.status === 409) {
               this.mensajeCarga = resultado.detail || "Error: Ya existen datos para algunos periodos en el lote especificado.";
           } else if (response.status === 401 || response.status === 403) {
               localStorage.removeItem('accessToken'); this.$router.push('/');
               throw new Error("Token inválido o expirado.");
           } else {
               this.mensajeCarga = resultado.detail || `Error ${response.status} al cargar el archivo.`;
           }
           this.tipoMensajeCarga = 'error';
        }
      } catch (error) {
        console.error("Error al subir CSV:", error);
         if (!this.mensajeCarga) { this.mensajeCarga = error.message || "Error de red o conexión al subir el archivo."; }
        this.tipoMensajeCarga = 'error';
      } finally {
        this.isLoadingCarga = false;
      }
    },

    // --- Métodos de Lotes (GET /lotes_disponibles) ---
    async obtenerLotesUsuario() {
      this.isLoadingLotes = true;
      this.lotesDisponibles = [];
      this.lotesError = null;

      const token = localStorage.getItem('accessToken');
      if (!token) { this.lotesError = "No autenticado."; this.isLoadingLotes = false; return; }

      const API_URL = `${API_BASE_URL}/api/energetico/lotes_disponibles`; // 🎯 Endpoint de lotes disponibles

      try {
        const response = await fetch(API_URL, {
          method: 'GET',
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
          const data = await response.json(); // Data es directamente el array de strings
          this.lotesDisponibles = data; 
          this.cargarSeleccionLotesDesdeLocalStorage(); // Intenta restaurar selección previa
        } else if (response.status === 401 || response.status === 403) {
          localStorage.removeItem('accessToken'); this.$router.push('/'); this.lotesError = "Sesión expirada.";
        } else {
          const errorData = await response.json();
          this.lotesError = errorData.detail || `Error ${response.status} al obtener los lotes.`;
        }
      } catch (error) {
        console.error("Error de red al obtener lotes:", error);
        this.lotesError = "Error de conexión o red al obtener lotes.";
      } finally {
        this.isLoadingLotes = false;
      }
    },

    toggleLote(lote) {
      const index = this.lotesSeleccionados.indexOf(lote);
      if (index > -1) {
        this.lotesSeleccionados.splice(index, 1); // Quitar
      } else {
        this.lotesSeleccionados.push(lote); // Añadir
      }
    },

    guardarSeleccionLotes() {
      localStorage.setItem('selectedEnergyDataLotes', JSON.stringify(this.lotesSeleccionados));
    },

    cargarSeleccionLotesDesdeLocalStorage() {
      const storedLotes = localStorage.getItem('selectedEnergyDataLotes');
      if (storedLotes) {
        const parsedLotes = JSON.parse(storedLotes);
        this.lotesSeleccionados = parsedLotes.filter(lote => 
          this.lotesDisponibles.includes(lote)
        );
      }
    }
  },
  watch: {
    lotesSeleccionados: {
      handler() { this.guardarSeleccionLotes(); },
      deep: true
    },
    lotesDisponibles: {
      handler() { this.cargarSeleccionLotesDesdeLocalStorage(); },
      immediate: true
    }
  }
};
</script>


<style scoped lang="scss">
@use "sass:color";

.plataforma-layout { display: flex; min-height: 100vh; background-color: $WHITE-SOFT; }
.theme-dark .plataforma-layout { background-color: $DARK-BG-CONTRAST; }
.plataforma-contenido {
  margin-left: $WIDTH-CLOSED; flex-grow: 1;
  transition: margin-left 0.3s ease-in-out;
  background-color: $WHITE-SOFT;
  &.shifted { margin-left: $WIDTH-SIDEBAR; }
}
.theme-dark .plataforma-contenido { background-color: $DARK-BG-CONTRAST; }

/* Contenido de la Vista */
.gestion-datos-contenido {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

/* 🎯 NUEVO: Grid de 2 columnas */
.gestion-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;

  @media (min-width: 992px) {
    grid-template-columns: 4fr 6fr; /* 40% carga, 60% selección/herramientas */
  }
}

.columna-derecha {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Panel Base (Reutilizado) */
.gestion-panel {
  background-color: $SUBTLE-BG-LIGHT;
  padding: 1.5rem 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid $GRAY-LIGHT;
  transition: background-color 0.3s, border-color 0.3s;
}

.panel-titulo {
  font-size: 1.25rem;
  font-weight: 600;
  color: $DARK-TEXT;
  border-bottom: 1px solid $GRAY-LIGHT;
  padding-bottom: 1rem;
  margin-bottom: 1.5rem;
  transition: color 0.3s, border-color 0.3s;
  display: flex;
  align-items: center;
  gap: 0.75rem;

  i {
    color: $PRIMARY-PURPLE;
  }
}

/* Estilos Carga CSV */
.campo-lote-nombre {
  margin-bottom: 1.5rem;
  label {
    display: block;
    font-size: 0.9rem;
    color: $DARK-TEXT;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }
  
  .input-con-icono {
    position: relative;
    i {
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      color: $GRAY-COLD;
    }
    .input-lote {
      padding-left: 2.5rem;
    }
  }

  .input-lote {
    width: 100%;
    padding: 0.7rem 1rem;
    border: 1px solid $GRAY-LIGHT;
    border-radius: 8px;
    font-size: 0.95rem;
    color: $DARK-TEXT;
    background-color: $WHITE-SOFT;
    transition: border-color 0.2s, box-shadow 0.2s, background-color 0.3s;

    &:focus {
      border-color: $PRIMARY-PURPLE;
      box-shadow: 0 0 0 3px rgba($PRIMARY-PURPLE, 0.2);
      outline: none;
    }
    &::placeholder {
      color: $GRAY-COLD;
    }
    &.input-error {
      border-color: $DANGER-COLOR;
      box-shadow: 0 0 0 3px rgba($DANGER-COLOR, 0.2);
    }
  }
  .error-texto {
    font-size: 0.75rem;
    color: $DANGER-COLOR;
    margin-top: 0.5rem;
  }
}

.boton-seleccionar-archivo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background-color: $SUBTLE-BG-LIGHT;
  color: $PRIMARY-PURPLE;
  padding: 0.7rem 1.2rem;
  border-radius: 8px;
  border: 2px dashed $PRIMARY-PURPLE;
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;
  font-weight: 500;
  margin-bottom: 0.5rem;
  text-align: center;
  width: 100%;

  i { font-size: 1.1rem; }
  span { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

  &:hover {
    background-color: rgba($PRIMARY-PURPLE, 0.1);
    border-style: solid;
  }
}

.ayuda-texto-formato, .ayuda-texto-estado, .ayuda-texto {
  font-size: 0.8rem;
  color: $GRAY-COLD;
  margin-top: 0.5rem;
  margin-bottom: 1.5rem;
  line-height: 1.5;
  transition: color 0.3s;
}

.boton-cargar {
  width: 100%;
  padding: 0.8rem 1rem;
  font-weight: 700;
  font-size: 1rem;
  color: white;
  background: $GRADIENT-SUCCESS;
  border-radius: 8px;
  transition: all 0.2s;
  cursor: pointer;
  border: none;
  box-shadow: 0 4px 10px rgba($SUCCESS-COLOR, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;

  &:hover { 
    opacity: 0.9;
    box-shadow: 0 6px 12px rgba($SUCCESS-COLOR, 0.4);
    transform: translateY(-2px);
  }
  &:disabled {
    background: $GRAY-COLD;
    cursor: not-allowed;
    box-shadow: none;
    opacity: 0.7;
    transform: translateY(0);
  }
}

.mensaje-carga {
    padding: 0.8rem 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    font-weight: 500;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    &.mensaje-exito { background-color: rgba($SUCCESS-COLOR, 0.15); color: color.adjust($SUCCESS-COLOR, $lightness: -10%); }
    &.mensaje-error { background-color: rgba($DANGER-COLOR, 0.15); color: color.adjust($DANGER-COLOR, $lightness: -10%); }
}


/* Estilos Panel Selección de Lotes */
.seleccion-lotes-panel {
  .cargando-lotes, .no-lotes {
    text-align: center;
    font-style: italic;
    color: $GRAY-COLD;
    padding: 1rem 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    .spinner { 
      width: 1rem;
      height: 1rem;
      border: 2px solid $GRAY-COLD;
      border-top-color: $PRIMARY-PURPLE;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
  }
  .mensaje-error {
    color: $DANGER-COLOR;
    font-weight: 500;
    text-align: center;
  }

  .lista-lotes {
    margin-top: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    max-height: 200px;
    overflow-y: auto;

    .checkbox-lote {
      display: flex;
      align-items: center;
      padding: 0.75rem 1rem;
      border: 1px solid $GRAY-LIGHT;
      border-radius: 8px;
      background-color: $WHITE-SOFT;
      transition: background-color 0.2s, border-color 0.2s;
      cursor: pointer;

      &:hover {
        background-color: rgba($PRIMARY-PURPLE, 0.05);
        border-color: rgba($PRIMARY-PURPLE, 0.5);
      }
      
      &.seleccionado {
        background-color: rgba($PRIMARY-PURPLE, 0.1);
        border-color: $PRIMARY-PURPLE;
        font-weight: 600;
      }

      i { 
        font-size: 1.2rem;
        margin-right: 0.75rem;
        color: $GRAY-COLD;
        transition: color 0.2s;
      }
      
      &.seleccionado i {
        color: $PRIMARY-PURPLE;
      }
      
      input[type="checkbox"] { display: none; }

      label {
        flex-grow: 1;
        font-size: 0.95rem;
        color: $DARK-TEXT;
        cursor: pointer;
        transition: color 0.3s;
      }
    }
  }
}


/* Estilos Panel Herramientas */
.ayuda-texto-estado {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  &.estado-ok {
    color: $SUCCESS-COLOR;
  }
  &.estado-warn {
    color: $WARNING-COLOR;
  }
}

.botones-herramientas {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.boton-herramienta {
  width: 100%;
  padding: 0.8rem 1rem;
  font-weight: 600;
  color: white; /* Color primario para botones */
  background-color: $PRIMARY-PURPLE; /* Color base */
  border: 2px solid $PRIMARY-PURPLE;
  border-radius: 8px;
  transition: all 0.2s;
  cursor: pointer;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.95rem;

  i {
    font-size: 1.1rem;
  }
  
  // 🎯 BOTÓN PRIMARIO (Simulador)
  &.boton-primario { 
    background-color: $PRIMARY-PURPLE;
    color: $WHITE;
  }

  // 🎯 BOTÓN SECUNDARIO (Análisis Descriptivo)
  &.boton-secundario {
    background-color: $SUBTLE-BG-LIGHT;
    color: $PRIMARY-PURPLE;
    border: 2px solid $PRIMARY-PURPLE;
  }

  &:hover:not(:disabled) {
    background-color: color.adjust($PRIMARY-PURPLE, $lightness: -5%);
    box-shadow: 0 4px 10px rgba($PRIMARY-PURPLE, 0.3);
    transform: translateY(-2px);
  }

  &:disabled {
    border-color: $GRAY-COLD;
    color: $GRAY-COLD;
    background-color: $SUBTLE-BG-LIGHT;
    cursor: not-allowed;
    opacity: 0.6;
     &:hover { transform: none; box-shadow: none; }
  }
}

/* --- THEME DARK OVERRIDES --- */
.theme-dark {
  .gestion-panel {
    background-color: $SUBTLE-BG-DARK;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    border-color: $DARK-BORDER;
  }
  .panel-titulo { color: $LIGHT-TEXT; border-color: rgba($LIGHT-TEXT, 0.15); }
  
  .campo-lote-nombre {
    label { color: $LIGHT-TEXT; }
    .input-con-icono i { color: $GRAY-LIGHT; }
    .input-lote {
      border-color: $DARK-BORDER;
      color: $LIGHT-TEXT;
      background-color: $DARK-INPUT-BG;
    }
  }

  .boton-seleccionar-archivo {
    background-color: rgba($PRIMARY-PURPLE, 0.1);
    color: color.adjust($PRIMARY-PURPLE, $lightness: 20%);
    border-color: rgba(color.adjust($PRIMARY-PURPLE, $lightness: 20%), 0.5);
     &:hover { background-color: rgba(color.adjust($PRIMARY-PURPLE, $lightness: 20%), 0.2); }
  }

  .ayuda-texto-formato, .ayuda-texto-estado, .ayuda-texto { color: $GRAY-COLD; }

  .boton-cargar {
    &:disabled { 
       background: color.adjust($GRAY-COLD, $lightness: 10%); 
       color: $LIGHT-TEXT;
    }
  }

  /* Lotes & Checkbox */
  .seleccion-lotes-panel {
    .cargando-lotes, .no-lotes { color: $GRAY-LIGHT; }
    .lista-lotes .checkbox-lote {
      border-color: $DARK-BORDER;
      background-color: $DARK-INPUT-BG;
      label { color: $LIGHT-TEXT; }
    }
  }

  .boton-herramienta {
      &.boton-primario { /* Simulador */
        background-color: color.adjust($PRIMARY-PURPLE, $lightness: 20%);
        color: $DARK-BG-CONTRAST;
      }
      &.boton-secundario { /* Análisis Descriptivo */
        background-color: transparent;
        color: color.adjust($PRIMARY-PURPLE, $lightness: 20%);
        border-color: color.adjust($PRIMARY-PURPLE, $lightness: 20%);
      }
       &:hover:not(:disabled) {
          background-color: color.adjust($PRIMARY-PURPLE, $lightness: 25%);
          color: $DARK-TEXT;
       }
  }
  
  .mensaje-carga {
      &.mensaje-exito { background-color: rgba($SUCCESS-COLOR, 0.2); color: color.adjust($SUCCESS-COLOR, $lightness: 20%); }
      &.mensaje-error { background-color: rgba($DANGER-COLOR, 0.2); color: color.adjust($DANGER-COLOR, $lightness: 20%); }
  }

}

/* Animaciones */
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>