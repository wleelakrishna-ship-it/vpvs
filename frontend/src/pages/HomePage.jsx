import React, { useEffect, useState } from "react";
import { useAdminAuth } from "../state/AdminAuthContext.jsx";
import { deletePost, getPosts } from "../lib/api";
import ImageCard from "../components/ImageCard.jsx";

export default function HomePage() {
  const { token } = useAdminAuth();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const next = await getPosts();
      setPosts(next);
    } catch (e) {
      setError(e.message || "Failed to load feed");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleDelete(postId) {
    if (!token) return;
    const ok = window.confirm("Delete this post? This cannot be undone.");
    if (!ok) return;

    try {
      await deletePost(postId, token);
      await refresh();
    } catch (e) {
      setError(e.message || "Failed to delete post");
    }
  }

  return (
    <section>
      <div className="sectionTitle" style={{ marginTop: 0 }}>
        Photo Feed
      </div>

      {error ? <div className="smallNote" style={{ color: "#ff9aa2" }}>{error}</div> : null}
      {loading ? <div className="smallNote">Loading…</div> : null}

      <div className="grid" aria-busy={loading}>
        {posts.map((post) => (
          <ImageCard key={post.id} post={post} onDelete={token ? handleDelete : null} />
        ))}
      </div>
    </section>
  );
}

