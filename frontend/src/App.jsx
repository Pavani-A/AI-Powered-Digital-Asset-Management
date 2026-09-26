import { useState } from 'react'
import './App.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

const FILTERS = [
  { value: 'all', label: 'All assets' },
  { value: 'image', label: 'Images' },
  { value: 'video', label: 'Videos' },
  { value: 'pdf', label: 'PDFs' },
]

function SearchIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="11" cy="11" r="6.5" />
      <path d="m16 16 5 5" />
    </svg>
  )
}

function SparkIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="m12 2 1.7 6.3L20 10l-6.3 1.7L12 18l-1.7-6.3L4 10l6.3-1.7L12 2Z" />
      <path d="m19 16 .8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8L19 16Z" />
    </svg>
  )
}

function FolderIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M3 6.5A2.5 2.5 0 0 1 5.5 4H10l2 2h6.5A2.5 2.5 0 0 1 21 8.5v8A2.5 2.5 0 0 1 18.5 19h-13A2.5 2.5 0 0 1 3 16.5v-10Z" />
    </svg>
  )
}

function GridIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <rect x="4" y="4" width="6" height="6" rx="1" />
      <rect x="14" y="4" width="6" height="6" rx="1" />
      <rect x="4" y="14" width="6" height="6" rx="1" />
      <rect x="14" y="14" width="6" height="6" rx="1" />
    </svg>
  )
}

function ImageIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <rect x="4" y="4" width="16" height="16" rx="2" />
      <circle cx="9" cy="9" r="1.5" />
      <path d="m5.5 17 4.5-4 3.2 2.7 2.2-2 3.1 3.3" />
    </svg>
  )
}

function VideoIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <rect x="3" y="6" width="13" height="12" rx="2" />
      <path d="m16 10 5-3v10l-5-3" />
    </svg>
  )
}

function FileIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M6 3h8l4 4v14H6z" />
      <path d="M14 3v5h5M9 13h6M9 17h6" />
    </svg>
  )
}

function DatabaseIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <ellipse cx="12" cy="5" rx="7" ry="3" />
      <path d="M5 5v7c0 1.7 3.1 3 7 3s7-1.3 7-3V5" />
      <path d="M5 12v7c0 1.7 3.1 3 7 3s7-1.3 7-3v-7" />
    </svg>
  )
}

function CloseIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="m7 7 10 10M17 7 7 17" />
    </svg>
  )
}

function ExternalIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M14 5h5v5M19 5l-8 8" />
      <path d="M18 13v5a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5" />
    </svg>
  )
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes)) {
    return '—'
  }

  if (bytes < 1024) {
    return `${bytes} B`
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }

  if (bytes < 1024 * 1024 * 1024) {
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
}

function formatDuration(seconds) {
  if (!Number.isFinite(seconds)) {
    return null
  }

  const totalSeconds = Math.round(seconds)

  if (totalSeconds < 60) {
    return `${totalSeconds}s`
  }

  const minutes = Math.floor(totalSeconds / 60)
  const remainingSeconds = totalSeconds % 60

  return `${minutes}m ${remainingSeconds}s`
}

function getFileTypeLabel(fileType) {
  switch (fileType) {
    case 'image':
      return 'Image'
    case 'video':
      return 'Video'
    case 'pdf':
      return 'PDF'
    default:
      return fileType || 'Asset'
  }
}

function getFileTypeIcon(fileType) {
  switch (fileType) {
    case 'image':
      return <ImageIcon />
    case 'video':
      return <VideoIcon />
    case 'pdf':
      return <FileIcon />
    default:
      return <FileIcon />
  }
}

function App() {
  const [query, setQuery] = useState('')
  const [activeFilter, setActiveFilter] = useState('all')
  const [results, setResults] = useState([])
  const [searching, setSearching] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)
  const [error, setError] = useState('')
  const [selectedAsset, setSelectedAsset] = useState(null)

  const [indexing, setIndexing] = useState(false)
  const [indexJob, setIndexJob] = useState(null)
  const [showIndexProgress, setShowIndexProgress] = useState(false)
  const [indexMessage, setIndexMessage] = useState('')

  async function searchAssets(searchValue = query) {
    const trimmedQuery = searchValue.trim()

    if (!trimmedQuery) {
      setError('Enter a natural-language description to search.')
      return
    }

    setSearching(true)
    setError('')
    setHasSearched(true)

    try {
      const params = new URLSearchParams({
        q: trimmedQuery,
        limit: '30',
      })

      if (activeFilter !== 'all') {
        params.set('file_type', activeFilter)
      }

      const response = await fetch(
        `${API_BASE_URL}/search?${params.toString()}`,
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Search failed.')
      }

      setResults(data.results || [])
    } catch (searchError) {
      setResults([])
      setError(
        searchError.message ||
          'Unable to connect to the DAM backend.',
      )
    } finally {
      setSearching(false)
    }
  }

  function handleSearchSubmit(event) {
    event.preventDefault()
    searchAssets()
  }

  function clearSearch() {
    setQuery('')
    setResults([])
    setHasSearched(false)
    setError('')
  }

  async function startIndexing() {
    if (indexing) {
      return
    }

    setIndexing(true)
    setShowIndexProgress(true)
    setIndexMessage('Scanning local library...')
    setError('')

    try {
      const scanResponse = await fetch(
        `${API_BASE_URL}/index/scan`,
        {
          method: 'POST',
        },
      )

      const scanData = await scanResponse.json()

      if (!scanResponse.ok) {
        throw new Error(
          scanData.detail || 'Library scan failed.',
        )
      }

      setIndexMessage(
        `Scan complete — ${scanData.total_files} supported files found.`,
      )

      const startResponse = await fetch(
        `${API_BASE_URL}/index/start`,
        {
          method: 'POST',
        },
      )

      const startData = await startResponse.json()

      if (!startResponse.ok) {
        throw new Error(
          startData.detail || 'Unable to start indexing.',
        )
      }

      if (startData.total_files === 0) {
        setIndexJob({
          total_files: 0,
          processed_files: 0,
          successful_files: 0,
          failed_files: 0,
          skipped_files: 0,
          status: 'completed',
          progress_percent: 100,
        })

        setIndexMessage(
          'Your library is already fully indexed.',
        )

        return
      }

      const jobId = startData.job_id

      setIndexJob({
        total_files: startData.total_files,
        processed_files: 0,
        successful_files: 0,
        failed_files: 0,
        skipped_files: 0,
        status: 'running',
        progress_percent: 0,
      })

      setIndexMessage(
        `Indexing ${startData.total_files} files...`,
      )

      while (true) {
        const jobResponse = await fetch(
          `${API_BASE_URL}/index/jobs/${jobId}`,
        )

        const jobData = await jobResponse.json()

        if (!jobResponse.ok) {
          throw new Error(
            jobData.detail || 'Unable to read indexing progress.',
          )
        }

        setIndexJob(jobData)

        if (
          jobData.status === 'completed' ||
          jobData.status === 'failed'
        ) {
          break
        }

        await new Promise((resolve) => {
          window.setTimeout(resolve, 1000)
        })
      }

      const latestJob = await fetch(
        `${API_BASE_URL}/index/jobs/${jobId}`,
      ).then((response) => response.json())

      if (latestJob.status === 'completed') {
        setIndexMessage(
          `Indexing complete — ${latestJob.successful_files} processed, ${latestJob.failed_files} failed, ${latestJob.skipped_files} skipped.`,
        )
      } else {
        setIndexMessage(
          `Indexing stopped with status: ${latestJob.status}.`,
        )
      }

      if (query.trim()) {
        await searchAssets(query)
      }
    } catch (indexError) {
      setError(
        indexError.message ||
          'Unable to start local indexing.',
      )
    } finally {
      setIndexing(false)
    }
  }

  function renderPreview(asset) {
    const fileUrl = `${API_BASE_URL}/assets/${asset.asset_id}/file`

    if (asset.file_type === 'image') {
      return (
        <img
          src={fileUrl}
          alt={asset.filename}
          className="preview-media"
        />
      )
    }

    if (asset.file_type === 'video') {
      return (
        <video
          src={fileUrl}
          controls
          className="preview-media preview-video"
        >
          Your browser does not support video playback.
        </video>
      )
    }

    if (asset.file_type === 'pdf') {
      return (
        <iframe
          src={fileUrl}
          title={asset.filename}
          className="preview-pdf"
        />
      )
    }

    return (
      <div className="preview-fallback">
        <div className="preview-fallback-icon">
          {getFileTypeIcon(asset.file_type)}
        </div>
        <p>Preview is not available for this file type.</p>
      </div>
    )
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <SparkIcon />
          </div>

          <div>
            <div className="brand-name">AI DAM</div>
            <div className="brand-subtitle">
              AI-powered digital asset management
            </div>
          </div>
        </div>

        <div className="local-status">
          <span className="status-dot" />
          <span>Local-first workspace</span>
        </div>
      </header>

      <div className="workspace">
        <aside className="sidebar">
          <div className="sidebar-section">
            <p className="sidebar-label">Workspace</p>

            <button
              type="button"
              className="sidebar-item active"
            >
              <GridIcon />
              <span>Asset library</span>
            </button>

            <button
              type="button"
              className="sidebar-item"
              onClick={startIndexing}
              disabled={indexing}
            >
              <DatabaseIcon />
              <span>
                {indexing ? 'Indexing...' : 'Index library'}
              </span>
            </button>
          </div>

          <div className="sidebar-section">
            <p className="sidebar-label">Filter by type</p>

            {FILTERS.map((filter) => (
              <button
                key={filter.value}
                type="button"
                className={`sidebar-item ${
                  activeFilter === filter.value ? 'selected' : ''
                }`}
                onClick={() => {
                  setActiveFilter(filter.value)

                  if (query.trim()) {
                    setTimeout(() => {
                      searchAssets(query)
                    }, 0)
                  }
                }}
              >
                {filter.value === 'all' ? (
                  <GridIcon />
                ) : filter.value === 'image' ? (
                  <ImageIcon />
                ) : filter.value === 'video' ? (
                  <VideoIcon />
                ) : (
                  <FileIcon />
                )}
                <span>{filter.label}</span>
              </button>
            ))}
          </div>

          <div className="sidebar-bottom">
            <div className="library-card">
              <FolderIcon />
              <div>
                <strong>Local collection</strong>
                <span>Original files stay on this machine.</span>
              </div>
            </div>
          </div>
        </aside>

        <main className="main-content">
          <section className="hero-section">
            <div>
              <p className="eyebrow">INTELLIGENT SEARCH</p>

              <h1>
                Find the right asset
                <br />
                with a simple description.
              </h1>

              <p className="hero-copy">
                Search images, videos and PDFs using natural language.
                Results are ranked by semantic relevance.
              </p>
            </div>

            <button
              type="button"
              className="index-button"
              onClick={startIndexing}
              disabled={indexing}
            >
              <DatabaseIcon />
              {indexing ? 'Indexing library...' : 'Index local library'}
            </button>
          </section>

          <form
            className="search-panel"
            onSubmit={handleSearchSubmit}
          >
            <div className="search-icon">
              <SearchIcon />
            </div>

            <input
              type="text"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder='Try "people outdoors", "financial report", or "red car"...'
              aria-label="Semantic asset search"
            />

            {query && (
              <button
                type="button"
                className="clear-search-button"
                onClick={clearSearch}
                aria-label="Clear search"
                title="Clear search"
              >
                <CloseIcon />
              </button>
            )}

            <button
              type="submit"
              className="search-button"
              disabled={searching}
            >
              {searching ? 'Searching...' : 'Search'}
            </button>
          </form>

          {indexJob && showIndexProgress && (
            <section className="index-progress">
              <button
                type="button"
                className="progress-close"
                onClick={() => setShowIndexProgress(false)}
                aria-label="Close indexing progress"
                title="Close"
              >
                <CloseIcon />
              </button>

              <div className="progress-header">
                <div>
                  <span className="progress-title">
                    Library indexing
                  </span>
                  <span className="progress-detail">
                    {indexJob.processed_files} /{' '}
                    {indexJob.total_files} files processed
                  </span>
                </div>

                <strong>
                  {indexJob.progress_percent}%
                </strong>
              </div>

              <div className="progress-track">
                <div
                  className="progress-fill"
                  style={{
                    width: `${Math.min(
                      100,
                      indexJob.progress_percent,
                    )}%`,
                  }}
                />
              </div>

              <div className="progress-stats">
                <span>
                  <b>{indexJob.successful_files}</b> successful
                </span>
                <span>
                  <b>{indexJob.skipped_files}</b> skipped
                </span>
                <span>
                  <b>{indexJob.failed_files}</b> failed
                </span>
                <span className="progress-status">
                  {indexJob.status}
                </span>
              </div>
            </section>
          )}

          {indexMessage && !indexing && (
            <div className="info-message">
              {indexMessage}
            </div>
          )}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <section className="results-section">
            <div className="results-header">
              <div>
                <p className="eyebrow">SEARCH RESULTS</p>

                <h2>
                  {searching
                    ? 'Searching…'
                    : hasSearched
                      ? `${results.length} matching assets`
                      : 'Your asset library'}
                </h2>
              </div>

              {hasSearched && (
                <div className="result-context">
                  <span>
                    {activeFilter === 'all'
                      ? 'All types'
                      : getFileTypeLabel(activeFilter)}
                  </span>
                  <span>•</span>
                  <span>Ranked by relevance</span>
                </div>
              )}
            </div>

            {!hasSearched ? (
              <div className="empty-state">
                <div className="empty-icon">
                  <SparkIcon />
                </div>

                <h3>Describe what you are looking for</h3>

                <p>
                  Semantic search understands concepts, scenes,
                  activities and document content rather than only
                  filenames.
                </p>

                <div className="suggestion-row">
                  <button
                    type="button"
                    onClick={() => {
                      setQuery('people outdoors')
                      searchAssets('people outdoors')
                    }}
                  >
                    people outdoors
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setQuery('financial report')
                      searchAssets('financial report')
                    }}
                  >
                    financial report
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setQuery('modern architecture')
                      searchAssets('modern architecture')
                    }}
                  >
                    modern architecture
                  </button>
                </div>
              </div>
            ) : results.length === 0 && !searching ? (
              <div className="empty-state">
                <div className="empty-icon">
                  <SearchIcon />
                </div>

                <h3>No matching assets</h3>

                <p>
                  Try a broader description or remove the file-type
                  filter.
                </p>
              </div>
            ) : (
              <div className="results-grid">
                {results.map((asset) => {
                  const fileUrl = `${API_BASE_URL}/assets/${asset.asset_id}/file`
                  const score = Number(asset.score || 0)

                  return (
                    <article
                      key={asset.asset_id}
                      className="asset-card"
                      onClick={() => setSelectedAsset(asset)}
                    >
                      <div className="asset-thumbnail">
                        {asset.file_type === 'image' ? (
                          <img
                            src={fileUrl}
                            alt={asset.filename}
                            loading="lazy"
                          />
                        ) : asset.file_type === 'video' ? (
                          <video
                            src={fileUrl}
                            muted
                            preload="metadata"
                          />
                        ) : (
                          <div className="document-preview">
                            <FileIcon />
                            <span>PDF</span>
                          </div>
                        )}

                        <div className="asset-type">
                          {getFileTypeIcon(asset.file_type)}
                          {getFileTypeLabel(asset.file_type)}
                        </div>

                        <div className="asset-score">
                          {Math.round(score * 100)}%
                        </div>
                      </div>

                      <div className="asset-content">
                        <h3 title={asset.filename}>
                          {asset.filename}
                        </h3>

                        <p className="asset-description">
                          {asset.description ||
                            'No searchable description available.'}
                        </p>

                        <div className="asset-meta">
                          <span>
                            {formatBytes(asset.size_bytes)}
                          </span>

                          {asset.width && asset.height && (
                            <span>
                              {asset.width} × {asset.height}
                            </span>
                          )}

                          {asset.duration_seconds && (
                            <span>
                              {formatDuration(
                                asset.duration_seconds,
                              )}
                            </span>
                          )}

                          {asset.page_count && (
                            <span>
                              {asset.page_count} pages
                            </span>
                          )}
                        </div>
                      </div>
                    </article>
                  )
                })}
              </div>
            )}
          </section>
        </main>
      </div>

      {selectedAsset && (
        <div
          className="modal-backdrop"
          role="presentation"
          onClick={() => setSelectedAsset(null)}
        >
          <div
            className="asset-modal"
            role="dialog"
            aria-modal="true"
            aria-label={selectedAsset.filename}
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <span className="modal-type">
                  {getFileTypeIcon(selectedAsset.file_type)}
                  {getFileTypeLabel(selectedAsset.file_type)}
                </span>

                <h2>{selectedAsset.filename}</h2>
              </div>

              <button
                type="button"
                className="icon-button"
                onClick={() => setSelectedAsset(null)}
                aria-label="Close preview"
              >
                <CloseIcon />
              </button>
            </div>

            <div className="modal-preview">
              {renderPreview(selectedAsset)}
            </div>

            <div className="modal-details">
              <div>
                <span>Relevance</span>
                <strong>
                  {Math.round(
                    Number(selectedAsset.score || 0) * 100,
                  )}
                  %
                </strong>
              </div>

              <div>
                <span>Size</span>
                <strong>
                  {formatBytes(selectedAsset.size_bytes)}
                </strong>
              </div>

              <div>
                <span>Status</span>
                <strong>{selectedAsset.status}</strong>
              </div>
            </div>

            <div className="modal-description">
              <p className="eyebrow">AI SEARCH CONTEXT</p>
              <p>
                {selectedAsset.description ||
                  'No description available.'}
              </p>
            </div>

            <div className="modal-path">
              <span>Original location</span>
              <code>{selectedAsset.original_path}</code>
            </div>

            <div className="modal-actions">
              <a
                href={`${API_BASE_URL}/assets/${selectedAsset.asset_id}/file`}
                target="_blank"
                rel="noreferrer"
                className="open-button"
              >
                <ExternalIcon />
                Open original
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App