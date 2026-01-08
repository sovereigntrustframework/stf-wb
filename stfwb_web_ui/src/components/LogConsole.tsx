import { LogEntry } from '../types'

interface LogConsoleProps {
  logs: LogEntry[]
  collapsed?: boolean
  onToggle?: () => void
}

export function LogConsole({ logs, collapsed = false, onToggle }: LogConsoleProps) {
  const getLogIcon = (type: string) => {
    switch (type) {
      case 'error':
        return '✕'
      case 'warning':
        return '⚠'
      case 'info':
        return 'ℹ'
      case 'debug':
        return '◆'
      default:
        return '•'
    }
  }

  const getLogColor = (type: string) => {
    switch (type) {
      case 'error':
        return '#ef4444'
      case 'warning':
        return '#f59e0b'
      case 'info':
        return '#3b82f6'
      case 'debug':
        return '#6b7280'
      default:
        return '#9ca3af'
    }
  }

  const recentLogs = logs.slice(-20) // Show last 20 logs

  return (
    <div className={`log-console ${collapsed ? 'collapsed' : ''}`}>
      <div className="log-header">
        <h4>Log Console ({logs.length})</h4>
        <button className="toggle-btn" onClick={onToggle} title={collapsed ? 'Expand' : 'Collapse'}>
          {collapsed ? '▲' : '▼'}
        </button>
      </div>

      {!collapsed && (
        <div className="log-content">
          {recentLogs.length === 0 ? (
            <div className="empty-logs">No logs yet</div>
          ) : (
            <div className="logs-list">
              {recentLogs.map((log) => (
                <div key={log.id} className={`log-entry log-${log.type}`}>
                  <span className="log-icon" style={{ color: getLogColor(log.type) }}>
                    {getLogIcon(log.type)}
                  </span>
                  <span className="log-time">{new Date(log.timestamp).toLocaleTimeString()}</span>
                  <span className="log-message">{log.message}</span>
                  {log.context?.stepId && <span className="log-context">[{log.context.stepId}]</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
