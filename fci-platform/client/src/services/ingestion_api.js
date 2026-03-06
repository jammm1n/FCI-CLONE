const BASE_URL = '/api/ingestion';

function authHeaders(token) {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };
}

function bearerOnly(token) {
  return { Authorization: `Bearer ${token}` };
}

async function handleResponse(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = body.detail;
    if (typeof detail === 'object' && detail.message) {
      const err = new Error(detail.message);
      err.data = detail;
      throw err;
    }
    throw new Error(detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

// ── Case Management ──────────────────────────────────────────────

export async function createCase(token, caseId) {
  const res = await fetch(`${BASE_URL}/cases`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify({
      case_id: caseId,
    }),
  });
  return handleResponse(res);
}

export async function getActiveCase(token) {
  const res = await fetch(`${BASE_URL}/cases/active`, {
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

export async function getCaseStatus(token, caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/status`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function resetCase(token, caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/reset`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function deleteCase(token, caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}`, {
    method: 'DELETE',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ── C360 ─────────────────────────────────────────────────────────

export async function uploadC360(token, caseId, files) {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }
  const res = await fetch(`${BASE_URL}/cases/${caseId}/c360`, {
    method: 'POST',
    headers: bearerOnly(token),
    body: formData,
  });
  return handleResponse(res);
}

export async function getC360Output(token, caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/c360`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export function c360CsvUrl(caseId) {
  return `${BASE_URL}/cases/${caseId}/c360/csv`;
}

// ── Elliptic ─────────────────────────────────────────────────────

export async function addManualAddresses(token, caseId, addresses) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/elliptic/addresses`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify({ manual_addresses: addresses }),
  });
  return handleResponse(res);
}

export async function submitElliptic(token, caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/elliptic/submit`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function getEllipticOutput(token, caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/elliptic`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ── Cross-Reference & UID Search ─────────────────────────────────

export async function runAddressXref(token, caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/address-xref`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function runUidSearch(token, caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/uid-search`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ── Section Output (for preview) ─────────────────────────────────

export async function getSectionOutput(token, caseId, sectionKey) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/${sectionKey}`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ── Sections ─────────────────────────────────────────────────────

export async function markSectionNone(token, caseId, sectionKey) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/sections/${sectionKey}/none`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function reopenSection(token, caseId, sectionKey) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/sections/${sectionKey}/reopen`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ── Notes ────────────────────────────────────────────────────────

export async function saveNotes(token, caseId, notes) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/notes`, {
    method: 'PUT',
    headers: authHeaders(token),
    body: JSON.stringify({ notes }),
  });
  return handleResponse(res);
}

// ── Text Sections with AI ────────────────────────────────────────

export async function saveTextSection(token, caseId, sectionKey, text) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/text-section/${sectionKey}`, {
    method: 'PUT',
    headers: authHeaders(token),
    body: JSON.stringify({ text }),
  });
  return handleResponse(res);
}

export async function getTextSection(token, caseId, sectionKey) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/text-section/${sectionKey}`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ── Iterative Entry Sections ─────────────────────────────────────

export async function addEntry(token, caseId, sectionKey, text) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/entries/${sectionKey}`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify({ text }),
  });
  return handleResponse(res);
}

export async function addEntryWithImages(token, caseId, sectionKey, text, files) {
  const formData = new FormData();
  formData.append('text', text);
  if (files && files.length > 0) {
    for (const file of files) {
      formData.append('files', file);
    }
  }
  const res = await fetch(`${BASE_URL}/cases/${caseId}/entries/${sectionKey}/with-images`, {
    method: 'POST',
    headers: bearerOnly(token),
    body: formData,
  });
  return handleResponse(res);
}

export async function removeEntry(token, caseId, sectionKey, entryId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/entries/${sectionKey}/${entryId}`, {
    method: 'DELETE',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function processEntries(token, caseId, sectionKey) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/entries/${sectionKey}/process`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function getEntries(token, caseId, sectionKey) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/entries/${sectionKey}`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ── Text + Image Sections (L1 Victim, L1 Suspect) ───────────────

export async function saveTextImageSection(token, caseId, sectionKey, text, files) {
  const formData = new FormData();
  formData.append('text', text || '');
  if (files && files.length > 0) {
    for (const file of files) {
      formData.append('files', file);
    }
  }
  const res = await fetch(`${BASE_URL}/cases/${caseId}/text-image-section/${sectionKey}`, {
    method: 'PUT',
    headers: bearerOnly(token),
    body: formData,
  });
  return handleResponse(res);
}

export async function getTextImageSection(token, caseId, sectionKey) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/text-image-section/${sectionKey}`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function resetTextImageSection(token, caseId, sectionKey) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/text-image-section/${sectionKey}/reset`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ── KYC (Image-Only) ────────────────────────────────────────────

export async function uploadKYC(token, caseId, files) {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }
  const res = await fetch(`${BASE_URL}/cases/${caseId}/kyc`, {
    method: 'POST',
    headers: bearerOnly(token),
    body: formData,
  });
  return handleResponse(res);
}

export async function getKYCOutput(token, caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/kyc`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function resetKYC(token, caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/kyc/reset`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ── Assembly ─────────────────────────────────────────────────────

export async function assembleCase(token, caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/assemble`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}
