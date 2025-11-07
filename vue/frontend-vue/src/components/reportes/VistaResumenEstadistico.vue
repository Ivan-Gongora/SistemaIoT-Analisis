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
            <div class="col-6 col-md-4 col-lg-3 col-xl-2 mb-3">
              <ResumenCard titulo="Consumo Promedio" :valor="formatoNumero(estadisticasBasicas.consumo_promedio_kwh, ' kWh/mes')" icono="bi-lightning" :is-dark="isDark" />
            </div>
            <div class="col-6 col-md-4 col-lg-3 col-xl-2 mb-3">
              <ResumenCard titulo="Costo Promedio" :valor="formatoMoneda(estadisticasBasicas.costo_promedio_mxn, ' MXN/mes')" icono="bi-cash-coin" :is-dark="isDark" />
            </div>
            <div class="col-6 col-md-4 col-lg-3 col-xl-2 mb-3">
              <ResumenCard titulo="Demanda Máx. Prom." :valor="formatoNumero(estadisticasBasicas.demanda_maxima_promedio_kw, ' kW')" icono="bi-graph-up" :is-dark="isDark" />
            </div>
            <div class="col-6 col-md-4 col-lg-3 col-xl-2 mb-3">
              <ResumenCard titulo="% Factor Pot. Prom." :valor="formatoPorcentaje(estadisticasBasicas.factor_potencia_promedio)" icono="bi-battery-charging" :is-dark="isDark" />
            </div>
            <div class="col-6 col-md-4 col-lg-3 col-xl-2 mb-3">
              <ResumenCard titulo="Correlación Consumo-Costo" :valor="formatoNumero(estadisticasAnalisis.correlaciones.consumo_costo)" icono="bi-arrow-left-right" :is-dark="isDark" />
            </div>
            <div class="col-6 col-md-4 col-lg-3 col-xl-2 mb-3">
              <ResumenCard titulo="Correlación Demanda-Consumo" :valor="formatoNumero(estadisticasAnalisis.correlaciones.demanda_consumo)" icono="bi-arrow-left-right" :is-dark="isDark" />
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

          <div class="row mb-4">
            <div class="col-12">
              <GraficoEvolucionSeries
                titulo="Evolución de Consumo por Lote (Histórico Completo)"
                :datos-evolucion="datosEvolucionPorLote"
                :metrica-seleccionada="metricaSeleccionada"
                :is-dark="isDark"
              />
            </div>
          </div>

          <div class="row">
            <div class="col-12">
              <div class="card chart-card p-4" :class="{ 'theme-dark': isDark }">
                <h5 class="card-title">Estadísticas Anuales (Tabla)</h5>
                <div class="table-responsive">
                  <table class="table table-hover mt-3" :class="{ 'table-dark-custom': isDark, 'table-light-custom': !isDark }">
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
import GraficoEvolucionSeries from '@/components/graficos/GraficoEvolucionSeries.vue'; // <-- NUEVO COMPONENTE

export default {
  name: 'VistaResumenEstadistico',
  components: {
    BarraLateralPlataforma,
    EncabezadoPlataforma,
    ResumenCard,
    GraficoBarrasComparativas,
    GraficoLineasEvolucion,
    GraficoEvolucionSeries, // Asegúrate de registrar el nuevo componente aquí
  },
  data() {
    return {
      isDark: false,
      isSidebarOpen: true,

      lotesCargados: [], // Lotes recibidos de la URL

      loading: true,
      error: null,

      // Datos de la API para estadisticasBasicas (del endpoint /historico)
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
      // Array de objetos { periodo, consumo_total_kwh, costo_total } del endpoint /historico
      tendenciasMensuales: [], 

      // Datos de la API para estadisticasAnalisis (del endpoint /estadisticas)
      estadisticasAnalisis: {
        estadisticas_anuales: [], // Array de objetos { año, consumo_total_kwh_sum, ... }
        patron_mensual: [], // Array de objetos { mes, consumo_total_kwh, costo_total }
        correlaciones: { consumo_costo: 0, demanda_consumo: 0 },
        lotes_analizados: [],
      },
      // Metrica seleccionada para el gráfico de evolución por lote
      metricaSeleccionada: 'consumo_total_kwh', 
    };
  },
  computed: {
    // Procesa `patron_mensual` (del endpoint /estadisticas) para GraficoLineasEvolucion
    // Este muestra el patrón promedio de los meses de TODOS los lotes seleccionados.
    tendenciasMensualesProcesadas() {
        // Asegúrate de usar `estadisticasAnalisis.patron_mensual` para este gráfico
        const patronMensual = this.estadisticasAnalisis.patron_mensual;

        if (!patronMensual || patronMensual.length === 0) {
            return [];
        }

        // Mapea los datos para las dos series: Consumo y Costo
        return [
            {
                name: 'Consumo (kWh)',
                data: patronMensual.map(m => ({ mes: m.mes, consumo_total_kwh: m.consumo_total_kwh }))
            },
            {
                name: 'Costo (MXN)',
                data: patronMensual.map(m => ({ mes: m.mes, costo_total: m.costo_total }))
            }
        ];
    },

    // Procesa `estadisticas_anuales` (del endpoint /estadisticas) para GraficoBarrasComparativas
    estadisticasAnualesProcesadas() {
      const annualData = {};
      this.estadisticasAnalisis.estadisticas_anuales.forEach(stat => {
        if (!annualData[stat.año]) {
          annualData[stat.año] = {
            consumo_total_kwh: 0,
            costo_total: 0,
          };
        }
        annualData[stat.año].consumo_total_kwh += stat.consumo_total_kwh_sum || 0;
        annualData[stat.año].costo_total += stat.costo_total_sum || 0;
      });
      return annualData;
    },

    // NUEVA PROPIEDAD COMPUTADA: Prepara datos para GraficoEvolucionSeries (línea de tiempo continua por lote)
    // Usa `tendenciasMensuales` (del endpoint /historico)
    datosEvolucionPorLote() {
      if (!this.lotesCargados || this.lotesCargados.length === 0 || !this.tendenciasMensuales || this.tendenciasMensuales.length === 0) {
        return { labels: [], series: [] };
      }

      const allPeriodsSet = new Set(); // Para recolectar todos los periodos (fechas) únicos
      const seriesDataByLote = {}; // Almacena los valores de cada lote por periodo

      // Inicializar `seriesDataByLote` para cada lote seleccionado
      this.lotesCargados.forEach(loteNombre => {
        seriesDataByLote[loteNombre] = {};
      });

      // Iterar sobre los datos brutos de `tendenciasMensuales` (del endpoint /historico)
      this.tendenciasMensuales.forEach(item => {
        const period = item.periodo; // '2021-01', '2022-12', etc.
        const year = period.substring(0, 4);

        // --- ATENCIÓN CRÍTICA AQUÍ ---
        // Necesitas una forma de saber A QUÉ LOTE pertenece cada `item` en `tendenciasMensuales`.
        // Si tu API `/historico` devuelve un `lote_id` en cada item, ¡úsalo!
        // Ejemplo: `item.lote_id`
        // Si no, estoy asumiendo que el nombre del lote contiene el año, y que un lote = un año.
        // Si tienes lotes como 'sectorA_2021', 'sectorB_2021', esto no funcionaría bien.
        // La mejor solución sería que la API te diera un `lote_id` en cada item.

        // Por ahora, estoy asumiendo que si el lote es 'historico_2021', se relaciona con '2021-XX'.
        // Esto solo funciona si cada lote representa un año distinto y su nombre lo indica.
        const relevantLoteName = this.lotesCargados.find(lote => lote.includes(year));

        if (relevantLoteName && seriesDataByLote[relevantLoteName]) {
          seriesDataByLote[relevantLoteName][period] = {
            consumo_total_kwh: item.consumo_total_kwh || 0,
            costo_total: item.costo_total || 0,
          };
        }
        allPeriodsSet.add(period); // Recopilar todos los periodos únicos de todos los lotes
      });

      // Ordenar todos los periodos de forma cronológica para el Eje X
      const sortedLabels = Array.from(allPeriodsSet).sort();

      // Construir el array final de series para ECharts
      const finalEchartsSeries = this.lotesCargados.map(loteName => {
        const dataForThisLote = sortedLabels.map(periodo => {
          const dataPoint = seriesDataByLote[loteName]?.[periodo];
          // Aquí estamos eligiendo `this.metricaSeleccionada` como el valor principal
          // para el gráfico. Si no hay datos, se usa 0.
          return dataPoint ? (dataPoint[this.metricaSeleccionada] || 0) : 0; 
        });

        return {
          name: `Lote ${loteName}`, // Nombre de la serie (ej: "Lote historico_2021")
          data: dataForThisLote,
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 4,
          // Puedes añadir más propiedades aquí (color, etc.)
        };
      });

      return {
        labels: sortedLabels,
        series: finalEchartsSeries,
      };
    },
  },
  
  async mounted() {
    this.detectarTemaSistema();
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', this.handleThemeChange);
    }
    await this.cargarDatos();
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
        // 1. Obtener Análisis Histórico (para estadísticas básicas y tendencias mensuales crudas)
        const historicoResponse = await fetch(`${API_BASE_URL}/api/energetico/analisis/historico`, { // Usar URL completa
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
          this.tendenciasMensuales = historicoData.data.tendencias_mensuales || []; // <-- Datos para GraficoEvolucionSeries
        } else {
            console.warn("Respuesta inesperada para analisis/historico:", historicoData);
            this.error = this.error || "Datos históricos incompletos o inesperados.";
        }

        // 2. Obtener Estadísticas de Análisis (para estadísticas anuales, patrón mensual y correlaciones)
        const estadisticasResponse = await fetch(`${API_BASE_URL}/api/energetico/analisis/estadisticas`, { // Usar URL completa
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
          this.estadisticasAnalisis.patron_mensual = estadisticasData.data.patron_mensual || []; // <-- Datos para GraficoLineasEvolucion
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

    // Métodos de formato
    formatoNumero(valor, unidad = '') {
      if (typeof valor !== 'number' || isNaN(valor) || valor === null) {
        return 'N/A';
      }
      return `${valor.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })}${unidad}`;
    },
    formatoMoneda(valor, unidad = '') {
      if (typeof valor !== 'number' || isNaN(valor) || valor === null) {
        return 'N/A';
      }
      return `${valor.toLocaleString('es-MX', { style: 'currency', currency: 'MXN', minimumFractionDigits: 0, maximumFractionDigits: 2 })}${unidad}`;
    },
    formatoPorcentaje(valor) {
      if (typeof valor !== 'number' || isNaN(valor) || valor === null) {
        return 'N/A';
      }
      // Ajuste si el valor ya viene como porcentaje (ej. 72.69%) o como decimal (ej. 0.7269)
      // Asumimos que `factor_potencia_promedio` viene ya en porcentaje (ej. 72.69)
      if (valor > 1) { // Si es un número como 72.69
        return `${valor.toFixed(1)}%`;
      }
      return `${(valor * 100).toFixed(1)}%`; // Si el valor viene como decimal (ej. 0.73)
    }
  },
};
</script>

<style scoped lang="scss"">
/* Estilos existentes de tu VistaResumenEstadistico.vue */
.plataforma-layout {
  display: flex;
  min-height: 100vh;
  transition: background-color 0.3s ease;
}

.plataforma-contenido {
  flex-grow: 1;
  padding: 20px;
  transition: margin-left 0.3s ease;
  margin-left: 80px; /* Ancho de la barra lateral colapsada */
  overflow-x: hidden; /* Evita desbordamiento horizontal */
}

.plataforma-contenido.shifted {
  margin-left: 250px; /* Ancho de la barra lateral expandida */
}

/* Temas */
.theme-dark {
  background-color: #2c2c3e;
  color: #e0e0e0;
}

.theme-light {
  background-color: #f4f7f6;
  color: #333;
}

/* Cards y tablas */
.card {
  background-color: var(--card-bg-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

.theme-dark .card {
  background-color: #3b3b5b;
  border-color: #4a4a6e;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.card-title {
  color: var(--heading-color);
}

.theme-dark .card-title {
  color: #f0f0f0;
}

.table-dark-custom {
  --bs-table-bg: #3b3b5b;
  --bs-table-color: #e0e0e0;
  --bs-table-border-color: #4a4a6e;
  --bs-table-hover-bg: #4a4a6e;
}

.table-light-custom {
  --bs-table-bg: #ffffff;
  --bs-table-color: #333;
  --bs-table-border-color: #e0e0e0;
  --bs-table-hover-bg: #f5f5f5;
}

/* Loading overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1050;
  color: white;
}

.loading-text {
  margin-top: 15px;
  font-size: 1.2rem;
}

.resumen-estadistico-container {
  padding-top: 20px;
}
</style>