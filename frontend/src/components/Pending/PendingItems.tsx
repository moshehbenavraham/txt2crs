import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

const PendingItems = () => (
  <>
    <ul className="flex flex-col gap-3 md:hidden" aria-hidden="true">
      {Array.from({ length: 3 }).map((_, index) => (
        <li
          key={index}
          className="flex flex-col gap-3 rounded-xl border border-border bg-surface-1 p-4"
        >
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-16" />
          <Skeleton className="h-4 w-1/2" />
        </li>
      ))}
    </ul>
    <div className="hidden md:block">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Title</TableHead>
            <TableHead>Description</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Source</TableHead>
            <TableHead>ID</TableHead>
            <TableHead>
              <span className="sr-only">Actions</span>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {Array.from({ length: 5 }).map((_, index) => (
            <TableRow key={index}>
              <TableCell>
                <Skeleton className="h-4 w-32" />
              </TableCell>
              <TableCell>
                <Skeleton className="h-4 w-48" />
              </TableCell>
              <TableCell>
                <Skeleton className="h-4 w-16" />
              </TableCell>
              <TableCell>
                <Skeleton className="h-4 w-32" />
              </TableCell>
              <TableCell>
                <Skeleton className="h-4 w-56 font-mono" />
              </TableCell>
              <TableCell>
                <div className="flex justify-end">
                  <Skeleton className="size-8 rounded-md" />
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  </>
)

export default PendingItems
