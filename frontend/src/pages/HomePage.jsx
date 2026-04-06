import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiClient from "../lib/universalApiClient.js";
import PostCard from "../components/PostCard.jsx";
import "./HomePage.css";

export default function HomePage() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [showPostForm, setShowPostForm] = useState(false);
  const [postForm, setPostForm] = useState({
    title: "",
    description: "",
    image_url: ""
  });

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getPosts();
      setPosts(data.posts || []);
    } catch (e) {
      setError(e.message || "Failed to load feed");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // Get current user
    const user = localStorage.getItem("currentUser");
    if (user) {
      setCurrentUser(JSON.parse(user));
    }
    
    refresh();
  }, []);

  const handleCreatePost = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await apiClient.createPost(postForm);
      setPostForm({ title: "", description: "", image_url: "" });
      setShowPostForm(false);
      await refresh();
    } catch (err) {
      setError(err.message || "Failed to create post");
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePost = async (postId) => {
    if (!window.confirm("Are you sure you want to delete this post?")) {
      return;
    }

    try {
      await apiClient.deletePost(postId);
      await refresh();
    } catch (err) {
      setError(err.message || "Failed to delete post");
    }
  };

  return (
    <div className="page" style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
      {/* Header */}
      <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ 
            fontSize: '2.5rem', 
            margin: '0 0 0.5rem 0', 
            color: 'var(--text)',
            fontWeight: '700'
          }}>
            Photo Feed
          </h1>
          <p style={{ color: 'var(--muted)', margin: 0 }}>
            Discover amazing photos and stories from our community
          </p>
        </div>
        
        {currentUser?.is_admin && (
          <button
            onClick={() => setShowPostForm(!showPostForm)}
            style={{
              padding: '0.75rem 1.5rem',
              background: 'var(--accent)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontWeight: '500',
              cursor: 'pointer'
            }}
          >
            {showPostForm ? 'Cancel' : 'Create Post'}
          </button>
        )}
      </div>

      {/* Post Creation Form */}
      {showPostForm && currentUser?.is_admin && (
        <div style={{ 
          background: 'var(--card)', 
          padding: '1.5rem', 
          borderRadius: '8px', 
          marginBottom: '2rem' 
        }}>
          <h3 style={{ color: 'var(--text)', marginBottom: '1rem' }}>Create New Post</h3>
          <form onSubmit={handleCreatePost} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label htmlFor="title" style={{ fontWeight: '600', color: 'var(--text)' }}>Title</label>
              <input
                type="text"
                id="title"
                value={postForm.title}
                onChange={(e) => setPostForm({ ...postForm, title: e.target.value })}
                required
                style={{
                  padding: '0.5rem',
                  border: '1px solid var(--border)',
                  borderRadius: '4px',
                  background: 'var(--bg)',
                  color: 'var(--text)'
                }}
              />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label htmlFor="description" style={{ fontWeight: '600', color: 'var(--text)' }}>Description</label>
              <textarea
                id="description"
                value={postForm.description}
                onChange={(e) => setPostForm({ ...postForm, description: e.target.value })}
                required
                rows="3"
                style={{
                  padding: '0.5rem',
                  border: '1px solid var(--border)',
                  borderRadius: '4px',
                  background: 'var(--bg)',
                  color: 'var(--text)',
                  resize: 'vertical'
                }}
              />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label htmlFor="image_url" style={{ fontWeight: '600', color: 'var(--text)' }}>Image URL</label>
              <input
                type="url"
                id="image_url"
                value={postForm.image_url}
                onChange={(e) => setPostForm({ ...postForm, image_url: e.target.value })}
                placeholder="https://picsum.photos/seed/example/400/300.jpg"
                required
                style={{
                  padding: '0.5rem',
                  border: '1px solid var(--border)',
                  borderRadius: '4px',
                  background: 'var(--bg)',
                  color: 'var(--text)'
                }}
              />
            </div>
            <button
              type="submit"
              style={{
                padding: '0.75rem 1.5rem',
                border: 'none',
                borderRadius: '6px',
                background: 'var(--accent)',
                color: 'var(--bg)',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              Create Post
            </button>
          </form>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '8px',
          padding: '1rem',
          marginBottom: '2rem',
          color: '#ef4444'
        }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '60vh',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '3px solid var(--border)',
            borderTop: '3px solid var(--accent)',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }}></div>
          <p style={{ color: 'var(--muted)' }}>Loading posts...</p>
        </div>
      )}

      {/* Posts Grid */}
      {!loading && posts.length === 0 && !error && (
        <div style={{ 
          textAlign: 'center', 
          padding: '4rem 2rem',
          color: 'var(--muted)'
        }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📸</div>
          <h2 style={{ margin: '0 0 1rem 0', color: 'var(--text)' }}>No posts yet</h2>
          <p style={{ margin: '0 0 2rem 0' }}>
            Be the first to share a photo with the community!
          </p>
          {currentUser?.is_admin && (
            <button
              onClick={() => setShowPostForm(true)}
              style={{
                display: 'inline-block',
                padding: '0.75rem 1.5rem',
                background: 'var(--accent)',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '8px',
                fontWeight: '500',
                border: 'none',
                cursor: 'pointer'
              }}
            >
              Create First Post
            </button>
          )}
        </div>
      )}

      {/* Posts */}
      {!loading && posts.length > 0 && (
        <div className="posts-grid">
          {posts.map((post) => (
            <PostCard 
              key={post.id} 
              post={post} 
              currentUser={currentUser}
              onDelete={handleDeletePost}
            />
          ))}
        </div>
      )}
    </div>
  );
}

