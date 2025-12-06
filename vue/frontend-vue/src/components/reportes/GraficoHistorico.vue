<template>
  <div class="chart-card" :class="{ 'theme-dark': isDark }">
    <h4 class="chart-title">{{ chartTitle }}</h4>
    
    <div v-if="loading" class="chart-loading">
      <i class="bi bi-arrow-clockwise fa-spin"></i> Cargando datos...
    </div>
    <div v-else-if="error" class="chart-error">{{ error }}</div>
    
    <div v-else class="chart-wrapper">
      <v-chart :option="chartOption" autoresize />
    </div>
  </div>
</template>

<script>
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent, 
  MarkPointComponent, 
  MarkLineComponent
} from 'echarts/components';
import VChart from 'vue-echarts';
import { ref, watch, computed } from 'vue';

// Registro de componentes de ECharts
use([
  CanvasRenderer, LineChart, TitleComponent, TooltipComponent, 
  LegendComponent, GridComponent, DataZoomComponent,
  MarkPointComponent, MarkLineComponent
]);

export default {
  name: 'GraficoHistorico',
  components: { VChart },
  props: {
    campoId: { type: Number, required: true },
    titulo: { type: String, default: 'Histórico de Datos' },
    fechaInicio: { type: String, required: true },
    fechaFin: { type: String, required: true },
    isDark: { type: Boolean, default: false },
    metodoCarga: { type: String, default: 'optimizado' },
    incluirAnalisis: { type: Boolean, default: false } 
  },
  
  setup(props) {
    const loading = ref(true);
    const error = ref(null);
    const chartOption = ref({});
    const chartTitle = ref(props.titulo);

    // Colores del tema
    const gridColor = computed(() => props.isDark ? 'rgba(228, 230, 235, 0.2)' : 'rgba(51, 51, 51, 0.2)');
    const textColor = computed(() => props.isDark ? '#E4E6EB' : '#333333');

    // --- LÓGICA PRINCIPAL DE CARGA DE DATOS ---
    const cargarDatosHistoricos = async () => {
      // 1. Validaciones
      if (!props.campoId || props.campoId <= 0) {
        loading.value = false;
        error.value = 'ID de campo no válido.';
        return;
      }
      if (!props.fechaInicio || !props.fechaFin) {
        loading.value = false;
        error.value = 'Rango de fechas no válido.';
        return; 
      }

      loading.value = true;
      error.value = null;
      let valores = []; // 🟢 CORRECCIÓN: Definimos variable fuera del try para que el catch la vea

      const token = localStorage.getItem('accessToken');
      const url = new URL(`${API_BASE_URL}/api/valores/historico-campo/${props.campoId}`);
      url.searchParams.append('fecha_inicio', props.fechaInicio);
      url.searchParams.append('fecha_fin', props.fechaFin);
      url.searchParams.append('metodo_carga', props.metodoCarga); 
      url.searchParams.append('incluir_analisis', props.incluirAnalisis.toString());

      try {
        const response = await fetch(url.toString(), {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Fallo al cargar datos del gráfico.');
        
        valores = await response.json();
        
        if (!valores || valores.length === 0) {
          chartOption.value = {}; 
          throw new Error('No se encontraron valores históricos para este rango.');
        }

        // 3. Procesar datos
        const primerValor = valores[0];
        const magnitud = primerValor.magnitud_tipo || props.titulo;
        const simbolo = primerValor.simbolo_unidad || ''; 
        chartTitle.value = `${magnitud} (${simbolo})`;

        // A. Datos de la Línea
        const dataPoints = valores.map(v => [
          v.fecha_hora_lectura, 
          parseFloat(v.valor)
        ]);

        // B. Datos de Anomalías (Pines Rojos)
        const anomaliasDetectadas = valores.filter(v => v.anomalia === true);
        
        // 🟢 DEBUG: Muestra en consola cuántas anomalías llegaron
        console.log(`[Gráfico] Total datos: ${valores.length}, Anomalías: ${anomaliasDetectadas.length}`);

        const puntosAnomalos = anomaliasDetectadas.map(v => ({
            // 🟢 CORRECCIÓN: 'coord' es más preciso que xAxis/yAxis para series de tiempo
            coord: [v.fecha_hora_lectura, parseFloat(v.valor)],
            value: parseFloat(v.valor).toFixed(1), // Redondear valor visual
            name: 'Anomalía',
            itemStyle: { color: '#ff4500' },
            tooltip: { 
                formatter: `⚠️ ${v.mensaje_alerta || 'Valor Atípico'}` 
            }
        }));

        actualizarOpciones(dataPoints, magnitud, puntosAnomalos);

      } catch (err) {
        error.value = err.message;
        if(valores.length === 0) chartOption.value = {};
      } finally {
        loading.value = false;
      }
    };

    // --- FUNCIÓN PARA CONSTRUIR EL GRÁFICO ---
    const actualizarOpciones = (data, magnitud, anomalias = []) => {
      chartOption.value = {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' }
        },
        grid: {
          left: '50px', right: '20px', bottom: '70px', top: '40px', // 🟢 Ajuste de márgenes para que quepan los pines
          containLabel: true
        },
        xAxis: {
          type: 'time',
          boundaryGap: false,
          axisLine: { lineStyle: { color: gridColor.value } },
          axisLabel: { color: textColor.value }
        },
        yAxis: {
          type: 'value',
          scale: true,
          axisLabel: { color: textColor.value },
          splitLine: { lineStyle: { color: gridColor.value } }
        },
        dataZoom: [
          { type: 'slider', bottom: 10, height: 25 },
          { type: 'inside' }
        ],
        series: [{
          name: magnitud,
          data: data,
          type: 'line',
          showSymbol: false, 
          color: '#8A2BE2',
          lineStyle: { width: 2 },
          
          markPoint: {
            data: anomalias,
            symbol: 'pin',
            symbolSize: 40,
            symbolOffset: [0, -10], // 🟢 Levantar un poco el pin para que apunte al dato
            label: {
                show: true,
                fontSize: 10,
                color: '#fff',
                formatter: '{c}' 
            }
          }
        }]
      };
    };

    watch(
      () => [props.campoId, props.fechaInicio, props.fechaFin, props.metodoCarga, props.incluirAnalisis], 
      cargarDatosHistoricos, 
      { immediate: true } 
    );

    watch(
      () => props.isDark, 
      () => {
        if (chartOption.value && chartOption.value.series) {
            const serie = chartOption.value.series[0];
            actualizarOpciones(serie.data, serie.name, serie.markPoint?.data);
        }
      }
    );

    return { loading, error, chartOption, chartTitle };
  }
}
</script>

<style scoped lang="scss">
$PRIMARY-PURPLE: #8A2BE2;
$GRAY-COLD: #99A2AD;
$LIGHT-TEXT: #E4E6EB;
$DARK-TEXT: #333333;
$SUBTLE-BG-DARK: #2B2B40;
$SUBTLE-BG-LIGHT: #FFFFFF;
$DANGER-COLOR: #e74c3c;

.chart-card {
    border-radius: 12px;
    padding: 20px;
    height: 380px; /* Un poco más de altura para el dataZoom */
    display: flex;
    flex-direction: column;
    transition: background-color 0.3s, box-shadow 0.3s;
}
.chart-wrapper {
    position: relative;
    flex-grow: 1;
    width: 100%;
    height: 100%; /* Asegura que ECharts tome el espacio */
}
.chart-title {
    font-size: 1.1rem; /* Título más sutil */
    font-weight: 600;
    margin-bottom: 15px;
}
.chart-loading, .chart-error {
    text-align: center;
    margin: auto; /* Centrar vertical y horizontalmente */
    font-style: italic;
}
.chart-error {
    color: $DANGER-COLOR;
}

/* ------------------- TEMAS ------------------- */
.theme-light .chart-card {
    background-color: $SUBTLE-BG-LIGHT;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    color: $DARK-TEXT;
}
.theme-dark .chart-card {
    background-color: $SUBTLE-BG-DARK;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    color: $LIGHT-TEXT;
}
.theme-dark .chart-title {
    color: $LIGHT-TEXT;
}
.theme-dark .chart-loading, .theme-dark .chart-error {
    color: $GRAY-COLD;
}
</style>