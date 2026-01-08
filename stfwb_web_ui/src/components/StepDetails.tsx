import { Step } from '../types'

interface StepDetailsProps {
  step: Step | null
  onRunStep?: (stepId: string) => void
}

export function StepDetails({ step, onRunStep }: StepDetailsProps) {
  if (!step) {
    return (
      <div className="step-details-panel empty">
        <div className="empty-state">
          <p>Select a step to view details</p>
        </div>
      </div>
    )
  }

  const STEP_TITLES: Record<string, string> = {
    S0: 'Problem Framing',
    S1: 'Requirements Extraction',
    S2: 'Property Identification',
    S3: 'Model Definition',
    S4: 'Assurance Evidence',
    S5: 'Publication',
  }

  const STEP_DESCRIPTIONS: Record<string, string> = {
    S0: 'Understand and frame the problem domain for specification and assurance planning.',
    S1: 'Extract and structure requirements from the specification document.',
    S2: 'Identify key properties and characteristics of requirements.',
    S3: 'Define models and structures to represent the requirements.',
    S4: 'Gather and organize assurance evidence and validation results.',
    S5: 'Publish findings and assurance results.',
  }

  return (
    <div className="step-details-panel">
      <div className="step-header">
        <h2>{step.name}</h2>
        <h3>{STEP_TITLES[step.name]}</h3>
      </div>

      <p className="step-description">{STEP_DESCRIPTIONS[step.name]}</p>

      <section className="section">
        <h4>Status</h4>
        <div className="status-grid">
          <div className="status-item">
            <span className="label">State:</span>
            <span className="value">{step.state.replace(/_/g, ' ')}</span>
          </div>
          {step.duration && (
            <div className="status-item">
              <span className="label">Duration:</span>
              <span className="value">{(step.duration / 1000).toFixed(1)}s</span>
            </div>
          )}
          {step.lastRun && (
            <div className="status-item">
              <span className="label">Last run:</span>
              <span className="value">{new Date(step.lastRun.timestamp).toLocaleTimeString()}</span>
            </div>
          )}
        </div>
      </section>

      <section className="section">
        <h4>Inputs ({step.inputs.length})</h4>
        {step.inputs.length > 0 ? (
          <div className="artifacts-list">
            {step.inputs.map((artifact) => (
              <div key={artifact.id} className="artifact-item">
                <div className="artifact-header">
                  <span className="artifact-id">{artifact.id}</span>
                  <span className={`artifact-status ${artifact.status}`}>{artifact.status}</span>
                </div>
                <div className="artifact-details">
                  <span className="version">v{artifact.version}</span>
                  {artifact.size && <span className="size">{(artifact.size / 1024).toFixed(1)} KB</span>}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="empty-message">No inputs</p>
        )}
      </section>

      <section className="section">
        <h4>Outputs ({step.outputs.length})</h4>
        {step.outputs.length > 0 ? (
          <div className="artifacts-list">
            {step.outputs.map((artifact) => (
              <div key={artifact.id} className="artifact-item">
                <div className="artifact-header">
                  <span className="artifact-id">{artifact.id}</span>
                  <span className={`artifact-status ${artifact.status}`}>{artifact.status}</span>
                </div>
                <div className="artifact-details">
                  <span className="version">v{artifact.version}</span>
                  {artifact.size && <span className="size">{(artifact.size / 1024).toFixed(1)} KB</span>}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="empty-message">No outputs</p>
        )}
      </section>

      {step.error && (
        <section className="section error-section">
          <h4>Error</h4>
          <div className="error-message">{step.error}</div>
        </section>
      )}

      <div className="action-buttons">
        <button className="btn primary" onClick={() => onRunStep?.(step.id)}>
          ▶ Run {step.name}
        </button>
        <button className="btn secondary">View Logs</button>
      </div>
    </div>
  )
}
