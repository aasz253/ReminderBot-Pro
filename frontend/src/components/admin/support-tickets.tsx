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
import type { SupportTicket } from "@/types"

interface SupportTicketsProps {
  tickets: SupportTicket[]
  onView: (id: string) => void
  onUpdateStatus: (id: string, status: string) => void
}

const statusColors: Record<string, "default" | "warning" | "success" | "outline"> = {
  open: "warning",
  in_progress: "default",
  resolved: "success",
  closed: "outline",
}

export function SupportTickets({ tickets, onView, onUpdateStatus }: SupportTicketsProps) {
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Subject</TableHead>
            <TableHead>User</TableHead>
            <TableHead>Priority</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Created</TableHead>
            <TableHead className="w-12"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {tickets.map((ticket) => (
            <TableRow key={ticket.id} className="cursor-pointer" onClick={() => onView(ticket.id)}>
              <TableCell className="font-medium">{ticket.subject}</TableCell>
              <TableCell className="text-sm">{ticket.user?.name || "Unknown"}</TableCell>
              <TableCell>
                <Badge variant={ticket.priority === "urgent" ? "destructive" : ticket.priority === "high" ? "warning" : "outline"}>
                  {ticket.priority}
                </Badge>
              </TableCell>
              <TableCell>
                <Badge variant={statusColors[ticket.status] || "outline"}>
                  {ticket.status.replace("_", " ")}
                </Badge>
              </TableCell>
              <TableCell className="text-sm text-muted-foreground">
                {new Date(ticket.created_at).toLocaleDateString()}
              </TableCell>
              <TableCell>
                <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); onUpdateStatus(ticket.id, "resolved") }}>
                  Resolve
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
