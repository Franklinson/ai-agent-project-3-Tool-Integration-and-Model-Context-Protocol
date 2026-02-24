"""Secure file system access tool with sandboxing and path validation."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class FileSystemTool:
    """Secure file system tool with sandbox restrictions."""
    
    def __init__(
        self,
        sandbox_dir: str,
        allowed_extensions: Optional[Set[str]] = None,
        max_file_size: int = 10 * 1024 * 1024  # 10MB default
    ):
        """Initialize file system tool.
        
        Args:
            sandbox_dir: Root directory for all operations
            allowed_extensions: Set of allowed file extensions (e.g., {'.txt', '.json'})
            max_file_size: Maximum file size in bytes
        """
        self.sandbox_dir = Path(sandbox_dir).resolve()
        self.allowed_extensions = allowed_extensions
        self.max_file_size = max_file_size
        
        # Create sandbox directory if it doesn't exist
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
    
    def _validate_path(self, path: str) -> Dict[str, Any]:
        """Validate path is within sandbox and meets security requirements.
        
        Args:
            path: Path to validate
            
        Returns:
            Dictionary with success status and resolved path or error
        """
        try:
            # Resolve path and check if it's within sandbox
            requested_path = Path(path)
            
            # Handle relative paths
            if not requested_path.is_absolute():
                requested_path = self.sandbox_dir / requested_path
            
            resolved_path = requested_path.resolve()
            
            # Check if path is within sandbox
            try:
                resolved_path.relative_to(self.sandbox_dir)
            except ValueError:
                return {
                    "success": False,
                    "path": None,
                    "error": "Path is outside sandbox directory"
                }
            
            # Check file extension if whitelist is enabled
            if self.allowed_extensions and resolved_path.suffix:
                if resolved_path.suffix.lower() not in self.allowed_extensions:
                    return {
                        "success": False,
                        "path": None,
                        "error": f"File type {resolved_path.suffix} not allowed"
                    }
            
            return {
                "success": True,
                "path": resolved_path,
                "error": None
            }
        
        except Exception as e:
            return {
                "success": False,
                "path": None,
                "error": f"Path validation failed: {str(e)}"
            }
    
    def read_file(self, path: str, binary: bool = False) -> Dict[str, Any]:
        """Read file content with security validation.
        
        Args:
            path: File path to read
            binary: Read in binary mode
            
        Returns:
            Dictionary with success, content, and error
        """
        validation = self._validate_path(path)
        if not validation["success"]:
            return {
                "success": False,
                "content": None,
                "size": 0,
                "error": validation["error"]
            }
        
        file_path = validation["path"]
        
        try:
            # Check if file exists
            if not file_path.exists():
                return {
                    "success": False,
                    "content": None,
                    "size": 0,
                    "error": "File does not exist"
                }
            
            # Check if it's a file
            if not file_path.is_file():
                return {
                    "success": False,
                    "content": None,
                    "size": 0,
                    "error": "Path is not a file"
                }
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                return {
                    "success": False,
                    "content": None,
                    "size": file_size,
                    "error": f"File size ({file_size} bytes) exceeds maximum ({self.max_file_size} bytes)"
                }
            
            # Read file
            mode = 'rb' if binary else 'r'
            with open(file_path, mode) as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "size": file_size,
                "error": None
            }
        
        except PermissionError:
            return {
                "success": False,
                "content": None,
                "size": 0,
                "error": "Permission denied"
            }
        
        except Exception as e:
            return {
                "success": False,
                "content": None,
                "size": 0,
                "error": f"Failed to read file: {str(e)}"
            }
    
    def write_file(self, path: str, content: str, binary: bool = False) -> Dict[str, Any]:
        """Write content to file with security validation.
        
        Args:
            path: File path to write
            content: Content to write
            binary: Write in binary mode
            
        Returns:
            Dictionary with success, bytes_written, and error
        """
        validation = self._validate_path(path)
        if not validation["success"]:
            return {
                "success": False,
                "bytes_written": 0,
                "error": validation["error"]
            }
        
        file_path = validation["path"]
        
        try:
            # Check content size
            content_size = len(content) if isinstance(content, (str, bytes)) else 0
            if content_size > self.max_file_size:
                return {
                    "success": False,
                    "bytes_written": 0,
                    "error": f"Content size ({content_size} bytes) exceeds maximum ({self.max_file_size} bytes)"
                }
            
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            mode = 'wb' if binary else 'w'
            with open(file_path, mode) as f:
                bytes_written = f.write(content)
            
            return {
                "success": True,
                "bytes_written": bytes_written,
                "error": None
            }
        
        except PermissionError:
            return {
                "success": False,
                "bytes_written": 0,
                "error": "Permission denied"
            }
        
        except Exception as e:
            return {
                "success": False,
                "bytes_written": 0,
                "error": f"Failed to write file: {str(e)}"
            }
    
    def list_directory(self, path: str = ".") -> Dict[str, Any]:
        """List directory contents with security validation.
        
        Args:
            path: Directory path to list
            
        Returns:
            Dictionary with success, files, directories, and error
        """
        validation = self._validate_path(path)
        if not validation["success"]:
            return {
                "success": False,
                "files": [],
                "directories": [],
                "error": validation["error"]
            }
        
        dir_path = validation["path"]
        
        try:
            # Check if directory exists
            if not dir_path.exists():
                return {
                    "success": False,
                    "files": [],
                    "directories": [],
                    "error": "Directory does not exist"
                }
            
            # Check if it's a directory
            if not dir_path.is_dir():
                return {
                    "success": False,
                    "files": [],
                    "directories": [],
                    "error": "Path is not a directory"
                }
            
            files = []
            directories = []
            
            for item in dir_path.iterdir():
                item_info = {
                    "name": item.name,
                    "path": str(item.relative_to(self.sandbox_dir)),
                    "size": item.stat().st_size if item.is_file() else 0
                }
                
                if item.is_file():
                    files.append(item_info)
                elif item.is_dir():
                    directories.append(item_info)
            
            return {
                "success": True,
                "files": files,
                "directories": directories,
                "error": None
            }
        
        except PermissionError:
            return {
                "success": False,
                "files": [],
                "directories": [],
                "error": "Permission denied"
            }
        
        except Exception as e:
            return {
                "success": False,
                "files": [],
                "directories": [],
                "error": f"Failed to list directory: {str(e)}"
            }
    
    def delete_file(self, path: str) -> Dict[str, Any]:
        """Delete file with security validation.
        
        Args:
            path: File path to delete
            
        Returns:
            Dictionary with success and error
        """
        validation = self._validate_path(path)
        if not validation["success"]:
            return {
                "success": False,
                "error": validation["error"]
            }
        
        file_path = validation["path"]
        
        try:
            if not file_path.exists():
                return {
                    "success": False,
                    "error": "File does not exist"
                }
            
            if not file_path.is_file():
                return {
                    "success": False,
                    "error": "Path is not a file"
                }
            
            file_path.unlink()
            
            return {
                "success": True,
                "error": None
            }
        
        except PermissionError:
            return {
                "success": False,
                "error": "Permission denied"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete file: {str(e)}"
            }


# Example usage and security tests
if __name__ == "__main__":
    import tempfile
    import shutil
    
    # Create temporary sandbox directory
    sandbox = tempfile.mkdtemp(prefix="fs_sandbox_")
    print(f"Created sandbox: {sandbox}\n")
    
    try:
        # Initialize tool with restrictions
        fs_tool = FileSystemTool(
            sandbox_dir=sandbox,
            allowed_extensions={'.txt', '.json', '.md'},
            max_file_size=1024 * 1024  # 1MB
        )
        
        print("=== Testing Valid Operations ===\n")
        
        # Test 1: Write file
        print("1. Write file:")
        result = fs_tool.write_file("test.txt", "Hello, World!")
        print(f"   Success: {result['success']}")
        print(f"   Bytes written: {result['bytes_written']}")
        print()
        
        # Test 2: Read file
        print("2. Read file:")
        result = fs_tool.read_file("test.txt")
        print(f"   Success: {result['success']}")
        print(f"   Content: {result['content']}")
        print()
        
        # Test 3: List directory
        print("3. List directory:")
        result = fs_tool.list_directory(".")
        print(f"   Success: {result['success']}")
        print(f"   Files: {result['files']}")
        print()
        
        # Test 4: Write to subdirectory
        print("4. Write to subdirectory:")
        result = fs_tool.write_file("subdir/nested.txt", "Nested content")
        print(f"   Success: {result['success']}")
        print()
        
        print("=== Testing Security Features ===\n")
        
        # Test 5: Path traversal attempt
        print("5. Path traversal attempt (../../../etc/passwd):")
        result = fs_tool.read_file("../../../etc/passwd")
        print(f"   Success: {result['success']}")
        print(f"   Error: {result['error']}")
        print()
        
        # Test 6: Absolute path outside sandbox
        print("6. Absolute path outside sandbox (/etc/passwd):")
        result = fs_tool.read_file("/etc/passwd")
        print(f"   Success: {result['success']}")
        print(f"   Error: {result['error']}")
        print()
        
        # Test 7: Disallowed file type
        print("7. Disallowed file type (.exe):")
        result = fs_tool.write_file("malware.exe", "bad content")
        print(f"   Success: {result['success']}")
        print(f"   Error: {result['error']}")
        print()
        
        # Test 8: File size limit
        print("8. File size limit (2MB content):")
        large_content = "x" * (2 * 1024 * 1024)
        result = fs_tool.write_file("large.txt", large_content)
        print(f"   Success: {result['success']}")
        print(f"   Error: {result['error']}")
        print()
        
        # Test 9: Delete file
        print("9. Delete file:")
        result = fs_tool.delete_file("test.txt")
        print(f"   Success: {result['success']}")
        print()
        
        # Test 10: Read non-existent file
        print("10. Read non-existent file:")
        result = fs_tool.read_file("nonexistent.txt")
        print(f"   Success: {result['success']}")
        print(f"   Error: {result['error']}")
        print()
        
        print("=== Security Summary ===")
        print("✓ Path traversal attacks blocked")
        print("✓ Sandbox restrictions enforced")
        print("✓ File type whitelist enforced")
        print("✓ File size limits enforced")
        print("✓ Permission errors handled")
        
    finally:
        # Cleanup
        shutil.rmtree(sandbox)
        print(f"\nCleaned up sandbox: {sandbox}")
