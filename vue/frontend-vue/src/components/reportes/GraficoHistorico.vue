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
  DataZoomComponent, // 👈 Para el Zoom/Drill-down
} from 'echarts/components';
import VChart from 'vue-echarts';
import { ref, watch, onMounted, computed } from 'vue';

// Registro de componentes de ECharts
use([
  CanvasRenderer, LineChart, TitleComponent, TooltipComponent, 
  LegendComponent, GridComponent, DataZoomComponent
]);


export default {
  name: 'GraficoHistorico',
  components: { VChart },
  props: {
    campoId: { type: Number, required: true },
    titulo: { type: String, default: 'Histórico de Datos' },
    fechaInicio: { type: String, required: true }, // ISO String
    fechaFin: { type: String, required: true },   // ISO String
    isDark: { type: Boolean, default: false }
  },
  
  setup(props) {
    const loading = ref(true);
    const error = ref(null);
    const chartOption = ref({});
    const chartTitle = ref(props.titulo); // Título dinámico

    // Colores del tema
    const gridColor = computed(() => props.isDark ? 'rgba(228, 230, 235, 0.2)' : 'rgba(51, 51, 51, 0.2)');
    const textColor = computed(() => props.isDark ? '#E4E6EB' : '#333333');

    // --- LÓGICA PRINCIPAL DE CARGA DE DATOS ---
   const cargarDatosHistoricos = async () => {
  // 1. Validar que tenemos un ID
  if (!props.campoId || props.campoId <= 0) {
    loading.value = false;
    error.value = 'ID de campo no válido.';
    return;
  }
  // 🚨 NUEVA VALIDACIÓN: Validar fechas
      if (!props.fechaInicio || !props.fechaFin) {
        loading.value = false;
        error.value = 'Rango de fechas no válido.';
        return; 
      }
  loading.value = true;
  error.value = null;
  const token = localStorage.getItem('accessToken');

  // 🚨 CORRECCIÓN: Mover la construcción de la URL aquí (ANTES de usarla)
  const url = new URL(`${API_BASE_URL}/api/valores/historico-campo/${props.campoId}`);
  url.searchParams.append('fecha_inicio', props.fechaInicio);
  url.searchParams.append('fecha_fin', props.fechaFin);

  try {
    // Ahora 'url' ya está definida y se puede usar
    const response = await fetch(url.toString(), {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!response.ok) throw new Error('Fallo al cargar datos del gráfico.');
    
    const valores = await response.json();
    
    if (valores.length === 0) {
      chartOption.value = {}; // Limpia el gráfico
      throw new Error('No se encontraron valores históricos para este rango.');
    }

    // 3. Procesar datos para ECharts
    const primerValor = valores[0];
    const magnitud = primerValor.magnitud_tipo || props.titulo;
    // 🚨 CORRECCIÓN: Asumir que el backend devuelve 'simbolo_unidad'
    const simbolo = primerValor.simbolo_unidad || ''; 
    chartTitle.value = `${magnitud} (${simbolo})`; // Actualiza el título
    
    // ECharts prefiere pares [timestamp, valor]
    const dataPoints = valores.map(v => [
      v.fecha_hora_lectura, 
      parseFloat(v.valor)
    ]);

    // 4. Actualizar las opciones del gráfico
    actualizarOpciones(dataPoints, magnitud);

  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

    // --- FUNCIÓN PARA CONSTRUIR EL GRÁFICO ECHARTS ---
    const actualizarOpciones = (data, magnitud) => {
      chartOption.value = {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' }
        },
        grid: {
          left: '50px', // Espacio para el eje Y
          right: '20px',
          bottom: '70px' // Espacio para el DataZoom
        },
        xAxis: {
          type: 'time',
          axisLine: { lineStyle: { color: gridColor.value } },
          axisLabel: { color: textColor.value }
        },
        yAxis: {
          type: 'value',
          scale: true, // Permite que el eje se ajuste
          axisLabel: { 
            color: textColor.value,
            formatter: '{value}' // Aquí podrías añadir el símbolo si es fijo
          },
          splitLine: { lineStyle: { color: gridColor.value } }
        },
        // 🚨 CRÍTICO: Habilita el Zoom y el Drill-down
        dataZoom: [
          {
            type: 'slider', // Barra de deslizamiento inferior
            start: 0,
            end: 100,
            bottom: 10,
            height: 25,
            backgroundColor: props.isDark ? 'rgba(43, 43, 64, 0.5)' : 'rgba(255, 255, 255, 0.5)',
            borderColor: gridColor.value,
            textStyle: { color: textColor.value }
          },
          {
            type: 'inside' // Zoom con la rueda del ratón
          }
        ],
        series: [{
          name: magnitud,
          data: data,
          type: 'line',
          showSymbol: false,
          color: '#8A2BE2', // Color púrpura
          lineStyle: { width: 2 },
        }]
      };
    };

    // --- WATCHERS ---
    // Observa los props y recarga el gráfico si cambian
    watch(
      () => [props.campoId, props.fechaInicio, props.fechaFin], 
      cargarDatosHistoricos, 
      { immediate: true } // Carga los datos al montar
    );

    // Observa el tema para cambiar colores
    watch(
      () => props.isDark, 
      () => {
        // Recarga las opciones con los nuevos colores
        if (chartOption.value && chartOption.value.series) {
          actualizarOpciones(chartOption.value.series[0].data, chartOption.value.series[0].name);
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