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

  return (
    <div className="page" style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
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
            <Link
              to="/admin"
              style={{
                display: 'inline-block',
                padding: '0.75rem 1.5rem',
                background: 'var(--accent)',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '8px',
                fontWeight: '500'
              }}
            >
              Create First Post
            </Link>
          )}
        </div>
      )}

      {/* Posts */}
      {!loading && posts.length > 0 && (
        <div className="posts-grid">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  );
}

