# AGENTS.md - Coding Agent's Instructions / Rules

## Project

This is a OpenAI + DevPost Hackathon project for the category of Education.  The goal is to create a solution (agent or app) with a beautiful interface that accepts any input and will deliver: 1) A full deep-researched course based on the input, 2) Create comprehensive review materials on that generated course, and 3) Generate a full test with answer sheet.

## Critical Rules

In no particular order.

- Add genearous code-comments as if a 1st year Computer-Science intern has to navigate / work in the code.
- Use descriptive variable names and function names that clearly explain their purpose
- README.me filename is reserved for root README file. All other appropriate / relevant project folders should have a README named in the form of README_<appropriate-name>.md - example docs/ folder should have a README file named README_docs.md
- Avoid over-engineering while still following best practices and industry standards.
- Create the tests before the code
- After completing an item from `docs/TODO.md`, move it to `docs/CHANGELOG.md`
- Once `docs/CHANGELOG.md` gets roughly 20+ entries, archive it to `docs/archive/CHANGELOG_YYYYMMDD.md` and create a new empty `docs/CHANGELOG.md`
- Follow `docs/VERSIONING.md` and keep `VERSION` synchronized with each release.

## Tech Stack

- Python (backend)
- FastAPI
- OpenAI Subscription
- Postgres OR SQLite
