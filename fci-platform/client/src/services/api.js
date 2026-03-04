const BASE_URL = '/api';

function authHeaders(token) {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };
}

async function handleResponse(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export async function login(username) {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username }),
  });
  return handleResponse(res);
}

export async function getMe(token) {
  const res = await fetch(`${BASE_URL}/auth/me`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ---------------------------------------------------------------------------
// Cases
// ---------------------------------------------------------------------------

export async function getCases(token) {
  const res = await fetch(`${BASE_URL}/cases`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function getCase(token, caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ---------------------------------------------------------------------------
// Conversations
// ---------------------------------------------------------------------------

export async function createConversation(token, caseId = null, mode = 'case') {
  const body = { mode };
  if (caseId) body.case_id = caseId;
  const res = await fetch(`${BASE_URL}/conversations`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

export async function sendMessage(token, conversationId, content, images = [], stream = false, initialAssessment = false) {
  const body = { content, stream };
  if (images.length > 0) {
    body.images = images;
  }
  if (initialAssessment) {
    body.initial_assessment = true;
  }

  const res = await fetch(`${BASE_URL}/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify(body),
  });

  // For streaming, return the raw Response so the caller can read the SSE stream
  if (stream) {
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Request failed: ${res.status}`);
    }
    return res;
  }

  return handleResponse(res);
}

export async function getConversationHistory(token, conversationId) {
  const res = await fetch(`${BASE_URL}/conversations/${conversationId}/history`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function getConversations(token, mode = null) {
  const params = mode ? `?mode=${mode}` : '';
  const res = await fetch(`${BASE_URL}/conversations${params}`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function deleteConversation(token, conversationId) {
  const res = await fetch(`${BASE_URL}/conversations/${conversationId}`, {
    method: 'DELETE',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ---------------------------------------------------------------------------
// PDF Export
// ---------------------------------------------------------------------------

export async function exportPdf(token, conversationId) {
  const res = await fetch(`${BASE_URL}/conversations/${conversationId}/export/pdf`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `PDF export failed: ${res.status}`);
  }
  // Extract filename from Content-Disposition header
  const disposition = res.headers.get('Content-Disposition') || '';
  const filenameMatch = disposition.match(/filename="?([^"]+)"?/);
  const filename = filenameMatch ? filenameMatch[1] : 'transcript.pdf';

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

// ---------------------------------------------------------------------------
// Images
// ---------------------------------------------------------------------------

export function imageUrl(conversationId, imageId) {
  return `${BASE_URL}/conversations/${conversationId}/images/${imageId}`;
}

// ---------------------------------------------------------------------------
// Admin (demo only)
// ---------------------------------------------------------------------------

export async function reseedDatabase(token) {
  const res = await fetch(`${BASE_URL}/admin/reseed`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ---------------------------------------------------------------------------
// Utility
// ---------------------------------------------------------------------------

export async function getHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  return handleResponse(res);
}
