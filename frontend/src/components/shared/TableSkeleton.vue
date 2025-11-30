<template>
  <div class="table-skeleton">
    <div class="skeleton-table">
      <div class="skeleton-thead">
        <div class="skeleton-tr">
          <div
            v-for="n in columns"
            :key="n"
            class="skeleton-th"
          >
            <div
              class="skeleton-box"
              style="height: 16px; width: 80%;"
            />
          </div>
        </div>
      </div>
      <div class="skeleton-tbody">
        <div
          v-for="r in rows"
          :key="r"
          class="skeleton-tr"
        >
          <div
            v-for="c in columns"
            :key="c"
            class="skeleton-td"
          >
            <div
              class="skeleton-box"
              style="height: 14px; width: 90%;"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TableSkeleton',
  props: {
    rows: {
      type: Number,
      default: 5
    },
    columns: {
      type: Number,
      default: 4
    }
  }
}
</script>

<style scoped>
.table-skeleton {
  width: 100%;
  padding: 1rem;
}

.skeleton-table {
  width: 100%;
}

.skeleton-thead {
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 0.5rem;
}

.skeleton-tbody {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.skeleton-tr {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 1rem;
  padding: 0.75rem 0;
}

.skeleton-th {
  padding: 0.5rem;
}

.skeleton-td {
  padding: 0.25rem;
}

.skeleton-box {
  background: linear-gradient(
    90deg,
    #f0f0f0 0%,
    #e0e0e0 50%,
    #f0f0f0 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}
</style>
