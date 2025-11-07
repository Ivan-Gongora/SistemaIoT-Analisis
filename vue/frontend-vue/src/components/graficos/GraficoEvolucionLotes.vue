<template>
  <div class="card chart-card mt-4" :class="{ 'theme-dark': isDark }">
    <div class="card-body">
      <h5 class="card-title">Evolución Histórica de {{ getMetricaTitulo(metricaSeleccionada) }} por Lote</h5>
      <h6 class="card-subtitle mb-2 text-muted">Datos de {{ datosEvolucion.labels[0] }} a {{ datosEvolucion.labels[datosEvolucion.labels.length - 1] }}</h6>
      <v-chart class="chart" :option="chartOption" autoresize />
    </div>
  </div>
</template>

<script>
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import {
  GridComponent, TooltipComponent, LegendComponent, TitleComponent, DataZoomComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';

// Registrar los componentes de ECharts que se usarán
use([
  CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent, DataZoomComponent
]);

export default {
  name: 'GraficoEvolucionLotes',
  components: {
    VChart,
  },
  props: {
    // 🎯 Recibe los datos ya preparados para ECharts
    datosEvolucion: { 
      type: Object, // { labels: string[], series: EChartsSeriesOption[] }
      required: true,
    },
    metricaSeleccionada: {
      type: String, // 'consumo_total_kwh', 'costo_total', etc.
      required: true,
    },
    isDark: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      chartOption: {},
    };
  },
  watch: {
    datosEvolucion: { handler: 'updateChart', deep: true },
    metricaSeleccionada: 'updateChart',
    isDark: 'updateChart',
  },
  mounted() {
    this.updateChart();
  },
  methods: {
    // Métodos auxiliares para obtener títulos y unidades
    getMetricaTitulo(key) {
      const titles = {
        'consumo_total_kwh': 'Consumo Eléctrico',
        'costo_total': 'Costo Total',
        'demanda_maxima_kw': 'Demanda Máxima',
        'factor_potencia': 'Factor de Potencia',
        // Agrega más métricas si tienes
      };
      return titles[key] || key;
    },
    getMetricaUnidad(key) {
      const units = {
        'consumo_total_kwh': ' kWh',
        'costo_total': ' MXN',
        'demanda_maxima_kw': ' kW',
        'factor_potencia': '%',
        // Agrega más unidades
      };
      return units[key] || '';
    },

    updateChart() {
      const { labels, series } = this.datosEvolucion;
      
      // Si no hay datos, muestra un gráfico vacío o un mensaje
      if (!labels || labels.length === 0) {
        this.chartOption = { title: { text: 'No hay datos para mostrar', left: 'center', top: 'center', textStyle: { color: this.isDark ? '#AAA' : '#555' } } };
        return;
      }

      const unit = this.getMetricaUnidad(this.metricaSeleccionada);
      const textColor = this.isDark ? '#E4E6EB' : '#333333'; // LIGHT-TEXT vs DARK-TEXT
      const axisColor = this.isDark ? '#99A2AD' : '#555555'; // GRAY-COLD
      const gridLineColor = this.isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
      
      this.chartOption = {
        title: {
          show: false, // El título se maneja en el template Vue
        },
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            let tooltipContent = `${params[0].name}<br/>`; // Muestra la fecha (ej: 2021-01)
            params.forEach(item => {
              tooltipContent += `${item.marker} ${item.seriesName}: ${item.value.toLocaleString('es-MX')}${unit}<br/>`;
            });
            return tooltipContent;
          },
          backgroundColor: this.isDark ? 'rgba(43,43,64,0.85)' : 'rgba(255,255,255,0.85)',
          borderColor: this.isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
          textStyle: {
            color: textColor,
          },
        },
        legend: {
          data: series.map(s => s.name),
          textStyle: { color: textColor },
          top: 'bottom',
          padding: [10, 0, 0, 0], // Pequeño padding para no pegar al borde
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%', // Deja espacio para la leyenda y el dataZoom
          containLabel: true,
        },
        xAxis: {
          type: 'category',
          data: labels, // Todas las fechas de la línea de tiempo
          boundaryGap: false,
          axisLine: { lineStyle: { color: axisColor } },
          axisLabel: { color: axisColor },
          splitLine: { show: false }, // No mostrar líneas de división verticales
        },
        yAxis: {
          type: 'value',
          name: `${this.getMetricaTitulo(this.metricaSeleccionada)} (${unit.trim()})`,
          axisLine: { lineStyle: { color: axisColor } },
          axisLabel: {
            formatter: `{value}${unit}`,
            color: axisColor,
          },
          splitLine: { lineStyle: { color: gridLineColor } }, // Líneas de división horizontales
        },
        series: series, // Aquí se pasan todas las series (una por lote)
        backgroundColor: 'transparent',
        // DataZoom para permitir navegación en la línea de tiempo larga
        dataZoom: [
          {
            type: 'slider', // Barra de desplazamiento para zoom
            xAxisIndex: 0,
            filterMode: 'filter',
            startValue: labels[labels.length - 12], // Muestra los últimos 12 meses por defecto
            endValue: labels[labels.length - 1],
            textStyle: { color: axisColor },
          },
          {
            type: 'inside', // Zoom con rueda del ratón
            xAxisIndex: 0,
            filterMode: 'filter',
          },
        ],
      };
    },
  },
};
</script>

<style scoped lang="scss">
// @import '@/assets/styles/_variables.scss'; // Asegúrate de importar tus variables globales
// // Si no tienes _variables.scss globales, define aquí las que necesites:
// $PRIMARY-PURPLE: #8A2BE2;
// $SUCCESS-COLOR: #1ABC9C;
// $GRAY-COLD: #99A2AD;
// $LIGHT-TEXT: #E4E6EB;
// $DARK-TEXT: #333333;
// $SUBTLE-BG-DARK: #2B2B40; 
// $SUBTLE-BG-LIGHT: #FFFFFF;
// $border-radius: 12px;
// $spacer: 1rem;

.chart-card {
  background-color: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: $border-radius;
  box-shadow: 0 4px 10px var(--shadow-color);
  padding: $spacer * 1.5;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: background-color 0.3s, border-color 0.3s, box-shadow 0.3s;
}

.chart-card .card-body {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  padding: 0; // El padding ya lo maneja el .chart-card
}

.chart-card .card-title {
  color: var(--text-color-primary);
  font-size: 1.35rem; 
  margin-bottom: $spacer * 0.5;
  text-align: left;
  font-weight: 600;
  line-height: 1.2;
}
.chart-card .card-subtitle {
  color: var(--text-color-secondary);
  font-size: 0.95rem;
  margin-bottom: $spacer * 1.5;
  text-align: left;
}

.chart {
  flex-grow: 1;
  min-height: 350px; // Altura mínima para el gráfico
  width: 100%;
}
</style>