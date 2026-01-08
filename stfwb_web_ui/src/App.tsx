import { useState, useEffect, useRef } from 'react'
import { useRun } from './hooks/useRun'
import { useAuth } from './context/AuthContext'
import { TopBar } from './components/TopBar'
import { MethodologyView } from './components/MethodologyView'
import { StepDetails } from './components/StepDetails'
import { LogConsole } from './components/LogConsole'
import { HomePage, type ProjectConfig } from './components/HomePage'
import { ProjectsPage } from './components/ProjectsPage'
import './App.css'

function App() {
  const { run, logs, handleSSEEvent, addLog } = useRun()
  const { user } = useAuth()
  const [connected, setConnected] = useState(false)
  const [selectedStep, setSelectedStep] = useState<string | null>('S0')
  const [logCollapsed, setLogCollapsed] = useState(false)
  const [view, setView] = useState<'landing' | 'projects' | 'workbench'>('landing')
  const [projects, setProjects] = useState<ProjectConfig[]>([
    {
      owner: 'sovereign-trust',
      repo: 'stf-wb',
      branch: 'main',
      specPath: 'docs/specs/stf-workbench-v0.2.0.md',
    },
    {
      owner: 'example-org',
      repo: 'trust-runbook',
      branch: 'main',
      specPath: 'specs/trust-runbook.md',
    },
  ])
  const prevUserRef = useRef<boolean | null>(null)

  useEffect(() => {
    // Connect to SSE endpoint
    const eventSource = new EventSource('http://localhost:8000/events')

    eventSource.onopen = () => {
      console.log('SSE connection opened')
      setConnected(true)
      addLog({
        timestamp: new Date().toISOString(),
        type: 'info',
        message: 'Connected to backend',
      })
    }

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('Received event:', data)
        handleSSEEvent(data)
      } catch (err) {
        console.error('Error parsing event:', err)
      }
    }

    eventSource.onerror = (err) => {
      console.error('SSE error:', err)
      setConnected(false)
      addLog({
        timestamp: new Date().toISOString(),
        type: 'error',
        message: 'Connection lost',
      })
    }

    return () => {
      eventSource.close()
    }
  }, [handleSSEEvent, addLog])

  // Manage view transitions based on auth state
  useEffect(() => {
    const isCurrentlyAuthenticated = user !== null
    const wasAuthenticated = prevUserRef.current

    // Only auto-redirect on auth state changes, not on every render
    if (wasAuthenticated === null) {
      // Initial load - if user is logged in, go to projects
      if (isCurrentlyAuthenticated) {
        setView('projects')
      }
    } else if (wasAuthenticated !== isCurrentlyAuthenticated) {
      // Auth state changed
      if (isCurrentlyAuthenticated) {
        // User just logged in - redirect to projects
        setView('projects')
      } else {
        // User just logged out - redirect to landing
        setView('landing')
      }
    }

    // Update the ref
    prevUserRef.current = isCurrentlyAuthenticated
  }, [user])

  const handleSync = async () => {
    addLog({
      timestamp: new Date().toISOString(),
      type: 'info',
      message: 'Syncing with remote...',
    })
    // Mock sync delay
    await new Promise((resolve) => setTimeout(resolve, 1000))
    addLog({
      timestamp: new Date().toISOString(),
      type: 'info',
      message: 'Sync complete',
    })
  }

  const handleRunStep = async (stepId: string) => {
    addLog({
      timestamp: new Date().toISOString(),
      type: 'info',
      message: `Starting step ${stepId}...`,
      context: { stepId },
    })
    // Mock step execution
    await new Promise((resolve) => setTimeout(resolve, 2000))
    addLog({
      timestamp: new Date().toISOString(),
      type: 'info',
      message: `Step ${stepId} completed`,
      context: { stepId },
    })
  }

  const currentStep = selectedStep ? run.steps[selectedStep] : null

  const handleStartProject = (config: ProjectConfig) => {
    setView('workbench')
    // Only add project if it doesn't already exist
    setProjects((prev) => {
      const exists = prev.some((p) => p.owner === config.owner && p.repo === config.repo)
      return exists ? prev : [...prev, config]
    })
    addLog({
      timestamp: new Date().toISOString(),
      type: 'info',
      message: `Project started: ${config.owner}/${config.repo} (${config.branch})`,
    })
  }

  const handleBackToHome = () => {
    setView('landing')
  }

  const handleBackToProjects = () => {
    setView('projects')
  }

  // Switch views based on auth state and current selection
  if (view === 'landing') {
    return <HomePage onStartProject={handleStartProject} onGoToProjects={user ? () => setView('projects') : undefined} allowProjectCreation={!!user} />
  }

  if (view === 'projects') {
    return (
      <ProjectsPage
        projects={projects}
        onStartProject={handleStartProject}
        onBackToLanding={() => setView('landing')}
      />
    )
  }

  return (
    <div className="app-container">
      <TopBar
        run={run}
        onSync={handleSync}
        onRunStep={handleRunStep}
        onHome={handleBackToHome}
        onBackToProjects={handleBackToProjects}
      />

      <div className="main-layout">
        <div className="left-panel">
          <MethodologyView
            run={run}
            selectedStep={selectedStep}
            onSelectStep={setSelectedStep}
          />
        </div>

        <div className="central-panel">
          <StepDetails
            step={currentStep}
            onRunStep={handleRunStep}
          />
        </div>
      </div>

      <LogConsole
        logs={logs}
        collapsed={logCollapsed}
        onToggle={() => setLogCollapsed(!logCollapsed)}
      />

      {/* Connection indicator */}
      <div className={`connection-indicator ${connected ? 'connected' : 'disconnected'}`}>
        <span className="indicator-dot"></span>
        {connected ? 'Connected' : 'Disconnected'}
      </div>
    </div>
  )
}

export default App
