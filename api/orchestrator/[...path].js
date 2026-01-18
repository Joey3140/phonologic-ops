/**
 * Orchestrator Proxy - Forwards requests to Railway-hosted orchestrator
 * Catches all /api/orchestrator/* requests and proxies to ORCHESTRATOR_URL
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
  
  // Get the path after /api/orchestrator/
  const { path } = req.query;
  const targetPath = Array.isArray(path) ? path.join('/') : path || '';
  const targetUrl = `${orchestratorUrl}/api/orchestrator/${targetPath}`;
  
  console.log('Proxying to:', targetUrl);
  
  try {
    const fetchOptions = {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    };
    
    // Forward body for POST/PUT/PATCH requests
    if (['POST', 'PUT', 'PATCH'].includes(req.method) && req.body) {
      fetchOptions.body = JSON.stringify(req.body);
    }
    
    const response = await fetch(targetUrl, fetchOptions);
    const data = await response.json();
    
    // Forward the status code and response
    res.status(response.status).json(data);
  } catch (error) {
    console.error('Orchestrator proxy error:', error);
    res.status(502).json({ 
      error: 'Orchestrator unavailable',
      message: error.message 
    });
  }
}
