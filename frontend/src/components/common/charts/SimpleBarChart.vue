<template>
  <div
    class="simple-bar-chart"
    :style="{ height: height + 'px' }"
  >
    <div class="chart-container">
      <div 
        v-for="(item, index) in normalizedData" 
        :key="index" 
        class="bar-group"
        @mouseenter="hoveredIndex = index"
        @mouseleave="hoveredIndex = null"
      >
        <div class="bar-wrapper">
          <div 
            class="bar" 
            :style="{ 
              height: item.percent + '%',
              backgroundColor: color
            }"
          />
          <div
            v-if="hoveredIndex === index"
            class="tooltip-value"
          >
            {{ item.value }}
          </div>
        </div>
        <div class="label">
          {{ item.label }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SimpleBarChart',
  props: {
    data: {
      type: Array,
      required: true,
      // Expected format: [{ label: 'Mon', value: 10 }, ...]
    },
    color: {
      type: String,
      default: '#007aff'
    },
    height: {
      type: Number,
      default: 200
    }
  },
  data() {
    return {
      hoveredIndex: null
    }
  },
  computed: {
    maxValue() {
      return Math.max(...this.data.map(d => d.value), 1)
    },
    normalizedData() {
      return this.data.map(d => ({
        ...d,
        percent: (d.value / this.maxValue) * 100
      }))
    }
  }
}
</script>

<style scoped>
.simple-bar-chart {
  width: 100%;
  position: relative;
}

.chart-container {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  height: 100%;
  padding-bottom: 24px; /* Space for labels */
}

.bar-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  position: relative;
  cursor: pointer;
}

.bar-wrapper {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  position: relative;
}

.bar {
  width: 60%;
  border-radius: 4px 4px 0 0;
  transition: height 0.3s ease-out, opacity 0.2s;
  min-height: 4px; /* Ensure visibility even if 0 */
  opacity: 0.8;
}

.bar-group:hover .bar {
  opacity: 1;
}

.label {
  position: absolute;
  bottom: -24px;
  font-size: 0.75rem;
  color: #86868b;
  white-space: nowrap;
}

.tooltip-value {
  position: absolute;
  top: -30px;
  background: #1d1d1f;
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  pointer-events: none;
  animation: fadeIn 0.2s;
  z-index: 10;
}

.tooltip-value::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 4px solid #1d1d1f;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
