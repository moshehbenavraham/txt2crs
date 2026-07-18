/**
 * Item management form schemas.
 *
 * Composed from base field schemas in ./fields.ts
 *
 * @module lib/schemas/item
 */
import { z } from "zod"

import {
  itemContentField,
  itemContentTypeField,
  itemDescriptionField,
  itemSourceUrlField,
  itemTitleField,
} from "./fields"

// =============================================================================
// Add Item
// =============================================================================

/**
 * Add item form schema.
 * Used in: components/Items/AddItem.tsx
 */
export const addItemSchema = z.object({
  title: itemTitleField,
  description: itemDescriptionField,
})

export type AddItemFormData = z.infer<typeof addItemSchema>

// =============================================================================
// Edit Item
// =============================================================================

/**
 * Edit item form schema.
 * Used in: components/Items/EditItem.tsx
 */
export const editItemSchema = z.object({
  title: itemTitleField,
  description: itemDescriptionField,
})

export type EditItemFormData = z.infer<typeof editItemSchema>

// =============================================================================
// Extended Item (Future Use)
// =============================================================================

/**
 * Full item form schema including all content fields.
 * For future use when content editing is implemented.
 */
export const fullItemSchema = z.object({
  title: itemTitleField,
  description: itemDescriptionField,
  content: itemContentField,
  content_type: itemContentTypeField,
  source_url: itemSourceUrlField,
})

export type FullItemFormData = z.infer<typeof fullItemSchema>

// =============================================================================
// Items List Filter
// =============================================================================

/**
 * Items list search/filter parameters schema.
 * Used in: routes/_layout/items.tsx (validateSearch)
 */
export const itemsSearchSchema = z.object({
  type: z.enum(["all", "general"]).default("all"),
})

export type ItemsSearchParams = z.infer<typeof itemsSearchSchema>
