document.getElementById('analyzeBtn').addEventListener('click', async () => {
  const loading = document.getElementById('loading');
  const resultDiv = document.getElementById('result');
  const company = document.getElementById('company').value;
  
  loading.classList.remove('hidden');
  resultDiv.classList.add('hidden');

  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    function: () => document.body.innerText,
  }, async (injectionResults) => {
    const pageText = injectionResults[0].result;
    
    try {
      const response = await fetch('http://127.0.0.1:8000/analyze_job', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: tab.url,
          html: pageText,
          company_name: company
        })
      });
      
      const data = await response.json();
      loading.classList.add('hidden');
      resultDiv.classList.remove('hidden');
      
      if(data.drafted_email) {
        resultDiv.innerHTML = `
          <span class="highlight">Role:</span> ${data.structured_job?.role_title}<br><br>
          <span class="highlight">Missing Skills:</span> ${data.skill_gap_plan?.missing_skills.join(", ")}<br><br>
          <span class="highlight">Drafted Email Subject:</span><br> ${data.drafted_email.subject_line}<br><br>
          <span class="highlight">Drafted Email Body:</span><br> ${data.drafted_email.body.replace(/\n/g, '<br>')}
        `;
      } else {
         resultDiv.innerHTML = `Error: ${JSON.stringify(data.error_logs)}`;
      }

    } catch (err) {
      loading.classList.add('hidden');
      resultDiv.classList.remove('hidden');
      resultDiv.innerHTML = `Failed to connect to backend. Is FastAPI running (python api.py)?<br><br>Error: ${err}`;
    }
  });
});
