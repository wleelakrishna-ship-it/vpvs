import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../lib/universalApiClient.js';
import './PostCard.css';

export default function PostCard({ post, currentUser, onDelete }) {
  const [likes, setLikes] = useState(post.likes || 0);
  const [comments, setComments] = useState(post.comments || []);
  const [showComments, setShowComments] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [liked, setLiked] = useState(false);

  const handleLike = async () => {
    try {
      if (liked) {
        await apiClient.unlikePost(post.id);
        setLikes(prev => prev - 1);
      } else {
        await apiClient.likePost(post.id);
        setLikes(prev => prev + 1);
      }
      setLiked(!liked);
    } catch (err) {
      console.error('Failed to toggle like:', err);
    }
  };

  const handleComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      const comment = await apiClient.addComment(post.id, {
        content: newComment,
        username: currentUser?.username || 'Anonymous'
      });
      setComments(prev => [...prev, comment]);
      setNewComment('');
    } catch (err) {
      console.error('Failed to add comment:', err);
    }
  };

  return (
    <div className="post-card">
      <div className="post-card-image">
        <img 
          src={post.image_url || `https://picsum.photos/seed/${post.id}/400/300.jpg`}
          alt={post.title}
          onError={(e) => {
            e.target.src = `https://picsum.photos/seed/fallback-${post.id}/400/300.jpg`;
          }}
        />
        <div className="post-card-overlay">
          <span className="post-card-date">
            {new Date(post.created_at).toLocaleDateString()}
          </span>
          {currentUser?.is_admin && (
            <button
              onClick={(e) => {
                e.preventDefault();
                onDelete(post.id);
              }}
              className="post-card-delete-btn"
              title="Delete post"
            >
              🗑️
            </button>
          )}
        </div>
      </div>
      
      <div className="post-card-content">
        <h3 className="post-card-title">{post.title}</h3>
        <p className="post-card-description">
          {post.description.length > 120 
            ? `${post.description.substring(0, 120)}...` 
            : post.description
          }
        </p>
        
        {/* Interaction Section */}
        <div className="post-card-interactions">
          <div className="post-card-actions">
            <button 
              onClick={handleLike}
              className={`post-card-like-btn ${liked ? 'liked' : ''}`}
            >
              ❤️ {likes}
            </button>
            <button 
              onClick={() => setShowComments(!showComments)}
              className="post-card-comment-btn"
            >
              💬 {comments.length}
            </button>
          </div>
          
          <Link to={`/post/${post.id}`} className="post-card-read-more">
            Read More →
          </Link>
        </div>

        {/* Comments Section */}
        {showComments && (
          <div className="post-card-comments">
            <div className="comments-list">
              {comments.map((comment, index) => (
                <div key={index} className="comment-item">
                  <strong>{comment.username}:</strong> {comment.content}
                </div>
              ))}
            </div>
            
            {currentUser && (
              <form onSubmit={handleComment} className="comment-form">
                <input
                  type="text"
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Add a comment..."
                  className="comment-input"
                />
                <button type="submit" className="comment-submit">
                  Post
                </button>
              </form>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
