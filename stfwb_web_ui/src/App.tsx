import { useState, useEffect } from 'react'
import { useRun } from './hooks/useRun'
import { useAuth } from './context/AuthContext'
import { TopBar } from './components/TopBar'
import { MethodologyView } from './components/MethodologyView'
import { StepDetails } from './components/StepDetails'
import { LogConsole } from './components/LogConsole'
import { HomePage, type ProjectConfig } from './components/HomePage'
import './App.css'

function App() {
  const { run, logs, handleSSEEvent, addLog } = useRun()
  const { user } = useAuth()
  const [connected, setConnected] = useState(false)
  const [selectedStep, setSelectedStep] = useState<string | null>('S0')
  const [logCollapsed, setLogCollapsed] = useState(false)
  const [showHome, setShowHome] = useState(true)
  const [currentProject, setCurrentProject] = useState<ProjectConfig | null>(null)

  useEffect(() => {
    // Connect to SSE endpoint
    const eventSource = new EventSource('/api/events')

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
    setCurrentProject(config)
    setShowHome(false)
    addLog({
      timestamp: new Date().toISOString(),
      type: 'info',
      message: `Project started: ${config.owner}/${config.repo} (${config.branch})`,
    })
  }

  const handleBackToHome = () => {
    setShowHome(true)
    setCurrentProject(null)
  }

  if (showHome) {
    return <HomePage onStartProject={handleStartProject} />
  }

  return (
    <div className="app-container">
      <TopBar
        run={run}
        onSync={handleSync}
        onRunStep={handleRunStep}
        onHome={handleBackToHome}
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
