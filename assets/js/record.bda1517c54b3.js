const ajaxUrl = window.appUrls.ajaxMatterOptions; // e.g. "/ajax/matter-options/"
fetch(`${ajaxUrl}?client=${clientId}`)
  .then(r => r.json())
  .then(data => { /* ... */ });

document.addEventListener('DOMContentLoaded', function() {
    const clientSelect = document.getElementById('id_client');
    const matterSelect = document.getElementById('id_matter');
    const url = "{% url 'ajax-matter-options' %}";

    async function loadMatters(clientId) {
      try {
        const resp = await fetch(`${url}?client=${clientId}`, {headers: {'X-Requested-With':'XMLHttpRequest'}});
        matterSelect.innerHTML = await resp.text();
      } catch (e) {
        console.error(e);
        matterSelect.innerHTML = '<option value="">— Unable to load matters —</option>';
      }
    }

    clientSelect.addEventListener('change', (e) => {
      const cid = e.target.value;
      if (cid) {loadMatters(cid);}
      else {matterSelect.innerHTML = '<option value="">— Select matter —</option>';}
    });

    // Preload matters if a client is already selected (e.g. after validation errors)
    if (clientSelect.value) {loadMatters(clientSelect.value);}
  });