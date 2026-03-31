import React, { useState } from "react";
import { useAdminAuth } from "../state/AdminAuthContext.jsx";
import { createPost } from "../lib/api";

export default function UploadForm({ onCreated }) {
  const { token } = useAdminAuth();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    if (!file) {
      setError("Please select an image.");
      return;
    }

    try {
      setLoading(true);
      await createPost({ title, description, imageFile: file, token });
      setTitle("");
      setDescription("");
      setFile(null);
      if (onCreated) onCreated();
    } catch (err) {
      setError(err.message || "Failed to upload post");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="form">
      <div className="sectionTitle" style={{ marginTop: 0 }}>
        Create a post
      </div>
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="title">Title</label>
          <input
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            maxLength={200}
          />
        </div>
        <div className="field">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional details…"
          />
        </div>
        <div className="field">
          <label htmlFor="image">Image</label>
          <input
            id="image"
            type="file"
            accept="image/*"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            required
          />
        </div>
        {error ? <div className="smallNote" style={{ color: "#ff9aa2" }}>{error}</div> : null}
        <div className="btnRow">
          <button className="navButton primaryButton" type="submit" disabled={loading}>
            {loading ? "Uploading…" : "Upload"}
          </button>
        </div>
      </form>
    </section>
  );
}

