/**
 * Brain query endpoint proxy
 */

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

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
  
  const targetUrl = `${orchestratorUrl}/api/orchestrator/brain/query`;
  
  try {
    const response = await fetch(targetUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(req.body),
    });
    
    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    console.error('Brain query error:', error);
    res.status(502).json({ 
      error: 'Orchestrator unavailable',
      message: error.message
    });
  }
}
