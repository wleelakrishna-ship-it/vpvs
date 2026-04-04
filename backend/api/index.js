// Simple Node.js backend for Vercel deployment
const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseServiceKey) {
  console.error('Missing Supabase environment variables');
}

const supabase = createClient(supabaseUrl, supabaseServiceKey);

// CORS headers
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  'Content-Type': 'application/json'
};

// Helper function
const createResponse = (statusCode, body) => ({
  statusCode: statusCode,
  headers: corsHeaders,
  body: JSON.stringify(body)
});

// Hash password
const hashPassword = (password) => {
  const crypto = require('crypto');
  return crypto.createHash('sha256').update(password).digest('hex');
};

// Health check
exports.handler = async (event, context) => {
  const { httpMethod, path, body } = event;

  // Handle CORS preflight
  if (httpMethod === 'OPTIONS') {
    return createResponse(200, {});
  }

  try {
    let data = {};
    if (body) {
      data = JSON.parse(body);
    }

    // Health check
    if (path === '/' || path === '/api') {
      return createResponse(200, { status: 'ok' });
    }

    // Signup endpoint
    if (path === '/api/profiles/signup' && httpMethod === 'POST') {
      const { username, email, password, phone, dob, is_admin } = data;
      
      // Validation
      if (!username || !email || !password || !phone || !dob) {
        return createResponse(400, { error: 'Missing required fields' });
      }
      
      if (username.length > 32) {
        return createResponse(400, { error: 'Username too long' });
      }
      
      if (password.length < 6) {
        return createResponse(400, { error: 'Password must be at least 6 characters' });
      }
      
      if (phone.length !== 10 || !/^\d+$/.test(phone)) {
        return createResponse(400, { error: 'Phone must be 10 digits' });
      }

      // Hash password
      const hashedPassword = hashPassword(password);

      // Insert user
      const { data, error } = await supabase
        .from('profiles')
        .insert({
          username,
          email,
          password: hashedPassword,
          phone,
          dob,
          is_admin: is_admin || false
        })
        .select();

      if (error) {
        if (error.code === '23505') {
          return createResponse(409, { error: 'Username or email already exists' });
        }
        return createResponse(500, { error: 'Failed to create user' });
      }

      return createResponse(200, {
        profile: {
          id: data[0].id,
          username: data[0].username,
          email: data[0].email,
          is_admin: data[0].is_admin,
          created_at: data[0].created_at
        }
      });
    }

    // Login endpoint
    if (path === '/api/auth/login' && httpMethod === 'POST') {
      const { username, password } = data;
      
      if (!username || !password) {
        return createResponse(400, { error: 'Username and password required' });
      }

      // Find user
      const { data: users, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('username', username)
        .limit(1);

      if (error || !users || users.length === 0) {
        return createResponse(401, { error: 'Invalid credentials' });
      }

      const user = users[0];
      const hashedPassword = hashPassword(password);

      // Verify password
      if (user.password !== hashedPassword) {
        return createResponse(401, { error: 'Invalid credentials' });
      }

      // Create simple token
      const token = require('crypto').randomUUID();

      return createResponse(200, {
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          is_admin: user.is_admin
        },
        token
      });
    }

    // Get posts (existing functionality)
    if (path === '/api/posts' && httpMethod === 'GET') {
      const { data, error } = await supabase
        .from('posts')
        .select('id,title,description,image_url,created_at')
        .order('created_at', { ascending: false });

      return createResponse(200, { posts: data || [] });
    }

    // Default response
    return createResponse(404, { error: 'Endpoint not found' });

  } catch (error) {
    console.error('API Error:', error);
    return createResponse(500, { error: 'Internal server error' });
  }
};
