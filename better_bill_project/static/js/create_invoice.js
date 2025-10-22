document.addEventListener('DOMContentLoaded', () => {
  if (!window.appUrls || !window.appUrls.ajaxMatterOptions) {
    console.error('ajaxMatterOptions URL not provided via window.appUrls');
    return;
  }

  const client = document.getElementById('id_inv_client');
  const matter = document.getElementById('id_inv_matter');
  const ajaxUrl = window.appUrls.ajaxMatterOptions;

  if (!client || !matter) return;

  const params = new URLSearchParams(window.location.search);
  const currentClient = params.get('client') || '';
  const currentMatter = params.get('matter') || '';

   /** 
    * Safely select option in a select element
   */
  function safeSelectOption(selectEl, value) {
    if (!value) return;
    try {
      const opt = selectEl.querySelector(`option[value="${CSS.escape(value)}"]`);
      if (opt) opt.selected = true;
    } catch {
      const opts = [...selectEl.options];
      const found = opts.find(o => o.value === value);
      if (found) found.selected = true;
    }
  }
 
   /** 
    *   Update URL query parameters without page reload
    * */ 
  function setURLWithoutReload(clientVal, matterVal) {
    const qs = new URLSearchParams();
    if (clientVal) qs.set('client', clientVal);
    if (matterVal) qs.set('matter', matterVal);
    const newUrl = `${location.pathname}${qs.toString() ? `?${qs}` : ''}`;
    history.replaceState(null, '', newUrl);
  }

   /** 
    * Load matters for a given client ID
   */
  async function loadMatters(cid, selectValue = '') {
    if (!cid) {
      matter.innerHTML = '<option value="">— Select matter —</option>';
      setURLWithoutReload('', '');
      return;
    }
    matter.disabled = true;
    matter.innerHTML = '<option value="">Loading matters…</option>';

    try {
      const r = await fetch(`${ajaxUrl}?client=${encodeURIComponent(cid)}`, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'text/html'
        }
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const optionsHtml = await r.text();
      matter.innerHTML = optionsHtml || '<option value="">No matters found</option>';
      matter.disabled = false;
      if (selectValue) safeSelectOption(matter, selectValue);
    } catch (err) {
      console.error('Failed to load matters:', err);
      matter.innerHTML = '<option value="">Error loading matters</option>';
      matter.disabled = true;
    }
  }

  const initialClient = client.value || currentClient;
  if (initialClient) {
    loadMatters(initialClient, currentMatter);
    setURLWithoutReload(initialClient, currentMatter);
  }

  client.addEventListener('change', e => {
    const cid = e.target.value || '';
    loadMatters(cid, '');
    setURLWithoutReload(cid, '');
  });

  matter.addEventListener('change', e => {
    const cid = client.value || '';
    const mid = e.target.value || '';
    setURLWithoutReload(cid, mid);
  });
});
