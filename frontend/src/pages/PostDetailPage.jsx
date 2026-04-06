import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiClient from "../lib/apiClient.js";

export default function PostDetailPage() {
  const { id } = useParams();
  const [post, setPost] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [comments, setComments] = useState([]);
  const [likes, setLikes] = useState([]);
  const [newComment, setNewComment] = useState("");
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    // Get current user
    const user = localStorage.getItem("currentUser");
    if (user) {
      setCurrentUser(JSON.parse(user));
    }
    
    loadPost();
    loadPosts();
  }, [id]);

  const loadPost = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getPosts();
      const foundPost = data.posts?.find(p => p.id === id);
      if (foundPost) {
        setPost(foundPost);
      } else {
        setError("Post not found");
      }
    } catch (e) {
      setError(e.message || "Failed to load post");
    } finally {
      setLoading(false);
    }
  };

  const loadPosts = async () => {
    try {
      const data = await apiClient.getPosts();
      setPosts(data.posts || []);
    } catch (e) {
      console.error("Failed to load posts:", e);
    }
  };

  const handleComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim() || !currentUser) return;

    try {
      const comment = {
        post_id: id,
        username: currentUser.username,
        content: newComment.trim()
      };
      
      // For now, just add to local state
      setComments([...comments, {
        ...comment,
        created_at: new Date().toISOString()
      }]);
      setNewComment("");
    } catch (error) {
      console.error("Failed to add comment:", error);
    }
  };

  const handleLike = async () => {
    if (!currentUser) return;

    try {
      const like = {
        post_id: id,
        username: currentUser.username
      };
      
      // Toggle like
      const isLiked = likes.some(l => l.username === currentUser.username);
      if (isLiked) {
        setLikes(likes.filter(l => l.username !== currentUser.username));
      } else {
        setLikes([...likes, {
          ...like,
          created_at: new Date().toISOString()
        }]);
      }
    } catch (error) {
      console.error("Failed to toggle like:", error);
    }
  };

  return (
    <div className="page" style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
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
          <p style={{ color: 'var(--muted)' }}>Loading post...</p>
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

      {/* Post Content */}
      {!loading && post && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Back Navigation */}
          <Link 
            to="/"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              color: 'var(--accent)',
              textDecoration: 'none',
              fontWeight: '500'
            }}
          >
            ← Back to Posts
          </Link>

          {/* Post Header */}
          <div style={{ 
            background: 'var(--surface)', 
            borderRadius: '12px', 
            overflow: 'hidden',
            border: '1px solid var(--border)'
          }}>
            {/* Post Image */}
            {post.image_url && (
              <div style={{ width: '100%', maxHeight: '400px', overflow: 'hidden' }}>
                <img 
                  src={post.image_url} 
                  alt={post.title}
                  style={{ 
                    width: '100%', 
                    height: 'auto', 
                    objectFit: 'cover',
                    display: 'block'
                  }}
                  onError={(e) => {
                    e.target.src = `https://via.placeholder.com/400x300.png?text=${encodeURIComponent(post.title)}`;
                  }}
                />
              </div>
            )}

            {/* Post Content */}
            <div style={{ padding: '2rem' }}>
              <h1 style={{ 
                fontSize: '2rem', 
                margin: '0 0 1rem 0', 
                color: 'var(--text)',
                fontWeight: '700'
              }}>
                {post.title}
              </h1>
              
              <div style={{ 
                color: 'var(--muted)', 
                fontSize: '0.9rem',
                marginBottom: '1.5rem'
              }}>
                {post.created_at ? new Date(post.created_at).toLocaleDateString() : ""}
              </div>
              
              <div style={{ 
                color: 'var(--text)', 
                lineHeight: 1.7,
                fontSize: '1.1rem',
                whiteSpace: 'pre-wrap'
              }}>
                {post.description}
              </div>
            </div>
          </div>

          {/* Engagement Section */}
          <div style={{ 
            background: 'var(--surface)', 
            borderRadius: '12px', 
            padding: '1.5rem',
            border: '1px solid var(--border)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '2rem', marginBottom: '1.5rem' }}>
              {/* Like Button */}
              <button
                onClick={handleLike}
                disabled={!currentUser}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.5rem 1rem',
                  borderRadius: '8px',
                  border: likes.some(l => l.username === currentUser?.username) ? 'none' : '1px solid var(--border)',
                  background: likes.some(l => l.username === currentUser?.username) ? 'var(--accent)' : 'var(--background)',
                  color: likes.some(l => l.username === currentUser?.username) ? 'white' : 'var(--text)',
                  cursor: currentUser ? 'pointer' : 'not-allowed',
                  fontSize: '0.9rem',
                  fontWeight: '500'
                }}
              >
                {likes.some(l => l.username === currentUser?.username) ? '❤️' : '🤍'} 
                {likes.length} {likes.length === 1 ? 'Like' : 'Likes'}
              </button>

              {/* Comment Count */}
              <div style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>
                💬 {comments.length} {comments.length === 1 ? 'Comment' : 'Comments'}
              </div>
            </div>

            {/* Comment Form */}
            {currentUser && (
              <form onSubmit={handleComment} style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <input
                    type="text"
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Add a comment..."
                    style={{
                      flex: 1,
                      padding: '0.75rem',
                      borderRadius: '8px',
                      border: '1px solid var(--border)',
                      background: 'var(--background)',
                      color: 'var(--text)',
                      fontSize: '0.9rem'
                    }}
                  />
                  <button
                    type="submit"
                    disabled={!newComment.trim()}
                    style={{
                      padding: '0.75rem 1.5rem',
                      borderRadius: '8px',
                      border: 'none',
                      background: newComment.trim() ? 'var(--accent)' : 'var(--border)',
                      color: newComment.trim() ? 'white' : 'var(--muted)',
                      cursor: newComment.trim() ? 'pointer' : 'not-allowed',
                      fontWeight: '500'
                    }}
                  >
                    Post
                  </button>
                </div>
              </form>
            )}

            {/* Comments List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {comments.length === 0 ? (
                <div style={{ 
                  textAlign: 'center', 
                  color: 'var(--muted)', 
                  padding: '2rem',
                  fontStyle: 'italic'
                }}>
                  No comments yet. Be the first to comment!
                </div>
              ) : (
                comments.map((comment, index) => (
                  <div 
                    key={index}
                    style={{
                      padding: '1rem',
                      borderRadius: '8px',
                      background: 'var(--background)',
                      border: '1px solid var(--border)'
                    }}
                  >
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      marginBottom: '0.5rem'
                    }}>
                      <strong style={{ color: 'var(--text)' }}>{comment.username}</strong>
                      <span style={{ color: 'var(--muted)', fontSize: '0.8rem' }}>
                        {new Date(comment.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div style={{ color: 'var(--text)', lineHeight: 1.5 }}>
                      {comment.content}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

