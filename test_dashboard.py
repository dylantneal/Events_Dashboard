#!/usr/bin/env python3
"""
Test script for Encore Dashboard
Verifies all components are working correctly
"""

import json
import os
import sys
from pathlib import Path
import subprocess

def test_content_generation():
    """Test the content generation layer"""
    print("🧪 Testing Content Generation Layer...")
    
    # Check if slides directory exists
    slides_dir = Path("slides")
    if not slides_dir.exists():
        print("  ❌ slides/ directory not found")
        return False
    
    # Check if manifest exists
    manifest_path = slides_dir / "slides.json"
    if not manifest_path.exists():
        print("  ❌ slides.json not found")
        return False
    
    # Validate manifest
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        if "slides" not in manifest:
            print("  ❌ manifest missing 'slides' key")
            return False
        
        if not isinstance(manifest["slides"], list):
            print("  ❌ manifest 'slides' is not a list")
            return False
        
        print(f"  ✅ Manifest valid with {len(manifest['slides'])} slides")
        
        # Check if all slides exist
        missing_slides = []
        for slide in manifest["slides"]:
            slide_path = slides_dir / slide
            if not slide_path.exists():
                missing_slides.append(slide)
        
        if missing_slides:
            print(f"  ❌ Missing slides: {missing_slides}")
            return False
        
        print("  ✅ All slides present")
        
        # Check file sizes
        total_size = 0
        for slide in manifest["slides"]:
            slide_path = slides_dir / slide
            size_kb = slide_path.stat().st_size / 1024
            total_size += size_kb
            if size_kb > 300:
                print(f"  ⚠️  Slide {slide} is {size_kb:.1f}KB (over 300KB limit)")
        
        print(f"  ✅ Total size: {total_size:.1f}KB")
        
    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON in manifest: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error reading manifest: {e}")
        return False
    
    return True

def test_presentation_layer():
    """Test the presentation layer"""
    print("\n🧪 Testing Presentation Layer...")
    
    # Check if index.html exists
    if not Path("index.html").exists():
        print("  ❌ index.html not found")
        return False
    
    # Check if index.html contains required elements
    with open("index.html") as f:
        content = f.read()
    
    required_elements = [
        "slides/slides.json",
        "Dashboard",
        "weather",
        "clock",
        "slide-container"
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"  ❌ Missing elements: {missing_elements}")
        return False
    
    print("  ✅ All required elements present")
    
    # Check for responsive design
    if "@media" not in content:
        print("  ⚠️  No responsive design detected")
    else:
        print("  ✅ Responsive design detected")
    
    return True

def test_publication_layer():
    """Test the publication layer configuration"""
    print("\n🧪 Testing Publication Layer...")
    
    # Check if GitHub Actions workflow exists
    workflow_path = Path(".github/workflows/deploy.yml")
    if not workflow_path.exists():
        print("  ❌ GitHub Actions workflow not found")
        return False
    
    print("  ✅ GitHub Actions workflow present")
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print("  ❌ requirements.txt not found")
        return False
    
    print("  ✅ requirements.txt present")
    
    return True

def test_kiosk_setup():
    """Test kiosk setup script"""
    print("\n🧪 Testing Kiosk Setup...")
    
    if not Path("setup_kiosk.sh").exists():
        print("  ❌ setup_kiosk.sh not found")
        return False
    
    # Check if script is executable
    if not os.access("setup_kiosk.sh", os.X_OK):
        print("  ⚠️  setup_kiosk.sh is not executable")
    else:
        print("  ✅ setup_kiosk.sh is executable")
    
    # Check script content
    with open("setup_kiosk.sh") as f:
        content = f.read()
    
    required_components = [
        "chromium-browser",
        "xdotool",
        "crontab",
        "autostart"
    ]
    
    missing_components = []
    for component in required_components:
        if component not in content:
            missing_components.append(component)
    
    if missing_components:
        print(f"  ⚠️  Missing components: {missing_components}")
    else:
        print("  ✅ All kiosk components present")
    
    return True

def test_file_structure():
    """Test overall file structure"""
    print("\n🧪 Testing File Structure...")
    
    required_files = [
        "flex_gantt.py",
        "index.html",
        "requirements.txt",
        "README.md",
        "setup_kiosk.sh",
        "slides/slides.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"  ❌ Missing files: {missing_files}")
        return False
    
    print("  ✅ All required files present")
    
    # Check for optimized slides
    slides_dir = Path("slides")
    png_files = list(slides_dir.glob("*.png"))
    if not png_files:
        print("  ❌ No PNG slides found")
        return False
    
    print(f"  ✅ Found {len(png_files)} slides")
    
    return True

def main():
    """Run all tests"""
    print("🎯 Encore Dashboard Test Suite")
    print("=" * 40)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Content Generation", test_content_generation),
        ("Presentation Layer", test_presentation_layer),
        ("Publication Layer", test_publication_layer),
        ("Kiosk Setup", test_kiosk_setup),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"  ✅ {test_name} PASSED")
            else:
                print(f"  ❌ {test_name} FAILED")
        except Exception as e:
            print(f"  ❌ {test_name} ERROR: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Dashboard is ready for deployment.")
        print("\n🚀 Next steps:")
        print("1. Push to GitHub: git add . && git commit -m 'Initial dashboard' && git push")
        print("2. Enable GitHub Pages in repository settings")
        print("3. Run setup_kiosk.sh on your Raspberry Pi")
        print("\n🌐 To test locally:")
        print("   python3 -m http.server 8000")
        print("   Then open http://localhost:8000")
    else:
        print("⚠️  Some tests failed. Please fix the issues before deploying.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 