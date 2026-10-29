(function () {
  const status = document.querySelector('#st');
  let lastCanvas;
  let sent = false;

  function sendCanvas(canvas, attempts = 0) {
    if (sent) return;
    // scan.js draws the uploaded image asynchronously in Image.onload.
    // Wait until the canvas has real dimensions before sending it.
    if (!canvas || !canvas.width || !canvas.height) {
      if (attempts < 80) setTimeout(() => sendCanvas(document.querySelector('#c'), attempts + 1), 100);
      return;
    }
    sent = true;
    lastCanvas = canvas;
    status.textContent = 'Generating your detailed skin report…';
    canvas.toBlob(async blob => {
      if (!blob) return;
      const data = new FormData();
      data.append('image', blob, 'glowra-scan.jpg');
      try {
        const response = await fetch('/analyze', { method: 'POST', body: data });
        const result = await response.json();
        if (!result.ok) throw new Error(result.error);
        const panel = document.createElement('div');
        panel.className = 'panel';
        panel.innerHTML = `<h2 style="margin-top:0">Detailed skin analysis</h2>
          <img src="${result.result_url}?t=${Date.now()}" alt="Annotated skin analysis" style="max-width:100%;border-radius:14px">
          <p class="mut">Acne/redness: ${result.acne.count} · Dark spots: ${result.dark_spots.count} · Pigmentation: ${result.pigmentation.count}</p>
          <p class="mut">${result.note}</p>`;
        // Feed the real analyzer findings into Glowra's product matcher.
        const scan = LS.get('scan', {});
        const backendConcerns = [
          result.acne && result.acne.count > 0 ? 'redness' : null,
          result.dark_spots && result.dark_spots.count > 0 ? 'darkspots' : null,
          result.pigmentation && result.pigmentation.count > 0 ? 'pigmentation' : null,
        ].filter(Boolean);
        scan.concerns = [...new Set([...(scan.concerns || []), ...backendConcerns])];
        LS.set('scan', scan);
        if (typeof window.show === 'function') window.show(scan);
        const results = document.querySelector('#res');
        const profile = results.querySelector('.panel');
        if (profile) profile.insertAdjacentElement('afterend', panel);
        else results.prepend(panel);
        panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
        status.textContent = 'Done. Your scan is saved to this browser.';
      } catch (error) {
        sent = false;
        status.textContent = error.message || 'Detailed analysis was unavailable.';
      }
    }, 'image/jpeg', .92);
  }

  document.querySelector('#f').addEventListener('change', () => {
    sent = false;
    sendCanvas(document.querySelector('#c'));
  });
  document.querySelector('#snap').addEventListener('click', () => {
    sent = false;
    sendCanvas(document.querySelector('#c'));
  });
})();
