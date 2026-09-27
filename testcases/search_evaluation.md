# Search Evaluation

## Overview

The AI-DAM semantic search was evaluated using 10 natural-language queries across
images, videos, and PDFs. Each query was selected to test a different type of
visual or document-oriented search intent.

The evaluation records the expected asset type/content, observed results,
relevance, and limitations. Results are ranked by semantic similarity score.

---

## Search 1 — `yellow flower`

**User intent:** Find images or videos containing yellow flowers.

**Expected assets:** Sunflower and other yellow-flower imagery.

**Observed results:**
1. `sunflower.jpg` — 50% — Image
2. `test_sunflower.mp4` — 48% — Video
3. `image-102.jpg` — 45% — Image — pink flowers
4. `image-1040.jpg` — 44% — Image — butterfly on white flowers
5. `output_with_metadata_pymupdf.pdf` — 35% — PDF
6. `image-1044.jpg` — 33% — Image — outdoor landscape

**Result:** Strong retrieval of the intended sunflower image and video as the
top two results. Other flower-related imagery was also retrieved.

**Limitation:** Some unrelated PDFs and outdoor images appear lower in the
ranking.

---

## Search 2 — `forest`

**User intent:** Find forest and woodland scenes.

**Expected assets:** Forests, trees, woodland environments, and animals in
forest settings.

**Observed results:**
1. `output_with_metadata_pymupdf.pdf` — 46% — PDF
2. `image-1006.jpg` — 46% — Image — forest road
3. `page-0-Im1.jpg` — 45% — Image — animal in a forest
4. `pdfkit.pdf` — 41% — PDF
5. `annotated_pdf.pdf` — 40% — PDF
6. `image-10.jpg` — 37% — Image — tree with berries
7. `image-1020.jpg` — 33% — Image — large trees
8. `image-1031.jpg` — 33% — Image — cat in wooded area
9. `image-1039.jpg` — 33% — Image — tree and leaves

**Result:** Relevant forest and woodland images were retrieved, including a
forest road and an animal in a forest.

**Limitation:** Several PDFs ranked highly despite not being visually related
to a forest.

---

## Search 3 — `flowers`

**User intent:** Find flower-related images and videos.

**Expected assets:** Different types of flowers and floral scenes.

**Observed results:**
1. `image-102.jpg` — 50% — Image — pink flowers
2. `image-1040.jpg` — 44% — Image — butterfly on white flowers
3. `output_with_metadata_pymupdf.pdf` — 41% — PDF
4. `image-1043.jpg` — 41% — Image — floral pattern
5. `pdfkit.pdf` — 40% — PDF
6. `test_sunflower.mp4` — 39% — Video — sunflower
7. `image-1016.jpg` — 35% — Image — deer in a flower field
8. `image-1038.jpg` — 34% — Image — red rose

**Result:** Multiple relevant flower assets were retrieved across images and
video.

**Limitation:** Some unrelated PDFs were ranked relatively highly.

---

## Search 4 — `people`

**User intent:** Find assets containing people or human subjects.

**Expected assets:** Images containing one or more people.

**Observed results:**
1. `output_with_metadata_pymupdf.pdf` — 42% — PDF
2. `image-1024.jpg` — 38% — Image — family with a child
3. `pdfkit.pdf` — 37% — PDF
4. `libreoffice-form.pdf` — 31% — PDF
5. `annotated_pdf.pdf` — 31% — PDF
6. `pdflatex-forms.pdf` — 30% — PDF
7. Image containing two people — 31%
8. Image containing people — 30%

**Result:** The family image was retrieved near the top, and other images
containing people were also returned.

**Limitation:** Text-based PDFs frequently appeared above or alongside visual
matches.

---

## Search 5 — `animal`

**User intent:** Find images containing animals.

**Expected assets:** Animals such as dogs, cats, squirrels, reptiles, and
other wildlife.

**Observed results:**
1. `output_with_metadata_pymupdf.pdf` — 43% — PDF
2. `page-0-Im1.jpg` — 41% — Image — small animal in forest
3. `pdfkit.pdf` — 40% — PDF
4. `image-1001.jpg` — 40% — Image — dog
5. `image.jpg` — 40% — Image — animal in zoo enclosure
6. `wrong-references.pdf` — 39% — PDF
7. Additional animal images — 37–36%

**Result:** Multiple animal images were successfully retrieved, including a
forest animal, dog, zoo animal, lizard, and cat.

**Limitation:** Several PDFs appeared among the higher-ranked results.

---

## Search 6 — `nature`

**User intent:** Find natural environments and outdoor nature scenes.

**Expected assets:** Forests, trees, mountains, plants, landscapes, and
outdoor scenes.

**Observed results:**
1. `output_with_metadata_pymupdf.pdf` — 44% — PDF
2. `image-1006.jpg` — 39% — Image — forest road
3. `image-10.jpg` — 39% — Image — tree branch with berries
4. `annotated_pdf.pdf` — 36% — PDF
5. `page-0-Im1.jpg` — 34% — Image — animal in forest
6. `pdfkit.pdf` — 34% — PDF
7. `pdflatex-forms.pdf` — 34% — PDF
8. `image-1047.jpg` — 33% — Image — mountain/cloud landscape
9. `image-1021.jpg` — 33% — Image — mountain landscape
10. `image-1020.jpg` — 33% — Image — large tree

**Result:** Several natural scenes were retrieved successfully.

**Limitation:** Unrelated PDFs continued to receive relatively high semantic
similarity scores.

---

## Search 7 — `document with text`

**User intent:** Find text-based documents.

**Expected assets:** PDFs containing readable document text.

**Observed results:**
1. `annotated_pdf.pdf` — 57% — PDF
2. `google-doc-document.pdf` — 48% — PDF
3. `002-trivial-libre-office-writer...` — 46% — PDF
4. `pdfkit.pdf` — 45% — PDF
5. `pdflatex-image.pdf` — 43% — PDF
6. `multicolumn.pdf` — 43% — PDF

**Result:** Strong retrieval. The highest-ranked results were all PDFs with
textual/document content.

**Limitation:** No major visual-search issue was observed for this query.

---

## Search 8 — `car`

**User intent:** Find images containing cars or vehicles.

**Expected assets:** Cars and other vehicle imagery.

**Observed results:**
1. `image-1017.jpg` — 45% — Image — gray car on rocky beach
2. `image-1036.jpg` — 42% — Image — Tesla Model S
3. `wrong-references.pdf` — 41% — PDF
4. `output_with_metadata_pymupdf.pdf` — 41% — PDF
5. `image-1.jpg` — 39% — Image — toy car
6. `pdfkit.pdf` — 39% — PDF

**Result:** Multiple car images were retrieved, with two clearly relevant car
images occupying the top two positions.

**Limitation:** Some PDFs were also ranked highly.

---

## Search 9 — `outdoor scene`

**User intent:** Find general outdoor scenes.

**Expected assets:** Forests, fields, beaches, mountains, and other outdoor
environments.

**Observed results:**
1. `image-1006.jpg` — 47% — Image — forest road
2. `image-1012.jpg` — 47% — Image — field
3. `image-1013.jpg` — 46% — Image — beach/dunes
4. `image-1020.jpg` — 46% — Image — large trees
5. `image-1044.jpg` — 45% — Image — landscape with hot-air balloons
6. `output_with_metadata_pymupdf.pdf` — 45% — PDF
7. Additional outdoor images — 45–44%

**Result:** Strong broad semantic retrieval. Most of the high-ranking visible
results were relevant outdoor scenes across different environments.

**Limitation:** An unrelated PDF still appeared among the higher-ranked
results.

---

## Search 10 — `mountain landscape`

**User intent:** Find mountain landscapes.

**Expected assets:** Mountain ranges, snowy mountains, valleys, and related
landscape imagery.

**Observed results:**
1. `image-1047.jpg` — 59% — Image — aerial mountain range above clouds
2. `image-1021.jpg` — 55% — Image — mountain range
3. `image-103.jpg` — 52% — Image — outdoor/window scene
4. `image-104.jpg` — 50% — Image — snowy mountain landscape and village
5. `output_with_metadata_pymupdf.pdf` — 41% — PDF
6. `image-1006.jpg` — 40% — Image — forest road
7. `image-1044.jpg` — 38% — Image — landscape with hot-air balloons
8. `image-10.jpg` — 37% — Image — tree/berries
9. `image-1012.jpg` — 37% — Image — field
10. `image-1005.jpg` — 37% — Image — night sky
11. `image-1017.jpg` — 36% — Image — car on rocky coast
12. `image-1020.jpg` — 36% — Image — large trees

**Result:** Strong retrieval of mountain imagery. The first, second, and fourth
results are directly relevant mountain scenes.

**Limitation:** Broader outdoor/nature images and an unrelated PDF also appear
lower in the ranking.

---

## Overall Findings

### What worked

- Natural-language semantic queries successfully retrieved visually related
  images and videos.
- Queries did not need to exactly match filenames.
- The system retrieved related concepts, such as `yellow flower` returning
  sunflower assets.
- Cross-media retrieval worked: image, video, and PDF assets could appear in
  the same search results.
- Text-oriented queries such as `document with text` successfully retrieved
  text-based PDFs.

### Observed limitations

- Some short or generic PDFs received relatively high semantic similarity
  scores for visual queries.
- Broad queries such as `nature` and `outdoor scene` naturally produced a
  wider range of related assets.
- Semantic similarity does not guarantee literal keyword relevance.
- The evaluation demonstrates that ranking is based on embedding similarity
  rather than exact keyword matching.

### Special handling during evaluation

Four noisy/non-useful PDFs were marked as `excluded` rather than deleted:

- `inline-image.pdf`
- `habibi.pdf`
- `habibi-oneline-cmap.pdf`
- `habibi-rotated.pdf`

These files remain in the local dataset but are excluded from normal search
results.