<template>
  <div class="plataforma-tarjetas" :class="{ 'theme-dark': isDark, 'theme-light': !isDark }">
    <div class="row row-cols-1 row-cols-md-4 g-4">
      
      <div class="col" v-for="card in metricCards" :key="card.key">
        <div class="metric-card h-100">
          <div class="card-body">
            
            <div class="icon-container" :style="{ background: card.gradient }">
              <i :class="card.icon" class="metric-icon"></i>
            </div>
            
            <div class="metric-content">
              <p class="metric-value">{{ card.value }}</p>
              <p class="metric-label">{{ card.title }}</p>
            </div>
            
            <div class="metric-details" v-if="card.key === 'proyectos'">
              <span class="detail-new">{{ card.details }}</span>
              <router-link :to="card.link" class="detail-link">Explorar →</router-link>
            </div>

          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script>
export default {
  name: 'TarjetasPlataforma',
  data() {
    return {
      isDark: false,
      // Datos simulados (DEBEN SER CONSUMIDOS DE TU API EN EL FUTURO)
      metricCards: [
        { 
          key: 'proyectos', 
          title: 'PROYECTOS', 
          value: 1, 
          icon: 'fas fa-folder', 
          gradient: 'linear-gradient(to bottom right, #6F00FF, #A300FF)', // Morado
          details: '+2 nuevos este mes',
          link: '/mis-proyectos' 
        },
        { 
          key: 'dispositivos', 
          title: 'DISPOSITIVOS', 
          value: 1, 
          icon: 'fas fa-microchip', 
          gradient: 'linear-gradient(to bottom right, #00C853, #1ABC9C)', // Verde Menta
          details: 'Conectados ahora', // Solo para fines de prueba
          link: '/dispositivos'
        },
        { 
          key: 'sensores', 
          title: 'SENSORES', 
          value: 1, 
          icon: 'fas fa-signal', 
          gradient: 'linear-gradient(to bottom right, #FF8C00, #FFA500)', // Naranja Cítrico
          details: 'Recopilando datos', // Solo para fines de prueba
          link: '/sensores'
        },
        { 
          key: 'reportes', 
          title: 'REPORTES', 
          value: 1, 
          icon: 'fas fa-file-alt', 
          gradient: 'linear-gradient(to bottom right, #FF5733, #FF8C00)', // Rojo/Naranja
          details: 'Generados este mes', // Solo para fines de prueba
          link: '/reportes'
        }
      ]
    };
  },
  mounted() {
    this.detectarTemaSistema();
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', this.handleThemeChange);
    }
  },
  // 🚨 CORRECCIÓN CLAVE: Usamos beforeUnmount (Compatible con Vue 3/ESLint)
  beforeUnmount() { 
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', this.handleThemeChange);
    }
  },
  methods: {
    handleThemeChange(event) {
      this.isDark = event.matches;
    },
    detectarTemaSistema() {
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        this.isDark = true;
      } else {
        this.isDark = false;
      }
    }
  }
};
</script>

<style scoped lang="scss">
// ----------------------------------------
// VARIABLES DE LA PALETA "IoT SPECTRUM"
// ----------------------------------------
$PRIMARY-PURPLE: #8A2BE2; 
$ACCENT-COLOR: #7B1FA2;   
$SUCCESS-COLOR: #1ABC9C;  

// GRADIENTES
$GRADIENT-SUCCESS: linear-gradient(to right, #00C853, #1ABC9C);
$PURPLE-GRADIENT: linear-gradient(to right, #6F00FF, #A300FF);

// COLORES BASE
$WHITE-SOFT: #F7F9FC;     // Fondo Claro
$BLUE-MIDNIGHT: #1A1A2E;  // Fondo Oscuro
$DARK-TEXT: #333333;      // Texto Claro (Modo Light)
$LIGHT-TEXT: #E4E6EB;     // Texto Oscuro (Modo Dark)
$SUBTLE-BG-DARK: #2B2B40; // Fondo de tarjeta en Modo Oscuro (como en tu imagen)
$SUBTLE-BG-LIGHT: #FFFFFF; // Fondo de tarjeta en Modo Claro
$GRAY-COLD: #99A2AD;      // Subtítulos
$DARK-BG-CONTRAST: #131322; // Fondo para que las tarjetas oscuras resalten más
$DARK-DETAILS: rgba($LIGHT-TEXT, 0.4); // Detalles sutiles en modo oscuro

// ----------------------------------------
// ESTRUCTURA GENERAL
// ----------------------------------------
.plataforma-tarjetas {
  padding: 0 40px;
  transition: background-color 0.3s; 
}

// ----------------------------------------
// CARD DE MÉTRICAS INDIVIDUAL
// ----------------------------------------
.metric-card {
  border: none;
  border-radius: 20px; // Aplicar el borde redondeado también al base
  padding: 28px; // Aumentar ligeramente el padding para que respire
  transition: all 0.2s ease-in-out;
  height: 100%;
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  }
}

// ----------------------------------------
// ELEMENTOS DE LA CARD
// ----------------------------------------

.icon-container {
  width: 45px;
  height: 45px;
  border-radius: 10px;
  margin-bottom: 20px;
  float: right; 
  display: flex;
  justify-content: center;
  align-items: center;
  
  .metric-icon {
    color: #fff;
    font-size: 1.2rem;
  }
}

.metric-content {
  text-align: left;
  
  .metric-value {
    color: $LIGHT-TEXT; 

    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 0px;
    line-height: 1;
  }
  .metric-label {
    // font-size: 0.9rem;
    font-weight: 500;
    text-transform: uppercase;
    // letter-spacing: 0.5px;
    margin-top: 5px;
    margin-bottom: 20px;
    clear: both; 
    color: $GRAY-COLD;
    font-size: 0.85rem; // Ligero aumento para mejor lectura
    letter-spacing: 0.8px; // Aumentar el espaciado para un look limpio
  }
}

.metric-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
  padding-top: 10px;
  border-top-style: solid; 
  border-top-width: 1px;

  .detail-new {
    font-size: 0.85rem;
    font-weight: 500;
    color: $PRIMARY-PURPLE;
  }
  .detail-link {
    font-size: 0.85rem;
    color: $PRIMARY-PURPLE;
    text-decoration: none;
    font-weight: 600;
    transition: color 0.2s;
    
    &:hover {
        opacity: 0.8;
    }
  }
}

// ----------------------------------------
// TEMAS (DARK/LIGHT)
// ----------------------------------------

// MODO CLARO
.theme-light {
    background-color: $WHITE-SOFT; 
    .metric-card {
        background-color: $SUBTLE-BG-LIGHT; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    }
    .metric-value {
        color: $DARK-TEXT;
    }
    .metric-label {
        color: $GRAY-COLD;
    }
    .metric-details {
        border-top-color: rgba($DARK-TEXT, 0.1);
    }
}

// MODO OSCURO
.theme-dark {
    background-color: $DARK-BG-CONTRAST; 
    
    .metric-card {
        background-color: $SUBTLE-BG-DARK; /* Mantiene el fondo oscuro de la tarjeta */
        
        // 🚨 AJUSTE CLAVE: Sombra más moderna y sutil para la elevación
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4); 
        
        // 🚨 Aumentamos el radio para un look moderno
        border-radius: 20px; 
    }
    .metric-value {
        color: $LIGHT-TEXT;
    }
    .metric-label {
        color: $DARK-DETAILS;
    }
    .metric-details {
        border-top-color: rgba($LIGHT-TEXT, 0.2);
    }
    .detail-new, .detail-link {
        color: $LIGHT-TEXT;
    }
}
</style>