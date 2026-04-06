import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import apiClient from "../lib/apiClient.js";

export default function AdminDashboardPage() {
  const [posts, setPosts] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showPostForm, setShowPostForm] = useState(false);
  const [postForm, setPostForm] = useState({
    title: "",
    description: "",
    image: null
  });

  const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}");

  useEffect(() => {
    fetchPosts();
    fetchUsers();
  }, []);

  const fetchPosts = async () => {
    try {
      const data = await apiClient.getPosts();
      setPosts(data.posts || []);
    } catch (error) {
      console.error("Failed to fetch posts:", error);
    }
  };

  const fetchUsers = async () => {
    try {
      // This would need a new endpoint to fetch users
      // For now, we'll skip users fetching
      setUsers([]);
    } catch (error) {
      console.error("Failed to fetch users:", error);
    } finally {
      setLoading(false);
    }
  };

  const handlePostSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem("authToken");
      const postData = {
        title: postForm.title,
        description: postForm.description,
        image_url: postForm.image ? URL.createObjectURL(postForm.image) : null
      };

      const result = await apiClient.createPost(postData);
      
      setShowPostForm(false);
      setPostForm({ title: "", description: "", image: null });
      fetchPosts();
    } catch (error) {
      console.error("Error creating post:", error);
      alert("Failed to create post: " + error.message);
    }
  };

  const handleDeletePost = async (postId) => {
    if (!confirm("Are you sure you want to delete this post?")) return;

    try {
      const token = localStorage.getItem("authToken");
      // For now, we'll skip delete functionality
      alert("Delete functionality not yet implemented");
    } catch (error) {
      console.error("Error deleting post:", error);
      alert("Failed to delete post");
    }
  };

  if (loading) {
    return (
      <div className="page" style={{ textAlign: 'center', padding: '2rem' }}>
        <h2>Loading Admin Dashboard...</h2>
      </div>
    );
  }

  return (
    <div className="page" style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Admin Dashboard</h1>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span>Welcome, {currentUser.username || 'Admin'}!</span>
          <button 
            className="button" 
            onClick={() => setShowPostForm(true)}
            style={{ backgroundColor: 'var(--accent)', color: 'white' }}
          >
            Create Post
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div style={{ backgroundColor: 'var(--surface)', padding: '1.5rem', borderRadius: '8px', border: '1px solid var(--border)' }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--accent)' }}>Total Posts</h3>
          <p style={{ fontSize: '2rem', margin: '0', fontWeight: 'bold' }}>{posts.length}</p>
        </div>
        <div style={{ backgroundColor: 'var(--surface)', padding: '1.5rem', borderRadius: '8px', border: '1px solid var(--border)' }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--accent)' }}>Total Users</h3>
          <p style={{ fontSize: '2rem', margin: '0', fontWeight: 'bold' }}>{users.length}</p>
        </div>
        <div style={{ backgroundColor: 'var(--surface)', padding: '1.5rem', borderRadius: '8px', border: '1px solid var(--border)' }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--accent)' }}>Your Role</h3>
          <p style={{ fontSize: '1.5rem', margin: '0', fontWeight: 'bold' }}>
            {currentUser.is_admin ? 'Administrator' : 'User'}
          </p>
        </div>
      </div>

      {/* Posts Management */}
      <div style={{ backgroundColor: 'var(--surface)', padding: '1.5rem', borderRadius: '8px', border: '1px solid var(--border)' }}>
        <h2 style={{ margin: '0 0 1rem 0' }}>Posts Management</h2>
        
        {posts.length === 0 ? (
          <p style={{ textAlign: 'center', color: 'var(--muted)', padding: '2rem' }}>
            No posts yet. Create your first post!
          </p>
        ) : (
          <div style={{ display: 'grid', gap: '1rem' }}>
            {posts.map((post) => (
              <div key={post.id} style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                padding: '1rem',
                backgroundColor: 'var(--background)',
                border: '1px solid var(--border)',
                borderRadius: '8px'
              }}>
                <div style={{ flex: 1 }}>
                  <h4 style={{ margin: '0 0 0.5rem 0' }}>{post.title}</h4>
                  <p style={{ margin: '0', color: 'var(--muted)', fontSize: '0.9rem' }}>
                    {post.description.substring(0, 100)}{post.description.length > 100 ? '...' : ''}
                  </p>
                  <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.8rem', color: 'var(--muted)' }}>
                    Created: {new Date(post.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <Link 
                    to={`/post/${post.id}`}
                    className="button"
                    style={{ textDecoration: 'none', padding: '0.5rem 1rem' }}
                  >
                    View
                  </Link>
                  <button 
                    className="button"
                    onClick={() => handleDeletePost(post.id)}
                    style={{ backgroundColor: 'var(--error)', color: 'white' }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div style={{ marginTop: '2rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <Link 
          to="/expenses" 
          className="button"
          style={{ 
            textDecoration: 'none', 
            textAlign: 'center',
            padding: '1rem',
            backgroundColor: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: '8px'
          }}
        >
          <h3 style={{ margin: '0 0 0.5rem 0' }}>💰 Expenses</h3>
          <p style={{ margin: '0', fontSize: '0.9rem', color: 'var(--muted)' }}>Manage expenses and groups</p>
        </Link>
        
        <Link 
          to="/admin-signup" 
          className="button"
          style={{ 
            textDecoration: 'none', 
            textAlign: 'center',
            padding: '1rem',
            backgroundColor: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: '8px'
          }}
        >
          <h3 style={{ margin: '0 0 0.5rem 0' }}>👥 Add Users</h3>
          <p style={{ margin: '0', fontSize: '0.9rem', color: 'var(--muted)' }}>Create new admin or user accounts</p>
        </Link>
      </div>

      {/* Create Post Modal */}
      {showPostForm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'var(--surface)',
            padding: '2rem',
            borderRadius: '8px',
            width: '90%',
            maxWidth: '500px'
          }}>
            <h2 style={{ margin: '0 0 1rem 0' }}>Create New Post</h2>
            
            <form onSubmit={handlePostSubmit}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Title</label>
                <input
                  type="text"
                  required
                  value={postForm.title}
                  onChange={(e) => setPostForm({...postForm, title: e.target.value})}
                  style={{ 
                    width: '100%', 
                    padding: '0.5rem',
                    backgroundColor: 'var(--background)',
                    border: '1px solid var(--border)',
                    borderRadius: '4px',
                    color: 'var(--text)'
                  }}
                />
              </div>
              
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Description</label>
                <textarea
                  required
                  value={postForm.description}
                  onChange={(e) => setPostForm({...postForm, description: e.target.value})}
                  rows={4}
                  style={{ 
                    width: '100%', 
                    padding: '0.5rem',
                    backgroundColor: 'var(--background)',
                    border: '1px solid var(--border)',
                    borderRadius: '4px',
                    color: 'var(--text)',
                    resize: 'vertical'
                  }}
                />
              </div>
              
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Image (optional)</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setPostForm({...postForm, image: e.target.files[0]})}
                  style={{ 
                    width: '100%',
                    color: 'var(--text)'
                  }}
                />
              </div>
              
              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => setShowPostForm(false)}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: 'var(--background)',
                    border: '1px solid var(--border)',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: 'var(--accent)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Create Post
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
