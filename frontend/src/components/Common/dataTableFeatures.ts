import {
  columnVisibilityFeature,
  createPaginatedRowModel,
  rowPaginationFeature,
  tableFeatures,
} from "@tanstack/react-table"

/**
 * TanStack Table v9 feature set shared by `DataTable` and its column
 * definitions. Module-level so the reference stays stable across renders.
 * The core row model is built in; v9 makes every other feature opt-in.
 */
export const dataTableFeatures = tableFeatures({
  // v8 had visibility built in; DataTable renders via row.getVisibleCells().
  columnVisibilityFeature,
  rowPaginationFeature,
  paginatedRowModel: createPaginatedRowModel(),
})

export type DataTableFeatures = typeof dataTableFeatures
