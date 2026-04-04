import { createClient } from "@supabase/supabase-js";
import { sha256 } from "crypto-js/sha256";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseServiceKey = "sb_secret_NeuEJonW2p8YGGyv1551Yg_Ge-BHrXH";

// Create admin client with service role key
const supabaseAdmin = createClient(supabaseUrl, supabaseServiceKey);

export async function directSignup(userData) {
  try {
    const { username, email, password, phone, dob, is_admin } = userData;
    
    // Validate input
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
    const hashedPassword = sha256(password).toString();
    
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
  } catch (error) {
    console.error('Direct signup error:', error);
    throw error;
  }
}

export async function directLogin(username, password) {
  try {
    if (!username || !password) {
      throw new Error("Username and password required");
    }
    
    // Hash password
    const hashedPassword = sha256(password).toString();
    
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
  } catch (error) {
    console.error('Direct login error:', error);
    throw error;
  }
}
