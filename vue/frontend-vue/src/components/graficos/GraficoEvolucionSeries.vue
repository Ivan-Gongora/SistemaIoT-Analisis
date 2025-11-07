<template>
  <div class="card chart-card mt-4" :class="{ 'theme-dark': isDark }">
    <div class="card-body">
      <h5 class="card-title">{{ titulo }}</h5>
      <v-chart class="chart" :option="chartOption" autoresize />
    </div>
  </div>
</template>

<script>
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import {
  GridComponent, TooltipComponent, LegendComponent, DataZoomComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent, DataZoomComponent]);

export default {
  name: 'GraficoEvolucionSeries',
  components: { VChart },
  props: {
    titulo: String,
    // La estructura de datos esperada de `datosEvolucionPorLote`
    datosEvolucion: { 
      type: Object, // { labels: string[], series: EChartsSeriesOption[] }
      required: true,
    },
    metricaSeleccionada: String, // Para personalizar el eje Y y tooltips
    isDark: Boolean,
  },
  data() {
    return { chartOption: {} };
  },
  watch: {
    datosEvolucion: { handler: 'crearChartOption', deep: true },
    metricaSeleccionada: 'crearChartOption',
    isDark: 'crearChartOption',
  },
  mounted() {
    this.crearChartOption();
  },
  methods: {
    getMetricaTitulo(key) {
      const titles = {
        'consumo_total_kwh': 'Consumo Eléctrico',
        'costo_total': 'Costo Total',
        'demanda_maxima_kw': 'Demanda Máxima',
        'factor_potencia': 'Factor de Potencia',
      };
      return titles[key] || key;
    },
    getMetricaUnidad(key) {
      const units = {
        'consumo_total_kwh': ' kWh',
        'costo_total': ' MXN',
        'demanda_maxima_kw': ' kW',
        'factor_potencia': '%',
      };
      return units[key] || '';
    },
    
    crearChartOption() {
      const { labels, series } = this.datosEvolucion;
      
      // Manejo de casos sin datos o con pocos datos
      if (!labels || labels.length < 1) {
        this.chartOption = { title: { text: 'Seleccione lotes para ver la evolución.', left: 'center', top: 'center' } };
        return;
      }

      const unit = this.getMetricaUnidad(this.metricaSeleccionada);
      const metricTitle = this.getMetricaTitulo(this.metricaSeleccionada);
      const textColor = this.isDark ? '#E4E6EB' : '#333333';
      const axisColor = this.isDark ? '#99A2AD' : '#555555';
      const gridLineColor = this.isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';

      this.chartOption = {
        color: ['#8A2BE2', '#1ABC9C', '#FFC107', '#E74C3C', '#3498DB', '#9B59B6', '#F1C40F', '#2ECC71'], // Paleta de colores para múltiples series
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            let tooltipContent = `<b>Periodo: ${params[0].name}</b><br/>`;
            params.forEach(item => {
              // Asumimos que el `item.value` de la serie es la `metricaSeleccionada`
              tooltipContent += `${item.marker} ${item.seriesName}: <b>${item.value.toLocaleString('es-MX', { maximumFractionDigits: 2 })}${unit}</b><br/>`;
            });
            return tooltipContent;
          },
          backgroundColor: this.isDark ? 'rgba(43,43,64,0.85)' : 'rgba(255,255,255,0.85)',
          borderColor: this.isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
          textStyle: { color: textColor },
        },
        legend: {
          data: series.map(s => s.name),
          textStyle: { color: textColor },
          top: 30, // Leyenda en la parte superior del gráfico
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: '20%',
          containLabel: true,
        },
        xAxis: {
          type: 'category',
          data: labels,
          boundaryGap: false,
          axisLabel: { color: axisColor },
          axisLine: { lineStyle: { color: axisColor } },
          splitLine: { show: false },
        },
        yAxis: {
          type: 'value',
          name: `${metricTitle} (${unit.trim()})`,
          axisLabel: {
            formatter: `{value}${unit}`,
            color: axisColor,
          },
          axisLine: { lineStyle: { color: axisColor } },
          splitLine: { lineStyle: { color: gridLineColor } },
        },
        series: series, // ECharts recibe directamente el array de series
        backgroundColor: 'transparent',
        dataZoom: [
          { 
            type: 'slider', 
            xAxisIndex: 0, 
            start: 0, 
            end: 100, // Inicialmente muestra todo
            textStyle: { color: axisColor } 
          },
          { 
            type: 'inside', 
            xAxisIndex: 0, 
            start: 0, 
            end: 100 
          },
        ],
      };
    },
  },
};
</script>

<style scoped>
/* Estilos similares a los anteriores, si necesitas: */
.chart-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.chart-card .card-title {
  text-align: left;
}
.chart {
  flex-grow: 1;
  min-height: 350px; 
  width: 100%;
}
</style>