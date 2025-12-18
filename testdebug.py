"""
Debug helper để test PaddleOCR extraction
Chạy file này để kiểm tra tại sao PDF không đọc được
"""

from paddleocr import PaddleOCR
from pdf2image import convert_from_path
from PIL import Image
import os


def test_paddleocr_basic():
    """Test PaddleOCR cơ bản với một ảnh"""
    print("=" * 70)
    print("TEST 1: PaddleOCR Basic Test")
    print("=" * 70)

    # Tạo một ảnh test đơn giản
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(img)

    try:
        # Thử dùng font mặc định
        draw.text((10, 30), "Hello World Test 123", fill='black')
    except:
        draw.text((10, 30), "Hello World Test 123", fill='black')

    img.save("test_image.jpg")
    print("Created test_image.jpg")

    # Test OCR
    ocr = PaddleOCR(lang='en', use_angle_cls=True, use_gpu=False)
    result = ocr.ocr("test_image.jpg", cls=True)

    print(f"\nResult type: {type(result)}")
    print(f"Result: {result}")

    if result and len(result) > 0:
        print("\n✓ PaddleOCR is working!")
        return True
    else:
        print("\n✗ PaddleOCR returned empty result")
        return False


def test_pdf_to_image(pdf_path):
    """Test chuyển PDF sang ảnh"""
    print("\n" + "=" * 70)
    print("TEST 2: PDF to Image Conversion")
    print("=" * 70)

    if not os.path.exists(pdf_path):
        print(f"✗ File not found: {pdf_path}")
        return False

    print(f"Converting PDF: {pdf_path}")

    try:
        pages = convert_from_path(pdf_path)
        print(f"✓ Converted {len(pages)} page(s)")

        # Lưu trang đầu tiên
        if pages:
            pages[0].save("debug_page_0.jpg", "JPEG")
            print(f"✓ Saved debug_page_0.jpg (size: {pages[0].size})")
            return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_ocr_on_pdf_image(image_path="debug_page_0.jpg"):
    """Test OCR trên ảnh từ PDF"""
    print("\n" + "=" * 70)
    print("TEST 3: OCR on PDF Image")
    print("=" * 70)

    if not os.path.exists(image_path):
        print(f"✗ Image not found: {image_path}")
        print("Run test_pdf_to_image first!")
        return False

    print(f"Running OCR on: {image_path}")

    ocr = PaddleOCR(lang='en', use_angle_cls=True, use_gpu=False)
    result = ocr.ocr(image_path, cls=True)

    print(f"\nResult type: {type(result)}")
    print(f"Result length: {len(result) if result else 0}")
    print(f"\nFull result:")
    print(result)

    # Parse result
    if result is None:
        print("\n✗ Result is None")
        return False

    text_lines = []
    if isinstance(result, list) and len(result) > 0:
        page_result = result[0] if isinstance(result[0], list) else result

        print(f"\nPage result type: {type(page_result)}")
        print(f"Page result length: {len(page_result)}")

        for i, line in enumerate(page_result):
            print(f"\n--- Line {i} ---")
            print(f"Type: {type(line)}")
            print(f"Content: {line}")

            if line and isinstance(line, (list, tuple)) and len(line) >= 2:
                text_info = line[1]
                if isinstance(text_info, (list, tuple)) and len(text_info) > 0:
                    text = text_info[0]
                    confidence = text_info[1] if len(text_info) > 1 else 0
                    text_lines.append(text)
                    print(f"Extracted: '{text}' (confidence: {confidence:.2f})")

    print(f"\n{'=' * 70}")
    print(f"TOTAL EXTRACTED: {len(text_lines)} lines")
    print(f"{'=' * 70}")

    if text_lines:
        print("\nExtracted text:")
        for i, line in enumerate(text_lines):
            print(f"  [{i}] {line}")
        return True
    else:
        print("\n✗ No text extracted")
        return False


def test_different_ocr_configs(image_path="debug_page_0.jpg"):
    """Test các config khác nhau của PaddleOCR"""
    print("\n" + "=" * 70)
    print("TEST 4: Different OCR Configurations")
    print("=" * 70)

    if not os.path.exists(image_path):
        print(f"✗ Image not found: {image_path}")
        return False

    configs = [
        {"lang": "en", "use_angle_cls": True, "use_gpu": False},
        {"lang": "en", "use_angle_cls": False, "use_gpu": False},
        {"lang": "en", "det": True, "rec": True, "cls": False},
    ]

    for i, config in enumerate(configs):
        print(f"\n--- Config {i + 1}: {config} ---")
        try:
            ocr = PaddleOCR(**config)
            result = ocr.ocr(image_path, cls=config.get("use_angle_cls", True))

            if result and len(result) > 0:
                line_count = len(result[0]) if isinstance(result[0], list) else len(result)
                print(f"✓ Extracted {line_count} lines")
            else:
                print(f"✗ No result")
        except Exception as e:
            print(f"✗ Error: {e}")


def full_debug_pipeline(pdf_path):
    """Chạy toàn bộ debug pipeline"""
    print("\n" + "#" * 70)
    print("# FULL DEBUG PIPELINE")
    print("#" * 70)

    results = []

    # Test 1: Basic OCR
    print("\n1️⃣  Testing basic OCR...")
    results.append(("Basic OCR", test_paddleocr_basic()))

    # Test 2: PDF to Image
    print("\n2️⃣  Testing PDF to Image conversion...")
    results.append(("PDF to Image", test_pdf_to_image(pdf_path)))

    # Test 3: OCR on PDF image
    print("\n3️⃣  Testing OCR on PDF image...")
    results.append(("OCR on PDF", test_ocr_on_pdf_image()))

    # Test 4: Different configs
    print("\n4️⃣  Testing different configurations...")
    test_different_ocr_configs()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")

    # Cleanup
    print("\nCleaning up temporary files...")
    for f in ["test_image.jpg", "debug_page_0.jpg"]:
        if os.path.exists(f):
            try:
                os.remove(f)
                print(f"  Removed {f}")
            except:
                pass


if __name__ == "__main__":
    import sys

    print("PaddleOCR Debug Tool")
    print("=" * 70)

    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        print(f"PDF file: {pdf_path}\n")
        full_debug_pipeline(pdf_path)
    else:
        print("Usage: python debug_pdf.py <path_to_pdf>")
        print("\nExample: python debug_pdf.py ds.pdf")
        print("\nThis will:")
        print("  1. Test if PaddleOCR works")
        print("  2. Convert PDF to images")
        print("  3. Run OCR on the images")
        print("  4. Try different OCR configurations")
        print("  5. Show detailed debug output")