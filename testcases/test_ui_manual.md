# Manual UI Test Cases

## TC-UI-001 — Natural Language Search

**Objective:** Verify natural-language asset search.

**Steps:**

1. Open the application.
2. Enter `cartoon rabbit`.
3. Click Search.
4. Observe the results.

**Expected Result:**

- Relevant assets are displayed.
- Results are ranked by relevance.
- Relevance scores are displayed.

**Actual Result:** Passed

---

## TC-UI-002 — Image Preview

**Steps:**

1. Search for `sunflower`.
2. Select `sunflower.jpg`.
3. Open the asset details.

**Expected Result:**

- Image preview is displayed.
- Asset metadata is displayed.
- AI Search Context is displayed.
- Original file can be opened.

**Actual Result:** Passed

---

## TC-UI-003 — Video Preview

**Steps:**

1. Search for a video.
2. Select the result.
3. Play the video.

**Expected Result:**

- Video preview loads.
- Video can be played.
- Duration and metadata are displayed.

**Actual Result:** Passed

---

## TC-UI-004 — PDF Preview

**Steps:**

1. Search for a PDF.
2. Select the PDF result.
3. Navigate through the preview.

**Expected Result:**

- PDF preview loads.
- PDF pages can be navigated.
- Metadata is displayed.

**Actual Result:** Passed

---

## TC-UI-005 — File Type Filter

**Steps:**

1. Search for `sunflower`.
2. Select Images.
3. Verify results.
4. Select Videos.
5. Verify results.
6. Select PDFs.
7. Verify results.

**Expected Result:**

Only assets matching the selected file type are displayed.

**Actual Result:** Passed

---

## TC-UI-006 — Library Indexing

**Steps:**

1. Click `Index Library`.
2. Observe the progress indicator.
3. Wait for completion.

**Expected Result:**

- Indexing progress is displayed.
- Processed, successful and failed counts are shown.
- The indexing job reaches `Completed` for the processed batch.

**Actual Result:** Passed

---

## TC-UI-007 — Original File Access

**Objective:** Verify that the original local asset can be accessed from the asset details.

**Steps:**

1. Search for `sunflower`.
2. Select `sunflower.jpg`.
3. Open the asset details.
4. Use the option to open/access the original file.

**Expected Result:**

- The original local file can be opened.
- The file corresponds to the selected asset.

**Actual Result:** Passed

---

## TC-UI-008 — AI Search Context

**Objective:** Verify that AI-generated asset understanding is displayed.

**Steps:**

1. Search for `cartoon rabbit`.
2. Select `big_buck_bunny.jpg`.
3. Open the asset details.
4. Inspect the AI Search Context.

**Expected Result:**

- AI-generated description is displayed.
- The description contains information about the asset.
- The AI-generated context corresponds to the indexed asset.

**Actual Result:** Passed

---

## TC-UI-009 — Failed Asset Handling

**Objective:** Verify that failed asset processing is recorded without preventing the application from functioning.

**Steps:**

1. Run library indexing on the local dataset.
2. Observe assets that fail during processing.
3. Observe the indexing job status and failure count.
4. Continue using the application after indexing.

**Expected Result:**

- Failed assets are recorded as failed.
- Failure information is available.
- The indexing job completes without crashing the application.
- Successfully processed assets remain searchable.

**Actual Result:** Passed

---

## TC-UI-010 — Excluded Asset Handling

**Objective:** Verify that assets marked as excluded do not appear in normal semantic search.

**Steps:**

1. Mark the test PDFs as excluded.
2. Search for `cartoon rabbit`.
3. Observe the search results.
4. Verify that excluded assets are not displayed.

**Expected Result:**

- Excluded assets remain in the local dataset.
- Excluded assets do not appear in normal semantic search.
- Other indexed assets continue to appear normally.

**Actual Result:** Passed