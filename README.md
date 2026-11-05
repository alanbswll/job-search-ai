# Claude Job Search Kit

A replicable setup for running a job search with Claude: a weekday routine that pulls fresh leads from several
job boards, ranks them against your resume, finds a public recruiting contact for each, and publishes a
tracker page; a second routine that scans Gmail for rejections and interview requests and keeps a
Follow-up Board current; and on-demand tailored resumes and cover letters.

Everything personal (your resume, name, email, location and role preferences) lives in files you keep
private. This repo holds only the prompts, scripts, templates and a config template.

## What you get

| Piece | What it does |
|---|---|
| **Weekday job batch** routine | Searches ZipRecruiter, Indeed, Dice and Upwork; filters by location and role; dedupes against every earlier list; ranks up to 50 fractional/contract (#1-50) and 50 full-time (#51-100) jobs; finds a public contact per job; publishes the tracker page. |
| **Job Leads tracker** (`scripts/tracker/`) | A sortable page of today's list with status pills (to do, applied, skipped), contacts and apply links. |
| **Follow-up Board** (`scripts/followups/`) | One card per job you've applied to, oldest first, with days since applying, contact, a copy-ready follow-up note, inbox status, and an optional "Active interviews" strip. |
| **Follow-up email scan** routine | Reads Gmail (read-only) four times a weekday and marks board jobs as rejected, next steps, or confirmation received. |
| **job-batch skill** | The search/rank method and the tailoring rules for resumes and cover letters. |

## Repo layout

```
README.md
config.example.json            copy to config.json and fill in (git-ignored)
prompts/
  project-instructions.md      paste into the Claude project's instructions
  routine-weekday-job-batch.md prompt + schedule for the daily batch
  routine-followup-email-scan.md prompt + schedule for the Gmail scan
  memory-rules.md              sanitized lessons to seed project memory
skills/job-batch/SKILL.md      upload as a Claude skill
scripts/
  common.py                    config + paths shared by all scripts
  tracker/  merge.py gen.py mark.py template.html
  followups/ add.py board_gen.py board_template.html
examples/
  sample_Job_Leads_Top100.md   list format the scripts read and write
  interviews.example.json      optional data for the board's interview strip
```

## Setup

### 1. Create the Claude project
1. In Claude, create a project (e.g. "Job Search") with a topic such as "Help tailor and analyze job opportunities for me."
2. Paste `prompts/project-instructions.md` into the project instructions, filling in the `{{...}}` values.
3. Upload your resume(s) and any portfolio/background docs to the project files root.

### 2. Connect the tools
Turn these on for the project (Settings → Connectors):

| Connector | Used for | Required? |
|---|---|---|
| **ZipRecruiter** | job search (often titles only) | yes, the baseline source |
| **Indeed** | job search plus full job descriptions (`get_job_details`) | recommended |
| **Dice** | job search, full descriptions, named recruiters, Easy Apply flag | recommended |
| **Upwork** | fractional/contract leads (read-only; never submits proposals) | optional |
| **Gmail** | the follow-up scan (read-only) | needed for the Follow-up Board scan |
| **Claude in Chrome** | reading postings that need a real browser, LinkedIn pages | optional |

Allow each connector's tools the first time Claude asks. The routines check with ToolSearch and carry on with
whichever sources are connected.

### 3. Fill in your config
```bash
cp config.example.json config.json
```
Edit `config.json`: name, timezone, base resume path, search queries, excluded title keywords, home metro and
its suburbs, Gmail address, follow-up pitch line. Leave `paths` empty to use the defaults (lists live next to
the scripts; generated pages go to `_out/`).

### 4. Upload the scripts to the project files
The routines run in the cloud and read the project files at `/mnt/project-files/`. Upload so the project
looks like this:

```
/mnt/project-files/
  <your resume>.docx
  job-leads/
    config.json                 your filled-in config
    common.py
    tracker/   merge.py gen.py mark.py template.html
    followups/ add.py board_gen.py board_template.html
               interviews.json  (optional, copy from examples/)
  tailored/                     created on first tailoring request
  interview-prep/               optional prep notes
```
That is: the contents of `scripts/` go into `job-leads/`, and `config.json` goes beside `common.py`.

### 5. Add the skill
Upload `skills/job-batch/` as a skill (Settings → Capabilities → Skills), or keep `SKILL.md` in the project
files and point the routine at it.

### 6. Create the routines
In the project, start a thread called "Weekday job batch" and ask Claude to schedule each routine with the
prompt from `prompts/`:
- `routine-weekday-job-batch.md`, weekdays 8:00 AM your time.
- `routine-followup-email-scan.md`, four times each weekday.

On the first run Claude publishes the tracker and the board as new artifacts. Put those two URLs in
`config.json` under `artifacts` and in the routine prompts so later runs update the same pages.

### 7. Seed memory
Paste `prompts/memory-rules.md` into project memory, or tell Claude "remember these rules" with the file.

## Daily use
- Open the tracker each morning. Apply to what fits.
- Tell Claude **"51 complete"** (or "51, 53 complete"). It runs `mark.py`, which marks the row, rebuilds the
  tracker and adds the job to the Follow-up Board.
- **"52 not a fit"** / **"53 expired"** greys a row out.
- **"Resume and cover letter for 54"** makes tailored documents for that job.
- The Gmail scan flags rejections and interview requests on the board and posts in the thread when it finds
  something you need to act on.

## Running the scripts locally
Python 3.8+, standard library only.
```bash
python scripts/tracker/merge.py 20260105        # needs _out/merge/*.json from a search step
python scripts/tracker/gen.py examples/sample_Job_Leads_Top100.md
python scripts/tracker/mark.py path/to/list.md applied 51
python scripts/followups/board_gen.py path/to/followups/followups.json 2026-01-05
```
Generated pages land in `_out/` (or `paths.out_dir`).

## Privacy
`.gitignore` keeps `config.json`, job lists, contacts, follow-up data, interviews, tailored documents and any
`.docx`/`.pdf` out of git. Check `git status` before every commit if you fork this for yourself.

## Caveats
- Job listings and contacts come from AI-assisted search. Verify details with the employer before applying.
- Contacts are only taken from postings or public pages; email addresses are never guessed.
- Nothing is ever submitted, sent or applied for without your explicit OK.
