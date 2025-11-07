<template>
  <div class="chart-card" :class="{ 'theme-dark': isDark }">
    <h5 class="card-title">{{ titulo }}</h5>
    <v-chart class="chart" :option="chartOption" autoresize />
  </div>
</template>

<script>
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart } from 'echarts/charts';
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';

use([
  CanvasRenderer,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
]);

export default {
  name: 'GraficoBarrasComparativas',
  components: {
    VChart,
  },
  props: {
    titulo: { type: String, default: 'Gráfico de Barras' },
    datosAnuales: {
      type: Object, // { '2021': { consumo_total_kwh: X, costo_total: Y }, '2022': { ... } }
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
    datosAnuales: { handler: 'crearChartOption', deep: true },
    isDark: 'crearChartOption',
  },
  mounted() {
    this.crearChartOption();
  },
  methods: {
    crearChartOption() {
      const anos = Object.keys(this.datosAnuales).sort(); // Ordenar años
      const consumoData = anos.map(year => this.datosAnuales[year].consumo_total_kwh || 0);
      const costoData = anos.map(year => this.datosAnuales[year].costo_total || 0);

      const textColor = this.isDark ? '#FFF' : '#333';
      const axisColor = this.isDark ? '#AAA' : '#555';
      const lineColor = this.isDark ? '#444' : '#CCC';
      const splitLineColor = this.isDark ? '#333' : '#EEE';

      this.chartOption = {
        color: ['#8A2BE2', '#00C853'], // Violeta y Verde, similar a la imagen
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: function (params) {
            let tooltip = `<b>${params[0].name}</b><br/>`; // Año
            params.forEach(item => {
              let value = item.value;
              let unit = '';
              if (item.seriesName === 'Consumo Total (kWh)') {
                unit = ' kWh';
              } else if (item.seriesName === 'Costo Total (MXN)') {
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
          data: ['Consumo Total (kWh)', 'Costo Total (MXN)'],
          textStyle: { color: axisColor },
          top: 'bottom',
        },
        xAxis: {
          type: 'category',
          data: anos,
          axisLabel: { color: axisColor },
          axisLine: { lineStyle: { color: lineColor } },
        },
        yAxis: [
          {
            type: 'value',
            name: 'Consumo (kWh)',
            axisLabel: { formatter: '{value} kWh', color: axisColor },
            axisLine: { lineStyle: { color: lineColor } },
            splitLine: { lineStyle: { color: splitLineColor } },
            nameTextStyle: { color: axisColor }
          },
          {
            type: 'value',
            name: 'Costo (MXN)',
            axisLabel: { formatter: '{value} MXN', color: axisColor },
            axisLine: { lineStyle: { color: lineColor } },
            splitLine: { lineStyle: { color: splitLineColor } },
            nameTextStyle: { color: axisColor }
          }
        ],
        series: [
          {
            name: 'Consumo Total (kWh)',
            type: 'bar',
            data: consumoData,
            yAxisIndex: 0,
            itemStyle: {
              borderRadius: 5,
            },
            label: {
              show: false, // Opcional, si quieres mostrar el valor encima de la barra
              position: 'top',
              formatter: '{c} kWh',
              color: textColor
            }
          },
          {
            name: 'Costo Total (MXN)',
            type: 'bar',
            data: costoData,
            yAxisIndex: 1,
            itemStyle: {
              borderRadius: 5,
            },
            label: {
              show: false, // Opcional
              position: 'top',
              formatter: '{c} MXN',
              color: textColor
            }
          }
        ],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          containLabel: true
        },
        backgroundColor: 'transparent'
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
.chart {
  flex-grow: 1;
  min-height: 300px; // Altura mínima para el gráfico
}
</style>