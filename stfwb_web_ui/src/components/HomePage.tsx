import { useState } from 'react'
import { useAuth } from '../context/AuthContext'

interface HomePageProps {
  onStartProject: (config: ProjectConfig) => void
}

export interface ProjectConfig {
  owner: string
  repo: string
  branch: string
  specPath: string
}

export function HomePage({ onStartProject }: HomePageProps) {
  const { user, login } = useAuth()
  const [showNewProject, setShowNewProject] = useState(false)
  const [formData, setFormData] = useState<ProjectConfig>({
    owner: 'sovereign-trust',
    repo: 'stf-wb',
    branch: 'main',
    specPath: 'docs/specs/stf-workbench-v0.2.0.md',
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onStartProject(formData)
  }

  return (
    <div className="home-page">
      <div className="home-container">
        <div className="home-header">
          <div className="logo-section">
            <h1>STF-Workbench</h1>
            <p className="tagline">Specification & Assurance Methodology Workbench</p>
          </div>
        </div>

        {!showNewProject ? (
          <div className="home-options">
            {user && user.identities && user.identities.length > 0 && (
              <div className="user-banner">
                <img src={user.identities[0].avatar_url || ''} alt={user.identities[0].display} className="user-avatar" />
                <div className="user-info">
                  <div className="user-name">{user.identities[0].display}</div>
                  <div className="user-login">GitHub ({user.user_id})</div>
                </div>
              </div>
            )}
            <div className="options-grid">
              <button className="option-card start-project" onClick={() => setShowNewProject(true)}>
                <div className="option-icon">📋</div>
                <div className="option-title">Start New Project</div>
                <div className="option-description">
                  Create a new workbench run from a GitHub repository and specification
                </div>
              </button>

              {!user && (
                <button className="option-card login" onClick={login}>
                  <div className="option-icon">🔐</div>
                  <div className="option-title">Sign In with GitHub</div>
                  <div className="option-description">
                    Authenticate with your GitHub account to access private repositories
                  </div>
                </button>
              )}

              <button className="option-card recent" disabled>
                <div className="option-icon">⏱️</div>
                <div className="option-title">Recent Projects</div>
                <div className="option-description">
                  Load a recent project (coming soon)
                </div>
              </button>

              <button className="option-card help" disabled>
                <div className="option-icon">❓</div>
                <div className="option-title">Documentation</div>
                <div className="option-description">
                  Learn how to use STF-Workbench (coming soon)
                </div>
              </button>
            </div>

            <div className="home-footer">
              <p className="version">STF-Workbench v0.1.0 • Phase 1 MVP</p>
              <p className="info">
                For issues and feedback:{' '}
                <a href="https://github.com/sovereign-trust/stf-wb/issues" target="_blank" rel="noopener noreferrer">
                  GitHub Issues
                </a>
              </p>
            </div>
          </div>
        ) : (
          <div className="new-project-form">
            <button className="back-btn" onClick={() => setShowNewProject(false)}>
              ← Back
            </button>

            <h2>Start New Project</h2>
            <p className="form-description">
              Configure your project source and specification file to begin a new workbench run.
            </p>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="owner">Repository Owner</label>
                <input
                  type="text"
                  id="owner"
                  name="owner"
                  value={formData.owner}
                  onChange={handleInputChange}
                  placeholder="e.g., sovereign-trust"
                  required
                />
                <span className="help-text">GitHub user or organization name</span>
              </div>

              <div className="form-group">
                <label htmlFor="repo">Repository Name</label>
                <input
                  type="text"
                  id="repo"
                  name="repo"
                  value={formData.repo}
                  onChange={handleInputChange}
                  placeholder="e.g., stf-wb"
                  required
                />
                <span className="help-text">Repository name (without .git)</span>
              </div>

              <div className="form-group">
                <label htmlFor="branch">Branch</label>
                <input
                  type="text"
                  id="branch"
                  name="branch"
                  value={formData.branch}
                  onChange={handleInputChange}
                  placeholder="e.g., main"
                  required
                />
                <span className="help-text">Git branch to work from</span>
              </div>

              <div className="form-group">
                <label htmlFor="specPath">Specification Path</label>
                <textarea
                  id="specPath"
                  name="specPath"
                  value={formData.specPath}
                  onChange={handleInputChange}
                  placeholder="e.g., docs/specs/stf-workbench-v0.2.0.md"
                  rows={3}
                  required
                />
                <span className="help-text">Path to the specification file in the repository</span>
              </div>

              <div className="form-actions">
                <button type="submit" className="btn primary">
                  Create Project
                </button>
                <button type="button" className="btn secondary" onClick={() => setShowNewProject(false)}>
                  Cancel
                </button>
              </div>

              <div className="form-example">
                <h4>Example Configuration:</h4>
                <ul>
                  <li>Owner: <code>sovereign-trust</code></li>
                  <li>Repo: <code>stf-wb</code></li>
                  <li>Branch: <code>main</code></li>
                  <li>Spec Path: <code>docs/specs/stf-workbench-v0.2.0.md</code></li>
                </ul>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  )
}
