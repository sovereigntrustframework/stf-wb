/**
 * Shared types for STF-Workbench UI
 */

export type StepState = 'not_started' | 'in_progress' | 'completed' | 'stale' | 'failed'
export type RunState = 'created' | 'running' | 'blocked' | 'failed' | 'published'
export type SyncStatus = 'in_sync' | 'ahead' | 'behind' | 'diverged'

export interface Artifact {
  id: string
  version: string
  producedBy: string // step name
  status: 'fresh' | 'stale'
  size?: number
}

export interface Step {
  id: string
  name: string // S0, S1, etc.
  title: string // "Problem Framing", etc.
  state: StepState
  inputs: Artifact[]
  outputs: Artifact[]
  duration?: number // milliseconds
  error?: string
  lastRun?: {
    timestamp: string
    user?: string
    status: StepState
  }
}

export interface Run {
  id: string
  label: string
  state: RunState
  currentStep: string | null
  project: {
    id: string
    name: string
    owner: string
    repo: string
    branch: string
  }
  steps: Record<string, Step>
  createdAt: string
  updatedAt: string
  syncStatus: SyncStatus
  lastSyncTime?: string
  coverage?: {
    requirements: number
    mapped: number
    percentage: number
  }
  validationIssues?: {
    errors: number
    warnings: number
  }
}

export interface LogEntry {
  id: string
  timestamp: string
  type: 'info' | 'warning' | 'error' | 'debug'
  message: string
  context?: {
    runId?: string
    stepId?: string
    artifactId?: string
  }
  relatedEvent?: {
    type: string
    payload: Record<string, unknown>
  }
}

export interface SSEEvent {
  type: string
  payload: Record<string, unknown>
}
