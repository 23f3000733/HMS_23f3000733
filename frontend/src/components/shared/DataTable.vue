<template>
  <div class="data-table p-lg-2">
    <!-- Search & Actions -->
    <div class="table-header mb-3 d-flex justify-content-between align-items-center">
      <div
        v-if="searchable"
        class="search-box"
      >
        <input 
          v-model="searchQuery" 
          type="text" 
          class="form-control"
          :placeholder="searchPlaceholder"
          @input="handleSearch"
        >
      </div>
      <div
        v-if="showDownloadButton"
        class="download-button"
      >
        <button
          class="btn btn-outline-secondary btn-sm"
          @click="downloadCSV"
        >
          <i class="bi bi-download me-1" /> Download CSV
        </button>
      </div>
    </div>

    <!-- Loading Skeleton -->
    <TableSkeleton
      v-if="loading"
      :rows="perPage"
      :columns="columns.length + (hasActions ? 1 : 0)"
    />

    <!-- Table -->
    <div
      v-else
      class="table-responsive"
    >
      <table class="table table-hover">
        <thead>
          <tr>
            <th 
              v-for="column in columns" 
              :key="column.key"
              :class="{ 'sortable': column.sortable, 'text-center': column.align === 'center' }"
              @click="column.sortable && handleSort(column.key)"
            >
              {{ column.label }}
              <i
                v-if="column.sortable"
                class="bi"
                :class="getSortIcon(column.key)"
              />
            </th>
            <th
              v-if="hasActions"
              class="text-center"
            >
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          <!-- Empty State -->
          <tr v-if="paginatedData.length === 0">
            <td
              :colspan="columns.length + (hasActions ? 1 : 0)"
              class="text-center py-5 text-muted"
            >
              <i class="bi bi-inbox display-4 d-block mb-3" />
              <p class="mb-0">
                {{ emptyMessage }}
              </p>
            </td>
          </tr>

          <!-- Data Rows -->
          <tr
            v-for="(row, index) in paginatedData"
            v-else
            :key="index"
          >
            <td 
              v-for="column in columns" 
              :key="column.key"
              :class="{ 'text-center': column.align === 'center' }"
            >
              <!-- Custom Column Slot -->
              <slot
                :name="`column-${column.key}`"
                :row="row"
                :value="row[column.key]"
              >
                {{ formatValue(row[column.key], column.format) }}
              </slot>
            </td>

            <!-- Action Buttons -->
            <td
              v-if="hasActions"
              class="text-center"
            >
              <slot
                name="actions"
                :row="row"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div
      v-if="paginated && totalPages > 1"
      class="pagination-controls d-flex justify-content-between align-items-center mt-3"
    >
      <div class="pagination-info text-muted small">
        Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ totalItems }} entries
      </div>
      <nav>
        <ul class="pagination mb-0">
          <li
            class="page-item"
            :class="{ disabled: currentPage === 1 }"
          >
            <a
              class="page-link"
              href="#"
              @click.prevent="changePage(currentPage - 1)"
            >
              Previous
            </a>
          </li>
          <li 
            v-for="page in displayedPages" 
            :key="page"
            class="page-item" 
            :class="{ active: page === currentPage }"
          >
            <a
              class="page-link"
              href="#"
              @click.prevent="changePage(page)"
            >
              {{ page }}
            </a>
          </li>
          <li
            class="page-item"
            :class="{ disabled: currentPage === totalPages }"
          >
            <a
              class="page-link"
              href="#"
              @click.prevent="changePage(currentPage + 1)"
            >
              Next
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script>
import TableSkeleton from './TableSkeleton.vue'

export default {
  name: 'DataTable',
  components: {
    TableSkeleton
  },
  props: {
    columns: {
      type: Array,
      required: true,
      // Example: [{ key: 'name', label: 'Name', sortable: true, format: 'uppercase' }]
    },
    data: {
      type: [Array, Object],
      required: true,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    searchable: {
      type: Boolean,
      default: true
    },
    searchPlaceholder: {
      type: String,
      default: 'Search...'
    },
    paginated: {
      type: Boolean,
      default: true
    },
    perPage: {
      type: Number,
      default: 10
    },
    emptyMessage: {
      type: String,
      default: 'No data available'
    },
    showDownloadButton: {
      type: Boolean,
      default: false
    },
    fileName: {
      type: String,
      default: 'data.csv'
    }
  },
  data() {
    return {
      searchQuery: '',
      sortKey: '',
      sortOrder: 'asc',
      currentPage: 1
    }
  },
  computed: {
    hasActions() {
      return !!this.$slots.actions
    },
    filteredData() {
      // Ensure data is an array
      const dataArray = Array.isArray(this.data) ? this.data : [];
      
      if (!this.searchQuery) return dataArray

      const query = this.searchQuery.toLowerCase()
      return dataArray.filter(row => {
        return this.columns.some(column => {
          const value = String(row[column.key] || '').toLowerCase()
          return value.includes(query)
        })
      })
    },
    sortedData() {
      // Ensure filteredData is an array
      const dataArray = Array.isArray(this.filteredData) ? this.filteredData : [];
      
      if (!this.sortKey) return dataArray

      return [...dataArray].sort((a, b) => {
        const aVal = a[this.sortKey]
        const bVal = b[this.sortKey]
        
        if (aVal === bVal) return 0
        
        const comparison = aVal > bVal ? 1 : -1
        return this.sortOrder === 'asc' ? comparison : -comparison
      })
    },
    paginatedData() {
      // Ensure sortedData is an array
      const dataArray = Array.isArray(this.sortedData) ? this.sortedData : [];
      
      if (!this.paginated) return dataArray

      const start = (this.currentPage - 1) * this.perPage
      const end = start + this.perPage
      return dataArray.slice(start, end)
    },
    totalItems() {
      // Ensure sortedData is an array
      const dataArray = Array.isArray(this.sortedData) ? this.sortedData : [];
      return dataArray.length
    },
    totalPages() {
      // Ensure perPage is valid
      const perPage = this.perPage > 0 ? this.perPage : 10;
      return Math.ceil(this.totalItems / perPage)
    },
    startIndex() {
      return (this.currentPage - 1) * this.perPage
    },
    endIndex() {
      return Math.min(this.startIndex + this.perPage, this.totalItems)
    },
    displayedPages() {
      const pages = []
      const maxPages = 5
      
      let start = Math.max(1, this.currentPage - Math.floor(maxPages / 2))
      const end = Math.min(this.totalPages, start + maxPages - 1)
      
      if (end - start < maxPages - 1) {
        start = Math.max(1, end - maxPages + 1)
      }
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
    }
  },
  methods: {
    handleSearch() {
      this.currentPage = 1 // Reset to first page on search
    },
    handleSort(key) {
      if (this.sortKey === key) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc'
      } else {
        this.sortKey = key
        this.sortOrder = 'asc'
      }
    },
    getSortIcon(key) {
      if (this.sortKey !== key) return 'bi-arrow-down-up'
      return this.sortOrder === 'asc' ? 'bi-sort-up' : 'bi-sort-down'
    },
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
      }
    },
    formatValue(value, format) {
      if (value === null || value === undefined) return ''
      
      switch (format) {
        case 'uppercase':
          return String(value).toUpperCase()
        case 'lowercase':
          return String(value).toLowerCase()
        case 'capitalize':
          return String(value).charAt(0).toUpperCase() + String(value).slice(1)
        case 'date':
          return new Date(value).toLocaleDateString()
        default:
          return value
      }
    },
    downloadCSV() {
      // Show alert instead of direct download
      alert('Sending CSV file to your email...');
      
      // Emit event to parent component to handle email-based export
      this.$emit('download-requested');
    }
  }
}
</script>

<style scoped>
.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  background-color: var(--bs-light);
}

.table-actions {
  display: flex;
  gap: 0.5rem;
}

.search-box {
  max-width: 300px;
}

.download-button {
  margin-left: 1rem;
}
</style>