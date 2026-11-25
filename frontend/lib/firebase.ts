import { getApps, initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const cfg = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY, authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID, appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};
export const authEnabled = !!cfg.apiKey;
export const auth = authEnabled ? getAuth(getApps()[0] ?? initializeApp(cfg)) : null;

/** ID token for the signed-in user, or null (demo mode / signed out). */
export async function getToken(): Promise<string | null> {
  if (!auth) return null;
  await auth.authStateReady();
  return auth.currentUser ? auth.currentUser.getIdToken() : null;
}
