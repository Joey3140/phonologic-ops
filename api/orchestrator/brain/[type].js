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
    // Forward the X-User-Email header for authentication
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    
    if (req.headers['x-user-email']) {
      headers['X-User-Email'] = req.headers['x-user-email'];
    }
    
    const fetchOptions = {
      method: req.method,
      headers,
    };
    
    // Forward body for POST/PUT/PATCH/DELETE requests
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method) && req.body) {
      fetchOptions.body = JSON.stringify(req.body);
    }
    
    const response = await fetch(targetUrl, fetchOptions);
    
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
