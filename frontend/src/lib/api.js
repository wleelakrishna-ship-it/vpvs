const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

function getAuthHeaders(token) {
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

async function expectJson(res) {
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return { raw: text };
  }
}

export async function getPosts() {
  const res = await fetch(`${API_BASE_URL}/api/posts`);
  const json = await expectJson(res);
  if (!res.ok) throw new Error(json?.error || "Failed to fetch posts");
  return json.posts || [];
}

export async function getPostById(id) {
  const res = await fetch(`${API_BASE_URL}/api/posts/${encodeURIComponent(id)}`);
  const json = await expectJson(res);
  if (!res.ok) throw new Error(json?.error || "Failed to fetch post");
  return json.post;
}

export async function createPost({ title, description, imageFile, token }) {
  const form = new FormData();
  form.append("title", title);
  form.append("description", description || "");
  form.append("image", imageFile); // field name used by multipart parser

  const res = await fetch(`${API_BASE_URL}/api/posts`, {
    method: "POST",
    headers: {
      ...getAuthHeaders(token),
      // Don't set Content-Type manually; browser will add proper multipart boundary.
    },
    body: form,
  });
  const json = await expectJson(res);
  if (!res.ok) throw new Error(json?.error || "Failed to create post");
  return json.post;
}

export async function deletePost(id, token) {
  const res = await fetch(`${API_BASE_URL}/api/posts/${encodeURIComponent(id)}`, {
    method: "DELETE",
    headers: {
      ...getAuthHeaders(token),
    },
  });
  const json = await expectJson(res);
  if (!res.ok) throw new Error(json?.error || "Failed to delete post");
  return json;
}

export async function getComments(postId) {
  const res = await fetch(
    `${API_BASE_URL}/api/comments?postId=${encodeURIComponent(postId)}`,
  );
  const json = await expectJson(res);
  if (!res.ok) throw new Error(json?.error || "Failed to fetch comments");
  return json.comments || [];
}

export async function addComment({ postId, username, comment }) {
  const res = await fetch(`${API_BASE_URL}/api/comments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ postId, username, comment }),
  });
  const json = await expectJson(res);
  if (!res.ok) throw new Error(json?.error || "Failed to add comment");
  return json.comment;
}

export async function getLikes(postId) {
  const res = await fetch(
    `${API_BASE_URL}/api/likes?postId=${encodeURIComponent(postId)}`,
  );
  const json = await expectJson(res);
  if (!res.ok) throw new Error(json?.error || "Failed to fetch likes");
  return json.likes || [];
}

export async function addLike({ postId, username }) {
  const res = await fetch(`${API_BASE_URL}/api/likes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ postId, username }),
  });
  const json = await expectJson(res);
  if (!res.ok) throw new Error(json?.error || "Failed to add like");
  return json.like;
}

export async function removeLike({ postId, username }) {
  const res = await fetch(`${API_BASE_URL}/api/likes`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ postId, username }),
  });
  const json = await expectJson(res);
  if (!res.ok) throw new Error(json?.error || "Failed to remove like");
  return json;
}

