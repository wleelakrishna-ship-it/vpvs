import { createClient } from "@supabase/supabase-js";

export function createSupabaseBrowserClient({ persistSession = false } = {}) {
  const url = import.meta.env.VITE_SUPABASE_URL;
  const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;
  if (!url || !anonKey) {
    throw new Error("Missing VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY");
  }

  return createClient(url, anonKey, {
    auth: { persistSession },
  });
}

