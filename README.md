# ID Card Scanner

**Team 7 - Digital Image Processing Project**

## Team Members
- Abdallah Ahmed Abdelfattah 9230553
- Karim Farid Abdelhamid 9230673
- Mohamed Kamal Abdelrazek 9230798
- Mohamed Hany Abdelmonem 9230818

## Project Overview

Complete ID card scanning system that:
1. **Detects and normalizes ID cards** using edge detection and perspective transformation
2. **Extracts faces** from ID cards automatically
3. **Extracts text** from specific regions using OCR (Tesseract)
4. **Saves masks permanently** for reuse across scanning sessions

## Quick Start

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

You also need Tesseract OCR:
- **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr`
- **macOS:** `brew install tesseract`
- **Windows:** Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

### 2. Run the System
```bash
python id_scanner.py
```

### 3. Choose Option:

**Option 1: Run (Extract Text)**
- Select a saved mask
- Enter image filename (e.g., `image.jpg`)
- Get extracted text and face

**Option 2: Mask Creation**
- Enter image filename
- Enter mask name
- Draw regions with mouse
- Save for future use

**Option 3: Webcam**
- Select a saved mask
- Real-time scanning
- Press SPACE to scan, Q to quit

## Simplified Scanner

A new, simplified script `id_scanner_simple.py` is available for a more straightforward experience.

### Features
- A simple, clean interface with a box to position your ID card.
- Captures the ID card image when you press the 'c' key.
- Extracts the ID number and name (in Arabic) using predefined masks.
- Saves the captured card and the extracted text to the `output` directory.

### How to Run
1.  **Install Arabic language pack for Tesseract:**
    -   **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr-ara`
    -   **macOS:** `brew install tesseract-lang` (and select Arabic)
    -   **Windows:** When installing Tesseract, make sure to select the Arabic language from the list of languages to install.

2.  **Run the simplified scanner:**
    ```bash
    python id_scanner_simple.py
    ```

3.  **Position your ID card** inside the green box on the screen.

4.  **Press 'c'** to capture and process the ID card.

### Masks
The simplified scanner uses two mask files:
- `masks/id mask.json`: For the ID number.
- `masks/name_mask.json`: For the name.

You can edit the coordinates in these JSON files to match the layout of your specific ID card. The coordinates are in the format `[x1, y1, x2, y2]`, representing the top-left and bottom-right corners of the rectangle.

## How It Works

### 1. ID Card Detection & Normalization
- **Canny edge detection** finds card boundaries
- **Contour analysis** identifies rectangular shapes
- **Perspective transformation** normalizes card to 800x500 pixels

### 2. Mask-Based Text Extraction
- **Mouse-drawn regions** define text areas precisely
- **Permanent mask storage** in `masks/` directory
- **OCR optimization** with 4x scaling and preprocessing
- **Number-only extraction** for ID regions, full text for names

### 3. Face Extraction
- **Haar Cascade** detects faces on normalized cards
- **Automatic cropping** with padding
- **High-quality output** for comparison

## File Structure

```
Project/
├── id_scanner.py           # Main CLI application
├── requirements.txt        # Dependencies
├── README.md              # This file
├── masks/                 # Saved mask configurations
├── image.jpg              # Input images
├── face_TIMESTAMP.jpg     # Extracted faces  
├── card_TIMESTAMP.jpg     # Normalized cards
├── region_*.jpg           # Individual regions
└── results_TIMESTAMP.txt  # Extraction results
```

## Usage Examples

### First Time Setup:
1. Run `python id_scanner.py`
2. Choose "2" (Mask Creation)  
3. Enter image: `image.jpg`
4. Enter mask name: `student_id`
5. Draw rectangles around ID number and name
6. Press ENTER to save

### Subsequent Scans:
1. Run `python id_scanner.py`
2. Choose "1" (Run)
3. Select mask: `student_id`  
4. Enter image: `new_card.jpg`
5. Get instant results!

### Real-Time Scanning:
1. Run `python id_scanner.py`
2. Choose "3" (Webcam)
3. Select mask: `student_id`
4. Hold card to camera, press SPACE

## Output Files

Each scan creates timestamped files:
- `face_20241215_143022.jpg` - Extracted face
- `card_20241215_143022.jpg` - Normalized card  
- `region_id_number_20241215_143022.jpg` - ID region
- `results_20241215_143022.txt` - Text results

## Mask Creation Controls

**Mouse:**
- **Click & Drag** - Draw rectangles

**Keyboard:**
- **i** - ID number mode (green rectangles)
- **n** - Name mode (red rectangles)  
- **c** - Clear all rectangles
- **u** - Undo last rectangle
- **ENTER** - Save mask
- **ESC** - Cancel

## Tips for Best Results

### For Card Detection:
- Good lighting, avoid shadows
- Hold card flat and straight
- Fill most of the frame
- Use plain background

### For Mask Creation:
- Draw tight rectangles around text
- Avoid including borders/decorations
- Test with multiple similar cards
- Create separate masks for different card types

## Technical Features

- **Automatic corner ordering** for consistent normalization
- **Multiple preprocessing methods** for OCR optimization
- **Region-specific OCR config** (digits-only for IDs)
- **Permanent mask storage** as JSON files
- **Timestamped outputs** prevent overwrites
- **Real-time webcam processing**

This system provides a complete solution for ID card text extraction with reusable mask configurations!
