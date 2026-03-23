# SESSION INITIALIZATION RULES

## On Every Session Start

### 1. Load ONLY These Files:
- `SOUL.md` - Who I am
- `USER.md` - Who you are  
- `IDENTITY.md` - My identity
- `memory/YYYY-MM-DD.md` - Today's notes (if exists)

### 2. DO NOT Auto-Load:
- ❌ `MEMORY.md` (long-term memory - load on demand only)
- ❌ Session history
- ❌ Prior messages
- ❌ Previous tool outputs

### 3. When User Asks About Prior Context:
- Use `memory_search()` to find relevant snippets
- Pull only the needed lines with `memory_get()`
- **Don't load the whole file**

### 4. Update Daily Memory at End of Session:
Save to `memory/YYYY-MM-DD.md`:
- What you worked on
- Decisions made
- Leads generated
- Blockers encountered
- Next steps

---

**Why This Matters:**
Prevents token bloat (like the 160k token issue that caused rate limiting).
Keep context lean, search memory on demand.

**Last Updated:** 2026-02-15
