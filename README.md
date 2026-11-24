# Recovery Atlas community

Help document rebuilding after the Palisades Fire. Pick a job and contribute computer time, an image edit or a verified record. The [live atlas](https://palisades-recovery-atlas.vercel.app/) uses public records and labels future scenes as illustrations.

## Render one block with your agent

[Copy the rendering prompt](https://palisades-recovery-atlas.vercel.app/contribute/) or paste this directly into an agent with web requests and image editing:

> Follow https://palisades-recovery-atlas.vercel.app/contribute/render-one.txt to claim one block, render it with my image tool, and submit it for review. Give me the review link.

The Atlas reserves a block for an hour and supplies the image, brief and attribution. Your agent uses its own image tool. You receive a side-by-side review link. No GitHub login is needed for rendering.

[Choose an open job](https://github.com/jdavies69/recovery-atlas-community/issues?q=is%3Aissue%20is%3Aopen) · [See contributions in review](https://github.com/jdavies69/recovery-atlas-community/pulls) · [Browse accepted results](results/)

## Give a minute of compute

With Python 3.8+ and Git installed, run:

```sh
git clone https://github.com/jdavies69/recovery-atlas-community.git
cd recovery-atlas-community
python3 contribute.py
```

The runner picks an open records job, fetches city inspection rows for its listed dwelling permits, checks address and permit matches, and writes a report in `out/`. This uses public data and standard Python. No model subscription, API key or payment is needed. Jobs may overlap if two people start at the same time. The first verified submission resolves the issue.

To contribute the report, sign into GitHub CLI with your own account and run the specific `--submit` command printed by the runner. This creates a fork when needed and opens a pull request. You may instead attach the report to the job issue. To see all seed briefs run `python3 contribute.py --list`; the Issues board shows current availability.

## Review and publish

Records reviewers run `python3 contribute.py JOB_ID` from trusted main, then compare the submitted JSON to the fresh report. Check primary permit scope and source links. Municipal records may be revised after the snapshot. Preserve distinct corrections, cancellations and approvals. Image reviewers compare camera geometry, stage, licensing and lighting with the reference. Credit contributors by their chosen public name. Merging accepts a contribution into the public archive. Changes to the production atlas have a separate review.

Each job lists its own inputs. The Fiske images are CC BY-SA 4.0. Credit uwrapid via Mapillary and identify modifications when redistributing those images.
