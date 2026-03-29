// Auto-load .env for X bearer token
export function loadEnv(): void {
  try {
    // Dynamically require to avoid hard dependency at build time
    const path = require('path');
    const dotenv = require('dotenv');
    const envPath = path.resolve(__dirname, '.env');
    dotenv.config({ path: envPath });
    // Merge into process.env
    process.env = { ...process.env, ...(dotenv.config({ path: envPath }).parsed || {}) } as any;
  } catch {
    // If dotenv isn't available, silently ignore; user can configure manually.
  }
}
