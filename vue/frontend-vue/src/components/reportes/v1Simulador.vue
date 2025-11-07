<template>
  <div class="plataforma-layout" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    <BarraLateralPlataforma :is-open="isSidebarOpen" />
    <div class="plataforma-contenido" :class="{ 'shifted': isSidebarOpen }">
      <EncabezadoPlataforma
        titulo="Simulador Energético"
        subtitulo="Proyección de escenarios de consumo y costos energéticos institucionales."
        @toggle-sidebar="toggleSidebar"
        :is-sidebar-open="isSidebarOpen"
      />

      <div class="simulador-principal-contenido">

        <div class="simulador-grid">
          
          <div class="gestion-panel panel-controles">
            <h2 class="panel-titulo"><i class="bi bi-sliders"></i> Parámetros de Simulación</h2>

            <div class="control-grupo">
              <label for="meses">
                Horizonte (Meses): <span class="valor-resaltado">{{ meses }}</span>
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

            <button @click="ejecutarSimulacion" :disabled="isLoading || !lotesCargados" class="boton-simular">
              <i v-if="isLoading" class="bi bi-arrow-repeat spin"></i>
              <i v-else class="bi bi-play-circle-fill"></i>
              {{ isLoading ? 'Simulando...' : 'Ejecutar Simulación' }}
            </button>
            
            <p v-if="!lotesCargados" class="ayuda-texto-carga">
              <i class="bi bi-info-circle"></i> Cargando lotes de la vista anterior...
            </p>
          </div>

          <div class="columna-resultados">
            
            <div class="resumen-costos-grid">
              
              <div class="tarjeta-resumen tarjeta-base">
                <span class="titulo-resumen">Costo Base ({{ meses }} m)</span>
                <p class="valor-grande">{{ formatCurrency(simulacionResultado.total_costo_base_mxn) }}</p>
              </div>

              <div class="tarjeta-resumen tarjeta-simulado">
                <span class="titulo-resumen">Costo Simulado ({{ meses }} m)</span>
                <p class="valor-grande">{{ formatCurrency(simulacionResultado.total_costo_simulado_mxn) }}</p>
              </div>

              <div class="tarjeta-resumen tarjeta-variacion" 
                   :class="simulacionResultado.variacion_costo_total_mxn <= 0 ? 'variacion-negativa' : 'variacion-positiva'">
                <span class="titulo-resumen">Variación vs. Base</span>
                <p class="valor-grande">
                    {{ formatCurrency(simulacionResultado.variacion_costo_total_mxn) }}
                </p>
                <span class="leyenda-variacion">
                   ({{ simulacionResultado.variacion_costo_total_mxn <= 0 ? 'Ahorro' : 'Gasto Extra' }})
                </span>
              </div>
            </div>
            
            <div class="grafica-simulador-contenedor">
              <GraficoSimulacionECharts
                v-if="chartData.labels.length > 0"
                :chart-data="chartData"
                :is-dark="isDark"
              />
              <div v-else class="mensaje-placeholder">
                <i class="bi bi-bar-chart-fill"></i> {{ isLoading ? 'Calculando proyección...' : 'Ajuste los parámetros y ejecute la simulación.' }}
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

// const API_BASE_URL = 'http://127.0.0.1:8001/api/v1'; 

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
      
      lotesCargados: [], // Lotes recibidos de la URL (STRINGS)
      
      meses: 24, // Valor inicial del slider
      simulacionParams: {
        tasa_inflacion_energetica: 0.08,
        tasa_crecimiento_consumo: 0.05,
        mejora_eficiencia_consumo: 0.10
      },
      isLoading: false,
      simulacionResultado: { // Inicializar con valores nulos para evitar errores
        total_costo_base_mxn: 0,
        total_costo_simulado_mxn: 0,
        variacion_costo_total_mxn: 0,
        porcentaje_variacion: 0,
      },
      chartData: { labels: [], datasets: [] },
      errorApi: null,
      
      _themeMediaQuery: null,
    };
  },
  mounted() {
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
    toggleSidebar() { this.isSidebarOpen = !this.isSidebarOpen; },
    handleThemeChange(event) { this.isDark = event.matches; this.formatearDatosGraficaConEstadoActual(); },
    detectarTemaSistema() {
       if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) { this.isDark = true; } else { this.isDark = false; }
    },
    
    cargarLotesDesdeUrl() {
      const lotesQuery = this.$route.query.lotes;
      if (lotesQuery) {
        // Asegurarse de que siempre sea un array de strings (nombres de lotes)
        this.lotesCargados = Array.isArray(lotesQuery) ? lotesQuery : [lotesQuery];
        if (this.lotesCargados.length > 0) {
            // Cargar simulación inicial con valores por defecto
            this.ejecutarSimulacion(); 
        }
      } else {
        this.errorApi = "No se recibieron lotes para simular. Regrese a la vista de Gestión.";
        this.lotesCargados = [];
      }
    },
    
    // --- Métodos de Formato ---
    formatPercent(value) { return (value * 100).toFixed(1) + '%'; },
    formatCurrency(value) { 
        if (value === null || value === undefined) return '$0';
        // Asegurarse de que el signo de variación se mantenga
        const sign = value < 0 ? '-' : '';
        const absValue = Math.abs(value);
        return `${sign} ${absValue.toLocaleString('es-MX', { style: 'currency', currency: 'MXN', minimumFractionDigits: 0 })}`;
    },
    
    // --- Lógica de Simulación ---
    async ejecutarSimulacion() {
      if (this.lotesCargados.length === 0) {
        this.errorApi = "No se seleccionaron lotes para ejecutar la simulación.";
        return;
      }
      
      this.isLoading = true;
      this.errorApi = null;
      this.chartData = { labels: [], datasets: [] };

      const token = localStorage.getItem('accessToken');
      if (!token) { this.errorApi = "Error de autenticación."; this.isLoading = false; this.$router.push('/'); return; }

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

        // 1. Actualizar Resumen KPI
        this.simulacionResultado = data.resumen_simulacion; 

        // 2. Formatear para Gráfica
        this.formatearDatosGrafica(data.predicciones_escenario); 

      } catch (error) {
        console.error("Error en la simulación:", error);
        this.errorApi = error.message || "Error al conectar con la API de simulación.";
      } finally {
        this.isLoading = false;
      }
    },
    
    formatearDatosGrafica(predicciones) {
      // Esta función prepara los datos para el GraficoSimulacionECharts
      const labels = predicciones.map(item => item.periodo);
      const datosCostoBase = predicciones.map(item => item.costo_base_mxn);
      const datosCostoSimulado = predicciones.map(item => item.costo_escenario_mxn);

      this.chartData = {
        labels: labels,
        datasets: [
          { label: 'Costo Base (Sin cambios)', data: datosCostoBase },
          { label: 'Costo Simulado', data: datosCostoSimulado }
        ]
      };
    },

    formatearDatosGraficaConEstadoActual() {
      // Re-formatear solo si hay datos para actualizar los colores
      if (!this.chartData || !this.chartData.labels || this.chartData.labels.length === 0) return;
      this.formatearDatosGrafica(this.chartData.labels.map((label, index) => ({
        periodo: label,
        costo_base_mxn: this.chartData.datasets[0].data[index],
        costo_escenario_mxn: this.chartData.datasets[1].data[index]
      })));
    },
  },
};
</script>

<style scoped lang="scss">
@use "sass:color";


/* El estilo de la vista Simulación debe ser similar al de VistaResumenEstadistico */

.simulador-principal-contenido {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.simulador-grid {
  display: grid;
  grid-template-columns: 350px 1fr; /* Controles más angostos (350px), resultados más grandes */
  gap: 2rem;
}

// ------------------------------------
// PANELES Y CONTROLES
// ------------------------------------
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
  font-size: 1.25rem;
  font-weight: 600;
  border-bottom: 1px solid var(--card-border);
  padding-bottom: 0.75rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.control-grupo {
  margin-bottom: 1.5rem;
  label {
    display: block;
    font-weight: 500;
    margin-bottom: 0.5rem;
    color: var(--text-color-primary);
  }
  input[type="range"] {
    width: 100%;
    accent-color: $PRIMARY-PURPLE;
  }
}

.valor-resaltado {
  font-weight: 700;
  color: $PRIMARY-PURPLE;
}

.boton-simular {
  width: 100%;
  padding: 0.8rem 1rem;
  font-weight: 700;
  color: white;
  background-color: $PRIMARY-PURPLE;
  border-radius: $border-radius-sm;
  border: none;
  transition: all 0.2s;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;

  &:hover:not(:disabled) {
    background-color: color.adjust($PRIMARY-PURPLE, $lightness: -5%);
    transform: translateY(-2px);
  }
  &:disabled {
    background-color: $GRAY-COLD;
    cursor: not-allowed;
    opacity: 0.7;
    transform: translateY(0);
  }
}
.spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

.ayuda-texto-carga {
    font-size: 0.85rem;
    color: $GRAY-COLD;
    text-align: center;
    margin-top: 1rem;
}

// ------------------------------------
// RESULTADOS Y GRÁFICA
// ------------------------------------
.columna-resultados {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.resumen-costos-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1.2fr; /* 3 columnas: Base | Simulado | Variación */
  gap: 1rem;
}

.tarjeta-resumen {
  background-color: var(--card-bg);
  border-radius: $border-radius;
  padding: 1rem;
  box-shadow: $box-shadow-sm;
  text-align: left;
  transition: background-color 0.3s;
  border: 1px solid var(--card-border);
  
  .titulo-resumen {
    font-size: 0.9rem;
    color: var(--text-color-secondary);
    font-weight: 500;
    display: block;
    margin-bottom: 0.25rem;
  }
  .valor-grande {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--color-heading);
    line-height: 1.1;
  }
  .leyenda-variacion {
    font-size: 0.8rem;
    color: var(--text-color-secondary);
  }

  // Estilos de Variación
  &.tarjeta-variacion {
    .valor-grande {
      font-size: 2rem;
    }
    
    &.variacion-negativa { /* Ahorro (Verde) */
      background-color: rgba($SUCCESS-COLOR, 0.2);
      border-color: $SUCCESS-COLOR;
      .valor-grande {
        color: $SUCCESS-COLOR;
      }
    }
    &.variacion-positiva { /* Gasto Extra (Rojo/Naranja) */
      background-color: rgba($DANGER-COLOR, 0.2);
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
}

.mensaje-placeholder {
  text-align: center;
  color: var(--text-color-secondary);
  padding: 100px 0;
  font-size: 1.1rem;

  i {
    display: block;
    font-size: 2rem;
    margin-bottom: 10px;
  }
}

.alerta-error {
  background-color: rgba($DANGER-COLOR, 0.1);
  color: $DANGER-COLOR;
  border: 1px solid $DANGER-COLOR;
  padding: 1rem;
  border-radius: $border-radius-sm;
  display: flex;
  align-items: center;
  gap: 0.75rem;
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
</style>