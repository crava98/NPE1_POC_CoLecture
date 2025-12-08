#!/usr/bin/env python3
"""
Test if image fetching from gurk.li works with the new JSON format.
"""
from data_models import CustomerSlide, BulletItem, Source, ImageColors
from image_providers import get_image_from_gurkli
import os

# Create a test slide with new fields
test_slide = CustomerSlide(
    title="Digital Transformation",
    sources=[],
    unsplashSearchTerms=["business", "technology", "office"],  # Fallback
    bullets=[
        BulletItem(bullet="Cloud migration and SaaS adoption", sub=[]),
        BulletItem(bullet="AI integration in business processes", sub=[])
    ],
    # Neue Felder:
    ImageKeywords=["technology", "innovation"],  # überschreibt unsplashSearchTerms
    style="flat_illustration",  # flat_illustration | fine_line | photorealistic
    image_mode="auto",  # stock_only | ai_only | auto
    ai_model="auto",    # auto | flux | banana
    colors=ImageColors(primary="#0066CC", secondary="#00CC66")
)

print("Testing image fetch from gurk.li with NEW JSON format...")
print(f"ImageKeywords: {test_slide.ImageKeywords}")
print(f"Style: {test_slide.style}")
print(f"Image Mode: {test_slide.image_mode}")
print(f"AI Model: {test_slide.ai_model}")
print(f"Colors: {test_slide.colors}")
print("-" * 60)

image_path = get_image_from_gurkli(test_slide)

print("-" * 60)
if image_path:
    if os.path.exists(image_path):
        file_size = os.path.getsize(image_path)
        print(f"✓ SUCCESS: Image downloaded")
        print(f"  Path: {image_path}")
        print(f"  Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    else:
        print(f"✗ FAIL: Path returned but file doesn't exist: {image_path}")
else:
    print("✗ FAIL: No image path returned")
