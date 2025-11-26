<template>
  <div class="chart-card" :class="{ 'theme-dark': isDark }">
    
    <div class="chart-header">
      <div class="title-group">
          <h4 class="chart-title">{{ chartTitle }}</h4>
          <!-- Indicador visual de IA activa -->
          <span v-if="analisisActivo" class="analysis-badge" title="Detección activa">
            <span class="pulse-dot"></span> AI
          </span>
      </div>
      
      <span 
        class="last-update" 
        :class="{ 'stale': isStale, 'live': !isStale && !loading }"
        :title="isStale ? 'Sin datos recientes' : 'Conexión estable'"
      >
        <i class="bi bi-broadcast"></i> {{ ultimaLectura }}
      </span>
    </div>
    
    <div v-if="loading && !chartOption.series" class="chart-loading">
      <div class="spinner-border"></div>
      <p>Sincronizando...</p>
    </div>
    
    <div v-else-if="error" class="chart-error">
        <i class="bi bi-exclamation-circle"></i> {{ error }}
    </div>
    
    <div v-else class="chart-content">
        <div class="chart-wrapper">
            <v-chart :option="chartOption" autoresize />
        </div>

        <!-- 🚨 PANEL DE ESTADÍSTICAS MEJORADO -->
        <div class="stats-footer">
            <div class="stat-item">
                <span class="label">Último</span>
                <span class="value">{{ stats.ultimo }}</span>
            </div>
            
            <!-- Lógica Condicional para Movimiento -->
            <template v-if="!esMovimiento">
                <div class="stat-item">
                    <span class="label">Promedio</span>
                    <span class="value">{{ stats.promedio }}</span>
                </div>
                <div class="stat-item highlight">
                    <span class="label">Pico Máx</span>
                    <span class="value">{{ stats.maximo }}</span>
                </div>
            </template>

            <!-- Si ES movimiento, mostramos conteo de eventos -->
            <template v-else>
                <div class="stat-item highlight">
                    <span class="label">Total Eventos</span>
                    <span class="value">{{ stats.totalEventos }}</span>
                </div>
                <div class="stat-item">
                    <span class="label">Densidad Máx</span>
                    <span class="value">{{ stats.maximo }} <small>/min</small></span>
                </div>
            </template>
        </div>
    </div>
  </div>
</template>

<script>
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, BarChart } from 'echarts/charts';
import {
  TitleComponent, TooltipComponent, LegendComponent, GridComponent, DataZoomComponent, VisualMapComponent, MarkPointComponent, ToolboxComponent
} from 'echarts/components';
import VChart from 'vue-echarts';
import { ref, watch, computed, onMounted, onBeforeUnmount } from 'vue';

use([
  CanvasRenderer, LineChart, BarChart, TitleComponent, TooltipComponent, 
  LegendComponent, GridComponent, DataZoomComponent, VisualMapComponent, MarkPointComponent, ToolboxComponent
]);

const API_BASE_URL = 'http://127.0.0.1:8001';

export default {
  name: 'GraficoEnTiempoReal',
  components: { VChart },
  props: {
    campoId: { type: Number, required: true },
    titulo: { type: String, default: 'Tiempo Real' },
    isDark: { type: Boolean, default: false },
    simboloUnidad: { type: String, default: '' },
    metodoCarga: { type: String, default: 'optimizado' },
    ventanaTiempo: { type: Number, default: 5 },
    analisisActivo: { type: Boolean, default: true }
  },
  
  setup(props) {
    const loading = ref(true); 
    const error = ref(null);
    const chartOption = ref({});
    const chartTitle = ref(props.titulo);
    
    const ultimaLectura = ref('Esperando...');
    const isStale = ref(true);
    const stats = ref({ ultimo: '-', promedio: '-', maximo: '-', totalEventos: 0 });
    
    let pollingInterval = null; 
    const POLLING_INTERVAL_MS = 5000;
    const STALE_THRESHOLD_MS = 60000; 

    const gridColor = computed(() => props.isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)');
    const textColor = computed(() => props.isDark ? '#E4E6EB' : '#333333');
    const colorPrincipal = '#8A2BE2'; 
    const colorAlerta = '#E74C3C';    

    const esMovimiento = computed(() => {
        const t = props.titulo.toLowerCase();
        return t.includes('movimiento') || t.includes('puerta') || t.includes('presencia') || t.includes('estado');
    });

    // ---------------------------------------------------------
    // CÁLCULO DE ESTADÍSTICAS MEJORADO
    // ---------------------------------------------------------
    const calcularEstadisticas = (data) => {
        if (!data || data.length === 0) return;
        
        const valores = data.map(item => item.value[1]);
        const ultimo = valores[valores.length - 1];
        const maximo = Math.max(...valores);
        const promedio = valores.reduce((a, b) => a + b, 0) / valores.length;
        
        if (esMovimiento.value) {
             // Para movimiento, sumamos todos los eventos detectados en el periodo
             const total = valores.reduce((a,b) => a + b, 0);
             
             stats.value = {
                ultimo: ultimo > 0 ? 'Activo' : 'Inactivo',
                promedio: '-',
                maximo: maximo.toFixed(0), // Muestra el pico más alto de actividad en un bloque
                totalEventos: total.toFixed(0)
            };
        } else {
            stats.value = {
                ultimo: ultimo.toFixed(2),
                promedio: promedio.toFixed(2),
                maximo: maximo.toFixed(2),
                totalEventos: 0
            };
        }
    };

    // ---------------------------------------------------------
    // PROCESAMIENTO DE MOVIMIENTO (AGREGACIÓN VISUAL)
    // ---------------------------------------------------------
    const procesarDatosMovimiento = (rawData) => {
        // Si la ventana es corta (5 min), mostramos datos crudos (línea 0/1)
        if (props.ventanaTiempo <= 5) return rawData;

        // Si es ventana larga, agrupamos por bloques de tiempo para ver densidad
        const intervaloMinutos = props.ventanaTiempo > 60 ? 15 : 1;
        const intervaloMs = intervaloMinutos * 60 * 1000;

        const agrupado = {};
        
        rawData.forEach(item => {
            const timestamp = new Date(item.value[0]).getTime();
            // "Redondear" al bloque de tiempo (Bucket)
            const bloque = Math.floor(timestamp / intervaloMs) * intervaloMs;
            
            if (!agrupado[bloque]) {
                agrupado[bloque] = { sum: 0, anomalia: false, mensaje: '' };
            }
            
            // Sumar actividad (si valor > 0.5 asumimos 1/true)
            if (item.value[1] > 0.5) {
                agrupado[bloque].sum += 1;
            }
            
            // Heredar anomalía del backend
            if (item.anomalia) {
                agrupado[bloque].anomalia = true;
                if (!agrupado[bloque].mensaje) agrupado[bloque].mensaje = item.mensaje;
            }
        });

        // Convertir objeto agrupado a array para ECharts
        const resultado = Object.keys(agrupado).sort().map(key => {
            const dataBloque = agrupado[key];
            return {
                value: [parseInt(key), dataBloque.sum], // Y = Total de eventos en el lapso
                anomalia: dataBloque.anomalia,
                mensaje: dataBloque.mensaje || `${dataBloque.sum} eventos`
            };
        });

        // 🚨 DETECCIÓN LOCAL DE PICOS (Frontend)
        // Si la gráfica muestra mucha actividad en un bloque comparado con otros, márcalo
        if (resultado.length > 5) {
             const sumas = resultado.map(r => r.value[1]);
             const mediaLocal = sumas.reduce((a,b) => a+b, 0) / sumas.length;
             
             resultado.forEach(r => {
                 if (r.value[1] > (mediaLocal * 3) && r.value[1] > 5) {
                     r.anomalia = true;
                     if (!r.mensaje.includes('Pico')) r.mensaje = `Pico de actividad (${r.value[1]} eventos)`;
                 }
             });
        }

        return resultado;
    };

    // ---------------------------------------------------------
    // 1. CARGA INICIAL
    // ---------------------------------------------------------
    const cargarDatosIniciales = async () => {
      if (!props.campoId || props.campoId <= 0) { loading.value = false; return; }
      
      if (!chartOption.value.series) loading.value = true;
      
      error.value = null;
      const token = localStorage.getItem('accessToken');

      try {
        const url = new URL(`${API_BASE_URL}/api/valores/ventana/${props.campoId}`);
        url.searchParams.append('minutos', props.ventanaTiempo);
        if (props.analisisActivo) url.searchParams.append('analisis_activo', 'true');

        const response = await fetch(url.toString(), { headers: { 'Authorization': `Bearer ${token}` } });
        if (!response.ok) throw new Error('Sin conexión.');
        
        const valores = await response.json();
        
        if (valores.length > 0) {
            const primerValor = valores[0];
            const magnitud = primerValor.magnitud_tipo || props.titulo;
            const unidad = props.simboloUnidad || primerValor.simbolo_unidad || '';
            chartTitle.value = `${magnitud} (${unidad})`;
            
            let dataPoints = valores.map(v => ({
                value: [v.fecha_hora_lectura, parseFloat(v.valor)],
                anomalia: v.anomalia || false, 
                mensaje: v.mensaje_alerta
            }));

            // Transformación si es movimiento
            if (esMovimiento.value) {
                dataPoints = procesarDatosMovimiento(dataPoints);
            }
            
            actualizarOpciones(dataPoints, magnitud);
            calcularEstadisticas(dataPoints);

            const ultimaFecha = new Date(valores[valores.length - 1].fecha_hora_lectura);
            ultimaLectura.value = ultimaFecha.toLocaleTimeString();
            isStale.value = (new Date() - ultimaFecha) > STALE_THRESHOLD_MS;
        } else {
            actualizarOpciones([], props.titulo);
            ultimaLectura.value = "Sin datos recientes";
        }
      } catch (err) {
        error.value = err.message;
      } finally {
        loading.value = false;
      }
    };

    // ---------------------------------------------------------
    // 2. POLLING (Adaptativo)
    // ---------------------------------------------------------
    const sondearUltimoValor = async () => {
      // Si es ventana larga, recargamos todo para mantener la agregación correcta
      if (props.ventanaTiempo > 5) {
          await cargarDatosIniciales(); 
          return;
      }

      const token = localStorage.getItem('accessToken');
      if (!props.campoId || !token) return;

      try {
        const url = new URL(`${API_BASE_URL}/api/valores/ultimo/${props.campoId}`);
        if (props.analisisActivo) url.searchParams.append('analisis_activo', 'true');

        const response = await fetch(url.toString(), { headers: { 'Authorization': `Bearer ${token}` } });
        if (!response.ok) { isStale.value = true; return; }
        
        const ultimoValor = await response.json();
        const nuevaFecha = new Date(ultimoValor.fecha_hora_lectura);
        
        const nuevoPunto = {
            value: [ultimoValor.fecha_hora_lectura, parseFloat(ultimoValor.valor)],
            anomalia: ultimoValor.anomalia || false,
            mensaje: ultimoValor.mensaje_alerta
        };

        ultimaLectura.value = nuevaFecha.toLocaleTimeString();
        isStale.value = false;
        
        if (!chartOption.value.series || chartOption.value.series.length === 0) {
            actualizarOpciones([nuevoPunto], props.titulo);
            return;
        }

        let seriesData = chartOption.value.series[0].data;
        const lastTimestamp = seriesData.length > 0 ? seriesData[seriesData.length - 1].value[0] : null;
        if (lastTimestamp === nuevoPunto.value[0]) return;

        seriesData.push(nuevoPunto); 
        
        const minTime = new Date(nuevaFecha.getTime() - (props.ventanaTiempo * 60 * 1000)).getTime();
        while (seriesData.length > 0 && new Date(seriesData[0].value[0]).getTime() < minTime) {
             seriesData.shift();
        }
        
        actualizarOpciones(seriesData, chartTitle.value.split(' ')[0]); 
        calcularEstadisticas(seriesData);

      } catch (err) {
        isStale.value = true;
      }
    };

    // ---------------------------------------------------------
    // 3. CONFIGURACIÓN ECHARTS
    // ---------------------------------------------------------
    const actualizarOpciones = (data, seriesName) => {
        // Filtrar anomalías para crear la serie de pines
        const anomalypoints = data.filter(item => item.anomalia).map(item => ({
            name: item.mensaje || 'Anomalía', 
            xAxis: item.value[0], 
            yAxis: item.value[1], 
            value: item.value[1],
            itemStyle: { color: colorAlerta }
        }));
        
        const isBarChart = esMovimiento.value && props.ventanaTiempo > 5;
        const chartType = isBarChart ? 'bar' : 'line';

        chartOption.value = {
            toolbox: {
                show: true,
                feature: {
                    saveAsImage: { show: true, title: 'Guardar' },
                    dataZoom: { show: true, title: { zoom: 'Zoom', back: 'Restaurar' } }
                },
                iconStyle: { borderColor: textColor.value },
                right: 20, top: 0
            },
            tooltip: { 
                trigger: 'axis', 
                axisPointer: { type: isBarChart ? 'shadow' : 'line' },
                backgroundColor: props.isDark ? 'rgba(43, 43, 64, 0.95)' : 'rgba(255, 255, 255, 0.95)',
                borderColor: props.isDark ? '#444' : '#ddd',
                textStyle: { color: textColor.value },
                formatter: (params) => {
                    const item = params[0];
                    if (!item || !item.value) return ''; 
                    
                    const fechaObj = new Date(item.value[0]);
                    const fecha = fechaObj.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                    const dia = fechaObj.toLocaleDateString([], {month: 'short', day: 'numeric'});
                    
                    const val = item.value[1];
                    const alerta = item.data.anomalia ? `<br/><span style="color:${colorAlerta}; font-weight:bold;">⚠️ ${item.data.mensaje || 'Anomalía'}</span>` : '';
                    const label = isBarChart ? 'Eventos' : item.seriesName;
                    
                    return `<b>${dia} ${fecha}</b><br/>${label}: ${val}${alerta}`;
                }
            },
            grid: { left: 40, right: 30, bottom: 40, top: 50, containLabel: true },
            xAxis: {
                type: 'time',
                boundaryGap: isBarChart,
                axisLine: { show: false },
                axisTick: { show: false },
                axisLabel: { color: textColor.value, fontSize: 11 },
                splitLine: { show: false }
            },
            yAxis: {
                type: 'value',
                scale: true, 
                axisLabel: { color: textColor.value, fontSize: 11 },
                splitLine: { lineStyle: { color: gridColor.value, type: 'dashed' } }
            },
            dataZoom: [ 
                { type: 'slider', show: true, bottom: 5, height: 15, borderColor: 'transparent', textStyle: { color: textColor.value } }, 
                { type: 'inside' } 
            ], 
            series: [{
                name: seriesName,
                type: chartType,
                data: data.map(item => ({
                    value: item.value,
                    itemStyle: { color: item.anomalia ? colorAlerta : colorPrincipal },
                    // Puntos solo en modo línea
                    symbol: (chartType === 'line' && item.anomalia) ? 'circle' : 'none',
                    symbolSize: 6,
                    anomalia: item.anomalia,
                    mensaje: item.mensaje
                })),
                smooth: true,
                barMaxWidth: 40, 
                lineStyle: { width: 2, color: colorPrincipal },
                itemStyle: { color: colorPrincipal },
                areaStyle: chartType === 'line' ? {
                    color: {
                        type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
                        colorStops: [{ offset: 0, color: 'rgba(138, 43, 226, 0.3)' }, { offset: 1, color: 'rgba(138, 43, 226, 0)' }]
                    }
                } : undefined,
                
                // 🚨 Pines activados en AMBOS modos (Línea y Barra)
                markPoint: props.analisisActivo ? {
                    data: anomalypoints,
                    symbol: 'pin', symbolSize: 40,
                    label: { show: true, formatter: '!', color: '#fff', fontWeight: 'bold' },
                    itemStyle: { color: colorAlerta, shadowBlur: 5, shadowColor: 'rgba(0,0,0,0.3)' },
                    animation: false 
                } : null
            }]
        };
    };

    watch(() => [props.campoId, props.ventanaTiempo, props.analisisActivo], () => {
        clearInterval(pollingInterval);
        cargarDatosIniciales().then(() => {
            pollingInterval = setInterval(sondearUltimoValor, POLLING_INTERVAL_MS);
        });
    });

    watch(() => props.isDark, () => {
        if (chartOption.value.series) chartOption.value = { ...chartOption.value };
    });

    onMounted(() => {
        cargarDatosIniciales().then(() => {
            if (pollingInterval) clearInterval(pollingInterval);
            pollingInterval = setInterval(sondearUltimoValor, POLLING_INTERVAL_MS);
        });
    });
    onBeforeUnmount(() => { if (pollingInterval) clearInterval(pollingInterval); });

    return { loading, error, chartOption, chartTitle, ultimaLectura, isStale, stats, esMovimiento };
  }
}
</script>

<style scoped lang="scss">
$PRIMARY-PURPLE: #8A2BE2;
$DANGER-COLOR: #E74C3C;
$SUCCESS-COLOR: #1ABC9C;
$GRAY-COLD: #99A2AD;
$LIGHT-TEXT: #E4E6EB;
$DARK-TEXT: #333333;
$SUBTLE-BG-DARK: #2B2B40;
$SUBTLE-BG-LIGHT: #FFFFFF;

.chart-card {
    border-radius: 16px;
    padding: 20px;
    height: 450px; 
    display: flex;
    flex-direction: column;
    transition: background-color 0.3s, box-shadow 0.3s;
    border: 1px solid transparent;
}

.chart-content { flex-grow: 1; display: flex; flex-direction: column; height: 100%; }
.chart-wrapper { flex-grow: 1; width: 100%; min-height: 0; }

.chart-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid rgba(0,0,0,0.05);
    
    .title-group {
        display: flex; align-items: center; gap: 12px;
        .chart-title { font-size: 1.1rem; font-weight: 700; margin: 0; }
        .analysis-badge {
            font-size: 0.7rem; background-color: rgba($PRIMARY-PURPLE, 0.1);
            color: $PRIMARY-PURPLE; padding: 3px 8px; border-radius: 12px;
            font-weight: 700; display: flex; align-items: center; gap: 6px;
            .pulse-dot { width: 6px; height: 6px; background-color: $PRIMARY-PURPLE; border-radius: 50%; animation: pulse 2s infinite; }
        }
    }
    .last-update { font-size: 0.8rem; font-weight: 600; color: $GRAY-COLD; i { margin-right: 4px; } &.live { color: $SUCCESS-COLOR; } &.stale { color: $DANGER-COLOR; } }
}
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba($PRIMARY-PURPLE, 0.7); } 70% { box-shadow: 0 0 0 6px rgba($PRIMARY-PURPLE, 0); } 100% { box-shadow: 0 0 0 0 rgba($PRIMARY-PURPLE, 0); } }

.stats-footer {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); gap: 10px;
    padding-top: 15px; margin-top: 10px; border-top: 1px solid rgba(0,0,0,0.05);
    
    .stat-item {
        display: flex; flex-direction: column; align-items: center;
        .label { font-size: 0.7rem; text-transform: uppercase; color: $GRAY-COLD; font-weight: 600; margin-bottom: 2px; }
        .value { font-size: 1rem; font-weight: 700; }
        &.highlight .value { color: $PRIMARY-PURPLE; }
    }
}

.chart-loading, .chart-error { flex-grow: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: $GRAY-COLD; gap: 10px; }
.spinner-border { width: 2rem; height: 2rem; border: 3px solid rgba($PRIMARY-PURPLE, 0.3); border-top-color: $PRIMARY-PURPLE; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.chart-error { color: $DANGER-COLOR; }

.theme-light .chart-card { background-color: $SUBTLE-BG-LIGHT; box-shadow: 0 4px 20px rgba(0,0,0,0.05); color: $DARK-TEXT; .chart-header, .stats-footer { border-color: rgba(0,0,0,0.05); } }
.theme-dark .chart-card { background-color: $SUBTLE-BG-DARK; box-shadow: 0 4px 20px rgba(0,0,0,0.2); color: $LIGHT-TEXT; .chart-header, .stats-footer { border-color: rgba(255,255,255,0.05); } .chart-title { color: $LIGHT-TEXT; } .stats-footer { border-color: rgba(255,255,255,0.05); } }
</style>