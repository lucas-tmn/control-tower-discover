# Repository Principles

**Principle: the repository is a mirror of validated knowledge, not a
container we fill in advance.**

1. **No empty scaffolding.** A folder or file exists only when it holds
   real, evidence-backed content. Structure is allowed to be incomplete;
   it is not allowed to be fake.
2. **Repository follows Knowledge, not the reverse.** We do not design the
   ideal folder structure first and hunt for content to fit it. As
   Decision Knowledge is discovered, its shape tells us what the
   repository needs.
3. **Evidence before Architecture.** No structural decision (a new folder,
   a new schema field) is made until there is discovered evidence that
   requires it.
4. **Knowledge is promoted, not created.** Moving something into a
   governed location (e.g. from a draft note into `02_Discovery/`) means
   it has evidence behind it — promotion is a statement that something
   has been validated enough to trust, not a relabeling exercise.
5. **AI is a consumer, not a starting point.** Nothing in the repository
   is structured for a future AI feature before it has proven useful to a
   human reviewing it first.

This directly reflects the lesson learned from the GitHub repo scaffold
review: the "90 empty files" pattern is the one failure mode this set of
principles exists to prevent — and the standard this pack itself is held
to (see `Worked_Examples.md` for where that standard is actually applied).
