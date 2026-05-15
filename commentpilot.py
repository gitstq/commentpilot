#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CommentPilot - Lightweight Code Comment Quality Intelligent Analysis Engine
轻量级代码注释质量智能分析引擎

A zero-dependency CLI tool for analyzing code comment quality, coverage,
and detecting missing or outdated comments across multiple programming languages.

Author: CommentPilot Team
License: MIT
Version: 1.0.0
"""

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict
from enum import Enum
import hashlib


__version__ = "1.0.0"
__author__ = "CommentPilot Team"


class CommentType(Enum):
    """Types of comments"""
    SINGLE_LINE = "single_line"
    MULTI_LINE = "multi_line"
    DOCSTRING = "docstring"
    TODO = "todo"
    FIXME = "fixme"
    XXX = "xxx"
    HACK = "hack"
    NOTE = "note"


class Language(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    JAVA = "java"
    RUST = "rust"
    C = "c"
    CPP = "cpp"
    CSHARP = "csharp"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SCALA = "scala"
    LUA = "lua"
    SHELL = "shell"
    UNKNOWN = "unknown"


@dataclass
class CommentInfo:
    """Information about a single comment"""
    file_path: str
    line_start: int
    line_end: int
    comment_type: CommentType
    content: str
    is_docstring: bool = False
    associated_element: Optional[str] = None  # function/class/variable name
    element_type: Optional[str] = None  # function/class/module
    quality_score: float = 0.0
    issues: List[str] = field(default_factory=list)


@dataclass
class CodeElement:
    """Information about a code element (function, class, etc.)"""
    name: str
    element_type: str  # function, class, method, module
    line_start: int
    line_end: int
    has_comment: bool = False
    comment: Optional[CommentInfo] = None
    complexity: int = 1
    parameters: List[str] = field(default_factory=list)
    docstring_content: Optional[str] = None


@dataclass
class FileAnalysisResult:
    """Analysis result for a single file"""
    file_path: str
    language: Language
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    coverage_ratio: float
    elements: List[CodeElement] = field(default_factory=list)
    comments: List[CommentInfo] = field(default_factory=list)
    todos: List[CommentInfo] = field(default_factory=list)
    missing_comments: List[CodeElement] = field(default_factory=list)
    quality_score: float = 0.0
    issues: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AnalysisReport:
    """Complete analysis report"""
    project_path: str
    analyzed_at: str
    total_files: int
    total_lines: int
    total_code_lines: int
    total_comment_lines: int
    overall_coverage: float
    overall_quality_score: float
    file_results: List[FileAnalysisResult] = field(default_factory=list)
    language_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    todo_summary: Dict[str, int] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class LanguageDetector:
    """Detect programming language from file extension"""
    
    EXTENSION_MAP = {
        '.py': Language.PYTHON,
        '.js': Language.JAVASCRIPT,
        '.mjs': Language.JAVASCRIPT,
        '.cjs': Language.JAVASCRIPT,
        '.ts': Language.TYPESCRIPT,
        '.tsx': Language.TYPESCRIPT,
        '.go': Language.GO,
        '.java': Language.JAVA,
        '.rs': Language.RUST,
        '.c': Language.C,
        '.h': Language.C,
        '.cpp': Language.CPP,
        '.hpp': Language.CPP,
        '.cc': Language.CPP,
        '.cs': Language.CSHARP,
        '.php': Language.PHP,
        '.rb': Language.RUBY,
        '.swift': Language.SWIFT,
        '.kt': Language.KOTLIN,
        '.kts': Language.KOTLIN,
        '.scala': Language.SCALA,
        '.lua': Language.LUA,
        '.sh': Language.SHELL,
        '.bash': Language.SHELL,
        '.zsh': Language.SHELL,
    }
    
    @classmethod
    def detect(cls, file_path: str) -> Language:
        """Detect language from file extension"""
        ext = Path(file_path).suffix.lower()
        return cls.EXTENSION_MAP.get(ext, Language.UNKNOWN)


class CommentParser:
    """Parse comments from various programming languages"""
    
    # Comment patterns for different languages
    PATTERNS = {
        Language.PYTHON: {
            'single_line': r'#.*$',
            'multi_line': r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'',
            'docstring': r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'',
        },
        Language.JAVASCRIPT: {
            'single_line': r'//.*$',
            'multi_line': r'/\*[\s\S]*?\*/',
            'docstring': r'/\*\*[\s\S]*?\*/',
        },
        Language.TYPESCRIPT: {
            'single_line': r'//.*$',
            'multi_line': r'/\*[\s\S]*?\*/',
            'docstring': r'/\*\*[\s\S]*?\*/',
        },
        Language.GO: {
            'single_line': r'//.*$',
            'multi_line': r'/\*[\s\S]*?\*/',
            'docstring': r'//.*$',  # Go uses // for doc comments
        },
        Language.JAVA: {
            'single_line': r'//.*$',
            'multi_line': r'/\*[\s\S]*?\*/',
            'docstring': r'/\*\*[\s\S]*?\*/',
        },
        Language.RUST: {
            'single_line': r'//.*$',
            'multi_line': r'/\*[\s\S]*?\*/',
            'docstring': r'///.*$|/\*![\s\S]*?\*/',
        },
        Language.C: {
            'single_line': r'//.*$',
            'multi_line': r'/\*[\s\S]*?\*/',
            'docstring': r'/\*\*[\s\S]*?\*/',
        },
        Language.CPP: {
            'single_line': r'//.*$',
            'multi_line': r'/\*[\s\S]*?\*/',
            'docstring': r'/\*\*[\s\S]*?\*/',
        },
        Language.CSHARP: {
            'single_line': r'//.*$',
            'multi_line': r'/\*[\s\S]*?\*/',
            'docstring': r'///.*$|/\*\*[\s\S]*?\*/',
        },
        Language.PHP: {
            'single_line': r'//.*$|#.*$',
            'multi_line': r'/\*[\s\S]*?\*/',
            'docstring': r'/\*\*[\s\S]*?\*/',
        },
        Language.RUBY: {
            'single_line': r'#.*$',
            'multi_line': r'=begin[\s\S]*?=end',
            'docstring': r'##[\s\S]*?##',
        },
        Language.SWIFT: {
            'single_line': r'//.*$',
            'multi_line': r'/\*[\s\S]*?\*/',
            'docstring': r'///.*$',
        },
        Language.KOTLIN: {
            'single_line': r'//.*$',
            'multi_line': r'/\*[\s\S]*?\*/',
            'docstring': r'/\*\*[\s\S]*?\*/',
        },
        Language.SCALA: {
            'single_line': r'//.*$',
            'multi_line': r'/\*[\s\S]*?\*/',
            'docstring': r'/\*\*[\s\S]*?\*/',
        },
        Language.LUA: {
            'single_line': r'--.*$',
            'multi_line': r'--\[\[[\s\S]*?\]\]',
            'docstring': r'---.*$',
        },
        Language.SHELL: {
            'single_line': r'#.*$',
            'multi_line': r': << ?\'EOF\'[\s\S]*?EOF|: << ?"EOF"[\s\S]*?EOF',
            'docstring': r'##.*$',
        },
    }
    
    # TODO/FIXME patterns
    TODO_PATTERNS = [
        (r'(?i)TODO\s*[:\(]?\s*(.+)', CommentType.TODO),
        (r'(?i)FIXME\s*[:\(]?\s*(.+)', CommentType.FIXME),
        (r'(?i)XXX\s*[:\(]?\s*(.+)', CommentType.XXX),
        (r'(?i)HACK\s*[:\(]?\s*(.+)', CommentType.HACK),
        (r'(?i)NOTE\s*[:\(]?\s*(.+)', CommentType.NOTE),
    ]
    
    @classmethod
    def parse_comments(cls, content: str, language: Language) -> List[CommentInfo]:
        """Parse all comments from source code"""
        comments = []
        lines = content.split('\n')
        
        if language not in cls.PATTERNS:
            return comments
        
        patterns = cls.PATTERNS[language]
        
        # Parse single-line comments
        single_pattern = patterns.get('single_line', '')
        if single_pattern:
            for i, line in enumerate(lines, 1):
                for match in re.finditer(single_pattern, line, re.MULTILINE):
                    comment_text = match.group(0)
                    comment_info = cls._create_comment_info(
                        line, i, i, comment_text, CommentType.SINGLE_LINE
                    )
                    comments.append(comment_info)
        
        # Parse multi-line comments
        multi_pattern = patterns.get('multi_line', '')
        if multi_pattern:
            for match in re.finditer(multi_pattern, content, re.MULTILINE):
                start_line = content[:match.start()].count('\n') + 1
                end_line = start_line + match.group(0).count('\n')
                comment_text = match.group(0)
                
                # Check if it's a docstring
                is_docstring = comment_text.startswith('/**') or comment_text.startswith('"""') or comment_text.startswith("'''")
                comment_type = CommentType.DOCSTRING if is_docstring else CommentType.MULTI_LINE
                
                comment_info = cls._create_comment_info(
                    "", start_line, end_line, comment_text, comment_type
                )
                comments.append(comment_info)
        
        return comments
    
    @classmethod
    def _create_comment_info(cls, file_path: str, line_start: int, line_end: int, 
                            content: str, comment_type: CommentType) -> CommentInfo:
        """Create a CommentInfo object"""
        issues = []
        quality_score = cls._calculate_comment_quality(content)
        
        # Check for TODOs
        for pattern, todo_type in cls.TODO_PATTERNS:
            if re.search(pattern, content):
                comment_type = todo_type
                break
        
        return CommentInfo(
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            comment_type=comment_type,
            content=content,
            quality_score=quality_score,
            issues=issues
        )
    
    @classmethod
    def _calculate_comment_quality(cls, content: str) -> float:
        """Calculate comment quality score (0-100)"""
        if not content:
            return 0.0
        
        score = 50.0  # Base score
        
        # Remove comment markers
        clean_content = re.sub(r'^[#/*\s]+|[#/*\s]+$', '', content, flags=re.MULTILINE)
        clean_content = clean_content.strip()
        
        if not clean_content:
            return 10.0  # Empty comment
        
        # Length bonus (reasonable length)
        word_count = len(clean_content.split())
        if word_count >= 3:
            score += min(20, word_count * 2)  # Up to 20 points for length
        
        # Check for meaningful content
        if re.search(r'\b(param|return|arg|example|note|warning|raise|throw)\b', clean_content, re.I):
            score += 15  # Documentation keywords
        
        # Check for code examples
        if re.search(r'`[^`]+`|```', content):
            score += 10  # Code examples
        
        # Penalize very short comments
        if word_count < 2:
            score -= 20
        
        # Penalize repeated characters (like "/////")
        if re.search(r'(.)\1{4,}', content):
            score -= 15
        
        return max(0, min(100, score))


class PythonAnalyzer:
    """Analyze Python code using AST"""
    
    @staticmethod
    def analyze(content: str, file_path: str) -> Tuple[List[CodeElement], List[CommentInfo]]:
        """Analyze Python code for comments and code elements"""
        elements = []
        comments = []
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return elements, comments
        
        lines = content.split('\n')
        
        # Parse module docstring
        module_docstring = ast.get_docstring(tree)
        if module_docstring:
            docstring_line = 1
            for i, line in enumerate(lines):
                if '"""' in line or "'''" in line:
                    docstring_line = i + 1
                    break
            
            elements.append(CodeElement(
                name='<module>',
                element_type='module',
                line_start=1,
                line_end=docstring_line,
                has_comment=True,
                docstring_content=module_docstring
            ))
        
        # Parse classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                docstring = ast.get_docstring(node)
                element = CodeElement(
                    name=node.name,
                    element_type='function' if not any(isinstance(p, ast.FunctionDef) for p in ast.walk(tree) if p != node and hasattr(p, 'body') and node in getattr(p, 'body', [])) else 'method',
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    has_comment=docstring is not None,
                    docstring_content=docstring,
                    parameters=[arg.arg for arg in node.args.args]
                )
                elements.append(element)
                
                if docstring:
                    comments.append(CommentInfo(
                        file_path=file_path,
                        line_start=node.lineno + 1,
                        line_end=node.lineno + docstring.count('\n') + 1,
                        comment_type=CommentType.DOCSTRING,
                        content=docstring,
                        is_docstring=True,
                        associated_element=node.name,
                        element_type='function'
                    ))
            
            elif isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)
                element = CodeElement(
                    name=node.name,
                    element_type='class',
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    has_comment=docstring is not None,
                    docstring_content=docstring
                )
                elements.append(element)
                
                if docstring:
                    comments.append(CommentInfo(
                        file_path=file_path,
                        line_start=node.lineno + 1,
                        line_end=node.lineno + docstring.count('\n') + 1,
                        comment_type=CommentType.DOCSTRING,
                        content=docstring,
                        is_docstring=True,
                        associated_element=node.name,
                        element_type='class'
                    ))
        
        # Parse inline comments
        for i, line in enumerate(lines, 1):
            if '#' in line:
                # Find the comment part
                comment_match = re.search(r'#.*$', line)
                if comment_match:
                    comment_text = comment_match.group(0)
                    comments.append(CommentInfo(
                        file_path=file_path,
                        line_start=i,
                        line_end=i,
                        comment_type=CommentType.SINGLE_LINE,
                        content=comment_text
                    ))
        
        return elements, comments


class GenericAnalyzer:
    """Generic analyzer for non-Python languages"""
    
    @staticmethod
    def analyze(content: str, file_path: str, language: Language) -> Tuple[List[CodeElement], List[CommentInfo]]:
        """Analyze code for comments and code elements"""
        elements = []
        comments = CommentParser.parse_comments(content, language)
        
        lines = content.split('\n')
        
        # Detect functions and classes using regex
        if language in [Language.JAVASCRIPT, Language.TYPESCRIPT]:
            # JavaScript/TypeScript patterns
            func_pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(|(\w+)\s*:\s*(?:async\s*)?\()'
            class_pattern = r'class\s+(\w+)'
            
            for i, line in enumerate(lines, 1):
                for match in re.finditer(func_pattern, line):
                    name = match.group(1) or match.group(2) or match.group(3)
                    elements.append(CodeElement(
                        name=name,
                        element_type='function',
                        line_start=i,
                        line_end=i
                    ))
                
                for match in re.finditer(class_pattern, line):
                    elements.append(CodeElement(
                        name=match.group(1),
                        element_type='class',
                        line_start=i,
                        line_end=i
                    ))
        
        elif language == Language.GO:
            # Go patterns
            func_pattern = r'func\s+(?:\([^)]+\)\s*)?(\w+)\s*\('
            struct_pattern = r'type\s+(\w+)\s+struct'
            
            for i, line in enumerate(lines, 1):
                for match in re.finditer(func_pattern, line):
                    elements.append(CodeElement(
                        name=match.group(1),
                        element_type='function',
                        line_start=i,
                        line_end=i
                    ))
                
                for match in re.finditer(struct_pattern, line):
                    elements.append(CodeElement(
                        name=match.group(1),
                        element_type='struct',
                        line_start=i,
                        line_end=i
                    ))
        
        elif language == Language.JAVA:
            # Java patterns
            method_pattern = r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\('
            class_pattern = r'(?:public\s+)?class\s+(\w+)'
            
            for i, line in enumerate(lines, 1):
                for match in re.finditer(method_pattern, line):
                    name = match.group(1)
                    if name not in ['if', 'for', 'while', 'switch', 'catch']:
                        elements.append(CodeElement(
                            name=name,
                            element_type='method',
                            line_start=i,
                            line_end=i
                        ))
                
                for match in re.finditer(class_pattern, line):
                    elements.append(CodeElement(
                        name=match.group(1),
                        element_type='class',
                        line_start=i,
                        line_end=i
                    ))
        
        elif language == Language.RUST:
            # Rust patterns
            func_pattern = r'(?:pub\s+)?fn\s+(\w+)'
            struct_pattern = r'(?:pub\s+)?struct\s+(\w+)'
            
            for i, line in enumerate(lines, 1):
                for match in re.finditer(func_pattern, line):
                    elements.append(CodeElement(
                        name=match.group(1),
                        element_type='function',
                        line_start=i,
                        line_end=i
                    ))
                
                for match in re.finditer(struct_pattern, line):
                    elements.append(CodeElement(
                        name=match.group(1),
                        element_type='struct',
                        line_start=i,
                        line_end=i
                    ))
        
        # Associate comments with elements
        for element in elements:
            # Check if there's a comment just before the element
            for comment in comments:
                if comment.line_end == element.line_start - 1 or comment.line_start == element.line_start + 1:
                    if comment.comment_type in [CommentType.DOCSTRING, CommentType.MULTI_LINE]:
                        element.has_comment = True
                        element.comment = comment
                        comment.associated_element = element.name
                        comment.element_type = element.element_type
                        break
        
        return elements, comments


class QualityAnalyzer:
    """Analyze comment quality and detect issues"""
    
    @staticmethod
    def analyze_file(file_result: FileAnalysisResult) -> None:
        """Analyze comment quality for a file"""
        issues = []
        
        # Check for missing comments on public elements
        for element in file_result.elements:
            if not element.has_comment:
                # Only flag functions and classes
                if element.element_type in ['function', 'class', 'method', 'struct']:
                    # Check if it's a simple getter/setter
                    if element.element_type == 'function' and element.name:
                        if element.name.startswith('get_') or element.name.startswith('set_'):
                            continue  # Skip simple getters/setters
                    
                    file_result.missing_comments.append(element)
                    issues.append({
                        'type': 'missing_comment',
                        'element': element.name,
                        'element_type': element.element_type,
                        'line': element.line_start,
                        'message': f"Missing comment for {element.element_type} '{element.name}'"
                    })
        
        # Check for low-quality comments
        for comment in file_result.comments:
            if comment.quality_score < 30:
                issues.append({
                    'type': 'low_quality',
                    'line': comment.line_start,
                    'message': f"Low quality comment (score: {comment.quality_score:.1f})",
                    'content': comment.content[:50] + '...' if len(comment.content) > 50 else comment.content
                })
        
        # Check for TODO/FIXME items
        for comment in file_result.comments:
            if comment.comment_type in [CommentType.TODO, CommentType.FIXME, CommentType.XXX, CommentType.HACK]:
                file_result.todos.append(comment)
        
        file_result.issues = issues
        
        # Calculate quality score
        if file_result.elements:
            commented_count = sum(1 for e in file_result.elements if e.has_comment)
            file_result.quality_score = (commented_count / len(file_result.elements)) * 100
        else:
            file_result.quality_score = 100.0


class CommentPilot:
    """Main CommentPilot analyzer class"""
    
    def __init__(self, project_path: str, exclude_patterns: List[str] = None):
        self.project_path = Path(project_path).resolve()
        self.exclude_patterns = exclude_patterns or [
            'node_modules', '.git', '__pycache__', 'venv', '.venv',
            'dist', 'build', '.idea', '.vscode', 'target', 'vendor',
            '*.min.js', '*.min.css', 'migrations', '.tox', 'env'
        ]
    
    def should_analyze(self, file_path: Path) -> bool:
        """Check if a file should be analyzed"""
        # Check extension
        if LanguageDetector.detect(str(file_path)) == Language.UNKNOWN:
            return False
        
        # Check exclude patterns
        path_str = str(file_path)
        for pattern in self.exclude_patterns:
            if pattern.startswith('*'):
                if path_str.endswith(pattern[1:]):
                    return False
            elif pattern in path_str:
                return False
        
        return True
    
    def analyze_file(self, file_path: Path) -> Optional[FileAnalysisResult]:
        """Analyze a single file"""
        language = LanguageDetector.detect(str(file_path))
        if language == Language.UNKNOWN:
            return None
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return None
        
        lines = content.split('\n')
        total_lines = len(lines)
        
        # Count different line types
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        
        in_multiline_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                blank_lines += 1
                continue
            
            # Check for multiline comments
            if language in [Language.PYTHON]:
                if '"""' in stripped or "'''" in stripped:
                    in_multiline_comment = not in_multiline_comment
                    comment_lines += 1
                    continue
            elif language in [Language.JAVASCRIPT, Language.TYPESCRIPT, Language.JAVA, 
                            Language.C, Language.CPP, Language.CSHARP, Language.PHP,
                            Language.KOTLIN, Language.SCALA, Language.RUST, Language.GO]:
                if stripped.startswith('/*') or stripped.endswith('*/'):
                    in_multiline_comment = not in_multiline_comment
                    comment_lines += 1
                    continue
            
            if in_multiline_comment:
                comment_lines += 1
                continue
            
            # Check for single-line comments
            if language == Language.PYTHON:
                if stripped.startswith('#'):
                    comment_lines += 1
                    continue
            elif language in [Language.JAVASCRIPT, Language.TYPESCRIPT, Language.JAVA,
                            Language.C, Language.CPP, Language.CSHARP, Language.PHP,
                            Language.KOTLIN, Language.SCALA, Language.RUST, Language.GO]:
                if stripped.startswith('//') or stripped.startswith('/*'):
                    comment_lines += 1
                    continue
            elif language == Language.RUBY:
                if stripped.startswith('#'):
                    comment_lines += 1
                    continue
            elif language == Language.LUA:
                if stripped.startswith('--'):
                    comment_lines += 1
                    continue
            elif language == Language.SHELL:
                if stripped.startswith('#'):
                    comment_lines += 1
                    continue
            
            code_lines += 1
        
        # Analyze code elements and comments
        if language == Language.PYTHON:
            elements, comments = PythonAnalyzer.analyze(content, str(file_path))
        else:
            elements, comments = GenericAnalyzer.analyze(content, str(file_path), language)
        
        # Calculate coverage
        coverage_ratio = (comment_lines / total_lines * 100) if total_lines > 0 else 0
        
        result = FileAnalysisResult(
            file_path=str(file_path.relative_to(self.project_path)),
            language=language,
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            coverage_ratio=coverage_ratio,
            elements=elements,
            comments=comments
        )
        
        # Analyze quality
        QualityAnalyzer.analyze_file(result)
        
        return result
    
    def analyze(self) -> AnalysisReport:
        """Analyze entire project"""
        file_results = []
        language_stats = defaultdict(lambda: {
            'files': 0,
            'total_lines': 0,
            'code_lines': 0,
            'comment_lines': 0,
            'coverage': 0.0
        })
        todo_summary = defaultdict(int)
        
        # Find all files to analyze
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file() and self.should_analyze(file_path):
                result = self.analyze_file(file_path)
                if result:
                    file_results.append(result)
                    
                    # Update language stats
                    lang_name = result.language.value
                    language_stats[lang_name]['files'] += 1
                    language_stats[lang_name]['total_lines'] += result.total_lines
                    language_stats[lang_name]['code_lines'] += result.code_lines
                    language_stats[lang_name]['comment_lines'] += result.comment_lines
                    
                    # Update TODO summary
                    for todo in result.todos:
                        todo_summary[todo.comment_type.value] += 1
        
        # Calculate overall stats
        total_lines = sum(r.total_lines for r in file_results)
        total_code_lines = sum(r.code_lines for r in file_results)
        total_comment_lines = sum(r.comment_lines for r in file_results)
        overall_coverage = (total_comment_lines / total_lines * 100) if total_lines > 0 else 0
        overall_quality = sum(r.quality_score for r in file_results) / len(file_results) if file_results else 0
        
        # Calculate language coverage
        for lang, stats in language_stats.items():
            stats['coverage'] = (stats['comment_lines'] / stats['total_lines'] * 100) if stats['total_lines'] > 0 else 0
        
        # Generate recommendations
        recommendations = self._generate_recommendations(file_results, overall_coverage, overall_quality)
        
        return AnalysisReport(
            project_path=str(self.project_path),
            analyzed_at=datetime.now().isoformat(),
            total_files=len(file_results),
            total_lines=total_lines,
            total_code_lines=total_code_lines,
            total_comment_lines=total_comment_lines,
            overall_coverage=overall_coverage,
            overall_quality_score=overall_quality,
            file_results=file_results,
            language_stats=dict(language_stats),
            todo_summary=dict(todo_summary),
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, file_results: List[FileAnalysisResult], 
                                  coverage: float, quality: float) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if coverage < 10:
            recommendations.append("🚨 Critical: Comment coverage is very low (<10%). Consider adding documentation to key files.")
        elif coverage < 20:
            recommendations.append("⚠️ Warning: Comment coverage is low (<20%). Add comments to improve code maintainability.")
        elif coverage < 30:
            recommendations.append("📝 Notice: Comment coverage could be improved. Focus on documenting public APIs.")
        else:
            recommendations.append("✅ Good: Comment coverage is reasonable.")
        
        if quality < 50:
            recommendations.append("📉 Quality Alert: Many elements lack proper documentation. Review missing comments.")
        elif quality < 70:
            recommendations.append("📊 Quality Notice: Some elements need better documentation.")
        
        # Check for TODOs
        total_todos = sum(len(r.todos) for r in file_results)
        if total_todos > 10:
            recommendations.append(f"📋 Found {total_todos} TODO/FIXME items. Consider addressing them.")
        elif total_todos > 0:
            recommendations.append(f"📋 Found {total_todos} TODO/FIXME items to review.")
        
        # Check for files with no comments
        no_comment_files = [r for r in file_results if r.coverage_ratio == 0 and r.code_lines > 50]
        if no_comment_files:
            recommendations.append(f"📄 {len(no_comment_files)} files with >50 lines have no comments.")
        
        return recommendations


class ReportFormatter:
    """Format analysis reports in various formats"""
    
    @staticmethod
    def to_json(report: AnalysisReport, indent: int = 2) -> str:
        """Convert report to JSON"""
        def dataclass_to_dict(obj):
            if hasattr(obj, '__dataclass_fields__'):
                result = {}
                for key, value in asdict(obj).items():
                    if isinstance(value, Enum):
                        result[key] = value.value
                    elif isinstance(value, list):
                        result[key] = [dataclass_to_dict(item) for item in value]
                    elif isinstance(value, dict):
                        result[key] = {k: dataclass_to_dict(v) for k, v in value.items()}
                    else:
                        result[key] = value
                return result
            return obj
        
        return json.dumps(dataclass_to_dict(report), indent=indent, ensure_ascii=False)
    
    @staticmethod
    def to_markdown(report: AnalysisReport) -> str:
        """Convert report to Markdown"""
        lines = [
            "# 📊 CommentPilot Analysis Report",
            "",
            f"**Project**: `{report.project_path}`",
            f"**Analyzed**: {report.analyzed_at}",
            "",
            "## 📈 Summary",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Files | {report.total_files} |",
            f"| Total Lines | {report.total_lines:,} |",
            f"| Code Lines | {report.total_code_lines:,} |",
            f"| Comment Lines | {report.total_comment_lines:,} |",
            f"| Coverage | {report.overall_coverage:.1f}% |",
            f"| Quality Score | {report.overall_quality_score:.1f}/100 |",
            "",
            "## 🌐 Language Statistics",
            "",
            "| Language | Files | Lines | Coverage |",
            "|----------|-------|-------|----------|",
        ]
        
        for lang, stats in sorted(report.language_stats.items(), key=lambda x: x[1]['files'], reverse=True):
            lines.append(f"| {lang} | {stats['files']} | {stats['total_lines']:,} | {stats['coverage']:.1f}% |")
        
        if report.todo_summary:
            lines.extend([
                "",
                "## 📋 TODO Summary",
                "",
                "| Type | Count |",
                "|------|-------|",
            ])
            for todo_type, count in report.todo_summary.items():
                lines.append(f"| {todo_type.upper()} | {count} |")
        
        lines.extend([
            "",
            "## 💡 Recommendations",
            "",
        ])
        for rec in report.recommendations:
            lines.append(f"- {rec}")
        
        # Top files needing attention
        files_needing_attention = sorted(
            [r for r in report.file_results if r.missing_comments],
            key=lambda x: len(x.missing_comments),
            reverse=True
        )[:10]
        
        if files_needing_attention:
            lines.extend([
                "",
                "## 🔍 Files Needing Attention",
                "",
                "| File | Missing Comments | Coverage |",
                "|------|-----------------|----------|",
            ])
            for f in files_needing_attention:
                lines.append(f"| `{f.file_path}` | {len(f.missing_comments)} | {f.coverage_ratio:.1f}% |")
        
        return '\n'.join(lines)
    
    @staticmethod
    def to_html(report: AnalysisReport) -> str:
        """Convert report to HTML"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CommentPilot Report</title>
    <style>
        :root {{
            --primary: #4F46E5;
            --success: #10B981;
            --warning: #F59E0B;
            --danger: #EF4444;
            --bg: #F9FAFB;
            --card: #FFFFFF;
            --text: #1F2937;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            color: var(--primary);
            border-bottom: 3px solid var(--primary);
            padding-bottom: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: var(--card);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: var(--primary);
        }}
        .stat-label {{
            color: #6B7280;
            font-size: 0.9em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--card);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #E5E7EB;
        }}
        th {{
            background: var(--primary);
            color: white;
        }}
        tr:hover {{
            background: #F3F4F6;
        }}
        .progress-bar {{
            background: #E5E7EB;
            border-radius: 4px;
            height: 8px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: var(--primary);
            transition: width 0.3s;
        }}
        .recommendation {{
            background: var(--card);
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid var(--primary);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 CommentPilot Analysis Report</h1>
        <p><strong>Project:</strong> {report.project_path}</p>
        <p><strong>Analyzed:</strong> {report.analyzed_at}</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{report.total_files}</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{report.total_lines:,}</div>
                <div class="stat-label">Total Lines</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{report.overall_coverage:.1f}%</div>
                <div class="stat-label">Comment Coverage</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {min(report.overall_coverage, 100)}%"></div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{report.overall_quality_score:.0f}/100</div>
                <div class="stat-label">Quality Score</div>
            </div>
        </div>
        
        <h2>🌐 Language Statistics</h2>
        <table>
            <tr>
                <th>Language</th>
                <th>Files</th>
                <th>Lines</th>
                <th>Coverage</th>
            </tr>
            {''.join(f'<tr><td>{lang}</td><td>{stats["files"]}</td><td>{stats["total_lines"]:,}</td><td>{stats["coverage"]:.1f}%</td></tr>' for lang, stats in sorted(report.language_stats.items(), key=lambda x: x[1]['files'], reverse=True))}
        </table>
        
        <h2>💡 Recommendations</h2>
        {''.join(f'<div class="recommendation">{rec}</div>' for rec in report.recommendations)}
    </div>
</body>
</html>"""


def print_console_report(report: AnalysisReport) -> None:
    """Print a formatted console report"""
    print("\n" + "=" * 60)
    print("📊 CommentPilot Analysis Report")
    print("=" * 60)
    print(f"\n📁 Project: {report.project_path}")
    print(f"⏰ Analyzed: {report.analyzed_at}")
    
    print("\n" + "-" * 40)
    print("📈 Summary")
    print("-" * 40)
    print(f"  Total Files:      {report.total_files}")
    print(f"  Total Lines:      {report.total_lines:,}")
    print(f"  Code Lines:       {report.total_code_lines:,}")
    print(f"  Comment Lines:    {report.total_comment_lines:,}")
    print(f"  Coverage:         {report.overall_coverage:.1f}%")
    print(f"  Quality Score:    {report.overall_quality_score:.1f}/100")
    
    print("\n" + "-" * 40)
    print("🌐 Language Statistics")
    print("-" * 40)
    for lang, stats in sorted(report.language_stats.items(), key=lambda x: x[1]['files'], reverse=True):
        print(f"  {lang:12} {stats['files']:4} files, {stats['total_lines']:6,} lines, {stats['coverage']:5.1f}% coverage")
    
    if report.todo_summary:
        print("\n" + "-" * 40)
        print("📋 TODO Summary")
        print("-" * 40)
        for todo_type, count in report.todo_summary.items():
            print(f"  {todo_type.upper():8} {count}")
    
    print("\n" + "-" * 40)
    print("💡 Recommendations")
    print("-" * 40)
    for rec in report.recommendations:
        print(f"  {rec}")
    
    print("\n" + "=" * 60 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='CommentPilot - Lightweight Code Comment Quality Intelligent Analysis Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  commentpilot ./src
  commentpilot ./myproject --format json --output report.json
  commentpilot ./code --exclude "tests,docs" --format html
        """
    )
    
    parser.add_argument('path', help='Path to the project directory to analyze')
    parser.add_argument('--format', '-f', choices=['console', 'json', 'markdown', 'html'],
                       default='console', help='Output format (default: console)')
    parser.add_argument('--output', '-o', help='Output file path (for json/markdown/html)')
    parser.add_argument('--exclude', '-e', help='Comma-separated list of patterns to exclude')
    parser.add_argument('--version', '-v', action='version', version=f'CommentPilot {__version__}')
    
    args = parser.parse_args()
    
    # Validate path
    project_path = Path(args.path)
    if not project_path.exists():
        print(f"Error: Path '{args.path}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    if not project_path.is_dir():
        print(f"Error: Path '{args.path}' is not a directory", file=sys.stderr)
        sys.exit(1)
    
    # Parse exclude patterns
    exclude_patterns = None
    if args.exclude:
        exclude_patterns = [p.strip() for p in args.exclude.split(',')]
    
    # Run analysis
    print(f"🔍 Analyzing {project_path}...")
    analyzer = CommentPilot(str(project_path), exclude_patterns)
    report = analyzer.analyze()
    
    # Output results
    if args.format == 'console':
        print_console_report(report)
    elif args.format == 'json':
        output = ReportFormatter.to_json(report)
        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
            print(f"✅ Report saved to {args.output}")
        else:
            print(output)
    elif args.format == 'markdown':
        output = ReportFormatter.to_markdown(report)
        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
            print(f"✅ Report saved to {args.output}")
        else:
            print(output)
    elif args.format == 'html':
        output = ReportFormatter.to_html(report)
        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
            print(f"✅ Report saved to {args.output}")
        else:
            print(output)


if __name__ == '__main__':
    main()
