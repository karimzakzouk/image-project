import cv2
import numpy as np
from PIL import Image
import pytesseract
import re
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

class MaskCreatorUI:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        self.original = self.image.copy()
        self.display_image = self.image.copy()
        self.height, self.width = self.image.shape[:2]
        
        # Scale image if too large
        self.scale = 1.0
        max_height = 800
        if self.height > max_height:
            self.scale = max_height / self.height
            new_width = int(self.width * self.scale)
            new_height = int(self.height * self.scale)
            self.display_image = cv2.resize(self.display_image, (new_width, new_height))
        
        self.display_height, self.display_width = self.display_image.shape[:2]
        
        # Drawing state
        self.drawing = False
        self.current_rect = None
        self.start_point = None
        self.rectangles = {'face': None, 'id': None}
        self.current_mode = 'face'  # 'face' or 'id'
        
        self.window_name = 'ID Card Mask Creator'
        
    def mouse_callback(self, event, x, y, flags, param):
        temp_image = self.display_image.copy()
        
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                cv2.rectangle(temp_image, self.start_point, (x, y), 
                            (0, 255, 0) if self.current_mode == 'face' else (255, 0, 0), 2)
                self._draw_existing_rects(temp_image)
                self._draw_instructions(temp_image)
                cv2.imshow(self.window_name, temp_image)
                
        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing:
                self.drawing = False
                x1, y1 = self.start_point
                x2, y2 = x, y
                
                # Ensure coordinates are ordered correctly
                x_min, x_max = min(x1, x2), max(x1, x2)
                y_min, y_max = min(y1, y2), max(y1, y2)
                
                # Convert to original image coordinates
                orig_x = int(x_min / self.scale)
                orig_y = int(y_min / self.scale)
                orig_w = int((x_max - x_min) / self.scale)
                orig_h = int((y_max - y_min) / self.scale)
                
                self.rectangles[self.current_mode] = (orig_x, orig_y, orig_w, orig_h)
                
                # Redraw
                self._draw_existing_rects(temp_image)
                self._draw_instructions(temp_image)
                cv2.imshow(self.window_name, temp_image)
    
    def _draw_existing_rects(self, image):
        """Draw saved rectangles on the image"""
        if self.rectangles['face']:
            x, y, w, h = self.rectangles['face']
            # Scale to display coordinates
            dx = int(x * self.scale)
            dy = int(y * self.scale)
            dw = int(w * self.scale)
            dh = int(h * self.scale)
            cv2.rectangle(image, (dx, dy), (dx+dw, dy+dh), (0, 255, 0), 2)
            cv2.putText(image, 'FACE', (dx, dy-5), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (0, 255, 0), 2)
        
        if self.rectangles['id']:
            x, y, w, h = self.rectangles['id']
            # Scale to display coordinates
            dx = int(x * self.scale)
            dy = int(y * self.scale)
            dw = int(w * self.scale)
            dh = int(h * self.scale)
            cv2.rectangle(image, (dx, dy), (dx+dw, dy+dh), (255, 0, 0), 2)
            cv2.putText(image, 'ID NUMBER', (dx, dy-5), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (255, 0, 0), 2)
    
    def _draw_instructions(self, image):
        """Draw instructions on the image"""
        instructions = [
            f"Mode: {self.current_mode.upper()} ({'GREEN' if self.current_mode == 'face' else 'BLUE'})",
            "Draw rectangle around area",
            "Press 'F' for Face mode",
            "Press 'I' for ID mode",
            "Press 'R' to reset current",
            "Press 'S' to save & continue",
            "Press 'Q' to quit"
        ]
        
        y_offset = 30
        for i, text in enumerate(instructions):
            color = (0, 255, 0) if i == 0 and self.current_mode == 'face' else (255, 255, 255)
            if i == 0 and self.current_mode == 'id':
                color = (255, 0, 0)
            cv2.putText(image, text, (10, y_offset + i*25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    def create_masks(self):
        """Main loop for creating masks"""
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        while True:
            temp_image = self.display_image.copy()
            self._draw_existing_rects(temp_image)
            self._draw_instructions(temp_image)
            cv2.imshow(self.window_name, temp_image)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('f') or key == ord('F'):
                self.current_mode = 'face'
                print("Switched to FACE mode (green)")
                
            elif key == ord('i') or key == ord('I'):
                self.current_mode = 'id'
                print("Switched to ID mode (blue)")
                
            elif key == ord('r') or key == ord('R'):
                self.rectangles[self.current_mode] = None
                print(f"Reset {self.current_mode.upper()} rectangle")
                
            elif key == ord('s') or key == ord('S'):
                if self.rectangles['face'] and self.rectangles['id']:
                    cv2.destroyAllWindows()
                    return self.rectangles
                else:
                    print("Please draw both FACE and ID rectangles before saving!")
                    
            elif key == ord('q') or key == ord('Q'):
                cv2.destroyAllWindows()
                return None
        
        cv2.destroyAllWindows()
        return None


class IDCardProcessor:
    def __init__(self, id_image_path, mask_config_path='mask_config.json'):
        self.image_path = id_image_path
        self.mask_config_path = mask_config_path
        self.image = cv2.imread(id_image_path)
        if self.image is None:
            raise ValueError(f"Could not load image from {id_image_path}")
        
        self.height, self.width = self.image.shape[:2]
        self.masks = self.load_masks()
        
    def load_masks(self):
        """Load saved mask configuration"""
        if Path(self.mask_config_path).exists():
            with open(self.mask_config_path, 'r') as f:
                return json.load(f)
        return None
    
    def save_masks(self, masks):
        """Save mask configuration"""
        with open(self.mask_config_path, 'w') as f:
            json.dump(masks, f, indent=2)
        print(f"✓ Masks saved to {self.mask_config_path}")
    
    def create_mask_overlay(self, face_rect, id_rect):
        """Create a semi-transparent mask overlay with cutouts"""
        overlay = self.image.copy()
        mask = np.zeros_like(overlay)
        
        # Create semi-transparent dark overlay
        cv2.rectangle(mask, (0, 0), (self.width, self.height), (0, 0, 0), -1)
        
        # Cut out the face and ID areas
        fx, fy, fw, fh = face_rect
        ix, iy, iw, ih = id_rect
        
        mask[fy:fy+fh, fx:fx+fw] = overlay[fy:fy+fh, fx:fx+fw]
        mask[iy:iy+ih, ix:ix+iw] = overlay[iy:iy+ih, ix:ix+iw]
        
        # Draw green rectangles around cutouts
        cv2.rectangle(mask, (fx, fy), (fx+fw, fy+fh), (0, 255, 0), 2)
        cv2.rectangle(mask, (ix, iy), (ix+iw, iy+ih), (0, 255, 0), 2)
        cv2.putText(mask, 'FACE', (fx, fy-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(mask, 'ID', (ix, iy-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Blend with original image
        alpha = 0.6
        result = cv2.addWeighted(overlay, alpha, mask, 1-alpha, 0)
        
        return result
    
    def extract_id_number(self, id_rect):
        """Extract ID number using OCR from specified region"""
        ix, iy, iw, ih = id_rect
        id_region = self.image[iy:iy+ih, ix:ix+iw]
        
        # Preprocess for better OCR
        gray = cv2.cvtColor(id_region, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Use pytesseract for OCR
        text = pytesseract.image_to_string(thresh, config='--psm 6')
        
        # Extract ID numbers
        id_patterns = re.findall(r'[A-Z0-9]{5,}', text.replace(' ', ''))
        
        return {
            'raw_text': text.strip(),
            'id_numbers': id_patterns,
            'primary_id': id_patterns[0] if id_patterns else None
        }
    
    def crop_face(self, face_rect, output_path='face_crop.jpg'):
        """Crop and save the face photo"""
        fx, fy, fw, fh = face_rect
        face_crop = self.image[fy:fy+fh, fx:fx+fw]
        
        cv2.imwrite(output_path, face_crop)
        return face_crop
    
    def process(self, show_results=True, save_outputs=True):
        """Main processing function"""
        if not self.masks:
            print("No mask configuration found! Please create masks first.")
            return None
        
        face_rect = tuple(self.masks['face'])
        id_rect = tuple(self.masks['id'])
        
        # Create mask overlay
        masked_image = self.create_mask_overlay(face_rect, id_rect)
        
        # Extract ID information
        id_info = self.extract_id_number(id_rect)
        
        # Crop face
        face_crop = self.crop_face(face_rect)
        
        results = {
            'id_info': id_info,
            'face_rect': face_rect,
            'id_rect': id_rect,
            'masked_image': masked_image,
            'face_crop': face_crop
        }
        
        # Display results
        if show_results:
            cv2.imshow('ID Card with Mask Overlay', masked_image)
            cv2.imshow('Extracted Face', face_crop)
            print("\n=== Extracted ID Information ===")
            print(f"Raw OCR Text: {id_info['raw_text']}")
            print(f"Detected ID Numbers: {id_info['id_numbers']}")
            print(f"Primary ID: {id_info['primary_id']}")
            print("\nPress any key to close windows...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        # Save outputs
        if save_outputs:
            cv2.imwrite('id_card_masked.jpg', masked_image)
            cv2.imwrite('face_extracted.jpg', face_crop)
            print("\n✓ Saved: id_card_masked.jpg")
            print("✓ Saved: face_extracted.jpg")
        
        return results


def main():
    print("=== ID Card Processor ===\n")
    print("1. Create new mask configuration")
    print("2. Process ID card with existing masks")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        # File selection
        root = tk.Tk()
        root.withdraw()
        image_path = filedialog.askopenfilename(
            title="Select ID Card Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if not image_path:
            print("No image selected!")
            return
        
        # Create masks
        print(f"\nLoaded: {image_path}")
        print("Creating mask UI...")
        
        ui = MaskCreatorUI(image_path)
        masks = ui.create_masks()
        
        if masks:
            processor = IDCardProcessor(image_path)
            processor.save_masks(masks)
            print("✓ Masks saved successfully!")
            
            # Ask if user wants to process now
            process_now = input("\nProcess this ID card now? (y/n): ").strip().lower()
            if process_now == 'y':
                processor.process()
        else:
            print("Mask creation cancelled.")
            
    elif choice == '2':
        # File selection
        root = tk.Tk()
        root.withdraw()
        image_path = filedialog.askopenfilename(
            title="Select ID Card Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if not image_path:
            print("No image selected!")
            return
        
        processor = IDCardProcessor(image_path)
        if processor.masks:
            processor.process()
        else:
            print("No mask configuration found! Please create masks first (option 1).")
            
    elif choice == '3':
        print("Goodbye!")
        return
    else:
        print("Invalid option!")


if __name__ == "__main__":
    main()