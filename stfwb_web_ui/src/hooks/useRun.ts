import { useState, useEffect, useCallback } from 'react'
import { Run, Step, LogEntry, SSEEvent, StepState } from '../types'

// Mock data for MVP
const MOCK_RUN: Run = {
  id: 'run-20260107-001',
  label: 'S0+S1 iteration 3',
  state: 'running',
  currentStep: 'S0',
  project: {
    id: 'proj-demo',
    name: 'stf-workbench',
    owner: 'sovereign-trust',
    repo: 'stf-wb',
    branch: 'main',
  },
  steps: {
    S0: {
      id: 'S0',
      name: 'S0',
      title: 'Problem Framing',
      state: 'in_progress',
      inputs: [
        {
          id: 'spec',
          version: 'v0.1.3',
          producedBy: 'external',
          status: 'fresh',
        },
      ],
      outputs: [
        {
          id: 'artifacts/S0/snapshot.json',
          version: '8a3f2b',
          producedBy: 'S0',
          status: 'fresh',
          size: 2048,
        },
      ],
      duration: 5000,
      lastRun: {
        timestamp: '2026-01-07T17:30:00Z',
        user: 'alex',
        status: 'completed',
      },
    },
    S1: {
      id: 'S1',
      name: 'S1',
      title: 'Requirements Extraction',
      state: 'not_started',
      inputs: [
        {
          id: 'artifacts/S0/snapshot.json',
          version: '8a3f2b',
          producedBy: 'S0',
          status: 'fresh',
        },
      ],
      outputs: [
        {
          id: 'artifacts/S1/requirements.json',
          version: 'pending',
          producedBy: 'S1',
          status: 'stale',
        },
      ],
    },
    S2: {
      id: 'S2',
      name: 'S2',
      title: 'Property Identification',
      state: 'not_started',
      inputs: [],
      outputs: [],
    },
    S3: {
      id: 'S3',
      name: 'S3',
      title: 'Model Definition',
      state: 'not_started',
      inputs: [],
      outputs: [],
    },
    S4: {
      id: 'S4',
      name: 'S4',
      title: 'Assurance Evidence',
      state: 'not_started',
      inputs: [],
      outputs: [],
    },
    S5: {
      id: 'S5',
      name: 'S5',
      title: 'Publication',
      state: 'not_started',
      inputs: [],
      outputs: [],
    },
  },
  createdAt: '2026-01-07T16:00:00Z',
  updatedAt: '2026-01-07T17:30:00Z',
  syncStatus: 'in_sync',
  lastSyncTime: '2026-01-07T17:29:00Z',
  coverage: {
    requirements: 116,
    mapped: 89,
    percentage: 77,
  },
  validationIssues: {
    errors: 0,
    warnings: 3,
  },
}

export function useRun() {
  const [run, setRun] = useState<Run>(MOCK_RUN)
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      id: '1',
      timestamp: '2026-01-07T17:30:00Z',
      type: 'info',
      message: 'Run started',
      context: { runId: run.id },
    },
    {
      id: '2',
      timestamp: '2026-01-07T17:30:05Z',
      type: 'info',
      message: 'Step S0 started',
      context: { runId: run.id, stepId: 'S0' },
    },
    {
      id: '3',
      timestamp: '2026-01-07T17:30:10Z',
      type: 'info',
      message: 'Extracted 116 requirements from specification',
      context: { runId: run.id, stepId: 'S0' },
    },
  ])

  const updateStepState = useCallback((stepId: string, state: StepState) => {
    setRun((prev) => ({
      ...prev,
      steps: {
        ...prev.steps,
        [stepId]: {
          ...prev.steps[stepId],
          state,
        },
      },
    }))
  }, [])

  const updateRunState = useCallback((state: string) => {
    setRun((prev) => ({
      ...prev,
      state: state as any,
    }))
  }, [])

  const addLog = useCallback((entry: Omit<LogEntry, 'id'>) => {
    setLogs((prev) => [
      ...prev,
      {
        ...entry,
        id: Date.now().toString(),
      },
    ])
  }, [])

  const handleSSEEvent = useCallback(
    (event: SSEEvent) => {
      const { type, payload } = event

      switch (type) {
        case 'step.started':
          updateStepState(payload.step as string, 'in_progress')
          addLog({
            timestamp: new Date().toISOString(),
            type: 'info',
            message: `Step ${payload.step} started`,
            context: { stepId: payload.step as string, runId: run.id },
            relatedEvent: event,
          })
          break

        case 'step.completed':
          updateStepState(payload.step as string, 'completed')
          addLog({
            timestamp: new Date().toISOString(),
            type: 'info',
            message: `Step ${payload.step} completed`,
            context: { stepId: payload.step as string, runId: run.id },
            relatedEvent: event,
          })
          break

        case 'run.started':
          updateRunState('running')
          addLog({
            timestamp: new Date().toISOString(),
            type: 'info',
            message: 'Run started',
            context: { runId: run.id },
            relatedEvent: event,
          })
          break

        case 'run.completed':
          updateRunState('published')
          addLog({
            timestamp: new Date().toISOString(),
            type: 'info',
            message: 'Run completed',
            context: { runId: run.id },
            relatedEvent: event,
          })
          break

        case 'heartbeat':
          // Silently ignore heartbeats
          break

        default:
          addLog({
            timestamp: new Date().toISOString(),
            type: 'debug',
            message: `Event: ${type}`,
            relatedEvent: event,
          })
      }
    },
    [run.id, updateStepState, updateRunState, addLog]
  )

  return {
    run,
    logs,
    updateStepState,
    updateRunState,
    addLog,
    handleSSEEvent,
  }
}
