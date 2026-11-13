# MILESTONE II FIX PROMPT: Complete the Crawl and Repair the Deliverables
### CSCE 2501 – Resale Properties – repo: `Database-Final-project-milestone-2`

> Paste everything below the line into your AI coding assistant, opened at the root of the repo.
> It assumes the repo already contains `milestone1/` and `milestone2/` (crawler, parsing, load, validate, deliverables).

---

## 0. ROLE AND GOAL

You are a senior data engineer. The Milestone II submission in this repo was reviewed against the official requirements and has defects. Your job is to **fix them, re-run the pipeline for real, and re-verify every claim in the README**. Do not rewrite working code unnecessarily; change only what each issue below requires.

### Official Milestone II requirements (unchanged, source of truth)
- Crawl the AqarExit pages for **all the properties listed**.
- Parse the HTML and extract fields for the **non-user tables** (some fields come from free text).
- All non-user tables populated; **user tables populated with sample test data**.
- **Rate-limit requests** (Cloudflare is present; aggressive scraping risks IP blocks).
- Deliverables: **crawling script**, **populated MySQL dump**, **CSV files for every table**.

### Non-negotiable rules (carry over)
1. Stay polite: obey robots.txt, honest User-Agent, concurrency 1, jittered delay of at least 2.5 s. **Never** raise the request rate to save time. **Never** bypass Cloudflare or any bot protection (no stealth plugins, fingerprint spoofing, CAPTCHA solving, proxy/IP rotation). If challenged, back off, pause, and tell me.
2. Never fabricate data. Unknown means `NULL`.
3. Never store personal data of sellers/agents.
4. Real execution only. Show real counts and real command output. If you cannot run something (for example no MySQL available), say so and give me the exact command to run myself. Never invent output.
5. Every claim in the README must be true when you finish. Remove or correct any that is not.

---

## 1. ISSUES TO FIX (in priority order)

### ISSUE 1 (CRITICAL): Only 42 of about 9,690 listings were crawled
**Evidence:** `quality_report.md` shows Discovered 9,690, Fetched 42, Loaded 42. The README says the crawl reconciles with the sitemap, but the documented command is `fetch --limit 35`. The requirement says "all the properties listed".

**Fix:**
1. Run discovery again so the crawl-state store lists every listing. Confirm the discovered count and compare it with the sitemap count. Explain any difference between 9,684 (README) and 9,690 (report). The cause is probably the index page adding a few extra URLs; verify and document it.
2. Make the full crawl run **unattended and resumable**:
   - Add a `--limit 0` (meaning unlimited) option and make it the default for a full run, or add `--all`. Keep `--limit N` for testing.
   - Keep `--resume`: skip any listing whose raw file exists and is non-empty and whose state is `done`.
   - Keep the polite settings (2.5 to 5.0 s jitter, backoff on 429/503/403, circuit breaker after 3 consecutive blocks). Add a **long pause** (15+ minutes) when the circuit breaker trips, then continue automatically up to a configurable number of pauses (e.g. 6) before stopping cleanly.
   - Print a progress line every 25 requests: done / pending / failed / blocked / ETA.
   - Handle `Ctrl+C` gracefully: finish the current request, flush state, exit.
   - Make sure state is committed after **every** request so a crash loses nothing.
3. Estimated time is about 9,690 × ~3.75 s ≈ 10 hours. Print this estimate before starting. Start the crawl in the background (`nohup`, `tmux`, or Windows Task Scheduler / a separate terminal) and keep working on Issues 2 to 7 on the cached pages while it runs.
4. After the crawl, run `--retry-failed` once for anything that failed for transient reasons. Report the final funnel: discovered / fetched / failed (with reasons) / parsed / rejected / loaded.
5. **If the crawl cannot finish before I must submit:** do not speed it up. Stop at a cut-off I choose, make the sample **representative** (not just the first N URLs; sample across areas, developments, property types), and make the README state the exact coverage as "N of M listings (X%)" with no wording that implies full coverage.

### ISSUE 2 (CRITICAL): The database dump is unusable
**Evidence:** `milestone2/deliverables/resale_properties_dump.sql` is encoded as **UTF-16 LE with BOM** (probably created by a PowerShell `>` redirect). The `mysql` client cannot read UTF-16 files, and the Arabic strings inside are garbled (mojibake, e.g. the `property_type` names), although the CSVs are correct.

**Fix:**
1. Re-create the dump **without shell redirection**, using the tool's own file output:
   `mysqldump --single-transaction --routines --triggers --default-character-set=utf8mb4 --set-gtid-purged=OFF --result-file=milestone2/deliverables/resale_properties_dump.sql -u <user> -p resale_properties`
2. Verify the encoding: the file must be plain UTF-8 (no UTF-16, optionally no BOM). Show the output of `file` (or a Python check that decodes it as UTF-8 and finds `CREATE TABLE` and `INSERT INTO`).
3. **Restore test (mandatory):** create a brand-new empty database (e.g. `resale_properties_restore_test`), load the dump with `mysql --default-character-set=utf8mb4 ... < dump.sql`, and compare **row counts for every table** with the source database. Show both lists side by side.
4. Round-trip test for Arabic: select a known Arabic string (e.g. an area or developer name) from the restored DB and compare it, character by character, with the CSV value. Show the result.
5. Add `deliverables/restore_check.md` containing the exact commands you ran and the real output.
6. Add the dump command and the encoding warning ("do not use `>` in PowerShell") to the README.

### ISSUE 3: Location hierarchy is wrong, and names mix languages
**Evidence:** `location.csv` has every area (North Coast, Sharm El Sheikh, Ain Sokhna, 6th of October, ...) as a child of "New Cairo", which is a child of "Cairo". Only "Cairo" and "New Cairo" are in English; all other names are Arabic. `property_type` mixes English ("Apartment", "Chalet") and Arabic ("محل", "مكتب").

**Fix:**
1. Inspect the raw pages / JSON-LD to see what location information AqarExit really provides per listing (area, city, governorate, region). Build the hierarchy **from the data**, not from a hardcoded guess. Where the page gives only an area name, map it to its correct city/governorate using a small, **reviewable lookup file** (`parsing/location_hierarchy.csv`: `area_name, area_name_ar, city, governorate`). Never put an area under an unrelated city. Examples that are geographically separate: North Coast, Sharm El Sheikh, Ain Sokhna, New Administrative Capital, 6th of October, Sheikh Zayed, Mostakbal City, New Cairo, El Shorouk, Obour, Mokattam, Nasr City.
2. Choose **one** language policy and apply it everywhere, then document the decision (Decision / Alternatives / Why):
   - Preferred: keep **both** names. Add `name_en` and `name_ar` columns to `location` and `property_type` (document the change in `sql/schema_changes_m2.sql`, apply it to the schema, and update the loader, CSV export, and the dump). The English name is the canonical display name; Arabic is stored alongside.
   - Acceptable alternative: normalize everything to English display names with a mapping dictionary, and keep the original Arabic in a separate column.
   - Whatever you choose, **the same entity must never appear twice in two languages** (e.g. "New Administrative Capital" and "العاصمة الإدارية الجديدة" must resolve to one row).
3. Apply the same normalization to `property_type` (e.g. محل = Shop, مكتب = Office) and to `amenity`, and check `developer` and `development` for English/Arabic duplicates of the same company or project. Produce `data/staging/entity_resolution_report.csv` listing every merge and every near-duplicate you did **not** merge, so a human can review it. Do not blindly fuzzy-merge distinct entities (e.g. "Sodic West" vs "Sodic East").
4. After the full crawl the lookup tables will grow; make sure unmapped locations/types are **logged and loaded under a clearly labeled fallback behaviour** (e.g. placed at governorate level as "Unclassified" only if truly unknown, and listed in the report), never silently attached to a wrong parent.
5. Re-run loading and show the final `location` tree (indented text) so I can check it by eye.

### ISSUE 4: Location coordinates are empty
**Evidence:** `location.csv` has empty `latitude` and `longitude` for all rows, and the project needs "the location of a given development" later.

**Fix:**
1. Check whether the listing pages / JSON-LD / embedded map data contain coordinates or a map link for the property or development. If they do, extract them into `development.latitude/longitude` (and the property if the schema has it) using `DECIMAL`, and validate they fall inside Egypt (roughly lat 22 to 32, lon 24 to 37).
2. Report coverage: how many developments have coordinates, and how many do not.
3. If the site does not expose coordinates, **leave them NULL** and say so in the README. Do not call a geocoding API with scraped data, and do not guess.
4. Check `development.csv` too, not only `location.csv`.

### ISSUE 5: README contradicts itself and contains false or broken claims
**Evidence:**
- Section 5 of `milestone2/README.md` shows 35 property / 34 developer / 8 amenity rows, while the quality report and manifest show 42 / 38 / 10.
- Sitemap count is given as 9,684 in one place and 9,690 in another.
- Links use `file:///c:/Users/iRepair/...`, which are broken for anyone else.
- The checklist says the crawl reconciles with the sitemap, the loader is idempotent, the dump restores cleanly, and all Milestone III queries return meaningful rows. Several of these were not true or not verified.

**Fix:**
1. **Generate the README tables from the real database and the real quality report** (script or copy-paste of real output), not by hand, so numbers cannot drift. Add a "Generated on <date>" line.
2. Replace every absolute local link with a **relative** link (e.g. `deliverables/csv/`).
3. Make the reproduction commands consistent and correct. The module commands use `python -m milestone2....`; verify they actually run from the repo root (add `__init__.py` files if needed), and state the working directory.
4. Rewrite the Definition-of-Done checklist so each line is **YES only if you verified it in this session**, with a pointer to evidence (file or command output). Mark anything not achieved as NO or PARTIAL with the reason.
5. Add a short **"Known limitations"** section (e.g. `data/raw/` is git-ignored so offline re-parsing needs a fresh crawl or a zipped raw archive; coordinates coverage; any listings that failed).
6. If raw HTML is too large for Git, **zip `data/raw/` to `deliverables/raw_html_archive.zip`** (only if under a reasonable size, e.g. 100 MB; otherwise skip and say so) so the "parse offline" claim is reproducible.

### ISSUE 6: Possibly redundant financial columns
**Evidence:** in the staged data, `gain_over_market_value` equals `discount_over_market_price` in every row inspected.

**Fix:**
1. Check across **all** rows whether the two columns are always equal. If they are, decide and document one of: (a) keep both because the Milestone I schema and the later analytics ask for both "gain over market value" and "discount over market price", or (b) keep one stored column and expose the other as a view column. Do not delete a column the schema requires without telling me. Record the decision in `schema_changes_m2.sql` and the README.
2. Also check the values themselves against the page (spot-check 10 random listings: price, market price, down payment, installment, contract year) and report any mismatch.

### ISSUE 7: Validation must be re-run on the full data
After Issues 1 to 6, regenerate and verify everything:
1. `quality_report.md`: full funnel, row counts, null rates, FK orphan checks (must all be 0), duplicate natural keys (must be 0), range checks with the top 20 outliers, text-extraction coverage, charset check.
2. `m3_smoke_queries.sql` (the 8 analytic smoke queries) against the full data. Show the first rows of each; if a query is empty or meaningless, report it as a data problem and fix the extraction.
3. **Idempotency test:** run the loader twice and show that row counts are identical.
4. **CSV test:** re-export all 11 tables (utf-8-sig, headers, `NULL` as an empty field), regenerate `_manifest.csv`, and show DB row count = CSV row count for every table. Include the new `name_en` / `name_ar` columns if you added them.
5. **Seed users test:** user tables must reference only developments and locations that exist after the re-load (re-run `seed_users.py` after the final data load, with the fixed seed). Ratings 1 to 10; emails only on `example.com`.
6. Run the unit tests (`pytest`) and add tests for the new location mapping and language normalization.

---

## 2. ORDER OF WORK

1. Issue 1: start the full crawl in the background **first** (it takes hours).
2. While it runs, on the cached pages: Issue 3 (location/language), Issue 4 (coordinates), Issue 6 (financial columns), and the parser/loader updates and tests.
3. When the crawl finishes (or at the cut-off): re-parse offline, reload from scratch (`--init`), re-seed users, export CSVs.
4. Issue 2: re-dump to UTF-8 and run the restore test **after** the final load.
5. Issue 7: regenerate the quality report and smoke-query output.
6. Issue 5: regenerate the README from real outputs last.
7. Keep `deliverables/crawler/` in sync with the final source files (copy, then diff to prove they match).

---

## 3. DEFINITION OF DONE (answer YES / NO / PARTIAL with evidence)

- [ ] Discovered count explained; crawl covers all listings, or the README states exact partial coverage.
- [ ] No request-rate increase; no protection bypass; robots.txt obeyed.
- [ ] Dump is UTF-8, restores into an empty database with no edits, row counts match, Arabic matches the CSVs.
- [ ] Location hierarchy is geographically correct and shown as a tree.
- [ ] No entity appears twice in two languages; resolution report produced.
- [ ] Coordinates extracted where available; coverage reported; otherwise NULL.
- [ ] Gain vs discount columns decision documented.
- [ ] 0 FK orphans, 0 duplicate natural keys.
- [ ] Loader idempotent (two runs, same counts).
- [ ] One CSV per table; CSV counts = DB counts; manifest regenerated.
- [ ] Synthetic users/reviews reference real developments/areas.
- [ ] Smoke queries return meaningful rows.
- [ ] Unit tests pass.
- [ ] README numbers generated from real output; relative links; honest checklist; known limitations listed.
- [ ] `deliverables/crawler/` identical to the working source.

---

## 4. STYLE OF YOUR RESPONSE

- Work issue by issue. After each, show: what you changed (files), commands run, real output, and what is still open.
- For each non-trivial decision give **Decision / Alternatives / Why**; I must be able to defend them in the demo.
- If something blocks you (Cloudflare challenge, missing MySQL, site structure differs from what is described here), **stop and explain the options** instead of improvising around it.
- If the real data contradicts anything in this prompt, the real data and the official project text win; tell me.
- End with a "What to hand in" list mapped to the three official deliverables.
