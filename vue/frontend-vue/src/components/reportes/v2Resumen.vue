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
    tendenciasMensualesProcesadas() {
      const series = {}; // Objeto para almacenar series por año (o por lote)

      // Itera sobre los datos crudos de tendenciasMensuales
      // Estos vienen de `historicoResponse.data.tendencias_mensuales`
      // Asumimos que cada item tiene `periodo` (ej: "2021-01") y las métricas
      
      this.tendenciasMensuales.forEach(item => {
        const year = item.periodo.substring(0, 4); // Extrae el año "YYYY"
        const month = parseInt(item.periodo.substring(5, 7)); // Extrae el mes (1-12)
        // Puedes agregar un identificador de lote si tu API lo envía en `tendenciasMensuales`
        // const loteId = item.lote_id; // Si existiera

        // Usaremos el año como la clave de la serie
        const seriesKey = year; // O `${year}-${loteId}` si quieres comparar por lote individual

        if (!series[seriesKey]) {
          // Inicializa la serie para este año con 12 meses, todos a 0
          series[seriesKey] = {
            name: `Año ${year}`, // Nombre de la serie para la leyenda
            data: Array(12).fill(0).map((_, i) => ({
              mes: i + 1,
              consumo_total_kwh: 0,
              costo_total: 0
            }))
          };
        }

        // Asegúrate de que el mes es válido (1-12)
        if (month >= 1 && month <= 12) {
          const monthIndex = month - 1; // Ajusta a índice de array (0-11)
          series[seriesKey].data[monthIndex].consumo_total_kwh += item.consumo_total_kwh || 0;
          series[seriesKey].data[monthIndex].costo_total += item.costo_total || 0;
        }
      });

      // Transforma el objeto de series en un array de series que el componente de gráfico pueda consumir
      return Object.values(series).map(serie => ({
        name: serie.name,
        // Ordena los datos por mes para asegurar la visualización correcta
        data: serie.data.sort((a, b) => a.mes - b.mes)
      }));
    },

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
    }
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
          this.estadisticasAnalisis.patron_mensual = estadisticasData.data.patron_mensual || []; // Usar este para el gráfico de líneas
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
      return `${(valor * 100).toFixed(1)}%`; // Si el valor viene como decimal (ej. 0.73)
    }
  },
};
</script>

<style scoped lang="scss">
// // ----------------------------------------
// // VARIABLES DE PALETA (Copiadas de tu VistaReportes.vue y ajustadas)
// // ----------------------------------------
// $PRIMARY-PURPLE: #8A2BE2;
// $SUCCESS-COLOR: #1ABC9C;
// $GRAY-COLD: #99A2AD;
// $LIGHT-TEXT: #E4E6EB;
// $DARK-TEXT: #333333;
// $SUBTLE-BG-DARK: #2B2B40; // Fondo de Tarjeta Oscura
// $BLUE-MIDNIGHT: #1A1A2E; // Fondo de Inputs Oscuros (y elementos más oscuros)
// $SUBTLE-BG-LIGHT: #FFFFFF;
// $WHITE-SOFT: #F7F9FC; 
// $DANGER-COLOR: #e74c3c;
// $WIDTH-SIDEBAR: 280px; 
// $WIDTH-CLOSED: 80px;
// $DARK-BG-CONTRAST: #1E1E30; 
// $BOX-SHADOW-DARK: 0 4px 15px rgba(0, 0, 0, 0.4); // Más pronunciado para oscuro
// $BOX-SHADOW-LIGHT: 0 4px 15px rgba(0, 0, 0, 0.1); // Más sutil para claro

// // Spacing & Border Radius
// $spacer: 1rem; // Ya definido en _variables.scss, pero aquí para contexto local
// $border-radius: 12px;
// $border-radius-sm: 8px;

// ----------------------------------------
// LAYOUT GENERAL Y TEMAS
// ----------------------------------------
.plataforma-layout {
  display: flex;
  min-height: 100vh;
  transition: background-color 0.3s;

  &.theme-light {
    background-color: $WHITE-SOFT; // Fondo de la página en tema claro
    --text-color-primary: #{$DARK-TEXT};
    --text-color-secondary: #{$GRAY-COLD};
    --card-bg: #{$SUBTLE-BG-LIGHT};
    --card-border: #f0f0f0;
    --shadow-color: rgba(0, 0, 0, 0.1);
    --table-bg: #{$SUBTLE-BG-LIGHT};
    --table-header-bg: #f8f9fa;
    --table-hover-bg: #e9ecef;
  }

  &.theme-dark {
    background-color: $DARK-BG-CONTRAST; // Fondo de la página en tema oscuro
    --text-color-primary: #{$LIGHT-TEXT};
    --text-color-secondary: #{$GRAY-COLD};
    --card-bg: #{$SUBTLE-BG-DARK};
    --card-border: #3a3a5a;
    --shadow-color: rgba(0, 0, 0, 0.4);
    --table-bg: #{$SUBTLE-BG-DARK};
    --table-header-bg: #{$BLUE-MIDNIGHT};
    --table-hover-bg: #3c4048;
  }
}

.plataforma-contenido {
  flex-grow: 1;
  margin-left: $WIDTH-CLOSED; // Sidebar colapsada por defecto
  padding: 0; // El padding se maneja dentro de .resumen-estadistico-container
  transition: margin-left 0.3s ease-in-out;

  &.shifted {
    margin-left: $WIDTH-SIDEBAR; // Sidebar expandida
  }
}

.resumen-estadistico-container {
  padding: 25px 40px 40px 40px; // Padding uniforme, similar a reportes-contenido
  position: relative;
  min-height: calc(100vh - 80px); // Ajuste para altura, asumiendo un encabezado de 80px
}

// ----------------------------------------
// ESTILOS DE CARGA Y ERRORES
// ----------------------------------------
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(var(--card-bg-rgb, 43, 43, 64), 0.9); // Usa la variable de fondo de tarjeta para consistencia
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
  border-radius: $border-radius;

  .spinner-border {
    width: 3.5rem;
    height: 3.5rem;
    color: $PRIMARY-PURPLE !important; // Usa tu color principal
    border-width: 0.3em;
  }

  .loading-text {
    margin-top: $spacer;
    color: var(--text-color-secondary);
    font-size: 1.2rem;
    font-weight: 500;
  }
}

.alert {
  padding: 1.25rem 1.5rem;
  border-radius: $border-radius-sm;
  font-size: 1rem;
  font-weight: 500;
  margin-top: 20px;
}

.alert-danger {
  background-color: rgba($DANGER-COLOR, 0.15);
  color: $DANGER-COLOR;
  border: 1px solid $DANGER-COLOR;
}

.alert-warning {
  background-color: rgba($warning-color, 0.15); // Si tienes $warning-color definida en _variables.scss
  color: $warning-color; // Asumiendo $warning-color de Bootstrap o tu _variables.scss
  border: 1px solid $warning-color;
}

// ----------------------------------------
// CARDS (GENERAL)
// ----------------------------------------
.card.chart-card {
  background-color: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: $border-radius;
  box-shadow: 0 4px 10px var(--shadow-color);
  padding: $spacer * 1.5;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: background-color 0.3s, border-color 0.3s, box-shadow 0.3s;

  .card-title {
    color: var(--text-color-primary);
    font-size: 1.35rem; // Un poco más grande
    margin-bottom: $spacer * 1.5;
    text-align: left; // Alineado a la izquierda como en la foto
    font-weight: 600;
    line-height: 1.2;
  }
  .card-subtitle {
    color: var(--text-color-secondary);
    font-size: 0.95rem;
    margin-bottom: $spacer;
    text-align: left;
  }
}

// ----------------------------------------
// TABLAS (Estilo de la imagen)
// ----------------------------------------
.table {
  width: 100%;
  margin-bottom: 1rem;
  color: var(--text-color-primary); // Color de texto principal de la tabla
  vertical-align: middle;
  border-color: var(--card-border); // Borde de las celdas

  th, td {
    padding: 1rem;
    border-bottom: 1px solid var(--card-border);
    white-space: nowrap; // Evita que el contenido de la tabla se rompa

    &:first-child {
      padding-left: 0; // Sin padding izquierdo para la primera columna
    }
    &:last-child {
      padding-right: 0; // Sin padding derecho para la última columna
    }
  }

  th {
    background-color: var(--table-header-bg); // Fondo del encabezado
    color: var(--text-color-primary); // Texto del encabezado
    font-weight: 600;
    text-align: left;
    border-top: none;
    border-bottom: 2px solid var(--card-border); // Borde inferior más fuerte para encabezado
  }

  tbody tr {
    transition: background-color 0.2s ease;
    &:hover {
      background-color: var(--table-hover-bg); // Fondo al pasar el ratón
    }
  }

  &.table-dark-custom { // Usamos un nombre más específico para evitar conflictos con Bootstrap
    --bs-table-bg: var(--table-bg);
    --bs-table-striped-bg: var(--table-bg);
    --bs-table-hover-bg: var(--table-hover-bg);
    --bs-table-color: var(--text-color-primary);
    th {
      background-color: var(--table-header-bg);
      color: var(--text-color-primary);
      border-color: var(--card-border);
    }
    td {
      border-color: var(--card-border);
    }
  }

  &.table-light-custom {
    --bs-table-bg: var(--table-bg);
    --bs-table-striped-bg: var(--table-bg);
    --bs-table-hover-bg: var(--table-hover-bg);
    --bs-table-color: var(--text-color-primary);
    th {
      background-color: var(--table-header-bg);
      color: var(--text-color-primary);
      border-color: var(--card-border);
    }
    td {
      border-color: var(--card-border);
    }
  }
}

.text-muted {
  color: var(--text-color-secondary) !important;
  font-style: italic;
  font-size: 0.9rem;
}

// Asegurar que las variables de Bootstrap se inyecten correctamente si usas Bootstrap
// $theme-colors: (
//   "primary": $PRIMARY-PURPLE,
//   "success": $SUCCESS-COLOR,
//   "danger": $DANGER-COLOR,
//   "warning": $warning-color, // Asegúrate de que $warning-color esté definido si se usa
// );
</style>