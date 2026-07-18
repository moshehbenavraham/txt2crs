/**
 * EXAMPLE: TanStack Query with Suspense for data fetching
 *
 * PATTERN: Suspense Query with Type-Safe API Client
 * USE WHEN: Fetching data in components that use React Suspense
 * TAGS: query, suspense, tanstack-query, hooks, data-fetching
 *
 * This example demonstrates:
 * 1. useSuspenseQuery for Suspense-compatible data fetching
 * 2. Type-safe query keys
 * 3. Proper query configuration
 * 4. Integration with generated API client
 *
 * Based on: frontend/src/hooks/useAuth.ts
 */

import { useSuspenseQuery, useQuery } from "@tanstack/react-query";

import { ItemsService, UsersService } from "@/client";
import type { ItemPublic, ItemsPublic, UserPublic } from "@/client/types.gen";

/**
 * Fetch current user with Suspense.
 *
 * This hook suspends the component while loading, so it must be used
 * within a Suspense boundary.
 *
 * @example
 * ```tsx
 * // In parent component
 * <Suspense fallback={<Spinner />}>
 *   <UserProfile />
 * </Suspense>
 *
 * // In UserProfile component
 * function UserProfile() {
 *   const { user } = useCurrentUser();
 *   return <div>Hello, {user.full_name}</div>;
 * }
 * ```
 */
export function useCurrentUser() {
  const { data: user } = useSuspenseQuery<UserPublic>({
    // Step 1: Define unique query key
    // Query keys are used for caching and invalidation
    queryKey: ["currentUser"],

    // Step 2: Define fetch function
    // Uses generated API client for type safety
    queryFn: () => UsersService.readUserMe(),

    // Step 3: Configure caching behavior (optional)
    // staleTime: 5 * 60 * 1000, // Consider fresh for 5 minutes
    // gcTime: 30 * 60 * 1000,   // Keep in cache for 30 minutes
  });

  return { user };
}

/**
 * Fetch paginated items with Suspense.
 *
 * @param options - Pagination and filter options
 *
 * @example
 * ```tsx
 * function ItemsList() {
 *   const { items, count } = useItems({ limit: 20, skip: 0 });
 *
 *   return (
 *     <div>
 *       <p>Total: {count} items</p>
 *       {items.map((item) => (
 *         <ItemCard key={item.id} item={item} />
 *       ))}
 *     </div>
 *   );
 * }
 * ```
 */
export function useItems(options: {
  skip?: number;
  limit?: number;
  contentType?: string;
} = {}) {
  const { skip = 0, limit = 100, contentType } = options;

  const { data } = useSuspenseQuery<ItemsPublic>({
    // Include parameters in query key for proper caching
    queryKey: ["items", { skip, limit, contentType }],

    queryFn: () =>
      ItemsService.readItems({
        skip,
        limit,
        contentType: contentType as "general" | undefined,
      }),
  });

  return {
    items: data.data,
    count: data.count,
  };
}

/**
 * Fetch single item by ID with Suspense.
 *
 * @example
 * ```tsx
 * function ItemDetail({ itemId }: { itemId: string }) {
 *   const { item } = useItem(itemId);
 *   return <h1>{item.title}</h1>;
 * }
 * ```
 */
export function useItem(itemId: string) {
  const { data: item } = useSuspenseQuery<ItemPublic>({
    queryKey: ["items", itemId],
    queryFn: () => ItemsService.readItem({ id: itemId }),
    // Only fetch if itemId is provided
    // enabled: !!itemId,  // Note: Not supported with useSuspenseQuery
  });

  return { item };
}

// === NON-SUSPENSE VERSION ===
//
// Use regular useQuery when you want to handle loading states manually
// or when the component doesn't need Suspense.
//
// export function useItemsManual(options: { skip?: number; limit?: number } = {}) {
//   const { skip = 0, limit = 100 } = options;
//
//   const { data, isLoading, isError, error } = useQuery<ItemsPublic>({
//     queryKey: ["items", { skip, limit }],
//     queryFn: () => ItemsService.readItems({ skip, limit }),
//   });
//
//   return {
//     items: data?.data ?? [],
//     count: data?.count ?? 0,
//     isLoading,
//     isError,
//     error,
//   };
// }


// === KEY PATTERNS USED ===
//
// 1. Query Keys
//    - ["currentUser"]           - Simple key
//    - ["items", { skip, limit }] - Key with parameters
//    - ["items", itemId]          - Key with ID
//    - Used for caching, invalidation, and refetching
//
// 2. useSuspenseQuery vs useQuery
//    - useSuspenseQuery: Suspends component, data is always defined
//    - useQuery: Returns loading/error states, data may be undefined
//    - Choose based on component structure
//
// 3. Query Configuration
//    - staleTime: How long data is considered fresh
//    - gcTime: How long to keep in cache after unmount
//    - enabled: Conditional fetching (useQuery only)
//    - refetchOnWindowFocus: Refetch when tab becomes active
//
// 4. Type-Safe API Client
//    - ItemsService.readItems() returns typed response
//    - No need for manual type assertions
//    - Generated from OpenAPI spec


// === QUERY KEY FACTORY PATTERN ===
//
// For larger apps, organize query keys in a factory:
//
// export const itemKeys = {
//   all: ["items"] as const,
//   lists: () => [...itemKeys.all, "list"] as const,
//   list: (filters: { skip?: number; limit?: number }) =>
//     [...itemKeys.lists(), filters] as const,
//   details: () => [...itemKeys.all, "detail"] as const,
//   detail: (id: string) => [...itemKeys.details(), id] as const,
// };
//
// // Usage:
// queryKey: itemKeys.list({ skip: 0, limit: 20 })
// queryKey: itemKeys.detail(itemId)
// queryClient.invalidateQueries({ queryKey: itemKeys.all })

export default useCurrentUser;
