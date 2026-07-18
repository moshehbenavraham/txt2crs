import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { Suspense } from "react"

import { type UserPublic, UsersService } from "@/client"
import AddUser from "@/components/Admin/AddUser"
import { columns, type UserTableData } from "@/components/Admin/columns"
import { UserRecordCard } from "@/components/Admin/UserRecordCard"
import { DataTable } from "@/components/Common/DataTable"
import { PageHeader } from "@/components/Common/PageHeader"
import PendingUsers from "@/components/Pending/PendingUsers"
import useAuth from "@/hooks/useAuth"
import { CURRENT_USER_QUERY_KEY } from "@/lib/session"

function getUsersQueryOptions() {
  return {
    queryFn: () => UsersService.readUsers({ query: { skip: 0, limit: 100 } }),
    queryKey: ["users"],
  }
}

export const Route = createFileRoute("/_layout/admin")({
  component: Admin,
  beforeLoad: async ({ context }) => {
    const currentUser = await context.queryClient.ensureQueryData({
      queryKey: CURRENT_USER_QUERY_KEY,
      queryFn: () => UsersService.readUserMe(),
    })

    if (!currentUser.is_superuser) {
      throw redirect({ to: "/forbidden" })
    }
  },
  head: () => ({
    meta: [
      {
        title: "Admin - AIwithApex.com",
      },
    ],
  }),
})

function UsersTableContent() {
  const { user: currentUser } = useAuth()
  const { data: users } = useSuspenseQuery(getUsersQueryOptions())

  const tableData: UserTableData[] = users.data.map((user: UserPublic) => ({
    ...user,
    isCurrentUser: currentUser?.id === user.id,
  }))

  return (
    <DataTable
      columns={columns}
      data={tableData}
      renderMobileRow={(user) => <UserRecordCard user={user} />}
    />
  )
}

function UsersTable() {
  return (
    <Suspense fallback={<PendingUsers />}>
      <UsersTableContent />
    </Suspense>
  )
}

function Admin() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Administration"
        title="Users"
        description="Manage user accounts and permissions."
        actions={<AddUser />}
      />
      <UsersTable />
    </div>
  )
}
