# Routine: Follow-up Board email scan

**Schedule:** four times each weekday, e.g. `CRON_TZ=America/New_York 47 7,12,16,20 * * 1-5`.
**Needs:** the Gmail connector (read-only use).
**Where it posts:** the same job-batch thread, and only when something new is found.

Replace every `{{...}}` before saving the routine.

---

```text
Scheduled Follow-up Board email scan.

1. Read /mnt/project-files/job-leads/followups/followups.json (the board's jobs) and scan_state.json (last_scan; if missing, scan the last 7 days).

2. Search the connected Gmail ({{GMAIL_INBOX}}) for mail since last_scan (use after:YYYY/MM/DD from the last_scan date): rejection phrasing (unfortunately, "not moving forward", "not to move forward", "other candidates", "not selected", "position has been filled", "decided to pursue") and next-steps phrasing (schedule, interview, assessment, "next steps"), plus mail from common ATS senders (myworkday, greenhouse, lever, jobvite, workable, icims, smartrecruiters, ashby). Read candidate threads with get_thread. Read only: never send, label, archive or change email.

3. Match each email to a board job by company and, where the company has several jobs, by role title. Only mark a job when the match is clear. Set email_status to "rejected" or "interview" (or "received" for a plain application confirmation on a job that is "no email"/"not checked"), with email_date, email_subject and email_url. Re-read followups.json just before writing, change only the matched entries, and read it back ~10 s later.

4. Update scan_state.json with last_scan (now, UTC ISO) and last_scan_label (e.g. "Jan 5, 8:47 AM ET").

5. Run `python3 /mnt/project-files/job-leads/followups/board_gen.py /mnt/project-files/job-leads/followups/followups.json <today YYYY-MM-DD>` and publish <out_dir>/followup-board.html with the Artifact tool to {{BOARD_ARTIFACT_URL}}.

6. Reply in the job thread only if something new was found: one short line per rejection or next-steps email (company, role, date), and lead with any next-steps email since {{NAME}} needs to act on it. If nothing new, end with no reply.
```
