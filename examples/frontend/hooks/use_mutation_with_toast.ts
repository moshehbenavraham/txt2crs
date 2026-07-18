/**
 * EXAMPLE: TanStack Query mutation with toast notifications
 *
 * PATTERN: Mutation with Optimistic UI Feedback
 * USE WHEN: Performing create/update/delete operations with user feedback
 * TAGS: mutation, toast, tanstack-query, hooks
 *
 * This example demonstrates:
 * 1. useMutation with success/error callbacks
 * 2. Toast notifications for user feedback
 * 3. Query invalidation for cache refresh
 * 4. Error handling with API error utility
 *
 * Based on: frontend/src/hooks/useSaveToItems.ts
 */

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { ItemsService } from "@/client";
import type { ItemCreate, ItemPublic } from "@/client/types.gen";
import { handleError } from "@/utils";

/**
 * Hook for creating items with toast notifications.
 *
 * @returns Mutation object with mutate, mutateAsync, isPending, etc.
 *
 * @example
 * ```tsx
 * function CreateItemButton() {
 *   const createItem = useCreateItem();
 *
 *   const handleClick = () => {
 *     createItem.mutate({
 *       title: "New Item",
 *       description: "Created from button",
 *     });
 *   };
 *
 *   return (
 *     <Button
 *       onClick={handleClick}
 *       disabled={createItem.isPending}
 *     >
 *       {createItem.isPending ? "Creating..." : "Create Item"}
 *     </Button>
 *   );
 * }
 * ```
 */
export function useCreateItem() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    // Step 1: Define the mutation function
    // This calls the generated API client
    mutationFn: (item: ItemCreate) =>
      ItemsService.createItem({ requestBody: item }),

    // Step 2: Handle success
    onSuccess: (data: ItemPublic) => {
      // Invalidate items query to refetch the list
      queryClient.invalidateQueries({ queryKey: ["items"] });

      // Show success toast
      toast.success("Item created successfully", {
        description: `"${data.title}" has been saved`,
      });
    },

    // Step 3: Handle errors
    onError: (error: Error) => {
      // Use centralized error handler
      handleError(error);

      // Or show simple error toast
      // toast.error("Failed to create item", {
      //   description: error.message,
      // });
    },
  });

  return mutation;
}

/**
 * Hook for deleting items with confirmation toast.
 *
 * @example
 * ```tsx
 * function DeleteButton({ itemId }: { itemId: string }) {
 *   const deleteItem = useDeleteItem();
 *
 *   return (
 *     <Button
 *       variant="destructive"
 *       onClick={() => deleteItem.mutate(itemId)}
 *       disabled={deleteItem.isPending}
 *     >
 *       Delete
 *     </Button>
 *   );
 * }
 * ```
 */
export function useDeleteItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (itemId: string) =>
      ItemsService.deleteItem({ id: itemId }),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["items"] });
      toast.success("Item deleted");
    },

    onError: (error: Error) => {
      toast.error("Failed to delete item", {
        description: error.message,
      });
    },
  });
}

// === KEY PATTERNS USED ===
//
// 1. Query Invalidation
//    queryClient.invalidateQueries({ queryKey: ["items"] })
//    - Marks cached queries as stale
//    - Triggers refetch of items list
//    - Use exact: true for specific query matching
//
// 2. Toast Notifications (sonner)
//    toast.success("Message", { description: "Details" })
//    toast.error("Error message")
//    toast.loading("Loading...")
//    - Provides immediate user feedback
//    - Auto-dismisses after timeout
//
// 3. Mutation States
//    - isPending: true while mutation is in progress
//    - isError: true if mutation failed
//    - isSuccess: true if mutation succeeded
//    - Use for button disabled states, loading indicators
//
// 4. mutate vs mutateAsync
//    mutation.mutate(data)      // Fire and forget
//    await mutation.mutateAsync(data)  // Returns promise
//    - Use mutateAsync when you need to await the result


// === MUTATION WITH OPTIMISTIC UPDATE ===
//
// export function useUpdateItem() {
//   const queryClient = useQueryClient();
//
//   return useMutation({
//     mutationFn: ({ id, data }: { id: string; data: ItemUpdate }) =>
//       ItemsService.updateItem({ id, requestBody: data }),
//
//     // Optimistic update: update cache immediately
//     onMutate: async ({ id, data }) => {
//       await queryClient.cancelQueries({ queryKey: ["items"] });
//
//       const previousItems = queryClient.getQueryData<ItemPublic[]>(["items"]);
//
//       queryClient.setQueryData<ItemPublic[]>(["items"], (old) =>
//         old?.map((item) =>
//           item.id === id ? { ...item, ...data } : item
//         )
//       );
//
//       return { previousItems };
//     },
//
//     // Rollback on error
//     onError: (err, variables, context) => {
//       if (context?.previousItems) {
//         queryClient.setQueryData(["items"], context.previousItems);
//       }
//       toast.error("Failed to update item");
//     },
//
//     onSuccess: () => {
//       toast.success("Item updated");
//     },
//
//     // Always refetch after error or success
//     onSettled: () => {
//       queryClient.invalidateQueries({ queryKey: ["items"] });
//     },
//   });
// }

export default useCreateItem;
