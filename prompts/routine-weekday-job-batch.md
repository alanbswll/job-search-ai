# Routine: weekday job batch

**Schedule:** weekdays at 8:00 AM in your timezone, e.g. `CRON_TZ=America/New_York 0 8 * * 1-5`.
**Where it posts:** a dedicated "Weekday job batch" thread in your Claude project.

Replace every `{{...}}` with your values from `config.json` before saving the routine. Paths assume the
scripts were uploaded to the project's files under `job-leads/` (see the README).

---

```text
Scheduled weekday run: use the job-batch skill's search and ranking approach for {{NAME}}, with these rules.

Do NOT create any tailored resumes or cover letters; {{NAME}} will ask for specific ones by number later.

Do NOT include roles matching these title keywords: {{EXCLUDED_TITLE_KEYWORDS, e.g. "Solution/Enterprise/Principal/Technical Architect"}}. Focus on {{SEARCH_FOCUS, e.g. "engineering leadership (manager, senior manager, director, head of, VP, fractional/interim engineering leadership, delivery/program leadership)"}}.

LOCATION RULE: keep remote jobs (including "remote optional") and on-site or hybrid jobs in the {{HOME_METRO}} area ({{METRO_KEYWORDS}}). Drop every on-site or hybrid job outside that area; the merge script's location filter (config.json "location") enforces this.

SOURCES: ZipRecruiter, plus Indeed, Dice and Upwork whenever their connector tools are available (check with ToolSearch for "indeed", "dice" and "upwork"). Run the fractional/contract and full-time queries on every available source, with several query variations and pages, so there is a large pool. Save each source's results as a JSON list in <out_dir>/merge/ (zip.json, indeed.json, dice.json, upwork.json) with fields: source, company, title, loc, pay, posted, url, score (1-10 fit), why (one line), cat ("F" fractional/contract or "T" full-time), easy_apply.

UPWORK: use it mainly for the fractional/contract category; label rows Source "Upwork" and put budget/rate in Pay; same filters as above. Never submit an Upwork proposal or application; {{NAME}} must OK a specific job first.

DICE: record the easyApply flag (merge.py marks those rows "⚡ Easy apply").

MERGE: run `python3 /mnt/project-files/job-leads/tracker/merge.py` (dedupes by company + title ignoring suffixes like Inc/LLC/Ltd/Corp, skips jobs already in earlier lists in /mnt/project-files/job-leads/, ranks each category by fit to {{BASE_RESUME_PATH}} and keeps at most the top 50: fractional/contract numbered 1-50, full-time 51-100; fewer if fewer good matches exist, never pad with poor fits). Prefer direct employer or Dice/ZipRecruiter links over short to.indeed.com links, which can expire. If Indeed, Dice or Upwork is not connected, say so in one line and carry on. The list is saved as /mnt/project-files/job-leads/YYYYMMDD_Job_Leads_Top100.md.

HR CONTACTS: for every job on today's list, find the best public contact for a follow-up email. Preference: (1) a recruiter or hiring contact named in the posting itself; (2) a named recruiter, talent acquisition person or hiring manager at the company found on a public page (company site, public LinkedIn profile URL); (3) the company's publicly listed careers/recruiting email or careers page. For Upwork jobs the contact is the client via Upwork messaging; use level "posting" with the job link. NEVER guess or construct an email address; only report emails shown on a public page or in the posting. Business contacts only. Write /mnt/project-files/job-leads/YYYYMMDD_contacts.json (object keyed by job number as a string: {"name","title","email","url","source","level": "posting"|"named"|"general"|"none"}) and a readable /mnt/project-files/job-leads/YYYYMMDD_Contacts.md table (# | Company | Title | Contact | Email | Link | Found via).

TRACKER: run `python3 /mnt/project-files/job-leads/tracker/gen.py <today's list.md>` and publish the generated <out_dir>/job-leads.html with the Artifact tool to {{TRACKER_ARTIFACT_URL}} (same link every day; on the very first run publish a new artifact and save its URL into config.json "artifacts.tracker_url").

REPLY: post one reply in this thread: how many jobs made each list, the top 6 of each category as a short preview, how many jobs have a named contact, a link to the tracker page, the full list file and the contacts file, and one line saying {{NAME}} can ask for a resume and cover letter for any number. Include one line noting the listings and contacts were found with AI-assisted search and should be verified with the employer. If no new jobs turn up, say so in one line.
```

## Follow-on commands you'll use in the thread

- **"51 complete"** → Claude runs `python3 job-leads/tracker/mark.py <today's list> applied 51`, which marks the row, rebuilds the tracker and adds the job to the Follow-up Board. Republish both pages.
- **"52 not a fit"** / **"53 expired"** → `mark.py <list> nofit 52` / `mark.py <list> expired 53`.
- **"resume and cover letter for 54"** → the job-batch skill's tailoring step for that one job.
