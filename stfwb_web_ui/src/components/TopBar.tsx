import { Run } from '../types'
import { useAuth } from '../context/AuthContext'

interface TopBarProps {
  run: Run
  onSync?: () => void
  onRunStep?: (stepId: string) => void
  onHome?: () => void
  onBackToProjects?: () => void
}

export function TopBar({ run, onSync, onRunStep, onHome, onBackToProjects }: TopBarProps) {
  const { user, logout } = useAuth()
  const getStateColor = (state: string) => {
    switch (state) {
      case 'in_progress':
        return '#3b82f6' // blue
      case 'completed':
        return '#10b981' // green
      case 'failed':
        return '#ef4444' // red
      case 'stale':
        return '#f59e0b' // amber
      default:
        return '#6b7280' // gray
    }
  }

  const getSyncIcon = (status: string) => {
    switch (status) {
      case 'in_sync':
        return '✓'
      case 'ahead':
        return '↑'
      case 'behind':
        return '↓'
      case 'diverged':
        return '⚠'
      default:
        return '?'
    }
  }

  return (
    <div className="top-bar">
      <div className="top-bar-left">
        <button className="logo-home-btn" onClick={onHome} title="Go to home">
          <img src="/stf-logo.png" alt="STF Logo" className="top-bar-logo" />
        </button>
        <button className="back-to-projects-btn" onClick={onBackToProjects} title="Back to projects">
          ← Back to Projects
        </button>

        <div className="run-context">
          <div className="run-label">{run.label}</div>
          <div className="run-state" style={{ color: getStateColor(run.state) }}>
            {run.state}
          </div>
          {run.currentStep && (
            <div className="current-step">
              Step: <strong>{run.currentStep}</strong>
            </div>
          )}
        </div>
      </div>

      <div className="top-bar-right">
        <div className="coverage-badge">
          <span className="label">Coverage</span>
          <span className="value">{run.coverage?.percentage || 0}%</span>
          <span className="detail">
            {run.coverage?.mapped}/{run.coverage?.requirements}
          </span>
        </div>

        {run.validationIssues && (
          <div className="validation-issues">
            {run.validationIssues.errors > 0 && (
              <span className="error-count">
                ⚠ {run.validationIssues.errors} error{run.validationIssues.errors !== 1 ? 's' : ''}
              </span>
            )}
            {run.validationIssues.warnings > 0 && (
              <span className="warning-count">
                ℹ {run.validationIssues.warnings} warning{run.validationIssues.warnings !== 1 ? 's' : ''}
              </span>
            )}
          </div>
        )}

        <div className="sync-status">
          <span className="sync-icon">{getSyncIcon(run.syncStatus)}</span>
          <span className="sync-label">{run.syncStatus}</span>
        </div>

        <button className="action-btn sync-btn" onClick={onSync} title="Sync with remote">
          ⟳ Sync
        </button>

        {run.currentStep && (
          <button
            className="action-btn run-btn"
            onClick={() => onRunStep?.(run.currentStep!)}
            title="Run current step"
          >
            ▶ Run {run.currentStep}
          </button>
        )}

        {run.state === 'running' && (
          <div className="running-indicator">
            <span className="spinner">⧖</span> Running
          </div>
        )}

        {user && (
          <div className="user-section">
            {user.identities && user.identities.length > 0 && (
              <>
                <img
                  src={user.identities[0].avatar_url || ''}
                  alt={user.identities[0].display || user.user_id}
                  className="user-avatar"
                  title={user.identities[0].display || user.user_id}
                />
                <button className="logout-btn" onClick={logout} title="Logout">
                  ↪
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
