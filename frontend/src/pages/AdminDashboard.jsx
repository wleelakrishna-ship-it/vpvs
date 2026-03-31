import React, { useEffect, useState } from "react";
import { useAdminAuth } from "../state/AdminAuthContext.jsx";
import { deletePost, getPosts } from "../lib/api";
import ImageCard from "../components/ImageCard.jsx";
import UploadForm from "../components/UploadForm.jsx";

export default function AdminDashboard() {
  const { token, logout } = useAdminAuth();
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
      setError(e.message || "Failed to load posts");
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

    setError(null);
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
        Admin Dashboard
      </div>
      <div className="smallNote" style={{ marginBottom: 12 }}>
        Upload images to create posts. Delete posts from the feed below.
        <div style={{ marginTop: 6 }}>
          <button className="navButton" type="button" onClick={logout}>
            Logout
          </button>
        </div>
      </div>

      <UploadForm onCreated={refresh} />

      <div className="sectionTitle">All posts</div>
      {error ? <div className="smallNote" style={{ color: "#ff9aa2" }}>{error}</div> : null}
      {loading ? <div className="smallNote">Loading…</div> : null}

      <div className="grid" aria-busy={loading}>
        {posts.map((post) => (
          <ImageCard key={post.id} post={post} onDelete={handleDelete} />
        ))}
      </div>
    </section>
  );
}

