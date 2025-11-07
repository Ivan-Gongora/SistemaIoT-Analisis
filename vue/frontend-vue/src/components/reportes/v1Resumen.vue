<template>
  <div class="plataforma-layout" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    <BarraLateralPlataforma :is-open="isSidebarOpen" />
    <div class="plataforma-contenido" :class="{ 'shifted': isSidebarOpen }">
      <EncabezadoPlataforma
        titulo="Resumen Estadístico Energético"
        subtitulo="Análisis de los lotes energéticos seleccionados"
        @toggle-sidebar="toggleSidebar"
        :is-sidebar-open="isSidebarOpen"
      />

      <div class="resumen-estadistico-container container-fluid">
        <div v-if="loading" class="loading-overlay">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
          <p class="loading-text">Cargando datos. Esto puede tomar un momento...</p>
        </div>
        <div v-else-if="error" class="alert alert-danger mt-4" role="alert">
          {{ error }}
        </div>
        <div v-else-if="!lotesCargados || lotesCargados.length === 0" class="alert alert-warning mt-4" role="alert">
          No se han seleccionado lotes para analizar o no se pudieron cargar. Por favor, regrese a la vista anterior.
        </div>
        <div v-else>
          <div class="row mb-4">
            <div class="col-md-4 col-lg-3 mb-3">
              <ResumenCard titulo="Consumo Promedio" :valor="formatoNumero(estadisticasBasicas.consumo_promedio_kwh, ' kWh/mes')" icono="bi-lightning" />
            </div>
            <div class="col-md-4 col-lg-3 mb-3">
              <ResumenCard titulo="Costo Promedio" :valor="formatoMoneda(estadisticasBasicas.costo_promedio_mxn, ' MXN/mes')" icono="bi-cash-coin" />
            </div>
            <div class="col-md-4 col-lg-2 mb-3">
              <ResumenCard titulo="Demanda Máx. Prom." :valor="formatoNumero(estadisticasBasicas.demanda_maxima_promedio_kw, ' kW')" icono="bi-graph-up" />
            </div>
            <div class="col-md-4 col-lg-2 mb-3">
              <ResumenCard titulo="% Factor Pot. Prom." :valor="formatoPorcentaje(estadisticasBasicas.factor_potencia_promedio)" icono="bi-battery-charging" />
            </div>
            <div class="col-md-4 col-lg-2 mb-3">
              <ResumenCard titulo="Correlación Consumo-Costo" :valor="formatoNumero(estadisticasAnalisis.correlaciones.consumo_costo)" icono="bi-arrow-left-right" />
            </div>
          </div>

          <div class="row mb-4">
            <div class="col-lg-6 mb-3">
              <GraficoLineasEvolucion
                titulo="Patrón Mensual Promedio"
                subtitulo="Tendencia Mensual Promedio (Histórico)"
                :datos-mensuales="tendenciasMensualesProcesadas"
                :is-dark="isDark"
              />
            </div>
            <div class="col-lg-6 mb-3">
              <GraficoBarrasComparativas
                titulo="Comparativa Anual (Totales)"
                :datos-anuales="estadisticasAnualesProcesadas"
                :is-dark="isDark"
              />
            </div>
          </div>

          <div class="row">
            <div class="col-12">
              <div class="card chart-card p-4" :class="{ 'theme-dark': isDark }">
                <h5 class="card-title">Estadísticas Anuales (Tabla)</h5>
                <div class="table-responsive">
                  <table class="table table-hover mt-3" :class="{ 'table-dark': isDark, 'table-light': !isDark }">
                    <thead>
                      <tr>
                        <th>Año</th>
                        <th>Consumo Total (kWh)</th>
                        <th>Consumo Prom. (kWh)</th>
                        <th>Costo Total (MXN)</th>
                        <th>Costo Prom. (MXN)</th>
                        <th>Demanda Máx. (kW)</th>
                        <th>Demanda Prom. (kW)</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="stat in estadisticasAnalisis.estadisticas_anuales" :key="stat.año">
                        <td>{{ stat.año }}</td>
                        <td>{{ formatoNumero(stat.consumo_total_kwh_sum) }}</td>
                        <td>{{ formatoNumero(stat.consumo_total_kwh_mean) }}</td>
                        <td>{{ formatoMoneda(stat.costo_total_sum) }}</td>
                        <td>{{ formatoMoneda(stat.costo_total_mean) }}</td>
                        <td>{{ formatoNumero(stat.demanda_maxima_kw_max) }}</td>
                        <td>{{ formatoNumero(stat.demanda_maxima_kw_mean) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p class="text-muted mt-3" v-if="estadisticasAnalisis.lotes_analizados && estadisticasAnalisis.lotes_analizados.length > 0">
                  Lotes analizados: {{ estadisticasAnalisis.lotes_analizados.join(', ') }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// Componentes de Layout
import BarraLateralPlataforma from '../plataforma/BarraLateralPlataforma.vue';
import EncabezadoPlataforma from '../plataforma/EncabezadoPlataforma.vue';

// Componentes específicos para esta vista
import ResumenCard from '@/components/ResumenCard.vue';
import GraficoBarrasComparativas from '@/components/graficos/GraficoBarrasComparativas.vue';
import GraficoLineasEvolucion from '@/components/graficos/GraficoLineasEvolucion.vue';

export default {
  name: 'VistaResumenEstadistico',
  components: {
    BarraLateralPlataforma,
    EncabezadoPlataforma,
    ResumenCard,
    GraficoBarrasComparativas,
    GraficoLineasEvolucion,
  },
  data() {
    return {
      isDark: false,
      isSidebarOpen: true,

      lotesCargados: [], // Lotes recibidos de la URL

      loading: true,
      error: null,

      // Datos de la API
      estadisticasBasicas: {
        total_registros: 0,
        rango_fechas: { inicio: '', fin: '' },
        consumo_promedio_kwh: 0,
        consumo_max_kwh: 0,
        consumo_min_kwh: 0,
        costo_promedio_mxn: 0,
        costo_total_acumulado: 0,
        demanda_maxima_promedio_kw: 0,
        factor_potencia_promedio: 0,
      },
      tendenciasMensuales: [], // Array de objetos { periodo, consumo_total_kwh, costo_total }

      estadisticasAnalisis: {
        estadisticas_anuales: [], // Array de objetos { año, consumo_total_kwh_sum, ... }
        patron_mensual: [], // Array de objetos { mes, consumo_total_kwh, costo_total }
        correlaciones: { consumo_costo: 0, demanda_consumo: 0 },
        lotes_analizados: [],
      },
      // Datos crudos del tercer endpoint, si se necesitan para la tabla detallada
      // datosMuestra: [],
    };
  },
  computed: {
    // Procesa tendenciasMensuales para el formato esperado por GraficoLineasEvolucion
    tendenciasMensualesProcesadas() {
      // Como tu API devuelve tendencias_mensuales para TODOS los lotes seleccionados mezclados,
      // el gráfico de líneas mostrará la tendencia "promedio" o "agregada" de todos ellos.
      // Si quisieras una línea por cada lote, la API debería devolver un array de tendencias_mensuales
      // anidado por lote. Dada la respuesta, procesamos un único conjunto de tendencias.
      const processed = Array(12).fill(0).map((_, i) => ({ mes: i + 1, consumo_total_kwh: 0, costo_total: 0 }));

      this.tendenciasMensuales.forEach(item => {
        const monthIndex = new Date(item.periodo + '-01').getMonth(); // 0-11
        if (processed[monthIndex]) {
          processed[monthIndex].consumo_total_kwh += item.consumo_total_kwh;
          processed[monthIndex].costo_total += item.costo_total;
        }
      });

      // Si hay múltiples lotes, promediar los valores para la "tendencia mensual promedio"
      // La API ya devuelve tendencias_mensuales como un único array de objetos mensuales,
      // lo que sugiere que ya es un agregado (o un promedio si el backend lo hace).
      // Si `lotesCargados.length > 1`, el backend debe hacer el promedio/suma antes de enviar.
      // Aquí, asumimos que `tendenciasMensuales` ya es el conjunto de datos para el gráfico de líneas.
      // Para el ejemplo de la foto, parece ser una única línea, que bien podría ser el promedio.
      return [{
        name: 'Histórico', // Nombre genérico para la serie de línea
        data: processed.map(m => ({ consumo_total_kwh: m.consumo_total_kwh, costo_total: m.costo_total }))
      }];
    },

    // Procesa estadisticas_anuales para el formato esperado por GraficoBarrasComparativas
    estadisticasAnualesProcesadas() {
      // La imagen muestra barras de Consumo (kWh) y Costo (MXN) para el año.
      // Esto significa que necesitamos sumar los datos por año (si hay múltiples años en los lotes seleccionados)
      // o tomar el único año si solo se seleccionó un lote/año.
      const annualData = {};
      this.estadisticasAnalisis.estadisticas_anuales.forEach(stat => {
        if (!annualData[stat.año]) {
          annualData[stat.año] = {
            consumo_total_kwh: 0,
            costo_total: 0,
          };
        }
        annualData[stat.año].consumo_total_kwh += stat.consumo_total_kwh_sum;
        annualData[stat.año].costo_total += stat.costo_total_sum;
      });

      // El gráfico de barras comparativas ahora espera un objeto como:
      // {
      //   '2021': { consumo_total_kwh: X, costo_total: Y },
      //   '2022': { consumo_total_kwh: A, costo_total: B },
      // }
      // Esto coincide con el formato de `this.estadisticasAnalisis.estadisticas_anuales`
      // si cada elemento representa un año. Si los lotes pueden tener el mismo año pero
      // ser diferentes (e.g., "historico_2021_A", "historico_2021_B"), entonces tendríamos que agregar.
      // Por el ejemplo de la API, asumimos 1 entrada por año en `estadisticas_anuales`.
      return annualData;
    }
  },
  async mounted() {
    this.detectarTemaSistema();
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', this.handleThemeChange);
    }
    await this.cargarDatos(); // Llama a cargarDatos en el mounted
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
    },

    async cargarDatos() {
      this.loading = true;
      this.error = null;

      // Leer los lotes de los query params
      const lotesQuery = this.$route.query.lotes;
      if (lotesQuery) {
        this.lotesCargados = Array.isArray(lotesQuery) ? lotesQuery : [lotesQuery];
      }

      if (this.lotesCargados.length === 0) {
        this.error = "No se seleccionaron lotes para el análisis. Por favor, regrese y seleccione al menos uno.";
        this.loading = false;
        return;
      }

      const token = localStorage.getItem('accessToken');
      if (!token) {
        this.error = "Error de autenticación. No se pudo obtener el token.";
        this.loading = false;
        this.$router.push('/');
        return;
      }

      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };
      const body = JSON.stringify({ lotes_seleccionados: this.lotesCargados });

      try {
        // 1. Obtener Análisis Histórico (para estadísticas básicas y tendencias mensuales)
        const historicoResponse = await fetch(`${API_BASE_URL}/api/energetico/analisis/historico`, {
          method: 'POST',
          headers: headers,
          body: body
        });
        if (!historicoResponse.ok) {
          throw new Error(`Error ${historicoResponse.status} al cargar análisis histórico: ${historicoResponse.statusText}`);
        }
        const historicoData = await historicoResponse.json();
        if (historicoData.status === 'success' && historicoData.data) {
          this.estadisticasBasicas = historicoData.data.estadisticas_basicas || this.estadisticasBasicas;
          this.tendenciasMensuales = historicoData.data.tendencias_mensuales || [];
        } else {
            console.warn("Respuesta inesperada para analisis/historico:", historicoData);
            this.error = this.error || "Datos históricos incompletos o inesperados.";
        }

        // 2. Obtener Estadísticas de Análisis (para estadísticas anuales, patrón mensual y correlaciones)
        const estadisticasResponse = await fetch(`${API_BASE_URL}/api/energetico/analisis/estadisticas`, {
          method: 'POST',
          headers: headers,
          body: body
        });
        if (!estadisticasResponse.ok) {
          throw new Error(`Error ${estadisticasResponse.status} al cargar estadísticas: ${estadisticasResponse.statusText}`);
        }
        const estadisticasData = await estadisticasResponse.json();
        if (estadisticasData.status === 'success' && estadisticasData.data) {
          this.estadisticasAnalisis.estadisticas_anuales = estadisticasData.data.estadisticas_anuales || [];
          this.estadisticasAnalisis.patron_mensual = estadisticasData.data.patron_mensual || [];
          this.estadisticasAnalisis.correlaciones = estadisticasData.data.correlaciones || { consumo_costo: 0, demanda_consumo: 0 };
          this.estadisticasAnalisis.lotes_analizados = estadisticasData.data.lotes_analizados || [];
        } else {
            console.warn("Respuesta inesperada para analisis/estadisticas:", estadisticasData);
            this.error = this.error || "Estadísticas de análisis incompletas o inesperadas.";
        }

      } catch (err) {
        console.error("Error al cargar los datos del resumen:", err);
        this.error = "No se pudieron cargar los datos del resumen. Intente nuevamente o verifique los lotes seleccionados.";
      } finally {
        this.loading = false;
      }
    },

    // --- Métodos de Formato para la UI ---
    formatoNumero(valor, unidad = '') {
      if (typeof valor !== 'number' || isNaN(valor)) {
        return 'N/A';
      }
      return `${valor.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })}${unidad}`;
    },
    formatoMoneda(valor, unidad = '') {
      if (typeof valor !== 'number' || isNaN(valor)) {
        return 'N/A';
      }
      return `${valor.toLocaleString('es-MX', { style: 'currency', currency: 'MXN', minimumFractionDigits: 0, maximumFractionDigits: 2 })}${unidad}`;
    },
    formatoPorcentaje(valor) {
      if (typeof valor !== 'number' || isNaN(valor)) {
        return 'N/A';
      }
      return `${valor.toFixed(1)}%`;
    }
  },
};
</script>

<style scoped lang="scss">

.plataforma-layout {
  display: flex;
  min-height: 100vh;
  transition: all 0.3s ease;
  background-color: var(--color-background-soft);

  &.theme-dark {
    --color-background-soft: #{$dark-bg-soft};
    --color-background-mute: #{$dark-bg-mute};
    --color-text: #{$dark-text-color};
    --color-heading: #{$dark-heading-color};
    --color-border: #{$dark-border-color};
    --color-card-background: #{$dark-card-bg};
    --color-card-border: #{$dark-card-border};
    --color-table-header: #{$dark-table-header-bg};
    --color-table-hover: #{$dark-table-hover-bg};
  }

  &.theme-light {
    --color-background-soft: #{$light-bg-soft};
    --color-background-mute: #{$light-bg-mute};
    --color-text: #{$light-text-color};
    --color-heading: #{$light-heading-color};
    --color-border: #{$light-border-color};
    --color-card-background: #{$light-card-bg};
    --color-card-border: #{$light-card-border};
    --color-table-header: #{$light-table-header-bg};
    --color-table-hover: #{$light-table-hover-bg};
  }
}

.plataforma-contenido {
  flex-grow: 1;
  padding: $spacer * 1.5;
  padding-left: calc($sidebar-width-collapsed + $spacer * 1.5);
  transition: padding-left 0.3s ease;

  &.shifted {
    padding-left: calc($sidebar-width-expanded + $spacer * 1.5);
  }
}

.resumen-estadistico-container {
  padding: $spacer * 1.5;
  position: relative; // Para el overlay de carga
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(var(--color-card-background-rgb), 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
  border-radius: $border-radius;

  .spinner-border {
    width: 3rem;
    height: 3rem;
    color: $primary-color !important;
  }

  .loading-text {
    margin-top: $spacer;
    color: var(--color-text);
    font-size: 1.1rem;
  }
}

.chart-card {
  background-color: var(--color-card-background);
  border: 1px solid var(--color-card-border);
  border-radius: $border-radius;
  box-shadow: $box-shadow-sm;
  padding: $spacer * 1.5;
  height: 100%; // Asegura que las cards de gráficas ocupen todo el espacio disponible en altura
  display: flex;
  flex-direction: column;
}

.card-title {
  color: var(--color-heading);
  font-size: 1.25rem;
  margin-bottom: $spacer * 1.5;
  text-align: center;
  font-weight: 600;
}

.table {
  color: var(--color-text);

  th {
    background-color: var(--color-table-header);
    color: var(--color-heading);
    border-color: var(--color-border);
  }

  td {
    border-color: var(--color-border);
  }

  &.table-dark {
    --bs-table-bg: var(--color-card-background);
    --bs-table-striped-bg: var(--color-table-hover);
    --bs-table-hover-bg: var(--color-table-hover);
    --bs-table-color: var(--color-text);
    th { color: var(--color-heading); }
  }

  &.table-light {
    --bs-table-bg: var(--color-card-background);
    --bs-table-striped-bg: var(--color-table-hover);
    --bs-table-hover-bg: var(--color-table-hover);
    --bs-table-color: var(--color-text);
    th { color: var(--color-heading); }
  }
}

.text-muted {
  color: var(--color-text) !important; // Sobrescribir si es necesario para el tema
  font-style: italic;
}

// Estilos de alerta
.alert-danger {
  background-color: rgba(220, 53, 69, 0.1);
  color: #{$danger-color};
  border-color: #{$danger-color};
}
.alert-warning {
  background-color: rgba(255, 193, 7, 0.1);
  color: #{$warning-color};
  border-color: #{$warning-color};
}
</style>