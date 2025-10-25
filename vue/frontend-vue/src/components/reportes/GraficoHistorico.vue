<template>
  <div class="chart-card" :class="{ 'theme-dark': isDark }">
    <h4 class="chart-title">{{ titulo }}</h4>
    
    <div v-if="loading" class="chart-loading">Cargando datos...</div>
    <div v-else-if="error" class="chart-error">{{ error }}</div>
    
    <div v-else class="chart-wrapper">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script>
// Imports de Chart.js (Line y los módulos)
import { Line } from 'vue-chartjs';
import { 
    Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend 
} from 'chart.js';

ChartJS.register(
    CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend
);

const API_BASE_URL = 'http://127.0.0.1:8001';

export default {
    name: 'GraficoHistorico',
    components: { Line },
    props: {
        campoId: { type: Number, required: true },
        titulo: { type: String, default: 'Histórico de Datos' },
        simboloUnidad: { type: String, default: '' },
        isDark: { type: Boolean, default: false }
    },
    data() {
        return {
            loading: true,
            error: null,
            magnitudTipo: 'N/A', // 👈 Nuevo estado para guardar el tipo de magnitud
            chartData: { labels: [], datasets: [] },
            chartOptions: {
                responsive: true,
                maintainAspectRatio: false,
                // ... (Opciones de Chart.js)
            }
        };
    },
    mounted() {
        this.cargarDatosHistoricos();
        this.actualizarOpcionesTema();
    },
    watch: {
        campoId: {
        immediate: true, // Esto hace que se ejecute una vez al montar
        handler() {
            if (this.campoId && this.campoId > 0) {
                 this.cargarDatosHistoricos();
            }
        }
    },
       
        isDark() {
            this.actualizarOpcionesTema();
        }
    },
    methods: {
        async cargarDatosHistoricos() {// 🚨 CORRECCIÓN CRÍTICA: Bloquear la ejecución si campoId no es un número válido
    if (!this.campoId || this.campoId <= 0 || isNaN(this.campoId)) {
        this.loading = false;
        this.error = 'Seleccione un campo de medición válido.';
        return; // Detener la ejecución
    }

    
    this.loading = true; this.error = null;
    const token = localStorage.getItem('accessToken');
    
    try {
        // 🚨 CRÍTICO: Usar la ruta renombrada
        const response = await fetch(`${API_BASE_URL}/api/valores/historico-campo/${this.campoId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            throw new Error('Fallo al cargar datos del gráfico.');
        }
        
        const valores = await response.json();
        
        if (valores.length === 0) {
            this.chartData = { labels: ['Sin datos'], datasets: [{ data: [] }] };
            throw new Error('No se encontraron valores históricos para este campo.');
        }
        
        // 🚨 Extracción de la información de la unidad (del primer registro)
        const primerValor = valores[0]; 
        const magnitudLabel = primerValor.magnitud_tipo || this.titulo;
        // Asumo que el backend también devuelve 'simbolo' en el JOIN, si no, quedará vacío.
        const simbolo = primerValor.simbolo || ''; 
        
        const labels = valores.map(v => new Date(v.fecha_hora_lectura).toLocaleTimeString());
        const dataPoints = valores.map(v => parseFloat(v.valor));

        this.chartData = {
            labels: labels,
            datasets: [
                {
                    // 🚨 Etiqueta final del gráfico
                    label: `${magnitudLabel} (${simbolo})`, 
                    backgroundColor: '#8A2BE2',
                    borderColor: '#8A2BE2',
                    data: dataPoints,
                    tension: 0.1 
                }
            ]
        };
        // 🚨 Importante: Actualizar opciones de tema para reflejar el color de ejes
        this.actualizarOpcionesTema(); 

    } catch (err) {
        this.error = err.message;
    } finally {
        this.loading = false;
    }
},
        actualizarOpcionesTema() {
            // Actualiza los colores de los ejes y leyendas según el tema
            const colorEjes = this.isDark ? '#E4E6EB' : '#333333';
            this.chartOptions = {
                ...this.chartOptions, // Mantener opciones anteriores
                scales: {
                    y: { ticks: { color: colorEjes } },
                    x: { ticks: { color: colorEjes } }
                },
                plugins: {
                    legend: { labels: { color: colorEjes } }
                }
            };
        }
    }
}
</script>


<style scoped lang="scss">
// ----------------------------------------
// VARIABLES DE PALETA (Copiadas de tu Tarjeta)
// ----------------------------------------
$PRIMARY-PURPLE: #8A2BE2;
$SUCCESS-COLOR: #1ABC9C;
$GRAY-COLD: #99A2AD;
$LIGHT-TEXT: #E4E6EB;
$DARK-TEXT: #333333;
$SUBTLE-BG-DARK: #2B2B40;
$SUBTLE-BG-LIGHT: #FFFFFF;
$DARK-BG-CONTRAST: #1A1A2E; 

.chart-card {
    border-radius: 12px;
    padding: 20px;
    height: 350px; 
    display: flex;
    flex-direction: column;
    transition: background-color 0.3s, box-shadow 0.3s, color 0.3s; 
}
.chart-wrapper {
    position: relative;
    flex-grow: 1;
}
.chart-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 15px;
    transition: color 0.3s;
}
.chart-loading, .chart-error {
    text-align: center;
    margin-top: 50px;
    font-style: italic;
    color: $GRAY-COLD; 
    transition: color 0.3s;
}

/* ----------------------------------------
   TEMAS
   ---------------------------------------- */

/* TEMA CLARO */
.theme-light .chart-card {
    background-color: $SUBTLE-BG-LIGHT;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    color: $DARK-TEXT; /* Color de texto general */
}
.theme-light .chart-title {
    color: $DARK-TEXT;
}

/* TEMA OSCURO (Asegura color de fondo y título) */
.theme-dark .chart-card {
    background-color: $SUBTLE-BG-DARK; /* Fondo de tarjeta oscuro (consistente) */
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    color: $LIGHT-TEXT; /* Color de texto general para la tarjeta */
}
.theme-dark .chart-title {
    color: $LIGHT-TEXT; /* El título debe ser claro */
}
.theme-dark .chart-loading, .theme-dark .chart-error {
    color: $GRAY-COLD;
}
</style>