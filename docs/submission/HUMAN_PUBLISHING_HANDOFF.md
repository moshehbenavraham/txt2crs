# Human Publishing Handoff

The product and submission assets are prepared locally. Publishing is
human-only: the human operator owns all GitHub access changes, uploads,
platform forms, release tags, and pushes.

## Ready Assets

| Asset | Location |
|-------|----------|
| Demo video | `.release-private/video/txt2crs-demo-1.0.0.mp4` |
| Video title and description | `docs/submission/VIDEO_STORYBOARD.md` |
| Devpost project story | `docs/submission/DEVPOST_SUBMISSION.md` |
| Six reviewed screenshots | `docs/submission/screenshots/` |
| Evidence map | `docs/submission/PUBLIC_EVIDENCE_INDEX.md` |
| Codex feedback Session ID | `docs/submission/CODEX_FEEDBACK.md` |

Video identity:

- duration: 02:22.600;
- SHA-256:
  `cc78d540f41eb6bbb634540fbf70df0d98c9975a308a8ae984135fb492d5542f`;
- format: 1920x1080 H.264 video with AAC audio; and
- intended repository release: `v1.0.3`.

## 1. Keep GitHub Private And Add Reviewers

Keep <https://github.com/moshehbenavraham/txt2crs> Private.

In repository settings, grant read access to the accounts associated with:

- `testing@devpost.com`
- `build-week-event@openai.com`

If GitHub cannot resolve an address, contact the event organizer. Do not make
the repository Public as a workaround.

## 2. Review, Commit, Tag, And Push

Review the final local release commit and run the release checks supplied in
[`docs/release/README_release.md`](../release/README_release.md).

After the exact release commit is clean and approved, the human operator may
publish it:

```bash
final_commit="$(git rev-parse HEAD)"
test -z "$(git status --short)"

git tag --annotate v1.0.3 \
  --message "txt2crs 1.0.3 - OpenAI Build Week Education release" \
  "${final_commit}"

git push origin main
git push origin v1.0.3
```

Verify that remote `main` and peeled `v1.0.3` resolve to `final_commit`. Make
no tracked edit after tagging; use a new SemVer version for any later change.

## 3. Publish The Demo Video

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

## 4. Submit On Devpost

Open:
<https://devpost.com/submit-to/30223-openai-build-week/manage/submissions>

Use:

- project name: `txt2crs`;
- category: Education;
- repository: <https://github.com/moshehbenavraham/txt2crs>;
- release:
  <https://github.com/moshehbenavraham/txt2crs/tree/v1.0.3>;
- project story: [`DEVPOST_SUBMISSION.md`](DEVPOST_SUBMISSION.md);
- screenshots: the six reviewed files in `docs/submission/screenshots/`;
- video: the stable YouTube URL from the previous step; and
- Codex feedback Session ID:
  `019f7990-e049-7242-9d36-dc1eb4462d69`.

Complete submitter type and country directly in Devpost. Those account-only
answers do not belong in the repository.

Submit before `2026-07-22T00:00:00Z`.

## 5. Final Human Check

Before considering the entry finished, confirm:

- the repository is still Private and both reviewers have access;
- remote `main` and `v1.0.3` match the reviewed release commit;
- the YouTube video works while signed out and is under three minutes;
- the Devpost entry is in Education and shows all six screenshots;
- the repository, release, video, and Session ID values are exact; and
- Devpost shows a successful submission before the deadline.

Store platform URLs and confirmation details privately. Do not add a tracked
post-tag receipt or expose account-only information.
