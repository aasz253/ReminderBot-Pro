"use client"

import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { Trash2, CheckCircle, PauseCircle, Play } from "lucide-react"

interface BulkActionsProps {
  selectedCount: number
  totalCount: number
  onSelectAll: () => void
  onDeselectAll: () => void
  onBulkComplete: () => void
  onBulkDelete: () => void
  onBulkPause: () => void
  onBulkResume: () => void
}

export function BulkActions({
  selectedCount,
  totalCount,
  onSelectAll,
  onDeselectAll,
  onBulkComplete,
  onBulkDelete,
  onBulkPause,
  onBulkResume,
}: BulkActionsProps) {
  if (selectedCount === 0) return null

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 animate-fade-in">
      <Checkbox
        checked={selectedCount === totalCount}
        onCheckedChange={(checked) => checked ? onSelectAll() : onDeselectAll()}
      />
      <span className="text-sm text-muted-foreground">
        {selectedCount} selected
      </span>
      <div className="flex items-center gap-1 ml-auto">
        <Button variant="ghost" size="sm" onClick={onBulkComplete}>
          <CheckCircle className="h-4 w-4 mr-1" /> Complete
        </Button>
        <Button variant="ghost" size="sm" onClick={onBulkPause}>
          <PauseCircle className="h-4 w-4 mr-1" /> Pause
        </Button>
        <Button variant="ghost" size="sm" onClick={onBulkResume}>
          <Play className="h-4 w-4 mr-1" /> Resume
        </Button>
        <Button variant="ghost" size="sm" onClick={onBulkDelete} className="text-red-500 hover:text-red-600">
          <Trash2 className="h-4 w-4 mr-1" /> Delete
        </Button>
      </div>
    </div>
  )
}
