# Beki StoryMap & Dashboard — Data Onboarding & Content Management Guide

This document explains step-by-step how non-technical users can add, modify, or update story points, narratives, coordinates, images, and overlay layers for the Beki River StoryMap.

---

## 1. Overview of Data Files

The StoryMap uses a simple data structure stored in the `data/` folder:

- **`inputs/Story Map.docx`**: The primary input Word document.
- **`data/story_points.md`**: Human-readable Markdown version of all 10 story locations.
- **`data/story_data.json`**: Structured JSON data used by the website frontend (`js/app.js`).
- **`assets/images/`**: Image folder for location photos (`poi_1.jpg`, `poi_2.jpg`, etc.).

---

## 2. How to Update Story Content

### Method A: Editing via Word Document (`inputs/Story Map.docx`)
1. Open `inputs/Story Map.docx` in Microsoft Word.
2. Edit the titles, coordinates, or paragraph text as needed.
3. Save the document.
4. Run the Python data script in your command line:
   ```bash
   python scripts/convert_docx.py
   ```
5. The script automatically updates `data/story_data.json` and `data/story_points.md`!

---

### Method B: Editing directly in Markdown (`data/story_points.md`) or JSON (`data/story_data.json`)
If you prefer editing formatted text directly:
1. Open `data/story_data.json` in any text editor (VS Code, Notepad++, etc.).
2. Locate the specific POI (e.g. `"id": 1`).
3. Update the fields:
   - `"title"`: Location name
   - `"subtitle"`: Theme subtitle
   - `"lat"` & `"lon"`: Latitude and Longitude in decimal degrees (e.g. `27.51` and `91.16`)
   - `"text"`: Detailed narrative description
   - `"media"`:
     ```json
     "media": {
       "type": "image",
       "url": "assets/images/poi_1.jpg",
       "caption": "Photo of Tsatichhu landslide dam site",
       "alt": "Tsatichhu Landslide Dam"
     }
     ```
4. Save the file and refresh your browser!

---

## 3. Adding Photos and Media

1. Save your photo into `assets/images/`.
2. Name the file clearly (e.g. `poi_1.jpg`, `kurichhu_dam.png`, etc.).
3. Update the `"url"` field in `data/story_data.json` to point to `assets/images/your_image.jpg`.

---

## 4. Hosting on GitHub Pages

The application is completely static (zero backend required).
To host on GitHub Pages:
1. Push the project repository to GitHub.
2. Go to **Repository Settings** -> **Pages**.
3. Under **Build and deployment**, select **Deploy from a branch** and choose `main` / `root`.
4. Click **Save**. Your website will be live in 1-2 minutes!
