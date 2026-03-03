// file: frontend/src/utils/supabaseFlow.ts
// Matrx Flow Supabase client — uses automation-matrix as the auth provider
import { createClient, SupabaseClient } from "@supabase/supabase-js";
import supabase from "./supabase"; // your existing automation-matrix client

const flowUrl = import.meta.env.VITE_MATRX_FLOW_SUPABASE_URL;
const flowKey = import.meta.env.VITE_MATRX_FLOW_SUPABASE_PUBLISHABLE_KEY;

const supabaseFlow: SupabaseClient = createClient(flowUrl, flowKey, {
  accessToken: async () => {
    // Get the current session from automation-matrix (your primary auth)
    const {
      data: { session },
    } = await supabase.auth.getSession();
    return session?.access_token ?? "";
  },
});

// Call once on login / app init to ensure user_profile exists in Matrx Flow.
// Idempotent — safe to call every time.
export async function provisionFlowUser(): Promise<void> {
  const { error } = await supabaseFlow.functions.invoke("provision-user", {
    method: "POST",
  });
  if (error) {
    console.error("Failed to provision Matrx Flow user profile:", error);
  }
}

export default supabaseFlow;
