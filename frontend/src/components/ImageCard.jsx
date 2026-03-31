import React from "react";
import { Link } from "react-router-dom";

export default function ImageCard({ post, onDelete }) {
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

      {onDelete ? (
        <div className="imageCardBody" style={{ paddingTop: 0 }}>
          <div className="btnRow">
            <button className="navButton dangerButton" type="button" onClick={() => onDelete(post.id)}>
              Delete
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}

