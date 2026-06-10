"use client"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

const subscriptions = [
  { id: "1", user: "John Doe", plan: "Premium", status: "active", amount: "$3/mo", period: "2024-01-15 - 2024-02-15" },
  { id: "2", user: "Jane Smith", plan: "Business", status: "active", amount: "$10/mo", period: "2024-02-20 - 2024-03-20" },
  { id: "3", user: "Bob Wilson", plan: "Free", status: "active", amount: "$0", period: "N/A" },
  { id: "4", user: "Alice Brown", plan: "Premium", status: "cancelled", amount: "$3/mo", period: "2024-03-01 - 2024-04-01" },
]

export default function AdminSubscriptionsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Subscriptions</h1>
        <p className="text-muted-foreground">Manage user subscriptions.</p>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>User</TableHead>
              <TableHead>Plan</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Period</TableHead>
              <TableHead className="w-12"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {subscriptions.map((sub) => (
              <TableRow key={sub.id}>
                <TableCell className="font-medium">{sub.user}</TableCell>
                <TableCell>{sub.plan}</TableCell>
                <TableCell>
                  <Badge variant={sub.status === "active" ? "success" : "destructive"}>
                    {sub.status}
                  </Badge>
                </TableCell>
                <TableCell>{sub.amount}</TableCell>
                <TableCell className="text-sm text-muted-foreground">{sub.period}</TableCell>
                <TableCell>
                  <Button variant="ghost" size="sm">View</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
