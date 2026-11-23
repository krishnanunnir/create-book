# Writing the book

Read this before Claude writes any chapter. Web-article collections don't need it.

## Why the process looks like this

A reader with a book is alone with it. Five facts about that reader set every rule
below. When a rule doesn't fit a case, go back to the fact behind it.

1. **They can't ask.** Every question they would ask has to be answered on the page,
   before it comes up. So each concept is grounded before it is used, and a fresh
   reader tests each chapter.
2. **They hold only a few new ideas at once.** So each chapter has one job and 2–4 new
   concepts, each thing keeps one name, and diagrams grow one part at a time.
3. **They understand a thing when they can predict what it does.** A label or a
   metaphor feels like understanding but doesn't let them predict. So the literal
   mechanism comes first, then a concrete trace. An analogy is a handle, and you say
   where it breaks.
4. **They read in short sittings, on a phone.** So sections are short and findable in
   the TOC, and each chapter ends by stating what it established.
5. **They trust the book, and every sentence costs them attention.** So claims are
   cited at their real confidence, and sentences that carry nothing are cut.

A concept in the wrong order is cheap to fix in an outline and expensive to fix in a
draft. That sets the order of work: brief, outline (approved by the user), one
chapter at a time, edit pass, reader test, whole-book pass.

## 1. The reader (default)

Unless the user says otherwise, the reader is:

- a software engineer who reads code and knows HTTP, JSON, databases, caches, Git
  and at least one mainstream language. **Never explain these**;
- a **true beginner in the book's topic**: school maths only, no jargon of the
  field. Treat them as a beginner, not as a quick reader to rush. Experience in
  software does not make the new topic obvious;
- someone who learns best when an idea is **built up from the smallest working
  version**, the way Alex Xu's *System Design Interview* builds a design: start
  tiny, see what breaks, fix it, repeat.

Assume nothing about the book's topic and a lot about software in general. Don't
speed up once an idea is grounded: each new idea gets the same slow build.

If the book isn't for software engineers (cooking, history, personal finance), keep
the second and third points and replace the first with what the brief says the
reader already knows. Draw the analogies in §4 from that knowledge, not from
backend systems.

The user found a first draft written for a "quick, competent" reader too high-level
to learn from: terms arrived with one-line definitions, mechanisms were stated
instead of worked, and they couldn't predict anything from it. Err slow.

## 2. Brief (`brief.md`)

Ask once, as numbered questions the user can answer in shorthand ("1: yes, 3: skip").
Skip any question the request already answers.

1. What should the reader be able to do or decide after reading?
2. Why do they want it now? Every chapter should serve this mission.
3. What do they already know about the topic, and do they hold a wrong idea about it?
4. Rough length: a short guide (5–8 chapters) or a full book (10–20)?
5. Is there a sample of writing whose voice to match? (Optional.)
6. Which sources to build on: docs, papers, articles, the user's notes?

Record the answers and the **prerequisites**, the concepts the reader brings in. The
reader profile above gives most of them.

## 3. Outline (`outline.md`), approved before drafting

The outline is where fact 1 and fact 2 get enforced. For each chapter, write:

```text
## 4. Idempotency keys
Job: make retries safe without a distributed lock
Introduces: idempotency key, dedupe window
Requires: at-least-once delivery (ch 2), retry (ch 3)
Example: double-charged card from a retried POST
Analogy: a coat-check ticket
```

- **Grounding.** A chapter may only require prerequisites or concepts an earlier
  chapter introduces. If a chapter needs something nothing has grounded, add a
  grounding chapter or section before it, or move the concept to the prerequisites
  and say so in the intro.
- **One job per chapter.** Two chapters with the same job: merge them. A job with
  "and" in it: consider splitting.
- **2–4 new concepts per chapter.** Past that, nothing sticks.
- **A running example.** Name each chapter's example up front. Prefer one example that
  grows across the book over a new toy each chapter, since the reader already holds
  its details. Pick something **everyone has used** (a shop's help bot, a URL
  shortener, a chat app), never one tied to the user's own niche project: a too
  specific example makes the reader learn the example instead of the idea. For
  foundations chapters, a tiny example per chapter, worked by hand, often beats
  forcing the running example in.
- **A leading word.** Look for one coined term or image the book can hang on. It helps
  the title, the cover and the transitions.
- **The glossary.** The `Introduces` lines, in order, are the glossary. After a term is
  introduced, use it the same way everywhere.

Show the outline and change it until the user approves it.

## 4. Drafting a chapter

Draft one chapter per turn, save it to `md/NN.md`, and hand it to the user to review.
Chapter 1 is a gate: don't start chapter 2 until the user approves chapter 1, since it
fixes the voice, depth and length every later chapter follows.
When the user asks to co-write a chapter, build it block by block instead: offer 2–3
openings, let them pick, and after each block ask what the reader needs next.

**Opening.** Start with the problem or a concrete case the reader recognises: an
outage, a bug, a design question. Never "In this chapter we will…", and never restate
the heading as the first sentence.

**Build it by hand first.** The strongest chapters make the reader build a tiny
working version of the idea with real numbers: a next-word guesser from counting three
sentences, a one-knob model trained by hand, a tokenizer from merging letter pairs.
Then show what breaks (it loops, it can't see far, the table explodes), fix it, and
show what breaks next. Each fix is the motivation for the next concept, so nothing
arrives unexplained. Only after the toy works, say what the real system keeps and
what it changes, often as a small side-by-side table. Run any code and use its real
output.

**Each new concept, in this order:**

1. The problem it solves, in the running example.
2. The idea in one or two plain sentences, then its name, so the idea and the term
   land together. State the literal mechanism here: "When an item scrolls out past
   the buffer, both its DOM node and its in-memory data are evicted."
3. A concrete example: real values, a short trace, a code block or a table. A walk
   through what happens as the reader does the thing (sends the request, then retries
   it) often lands better than a description.
4. An analogy, preferably to something backend-side the reader knows: a database
   index, a queue, a cache, a mutex. It adds to the mechanism and never replaces it.
   Then say **where the analogy breaks**.
5. The cost, trade-off or failure mode.

**Few diagrams.** The reader is often on a Kindle. Prefer worked tables and
step-by-step traces ("text so far | picked") to box drawings, and use at most one or
two small diagrams per chapter, only where text can't do the job.

**Build diagrams up.** When a diagram is needed for something with three or more
moving parts, draw a short series instead of one diagram with everything in it. Each diagram redraws the last
one and adds one part: A→B, then A→B→C, then the return edge. The reader watches the
system assemble. One complete diagram saved for the end is reference, not teaching.
Small steps also keep each diagram inside the 52-character width.

**Rules while drafting:**

- **Define before display.** Explain every term and parameter before a diagram, table
  or code block uses it.
- **Format by job.** Prose carries an argument. A list is for items that really are
  parallel. A table is for three or more items with the same fields (2–3 columns on a
  phone). A `>` callout is for an aside that would break the flow. A code block is for
  anything multi-line or runnable.
- **Explain, don't list.** A chapter explains and may hold a view. Tables of flags,
  constants and API members are reference. Keep them dry and put them in an appendix
  or the glossary, not in the middle of an explanation.
- **Be specific.** "A column rename fails the build", not "schema changes can cause
  issues". Make every "this", "it" and "which" point at one obvious noun, never at a
  whole clause. Split sentences over about 25 words. Never write "simply" or "easy".
- **Short units.** Paragraphs of 2–5 sentences. A `##` section at least every
  800–1,000 words, since sections are how readers find their place in the TOC.
- **Cite at the source's confidence.** Cite claims about real systems. Never invent
  numbers, dates or quotes. Mark your own inferences as inferences, say what the
  sources don't answer, and don't turn an author's hedge into a firm claim.
- **Answer the "wait, why?"** Each worked example raises small questions: why the
  numbers add to 1, which option wins a tie, why every pair needs a row. Answer them
  in a sentence where they come up.
- **Define everywhere.** A term used in an answer, a callout or an interview section
  must be defined too, before that point. Don't use "frozen" before training, or
  "greedy" only in the answers.
- **Closing.** End with a short "What you now know" list, then state the chapter's
  one takeaway in specific terms. Then bridge forward
  by naming the problem the next chapter solves. Vary the wording, not "In the next
  chapter…" every time.
- **Check yourself.** In a book meant to teach (not a reference book), end with 3
  questions that make the reader recall or apply the idea. Put the answers at the very
  end of the chapter.

## 5. Edit pass (each chapter)

Each tell below spends the reader's attention (fact 5) without adding anything. If the
`humanizer` skill is installed, run it on the chapter file. Otherwise fix these,
strongest first:

1. **Not X but Y.** "It's not just a cache, it's a contract." State Y. Keep a contrast
   only when the reader really holds belief X.
2. **One-line closers** that restate the paragraph: "That's the real win."
3. **Run-ups:** "Let's dive in", "Here's the thing", "Now let's look at".
4. **Forced triads:** three adjectives or examples where one or two do the work.
5. **Inflated significance:** "plays a crucial role", "a testament to", "pivotal".
6. **False agency:** "the data tells us", "the system decides". Name who or what acts.
7. **Decorative bold and headings.** Bold only terms on first use and real warnings.
8. **Writing about the book** instead of the topic: "As we saw", "This section covers".
9. **Framing labels** that flag instead of say: "the key insight", "the tricky part",
   "here's where it gets interesting", "at its core", "TL;DR". Just say it.
10. **Tidy closers and mirror sentences:** "the rest follows", "it all falls out",
    "A without B, or B without A".
11. **Abstract metaphor nouns:** substrate, primitive, surface, wedge, flywheel, north
    star, paradigm. Use the concrete word.
12. **Portable sentences.** Cut any sentence that could appear unchanged in another
    book on another topic. Name the mechanism or the number instead.

Leave alone: quotes, names, and deliberate voice such as a real aside or honest
uncertainty. After editing, check that no fact, number, name or claim was lost or
changed.

Then run the checker on the sources. It flags many of these tells, plus long
paragraphs, long stretches without a heading and wide code lines:

```bash
python3 $SKILL/scripts/lint-md.py md/*.md
```

## 6. Reader test (each chapter)

This is how fact 1 gets checked: you can't tell where a reader gets lost, because you
already know the answer. Spawn a fresh subagent that has not seen this conversation.
Tell it to read as the beginner from §1. Give it only the prerequisites, the glossary
so far and the chapter text, and ask it to:

1. state the chapter's main point in one sentence;
2. answer 3–5 questions a reader would have after reading it (write them first);
3. list where it got lost or felt rushed, and every term or fact it had to assume,
   quoting the sentence;
4. list anything that felt condescending or padded.

If its sentence doesn't match the chapter's job, or it had to assume something not
yet grounded, fix the chapter and test again.

## 7. Whole-book pass

- Read the "First / last sentence" output of `lint-md.py` from top to bottom. Each
  chapter's last sentence should set up the next chapter's first.
- Check that each glossary term is introduced exactly once, before its first use.
- Add a short intro (who the book is for, what it assumes, how it is organised) and a
  `# Glossary` chapter at the end, built from the outline's `Introduces` lines.
