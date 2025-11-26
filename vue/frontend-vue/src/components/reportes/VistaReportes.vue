<template>
  <div class="plataforma-layout" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    <BarraLateralPlataforma :is-open="isSidebarOpen" />
    
    <div class="plataforma-contenido" :class="{ 'shifted': isSidebarOpen }">
      <EncabezadoPlataforma 
        titulo="Reportes y Análisis"
        subtitulo="Exploración histórica de datos IoT"
        @toggle-sidebar="toggleSidebar" 
        :is-sidebar-open="isSidebarOpen"
      />

      <div class="reportes-contenido">
        
        <!-- PANEL DE CONTROL UNIFICADO -->
        <div class="control-panel" :class="{ 'theme-dark': isDark }">
            
            <!-- SECCIÓN 1: ORIGEN -->
            <div class="control-section">
                <h4 class="section-title"><i class="bi bi-hdd-network"></i> Origen de Datos</h4>
                
                <div class="form-group">
                    <label>Proyecto</label>
                    <div class="input-wrapper">
                        <i class="bi bi-folder2-open input-icon"></i>
                        <select v-model="proyectoSeleccionadoId" @change="cargarDispositivos" class="form-control">
                            <option :value="null" disabled>
                                {{ loadingProyectos ? 'Cargando...' : 'Seleccionar...' }}
                            </option>
                            <option v-for="p in proyectos" :key="p.id" :value="p.id">{{ p.nombre }}</option>
                        </select>
                    </div>
                </div>

                <div class="form-group">
                    <label>Dispositivo</label>
                    <div class="input-wrapper">
                        <i class="bi bi-cpu input-icon"></i>
                        <select v-model="dispositivoSeleccionadoId" @change="cargarCamposYFechas" class="form-control" :disabled="!proyectoSeleccionadoId">
                            <option :value="null" disabled>
                                {{ loadingDispositivos ? 'Cargando...' : 'Seleccionar...' }}
                            </option>
                            <option v-for="d in dispositivos" :key="d.id" :value="d.id">{{ d.nombre }}</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- SECCIÓN 2: TIEMPO -->
            <div class="control-section time-section">
                <h4 class="section-title"><i class="bi bi-calendar-range"></i> Rango de Tiempo</h4>
                
                <div class="time-row">
                    <div class="form-group flex-grow">
                        <label>Inicio</label>
                        <div class="input-wrapper">
                            <input type="date" class="form-control" v-model="fechaInicioSeleccionada" :min="fechaMinimaDisponible" :max="fechaMaximaDisponible" :disabled="!dispositivoSeleccionadoId">
                        </div>
                    </div>
                    <div class="form-group time-input">
                        <label>Hora</label>
                        <div class="input-wrapper">
                            <input type="time" class="form-control" v-model="horaInicioSeleccionada" :disabled="!dispositivoSeleccionadoId">
                        </div>
                    </div>
                </div>

                <div class="time-row">
                    <div class="form-group flex-grow">
                        <label>Fin</label>
                        <div class="input-wrapper">
                            <input type="date" class="form-control" v-model="fechaFinSeleccionada" :min="fechaMinimaDisponible" :max="fechaMaximaDisponible" :disabled="!dispositivoSeleccionadoId">
                        </div>
                    </div>
                    <div class="form-group time-input">
                        <label>Hora</label>
                        <div class="input-wrapper">
                            <input type="time" class="form-control" v-model="horaFinSeleccionada" :disabled="!dispositivoSeleccionadoId">
                        </div>
                    </div>
                </div>
            </div>

            <!-- SECCIÓN 3: CONFIGURACIÓN -->
            <div class="control-section config-section">
                <h4 class="section-title"><i class="bi bi-sliders"></i> Preferencias</h4>
                
                <div class="form-group">
                    <label>Visualización</label>
                    <div class="input-wrapper">
                        <i class="bi bi-graph-up input-icon"></i>
                        <select v-model="modoVista" class="form-control" :disabled="!dispositivoSeleccionadoId">
                            <option value="multiple">Múltiples Gráficos</option>
                            <option value="combinado">Gráfico Combinado</option>
                        </select>
                    </div>
                </div>

                <div class="form-group">
                    <label>Procesamiento</label>
                    <div class="input-wrapper">
                        <i class="bi bi-database-gear input-icon"></i>
                        <select v-model="metodoCarga" class="form-control" :disabled="!dispositivoSeleccionadoId">
                            <option value="optimizado">Optimizado (Promedios)</option>
                            <option value="puro">Datos Puros (Raw)</option>
                        </select>
                    </div>
                    
                    <!-- Indicador de Estado Elegante -->
                    <div class="status-pill" :class="metodoCarga">
                        <i :class="metodoCarga === 'puro' ? 'bi bi-exclamation-triangle-fill' : 'bi bi-lightning-charge-fill'"></i>
                        <span>{{ metodoCarga === 'puro' ? 'Carga intensiva' : 'Rendimiento óptimo' }}</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- SELECTOR DE VARIABLES (Grid Moderno) -->
        <div class="variables-panel" v-if="campos.length > 0">
            <div class="panel-header">
                <h4><i class="bi bi-check2-square"></i> Variables Disponibles</h4>
                <span class="subtitle">Seleccione las métricas a graficar</span>
            </div>
            
            <div v-if="loadingCampos" class="loading-state">
                <div class="spinner"></div> Cargando variables...
            </div>

            <div class="variables-grid">
                <div 
                    v-for="c in campos" 
                    :key="c.id" 
                    class="selectable-card"
                    :class="{ 'selected': camposSeleccionadosIds.includes(c.id) }"
                    @click="toggleCampo(c.id)"
                >
                    <div class="card-icon">
                        <i :class="getIcon(c.magnitud_tipo)"></i>
                    </div>
                    <div class="card-info">
                        <span class="var-name">{{ c.nombre }}</span>
                        <span class="var-unit">{{ c.simbolo_unidad || '-' }}</span>
                    </div>
                    <div class="check-indicator">
                        <i class="bi bi-check-lg"></i>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- ALERTA DE ESTADO -->
        <div v-if="errorCampos" class="alert-box error">
            <i class="bi bi-x-circle"></i> {{ errorCampos }}
        </div>
        <div v-if="!loadingCampos && dispositivoSeleccionadoId && campos.length === 0" class="alert-box empty">
            <i class="bi bi-inbox"></i> Este dispositivo no tiene variables configuradas.
        </div>
        
        <!-- GRÁFICOS -->
        <div class="charts-container">
            <div class="charts-grid-multiple" v-if="camposFiltrados.length > 0 && modoVista === 'multiple' && dateRange.inicio">
                <GraficoHistorico
                    v-for="campo in camposFiltrados"
                    :key="'sep-'+campo.id"
                    :campo-id="campo.id"
                    :titulo="campo.nombre"
                    :fecha-inicio="dateRange.inicio" 
                    :fecha-fin="dateRange.fin"
                    :is-dark="isDark"
                    :metodo-carga="metodoCarga"
                />
            </div>
            
            <div class="charts-grid-single" v-else-if="camposFiltrados.length > 0 && modoVista === 'combinado' && dateRange.inicio">
                <GraficoCombinado
                    :key="'comb-'+dispositivoSeleccionadoId" 
                    :campos="camposFiltrados"
                    :fecha-inicio="dateRange.inicio"
                    :fecha-fin="dateRange.fin"
                    :is-dark="isDark"
                    :metodo-carga="metodoCarga"
                />
            </div>
        </div>
        
      </div>
    </div>
  </div>
</template>

<script>
import BarraLateralPlataforma from '../plataforma/BarraLateralPlataforma.vue';
import EncabezadoPlataforma from '../plataforma/EncabezadoPlataforma.vue';
import GraficoHistorico from './GraficoHistorico.vue';
import GraficoCombinado from './GraficoCombinado.vue'; 

export default {
    name: 'VistaReportes',
    components: {
        BarraLateralPlataforma,
        EncabezadoPlataforma,
        GraficoHistorico,
        GraficoCombinado
    },
    data() {
        return {
            isDark: false, 
            isSidebarOpen: true, 
            proyectos: [],
            dispositivos: [],
            campos: [], 
            
            proyectoSeleccionadoId: null,
            dispositivoSeleccionadoId: null,
            camposSeleccionadosIds: [], 

            // Fechas
            fechaMinimaDisponible: null,
            fechaMaximaDisponible: null,
            fechaInicioSeleccionada: null,
            fechaFinSeleccionada: null,
            horaInicioSeleccionada: '00:00',
            horaFinSeleccionada: '23:59',

            modoVista: 'multiple',
            metodoCarga: 'optimizado', 
            
            loadingProyectos: true,
            loadingDispositivos: false,
            loadingCampos: false,
            errorCampos: null,
            error: null,
        };
    },
    
    computed: {
        dateRange() {
            if (!this.fechaInicioSeleccionada || !this.fechaFinSeleccionada) {
                return { inicio: null, fin: null };
            }
            try {
                const inicioLocal = `${this.fechaInicioSeleccionada}T${this.horaInicioSeleccionada}:00`;
                const finLocal = `${this.fechaFinSeleccionada}T${this.horaFinSeleccionada}:00`;
                return { inicio: inicioLocal, fin: finLocal };
            } catch (e) {
                return { inicio: null, fin: null };
            }
        },
        camposFiltrados() {
            return this.campos.filter(c => this.camposSeleccionadosIds.includes(c.id));
        }
    },
    
    mounted() {
        this.cargarProyectos();
        this.detectarTemaSistema();
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', this.handleThemeChange);
        }
    },
    beforeUnmount() { 
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', this.handleThemeChange);
        }
    },
    methods: {
        toggleCampo(id) {
            const index = this.camposSeleccionadosIds.indexOf(id);
            if (index === -1) {
                this.camposSeleccionadosIds.push(id);
            } else {
                this.camposSeleccionadosIds.splice(index, 1);
            }
        },
        // ------------------------------------------------------
        // 1. CARGAR PROYECTOS 
        // ------------------------------------------------------
        async cargarProyectos() {
            this.loadingProyectos = true;
            const token = localStorage.getItem('accessToken');
            const resultado = JSON.parse(localStorage.getItem('resultado') || '{}');
            const usuarioId = resultado.usuario?.id;

            if (!token || !usuarioId) { 
                this.$router.push('/'); return; 
            }

            const params = new URLSearchParams({ page: 1, limit: 100 });

            try {
                const response = await fetch(`${API_BASE_URL}/api/proyectos/usuario/${usuarioId}?${params}`, { 
                    headers: { 'Authorization': `Bearer ${token}` } 
                });
                
                if (response.ok) {
                    const jsonResponse = await response.json();
                    this.proyectos = jsonResponse.data || [];
                    
                    if (this.proyectos.length > 0) {
                        this.proyectoSeleccionadoId = this.proyectos[0].id;
                        await this.cargarDispositivos(); 
                    }
                }
            } catch (err) {
                console.error(err);
            } finally {
                this.loadingProyectos = false;
            }
        },

        // ------------------------------------------------------
        // 2. CARGAR DISPOSITIVOS 
        // ------------------------------------------------------
        async cargarDispositivos() {
            this.loadingDispositivos = true;
            this.dispositivos = []; 
            this.campos = [];
            this.dispositivoSeleccionadoId = null;
            this.camposSeleccionadosIds = [];
            
            const token = localStorage.getItem('accessToken');
            if (!this.proyectoSeleccionadoId) return;
            
            const params = new URLSearchParams({ page: 1, limit: 100 });

            try {
                const response = await fetch(`${API_BASE_URL}/api/dispositivos/proyecto/${this.proyectoSeleccionadoId}?${params}`, { 
                    headers: { 'Authorization': `Bearer ${token}` } 
                });
                
                if (response.ok) { 
                    const jsonResponse = await response.json();
                    this.dispositivos = jsonResponse.data || [];
                }
                
                if (this.dispositivos.length > 0) {
                    this.dispositivoSeleccionadoId = this.dispositivos[0].id;
                    await this.cargarCamposYFechas();
                }
            } catch (err) {
                console.error(err);
            } finally {
                this.loadingDispositivos = false;
            }
        },
    
        async cargarCamposYFechas() {
            await this.cargarCampos();
            await this.cargarRangoDeFechas();
        },

        // ------------------------------------------------------
        // 3. CARGAR CAMPOS 
        // ------------------------------------------------------
        async cargarCampos() {
            this.loadingCampos = true;
            this.errorCampos = null;
            this.campos = [];
            this.camposSeleccionadosIds = [];
            
            const token = localStorage.getItem('accessToken');
            if (!this.dispositivoSeleccionadoId) return;

            try {
                const params = new URLSearchParams({ page: 1, limit: 50 });
                const sensoresResponse = await fetch(`${API_BASE_URL}/api/sensores/dispositivo/${this.dispositivoSeleccionadoId}?${params}`, { 
                    headers: { 'Authorization': `Bearer ${token}` } 
                });
                
                let sensores = [];
                if (sensoresResponse.ok) {
                    const sensoresData = await sensoresResponse.json();
                    sensores = Array.isArray(sensoresData) ? sensoresData : (sensoresData.data || []);
                }

                let todosLosCampos = [];
                for (const sensor of sensores) {
                    const camposResponse = await fetch(`${API_BASE_URL}/api/sensores/${sensor.id}/campos`, { 
                        headers: { 'Authorization': `Bearer ${token}` } 
                    });
                    
                    if (camposResponse.ok) {
                        const camposData = await camposResponse.json();
                        const listaCampos = camposData.campos || (Array.isArray(camposData) ? camposData : []);
                        todosLosCampos.push(...listaCampos); 
                    }
                }
                this.campos = todosLosCampos; 
                
            } catch (err) {
                console.error("Error al cargar campos:", err);
                this.errorCampos = 'Error al cargar los campos.';
            } finally {
                this.loadingCampos = false;
            }
        },
        
        // ------------------------------------------------------
        // FECHAS E ICONOS
        // ------------------------------------------------------
        async cargarRangoDeFechas() {
            const token = localStorage.getItem('accessToken');
            if (!this.dispositivoSeleccionadoId) return;

            try {
                const response = await fetch(`${API_BASE_URL}/api/valores/rango-fechas-dispositivo/${this.dispositivoSeleccionadoId}`, { 
                    headers: { 'Authorization': `Bearer ${token}` } 
                });
                
                if (response.ok) {
                    const rango = await response.json(); 
                    if (rango.fecha_minima) {
                        this.fechaMinimaDisponible = rango.fecha_minima.split('T')[0];
                        this.fechaInicioSeleccionada = this.fechaMinimaDisponible;
                    }
                    if (rango.fecha_maxima) {
                        this.fechaMaximaDisponible = rango.fecha_maxima.split('T')[0];
                        this.fechaFinSeleccionada = this.fechaMaximaDisponible;
                    }
                }
            } catch (err) {
                const hoy = new Date().toISOString().split('T')[0];
                this.fechaInicioSeleccionada = hoy;
                this.fechaFinSeleccionada = hoy;
            }
        },
        
        getIcon(magnitudTipo) {
            if (!magnitudTipo) return 'bi bi-speedometer2';
            const lower = magnitudTipo.toLowerCase();
            if (lower.includes('temperatura')) return 'bi bi-thermometer-half';
            if (lower.includes('humedad')) return 'bi bi-droplet-half';
            if (lower.includes('voltaje')) return 'bi bi-lightning-charge';
            return 'bi bi-activity'; 
        },
            
        toggleSidebar() { this.isSidebarOpen = !this.isSidebarOpen; },
        handleThemeChange(event) { this.isDark = event.matches; },
        detectarTemaSistema() {
            this.isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        }
    }
};
</script>

<style scoped lang="scss">
@use "sass:color";


.reportes-contenido {
    padding: 30px 40px;
    max-width: 1600px;
    margin: 0 auto;
}

// -----------------------------------
// 1. PANEL DE CONTROL MODERNO
// -----------------------------------
.control-panel {
    background-color: $WHITE;
    border-radius: 16px;
    padding: 25px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
    margin-bottom: 30px;
    border: 1px solid transparent;
}

.control-section {
    display: flex;
    flex-direction: column;
    gap: 15px;
    position: relative;
    
    .section-title {
        font-size: 0.95rem;
        font-weight: 700;
        text-transform: uppercase;
        color: $GRAY-COLD;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        gap: 8px;
        
        i { color: $PRIMARY-PURPLE; font-size: 1.1rem; }
    }
}

// INPUTS MODERNOS CON ICONO INTERNO
.form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
    
    label {
        font-size: 0.85rem;
        font-weight: 600;
        color: $DARK-TEXT;
    }
    
    .input-wrapper {
        position: relative;
        display: flex;
        align-items: center;
        
        .input-icon {
            position: absolute;
            left: 12px;
            color: $GRAY-COLD;
            pointer-events: none;
            font-size: 1rem;
        }
        
        .form-control {
            width: 100%;
            padding: 10px 15px 10px 40px; // Espacio para icono
            border-radius: 10px;
            border: 1px solid $LIGHT-BORDER;
            font-size: 0.95rem;
            transition: all 0.2s ease;
            background-color: $WHITE;
            appearance: none; 
            
            &:focus {
                border-color: $PRIMARY-PURPLE;
                box-shadow: 0 0 0 3px rgba($PRIMARY-PURPLE, 0.1);
                outline: none;
            }
            &:disabled {
                background-color: #f5f5f5;
                cursor: not-allowed;
                opacity: 0.7;
            }
        }
    }
}

// FILA DE TIEMPO
.time-row {
    display: flex;
    gap: 10px;
    .flex-grow { flex: 1; }
    .time-input { width: 110px; flex-shrink: 0; }
}

// PILL DE ESTADO
.status-pill {
    margin-top: 5px;
    font-size: 0.75rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 0;
    
    &.optimizado { color: $SUCCESS; }
    &.puro { color: $WARNING; }
}

// -----------------------------------
// 2. SELECTOR DE VARIABLES (GRID)
// -----------------------------------
.variables-panel {
    margin-bottom: 30px;
    
    .panel-header {
        margin-bottom: 15px;
        h4 { font-size: 1.1rem; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 8px; }
        .subtitle { font-size: 0.85rem; color: $GRAY-COLD; }
        i { color: $PRIMARY-PURPLE; }
    }
    
    .variables-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 15px;
    }
    
    .selectable-card {
        background-color: $WHITE;
        border: 1px solid $LIGHT-BORDER;
        border-radius: 12px;
        padding: 12px 15px;
        display: flex;
        align-items: center;
        gap: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
        
        &:hover { transform: translateY(-2px); border-color: $PRIMARY-PURPLE; }
        
        &.selected {
            background-color: rgba($PRIMARY-PURPLE, 0.08);
            border-color: $PRIMARY-PURPLE;
            
            .card-icon i { color: $PRIMARY-PURPLE; }
            .check-indicator { opacity: 1; transform: scale(1); }
        }
        
        .card-icon {
            width: 32px; height: 32px;
            background-color: rgba($GRAY-COLD, 0.1);
            border-radius: 8px;
            display: flex; align-items: center; justify-content: center;
            i { font-size: 1.1rem; color: $GRAY-COLD; transition: color 0.2s; }
        }
        
        .card-info {
            display: flex; flex-direction: column;
            .var-name { font-weight: 600; font-size: 0.9rem; color:$GRAY-COLD; }
            .var-unit { font-size: 0.75rem; color: $GRAY-COLD; }
        }
        
        .check-indicator {
            position: absolute; top: 8px; right: 8px;
            color: $PRIMARY-PURPLE;
            opacity: 0;
            transform: scale(0.5);
            transition: all 0.2s;
        }
    }
}

// -----------------------------------
// 3. GRÁFICOS Y ALERTAS
// -----------------------------------
.charts-container {
    margin-top: 30px;
}
.charts-grid-multiple, .charts-grid-single {
    display: grid;
    gap: 25px;
}
.charts-grid-multiple { grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); }
.charts-grid-single { grid-template-columns: 1fr; }

.alert-box {
    padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0; font-weight: 500;
    display: flex; align-items: center; justify-content: center; gap: 10px;
    
    &.empty { background-color: rgba($GRAY-COLD, 0.1); color: #555; }
    &.error { background-color: rgba($DANGER, 0.1); color: $DANGER; }
}

// -----------------------------------
// TEMAS (DARK MODE)
// -----------------------------------
.theme-dark {
    // Fondo general oscuro para que no se vea blanco
    background-color: $DARK-BG-CONTRAST;
    color: $LIGHT-TEXT;

    .control-panel {
        background-color: $SUBTLE-BG-DARK;
        border-color: rgba($WHITE, 0.05);
    }
    
    .form-group label { color: $GRAY-LIGHT; }
    
    .form-control {
        background-color: $DARK-INPUT-BG !important;
        border-color: $DARK-BORDER !important;
        color: $WHITE !important;
        
        &:focus { border-color: $PRIMARY-PURPLE !important; }
        &:disabled { background-color: rgba(0,0,0,0.2) !important; }
    }
    
    .section-title { color: $WHITE; }
    
    .selectable-card {
        background-color: $SUBTLE-BG-DARK;
        border-color: $DARK-BORDER;
        
        .var-name { color: $WHITE; }
        .card-icon { background-color: rgba($WHITE, 0.05); }
        
        &:hover { border-color: $PRIMARY-PURPLE;background-color: color.adjust($SUBTLE-BG-DARK, $lightness: 5%); }
        &.selected { background-color: rgba($PRIMARY-PURPLE, 0.15); }
    }
    
    .alert-box.empty { background-color: rgba($WHITE, 0.05); color: $GRAY-LIGHT; }
}

.theme-light {
    background-color: $WHITE-SOFT;
    .control-panel { border-color: $LIGHT-BORDER; }
      .card-info {
            display: flex; flex-direction: column;
            .var-name { font-weight: 600; font-size: 0.9rem; color:$BLACK; }
            .var-unit { font-size: 0.75rem; color: $GRAY-COLD; }
        }
}
</style>