import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

const PendingUsers = () => (
  <>
    <ul className="flex flex-col gap-3 md:hidden" aria-hidden="true">
      {Array.from({ length: 3 }).map((_, index) => (
        <li
          key={index}
          className="flex flex-col gap-3 rounded-xl border border-border bg-surface-1 p-4"
        >
          <Skeleton className="h-4 w-40" />
          <Skeleton className="h-4 w-52" />
          <Skeleton className="h-5 w-20 rounded-full" />
        </li>
      ))}
    </ul>
    <div className="hidden md:block">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Full Name</TableHead>
            <TableHead>Email</TableHead>
            <TableHead>Role</TableHead>
            <TableHead>Status</TableHead>
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
                <Skeleton className="h-4 w-40" />
              </TableCell>
              <TableCell>
                <Skeleton className="h-5 w-20 rounded-full" />
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <Skeleton className="size-2 rounded-full" />
                  <Skeleton className="h-4 w-12" />
                </div>
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

export default PendingUsers
