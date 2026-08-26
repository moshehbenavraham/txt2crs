# Human Publishing Handoff

> Archived Build Week handoff. Its external actions and deadline are expired.

The product and submission assets are prepared. The public GitHub repository,
security settings, branch, and immutable release tag are complete. YouTube
upload and the authenticated Devpost form remain human-owned actions.

## Ready Assets

| Asset | Location |
|-------|----------|
| Demo video | `.release-private/video/txt2crs-demo-1.0.0.mp4` |
| Video title and description | `docs/archive/build-week/VIDEO_STORYBOARD.md` |
| Devpost project story | `docs/archive/build-week/DEVPOST_SUBMISSION.md` |
| Six reviewed screenshots | `docs/archive/build-week/screenshots/` |
| Evidence map | `docs/archive/build-week/PUBLIC_EVIDENCE_INDEX.md` |
| Codex feedback Session ID | `docs/archive/build-week/CODEX_FEEDBACK.md` |

Video identity:

- duration: 02:22.600;
- SHA-256:
  `cc78d540f41eb6bbb634540fbf70df0d98c9975a308a8ae984135fb492d5542f`;
- format: 1920x1080 H.264 video with AAC audio; and
- immutable repository release: `v1.2.5`.

## 1. Verify The Public GitHub Release

Open these links while signed out:

- repository: <https://github.com/moshehbenavraham/txt2crs>; and
- immutable release:
  <https://github.com/moshehbenavraham/txt2crs/tree/v1.2.5>.

Confirm both load publicly and that the release tag resolves to the reviewed
`1.2.5` source. GitHub secret scanning, push protection, vulnerability alerts,
and automated security updates are enabled.

## 2. Publish The Demo Video

Upload `.release-private/video/txt2crs-demo-1.0.0.mp4` in YouTube Studio.

Copy the exact title and description from the `Upload Metadata` section of
[`VIDEO_STORYBOARD.md`](VIDEO_STORYBOARD.md), then:

1. choose `No, it is not made for kids`;
2. answer YouTube's required disclosures truthfully;
3. select `Public`;
4. wait for HD processing; and
5. verify signed-out playback, audio, 1080p availability, and a duration below
   three minutes.

Keep the resulting stable YouTube URL for the Devpost form.

## 3. Submit On Devpost

Open:
<https://devpost.com/submit-to/30223-openai-build-week/manage/submissions>

Use:

- project name: `txt2crs`;
- tagline: `Turn one bounded source into a complete, source-grounded learning package.`;
- category: Education;
- repository: <https://github.com/moshehbenavraham/txt2crs>;
- release:
  <https://github.com/moshehbenavraham/txt2crs/tree/v1.2.5>;
- built with: Codex, GPT-5.6, Python, FastAPI, Pydantic, SQLModel,
  PostgreSQL, SQLite, React, TypeScript, TanStack Router, TanStack Query,
  Tailwind CSS, shadcn/ui, Tavily, MCP, Docker, Playwright, and uv;
- project story: [`DEVPOST_SUBMISSION.md`](DEVPOST_SUBMISSION.md);
- project thumbnail: `docs/archive/build-week/screenshots/06-answer-key.png`, whose
  reviewed frame shows all four publications and all four formats;
- screenshots: the six reviewed files in `docs/archive/build-week/screenshots/`;
- video: the stable YouTube URL from the previous step; and
- Codex feedback Session ID:
  `019f7990-e049-7242-9d36-dc1eb4462d69`.

Complete submitter type and country directly in Devpost. Those account-only
answers do not belong in the repository.

Submit before `2026-07-22T00:00:00Z`.

## 4. Final Human Check

Before considering the entry finished, confirm:

- the repository and `v1.2.5` release load publicly while signed out;
- remote `main` and `v1.2.5` match the reviewed release commit;
- the YouTube video works while signed out and is under three minutes;
- the Devpost entry is in Education and shows all six screenshots;
- the repository, release, video, and Session ID values are exact; and
- Devpost shows a successful submission before the deadline.

Store platform URLs and confirmation details privately. Do not add a tracked
post-tag receipt or expose account-only information.
