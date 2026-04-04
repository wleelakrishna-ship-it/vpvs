import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getLikes, addLike, removeLike } from "../lib/api";

export default function ImageCard({ post, onDelete }) {
  const [likes, setLikes] = useState([]);
  const [liked, setLiked] = useState(false);
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchLikes();
    // Load saved username from localStorage
    const savedUsername = localStorage.getItem("username");
    if (savedUsername) {
      setUsername(savedUsername);
    }
  }, [post.id]);

  useEffect(() => {
    // Check if current user liked this post
    if (username && likes.length > 0) {
      const userLiked = likes.some(like => like.username === username);
      setLiked(userLiked);
    }
  }, [likes, username]);

  const fetchLikes = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/likes?postId=${post.id}`);
      const data = await response.json();
      if (response.ok) {
        setLikes(data.likes || []);
      }
    } catch (error) {
      console.error("Failed to fetch likes:", error);
    }
  };

  const handleLike = async () => {
    if (!username) {
      const inputUsername = prompt("Please enter your username to like this post:");
      if (!inputUsername) return;
      
      setUsername(inputUsername);
      localStorage.setItem("username", inputUsername);
    }

    setLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/likes`, {
        method: liked ? "DELETE" : "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          postId: post.id,
          username: username || localStorage.getItem("username"),
        }),
      });

      if (response.ok) {
        await fetchLikes();
        setLiked(!liked);
      }
    } catch (error) {
      console.error("Failed to toggle like:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <Link className="imageCardButton" to={`/post/${post.id}`}>
        <div className="imageWrap">
          <img src={post.image_url} alt={post.title} loading="lazy" />
        </div>
        <div className="imageCardBody">
          <div className="imageCardTitle">{post.title}</div>
        </div>
      </Link>

      <div className="imageCardBody" style={{ paddingTop: 0 }}>
        <div className="btnRow">
          <button 
            className={`navButton ${liked ? "likedButton" : ""}`} 
            type="button" 
            onClick={handleLike}
            disabled={loading}
          >
            {loading ? "..." : liked ? "❤️" : "🤍"} {likes.length}
          </button>
          {onDelete ? (
            <button className="navButton dangerButton" type="button" onClick={() => onDelete(post.id)}>
              Delete
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}

