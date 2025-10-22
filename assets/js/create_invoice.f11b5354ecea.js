const ajaxUrl = window.appUrls.ajaxMatterOptions; // e.g. "/ajax/matter-options/"
fetch(`${ajaxUrl}?client=${clientId}`)
  .then(r => r.json())
  .then(data => { /* ... */ });

document.addEventListener('DOMContentLoaded', function() {
  const client = document.getElementById('id_inv_client');
  const matter = document.getElementById('id_inv_matter');
  const ajaxURL = "{% url 'ajax-matter-options' %}";

  const params = new URLSearchParams(window.location.search);
  const currentClient = params.get('client') || '';
  const currentMatter = params.get('matter') || '';

  async function loadMatters(cid, selectValue = '') {
    if (!matter) return;
    if (!cid) {
      matter.innerHTML = '<option value="">— Select matter —</option>';
      return;
    }
    const r = await fetch(`${ajaxURL}?client=${encodeURIComponent(cid)}`, {
      headers: {'X-Requested-With': 'XMLHttpRequest'}
    });
    matter.innerHTML = await r.text();
    if (selectValue) {
      const opt = matter.querySelector(`option[value="${CSS.escape(selectValue)}"]`);
      if (opt) opt.selected = true;
    }
  }

  function reloadWith(clientVal, matterVal) {
    const qs = new URLSearchParams();
    if (clientVal) qs.set('client', clientVal);
    if (matterVal) qs.set('matter', matterVal);
    window.location.search = qs.toString();
  }

  // Initial populate
  const initialClient = (client && client.value) || currentClient;
  if (initialClient) loadMatters(initialClient, currentMatter);

  if (client) {
    client.addEventListener('change', e => {
      const cid = e.target.value;
      loadMatters(cid);
      reloadWith(cid, '');
    });
  }
  if (matter) {
    matter.addEventListener('change', e => {
      const cid = client ? client.value : currentClient;
      reloadWith(cid, e.target.value);
    });
  }
});