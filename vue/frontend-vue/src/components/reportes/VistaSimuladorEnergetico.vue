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

            <button @click="ejecutarSimulacion" :disabled="isLoading || !lotesCargados || lotesCargados.length === 0" class="boton-simular">
              <i v-if="isLoading" class="bi bi-arrow-repeat spin"></i>
              <i v-else class="bi bi-play-circle-fill"></i>
              {{ isLoading ? 'Simulando...' : 'Ejecutar Simulación' }}
            </button>
          </div>

          <div class="columna-resultados">
            
            <div class="resumen-costos-grid">
              
              <div class="tarjeta-resumen tarjeta-base" 
                   title="Costo total proyectado de la energía si no se realizan cambios ni optimizaciones en el consumo o tarifas. Es el punto de referencia para comparar con el escenario simulado.">
                <span class="titulo-resumen">Costo Base ({{ meses }} m)</span>
                <p class="valor-grande">{{ formatCurrency(simulacionResultado.total_costo_base_mxn) }}</p>
              </div>

              <div class="tarjeta-resumen tarjeta-simulado" 
                   title="Costo total proyectado de la energía considerando la inflación, el crecimiento del consumo y las mejoras de eficiencia que has configurado en los parámetros.">
                <span class="titulo-resumen">Costo Simulado ({{ meses }} m)</span>
                <p class="valor-grande">{{ formatCurrency(simulacionResultado.total_costo_simulado_mxn) }}</p>
              </div>

              <div class="tarjeta-resumen tarjeta-variacion" 
                   :class="simulacionResultado.variacion_costo_total_mxn <= 0 ? 'variacion-negativa' : 'variacion-positiva'"
                   :title="simulacionResultado.variacion_costo_total_mxn <= 0 ? 'Ahorro total estimado al comparar el costo simulado con el costo base. Un valor negativo es un ahorro, uno positivo es un gasto adicional.' : 'Gasto extra total estimado al comparar el costo simulado con el costo base. Un valor positivo es un gasto adicional, uno negativo es un ahorro.'">
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
              <h3 class="panel-titulo">
                  Proyección de Costos: Escenario Base vs. Simulado
                  
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
                v-if="chartData && chartData.labels && chartData.labels.length > 0"
                :chart-data="chartData"
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
// // 🎯 Asumimos que API_BASE_URL se inyecta globalmente o se importa desde config
// import { API_BASE_URL } from '@/config/apiConfig'; 

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
        total_meses_simulados: 0,
        total_costo_base_mxn: 0,
        total_costo_simulado_mxn: 0,
        variacion_costo_total_mxn: 0,
        porcentaje_variacion: 0,
        parametros_escenario: {},
        lotes_simulados: [],
      },
      chartData: { labels: [], datasets: [] }, // Datos para la gráfica
      errorApi: null,
      
      _themeMediaQuery: null,
       popoverTitle: "Análisis de Proyección",
      popoverContent: `
        <p>Esta gráfica ilustra la evolución mensual de tus costos energéticos.</p>
        <p>La línea <strong>"Costo Base (Sin cambios)"</strong> (generalmente punteada) muestra lo que pagarías si no aplicaras ninguna estrategia de optimización o ajuste a los parámetros.</p>
        <p>La línea <strong>"Costo Simulado"</strong> (generalmente sólida) te presenta tus costos esperados al aplicar los parámetros de simulación (inflación, crecimiento de consumo, reducción por eficiencia).</p>
        <p>Observa la diferencia entre ambas líneas: un espacio por debajo de la línea base indica ahorro, mientras que un espacio por encima muestra un gasto adicional proyectado.</p>
      `
    };
  },
  mounted() {
    this.initPopovers();
    this.detectarTemaSistema();
    this.cargarLotesDesdeUrl(); // Solo carga los lotes, no ejecuta la simulación
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
        // Selecciona todos los elementos que tienen data-bs-toggle="popover"
        const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
        
        // Itera sobre ellos y crea una nueva instancia de Popover para cada uno
        [...popoverTriggerList].map(popoverTriggerEl => {
            // Asegúrate de destruir cualquier instancia anterior para evitar duplicados si el componente se remonta
            if (bootstrap.Popover.getInstance(popoverTriggerEl)) {
                bootstrap.Popover.getInstance(popoverTriggerEl).dispose();
            }
            return new bootstrap.Popover(popoverTriggerEl);
        });
    },
    toggleSidebar() { this.isSidebarOpen = !this.isSidebarOpen; },
    handleThemeChange(event) { 
      this.isDark = event.matches; // <-- Actualiza isDark cuando cambia el tema del sistema
      this.formatearDatosGraficaConEstadoActual(); 
    },
    detectarTemaSistema() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) { 
          this.isDark = true; 
        } else { 
          this.isDark = false; 
        }
    },
    
    cargarLotesDesdeUrl() {
      const lotesQuery = this.$route.query.lotes;
      if (lotesQuery) {
        this.lotesCargados = Array.isArray(lotesQuery) ? lotesQuery : [lotesQuery];
        // NOTA: La simulación ya NO se ejecuta automáticamente aquí.
        // Se ejecuta solo al presionar el botón.
      } else {
        this.lotesCargados = []; // Vacío si no hay lotes
        // No mostrar error aquí, el mensaje "No se han seleccionado lotes..." lo maneja.
      }
    },
    
    // --- Métodos de Formato ---
    formatPercent(value) { return (value * 100).toFixed(1) + '%'; },
    formatCurrency(value) { 
        if (value === null || value === undefined) return '$0';
        const absValue = Math.abs(value);
        return `${value < 0 ? '-' : ''}${absValue.toLocaleString('es-MX', { style: 'currency', currency: 'MXN', minimumFractionDigits: 0 })}`;
    },
    
    // --- Lógica de Simulación ---
    async ejecutarSimulacion() {
      if (!this.lotesCargados || this.lotesCargados.length === 0) {
        this.errorApi = "Por favor, seleccione al menos un lote de datos en la vista 'Gestión de Datos Energéticos' para simular.";
        return;
      }
      
      this.isLoading = true;
      this.errorApi = null;
      this.chartData = { labels: [], datasets: [] }; // Limpiar gráfica al iniciar simulación

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

    // Asegura que la gráfica se re-renderice con los colores correctos al cambiar el tema
    formatearDatosGraficaConEstadoActual() {
      if (!this.chartData || !this.chartData.labels || this.chartData.labels.length === 0) return;
      // Recrear los datos con los mismos valores para forzar la actualización de ECharts
      this.chartData = { ...this.chartData };
    },
  },
};
</script>

<style scoped lang="scss">
@use "sass:color";


/* -----------------------------------------------------------------
 * DEFINICIÓN DE VARIABLES CSS DEL TEMA (CRÍTICO PARA MODO OSCURO)
 * Este bloque es necesario para que las variables CSS como --card-bg
 * tengan un valor dependiendo de la clase de tema aplicada.
 * ----------------------------------------------------------------- */

// Estilos base para el layout principal, incluyendo el color de fondo del body.
.plataforma-layout {
  display: flex;
  min-height: 100vh;
  transition: background-color 0.3s ease; // Transición suave para el color de fondo
  background-color: $WHITE-SOFT; // Fondo por defecto para el tema claro

  &.theme-dark {
    /* Variables CSS personalizadas para el modo oscuro */
    --card-bg: #{$SUBTLE-BG-DARK};
    --card-border: #{$DARK-BORDER};
    --text-color-primary: #{$LIGHT-TEXT};
    --text-color-secondary: #{$GRAY-COLD};
    --color-heading: #{$LIGHT-TEXT}; /* Para títulos grandes en modo oscuro */
    --input-bg: #{$DARK-INPUT-BG}; /* Fondo del track del slider en modo oscuro */
    background-color: $DARK-BG-CONTRAST; // Fondo del body en modo oscuro
  }

  &.theme-light {
    /* Variables CSS personalizadas para el modo claro */
    --card-bg: #{$SUBTLE-BG-LIGHT};
    --card-border: #{$LIGHT-BORDER};
    --text-color-primary: #{$DARK-TEXT};
    --text-color-secondary: #{$GRAY-COLD};
    --color-heading: #{$DARK-TEXT}; /* Para títulos grandes en modo claro */
    --input-bg: #{$LIGHT-INPUT-BG}; /* Fondo del track del slider en modo claro */
    background-color: $WHITE-SOFT; // Fondo del body en modo claro (redundante pero explícito)
  }
}

// Asegurar que el contenido principal también adapte su fondo
.simulador-principal-contenido {
    padding: 2rem;
    max-width: 1600px; /* Aumentar ancho máximo para más espacio */
    margin: 0 auto;

    // Estos estilos de fondo serán sobrescritos por el .plataforma-layout general
    // o pueden ser redundantes si el body ya tiene el color correcto.
    // Sin embargo, si hay un fondo intermedio, esto asegura la consistencia.
    // Puedes comentar o eliminar si el fondo principal ya cubre todo bien.
    .theme-dark & {
        background-color: $DARK-BG-CONTRAST; // Asegura que el área de contenido sea oscura
    }
    .theme-light & {
        background-color: $WHITE-SOFT; // Asegura que el área de contenido sea clara
    }
}

.grafica-explicacion {
  background-color: var(--card-bg); // Usará el color de la tarjeta
  border: 1px solid var(--card-border); // Usará el borde de la tarjeta
  border-left: 4px solid $PRIMARY-PURPLE; // Una barra de color para destacarlo
  border-radius: $border-radius-sm;
  padding: 1rem 1.2rem;
  margin-bottom: 1.5rem; // Espacio antes de la gráfica
  font-size: 0.9rem;
  line-height: 1.5;
  color: var(--text-color-secondary); // Texto secundario

  p {
    margin: 0; // Quitar margen por defecto del párrafo
  }
  
  strong {
    color: var(--text-color-primary); // Para resaltar el texto importante
  }
}
/* ------------------------------------
 * LAYOUT GENERAL DE LA VISTA
 * ------------------------------------ */
// Nota: .plataforma-layout y .simulador-principal-contenido son las clases raíz
// que manejan el fondo general.

.simulador-grid {
  display: grid;
  grid-template-columns: 380px 1fr; /* Controles un poco más anchos (380px) */
  gap: 2rem;
  margin-top: 1.5rem; // Espacio entre lotes seleccionados y la rejilla principal
}

/* ------------------------------------
 * DISPLAY DE LOTES SELECCIONADOS
 * ------------------------------------ */
.lotes-seleccionados-display {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background-color: var(--card-bg); /* Usa la variable de tema */
  border: 1px solid var(--card-border); /* Usa la variable de tema */
  border-radius: $border-radius;
  padding: 1rem 1.5rem;
  box-shadow: $box-shadow-sm;
  color: var(--text-color-primary); /* Usa la variable de tema */
  font-size: 1.05rem;
  margin-bottom: 1rem; /* Espacio antes de la cuadrícula principal */

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
    color: var(--text-color-secondary); /* Usa la variable de tema */
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
  background-color: var(--card-bg); /* Usa la variable de tema */
  border: 1px solid var(--card-border); /* Usa la variable de tema */
  border-radius: $border-radius;
  box-shadow: $box-shadow-sm;
  padding: 1.5rem;
  height: fit-content;
}

.panel-controles .panel-titulo {
  color: var(--text-color-primary); /* Usa la variable de tema */
  font-size: 1.3rem;
  font-weight: 600;
  border-bottom: 1px solid var(--card-border); /* Usa la variable de tema */
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
    display: flex; /* Para alinear el texto y el valor resaltado */
    justify-content: space-between;
    font-weight: 500;
    margin-bottom: 0.5rem;
    color: var(--text-color-primary); /* Usa la variable de tema */
    font-size: 0.95rem;
  }
  input[type="range"] {
    width: 100%;
    height: 8px; // Altura del slider
    background: var(--input-bg); // Fondo del track del slider, usa la variable de tema
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
  font-variant-numeric: tabular-nums; /* Para alinear números en ancho fijo */
}

.boton-simular {
  width: 100%;
  padding: 0.8rem 1rem;
  font-weight: 700;
  color: white;
  background-image: $PURPLE-GRADIENT; /* Usar el gradiente */
  border-radius: $border-radius-sm;
  border: none;
  transition: all 0.2s;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem; /* Más espacio entre icono y texto */
  font-size: 1.1rem;

  &:hover:not(:disabled) {
    box-shadow: 0 4px 10px rgba($PRIMARY-PURPLE, 0.4);
    transform: translateY(-3px); /* Efecto 3D sutil */
  }
  &:disabled {
    background-image: none; /* Quitar gradiente cuando deshabilitado */
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
  grid-template-columns: 1fr 1fr 1.2fr; /* 3 columnas: Base | Simulado | Variación */
  gap: 1.5rem; /* Más espacio entre tarjetas */
}

.tarjeta-resumen {
  background-color: var(--card-bg); /* Usa la variable de tema */
  border-radius: $border-radius;
  padding: 1.2rem; /* Más padding */
  box-shadow: $box-shadow-sm;
  text-align: left;
  transition: background-color 0.3s;
  border: 1px solid var(--card-border); /* Usa la variable de tema */
  position: relative; // Para los tooltips

  .titulo-resumen {
    font-size: 0.95rem;
    color: var(--text-color-secondary); /* Usa la variable de tema */
    font-weight: 500;
    display: block;
    margin-bottom: 0.4rem;
  }
  .valor-grande {
    font-size: 2rem; /* Más grande */
    font-weight: 700;
    color: var(--color-heading); /* Usa la variable de tema */
    line-height: 1.1;
  }
  .leyenda-variacion {
    font-size: 0.85rem;
    color: var(--text-color-secondary); /* Usa la variable de tema */
    display: block; // Asegura que esté en su propia línea si hay espacio
    margin-top: 0.25rem;
  }

  // Estilos de Variación
  &.tarjeta-variacion {
    .valor-grande {
      font-size: 2.2rem; // Aún más grande para la variación
    }
    
    &.variacion-negativa { /* Ahorro (Verde) */
      background-color: rgba($SUCCESS-COLOR, 0.15); /* Menos opaco */
      border-color: $SUCCESS-COLOR;
      .valor-grande {
        color: $SUCCESS-COLOR;
      }
    }
    &.variacion-positiva { /* Gasto Extra (Rojo/Naranja) */
      background-color: rgba($DANGER-COLOR, 0.15); /* Menos opaco */
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
  background-color: var(--card-bg); /* Usa la variable de tema */
  border: 1px solid var(--card-border); /* Usa la variable de tema */
  border-radius: $border-radius;
  box-shadow: $box-shadow-sm;
  padding: 1.5rem;
    .panel-titulo {
        color: var(--text-color-primary); /* Usa la variable de tema */
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
  color: var(--text-color-secondary); /* Usa la variable de tema */
  padding: 100px 0;
  font-size: 1.1rem;

  i {
    display: block;
    font-size: 2.5rem; // Ícono más grande
    margin-bottom: 15px;
    color: $GRAY-COLD;
  }
}

.alerta-error {
  background-color: rgba($DANGER-COLOR, 0.15); /* Menos opaco */
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
        grid-template-columns: 1fr; /* Una columna en pantallas pequeñas */
    }
    .lotes-seleccionados-display {
        flex-direction: column;
        align-items: flex-start;
        .boton-ir-gestion { margin-top: 0.5rem; }
    }
}
</style>