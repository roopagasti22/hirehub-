/**
 * HireHub — Main JavaScript
 * Provides: toast alerts, AJAX helpers, UI enhancements.
 */

// ── Toast notification helper ────────────────────────────────────────
function showAlert(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const alert = document.createElement('div');
  alert.className = `alert alert-${type} alert-dismissible fade show shadow`;
  alert.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  container.appendChild(alert);

  // Auto-dismiss after 4 seconds
  setTimeout(() => {
    alert.classList.remove('show');
    setTimeout(() => alert.remove(), 300);
  }, 4000);
}

// ── CSRF helper (reads from cookie if present) ───────────────────────
function getCsrfToken() {
  const match = document.cookie.match(/csrf_token=([^;]+)/);
  return match ? match[1] : '';
}

// ── Generic Fetch wrapper ────────────────────────────────────────────
async function apiRequest(url, method = 'GET', body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin',
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  return res.json();
}

// ── Save / unsave job (used on job list page) ────────────────────────
async function toggleSaveJob(jobId, saved) {
  const endpoint = saved
    ? `/api/candidates/me/unsave-job`
    : `/api/candidates/me/save-job`;
  const data = await apiRequest(endpoint, 'POST', { job_id: jobId });
  if (data.success) {
    showAlert(saved ? 'Job removed from saved.' : 'Job saved!', 'success');
    setTimeout(() => location.reload(), 1000);
  } else {
    showAlert(data.message || 'Error.', 'danger');
  }
}

// ── Notification badge update via polling ────────────────────────────
function initNotificationPolling(intervalMs = 60000) {
  async function update() {
    try {
      const data = await apiRequest('/api/analytics/candidate');
      // Badge is handled by context processor — no client-side update needed.
    } catch (_) {}
  }
  setInterval(update, intervalMs);
}

// ── Auto-dismiss flash alerts ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Auto dismiss flash messages after 5 seconds
  const flashAlerts = document.querySelectorAll('.alert.alert-dismissible.fade.show');
  flashAlerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });

  // Enable Bootstrap tooltips
  const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltips.forEach(el => new bootstrap.Tooltip(el));

  // Highlight active nav link
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') && currentPath.startsWith(link.getAttribute('href')) && link.getAttribute('href') !== '/') {
      link.classList.add('active');
    }
  });
});
