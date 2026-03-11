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

/** Build ?subject_index=N query param for multi-user cases. */
function sq(subjectIndex) {
  return subjectIndex != null ? `?subject_index=${subjectIndex}` : '';
}

// ── Case Management ──────────────────────────────────────────────

export async function createCase(token, caseId, { subjectUid, coconspirators, caseMode, totalSubjects } = {}) {
  const body = { case_id: caseId };
  if (subjectUid != null) body.subject_uid = subjectUid;
  if (coconspirators?.length) body.coconspirator_uids = coconspirators;
  if (caseMode != null) body.case_mode = caseMode;
  if (totalSubjects != null) body.total_subjects = totalSubjects;
  const res = await fetch(`${BASE_URL}/cases`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify(body),
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

// ── Subject Lifecycle (Multi-User) ───────────────────────────────

export async function submitSubject(token, caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/submit-subject`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function setSubjectUid(token, caseId, subjectIndex, userId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/subjects/${subjectIndex}/uid`, {
    method: 'PATCH',
    headers: authHeaders(token),
    body: JSON.stringify({ user_id: userId }),
  });
  return handleResponse(res);
}

// ── C360 ─────────────────────────────────────────────────────────

export async function uploadC360(token, caseId, files, subjectIndex) {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }
  const res = await fetch(`${BASE_URL}/cases/${caseId}/c360${sq(subjectIndex)}`, {
    method: 'POST',
    headers: bearerOnly(token),
    body: formData,
  });
  return handleResponse(res);
}

export async function fetchC360(token, caseId, uid, cookie, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/c360/fetch${sq(subjectIndex)}`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify({ uid, cookie }),
  });
  return handleResponse(res);
}

export async function getC360Output(token, caseId, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/c360${sq(subjectIndex)}`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export function c360CsvUrl(caseId, subjectIndex) {
  return `${BASE_URL}/cases/${caseId}/c360/csv${sq(subjectIndex)}`;
}

// ── Elliptic ─────────────────────────────────────────────────────

export async function addManualAddresses(token, caseId, addresses, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/elliptic/addresses${sq(subjectIndex)}`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify({ manual_addresses: addresses }),
  });
  return handleResponse(res);
}

export async function submitElliptic(token, caseId, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/elliptic/submit${sq(subjectIndex)}`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function getEllipticOutput(token, caseId, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/elliptic${sq(subjectIndex)}`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ── UOL Upload ──────────────────────────────────────────────────

export async function uploadUol(token, caseId, file, subjectIndex) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${BASE_URL}/cases/${caseId}/uol${sq(subjectIndex)}`, {
    method: 'POST',
    headers: bearerOnly(token),
    body: formData,
  });
  return handleResponse(res);
}

// ── Cross-Reference & UID Search ─────────────────────────────────

export async function runAddressXref(token, caseId, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/address-xref${sq(subjectIndex)}`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function runUidSearch(token, caseId, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/uid-search${sq(subjectIndex)}`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ── Section Output (for preview) ─────────────────────────────────

export async function getSectionOutput(token, caseId, sectionKey, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/${sectionKey}${sq(subjectIndex)}`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ── Sections ─────────────────────────────────────────────────────

export async function markSectionNone(token, caseId, sectionKey, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/sections/${sectionKey}/none${sq(subjectIndex)}`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function reopenSection(token, caseId, sectionKey, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/sections/${sectionKey}/reopen${sq(subjectIndex)}`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ── Notes ────────────────────────────────────────────────────────

export async function saveNotes(token, caseId, notes, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/notes${sq(subjectIndex)}`, {
    method: 'PUT',
    headers: authHeaders(token),
    body: JSON.stringify({ notes }),
  });
  return handleResponse(res);
}

// ── Text Sections with AI ────────────────────────────────────────

export async function saveTextSection(token, caseId, sectionKey, text, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/text-section/${sectionKey}${sq(subjectIndex)}`, {
    method: 'PUT',
    headers: authHeaders(token),
    body: JSON.stringify({ text }),
  });
  return handleResponse(res);
}

export async function getTextSection(token, caseId, sectionKey, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/text-section/${sectionKey}${sq(subjectIndex)}`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ── Iterative Entry Sections ─────────────────────────────────────

export async function addEntry(token, caseId, sectionKey, text, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/entries/${sectionKey}${sq(subjectIndex)}`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify({ text }),
  });
  return handleResponse(res);
}

export async function addEntryWithImages(token, caseId, sectionKey, text, files, subjectIndex) {
  const formData = new FormData();
  formData.append('text', text);
  if (files && files.length > 0) {
    for (const file of files) {
      formData.append('files', file);
    }
  }
  const res = await fetch(`${BASE_URL}/cases/${caseId}/entries/${sectionKey}/with-images${sq(subjectIndex)}`, {
    method: 'POST',
    headers: bearerOnly(token),
    body: formData,
  });
  return handleResponse(res);
}

export async function removeEntry(token, caseId, sectionKey, entryId, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/entries/${sectionKey}/${entryId}${sq(subjectIndex)}`, {
    method: 'DELETE',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function processEntries(token, caseId, sectionKey, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/entries/${sectionKey}/process${sq(subjectIndex)}`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function getEntries(token, caseId, sectionKey, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/entries/${sectionKey}${sq(subjectIndex)}`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function setTotalCount(token, caseId, sectionKey, count, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/entries/${sectionKey}/total-count${sq(subjectIndex)}`, {
    method: 'PATCH',
    headers: authHeaders(token),
    body: JSON.stringify({ count }),
  });
  return handleResponse(res);
}

// ── Text + Image Sections (L1 Victim, L1 Suspect) ───────────────

export async function saveTextImageSection(token, caseId, sectionKey, text, files, subjectIndex) {
  const formData = new FormData();
  formData.append('text', text || '');
  if (files && files.length > 0) {
    for (const file of files) {
      formData.append('files', file);
    }
  }
  const res = await fetch(`${BASE_URL}/cases/${caseId}/text-image-section/${sectionKey}${sq(subjectIndex)}`, {
    method: 'PUT',
    headers: bearerOnly(token),
    body: formData,
  });
  return handleResponse(res);
}

export async function getTextImageSection(token, caseId, sectionKey, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/text-image-section/${sectionKey}${sq(subjectIndex)}`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function resetTextImageSection(token, caseId, sectionKey, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/text-image-section/${sectionKey}/reset${sq(subjectIndex)}`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ── KYC (Image-Only) ────────────────────────────────────────────

export async function uploadKYC(token, caseId, files, subjectIndex) {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }
  const res = await fetch(`${BASE_URL}/cases/${caseId}/kyc${sq(subjectIndex)}`, {
    method: 'POST',
    headers: bearerOnly(token),
    body: formData,
  });
  return handleResponse(res);
}

export async function getKYCOutput(token, caseId, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/kyc${sq(subjectIndex)}`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function resetKYC(token, caseId, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/kyc/reset${sq(subjectIndex)}`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ── Kodex / LE Entry Pipeline ────────────────────────────────────

export async function addKodexEntry(token, caseId, label, files, subjectIndex) {
  const formData = new FormData();
  formData.append('label', label);
  for (const file of files) {
    formData.append('files', file);
  }
  const res = await fetch(`${BASE_URL}/cases/${caseId}/kodex/entries${sq(subjectIndex)}`, {
    method: 'POST',
    headers: bearerOnly(token),
    body: formData,
  });
  return handleResponse(res);
}

export async function removeKodexEntry(token, caseId, entryId, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/kodex/entries/${entryId}${sq(subjectIndex)}`, {
    method: 'DELETE',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// Legacy batch upload (kept for backward compat)
export async function uploadKodex(token, caseId, files, subjectIndex) {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }
  const res = await fetch(`${BASE_URL}/cases/${caseId}/kodex${sq(subjectIndex)}`, {
    method: 'POST',
    headers: bearerOnly(token),
    body: formData,
  });
  return handleResponse(res);
}

export async function getKodexOutput(token, caseId, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/kodex${sq(subjectIndex)}`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function resetKodex(token, caseId, subjectIndex) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/kodex/reset${sq(subjectIndex)}`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ── Assembly ─────────────────────────────────────────────────────

export async function previewAssembly(token, caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/assemble/preview`, {
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

export async function assembleCase(token, caseId) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/assemble`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  return handleResponse(res);
}
