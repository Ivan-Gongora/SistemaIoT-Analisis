<template>
  <div class="chart-card" :class="{ 'theme-dark': isDark }">
    
    <div class="chart-header">
      <h4 class="chart-title">{{ chartTitle }}</h4>
      <span 
        class="last-update" 
        :class="{ 'stale': isStale, 'live': !isStale && !loading }"
        :title="isStale ? 'Datos desactualizados' : 'Recibiendo datos'"
      >
        <i class="bi bi-broadcast"></i> {{ ultimaLectura }}
      </span>
    </div>
    
    <div v-if="loading" class="chart-loading">
      <i class="bi bi-arrow-clockwise fa-spin"></i> Cargando datos iniciales...
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
  TitleComponent, TooltipComponent, LegendComponent, GridComponent, DataZoomComponent
} from 'echarts/components';
import VChart from 'vue-echarts';
import { ref, watch, computed, onMounted, onBeforeUnmount } from 'vue';

// Registro de ECharts
use([
  CanvasRenderer, LineChart, TitleComponent, TooltipComponent, 
  LegendComponent, GridComponent, DataZoomComponent
]);

// 🚨 Asumo que API_BASE_URL está definida globalmente
// const API_BASE_URL = 'http://127.0.0.1:8001';

// --- FUNCIÓN AUXILIAR (Para evitar el error de Zona Horaria UTC) ---
function formatFechaLocalParaAPI(date) {
    const pad = (num) => String(num).padStart(2, '0');
    const Y = date.getFullYear();
    const M = pad(date.getMonth() + 1);
    const D = pad(date.getDate());
    const h = pad(date.getHours());
    const m = pad(date.getMinutes());
    const s = pad(date.getSeconds());
    return `${Y}-${M}-${D}T${h}:${m}:${s}`; 
}


export default {
  name: 'GraficoEnTiempoReal',
  components: { VChart },
  props: {
    campoId: { type: Number, required: true },
    titulo: { type: String, default: 'Tiempo Real' },
    isDark: { type: Boolean, default: false },
    simboloUnidad: { type: String, default: 'N/A' }
  },
  
  setup(props) {
    const loading = ref(true); 
    const error = ref(null);
    const chartOption = ref({});
    const chartTitle = ref(props.titulo);
    
    const ultimaLectura = ref('N/A');
    const isStale = ref(true);
    let pollingInterval = null; 
    
    // --- Constantes de Tiempo ---
    const POLLING_INTERVAL_MS = 5000;
    const INITIAL_LOAD_MINUTES = 5;
    const MAX_DATA_POINTS = (INITIAL_LOAD_MINUTES * 60) / (POLLING_INTERVAL_MS / 1000); 
    const STALE_THRESHOLD_MS = 60000;

    // --- Colores de tema ---
    const gridColor = computed(() => props.isDark ? 'rgba(228, 230, 235, 0.2)' : 'rgba(51, 51, 51, 0.2)');
    const textColor = computed(() => props.isDark ? '#E4E6EB' : '#333333');

    // --- 1. FUNCIÓN DE CARGA INICIAL (CORREGIDA CON LÓGICA DE 2 PASOS) ---
    const cargarDatosIniciales = async () => {
      // Validar ID
      if (!props.campoId || props.campoId <= 0) {
        loading.value = false;
        error.value = 'ID de campo no válido.';
        return;
      }
      
      loading.value = true;
      error.value = null;
      const token = localStorage.getItem('accessToken');

      let fechaFinReal; // Aquí guardaremos la última fecha de la DB

      try {
        // -----------------------------------------------------
        // PASO 1: Obtener la fecha máxima (usando el endpoint /ultimo)
        // -----------------------------------------------------
        const ultimoResponse = await fetch(`${API_BASE_URL}/api/valores/ultimo/${props.campoId}`, { 
            headers: { 'Authorization': `Bearer ${token}` } 
        });
        
        if (!ultimoResponse.ok) {
            if (ultimoResponse.status === 404) {
                 throw new Error('No se han encontrado datos históricos para este dispositivo.');
            }
            throw new Error('No se pudo obtener el último valor.');
        }
        
        const ultimoDato = await ultimoResponse.json();
        
        // ¡Éxito! Usamos la fecha máxima real como punto final
        fechaFinReal = new Date(ultimoDato.fecha_hora_lectura);

      } catch (err) {
          error.value = err.message;
          loading.value = false;
          actualizarOpciones([], props.titulo); // Iniciar gráfico vacío
          return; // Detener si no hay rango
      }

      // -----------------------------------------------------
      // PASO 2: Cargar los 5 minutos ANTERIORES a esa fecha máxima
      // -----------------------------------------------------
      try {
        const inicio = new Date(fechaFinReal.getTime() - (INITIAL_LOAD_MINUTES * 60 * 1000));
        
        const url = new URL(`${API_BASE_URL}/api/valores/historico-campo/${props.campoId}`);
        
        // Usar la función auxiliar para formato local
        url.searchParams.append('fecha_inicio', formatFechaLocalParaAPI(inicio));
        url.searchParams.append('fecha_fin', formatFechaLocalParaAPI(fechaFinReal));

        const response = await fetch(url.toString(), {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Fallo al cargar datos iniciales.');
        
        const valores = await response.json();
        
        if (valores.length > 0) {
            const primerValor = valores[0];
            const magnitud = primerValor.magnitud_tipo || props.titulo;
            const simbolo = (primerValor.unidad && primerValor.unidad.simbolo) ? primerValor.unidad.simbolo : 'N/A';
            chartTitle.value = `${magnitud} (${props.simboloUnidad})`;
            
            const dataPoints = valores.map(v => [v.fecha_hora_lectura, parseFloat(v.valor)]);
            actualizarOpciones(dataPoints, magnitud);
            
            const ultimaFecha = new Date(valores[valores.length - 1].fecha_hora_lectura);
            ultimaLectura.value = ultimaFecha.toLocaleTimeString();
            isStale.value = (new Date() - ultimaFecha) > STALE_THRESHOLD_MS;
        } else {
            actualizarOpciones([], props.titulo); // Iniciar gráfico vacío
        }

      } catch (err) {
        error.value = err.message;
      } finally {
        loading.value = false;
      }
    };

    // --- 2. FUNCIÓN DE POLLING (TIEMPO REAL) ---
    const sondearUltimoValor = async () => {
      // No ejecutar si no hay un ID de campo (ej. si el padre aún no lo envía)
      const token = localStorage.getItem('accessToken');
      if (!props.campoId || props.campoId <= 0 || !token) return;

      try {
        // Llama al endpoint de TIEMPO REAL (LIMIT 1)
        const response = await fetch(`${API_BASE_URL}/api/valores/ultimo/${props.campoId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) {
            // Si el sensor deja de responder, marcar los datos como "viejos"
            isStale.value = true;
            return; 
        }
        
        const ultimoValor = await response.json();
        const nuevaFecha = new Date(ultimoValor.fecha_hora_lectura);
        const nuevoPunto = [ultimoValor.fecha_hora_lectura, parseFloat(ultimoValor.valor)];

        // Actualizar UI (Hora e indicador de estado)
        ultimaLectura.value = nuevaFecha.toLocaleTimeString();
        isStale.value = (new Date() - nuevaFecha) > STALE_THRESHOLD_MS;
        
        // Si el gráfico estaba vacío (porque la carga inicial no trajo datos)
        if (!chartOption.value.series || chartOption.value.series.length === 0) {
            const magnitud = ultimoValor.magnitud_tipo || props.titulo;
            const simbolo = (ultimoValor.unidad && ultimoValor.unidad.simbolo) ? ultimoValor.unidad.simbolo : 'N/A';
            chartTitle.value = `${magnitud} (${simbolo})`;
            actualizarOpciones([nuevoPunto], magnitud); // Crea el gráfico con el primer punto
            return;
        }

        // Obtener la data existente del gráfico
        const data = chartOption.value.series[0].data;

        // Evitar duplicados (si el 'ultimoValor' es el mismo que ya tenemos)
        if (data.length > 0 && data[data.length - 1][0] === nuevoPunto[0]) {
            return; // El dato ya está, no hacer nada
        }

        // Lógica de Ventana Deslizante
        data.push(nuevoPunto); // Añadir el nuevo

        if (data.length > MAX_DATA_POINTS) {
          data.shift(); // Eliminar el más antiguo
        }
        
        // Forzar la actualización de ECharts
        chartOption.value.series[0].data = data;
        chartOption.value = { ...chartOption.value }; 

      } catch (err) {
        console.error("Error en polling:", err);
        isStale.value = true;
      }
    };

    // --- 3. FUNCIÓN DE ECHARTS (Configuración) ---
    const actualizarOpciones = (data, magnitud) => {
        chartOption.value = {
            tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
            // 🚨 Ajustamos el 'grid' para dar espacio al título y al dataZoom
            grid: { left: '50px', right: '20px', bottom: '70px', top: '50px' },
            xAxis: {
                type: 'time',
                axisLine: { lineStyle: { color: gridColor.value } },
                axisLabel: { color: textColor.value }
            },
            yAxis: {
                type: 'value',
                scale: true,
                axisLabel: { color: textColor.value, formatter: '{value}' },
                splitLine: { lineStyle: { color: gridColor.value } }
            },
            
            // 🚨 CORRECCIÓN: Añadir la barra de Zoom (dataZoom)
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
                color: '#8A2BE2',
                lineStyle: { width: 2 },
            }]
        };
    };

    // --- 4. CICLO DE VIDA ---
    onMounted(() => {
      // Lógica de dos fases: Carga inicial PRIMERO, luego polling
      cargarDatosIniciales().then(() => {
        if (pollingInterval) clearInterval(pollingInterval);
        pollingInterval = setInterval(sondearUltimoValor, POLLING_INTERVAL_MS);
      });
    });

    onBeforeUnmount(() => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    });
    
    // --- 5. WATCHERS ---
    watch(() => props.campoId, (newId, oldId) => {
      if (newId !== oldId) {
        clearInterval(pollingInterval);
        
        chartOption.value = {}; 
        loading.value = true;
        error.value = null;
        ultimaLectura.value = 'N/A';
        isStale.value = true;

        // Reiniciar carga y polling para el nuevo campoId
        cargarDatosIniciales().then(() => {
            if (pollingInterval) clearInterval(pollingInterval);
            pollingInterval = setInterval(sondearUltimoValor, POLLING_INTERVAL_MS);
        });
      }
    });

    watch(() => props.isDark, () => {
        if (chartOption.value && chartOption.value.series) {
          actualizarOpciones(chartOption.value.series[0].data, chartOption.value.series[0].name);
        }
      }
    );

    return { loading, error, chartOption, chartTitle, ultimaLectura, isStale };
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
$SUCCESS-COLOR: #1ABC9C;

.chart-card {
    border-radius: 12px;
    padding: 20px;
    height: 350px; /* Altura fija */
    display: flex;
    flex-direction: column;
    transition: background-color 0.3s, box-shadow 0.3s;
}
.chart-wrapper {
    position: relative;
    flex-grow: 1;
    width: 100%;
    height: 100%;
}
.chart-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0; /* Ajustado por el header */
}
.chart-loading, .chart-error {
    text-align: center;
    margin: auto;
    font-style: italic;
}
.chart-error { color: $DANGER-COLOR; }

/* 🚨 NUEVOS ESTILOS (Header y Estado) */
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 15px;
}
.last-update {
  font-size: 0.8rem;
  font-weight: 500;
  color: #99A2AD; /* $GRAY-COLD */
  transition: color 0.3s;
  
  i { margin-right: 4px; }
  
  &.live { /* Recibiendo datos */
    color: #1ABC9C; /* $SUCCESS-COLOR */
  }
  &.stale { /* Datos viejos */
    color: #e74c3c; /* $DANGER-COLOR */
  }
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

<!-- <template>
  <div class="chart-card" :class="{ 'theme-dark': isDark }">
    
    <div class="chart-header">
      <h4 class="chart-title">{{ chartTitle }}</h4>
      <span 
        class="last-update" 
        :class="{ 'stale': isStale, 'live': !isStale && !loading }"
        :title="isStale ? 'Datos desactualizados' : 'Recibiendo datos'"
      >
        <i class="bi bi-broadcast"></i> {{ ultimaLectura }}
      </span>
    </div>
    
    <div v-if="loading" class="chart-loading">
      <i class="bi bi-arrow-clockwise fa-spin"></i> Cargando datos iniciales...
    </div>
    <div v-else-if="error" class="chart-error">{{ error }}</div>
    
    <div v-else class="chart-wrapper">
      <v-chart :option="chartOption" autoresize />
    </div>
  </div>
</template>

<script>
// (Importaciones de ECharts: use, CanvasRenderer, LineChart, ...)
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import {
  TitleComponent, TooltipComponent, LegendComponent, GridComponent, DataZoomComponent
} from 'echarts/components';
import VChart from 'vue-echarts';
import { ref, watch, computed, onMounted, onBeforeUnmount } from 'vue';

// Registro de componentes de ECharts
use([
  CanvasRenderer, LineChart, TitleComponent, TooltipComponent, 
  LegendComponent, GridComponent, DataZoomComponent
]);

// // 🚨 CORRECCIÓN 1: API_BASE_URL debe estar definida
// const API_BASE_URL = 'http://127.0.0.1:8001';
function formatFechaLocalParaAPI(date) {
    const pad = (num) => String(num).padStart(2, '0');
    
    const Y = date.getFullYear();
    const M = pad(date.getMonth() + 1);
    const D = pad(date.getDate());
    const h = pad(date.getHours());
    const m = pad(date.getMinutes());
    const s = pad(date.getSeconds());
    
    return `${Y}-${M}-${D}T${h}:${m}:${s}`;
}
export default {
  name: 'GraficoEnTiempoReal',
  components: { VChart },
  props: {
    campoId: { type: Number, required: true },
    titulo: { type: String, default: 'Tiempo Real' },
    isDark: { type: Boolean, default: false }
  },
  
  setup(props) {
    const loading = ref(true); // 👈 Vuelve a 'true'
    const error = ref(null);
    const chartOption = ref({});
    const chartTitle = ref(props.titulo);
    
    const ultimaLectura = ref('N/A');
    const isStale = ref(true);
    let pollingInterval = null; 
    
    // Constantes de tiempo
    const POLLING_INTERVAL_MS = 5000;
    const INITIAL_LOAD_MINUTES = 5;
    const MAX_DATA_POINTS = (INITIAL_LOAD_MINUTES * 60) / (POLLING_INTERVAL_MS / 1000); // 60 puntos
    const STALE_THRESHOLD_MS = 60000;

    // Colores de tema
    const gridColor = computed(() => props.isDark ? 'rgba(228, 230, 235, 0.2)' : 'rgba(51, 51, 51, 0.2)');
    const textColor = computed(() => props.isDark ? '#E4E6EB' : '#333333');

    // --- FUNCIÓN DE CARGA INICIAL (RESTAURADA) ---
    const cargarDatosIniciales = async () => {
      loading.value = true;
      error.value = null;
      const token = localStorage.getItem('accessToken');

      // 1. Carga Inicial (Últimos 5 minutos)
      const fin = new Date();
      const inicio = new Date(fin.getTime() - (INITIAL_LOAD_MINUTES * 60 * 1000));

      const url = new URL(`${API_BASE_URL}/api/valores/historico-campo/${props.campoId}`);
      
      // 🚨 CORRECCIÓN UTC: Usar la función auxiliar para formato local
      url.searchParams.append('fecha_inicio', formatFechaLocalParaAPI(inicio));
      url.searchParams.append('fecha_fin', formatFechaLocalParaAPI(fin));

      try {
        const response = await fetch(url.toString(), {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Fallo al cargar datos iniciales.');
        
        const valores = await response.json();
        
        if (valores.length > 0) {
            const primerValor = valores[0];
            const magnitud = primerValor.magnitud_tipo || props.titulo;
            const simbolo = (primerValor.unidad && primerValor.unidad.simbolo) ? primerValor.unidad.simbolo : 'N/A';
            chartTitle.value = `${magnitud} (${simbolo})`;
            
            const dataPoints = valores.map(v => [v.fecha_hora_lectura, parseFloat(v.valor)]);
            actualizarOpciones(dataPoints, magnitud);
            
            const ultimaFecha = new Date(valores[valores.length - 1].fecha_hora_lectura);
            ultimaLectura.value = ultimaFecha.toLocaleTimeString();
        } else {
            // Si no hay datos iniciales, creamos un gráfico vacío
            actualizarOpciones([], props.titulo);
            // No lanzamos error, simplemente el polling empezará a llenar el gráfico
        }

      } catch (err) {
        error.value = err.message;
      } finally {
        loading.value = false;
      }
    };

    // --- FUNCIÓN DE POLLING (TIEMPO REAL) ---
    const sondearUltimoValor = async () => {
      const token = localStorage.getItem('accessToken');
      if (!props.campoId) return;

      try {
        const response = await fetch(`${API_BASE_URL}/api/valores/ultimo/${props.campoId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) {
            isStale.value = true;
            return; 
        }
        
        const ultimoValor = await response.json();
        
        const nuevaFecha = new Date(ultimoValor.fecha_hora_lectura);
        ultimaLectura.value = nuevaFecha.toLocaleTimeString();
        isStale.value = false; 
        
        const nuevoPunto = [ultimoValor.fecha_hora_lectura, parseFloat(ultimoValor.valor)];

        // Si el gráfico estaba vacío (por la carga inicial fallida)
        if (!chartOption.value.series || chartOption.value.series.length === 0) {
            const magnitud = ultimoValor.magnitud_tipo || props.titulo;
            const simbolo = (ultimoValor.unidad && ultimoValor.unidad.simbolo) ? ultimoValor.unidad.simbolo : 'N/A';
            chartTitle.value = `${magnitud} (${simbolo})`;
            actualizarOpciones([nuevoPunto], magnitud);
            return;
        }

        const data = chartOption.value.series[0].data;

        // Evitar duplicados
        if (data.length > 0 && data[data.length - 1][0] === nuevoPunto[0]) {
            const ahora = new Date();
            isStale.value = (ahora - nuevaFecha) > STALE_THRESHOLD_MS;
            return;
        }

        data.push(nuevoPunto); 

        if (data.length > MAX_DATA_POINTS) {
          data.shift(); 
        }
        
        chartOption.value.series[0].data = data;
        chartOption.value = { ...chartOption.value }; 

      } catch (err) {
        console.error("Error en polling:", err);
        isStale.value = true;
      }
    };
    // --- FUNCIÓN DE ECHARTS (ACTUALIZAR OPCIONES) ---
    const actualizarOpciones = (data, magnitud) => {
        chartOption.value = {
            tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
            grid: { left: '50px', right: '20px', bottom: '30px', top: '20px' }, 
            xAxis: {
                type: 'time',
                axisLine: { lineStyle: { color: gridColor.value } },
                axisLabel: { color: textColor.value }
            },
            yAxis: {
                type: 'value',
                scale: true,
                axisLabel: { color: textColor.value, formatter: '{value}' },
                splitLine: { lineStyle: { color: gridColor.value } }
            },
            dataZoom: [ { type: 'inside' } ], 
            series: [{
                name: magnitud,
                data: data,
                type: 'line',
                showSymbol: false,
                color: '#8A2BE2',
                lineStyle: { width: 2 },
            }]
        };
    };

    // --- CICLO DE VIDA ---
    onMounted(() => {
      // 🚨 CORREGIDO: Carga inicial PRIMERO, luego polling
      cargarDatosIniciales().then(() => {
        // Iniciar el polling solo después de la carga inicial
        if (pollingInterval) clearInterval(pollingInterval);
        pollingInterval = setInterval(sondearUltimoValor, POLLING_INTERVAL_MS);
      });
    });

    onBeforeUnmount(() => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    });
    
    // --- WATCHERS ---
    watch(() => props.campoId, (newId, oldId) => {
      if (newId !== oldId) {
        clearInterval(pollingInterval);
        
        // Reiniciar estados
        chartOption.value = {}; 
        loading.value = true;
        error.value = null;
        ultimaLectura.value = 'N/A';
        isStale.value = true;

        // Reiniciar carga y polling para el nuevo campoId
        cargarDatosIniciales().then(() => {
            if (pollingInterval) clearInterval(pollingInterval);
            pollingInterval = setInterval(sondearUltimoValor, POLLING_INTERVAL_MS);
        });
      }
    });

    // Actualizar colores del tema
    watch(() => props.isDark, () => {
        if (chartOption.value && chartOption.value.series) {
          actualizarOpciones(chartOption.value.series[0].data, chartOption.value.series[0].name);
        }
      }
    );

    return { loading, error, chartOption, chartTitle, ultimaLectura, isStale };
  }
}
</script> -->
