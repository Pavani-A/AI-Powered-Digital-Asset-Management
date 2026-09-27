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
- Job reaches Completed.

**Actual Result:** Passed