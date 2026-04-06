import React from 'react';
import { Link } from 'react-router-dom';
import './PostCard.css';

export default function PostCard({ post }) {
  return (
    <div className="post-card">
      <Link to={`/post/${post.id}`} className="post-card-link">
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
          <div className="post-card-footer">
            <span className="post-card-read-more">Read More →</span>
          </div>
        </div>
      </Link>
    </div>
  );
}
