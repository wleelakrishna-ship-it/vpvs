import React, { useEffect, useState } from "react";
import { addComment, getComments } from "../lib/api";

export default function CommentSection({ postId }) {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [username, setUsername] = useState("");
  const [comment, setComment] = useState("");
  const [error, setError] = useState(null);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const next = await getComments(postId);
      setComments(next);
    } catch (e) {
      setError(e.message || "Failed to load comments");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!postId) return;
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [postId]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    try {
      await addComment({
        postId,
        username: username.trim(),
        comment: comment.trim(),
      });
      setUsername("");
      setComment("");
      await refresh();
    } catch (err) {
      setError(err.message || "Failed to add comment");
    }
  }

  return (
    <section>
      <div className="sectionTitle">Comments</div>

      <form className="form" onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="username">Username</label>
          <input
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="e.g. ali_123"
            required
          />
        </div>
        <div className="field">
          <label htmlFor="comment">Comment</label>
          <textarea
            id="comment"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Write something…"
            required
          />
        </div>
        {error ? <div className="smallNote" style={{ color: "#ff9aa2" }}>{error}</div> : null}
        <div className="btnRow">
          <button className="navButton primaryButton" type="submit" disabled={loading}>
            {loading ? "Posting…" : "Post comment"}
          </button>
        </div>
      </form>

      <div className="sectionTitle" style={{ marginTop: 22 }}>
        {loading ? "Loading…" : `All comments (${comments.length})`}
      </div>

      {error && !loading ? (
        <div className="smallNote" style={{ color: "#ff9aa2" }}>
          {error}
        </div>
      ) : null}

      <div style={{ display: "grid", gap: 12 }}>
        {comments.map((c) => (
          <div key={c.id} className="comment">
            <div className="commentHeader">
              <div className="commentUser">{c.username}</div>
              <div className="commentTime">
                {c.created_at ? new Date(c.created_at).toLocaleString() : ""}
              </div>
            </div>
            <div className="commentText">{c.comment}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

