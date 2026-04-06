import { createClient } from "@supabase/supabase-js";
import CryptoJS from "crypto-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseServiceKey = "sb_secret_NeuEJonW2p8YGGyv1551Yg_Ge-BHrXH";

// Create admin client with service role key
const supabaseAdmin = createClient(supabaseUrl, supabaseServiceKey);

// Hash password function
const hashPassword = (password) => {
  return CryptoJS.SHA256(password).toString();
};

// API Client with fallback to direct Supabase
class ApiClient {
  constructor() {
    this.baseURL = import.meta.env.VITE_API_BASE_URL;
    this.useDirectSupabase = true; // Force direct Supabase for reliability
  }

  async request(endpoint, options = {}) {
    if (this.useDirectSupabase) {
      return this.directSupabaseRequest(endpoint, options);
    }

    // Fallback to HTTP API
    try {
      const url = `${this.baseURL}${endpoint}`;
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Request failed');
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed, falling back to direct Supabase:', error);
      return this.directSupabaseRequest(endpoint, options);
    }
  }

  async directSupabaseRequest(endpoint, options = {}) {
    const token = localStorage.getItem("authToken");
    
    try {
      // Handle different endpoints
      if (endpoint === '/api/auth/login' && options.method === 'POST') {
        const { username, password } = JSON.parse(options.body);
        return await this.directLogin(username, password);
      }
      
      if (endpoint === '/api/profiles/signup' && options.method === 'POST') {
        const userData = JSON.parse(options.body);
        return await this.directSignup(userData);
      }
      
      if (endpoint === '/api/posts' && options.method === 'GET') {
        return await this.directGetPosts();
      }
      
      if (endpoint === '/api/posts' && options.method === 'POST') {
        const postData = JSON.parse(options.body);
        return await this.directCreatePost(postData);
      }
      
      if (endpoint.startsWith('/api/expenses') && options.method === 'GET') {
        return await this.directGetExpenses();
      }
      
      if (endpoint === '/api/expenses' && options.method === 'POST') {
        const expenseData = JSON.parse(options.body);
        return await this.directCreateExpense(expenseData);
      }
      
      if (endpoint === '/api/expense-groups' && options.method === 'GET') {
        return await this.directGetExpenseGroups();
      }
      
      if (endpoint === '/api/expense-groups' && options.method === 'POST') {
        const groupData = JSON.parse(options.body);
        return await this.directCreateExpenseGroup(groupData);
      }
      
      throw new Error('Unsupported endpoint');
    } catch (error) {
      console.error('Direct Supabase request failed:', error);
      throw error;
    }
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
    
    // Hash password
    const hashedPassword = hashPassword(password);
    
    // Insert user directly into Supabase
    const { data, error } = await supabaseAdmin
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
    
    return {
      profile: {
        id: data.id,
        username: data.username,
        email: data.email,
        is_admin: data.is_admin,
        created_at: data.created_at
      }
    };
  }

  async directLogin(username, password) {
    if (!username || !password) {
      throw new Error("Username and password required");
    }
    
    // Hash password
    const hashedPassword = hashPassword(password);
    
    // Find user
    const { data, error } = await supabaseAdmin
      .from('profiles')
      .select('*')
      .eq('username', username)
      .single();
    
    if (error || !data) {
      throw new Error("Invalid credentials");
    }
    
    // Verify password
    if (data.password !== hashedPassword) {
      throw new Error("Invalid credentials");
    }
    
    // Create simple token
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

  async directGetPosts() {
    const { data, error } = await supabaseAdmin
      .from('posts')
      .select('id,title,description,image_url,created_at')
      .order('created_at', { ascending: false });

    if (error) {
      throw new Error('Failed to fetch posts');
    }

    return { posts: data || [] };
  }

  async directCreatePost(postData) {
    const { title, description, image_url } = postData;
    
    if (!title || !description) {
      throw new Error('Title and description required');
    }

    const { data, error } = await supabaseAdmin
      .from('posts')
      .insert({
        title,
        description,
        image_url: image_url || `https://via.placeholder.com/400x300.png?text=${encodeURIComponent(title)}`,
        image_path: 'placeholder' // Add required image_path field
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

  async directGetExpenses() {
    const { data, error } = await supabaseAdmin
      .from('expenses')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      throw new Error('Failed to fetch expenses');
    }

    return { expenses: data || [] };
  }

  async directCreateExpense(expenseData) {
    const { description, amount, type, date, group_id } = expenseData;
    
    if (!description || !amount || !type || !date) {
      throw new Error('Description, amount, type, and date required');
    }

    if (type !== 'debit' && type !== 'credit') {
      throw new Error('Type must be debit or credit');
    }

    // Get current user
    const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}");
    const userId = currentUser.id || '2f22be17-accb-4d89-b977-7bca27903a35';

    const { data, error } = await supabaseAdmin
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

  async directGetExpenseGroups() {
    const { data, error } = await supabaseAdmin
      .from('expense_groups')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      throw new Error('Failed to fetch expense groups');
    }

    return { groups: data || [] };
  }

  async directCreateExpenseGroup(groupData) {
    const { name, description } = groupData;
    
    if (!name) {
      throw new Error('Group name required');
    }

    // Get current user
    const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}");
    const createdBy = currentUser.id || '2f22be17-accb-4d89-b977-7bca27903a35';

    const { data, error } = await supabaseAdmin
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
    return this.request('/api/expenses', {
      method: 'GET',
    });
  }

  async createExpense(expenseData) {
    return this.request('/api/expenses', {
      method: 'POST',
      body: JSON.stringify(expenseData),
    });
  }

  async getExpenseGroups() {
    return this.request('/api/expense-groups', {
      method: 'GET',
    });
  }

  async createExpenseGroup(groupData) {
    return this.request('/api/expense-groups', {
      method: 'POST',
      body: JSON.stringify(groupData),
    });
  }
}

// Create singleton instance
const apiClient = new ApiClient();

export default apiClient;
