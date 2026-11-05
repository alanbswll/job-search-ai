# How to rebuild the job search setup

This guide walks through rebuilding the job search setup from scratch: two dashboards and two scheduled searches,
all run by Claude in a Claude project. It goes with the files in this folder (`scripts/`, `prompts/`,
`skills/`, `config.example.json`). The README lists those files. This guide covers how the pieces connect
and the order to set them up in.

Personal values are left out on purpose: names, email addresses, resume files, artifact links. Put yours in
`config.json`, which git ignores, and in the `{{...}}` placeholders in the prompts.

---

## 1. What you are building

| Piece | Kind | What it does |
|---|---|---|
| **Job Leads tracker** | Dashboard (Claude Artifact page) | Shows today's ranked list: fractional/contract #1-50 and full-time #51-100. Each row has a score, why it fits, pay, an apply link, a public contact and a status pill (To do, Docs ready, Applied, Skipped). Applied rows turn green. |
| **Follow-up Board** | Dashboard (Claude Artifact page) | Has one card for every job you've applied to, oldest first, with days since applying, the contact, a follow-up note under 200 characters, and inbox status (No reply yet, Confirmation received, Next steps email, Rejection email). It also has filters, a "Mark rejected" button, and an optional "Active interviews" strip at the top. |
| **Weekday job batch** | Scheduled search, 8:00 AM weekdays | Searches ZipRecruiter, Indeed, Dice and Upwork. It filters, dedupes against every earlier list, ranks against the resume, finds a contact per job, writes the dated list and rebuilds the tracker. |
| **Follow-up email scan** | Scheduled search, 4 times each weekday | Reads Gmail (read only) for rejections, interview requests and application confirmations. It updates the board's data, rebuilds the board, and posts in the thread only when something new turns up. |

How data moves:

```
job boards ──► batch routine ──► merge.py ──► YYYYMMDD_Job_Leads_Top100.md ──► gen.py ──► Job Leads tracker
                     └─► YYYYMMDD_contacts.json ───────────────────────────────┘
you: "51 complete" ──► mark.py ──► list Status column + gen.py (tracker)
                          └─► add.py ──► followups/followups.json ──► board_gen.py ──► Follow-up Board
Gmail ──► email-scan routine ──► followups.json + scan_state.json ──► board_gen.py ──► Follow-up Board
```

---

## 2. What you need

**Accounts and connectors.** Turn these on in the Claude project and allow each tool the first time Claude asks.

| Connector | Used by | Needed? |
|---|---|---|
| ZipRecruiter | batch | Yes. It's the baseline source and often returns titles only. |
| Indeed | batch, tailoring | Recommended. `get_job_details` gives the full job description. |
| Dice | batch, tailoring | Recommended. It gives full descriptions, named recruiters and the Easy Apply flag. Showing Dice results requires an AI-search disclosure line. |
| Upwork | batch | Optional, for fractional work. It only reads, never submits proposals. |
| Gmail | email scan | Required for the scan. It only reads. |
| Claude in Chrome (on your PC) | applying, reading pages that need a browser | Optional. |

There are no LinkedIn or Ladders job-seeker connectors. Applications made there won't show up on the lists.

**Software.** You need Python 3.8+ with the standard library only. The routines run it in Claude's cloud container,
so you don't have to install anything locally unless you want to test.

---

## 3. Files and folders

The routines run in the cloud and read the project's shared files at `/mnt/project-files/`. Lay them out like this:

```
/mnt/project-files/
  <base resume>.docx                    the resume every score is ranked against
  <portfolio / background>.docx         optional extra detail for tailoring
  job-leads/
    config.json                         your filled-in copy of config.example.json
    common.py                           from scripts/
    tracker/
      merge.py        filters, dedupes, ranks, writes the dated list
      gen.py          list (+ contacts json) -> job-leads.html
      mark.py         "N complete / not a fit / expired" -> updates list, rebuilds tracker, feeds board
      template.html   tracker page design (__DATA__, __DATE__ placeholders)
    followups/
      add.py          appends applied jobs to followups.json, rebuilds board
      board_gen.py    followups.json -> followup-board.html
      board_template.html  board page design (__DATA__, __DATE__, __SCAN__, __INTERVIEWS__, __CONFIG__)
      followups.json  master list of applied jobs (start it as [] )
      scan_state.json {"last_scan": "<UTC ISO>", "last_scan_label": "<readable time>"}
      interviews.json optional, see examples/interviews.example.json
    YYYYMMDD_Job_Leads_Top100.md        written daily
    YYYYMMDD_contacts.json / _Contacts.md  written daily
  tailored/                             resumes and cover letters, only when asked
  interview-prep/                       optional prep notes
```

To set it up, copy the contents of `scripts/` into `job-leads/`, put `config.json` next to `common.py`, and create
`followups/followups.json` containing `[]`.

**List format.** The scripts read and write one Markdown table per category with the columns
`# | Source | Company | Title | Location/remote | Pay | Posted | Score | Why it fits | Apply | Status`
(see `examples/sample_Job_Leads_Top100.md`). Never delete a row. Status is added to the Status column instead.

**Contacts json.** This is an object keyed by job number as a string:
`{"name","title","email","url","source","level": "posting"|"named"|"general"|"none"}`.

---

## 4. Rebuild from scratch, step by step

1. **Create the project.** Make a new Claude project (for example "Job Search") and paste
   `prompts/project-instructions.md` into its instructions, filling in the `{{...}}` values.
2. **Upload documents.** Put the base resume and any portfolio or background doc in the project files root.
3. **Connect connectors.** Connect the ones in section 2. Run one test search per board so the tool permissions get approved.
4. **Fill in config.** Copy `config.example.json` to `config.json` and set your name, timezone, base resume path,
   search queries, `exclude_title_keywords`, home metro and suburbs, Gmail inbox, follow-up pitch line and
   `min_score` (6 works well). Leave `artifacts` empty for now.
5. **Upload the scripts** into the layout in section 3.
6. **Add the skill.** Upload `skills/job-batch/` as a skill, or keep its `SKILL.md` in project files and point the
   routine at it.
7. **Seed memory.** Give Claude `prompts/memory-rules.md` and say "remember these rules". Add the personal rules
   from section 6 too.
8. **Make the batch routine.** Start a thread called "Weekday job batch schedule" and ask Claude to create a scheduled
   task from `prompts/routine-weekday-job-batch.md` on `CRON_TZ=America/New_York 0 8 * * 1-5`. Ask it to
   run once now.
9. **Save the tracker link.** The first run publishes the tracker as a new artifact. Put its URL in
   `config.json` → `artifacts.tracker_url` and in the routine prompt so every later run updates the same page.
10. **Make the board.** Mark one job applied ("51 complete"). That creates the first board entry. Ask Claude to
    publish `followup-board.html` as an artifact, then save that URL to `artifacts.board_url`.
11. **Make the email-scan routine.** In the same thread, create a scheduled task from
    `prompts/routine-followup-email-scan.md` on `CRON_TZ=America/New_York 47 7,12,16,20 * * 1-5`
    (7:47 AM, 12:47, 4:47 and 8:47 PM). Put the board URL in the prompt. Set `scan_state.json` to today so the
    first scan doesn't read your whole inbox.
12. **Check it worked.** The next morning there should be a new dated list, a contacts file, an updated tracker and one
    summary reply in the thread. After a scan, the board header shows "last scan <time>".

Both routines post into that one thread. Keep it open, because that's where you send "N complete" and ask for documents.

---

## 5. Schedule and triggers

| What | When (ET) | Fires | Posts in thread |
|---|---|---|---|
| Weekday job batch | Mon-Fri 8:00 AM | scheduled task, persistent thread session | always: counts, top 6 per category, contacts found, links |
| Follow-up email scan | Mon-Fri 7:47 AM, 12:47 PM, 4:47 PM, 8:47 PM | scheduled task, same thread | only when a rejection or next-steps email is new (next steps first) |
| Mark applied | when you write "N complete" | you | updates both dashboards |
| Tailored resume and letter | when you write "resume and cover letter for N" | you | links to the docs |

The off-the-hour minute (:47) keeps the scan from landing at the same time as other scheduled jobs.

**Things you say in the thread:**
- `51 complete` or `51, 53 complete` marks rows applied, turns them green and adds them to the board.
- `52 not a fit` or `53 expired` greys rows out.
- `resume and cover letter for 54` makes tailored documents. They go to `tailored/`, and also to the laptop folder if one is connected.

---

## 6. The rules this setup follows

Put these in the routine prompts, `config.json` and project memory so every run follows them.

**Search and ranking**
- **Location:** keep remote jobs, and on-site or hybrid only in the home metro. For this setup that's Atlanta, Alpharetta,
  Sandy Springs and nearby suburbs: Roswell, Johns Creek, Cumming, Duluth, Norcross, Dunwoody, Marietta, Peachtree
  Corners, Kennesaw, Smyrna, Suwanee, Buford, Lawrenceville, Brookhaven, Decatur, Milton. `loc_ok()` in merge.py
  enforces this. A "remote-optional" tag on a job board can be wrong, so trust the posting text when it says fully remote.
- **No architect roles.** Drop any title containing "architect" (Solution, Enterprise, Principal, Technical, and so on).
- **Leadership only:** manager, senior manager, director, head of, VP, fractional/interim engineering leadership,
  delivery/program leadership.
- **Dedupe** by company + title, ignoring Inc/LLC/Ltd/Corp. **Skip repeats** from every earlier list with a loose match
  (first company word + core title words). Put reworded reposts the match misses in `filters.skip_keys`.
- **Exclude companies** that already rejected you via `filters.exclude_companies`.
- Keep up to 50 per category with a score of 6 or higher. Never pad the list with poor fits.
- Prefer direct employer, Dice or ZipRecruiter links. Short `to.indeed.com` links expire.
- Always include a line saying listings and contacts come from AI-assisted search and should be verified.

**Contacts**
- The order of preference is: a recruiter named in the posting, then a named recruiter, TA person or hiring manager on a public page,
  then the public careers email or page. Business contacts only.
- Never guess or construct an email address.
- Follow-up notes must be under 200 characters.

**Documents**
- **No tailored resumes or cover letters unless asked** for a specific job number. The daily batch never makes them.
- Resume: copy the base resume and change only the headline and summary. Never invent experience, titles, metrics or
  skills. AI experience is application-level only. Name any gap honestly.
- Cover letter: one page, 3-4 short paragraphs, 2-3 concrete accomplishments. Same-day revisions get `_v2`.
- When tailoring for an application, Claude saves the files straight into your local tailored-docs folder through a
  connected device folder, so you don't have to download them.

**Applying**
- Use the dedicated **application email** set in `config.json` on every form. Keep it separate from the Gmail inbox
  the scan reads, and forward its mail to that inbox so the scan sees replies.
- When a site offers **"Sign in with Google"**, use that option with the Google account listed in `config.json`.
  You approve the Google prompt or password yourself.
- Form filling runs through a Remote Control session using Claude in Chrome on your PC. You paste the application
  link yourself, accept consent terms, and click **Submit** yourself. If a site requires a "no AI" attestation, Claude stops there and you finish.
- Never apply, send a message or submit an Upwork proposal without your OK on that specific job.
- Gmail is read only: never send, label, archive or delete email.

---

## 7. Keeping it running

- **Interviews strip:** edit `followups/interviews.json` (company, role, time, stage, with, prep link, join link),
  rebuild with `board_gen.py`, and republish.
- **Closed posting:** set `"posting": "closed"` on that entry in `followups.json`. It gets a tag and drops off To-do.
- **Synced folders can lag.** The scripts read their writes back after about 8 seconds. Keep that habit for manual edits too.
- **If a connector's sign-in expires,** the batch says so in one line and carries on with the other sources. Reconnect it in
  claude.ai → Settings → Connectors.
- **To test locally:** `python scripts/tracker/gen.py examples/sample_Job_Leads_Top100.md`. Generated pages go to `_out/`.
- **Privacy:** `.gitignore` keeps config, lists, contacts, follow-up data, interviews and every `.docx`/`.pdf` out of git.
  Run `git status` before each commit.
