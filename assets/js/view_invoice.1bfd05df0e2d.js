const ajaxUrl = window.appUrls.ajaxMatterOptions; // e.g. "/ajax/matter-options/"
fetch(`${ajaxUrl}?client=${clientId}`)
  .then(r => r.json())
  .then(data => { /* ... */ });

// Narrow Matter dropdown when Client changes
  document.addEventListener('DOMContentLoaded', function() {
    const client = document.getElementById('id_ledger_client');
    const matter = document.getElementById('id_ledger_matter');
    const url = "{% url 'ajax-matter-options' %}";
    async function loadMatters(cid){
      const r = await fetch(`${url}?client=${cid}`, {headers:{'X-Requested-With':'XMLHttpRequest'}});
      matter.innerHTML = await r.text();
      // Preserve selected value if it exists in new list
      const current = "{{ filters.matter }}";
      if (current) { Array.from(matter.options).forEach(o => { if (o.value === current) o.selected = true; }); }
    }
    if (client) {
      client.addEventListener('change', e => {
        const cid = e.target.value;
        if (cid) loadMatters(cid);
        else matter.innerHTML = '<option value="">— Any —</option>';
      });
      if (client.value) loadMatters(client.value);
    }
  });
