/**
 * Orchestrator Proxy - Forwards requests to Railway-hosted orchestrator
 * Catches all /api/orchestrator/* requests and proxies to ORCHESTRATOR_URL
 */

export default async function handler(req, res) {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-User-Email');
    return res.status(200).end();
  }
  
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
    // Build headers, forwarding X-User-Email for authentication
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
      redirect: 'manual',  // Prevent redirect from converting POST to GET
    };
    
    // Forward body for POST/PUT/PATCH requests
    if (['POST', 'PUT', 'PATCH'].includes(req.method) && req.body) {
      fetchOptions.body = JSON.stringify(req.body);
    }
    
    console.log('Proxying:', req.method, targetUrl);
    
    let response = await fetch(targetUrl, fetchOptions);
    
    // Handle redirects manually to preserve method
    if (response.status >= 300 && response.status < 400) {
      const redirectUrl = response.headers.get('location');
      if (redirectUrl) {
        console.log('Following redirect to:', redirectUrl);
        response = await fetch(redirectUrl, fetchOptions);
      }
    }
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
