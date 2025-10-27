document.addEventListener('DOMContentLoaded', () => {
  if (!window.appUrls?.ajaxMatterOptions) {
    console.error('ajaxMatterOptions URL not provided via window.appUrls');
    return;
  }

  const clientSelect = document.getElementById('id_client');
  const matterSelect = document.getElementById('id_matter');
  const ajaxUrl = window.appUrls.ajaxMatterOptions;

  if (!clientSelect || !matterSelect) {return;}

  function setLoading() {
    matterSelect.disabled = true;
    matterSelect.innerHTML = '<option value="">Loading matters…</option>';
  }

  function setEmpty() {
    matterSelect.disabled = false;
    matterSelect.innerHTML = '<option value="">— Select matter —</option>';
  }

  async function loadMatters(clientId, preserveValue = '') {
    if (!clientId) {return setEmpty();}

    setLoading();
    try {
      const resp = await fetch(`${ajaxUrl}?client=${encodeURIComponent(clientId)}`, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'text/html'
        }
      });
      if (!resp.ok) {throw new Error(`HTTP ${resp.status}`);}
      const html = await resp.text();
      matterSelect.innerHTML = html || '<option value="">No matters found</option>';
      matterSelect.disabled = false;

      // Re-select previously chosen matter if still present
      if (preserveValue) {
        const opt = matterSelect.querySelector(`option[value="${CSS.escape(preserveValue)}"]`);
        if (opt) {opt.selected = true;}
      }
    } catch (e) {
      console.error('Failed to load matters:', e);
      matterSelect.innerHTML = '<option value="">— Unable to load matters —</option>';
      matterSelect.disabled = true;
    }
  }

  // Event: client changed
  clientSelect.addEventListener('change', e => {
    const cid = e.target.value || '';
    loadMatters(cid);
  });

  // Preload if client already selected (e.g., after validation errors)
  if (clientSelect.value) {
    const currentMatter = matterSelect.value || '';
    loadMatters(clientSelect.value, currentMatter);
  } else {
    setEmpty();
  }
});
