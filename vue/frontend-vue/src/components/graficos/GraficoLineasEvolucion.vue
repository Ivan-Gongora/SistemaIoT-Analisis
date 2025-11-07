<template>
  <div class="chart-card" :class="{ 'theme-dark': isDark }">
    <h5 class="card-title">{{ titulo }}</h5>
    <h6 class="card-subtitle mb-2 text-muted">{{ subtitulo }}</h6>
    <v-chart class="chart" :option="chartOption" autoresize />
  </div>
</template>

<script>
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, LineChart } from 'echarts/charts'; // Usamos Bar y Line
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  DataZoomComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';

use([
  CanvasRenderer,
  BarChart, // Para las barras de consumo
  LineChart, // Para la línea de costo
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  DataZoomComponent,
]);

export default {
  name: 'GraficoLineasEvolucion',
  components: {
    VChart,
  },
  props: {
    titulo: { type: String, default: 'Gráfico de Líneas' },
    subtitulo: { type: String, default: '' },
    datosMensuales: {
      type: Array, // Expected: [{ name: 'Lote X', data: [{ consumo_total_kwh: Y, costo_total: Z }, ... ] }]
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
    datosMensuales: { handler: 'crearChartOption', deep: true },
    isDark: 'crearChartOption',
  },
  mounted() {
    this.crearChartOption();
  },
  methods: {
    crearChartOption() {
      const meses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
      ];

      const textColor = this.isDark ? '#FFF' : '#333';
      const axisColor = this.isDark ? '#AAA' : '#555';
      const lineColor = this.isDark ? '#444' : '#CCC';
      const splitLineColor = this.isDark ? '#333' : '#EEE';

      // Asumiendo que `datosMensuales` es un array con un solo objeto
      // que contiene la data de consumo y costo para el "Histórico"
      const consumoData = this.datosMensuales[0]?.data.map(d => d.consumo_total_kwh) || Array(12).fill(0);
      const costoData = this.datosMensuales[0]?.data.map(d => d.costo_total) || Array(12).fill(0);

      this.chartOption = {
        color: ['#8A2BE2', '#00C853'], // Violeta para consumo, Verde para costo
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            crossStyle: {
              color: '#999'
            }
          },
          formatter: function (params) {
            let tooltip = `<b>${params[0].name}</b><br/>`; // Mes
            params.forEach(item => {
              let value = item.value;
              let unit = '';
              if (item.seriesName === 'Consumo (kWh)') {
                unit = ' kWh';
              } else if (item.seriesName === 'Costo (MXN)') {
                unit = ' MXN';
              }
              tooltip += `${item.marker} ${item.seriesName}: <b>${value.toLocaleString()}${unit}</b><br/>`;
            });
            return tooltip;
          },
          backgroundColor: this.isDark ? 'rgba(50,50,50,0.7)' : 'rgba(255,255,255,0.7)',
          textStyle: { color: textColor }
        },
        legend: {
          data: ['Consumo (kWh)', 'Costo (MXN)'],
          textStyle: { color: axisColor },
          top: 'bottom',
        },
        xAxis: [
          {
            type: 'category',
            data: meses,
            axisPointer: {
              type: 'shadow'
            },
            axisLabel: { color: axisColor },
            axisLine: { lineStyle: { color: lineColor } },
          }
        ],
        yAxis: [
          {
            type: 'value',
            name: 'Consumo (kWh)',
            min: 0,
            axisLabel: { formatter: '{value} kWh', color: axisColor },
            axisLine: { lineStyle: { color: lineColor } },
            splitLine: { lineStyle: { color: splitLineColor } },
            nameTextStyle: { color: axisColor }
          },
          {
            type: 'value',
            name: 'Costo (MXN)',
            min: 0,
            axisLabel: { formatter: '{value} MXN', color: axisColor },
            axisLine: { lineStyle: { color: lineColor } },
            splitLine: { lineStyle: { color: splitLineColor } },
            nameTextStyle: { color: axisColor }
          }
        ],
        series: [
          {
            name: 'Consumo (kWh)',
            type: 'bar',
            tooltip: {
              valueFormatter: function (value) {
                return value + ' kWh';
              }
            },
            data: consumoData,
            itemStyle: {
              borderRadius: 5,
            },
          },
          {
            name: 'Costo (MXN)',
            type: 'line',
            yAxisIndex: 1,
            tooltip: {
              valueFormatter: function (value) {
                return value + ' MXN';
              }
            },
            data: costoData,
            smooth: true,
            symbol: 'circle', // Puntos en la línea
            symbolSize: 8,
            lineStyle: {
              width: 3,
            }
          }
        ],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          containLabel: true
        },
        backgroundColor: 'transparent',
        dataZoom: [
          {
            type: 'slider',
            xAxisIndex: 0,
            start: 0,
            end: 100,
            textStyle: { color: axisColor }
          },
          {
            type: 'inside',
            xAxisIndex: 0,
            start: 0,
            end: 100
          }
        ],
      };
    },
  },
};
</script>

<style scoped lang="scss">
.chart-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-subtitle {
  text-align: center;
  color: var(--color-text);
  font-size: 0.9rem;
}

.chart {
  flex-grow: 1;
  min-height: 300px;
}
</style>