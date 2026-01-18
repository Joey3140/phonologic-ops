/**
 * Brain info endpoint proxy (product, team, pitch, etc.)
 */

export default async function handler(req, res) {
  let orchestratorUrl = process.env.ORCHESTRATOR_URL;
  
  if (!orchestratorUrl) {
    return res.status(503).json({ 
      error: 'Orchestrator not configured',
      message: 'ORCHESTRATOR_URL environment variable not set'
    });
  }
  
  if (!orchestratorUrl.startsWith('http')) {
    orchestratorUrl = `https://${orchestratorUrl}`;
  }
  orchestratorUrl = orchestratorUrl.replace(/\/$/, '');
  
  const { type } = req.query;
  const targetUrl = `${orchestratorUrl}/api/orchestrator/brain/${type}`;
  
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
    console.error('Brain info error:', error);
    res.status(502).json({ 
      error: 'Orchestrator unavailable',
      message: error.message
    });
  }
}
