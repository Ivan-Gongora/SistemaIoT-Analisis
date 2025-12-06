<template>
  <div class="plataforma-layout" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    <BarraLateralPlataforma :is-open="isSidebarOpen" />
    <div class="plataforma-contenido" :class="{ 'shifted': isSidebarOpen }">
      <EncabezadoPlataforma
        titulo="Simulador Energético"
        subtitulo="Proyección de escenarios de consumo y costos energéticos institucionales."
        @toggle-sidebar="toggleSidebar"
        :is-sidebar-open="isSidebarOpen"
        :is-dark="isDark"
      />

      <div class="simulador-principal-contenido">

        <div v-if="lotesCargados && lotesCargados.length > 0" class="lotes-seleccionados-display">
          <i class="bi bi-stack"></i>
          <span class="lotes-titulo">Lotes en Simulación:</span>
          <span class="lotes-lista">{{ lotesCargados.join(', ') }}</span>
        </div>
        <div v-else class="lotes-seleccionados-display no-lotes">
            <i class="bi bi-info-circle-fill"></i> No se han seleccionado lotes de datos para simular.
            <router-link :to="{ name: 'MenuGestionDatosEnergeticos' }" class="boton-ir-gestion">
              Ir a Gestión de Datos
            </router-link>
        </div>

        <div class="simulador-grid">
          
          <div class="gestion-panel panel-controles">
            <h2 class="panel-titulo"><i class="bi bi-sliders"></i> Parámetros de Simulación</h2>

            <div class="control-grupo">
              <label for="meses">
                Horizontes (Meses): <span class="valor-resaltado">{{ meses }}</span>
              </label>
              <input type="range" id="meses" min="12" max="120" step="12" v-model.number="meses"/>
            </div>

            <div class="control-grupo">
              <label for="inflacion">
                Inflación Energética Anual: <span class="valor-resaltado">{{ formatPercent(simulacionParams.tasa_inflacion_energetica) }}</span>
              </label>
              <input type="range" id="inflacion" min="0" max="0.3" step="0.01" v-model.number="simulacionParams.tasa_inflacion_energetica"/>
            </div>

            <div class="control-grupo">
              <label for="crecimiento">
                Crecimiento Consumo Anual: <span class="valor-resaltado">{{ formatPercent(simulacionParams.tasa_crecimiento_consumo) }}</span>
              </label>
              <input type="range" id="crecimiento" min="-0.1" max="0.3" step="0.01" v-model.number="simulacionParams.tasa_crecimiento_consumo"/>
            </div>

            <div class="control-grupo">
              <label for="eficiencia">
                Reducción por Eficiencia: <span class="valor-resaltado">{{ formatPercent(simulacionParams.mejora_eficiencia_consumo) }}</span>
              </label>
              <input type="range" id="eficiencia" min="0" max="0.5" step="0.01" v-model.number="simulacionParams.mejora_eficiencia_consumo"/>
            </div>

            <button @click="ejecutarSimulacion" :disabled="isLoading || !lotesCargados || lotesCargados.length === 0" class="boton-simular">
              <i v-if="isLoading" class="bi bi-arrow-repeat spin"></i>
              <i v-else class="bi bi-play-circle-fill"></i>
              {{ isLoading ? 'Simulando...' : 'Ejecutar Simulación' }}
            </button>
          </div>

          <div class="columna-resultados">
            
            <div class="resumen-costos-grid">
              
              <div class="tarjeta-resumen tarjeta-base" 
                   title="Consumo total proyectado de energía si no se realizan cambios ni optimizaciones. Es el punto de referencia base.">
                <span class="titulo-resumen">Consumo Base ({{ meses }} m)</span>
                <p class="valor-grande">{{ formatKWH(simulacionResultado.total_consumo_base_kwh) }}</p>
              </div>

              <div class="tarjeta-resumen tarjeta-simulado" 
                   title="Consumo total proyectado de energía considerando el crecimiento y las mejoras de eficiencia que has configurado.">
                <span class="titulo-resumen">Consumo Simulado ({{ meses }} m)</span>
                <p class="valor-grande">{{ formatKWH(simulacionResultado.total_consumo_simulado_kwh) }}</p>
              </div>

              <div class="tarjeta-resumen tarjeta-variacion" 
                   :class="simulacionResultado.variacion_consumo_total_kwh <= 0 ? 'variacion-negativa' : 'variacion-positiva'"
                   title="Variación total de Consumo (kWh) estimada entre el escenario simulado y el escenario base.">
                <span class="titulo-resumen">Variación vs. Base (kWh)</span>
                <p class="valor-grande">
                    {{ formatKWH(simulacionResultado.variacion_consumo_total_kwh) }}
                </p>
                <span class="leyenda-variacion">
                    ({{ simulacionResultado.variacion_consumo_total_kwh <= 0 ? 'Reducción' : 'Aumento' }})
                </span>
              </div>
            </div>
            
            <div class="grafica-simulador-contenedor">
              <h3 class="panel-titulo">
                  Proyección de Consumo (kWh): Histórico y Simulado
                    <i class="bi bi-info-circle-fill info-icon"
                      data-bs-toggle="popover"
                      data-bs-trigger="hover focus"
                      data-bs-html="true"
                      data-bs-placement="top"
                      :data-bs-title="popoverTitle"
                      :data-bs-content="popoverContent">
                    </i>
              </h3>
              
              <GraficoSimulacionECharts
                v-if="fullChartData && fullChartData.datos_historicos_usados && fullChartData.predicciones_escenario"
                :chart-data="fullChartData"
                :is-dark="isDark"
              />
              <div v-else class="mensaje-placeholder">
                <i class="bi bi-bar-chart-fill"></i> 
                {{ isLoading ? 'Calculando proyección...' : 'Ajuste los parámetros y haga clic en "Ejecutar Simulación".' }}
              </div>
            </div>
          </div>
        </div>

        <div v-if="errorApi" class="alerta alerta-error mt-4">
          <i class="bi bi-exclamation-octagon-fill"></i>
          <strong>Error:</strong> {{ errorApi }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import BarraLateralPlataforma from '../plataforma/BarraLateralPlataforma.vue';
import EncabezadoPlataforma from '../plataforma/EncabezadoPlataforma.vue';
import GraficoSimulacionECharts from '../graficos/GraficoSimulacionECharts.vue';
import * as bootstrap from 'bootstrap';

// Asume que 'bootstrap' y 'API_BASE_URL' están disponibles globalmente.

export default {
  name: 'VistaSimuladorEnergetico',
  components: {
    BarraLateralPlataforma,
    EncabezadoPlataforma,
    GraficoSimulacionECharts,
  },
  data() {
    return {
      isDark: false,
      isSidebarOpen: true,
      
      lotesCargados: [], 
      
      meses: 24, 
      simulacionParams: {
        tasa_inflacion_energetica: 0.08,
        tasa_crecimiento_consumo: 0.05,
        mejora_eficiencia_consumo: 0.10
      },
      isLoading: false,
      simulacionResultado: { 
        // KPIs de Costo (para el resumen detallado o futuro uso)
        total_meses_simulados: 0,
        total_costo_base_mxn: 0,
        total_costo_simulado_mxn: 0,
        variacion_costo_total_mxn: 0,
        porcentaje_variacion: 0,
        // KPIs de Consumo (usados en el template)
        total_consumo_base_kwh: 0,
        total_consumo_simulado_kwh: 0,
        variacion_consumo_total_kwh: 0,
        
        parametros_escenario: {},
        lotes_simulados: [],
      },
      fullChartData: null, 
      errorApi: null,
      
      _themeMediaQuery: null,
      popoverTitle: "Análisis de Proyección de Consumo",
      popoverContent: `
        <p>Esta gráfica ilustra la evolución mensual de tu consumo energético (kWh) en un horizonte de tiempo.</p>
        <p>La línea <strong>Consumo Base</strong> (línea discontinua) muestra el consumo histórico **real** y su proyección futura sin aplicar mejoras.</p>
        <p>La línea <strong>Consumo Simulado</strong> (línea sólida) muestra el consumo esperado aplicando la reducción por eficiencia configurada.</p>
        <p>Una diferencia visible a la baja en la línea simulada respecto a la base indica una reducción efectiva del consumo proyectado.</p>
      `
    };
  },
  mounted() {
    this.initPopovers();
    this.detectarTemaSistema(); 
    this.cargarLotesDesdeUrl(); 
    if (window.matchMedia) {
      this._themeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      this._themeMediaQuery.addEventListener('change', this.handleThemeChange); 
    }
  },
  beforeUnmount() {
    if (this._themeMediaQuery) {
      this._themeMediaQuery.removeEventListener('change', this.handleThemeChange);
    }
  },
  methods: {
    // --- Métodos de Layout y Carga Inicial ---
    initPopovers() {
        const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
        
        // El operador spread ([...]) y map funcionan bien para inicializar Bootstrap Popovers
        [...popoverTriggerList].map(popoverTriggerEl => {
            if (bootstrap.Popover.getInstance(popoverTriggerEl)) {
                bootstrap.Popover.getInstance(popoverTriggerEl).dispose();
            }
            return new bootstrap.Popover(popoverTriggerEl);
        });
    },
    toggleSidebar() { this.isSidebarOpen = !this.isSidebarOpen; },
    
    // Método para manejar el cambio de tema del sistema
    handleThemeChange(event) { 
      this.isDark = event.matches; 
      // Forzar actualización de la gráfica si hay datos
      if(this.fullChartData) {
          this.fullChartData = { ...this.fullChartData };
      }
    },
    
    // Método para detectar el tema inicial
    detectarTemaSistema() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) { 
          this.isDark = true; 
        } else { 
          this.isDark = false; 
        }
    },
    
    // Método para cargar lotes desde la URL (query parameter)
    cargarLotesDesdeUrl() {
      const lotesQuery = this.$route.query.lotes;
      if (lotesQuery) {
        // Asegura que lotesCargados sea un array
        this.lotesCargados = Array.isArray(lotesQuery) ? lotesQuery : [lotesQuery];
      } else {
        this.lotesCargados = []; 
      }
    },
    
    // --- Métodos de Formato ---
    formatPercent(value) { return (value * 100).toFixed(1) + '%'; },
    formatCurrency(value) { 
        if (value === null || value === undefined) return '$0';
        const absValue = Math.abs(value);
        return `${value < 0 ? '-' : ''}${absValue.toLocaleString('es-MX', { style: 'currency', currency: 'MXN', minimumFractionDigits: 0 })}`;
    },
    // Formato para kWh
    formatKWH(value) {
        if (value === null || value === undefined) return '0 kWh';
        const absValue = Math.abs(value);
        const formatted = absValue.toLocaleString('es-MX', { maximumFractionDigits: 0 });
        return `${value < 0 ? '-' : ''}${formatted} kWh`;
    },
    
    // --- Lógica de Simulación ---
    async ejecutarSimulacion() {
      if (!this.lotesCargados || this.lotesCargados.length === 0) {
        this.errorApi = "Seleccione al menos un lote de datos para simular.";
        return;
      }
      
      this.isLoading = true;
      this.errorApi = null;
      this.fullChartData = null; 

      const token = localStorage.getItem('accessToken');
      if (!token) { this.errorApi = "Error de autenticación. Inicia sesión."; this.isLoading = false; this.$router.push('/'); return; }

      const API_URL = `${API_BASE_URL}/api/energetico/simular/escenario_personalizado`; 
      
      try {
        const payload = {
          tasa_inflacion_energetica: this.simulacionParams.tasa_inflacion_energetica,
          tasa_crecimiento_consumo: this.simulacionParams.tasa_crecimiento_consumo,
          mejora_eficiencia_consumo: this.simulacionParams.mejora_eficiencia_consumo,
          lotes_seleccionados: this.lotesCargados,
          meses_a_predecir: this.meses
        };

        const response = await fetch(API_URL, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        
        const resultado = await response.json();

        if (!response.ok || resultado.status !== 'success') {
          const detail = resultado.detail || resultado.error || "Fallo en el servicio de simulación.";
          throw new Error(detail);
        }
        
        const data = resultado.data;

        // --- CÁLCULO DE CONSUMOS TOTALES ---
        const historico = data.datos_historicos_usados || [];
        const proyeccion = data.predicciones_escenario || [];
        
        const totalConsumoReal = historico.reduce((sum, item) => sum + item.consumo_total_kwh, 0);
        const totalConsumoBaseProyectado = proyeccion.reduce((sum, item) => sum + item.consumo_base_kwh, 0);
        const totalConsumoSimuladoProyectado = proyeccion.reduce((sum, item) => sum + item.consumo_escenario_kwh, 0);
        
        const totalBase = totalConsumoReal + totalConsumoBaseProyectado;
        const totalSimulado = totalConsumoReal + totalConsumoSimuladoProyectado; 

        // 1. Actualizar Resumen KPI
        this.simulacionResultado = {
            ...data.resumen_simulacion,
            total_costo_base_mxn: data.resumen_simulacion.total_costo_base_mxn,
            total_costo_simulado_mxn: data.resumen_simulacion.total_costo_simulado_mxn,
            variacion_costo_total_mxn: data.resumen_simulacion.variacion_costo_total_mxn,
            
            total_consumo_base_kwh: totalBase,
            total_consumo_simulado_kwh: totalSimulado,
            variacion_consumo_total_kwh: totalSimulado - totalBase,
        }; 

        // 2. Asignar el objeto 'data' completo al prop de la gráfica
        this.fullChartData = data;

      } catch (error) {
        console.error("Error en la simulación:", error);
        this.errorApi = error.message || "Error al conectar con la API de simulación.";
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>

<style scoped lang="scss">
@use "sass:color";


/* -----------------------------------------------------------------
 * DEFINICIÓN DE VARIABLES CSS DEL TEMA (CRÍTICO PARA MODO OSCURO)
 * ----------------------------------------------------------------- */

// Estilos base para el layout principal, incluyendo el color de fondo del body.
.plataforma-layout {
  display: flex;
  min-height: 100vh;
  transition: background-color 0.3s ease; 
  background-color: $WHITE-SOFT; 

  &.theme-dark {
    /* Variables CSS personalizadas para el modo oscuro */
    --card-bg: #{$SUBTLE-BG-DARK};
    --card-border: #{$DARK-BORDER};
    --text-color-primary: #{$LIGHT-TEXT};
    --text-color-secondary: #{$GRAY-COLD};
    --color-heading: #{$LIGHT-TEXT}; 
    --input-bg: #{$DARK-INPUT-BG}; 
    background-color: $DARK-BG-CONTRAST; 
  }

  &.theme-light {
    /* Variables CSS personalizadas para el modo claro */
    --card-bg: #{$SUBTLE-BG-LIGHT};
    --card-border: #{$LIGHT-BORDER};
    --text-color-primary: #{$DARK-TEXT};
    --text-color-secondary: #{$GRAY-COLD};
    --color-heading: #{$DARK-TEXT}; 
    --input-bg: #{$LIGHT-INPUT-BG}; 
    background-color: $WHITE-SOFT; 
  }
}

.simulador-principal-contenido {
    padding: 2rem;
    max-width: 1600px; 
    margin: 0 auto;
}


/* ------------------------------------
 * LAYOUT GENERAL DE LA VISTA
 * ------------------------------------ */

.simulador-grid {
  /* MEJORA: Controles más estrechos para dar más espacio a la gráfica (350px) */
  display: grid;
  grid-template-columns: 350px 1fr; 
  gap: 2rem;
  margin-top: 1.5rem; 
}

/* ------------------------------------
 * DISPLAY DE LOTES SELECCIONADOS
 * ------------------------------------ */
.lotes-seleccionados-display {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background-color: var(--card-bg); 
  border: 1px solid var(--card-border); 
  border-radius: $border-radius;
  padding: 1rem 1.5rem;
  box-shadow: $box-shadow-sm;
  color: var(--text-color-primary); 
  font-size: 1.05rem;
  margin-bottom: 1rem; 

  &.no-lotes {
      background-color: rgba($WARNING-COLOR, 0.1);
      border-color: $WARNING-COLOR;
      color: $WARNING-COLOR;
      display: flex;
      justify-content: space-between;
      align-items: center;
  }

  i {
    color: $PRIMARY-PURPLE;
    font-size: 1.4rem;
  }
  .lotes-titulo {
    font-weight: 600;
  }
  .lotes-lista {
    font-weight: 400;
    color: var(--text-color-secondary); 
  }
}
.boton-ir-gestion {
    background-color: $PRIMARY-PURPLE;
    color: $WHITE;
    padding: 0.5rem 1rem;
    border-radius: $border-radius-sm;
    text-decoration: none;
    font-weight: 500;
    transition: background-color 0.2s ease;

    &:hover {
        background-color: color.adjust($PRIMARY-PURPLE, $lightness: -5%);
    }
}


/* ------------------------------------
 * PANELES Y CONTROLES
 * ------------------------------------ */
.gestion-panel {
  background-color: var(--card-bg); 
  border: 1px solid var(--card-border); 
  border-radius: $border-radius;
  box-shadow: $box-shadow-sm;
  padding: 1.5rem;
  height: fit-content;
}

.panel-controles .panel-titulo {
  color: var(--text-color-primary); 
  font-size: 1.3rem;
  font-weight: 600;
  border-bottom: 1px solid var(--card-border); 
  padding-bottom: 0.75rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  i {
      color: $PRIMARY-PURPLE;
      font-size: 1.5rem;
  }
}

.control-grupo {
  margin-bottom: 1.5rem;
  label {
    display: flex; 
    justify-content: space-between;
    font-weight: 500;
    margin-bottom: 0.5rem;
    color: var(--text-color-primary); 
    font-size: 0.95rem;
  }
  input[type="range"] {
    width: 100%;
    height: 8px; 
    background: var(--input-bg); 
    border-radius: 4px;
    outline: none;
    transition: background 0.2s ease-in-out;
    
    // Thumb del slider
    &::-webkit-slider-thumb {
      -webkit-appearance: none;
      appearance: none;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: $PRIMARY-PURPLE;
      cursor: grab;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
      transition: background 0.2s ease-in-out;
    }
    &::-moz-range-thumb {
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: $PRIMARY-PURPLE;
      cursor: grab;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    &:active::-webkit-slider-thumb {
        cursor: grabbing;
    }
    &:active::-moz-range-thumb {
        cursor: grabbing;
    }
  }
}

.valor-resaltado {
  font-weight: 700;
  color: $PRIMARY-PURPLE;
  font-variant-numeric: tabular-nums; 
}

.boton-simular {
  width: 100%;
  padding: 0.8rem 1rem;
  font-weight: 700;
  color: white;
  background-image: $PURPLE-GRADIENT; 
  border-radius: $border-radius-sm;
  border: none;
  transition: all 0.2s;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem; 
  font-size: 1.1rem;

  &:hover:not(:disabled) {
    box-shadow: 0 4px 10px rgba($PRIMARY-PURPLE, 0.4);
    transform: translateY(-3px); 
  }
  &:disabled {
    background-image: none; 
    background-color: $GRAY-COLD;
    cursor: not-allowed;
    opacity: 0.7;
    transform: translateY(0);
    box-shadow: none;
  }
}
.spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ------------------------------------
 * RESULTADOS Y GRÁFICA
 * ------------------------------------ */
.columna-resultados {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.resumen-costos-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1.2fr; 
  gap: 1.5rem; 
}

.tarjeta-resumen {
  background-color: var(--card-bg); 
  border-radius: $border-radius;
  padding: 1.2rem; 
  box-shadow: $box-shadow-sm;
  text-align: left;
  transition: background-color 0.3s;
  border: 1px solid var(--card-border); 
  position: relative; 

  .titulo-resumen {
    font-size: 0.95rem;
    color: var(--text-color-secondary); 
    font-weight: 500;
    display: block;
    margin-bottom: 0.4rem;
  }
  .valor-grande {
    font-size: 2rem; 
    font-weight: 700;
    color: var(--color-heading); 
    line-height: 1.1;
  }
  .leyenda-variacion {
    font-size: 0.85rem;
    color: var(--text-color-secondary); 
    display: block; 
    margin-top: 0.25rem;
  }

  // Estilos de Variación (Negativo = Reducción, Positivo = Aumento)
  &.tarjeta-variacion {
    .valor-grande {
      font-size: 2.2rem; 
    }
    
    &.variacion-negativa { /* Reducción (Verde/Éxito) */
      background-color: rgba($SUCCESS-COLOR, 0.15); 
      border-color: $SUCCESS-COLOR;
      .valor-grande {
        color: $SUCCESS-COLOR;
      }
    }
    &.variacion-positiva { /* Aumento (Rojo/Peligro) */
      background-color: rgba($DANGER-COLOR, 0.15); 
      border-color: $DANGER-COLOR;
      .valor-grande {
        color: $DANGER-COLOR;
      }
    }
  }

  // Estilo Base / Simulado
  &.tarjeta-base {
    .valor-grande { color: $GRAY-COLD; }
  }
  &.tarjeta-simulado {
    .valor-grande { color: $PRIMARY-PURPLE; }
  }
}

.grafica-simulador-contenedor {
  background-color: var(--card-bg); 
  border: 1px solid var(--card-border); 
  border-radius: $border-radius;
  box-shadow: $box-shadow-sm;
  padding: 1.5rem;
    .panel-titulo {
      color: var(--text-color-primary); 
      font-size: 1.2rem;
      font-weight: 600;
      margin-bottom: 1rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    
      .info-icon {
        color: $PRIMARY-PURPLE;
        font-size: 1.3rem;
        cursor: pointer;
      }
    }
}

.mensaje-placeholder {
  text-align: center;
  color: var(--text-color-secondary); 
  padding: 100px 0;
  font-size: 1.1rem;

  i {
    display: block;
    font-size: 2.5rem; 
    margin-bottom: 15px;
    color: $GRAY-COLD;
  }
}

.alerta-error {
  background-color: rgba($DANGER-COLOR, 0.15); 
  color: $DANGER-COLOR;
  border: 1px solid $DANGER-COLOR;
  padding: 1rem 1.5rem;
  border-radius: $border-radius-sm;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.95rem;
  font-weight: 500;
  margin-top: 2rem;
}

// --- Responsive ---
@media (max-width: 992px) {
  .simulador-grid {
    grid-template-columns: 1fr;
  }
  .resumen-costos-grid {
    grid-template-columns: 1fr 1fr;
  }
  .tarjeta-resumen {
    .valor-grande { font-size: 1.5rem; }
    &.tarjeta-variacion .valor-grande { font-size: 1.5rem; }
  }
}

@media (max-width: 768px) {
    .resumen-costos-grid {
        grid-template-columns: 1fr; 
    }
    .lotes-seleccionados-display {
        flex-direction: column;
        align-items: flex-start;
        .boton-ir-gestion { margin-top: 0.5rem; }
    }
}
</style>