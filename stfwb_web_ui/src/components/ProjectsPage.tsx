import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { type ProjectConfig } from './HomePage'

interface ProjectsPageProps {
  projects: ProjectConfig[]
  onStartProject: (config: ProjectConfig) => void
  onBackToLanding: () => void
}

export function ProjectsPage({ projects, onStartProject, onBackToLanding }: ProjectsPageProps) {
  const { user, logout } = useAuth()
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState<ProjectConfig>({
    owner: '',
    repo: '',
    branch: 'main',
    specPath: 'docs/specs/stf-workbench-v0.2.0.md',
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onStartProject(formData)
    setShowForm(false)
  }

  return (
    <div className="home-page">
      <div className="home-container">
        <div className="page-header-bar">
          <button className="header-logo-btn" onClick={onBackToLanding} title="Go home">
            <img src="/stf-logo.png" alt="STF Logo" className="header-logo" />
          </button>
          <button className="header-back-btn" onClick={onBackToLanding} title="Go back">
            ← Back
          </button>
          <h1 className="header-title">Your Projects</h1>
          <div className="header-right">
            {user && user.identities && user.identities.length > 0 ? (
              <>
                <div className="header-user" onClick={onBackToLanding} style={{ cursor: 'pointer' }} title="Go to home">
                  <img
                    src={user.identities[0].avatar_url || undefined}
                    alt={user.identities[0].display || undefined}
                    className="header-user-avatar"
                  />
                  <span className="header-user-name">{user.identities[0].display}</span>
                </div>
                <button className="header-logout-btn" onClick={logout} title="Logout">
                  Logout
                </button>
              </>
            ) : (
              <button className="header-login-btn" onClick={() => {}}>
                Sign In
              </button>
            )}
          </div>
        </div>

        {!showForm ? (
          <div className="home-options">
            <div className="options-grid">
              {/* Create new project card */}
              <button className="option-card start-project" onClick={() => setShowForm(true)}>
                <div className="option-icon">➕</div>
                <div className="option-title">Create New Project</div>
                <div className="option-description">
                  Start a new workbench run from a GitHub repository
                </div>
              </button>

              {/* Existing projects */}
              {projects.map((p, idx) => (
                <button
                  key={`${p.owner}-${p.repo}-${idx}`}
                  className="option-card project-card"
                  onClick={() => onStartProject(p)}
                >
                  <div className="option-icon">📦</div>
                  <div className="option-title">{p.repo}</div>
                  <div className="option-description">
                    <div className="project-owner">{p.owner}</div>
                    <div className="project-meta">
                      <span className="project-branch">📌 {p.branch}</span>
                    </div>
                  </div>
                </button>
              ))}

              {projects.length === 0 && (
                <div className="empty-state">
                  <p>No projects yet.</p>
                  <p>Create a new project to get started.</p>
                </div>
              )}
            </div>

            <div className="home-footer">
              <p className="info">Welcome! Select a project or create a new one to get started.</p>
            </div>
          </div>
        ) : (
          <div className="new-project-form">
            <button className="back-btn" onClick={() => setShowForm(false)}>
              ← Back
            </button>

            <h2>Create New Project</h2>
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
            </div>

            <div className="form-group">
              <label htmlFor="specPath">Specification Path</label>
              <textarea
                id="specPath"
                name="specPath"
                value={formData.specPath}
                onChange={handleInputChange}
                rows={3}
                placeholder="e.g., docs/specs/stf-workbench-v0.2.0.md"
                required
              />
              <span className="help-text">Path to the specification file in the repository</span>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn primary">
                Create Project
              </button>
              <button type="button" className="btn secondary" onClick={() => setShowForm(false)}>
                Cancel
              </button>
            </div>
          </form>
        </div>
        )}
      </div>
    </div>
  )
}
