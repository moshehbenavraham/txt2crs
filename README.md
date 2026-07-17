# txt2crs

txt2crs is an OpenAI + Devpost Education Hackathon project that turns a topic or
source material into a complete learning package:

- A deeply researched, source-grounded course
- Comprehensive review materials
- A full assessment with an answer key

## Origin Story

Two days after I joined OpenAI Build Week, my Zimbabwean wife asked me a simple,
powerful question: **“How can we bring AI to Africa?”**

Her question took me back to studying for my IBM AI Developer certification, when I
built a Make.com workflow to expand learning material, create study guides, and
generate review questions. Badda bing, badda boom—the question and that old experiment
clicked together, becoming the catalyst for txt2crs: a way to make rich, structured
learning experiences from almost any source material.

The planned application uses Python, FastAPI, an OpenAI subscription runtime, and
SQLite. Its target workflow normalizes the learner's input, researches and verifies
reliable sources, builds the course, derives aligned study materials and assessments,
and delivers polished learning artifacts through a clear, accessible interface.

## Current Status

This repository currently contains the original
[Make.com proof-of-concept workflows](make-scenarios/) and the
[product and architecture documentation](docs/). The production application is the
next stage of development.

## Versioning

txt2crs follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
The current pre-release version is stored in [`VERSION`](VERSION), and the
release process is documented in
[`docs/VERSIONING.md`](docs/VERSIONING.md).
