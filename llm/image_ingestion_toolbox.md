---
id: BLK-TOOLBOX-IMAGE-INGESTION-V1
name: Image Ingestion Toolbox
type: toolbox
scope: mixed
version: 1.0
status: active
revised: 2026-09-30
summary: Reusable, provenance-aware image inspection with cached sidecar notes and optional standard metadata.
---

# Image Ingestion Toolbox

Use this block when photographs, scans, screenshots, diagrams, or other raster
images must be inspected as project sources. Its purpose is to avoid repeatedly
spending vision tokens on the same image while preserving enough provenance for
another agent or human to verify the analysis.

## Core rule

Inspect once, record what was actually observed, and reuse a fresh companion
note before decoding the image again. A cached description is derived evidence,
not a replacement for the source image. Reopen the image when the question
requires details that the note does not cover, when the note is uncertain, or
when the source has changed.

Do not modify an original image merely to cache an analysis. Embedded metadata
is optional and should normally be written only to a derived copy or after the
user authorizes changing the source. The Markdown sidecar is the authoritative
analysis artifact because it is reviewable, diffable, and can hold provenance
and uncertainty that do not fit reliably in image metadata.

## Companion file and freshness

For `picture.jpg`, create `picture.md` beside it. If that name already belongs
to an unrelated document, use `picture.image-notes.md` and record the collision.

Before trusting a sidecar, compare its recorded source identity with the actual
file. Record at least:

- source filename and relative path;
- SHA-256 digest;
- byte size;
- pixel dimensions and orientation;
- media type;
- original capture time when present;
- analysis creation and update dates;
- tool/model used for visual inspection or OCR; and
- review status: partial, substantial, or complete for a stated purpose.

A mismatched digest makes the cached analysis stale. A matching digest proves
that the bytes are the same, not that an earlier description answers a new
question.

## Sidecar format

Use this compact structure and omit empty optional sections:

```md
# Image Notes — <descriptive title>

## Source
- File:
- SHA-256:
- Size:
- Dimensions/orientation:
- Capture time:
- Analysis updated:
- Tools/model:
- Review scope and status:

## Description
<Concise account of the whole image and its layout.>

## Extracted Content
- Visible text/OCR with regions or reading order
- Tables, labels, marks, values, and other structured content

## Details Relevant to Current Work
- Observation with location in image

## Uncertainty and Legibility
- Ambiguous text, occlusion, blur, glare, crop, handwriting, or inference

## Provenance and Transformations
- Original/derived status; rotation, crop, enhancement, or OCR performed

## Suggested Filename
- Current:
- Proposed:
- Reason:

## Reinspection Triggers
- Details that still require the original pixels or a higher-resolution crop
```

Separate direct observation from interpretation. Preserve uncertain readings
as alternatives rather than silently choosing one. For handwritten scorecards,
record the physical sheet, judge/participant identity, row and column, mark,
corrections or overwriting, and confidence independently.

## Inspection workflow

1. Inventory candidate images without opening all of them at full resolution.
   Capture filenames, dimensions, orientation, timestamps, and hashes.
2. Check for a fresh companion note. Reuse it when it covers the current
   question; cite the sidecar and source image together.
3. Inspect a thumbnail or contact sheet to classify images and find duplicates,
   related views, blank pages, and likely high-value files.
4. Open only relevant images. Use original resolution or targeted crops for
   small print, handwriting, score marks, fine diagrams, or disputed evidence.
5. Use OCR as a draft extraction, not visual truth. Verify names, numbers,
   symbols, checkboxes, decimal marks, and handwriting against the pixels.
6. Write or update the sidecar immediately, including scope and uncertainty.
7. Reuse the sidecar for later work; reopen only for a stated gap or validation.

When several images show one document or event, keep one sidecar per source
image and optionally add a separate synthesis note. Do not overwrite individual
provenance with a combined summary.

## Embedded metadata

When embedded metadata is useful and mutation is authorized, use standard
descriptive fields rather than private EXIF fields:

- `XMP-dc:Title` for a short human-readable title;
- `XMP-dc:Description` for a concise caption/description;
- `IPTC:Caption-Abstract` as the legacy-compatible Description/Caption mapping;
  and
- `XMP-dc:Subject` or `IPTC:Keywords` for controlled search terms.

The IPTC Photo Metadata Standard maps Description/Caption to
`dc:description` in XMP and `2:120 Caption/Abstract` in IIM. Keep the embedded
description short and factual; put detailed extraction, confidence, hashes,
and reasoning in the sidecar. Do not repurpose accessibility Alt Text or
Extended Description as an agent-analysis cache.

Preserve existing metadata and inspect the result after writing. Be aware that
metadata support differs among JPEG, TIFF, PNG, WebP, and other formats, and
that messaging, export, or optimization tools may strip it. Never make embedded
metadata the sole cache.

## Filenames

When names are timestamps, camera counters, hashes, or otherwise opaque,
propose a concise descriptive rename. Include enough stable context to avoid
collisions, for example:

```text
2026-retro-boreal-short-showcase-judge-03-scorecard.jpg
rule-7-worked-example-page-2.png
settings-dialog-export-options.png
```

Do not rename automatically. First check references, manifests, scripts,
sidecars, duplicate names, and whether the timestamp is useful provenance.
Present an old-to-new mapping for approval, then rename the image and its
sidecar together and update known references.

## Validation and reinspection

Reopen the source when:

- the digest differs or freshness cannot be established;
- the current question is outside the recorded review scope;
- a conclusion depends on small, faint, handwritten, cropped, or obscured data;
- two notes or sources conflict;
- exact visual placement, color, geometry, or typography matters; or
- the sidecar contains unresolved uncertainty relevant to the decision.

For material evidence, have a human or independent pass verify transcribed
values before they become official records, regression fixtures, or scoring
inputs.

## Anti-patterns

Avoid:

- repeatedly opening unchanged images without checking their sidecars;
- treating OCR or a prior caption as exact evidence;
- recording a description without a hash and review scope;
- overwriting originals to add convenience metadata;
- stripping capture, rights, or provenance metadata;
- putting long analysis only in an embedded caption;
- silently rotating, cropping, enhancing, or renaming evidence;
- claiming a full review after inspecting only a thumbnail; and
- collapsing multiple score sheets into one unattributed transcription.

## References

- IPTC Photo Metadata Standard and User Guide:
  https://www.iptc.org/std/photometadata/documentation/userguide/
- ExifTool tag names and XMP language alternatives:
  https://exiftool.org/TagNames/
