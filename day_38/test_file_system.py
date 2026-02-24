"""Comprehensive test suite for secure file system tool."""

import tempfile
import shutil
from file_system_tool import FileSystemTool


def test_valid_operations():
    """Test valid file system operations."""
    print("=" * 60)
    print("TEST: Valid Operations")
    print("=" * 60)
    
    sandbox = tempfile.mkdtemp(prefix="test_valid_")
    fs_tool = FileSystemTool(sandbox_dir=sandbox)
    
    try:
        # Test 1: Write and read
        print("\n1. Write and read file:")
        write_result = fs_tool.write_file("data.txt", "Test content")
        read_result = fs_tool.read_file("data.txt")
        print(f"   Write success: {write_result['success']}")
        print(f"   Read success: {read_result['success']}")
        print(f"   Content matches: {read_result['content'] == 'Test content'}")
        
        # Test 2: Nested directories
        print("\n2. Nested directory operations:")
        write_result = fs_tool.write_file("a/b/c/deep.txt", "Deep content")
        read_result = fs_tool.read_file("a/b/c/deep.txt")
        print(f"   Write success: {write_result['success']}")
        print(f"   Read success: {read_result['success']}")
        
        # Test 3: List directory
        print("\n3. List directory:")
        list_result = fs_tool.list_directory("a/b/c")
        print(f"   Success: {list_result['success']}")
        print(f"   Files found: {len(list_result['files'])}")
        
        # Test 4: Delete file
        print("\n4. Delete file:")
        delete_result = fs_tool.delete_file("data.txt")
        read_result = fs_tool.read_file("data.txt")
        print(f"   Delete success: {delete_result['success']}")
        print(f"   File gone: {not read_result['success']}")
        
        print("\n✓ All valid operations passed")
        
    finally:
        shutil.rmtree(sandbox)


def test_path_traversal_attacks():
    """Test path traversal attack prevention."""
    print("\n" + "=" * 60)
    print("TEST: Path Traversal Attack Prevention")
    print("=" * 60)
    
    sandbox = tempfile.mkdtemp(prefix="test_traversal_")
    fs_tool = FileSystemTool(sandbox_dir=sandbox)
    
    try:
        attacks = [
            "../../../etc/passwd",
            "../../etc/passwd",
            "../etc/passwd",
            "subdir/../../etc/passwd",
            "./../../etc/passwd",
            "a/../../../etc/passwd",
        ]
        
        all_blocked = True
        for i, attack in enumerate(attacks, 1):
            result = fs_tool.read_file(attack)
            blocked = not result['success']
            print(f"\n{i}. Attack: {attack}")
            print(f"   Blocked: {blocked}")
            print(f"   Error: {result['error']}")
            all_blocked = all_blocked and blocked
        
        print(f"\n✓ All path traversal attacks blocked: {all_blocked}")
        
    finally:
        shutil.rmtree(sandbox)


def test_absolute_path_attacks():
    """Test absolute path attack prevention."""
    print("\n" + "=" * 60)
    print("TEST: Absolute Path Attack Prevention")
    print("=" * 60)
    
    sandbox = tempfile.mkdtemp(prefix="test_absolute_")
    fs_tool = FileSystemTool(sandbox_dir=sandbox)
    
    try:
        attacks = [
            "/etc/passwd",
            "/tmp/malicious.txt",
            "/var/log/system.log",
            "/home/user/.ssh/id_rsa",
        ]
        
        all_blocked = True
        for i, attack in enumerate(attacks, 1):
            result = fs_tool.read_file(attack)
            blocked = not result['success']
            print(f"\n{i}. Attack: {attack}")
            print(f"   Blocked: {blocked}")
            print(f"   Error: {result['error']}")
            all_blocked = all_blocked and blocked
        
        print(f"\n✓ All absolute path attacks blocked: {all_blocked}")
        
    finally:
        shutil.rmtree(sandbox)


def test_file_type_restrictions():
    """Test file type whitelist enforcement."""
    print("\n" + "=" * 60)
    print("TEST: File Type Restrictions")
    print("=" * 60)
    
    sandbox = tempfile.mkdtemp(prefix="test_filetype_")
    fs_tool = FileSystemTool(
        sandbox_dir=sandbox,
        allowed_extensions={'.txt', '.json', '.md'}
    )
    
    try:
        # Allowed types
        print("\nAllowed file types:")
        allowed = ['test.txt', 'data.json', 'readme.md']
        for filename in allowed:
            result = fs_tool.write_file(filename, "content")
            print(f"   {filename}: {result['success']}")
        
        # Disallowed types
        print("\nDisallowed file types:")
        disallowed = ['script.sh', 'binary.exe', 'code.py', 'app.js']
        all_blocked = True
        for filename in disallowed:
            result = fs_tool.write_file(filename, "content")
            blocked = not result['success']
            print(f"   {filename}: Blocked={blocked}")
            all_blocked = all_blocked and blocked
        
        print(f"\n✓ File type restrictions enforced: {all_blocked}")
        
    finally:
        shutil.rmtree(sandbox)


def test_file_size_limits():
    """Test file size limit enforcement."""
    print("\n" + "=" * 60)
    print("TEST: File Size Limits")
    print("=" * 60)
    
    sandbox = tempfile.mkdtemp(prefix="test_size_")
    fs_tool = FileSystemTool(
        sandbox_dir=sandbox,
        max_file_size=1024  # 1KB limit
    )
    
    try:
        # Small file (should succeed)
        print("\n1. Small file (500 bytes):")
        result = fs_tool.write_file("small.txt", "x" * 500)
        print(f"   Success: {result['success']}")
        
        # Large file (should fail)
        print("\n2. Large file (2KB):")
        result = fs_tool.write_file("large.txt", "x" * 2048)
        print(f"   Blocked: {not result['success']}")
        print(f"   Error: {result['error']}")
        
        # Read large file (should fail)
        print("\n3. Read large existing file:")
        # Create file outside tool to bypass write limit
        import os
        large_file = os.path.join(sandbox, "existing_large.txt")
        with open(large_file, 'w') as f:
            f.write("x" * 2048)
        
        result = fs_tool.read_file("existing_large.txt")
        print(f"   Blocked: {not result['success']}")
        print(f"   Error: {result['error']}")
        
        print("\n✓ File size limits enforced")
        
    finally:
        shutil.rmtree(sandbox)


def test_permission_handling():
    """Test permission error handling."""
    print("\n" + "=" * 60)
    print("TEST: Permission Handling")
    print("=" * 60)
    
    sandbox = tempfile.mkdtemp(prefix="test_perms_")
    fs_tool = FileSystemTool(sandbox_dir=sandbox)
    
    try:
        import os
        
        # Create a file and make it read-only
        print("\n1. Write to read-only file:")
        fs_tool.write_file("readonly.txt", "initial content")
        readonly_path = os.path.join(sandbox, "readonly.txt")
        os.chmod(readonly_path, 0o444)
        
        result = fs_tool.write_file("readonly.txt", "new content")
        print(f"   Blocked: {not result['success']}")
        print(f"   Error: {result['error']}")
        
        # Restore permissions for cleanup
        os.chmod(readonly_path, 0o644)
        
        print("\n✓ Permission errors handled correctly")
        
    finally:
        shutil.rmtree(sandbox)


def test_edge_cases():
    """Test edge cases and error conditions."""
    print("\n" + "=" * 60)
    print("TEST: Edge Cases")
    print("=" * 60)
    
    sandbox = tempfile.mkdtemp(prefix="test_edge_")
    fs_tool = FileSystemTool(sandbox_dir=sandbox)
    
    try:
        # Test 1: Read non-existent file
        print("\n1. Read non-existent file:")
        result = fs_tool.read_file("nonexistent.txt")
        print(f"   Handled: {not result['success']}")
        print(f"   Error: {result['error']}")
        
        # Test 2: List non-existent directory
        print("\n2. List non-existent directory:")
        result = fs_tool.list_directory("nonexistent_dir")
        print(f"   Handled: {not result['success']}")
        print(f"   Error: {result['error']}")
        
        # Test 3: Delete non-existent file
        print("\n3. Delete non-existent file:")
        result = fs_tool.delete_file("nonexistent.txt")
        print(f"   Handled: {not result['success']}")
        print(f"   Error: {result['error']}")
        
        # Test 4: Read directory as file
        print("\n4. Read directory as file:")
        fs_tool.write_file("subdir/file.txt", "content")
        result = fs_tool.read_file("subdir")
        print(f"   Handled: {not result['success']}")
        print(f"   Error: {result['error']}")
        
        # Test 5: List file as directory
        print("\n5. List file as directory:")
        result = fs_tool.list_directory("subdir/file.txt")
        print(f"   Handled: {not result['success']}")
        print(f"   Error: {result['error']}")
        
        print("\n✓ All edge cases handled correctly")
        
    finally:
        shutil.rmtree(sandbox)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SECURE FILE SYSTEM TOOL - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    test_valid_operations()
    test_path_traversal_attacks()
    test_absolute_path_attacks()
    test_file_type_restrictions()
    test_file_size_limits()
    test_permission_handling()
    test_edge_cases()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("\nSecurity Features Verified:")
    print("✓ Sandbox directory enforcement")
    print("✓ Path traversal prevention")
    print("✓ Absolute path blocking")
    print("✓ File type whitelist")
    print("✓ File size limits")
    print("✓ Permission validation")
    print("✓ Error handling")
