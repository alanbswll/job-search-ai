---
name: "job-batch"
description: "Use when the user asks to find their top job matches (fractional/contract and full-time) on ZipRecruiter, Indeed, Dice or Upwork, rank them against their resume, or produce a tailored resume and cover letter for a listed job."
---

# Job batch: search, rank, and tailor on request

Settings come from `/mnt/project-files/job-leads/config.json` (see `config.example.json` in the repo).

## Inputs
- Base resume: `config.resume.base_resume`. Also read `config.resume.extra_context` files for detail.
- Existing leads: every file in `/mnt/project-files/job-leads/`. Skip any job already listed there so each batch is new.

## 1. Search
Use every connected job-board connector (ZipRecruiter, Indeed, Dice, Upwork).
- Fractional/contract: `config.search.fractional_queries` and variations.
- Full-time: `config.search.fulltime_queries` and variations.
- Run several queries and pages per track. Save raw results per source as JSON in `<out_dir>/merge/`
  (fields: source, company, title, loc, pay, posted, url, score, why, cat "F"|"T", easy_apply).

## 2. Score
Score each job 1-10 against the resume: title/level fit, core stack (`config.search.stack`), leadership scope,
domain (`config.search.domains`), remote/location, pay if shown. Write a one-line "why it fits".

## 3. Merge and write the list
Run `python3 /mnt/project-files/job-leads/tracker/merge.py`. It applies the location and title filters, dedupes,
skips earlier lists, and writes `YYYYMMDD_Job_Leads_Top100.md` (fractional 1-50, full-time 51-100).

## 4. Tailor documents (only when asked, by job number)
Save into `/mnt/project-files/tailored/`:
- `YYYYMMDD_<file_prefix>_Resume_<Company>_<Short_Title>.docx`
- `YYYYMMDD_<file_prefix>_Cover_Letter_<Company>_<Short_Title>.docx`

Resume rule: copy the base resume and change only the headline and summary to match the job. Keep the experience
section unchanged and never invent experience, titles, metrics or skills.
Cover letter: one page, addressed to the hiring team at the company, three or four short paragraphs tying two or
three concrete accomplishments from the resume to the posting's needs. For fractional roles, frame availability
and outcomes per engagement. Use the docx skill and open each file once to confirm it is valid.
Then add `📄 [Resume](...), [Cover letter](...)` to that row's Status column and rebuild the tracker.

## 5. Report
Reply with counts per category, the top 6 of each, links to the list and tracker, and a note that listings came
from AI-assisted search and should be verified with the employer.
