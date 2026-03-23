#!/usr/bin/env -S /home/claw/.bun/bin/bun run
/**
 * x-search — Live CLI for X/Twitter research.
 * Auto-loads .env for X_BEARER_TOKEN.
 */

import { loadEnv } from "./load-env";
loadEnv();

import * as api from "./lib/api";

const args = process.argv.slice(2);
const command = args[0];

function getFlag(name: string): boolean {
  const idx = args.indexOf(`--${name}`);
  if (idx >= 0) { args.splice(idx, 1); return true; }
  return false;
}

function getOpt(name: string): string | undefined {
  const idx = args.indexOf(`--${name}`);
  if (idx >= 0 && idx + 1 < args.length) {
    const val = args[idx + 1];
    args.splice(idx, 2);
    return val;
  }
  return undefined;
}

function compactNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 60) return `${mins}m`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h`;
  const days = Math.floor(hours / 24);
  return `${days}d`;
}

function formatTweet(t: api.Tweet, index?: number): string {
  const prefix = index !== undefined ? `${index + 1}. ` : "";
  const engagement = `${compactNumber(t.metrics.likes)}❤️ ${compactNumber(t.metrics.retweets)}🔁 ${compactNumber(t.metrics.impressions)}👁`;
  const time = timeAgo(t.created_at);
  const cleanText = t.text.replace(/https:\/\/t\.co\/\S+/g, "").trim();
  const truncated = cleanText.length > 280 ? cleanText.slice(0, 277) + "..." : cleanText;
  let out = `${prefix}@${t.username} (${engagement} · ${time})\n${truncated}`;
  if (t.urls.length > 0) out += `\n🔗 ${t.urls[0]}`;
  out += `\n${t.tweet_url}`;
  return out;
}

async function cmdSearch() {
  const quick = getFlag("quick");
  const quality = getFlag("quality");
  const fromUser = getOpt("from");
  const sortOpt = getOpt("sort") || "likes";
  const minLikes = parseInt(getOpt("min-likes") || "0");
  let pages = Math.min(parseInt(getOpt("pages") || "1"), 5);
  let displayLimit = parseInt(getOpt("limit") || "15");
  const since = getOpt("since");
  const noReplies = getFlag("no-replies");
  const asJson = getFlag("json");

  if (quick) { pages = 1; displayLimit = Math.min(displayLimit, 10); }

  const queryParts = args.slice(1).filter((a) => !a.startsWith("--"));
  let query = queryParts.join(" ");
  if (!query) { console.error("Usage: x-search.ts search <query> [options]"); process.exit(1); }

  if (fromUser && !query.toLowerCase().includes("from:")) {
    query += ` from:${fromUser.replace(/^@/, "")}`;
  }
  if (!query.includes("is:retweet")) query += " -is:retweet";
  if ((quick || noReplies) && !query.includes("is:reply")) query += " -is:reply";

  let tweets = await api.search(query, {
    pages,
    sortOrder: sortOpt === "recent" ? "recency" : "relevancy",
    since: since || undefined,
  });

  if (minLikes > 0) tweets = api.filterEngagement(tweets, { minLikes });
  if (quality) tweets = api.filterEngagement(tweets, { minLikes: 10 });
  if (sortOpt !== "recent") tweets = api.sortBy(tweets, sortOpt as any);
  tweets = api.dedupe(tweets);

  if (asJson) {
    console.log(JSON.stringify(tweets.slice(0, displayLimit), null, 2));
  } else {
    const shown = tweets.slice(0, displayLimit);
    if (shown.length === 0) {
      console.log(`No results found for "${query}".`);
    } else {
      console.log(`🔍 "${query}" — ${tweets.length} results\n`);
      console.log(shown.map((t, i) => formatTweet(t, i)).join("\n\n"));
      if (tweets.length > displayLimit) console.log(`\n... +${tweets.length - displayLimit} more`);
    }
  }

  const cost = (tweets.length * 0.005).toFixed(2);
  console.error(`\n📊 ${tweets.length} tweets read · est. cost ~$${cost}`);
}

async function main() {
  switch (command) {
    case "search":
    case "s":
      await cmdSearch();
      break;
    default:
      console.log("Usage: x-search.ts search <query> [options]");
  }
}

main().catch((e) => { console.error(`Error: ${e.message}`); process.exit(1); });
