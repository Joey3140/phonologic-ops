/**
 * Marketing Campaign Stream Proxy
 * Forwards SSE streaming requests to Railway orchestrator
 */

export const config = {
  api: {
    bodyParser: true,
    responseLimit: false,
  },
};

export default async function handler(req, res) {
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-User-Email');
    return res.status(200).end();
  }

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
  
  const targetUrl = `${orchestratorUrl}/api/orchestrator/marketing/campaign/stream`;
  
  console.log('Streaming proxy to:', targetUrl);
  
  try {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
    };
    if (req.headers['x-user-email']) {
      headers['X-User-Email'] = req.headers['x-user-email'];
    }
    
    const response = await fetch(targetUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(req.body),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Orchestrator error:', response.status, errorText);
      return res.status(response.status).json({ 
        error: 'Orchestrator error', 
        message: errorText 
      });
    }
    
    // Set SSE headers
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('X-Accel-Buffering', 'no');
    res.setHeader('Access-Control-Allow-Origin', '*');
    
    // Stream the response
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        res.write(chunk);
        
        // Flush if available
        if (res.flush) res.flush();
      }
    } catch (streamError) {
      console.error('Stream error:', streamError);
    } finally {
      res.end();
    }
    
  } catch (error) {
    console.error('Stream proxy error:', error);
    res.status(502).json({ 
      error: 'Orchestrator unavailable',
      message: error.message 
    });
  }
}
