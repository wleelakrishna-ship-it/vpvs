import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getPostById } from "../lib/api";
import CommentSection from "../components/CommentSection.jsx";

export default function PostDetailPage() {
  const { id } = useParams();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const p = await getPostById(id);
        if (!cancelled) setPost(p);
      } catch (e) {
        if (!cancelled) setError(e.message || "Failed to load post");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [id]);

  return (
    <section>
      {loading ? <div className="smallNote">Loading…</div> : null}
      {error ? <div className="smallNote" style={{ color: "#ff9aa2" }}>{error}</div> : null}
      {!loading && post ? (
        <div className="postDetail">
          <div>
            <div className="postHero">
              <img src={post.image_url} alt={post.title} />
            </div>
          </div>
          <div>
            <div className="sectionTitle" style={{ marginTop: 0 }}>
              {post.title}
            </div>
            <div className="smallNote">
              {post.created_at ? new Date(post.created_at).toLocaleString() : ""}
            </div>
            <div style={{ marginTop: 12, color: "var(--text)", lineHeight: 1.6, whiteSpace: "pre-wrap" }}>
              {post.description}
            </div>
          </div>

          <div style={{ gridColumn: "1 / -1" }}>
            <CommentSection postId={id} />
          </div>
        </div>
      ) : null}
    </section>
  );
}

