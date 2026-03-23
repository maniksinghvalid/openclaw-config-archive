#!/usr/bin/env node
import fetch from 'node-fetch';
import { loadEnv } from './load-env';
loadEnv();
const args = process.argv.slice(2);
const command = args[0] || 'search';
function getOpt(name:string):string|undefined{ const i=args.indexOf(`--${name}`); if(i>=0 && i+1<args.length) return args[i+1]; return undefined; }
function getFlag(name:string):boolean{ return args.includes(`--${name}`); }
const queryParts = args.filter(a=>!a.startsWith('--') && a!==command);
let query = queryParts.join(' ');
if(!query) query = 'AI';
const limit = parseInt(getOpt('limit')||'3');
const since = getOpt('since') || '7d';
const url = `https://api.x.com/2/tweets/search/recent?query=${encodeURIComponent(query)}&max_results=${Math.min(limit,100)}&tweet.fields=created_at,public_metrics,author_id&expansions=author_id&user.fields=username,name`; 
const token = process.env.X_BEARER_TOKEN;
(async ()=>{
  if(!token){ console.error('No X_BEARER_TOKEN found'); process.exit(1);} 
  const headers={'Authorization': `Bearer ${token}`};
  const finalUrl = since==='24h' ? url+'' : url; // keep simple
  const res = await fetch(finalUrl,{headers});
  if(!res.ok){ const text= await res.text(); console.error('API error', res.status, text); process.exit(1);} 
  const raw = await res.json();
  const arr = (raw.data||[]).slice(0, limit);
  for(const t of arr){ const u = raw.includes?.users?.find((x:any)=>x.id===t.author_id) || {}; const name = u.name || u.username || ''; const turl = `https://x.com/${u.username||name}/status/${t.id}`; console.log(`- @${u.username||name} ${t.text} (${t.created_at}) ${turl}`);
  }
})();
