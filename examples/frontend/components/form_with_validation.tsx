/**
 * EXAMPLE: Form with Zod validation and React Hook Form
 *
 * PATTERN: Validated Form with Type-Safe Submission
 * USE WHEN: Creating forms that submit data to the API
 * TAGS: form, validation, zod, react-hook-form, components
 *
 * This example demonstrates:
 * 1. Zod schema for validation rules
 * 2. React Hook Form integration
 * 3. Controlled form inputs with shadcn/ui
 * 4. Type-safe form submission
 * 5. Error display and handling
 *
 * Based on: frontend/src/lib/schemas/, frontend components
 */

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

// Step 1: Define Zod schema for validation
// This should mirror backend Pydantic validation exactly
const itemFormSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(255, "Title must be 255 characters or less"),
  description: z
    .string()
    .max(255, "Description must be 255 characters or less")
    .optional()
    .or(z.literal("")),
});

// Step 2: Infer TypeScript type from schema
type ItemFormData = z.infer<typeof itemFormSchema>;

interface ItemFormProps {
  /** Called when form is submitted with valid data */
  onSubmit: (data: ItemFormData) => void | Promise<void>;
  /** Initial values for editing existing item */
  defaultValues?: Partial<ItemFormData>;
  /** Whether form submission is in progress */
  isSubmitting?: boolean;
  /** Text for submit button */
  submitLabel?: string;
}

/**
 * Reusable item form with validation.
 *
 * @example
 * ```tsx
 * function CreateItemDialog() {
 *   const createItem = useCreateItem();
 *
 *   return (
 *     <ItemForm
 *       onSubmit={(data) => createItem.mutate(data)}
 *       isSubmitting={createItem.isPending}
 *       submitLabel="Create Item"
 *     />
 *   );
 * }
 * ```
 *
 * @example
 * ```tsx
 * // For editing existing item
 * function EditItemDialog({ item }: { item: ItemPublic }) {
 *   const updateItem = useUpdateItem();
 *
 *   return (
 *     <ItemForm
 *       defaultValues={{
 *         title: item.title,
 *         description: item.description ?? "",
 *       }}
 *       onSubmit={(data) => updateItem.mutate({ id: item.id, ...data })}
 *       isSubmitting={updateItem.isPending}
 *       submitLabel="Save Changes"
 *     />
 *   );
 * }
 * ```
 */
export function ItemForm({
  onSubmit,
  defaultValues = {},
  isSubmitting = false,
  submitLabel = "Submit",
}: ItemFormProps) {
  // Step 3: Initialize form with Zod resolver
  const form = useForm<ItemFormData>({
    resolver: zodResolver(itemFormSchema),
    defaultValues: {
      title: "",
      description: "",
      ...defaultValues,
    },
  });

  // Step 4: Handle form submission
  const handleSubmit = async (data: ItemFormData) => {
    await onSubmit(data);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
        {/* Title Field (Required) */}
        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Title</FormLabel>
              <FormControl>
                <Input
                  placeholder="Enter item title"
                  {...field}
                  disabled={isSubmitting}
                />
              </FormControl>
              <FormDescription>
                A descriptive title for your item (required)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Description Field (Optional) */}
        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Optional description"
                  className="resize-none"
                  {...field}
                  disabled={isSubmitting}
                />
              </FormControl>
              <FormDescription>
                Brief description (max 255 characters)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Submit Button */}
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : submitLabel}
        </Button>
      </form>
    </Form>
  );
}

// === KEY PATTERNS USED ===
//
// 1. Zod Schema Definition
//    - Define validation rules that mirror backend Pydantic
//    - Use descriptive error messages
//    - Handle optional fields with .optional() or .or(z.literal(""))
//
// 2. Type Inference
//    type FormData = z.infer<typeof schema>
//    - Automatically creates TypeScript type from schema
//    - Ensures type safety between validation and submission
//
// 3. React Hook Form Integration
//    const form = useForm<FormData>({
//      resolver: zodResolver(schema),
//      defaultValues: { ... },
//    });
//    - zodResolver bridges Zod and React Hook Form
//    - defaultValues prevents uncontrolled input warnings
//
// 4. FormField Component Pattern
//    <FormField
//      control={form.control}
//      name="fieldName"
//      render={({ field }) => (
//        <FormItem>
//          <FormLabel />
//          <FormControl><Input {...field} /></FormControl>
//          <FormMessage />
//        </FormItem>
//      )}
//    />
//    - Provides error handling and accessibility
//    - FormMessage displays validation errors


// === SCHEMA PATTERNS ===
//
// Required string with length constraints:
// title: z.string().min(1, "Required").max(255)
//
// Optional string:
// description: z.string().optional()
//
// Optional string that can be empty:
// description: z.string().optional().or(z.literal(""))
//
// Email validation:
// email: z.string().email("Invalid email")
//
// Password with constraints:
// password: z.string().min(8, "Min 8 characters").max(128)
//
// Password confirmation:
// const schema = z.object({
//   password: z.string().min(8),
//   confirmPassword: z.string(),
// }).refine((data) => data.password === data.confirmPassword, {
//   message: "Passwords don't match",
//   path: ["confirmPassword"],
// });
//
// Number with bounds:
// age: z.coerce.number().min(0).max(150)
//
// Enum/literal:
// status: z.enum(["active", "inactive"])


// === FORM WITH MUTATION INTEGRATION ===
//
// import { useCreateItem } from "@/hooks/useCreateItem";
//
// function CreateItemPage() {
//   const createItem = useCreateItem();
//   const navigate = useNavigate();
//
//   const handleSubmit = async (data: ItemFormData) => {
//     await createItem.mutateAsync(data);
//     navigate({ to: "/items" });
//   };
//
//   return (
//     <ItemForm
//       onSubmit={handleSubmit}
//       isSubmitting={createItem.isPending}
//       submitLabel="Create Item"
//     />
//   );
// }

export default ItemForm;
