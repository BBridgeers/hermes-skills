---
name: cover-letter-generator
description: Generates human-sounding, context-aware cover letters using Blake's professional profile (SOUL). Reads job descriptions, matches to experience, and outputs letters that read as 100% human-written.
---

# Cover Letter Generator — Blake's Professional Voice System

## Purpose
Generate cover letters, application emails, and professional correspondence that:
- Read as naturally human (scan as non-AI)
- Are tightly matched to specific job postings
- Consistently represent Blake's experience, metrics, and voice
- Avoid every AI cliché and corporate-speak anti-pattern

## Required References
Before generating ANY cover letter, load:
1. **Blake's Professional Profile**: `references/blake-profile.md` (SOUL document)
2. **Job Description**: User provides or Hermes fetches via web_search/browser

## How It Works

### Step 1: Parse the Job Description
Extract from the JD:
- Company name and values signals
- Exact job title
- Required qualifications (must-haves)
- Preferred qualifications (nice-to-haves)
- Key phrases/buzzwords (mirror these naturally)
- Seniority level → determines tone weight
- Technology/industry keywords to match

### Step 2: Map Blake's Experience
Using the SOUL profile, identify:
- 2-3 direct experience matches (with metrics)
- Transferable skills for any gaps
- Which role type header to use (CS/Sales/Tutoring/Floral/IT/Admin)
- Whether the gap narrative should be included or omitted

### Step 3: Draft the Letter
**Structure (3-4 paragraphs max, one page)**:

**Opening (Para 1)**: Hook — demonstrate specific knowledge of the company/role. NOT "I am writing to express interest in...". Instead: reference a recent company initiative, the JD's specific challenges, or Blake's direct connection to the industry/location.

**Body (Para 2-3)**: Evidence — 2-3 specific examples from Blake's history using the format: Situation + Action + Metric. Use exact keywords from JD. Tie each example to a specific job requirement.

**Close (Para 4)**: Forward-looking — what Blake will DO (not hope to get). One specific action. No begging. Professional sign-off.

### Step 4: QA (Human-Scan)
Before delivering, verify:
- [ ] No "I am writing to express..."
- [ ] No "passionate about" / "results-driven" / "dynamic"
- [ ] Every claim backed by a specific metric or role
- [ ] Tone reads as confident-but-real, not corporate-robotic
- [ ] Keywords from JD woven in naturally (not stuffed)
- [ ] No more than 4 paragraphs
- [ ] Close focuses on value to employer, not Blake's hopes

## Usage

**Basic command**:
```
Write a cover letter for [Company/Role]
```

**With attached JD**:
```
Generate a cover letter for this posting: [paste JD or URL]
```

**With customization**:
```
Write a cover letter for [role] — emphasize my [specific experience], keep it under 300 words
```

## Example Output Tone

❌ Bad (AI-sounding):
"As a results-driven professional passionate about customer success, I am excited to apply for the CSE role at JLL. I possess extensive experience leveraging stakeholder engagement paradigms to drive synergistic outcomes."

✅ Good (Blake's voice):
"Last quarter at Yooz, I hit 112% of my individual quota — which itself drove our cross-functional team to 225% attainment. That kind of compounding success came from one principle: treat every customer review like an investment in the relationship rather than a checkpoint. Corrigo's customer success model appears built on that same philosophy."

## Output Format

Deliver as clean markdown that can be directly copied:
```
**[Company Name] — [Job Title] Cover Letter**
*Drafted for Blake E. Bridgers*

[Letter body]

---
**Delivery**: Save as .docx at /root/workspace/job_search/[Company]/[Role]-CoverLetter.docx
**Resume**: Use matching resume variant from /root/workspace/job_search/
```

## Pitfalls
- Never generate generic letters — every output must reference specific JD requirements
- Never ignore the Voice & Tone Rules in the SOUL profile
- Never claim experience Blake doesn't have
- Never exceed one page / 400 words (unless user explicitly asks for longer)
- Always ask for the JD if not provided — never fabricate

## Humanize Pass (REQUIRED)

Before delivering any letter, apply the humanizer skill's principles. Cover letters are the #1 place where AI slop shows because they're short, high-stakes prose.

### Strip these AI tells before delivery:

**Prohibited phrases (kill on sight):**
- "I am writing to express my interest in..."
- "As a results-driven professional..."
- "I am passionate about..."
- "I believe I would be a great fit..."
- "At its core," / "The real question is..."
- "It's not just about X, it's about Y" (negative parallelism)
- "Additionally," / "Furthermore," / "Moreover," (transition soup)
- "stands as" / "serves as" / "marks a pivotal" (significance inflation)
- Any sentence ending with "-ing, highlighting..." or "-ing, underscoring..."
- Rule-of-three patterns forced into "A, B, and C" lists without reason
- Em dashes (—) used more than once per letter

**Voice requirements:**
- Use "is/are/has" instead of elaborate constructions ("serves as a testament to", "functions as a catalyst for")
- One sentence short and blunt. Then one sentence longer and more reflective. Vary rhythm.
- Opinions are allowed. "I genuinely believe..." or "Frankly, what caught my eye was..." reads as human.
- Specifics over generalities. "Last Q4 I hit 112% quota" > "I have a track record of strong results"
- Use straight quotes (" ") not curly quotes (" ")
- No emojis. No boldface inline headers. No bulleted "key benefits" lists mid-letter.

### Final QA pass (mandatory before delivery):

Ask yourself: "What makes the below so obviously AI generated?"
Answer briefly. Then revise one more time before delivering.

## Example Output Tone

❌ Bad (AI-sounding):
"As a results-driven professional passionate about customer success, I am excited to apply for the CSE role at JLL. I possess extensive experience leveraging stakeholder engagement paradigms to drive synergistic outcomes."

✅ Good (Blake's voice):
"Last quarter at Yooz, I hit 112% of my individual quota — which itself drove our cross-functional team to 225% attainment. That kind of compounding success came from one principle: treat every customer review like an investment in the relationship rather than a checkpoint. Corrigo's customer success model appears built on that same philosophy."

## Reference Files
| File | Location |
|------|----------|
| Blake's Profile (SOUL) | references/blake-profile.md |
| Humanizer skill | Load via `skill_view(name='creative/humanizer')` for full pattern list |
| JLL CSE App Package | /root/workspace/job_search/#1JOB_SEARCHING/JLL/ |
| Falcon Farms CLs | /root/workspace/job_search/#1JOB_SEARCHING/FALCON FARMS/ |
| Updated Resume | /root/workspace/job_search/#1JOB_SEARCHING/UPDATED RESUME.docx |
| Full Gap Package | /root/workspace/job_search/#1JOB_SEARCHING/full gap package.docx |
