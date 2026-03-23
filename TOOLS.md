# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

## Active Capabilities

### YouTube Transcripts
- **Skill:** `skills/youtube-transcript/`
- **Usage:** Can fetch and summarize any YouTube video with captions
- **API:** RapidAPI (configured)

### Markdown Search (qmd)
- **Skill:** `skills/qmd-skill/`
- **Usage:** Local BM25 + vector search for markdown notes/docs
- **Status:** ✅ Fully installed and ready
- **Version:** qmd 1.0.0, Bun 1.3.9
- **Index:** `~/.cache/qmd/index.sqlite`
- **Collections:** 
  - `workspace` → 13 files indexed (AGENTS.md, SOUL.md, IDENTITY.md, TOOLS.md, skills, etc.)
- **Search modes:**
  - `qmd search` → fast keyword (BM25) ⚡ default
  - `qmd vsearch` → semantic similarity (requires `qmd embed` first)
- **Auto-update:** Run `qmd update` periodically to keep index fresh

---

Add whatever helps you do your job. This is your cheat sheet.
