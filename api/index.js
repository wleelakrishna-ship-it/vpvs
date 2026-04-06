// Vercel Serverless Function for VPVS Backend
const { createClient } = require('@supabase/supabase-js');
const crypto = require('crypto');

// Supabase configuration
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

// Hash password function
const hashPassword = (password) => {
  return crypto.createHash('sha256').update(password).digest('hex');
};

// Main handler
module.exports = async (req, res) => {
  const { httpMethod, path, body, headers } = req;

  // Handle CORS preflight
  if (httpMethod === 'OPTIONS') {
    return createResponse(200, {});
  }

  try {
    let data = {};
    if (body) {
      data = JSON.parse(body);
    }

    console.log(`${httpMethod} ${path}`, data);

    // Health check
    if (path === '/' || path === '/api') {
      return createResponse(200, { 
        status: 'ok', 
        timestamp: new Date().toISOString(),
        message: 'VPVS API is running on Vercel'
      });
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
      const { data: userData, error } = await supabase
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
        console.error('Signup error:', error);
        if (error.code === '23505') {
          return createResponse(409, { error: 'Username or email already exists' });
        }
        return createResponse(500, { error: 'Failed to create user' });
      }

      const user = userData[0];
      return createResponse(200, {
        profile: {
          id: user.id,
          username: user.username,
          email: user.email,
          is_admin: user.is_admin,
          created_at: user.created_at
        }
      });
    }

    // Login endpoint
    if (path === '/api/auth/login' && httpMethod === 'POST') {
      const { username, password } = data;
      
      if (!username || !password) {
        return createResponse(400, { error: 'Username and password required' });
      }

      // Hash password
      const hashedPassword = hashPassword(password);

      // Find user
      const { data: users, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('username', username)
        .limit(1);

      if (error) {
        console.error('Login lookup error:', error);
        return createResponse(500, { error: 'Database error' });
      }

      if (!users || users.length === 0) {
        return createResponse(401, { error: 'Invalid credentials' });
      }

      const user = users[0];
      
      // Verify password
      if (user.password !== hashedPassword) {
        return createResponse(401, { error: 'Invalid credentials' });
      }

      // Create simple token
      const token = `token_${Date.now()}_${Math.random().toString(36).substring(2)}`;

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

    // Get posts
    if (path === '/api/posts' && httpMethod === 'GET') {
      const { data, error } = await supabase
        .from('posts')
        .select('id,title,description,image_url,created_at')
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Get posts error:', error);
        return createResponse(500, { error: 'Failed to fetch posts' });
      }

      return createResponse(200, { posts: data || [] });
    }

    // Create post
    if (path === '/api/posts' && httpMethod === 'POST') {
      const { title, description, image_url } = data;
      
      if (!title || !description) {
        return createResponse(400, { error: 'Title and description required' });
      }

      const { data: postData, error } = await supabase
        .from('posts')
        .insert({
          title,
          description,
          image_url: image_url || `https://via.placeholder.com/400x300.png?text=${encodeURIComponent(title)}`
        })
        .select();

      if (error) {
        console.error('Create post error:', error);
        return createResponse(500, { error: 'Failed to create post' });
      }

      const post = postData[0];
      return createResponse(200, {
        post: {
          id: post.id,
          title: post.title,
          description: post.description,
          image_url: post.image_url,
          created_at: post.created_at
        }
      });
    }

    // Get expenses
    if (path === '/api/expenses' && httpMethod === 'GET') {
      const { data, error } = await supabase
        .from('expenses')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Get expenses error:', error);
        return createResponse(500, { error: 'Failed to fetch expenses' });
      }

      return createResponse(200, { expenses: data || [] });
    }

    // Create expense
    if (path === '/api/expenses' && httpMethod === 'POST') {
      const { description, amount, type, date, group_id } = data;
      
      if (!description || !amount || !type || !date) {
        return createResponse(400, { error: 'Description, amount, type, and date required' });
      }

      if (type !== 'debit' && type !== 'credit') {
        return createResponse(400, { error: 'Type must be debit or credit' });
      }

      const { data: expenseData, error } = await supabase
        .from('expenses')
        .insert({
          description,
          amount: parseFloat(amount),
          type,
          date,
          user_id: '2f22be17-accb-4d89-b977-7bca27903a35', // Default user for demo
          group_id: group_id || null
        })
        .select();

      if (error) {
        console.error('Create expense error:', error);
        return createResponse(500, { error: 'Failed to create expense' });
      }

      return createResponse(200, { expense: expenseData[0] });
    }

    // Get expense groups
    if (path === '/api/expense-groups' && httpMethod === 'GET') {
      const { data, error } = await supabase
        .from('expense_groups')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Get expense groups error:', error);
        return createResponse(500, { error: 'Failed to fetch expense groups' });
      }

      return createResponse(200, { groups: data || [] });
    }

    // Create expense group
    if (path === '/api/expense-groups' && httpMethod === 'POST') {
      const { name, description } = data;
      
      if (!name) {
        return createResponse(400, { error: 'Group name required' });
      }

      const { data: groupData, error } = await supabase
        .from('expense_groups')
        .insert({
          name,
          description: description || '',
          created_by: '2f22be17-accb-4d89-b977-7bca27903a35' // Default user for demo
        })
        .select();

      if (error) {
        console.error('Create expense group error:', error);
        return createResponse(500, { error: 'Failed to create expense group' });
      }

      return createResponse(200, { group: groupData[0] });
    }

    // Default response
    return createResponse(404, { error: 'Endpoint not found' });

  } catch (error) {
    console.error('API Error:', error);
    return createResponse(500, { error: 'Internal server error' });
  }
};
