/**
 * Direct orchestrator status proxy (not catch-all)
 */

export default async function handler(req, res) {
  let orchestratorUrl = process.env.ORCHESTRATOR_URL;
  
  if (!orchestratorUrl) {
    return res.status(503).json({ 
      error: 'Orchestrator not configured',
      message: 'ORCHESTRATOR_URL environment variable not set'
    });
  }
  
  // Ensure URL has protocol
  if (!orchestratorUrl.startsWith('http')) {
    orchestratorUrl = `https://${orchestratorUrl}`;
  }
  
  // Remove trailing slash if present
  orchestratorUrl = orchestratorUrl.replace(/\/$/, '');
  
  const targetUrl = `${orchestratorUrl}/api/orchestrator/status`;
  
  try {
    const response = await fetch(targetUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });
    
    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    console.error('Orchestrator status error:', error);
    res.status(502).json({ 
      error: 'Orchestrator unavailable',
      message: error.message,
      targetUrl: targetUrl
    });
  }
}
