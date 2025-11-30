<template>
  <div class="donut-chart-container">
    <svg
      viewBox="0 0 36 36"
      class="donut-chart"
    >
      <!-- Background Circle -->
      <path
        class="donut-bg"
        d="M18 2.0845
          a 15.9155 15.9155 0 0 1 0 31.831
          a 15.9155 15.9155 0 0 1 0 -31.831"
      />
      
      <!-- Segments -->
      <path
        v-for="(segment, index) in segments"
        :key="index"
        class="donut-segment"
        :stroke="segment.color"
        :stroke-dasharray="segment.dashArray"
        :stroke-dashoffset="segment.dashOffset"
        d="M18 2.0845
          a 15.9155 15.9155 0 0 1 0 31.831
          a 15.9155 15.9155 0 0 1 0 -31.831"
        @mouseenter="hoveredSegment = index"
        @mouseleave="hoveredSegment = null"
      />
      
      <!-- Center Text -->
      <text
        x="18"
        y="20.35"
        class="donut-text"
      >
        {{ total }}
      </text>
    </svg>
    
    <!-- Legend -->
    <div class="legend mt-3">
      <div
        v-for="(item, index) in data"
        :key="index"
        class="legend-item"
      >
        <span
          class="dot"
          :style="{ backgroundColor: item.color }"
        />
        <span class="label">{{ item.label }}</span>
        <span class="value fw-bold ms-auto">{{ item.value }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DonutChart',
  props: {
    data: {
      type: Array,
      required: true,
      // Expected format: [{ label: 'Active', value: 10, color: '#007aff' }, ...]
    }
  },
  data() {
    return {
      hoveredSegment: null
    }
  },
  computed: {
    total() {
      return this.data.reduce((acc, curr) => acc + curr.value, 0)
    },
    segments() {
      let currentOffset = 25; // Start at top (12 o'clock)
      const total = this.total || 1; // Avoid division by zero
      
      return this.data.map(item => {
        const percentage = (item.value / total) * 100;
        const dashArray = `${percentage} ${100 - percentage}`;
        const dashOffset = currentOffset;
        
        // Update offset for next segment (counter-clockwise)
        currentOffset -= percentage;
        
        return {
          ...item,
          dashArray,
          dashOffset
        }
      });
    }
  }
}
</script>

<style scoped>
.donut-chart-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.donut-chart {
  width: 100%;
  max-width: 200px;
  display: block;
}

.donut-bg {
  fill: none;
  stroke: #f5f5f7;
  stroke-width: 3.8;
}

.donut-segment {
  fill: none;
  stroke-width: 3.8;
  stroke-linecap: round;
  transition: stroke-width 0.2s ease;
  cursor: pointer;
}

.donut-segment:hover {
  stroke-width: 4.5;
}

.donut-text {
  fill: #1d1d1f;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 0.5em;
  font-weight: 700;
  text-anchor: middle;
}

.legend {
  width: 100%;
  font-size: 0.85rem;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  color: #424245;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
}
</style>
