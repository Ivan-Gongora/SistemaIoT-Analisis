<template>
  <div class="modulo-estado-sistema" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    
    <h3 class="modulo-titulo">
      <i class="bi bi-activity"></i> Estado del Sistema
    </h3>
    <p class="modulo-subtitulo">Métricas en tiempo real (Por el momento son datos fijos)</p>
    
    <div class="metric-list">
      <div class="metric-item">
        <div class="metric-icon metric-icon-success"><i class="bi bi-graph-up-arrow"></i></div>
        <div class="metric-label">Uptime</div>
        <div class="metric-value">{{ metrics.uptime }}</div>
      </div>

      <div class="metric-item">
        <div class="metric-icon metric-icon-accent"><i class="bi bi-lightning-fill"></i></div>
        <div class="metric-label">Latencia</div>
        <div class="metric-value">{{ metrics.latency }}</div>
      </div>
      
      <div class="metric-item">
        <div class="metric-icon metric-icon-primary"><i class="bi bi-globe"></i></div>
        <div class="metric-label">Conectados</div>
        <div class="metric-value">{{ metrics.connected }}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
    name: 'EstadoSistema',
    props: {
        isDark: {
            type: Boolean,
            required: true
        }
    },
    data() {
        return {
            metrics: {
                // Datos simulados (futuro endpoint de FastAPI)
                uptime: '99.9%',
                latency: '12ms',
                connected: '14/16'
            }
        };
    },
    // Nota: Los estilos SCSS se proporcionan en la siguiente sección
}
</script>

<style scoped lang="scss">
// ----------------------------------------
// VARIABLES DE LA PALETA
// ----------------------------------------
// $LIGHT-TEXT: #E4E6EB;
// $DARK-TEXT: #333333;
// $GRAY-COLD: #99A2AD;
// $BLUE-MIDNIGHT: #1A1A2E; 
// $SUBTLE-BG-DARK: #2B2B40; 
// $PRIMARY-PURPLE: #8A2BE2;
// $SUCCESS-COLOR: #1ABC9C;
// $ACCENT-COLOR: #FFC107; 
// $SUBTLE-BG-LIGHT: #FFFFFF;

// ----------------------------------------
// ESTILOS PRINCIPALES DEL MÓDULO
// ----------------------------------------
.modulo-estado-sistema {
    padding: 25px;
    border-radius: 15px;
    height: 100%;
    transition: background-color 0.3s;
}

.modulo-titulo {
    font-size: 1.4rem;
    font-weight: 600;
    margin-bottom: 5px;
    
    i { margin-right: 8px; color: $SUCCESS-COLOR; }
}

.modulo-subtitulo {
    font-size: 0.9rem;
    margin-bottom: 20px;
}

// ----------------------------------------
// ESTILOS DE MÉTRICAS INDIVIDUALES
// ----------------------------------------
.metric-list {
    display: flex;
    flex-direction: column;
    gap: 5px; 
}

.metric-item {
    display: grid;
    grid-template-columns: 30px 1fr auto;
    align-items: center;
    padding: 15px 0;
    border-bottom: 1px solid; 
    
    &:last-child {
        border-bottom: none;
    }
}

.metric-icon {
    font-size: 1.2rem;
    text-align: center;
    width: 30px;
}

/* Estilos de color para los iconos */
.metric-icon-success i { color: $SUCCESS-COLOR; }
.metric-icon-accent i { color: $ACCENT-COLOR; }
.metric-icon-primary i { color: $PRIMARY-PURPLE; }

.metric-label {
    font-weight: 500;
    margin-left: 10px;
}

.metric-value {
    font-weight: 700;
    font-size: 1.1rem;
    
    /* Aplica el color del icono al valor para contraste */
    .metric-item:nth-child(2) & { color: $ACCENT-COLOR; } 
    .metric-item:nth-child(3) & { color: $PRIMARY-PURPLE; }
}

// ----------------------------------------
// TEMAS
// ----------------------------------------

// MODO CLARO
.theme-light {
    background-color: $SUBTLE-BG-LIGHT; 
    color: $DARK-TEXT;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    
    .modulo-subtitulo, .metric-list .metric-item {
        color: $GRAY-COLD;
        border-bottom-color: #eee;
    }
}

// MODO OSCURO (Estilo fijo y profundo)
.theme-dark {
    background-color: $SUBTLE-BG-DARK; 
    color: $LIGHT-TEXT;
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.4);
    
    .modulo-titulo { color: $LIGHT-TEXT; }
    .modulo-subtitulo { color: $GRAY-COLD; }
    .metric-list .metric-item {
        border-bottom-color: rgba($LIGHT-TEXT, 0.1);
    }
}
</style>