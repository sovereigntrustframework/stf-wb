import { Run } from '../types'

interface MethodologyViewProps {
  run: Run
  selectedStep: string | null
  onSelectStep: (stepId: string) => void
}

const STEP_ORDER = ['S0', 'S1', 'S2', 'S3', 'S4', 'S5']

const STEP_TITLES: Record<string, string> = {
  S0: 'Problem Framing',
  S1: 'Requirements Extraction',
  S2: 'Property Identification',
  S3: 'Model Definition',
  S4: 'Assurance Evidence',
  S5: 'Publication',
}

export function MethodologyView({ run, selectedStep, onSelectStep }: MethodologyViewProps) {
  const getStateColor = (state: string) => {
    switch (state) {
      case 'in_progress':
        return '#3b82f6'
      case 'completed':
        return '#10b981'
      case 'failed':
        return '#ef4444'
      case 'stale':
        return '#f59e0b'
      default:
        return '#d1d5db'
    }
  }

  const getStateLabel = (state: string) => {
    return state.replace(/_/g, ' ')
  }

  return (
    <div className="methodology-view">
      <h3>Methodology Steps</h3>

      <div className="steps-list">
        {STEP_ORDER.map((stepId) => {
          const step = run.steps[stepId]
          if (!step) return null

          return (
            <div
              key={stepId}
              className={`step-node ${selectedStep === stepId ? 'selected' : ''}`}
              onClick={() => onSelectStep(stepId)}
            >
              <div className="step-header">
                <span className="step-id">{stepId}</span>
                <div className="step-info">
                  <div className="step-title">{STEP_TITLES[stepId]}</div>
                  <div className="step-state-badge" style={{ borderColor: getStateColor(step.state) }}>
                    <span className="state-dot" style={{ backgroundColor: getStateColor(step.state) }}></span>
                    <span className="state-label">{getStateLabel(step.state)}</span>
                  </div>
                </div>
              </div>

              <div className="step-details">
                <div className="inputs-outputs">
                  {step.inputs.length > 0 && (
                    <span className="io-badge inputs" title={`${step.inputs.length} input(s)`}>
                      ↓ {step.inputs.length}
                    </span>
                  )}
                  {step.outputs.length > 0 && (
                    <span className="io-badge outputs" title={`${step.outputs.length} output(s)`}>
                      ↑ {step.outputs.length}
                    </span>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
