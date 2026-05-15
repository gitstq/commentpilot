#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script for CommentPilot"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from commentpilot import (
    CommentPilot, 
    LanguageDetector, 
    Language,
    CommentParser,
    QualityAnalyzer,
    ReportFormatter,
    print_console_report
)


def test_language_detection():
    """Test language detection"""
    print("Testing language detection...")
    
    tests = [
        ("test.py", Language.PYTHON),
        ("test.js", Language.JAVASCRIPT),
        ("test.ts", Language.TYPESCRIPT),
        ("test.go", Language.GO),
        ("test.java", Language.JAVA),
        ("test.rs", Language.RUST),
        ("test.c", Language.C),
        ("test.cpp", Language.CPP),
        ("test.cs", Language.CSHARP),
        ("test.php", Language.PHP),
        ("test.rb", Language.RUBY),
        ("test.swift", Language.SWIFT),
        ("test.kt", Language.KOTLIN),
        ("test.lua", Language.LUA),
        ("test.sh", Language.SHELL),
        ("test.unknown", Language.UNKNOWN),
    ]
    
    for file_path, expected in tests:
        result = LanguageDetector.detect(file_path)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {file_path}: {result.value} (expected: {expected.value})")
    
    print()


def test_comment_parsing():
    """Test comment parsing"""
    print("Testing comment parsing...")
    
    # Python
    python_code = '''
# This is a single-line comment
"""This is a docstring"""

def hello():
    """Say hello"""
    pass
'''
    comments = CommentParser.parse_comments(python_code, Language.PYTHON)
    print(f"  Python: Found {len(comments)} comments")
    
    # JavaScript
    js_code = '''
// Single line comment
/* Multi-line
   comment */

function test() {
    // TODO: implement
}
'''
    comments = CommentParser.parse_comments(js_code, Language.JAVASCRIPT)
    print(f"  JavaScript: Found {len(comments)} comments")
    
    # Go
    go_code = '''
// Package main
package main

// Main function
func main() {
    // TODO: implement
}
'''
    comments = CommentParser.parse_comments(go_code, Language.GO)
    print(f"  Go: Found {len(comments)} comments")
    
    print()


def test_analyzer():
    """Test the analyzer"""
    print("Testing analyzer...")
    
    # Create a test directory
    import tempfile
    import shutil
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_py = os.path.join(tmpdir, "test.py")
        with open(test_py, 'w') as f:
            f.write('''
"""Module docstring."""

def function_with_docstring():
    """This function has a docstring."""
    pass

def function_without_docstring():
    # TODO: implement this
    pass

class MyClass:
    """A class."""
    
    def method(self):
        pass
''')
        
        test_js = os.path.join(tmpdir, "test.js")
        with open(test_js, 'w') as f:
            f.write('''
// JavaScript file
function test() {
    // FIXME: broken
}

class Foo {
    constructor() {
        // No doc
    }
}
''')
        
        # Analyze
        analyzer = CommentPilot(tmpdir)
        report = analyzer.analyze()
        
        print(f"  Files analyzed: {report.total_files}")
        print(f"  Total lines: {report.total_lines}")
        print(f"  Coverage: {report.overall_coverage:.1f}%")
        print(f"  Quality score: {report.overall_quality_score:.1f}")
        
        if report.todo_summary:
            print(f"  TODOs: {report.todo_summary}")
    
    print()


def main():
    """Run all tests"""
    print("=" * 50)
    print("CommentPilot Test Suite")
    print("=" * 50)
    print()
    
    test_language_detection()
    test_comment_parsing()
    test_analyzer()
    
    print("=" * 50)
    print("All tests completed!")
    print("=" * 50)


if __name__ == '__main__':
    main()
