# Memory rules (sanitized)

These are the durable lessons the project's memory accumulated, with personal details removed. Seed your
project memory with them (or keep them in project instructions) so new threads don't relearn them.

## Working rules
- Every new list skips jobs already on any earlier list, matched loosely by first company word plus core title words, so reposts with "(Remote)" or "Inc" variations are still caught. Reworded reposts the loose match misses go in `config.json` `filters.skip_keys`.
- When a company rejects you, or you've already applied elsewhere, add it to `filters.exclude_companies` so future lists skip it.
- Rows are never deleted from a list. Status is appended in the Status column: `✅ Applied YYYY-MM-DD`, `✖️ Not a fit`, `⌛ Expired`, or `📄 [Resume](...), [Cover letter](...)` when documents were made.
- Synced project folders can lag. After writing a list or `followups.json`, read it back a few seconds later to confirm the write stuck.
- Dice results need an AI-search disclosure line whenever they are shown.
- Short `to.indeed.com` links expire; prefer direct employer, Dice or ZipRecruiter links.
- Some job-board connectors return titles only. When no job description is reachable, say the tailoring is based on title and company only.

## Tailoring rules
- Resume: copy the base resume and change only the headline and summary. Never invent experience, titles, metrics or skills.
- Cover letter: one page, 3-4 short paragraphs, 2-3 concrete accomplishments from the resume.
- If a job asks for something the resume doesn't show (a specific tool, certification, domain), name the gap honestly instead of papering over it.
- Same-day revisions use a `_v2` suffix rather than overwriting.

## Safety rules
- Never apply, submit an Upwork proposal, or message anyone without an explicit OK for that job.
- Gmail is read-only for the scan routine.
- Contacts: business contacts only, from the posting or a public page. Never guess an email address.

## Facts worth recording per person (keep these in your private memory, not in this repo)
- Which resume file is the current base, and what each resume variant emphasizes.
- Location rule and home-metro suburbs.
- Role types to exclude and why.
- Timezone for routines.
- Artifact URLs for the tracker and the Follow-up Board.
- Which email address(es) receive application mail.
