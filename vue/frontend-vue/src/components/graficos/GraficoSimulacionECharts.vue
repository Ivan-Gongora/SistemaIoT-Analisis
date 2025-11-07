<template>
  <div class="chart-card" :class="{ 'theme-dark': isDark }">
    <div class="card-body">
  
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

// Registrar los componentes de ECharts
use([
  CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent, DataZoomComponent
]);

export default {
  name: 'GraficoSimulacionECharts',
  components: { VChart },
  props: {
    chartData: {
      type: Object,
      required: true,
    },
    isDark: Boolean,
  },
  data() {
    return { chartOption: {} };
  },
  watch: {
    chartData: { handler: 'crearChartOption', deep: true },
    isDark: 'crearChartOption',
  },
  mounted() {
    this.crearChartOption();
  },
  methods: {
    crearChartOption() {
      const { labels, datasets } = this.chartData;
      if (!labels || labels.length === 0 || !datasets || datasets.length < 2) {
        this.chartOption = {};
        return;
      }
      
      const textColor = this.isDark ? '#E4E6EB' : '#333333';
      const axisColor = this.isDark ? '#99A2AD' : '#555555';
      const gridLineColor = this.isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
      const colorBase = this.isDark ? '#99A2AD' : '#B0B0B0'; // Gris base
      const colorSimulado = '#8A2BE2'; // Morado principal

      this.chartOption = {
        color: [colorBase, colorSimulado],
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            let tooltipContent = `<b>Periodo: ${params[0].name}</b><br/>`;
            params.forEach(item => {
              const value = item.value;
              tooltipContent += `${item.marker} ${item.seriesName}: <b>${value.toLocaleString('es-MX', { style: 'currency', currency: 'MXN', minimumFractionDigits: 0 })}</b><br/>`;
            });
            return tooltipContent;
          },
          backgroundColor: this.isDark ? 'rgba(43,43,64,0.85)' : 'rgba(255,255,255,0.85)',
          textStyle: { color: textColor },
        },
        legend: {
          data: datasets.map(d => d.label),
          textStyle: { color: textColor },
          top: 30,
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
          axisLabel: { color: axisColor, rotate: 45 },
          axisLine: { lineStyle: { color: axisColor } },
          splitLine: { show: false },
        },
        yAxis: {
          type: 'value',
          name: 'Costo Proyectado (MXN)',
          axisLabel: { formatter: (value) => value.toLocaleString('es-MX', { style: 'currency', currency: 'MXN', minimumFractionDigits: 0 }), color: axisColor },
          axisLine: { lineStyle: { color: axisColor } },
          splitLine: { lineStyle: { color: gridLineColor } },
        },
        series: [
          {
            name: datasets[0].label, // Costo Base
            type: 'line',
            data: datasets[0].data,
            smooth: true,
            lineStyle: { width: 2, type: 'dashed' }, // Línea base más sutil
            itemStyle: { color: colorBase },
          },
          {
            name: datasets[1].label, // Costo Simulado
            type: 'line',
            data: datasets[1].data,
            smooth: true,
            lineStyle: { width: 4 }, // Línea simulada más gruesa
            itemStyle: { color: colorSimulado },
            areaStyle: { // Relleno de área debajo de la línea simulada
              opacity: 0.3,
              color: colorSimulado
            },
          }
        ],
        backgroundColor: 'transparent',
        dataZoom: [{ type: 'slider', xAxisIndex: 0, start: 0, end: 100, textStyle: { color: axisColor } }, { type: 'inside', xAxisIndex: 0, start: 0, end: 100 }],
      };
    },
  },
};
</script>

<style scoped>
/* Estilos necesarios para que la card se vea bien en esta vista */
.chart-card {
  height: 100%;
  min-height: 450px; 
  display: flex;
  flex-direction: column;
  background-color: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  box-shadow: 0 4px 10px var(--shadow-color);
  padding: 1.5rem;
}
.chart-card .card-title {
  color: var(--text-color-primary);
  font-size: 1.35rem; 
  margin-bottom: 1.5rem;
  text-align: left;
  font-weight: 600;
}
.chart {
  flex-grow: 1;
  min-height: 350px;
}
</style>