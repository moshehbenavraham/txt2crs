# Third-Party Notices

## Hermes Agent

Selected control-flow and provider-boundary behavior in this distribution was
materially adapted from [Hermes Agent](https://github.com/NousResearch/hermes-agent)
by Nous Research at revision
`0f102fa4dc04b7dfdab048169aaaa640d09d7523`.

The adapted files are:

- `src/txt2crs/ai/retry.py`, from `agent/retry_utils.py`;
- `src/txt2crs/ai/tool_guardrails.py`, from `agent/tool_guardrails.py`;
- `src/txt2crs/research/tavily.py`, from `plugins/web/tavily/provider.py`; and
- `src/txt2crs/security/url_safety.py`, from `tools/url_safety.py`.

These files were substantially rewritten around txt2crs-owned contracts. Donor
registries, global environment access, general agent loops, provider-specific
exceptions, compatibility switches, and fail-open behavior were removed.

Hermes Agent is licensed under the MIT License:

Copyright (c) 2025 Nous Research

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
