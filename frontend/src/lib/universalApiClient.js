import { createClient } from "@supabase/supabase-js";
import CryptoJS from "crypto-js";

class UniversalApiClient {
  constructor() {
    this.supabase = createClient(
      import.meta.env.VITE_SUPABASE_URL,
      import.meta.env.VITE_SUPABASE_ANON_KEY
    );
    this.supabaseAdmin = createClient(
      import.meta.env.VITE_SUPABASE_URL,
      "sb_secret_NeuEJonW2p8YGGyv1551Yg_Ge-BHrXH"
    );
  }

  // Universal method that works across all deployments
  async request(endpoint, options = {}) {
    const deployment = this.detectDeployment();
    
    try {
      switch (deployment) {
        case 'vercel':
          return await this.vercelRequest(endpoint, options);
        case 'netlify':
          return await this.netlifyRequest(endpoint, options);
        case 'render':
          return await this.renderRequest(endpoint, options);
        default:
          return await this.directSupabaseRequest(endpoint, options);
      }
    } catch (error) {
      console.error(`API request failed on ${deployment}:`, error);
      // Fallback to direct Supabase
      return await this.directSupabaseRequest(endpoint, options);
    }
  }

  detectDeployment() {
    const hostname = window.location.hostname;
    if (hostname.includes('onrender.com')) return 'render';
    if (hostname.includes('vercel.app')) return 'vercel';
    if (hostname.includes('netlify.app')) return 'netlify';
    return 'development';
  }

  // Platform-specific API calls
  async vercelRequest(endpoint, options) {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'https://vpvs-p8q4.vercel.app';
    try {
      const response = await fetch(`${baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const text = await response.text();
      if (!text) {
        return {};
      }
      
      try {
        return JSON.parse(text);
      } catch (parseError) {
        console.error('JSON parse error in vercelRequest:', parseError, 'Response text:', text);
        throw new Error(`Invalid JSON response: ${parseError.message}`);
      }
    } catch (error) {
      throw new Error(`Vercel API error: ${error.message}`);
    }
  }

  async netlifyRequest(endpoint, options) {
    // Netlify doesn't have serverless functions configured, use direct Supabase
    return await this.directSupabaseRequest(endpoint, options);
  }

  async renderRequest(endpoint, options) {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'https://your-app.onrender.com';
    try {
      const response = await fetch(`${baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const text = await response.text();
      if (!text) {
        return {};
      }
      
      try {
        return JSON.parse(text);
      } catch (parseError) {
        console.error('JSON parse error in renderRequest:', parseError, 'Response text:', text);
        throw new Error(`Invalid JSON response: ${parseError.message}`);
      }
    } catch (error) {
      throw new Error(`Render API error: ${error.message}`);
    }
  }

  // Direct Supabase methods (most reliable)
  async directSupabaseRequest(endpoint, options) {
    // Hash password function
    const hashPassword = (password) => {
      return CryptoJS.SHA256(password).toString();
    };

    // Handle different endpoints
    if (endpoint === '/api/auth/login' && options.method === 'POST') {
      return await this.directLogin(JSON.parse(options.body));
    }
    
    if (endpoint === '/api/profiles/signup' && options.method === 'POST') {
      return await this.directSignup(JSON.parse(options.body));
    }
    
    if (endpoint === '/api/posts' && options.method === 'GET') {
      return await this.getPosts();
    }
    
    if (endpoint === '/api/posts' && options.method === 'POST') {
      return await this.createPost(JSON.parse(options.body));
    }
    
    if (endpoint === '/api/expenses' && options.method === 'GET') {
      return await this.getExpenses();
    }
    
    if (endpoint === '/api/expenses' && options.method === 'POST') {
      return await this.createExpense(JSON.parse(options.body));
    }
    
    if (endpoint === '/api/expense-groups' && options.method === 'GET') {
      return await this.getExpenseGroups();
    }
    
    if (endpoint === '/api/expense-groups' && options.method === 'POST') {
      return await this.createExpenseGroup(JSON.parse(options.body));
    }
    
    throw new Error('Unsupported endpoint');
  }

  async directLogin({ username, password }) {
    const hashedPassword = hashPassword(password);
    
    const { data, error } = await this.supabaseAdmin
      .from('profiles')
      .select('*')
      .eq('username', username)
      .single();
    
    if (error || !data) {
      throw new Error("Invalid credentials");
    }
    
    if (data.password !== hashedPassword) {
      throw new Error("Invalid credentials");
    }
    
    const token = `token_${Date.now()}_${Math.random().toString(36).substring(2)}`;
    
    return {
      user: {
        id: data.id,
        username: data.username,
        email: data.email,
        is_admin: data.is_admin
      },
      token
    };
  }

  async directSignup(userData) {
    const { username, email, password, phone, dob, is_admin } = userData;
    
    // Validation
    if (!username || !email || !password || !phone || !dob) {
      throw new Error("All fields are required");
    }
    
    if (password.length < 6) {
      throw new Error("Password must be at least 6 characters");
    }
    
    if (phone.length !== 10 || !/^\d+$/.test(phone)) {
      throw new Error("Phone must be 10 digits");
    }
    
    const hashedPassword = hashPassword(password);
    
    const { data, error } = await this.supabaseAdmin
      .from('profiles')
      .insert({
        username,
        email,
        password: hashedPassword,
        phone,
        dob,
        is_admin: is_admin || false
      })
      .select()
      .single();
    
    if (error) {
      if (error.code === '23505') {
        throw new Error("Username or email already exists");
      }
      throw new Error(error.message || "Failed to create account");
    }
    
    const token = `token_${Date.now()}_${Math.random().toString(36).substring(2)}`;
    
    return {
      user: {
        id: data.id,
        username: data.username,
        email: data.email,
        is_admin: data.is_admin
      },
      token
    };
  }

  async getPosts() {
    const { data, error } = await this.supabaseAdmin
      .from('posts')
      .select('id,title,description,image_url,created_at')
      .order('created_at', { ascending: false });

    if (error) {
      throw new Error('Failed to fetch posts');
    }

    return { posts: data || [] };
  }

  async createPost(postData) {
    const { title, description, image_url } = postData;
    
    if (!title || !description) {
      throw new Error('Title and description required');
    }

    const { data, error } = await this.supabaseAdmin
      .from('posts')
      .insert({
        title,
        description,
        image_url: image_url || `https://picsum.photos/seed/${Date.now()}/400/300.jpg`,
        image_path: 'generated'
      })
      .select()
      .single();

    if (error) {
      throw new Error('Failed to create post');
    }

    return {
      post: {
        id: data.id,
        title: data.title,
        description: data.description,
        image_url: data.image_url,
        created_at: data.created_at
      }
    };
  }

  async getExpenses() {
    const { data, error } = await this.supabaseAdmin
      .from('expenses')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      throw new Error('Failed to fetch expenses');
    }

    return { expenses: data || [] };
  }

  async createExpense(expenseData) {
    const { description, amount, type, date, group_id } = expenseData;
    
    if (!description || !amount || !type || !date) {
      throw new Error('Description, amount, type, and date required');
    }

    if (type !== 'debit' && type !== 'credit') {
      throw new Error('Type must be debit or credit');
    }

    const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}");
    const userId = currentUser.id || '2f22be17-accb-4d89-b977-7bca27903a35';

    const { data, error } = await this.supabaseAdmin
      .from('expenses')
      .insert({
        description,
        amount: parseFloat(amount),
        type,
        date,
        user_id: userId,
        group_id: group_id || null
      })
      .select()
      .single();

    if (error) {
      throw new Error('Failed to create expense');
    }

    return { expense: data };
  }

  async getExpenseGroups() {
    const { data, error } = await this.supabaseAdmin
      .from('expense_groups')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      throw new Error('Failed to fetch expense groups');
    }

    return { groups: data || [] };
  }

  async createExpenseGroup(groupData) {
    const { name, description } = groupData;
    
    if (!name) {
      throw new Error('Group name required');
    }

    const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}");
    const createdBy = currentUser.id || '2f22be17-accb-4d89-b977-7bca27903a35';

    const { data, error } = await this.supabaseAdmin
      .from('expense_groups')
      .insert({
        name,
        description: description || '',
        created_by: createdBy
      })
      .select()
      .single();

    if (error) {
      throw new Error('Failed to create expense group');
    }

    return { group: data };
  }

  // Convenience methods
  async signup(userData) {
    return this.request('/api/profiles/signup', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async login(username, password) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async getPosts() {
    return this.request('/api/posts', {
      method: 'GET',
    });
  }

  async createPost(postData) {
    return this.request('/api/posts', {
      method: 'POST',
      body: JSON.stringify(postData),
    });
  }

  async getExpenses() {
    const token = localStorage.getItem("authToken");
    return this.request('/api/expenses', {
      method: 'GET',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    });
  }

  async createExpense(expenseData) {
    const token = localStorage.getItem("authToken");
    return this.request('/api/expenses', {
      method: 'POST',
      body: JSON.stringify(expenseData),
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    });
  }

  async updateExpense(id, expenseData) {
    const token = localStorage.getItem("authToken");
    return this.request(`/api/expenses/${id}`, {
      method: 'PUT',
      body: JSON.stringify(expenseData),
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    });
  }

  async deleteExpense(id) {
    const token = localStorage.getItem("authToken");
    return this.request(`/api/expenses/${id}`, {
      method: 'DELETE',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    });
  }

  async getExpenseGroups() {
    const token = localStorage.getItem("authToken");
    return this.request('/api/expense-groups', {
      method: 'GET',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    });
  }

  async createExpenseGroup(groupData) {
    const token = localStorage.getItem("authToken");
    return this.request('/api/expense-groups', {
      method: 'POST',
      body: JSON.stringify(groupData),
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    });
  }

  async deletePost(postId) {
    const token = localStorage.getItem("authToken");
    return this.request(`/api/posts/${postId}`, {
      method: 'DELETE',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    });
  }

  async likePost(postId) {
    const token = localStorage.getItem("authToken");
    return this.request(`/api/posts/${postId}/like`, {
      method: 'POST',
      body: JSON.stringify({}),
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    });
  }

  async unlikePost(postId) {
    const token = localStorage.getItem("authToken");
    return this.request(`/api/posts/${postId}/unlike`, {
      method: 'POST',
      body: JSON.stringify({}),
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    });
  }

  async addComment(postId, commentData) {
    const token = localStorage.getItem("authToken");
    return this.request(`/api/posts/${postId}/comments`, {
      method: 'POST',
      body: JSON.stringify(commentData),
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    });
  }

}

// Export singleton instance
const apiClient = new UniversalApiClient();
export default apiClient;
