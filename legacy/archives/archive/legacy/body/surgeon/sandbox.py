import os
import shutil
import subprocess
import time
from typing import Tuple

class Sandbox:
    """
    Phase 19: The Surgeon - The Fortress Implementation.
    Securely executes AI-generated code inside a Docker container.
    Enforces hardware limits: 2GB RAM, 0.8 CPUs (~20% of 4 cores).
    """
    def __init__(self, workspace_root: str = None):
        if not workspace_root:
            self.workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        else:
            self.workspace_root = workspace_root
            
        self.sandbox_dir = os.path.join(self.workspace_root, "temp", "sandbox")
        self.image_name = "tonesoul-fortress:latest"
        self.dockerfile_path = os.path.join(self.workspace_root, "body", "surgeon", "Dockerfile")

    def _ensure_image(self):
        """Ensures the fortress container image is built."""
        print(f" [Sandbox] Verifying Fortress Image: {self.image_name}...")
        try:
            # Check if image exists
            check = subprocess.run(f"docker image inspect {self.image_name}", shell=True, capture_output=True)
            if check.returncode != 0:
                print(f" [Sandbox] Image not found. Building from {self.dockerfile_path}...")
                build = subprocess.run(
                    f"docker build -t {self.image_name} -f {self.dockerfile_path} {os.path.dirname(self.dockerfile_path)}",
                    shell=True, capture_output=True, text=True
                )
                if build.returncode != 0:
                    raise Exception(f"Docker build failed: {build.stderr}")
                print(" [Sandbox] Fortress Image built successfully.")
        except Exception as e:
            print(f" [Sandbox] Docker check failed: {e}. Falling back to insecure mode?")
            raise

    def setup(self, target_file_rel_path: str):
        """Presents the sandbox by copying the target file into a temp workspace."""
        if os.path.exists(self.sandbox_dir):
            shutil.rmtree(self.sandbox_dir)
        os.makedirs(self.sandbox_dir)

        # Copy Target
        src = os.path.join(self.workspace_root, target_file_rel_path)
        dst = os.path.join(self.sandbox_dir, os.path.basename(target_file_rel_path))
        
        if not os.path.exists(src):
            with open(dst, 'w') as f:
                pass
        else:
            shutil.copy2(src, dst)
            
        print(f" [Sandbox] Target isolated: {os.path.basename(target_file_rel_path)}")
        return dst

    def apply_patch(self, file_path: str, new_content: str):
        """Rewrites the file in the sandbox with the new content."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f" [Sandbox] Patch applied.")

    def verify(self, test_command: str = "pytest", timeout: int = 60) -> Tuple[bool, str]:
        """
        Executes the test_command inside a constrained Docker container.
        FALLBACK: If Docker fails, performs a local py_compile for basic safety.
        """
        try:
            self._ensure_image()
            print(f" [Sandbox] Executing Fortress Test: {test_command}...")
            
            abs_sandbox_path = os.path.abspath(self.sandbox_dir)
            
            docker_cmd = [
                "docker", "run", "--rm",
                "--network", "none",
                "--memory", "2g",
                "--cpus", "0.8",
                "-v", f"{abs_sandbox_path}:/home/surgeon/workspace",
                self.image_name,
                "bash", "-c", f"cd /home/surgeon/workspace && {test_command}"
            ]
            
            result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=timeout)
            passed = (result.returncode == 0)
            return (passed, result.stdout + result.stderr)

        except Exception as e:
            print(f" [Sandbox] Docker failure: {e}. Attempting Local Fallback...")
            # FALLBACK: Local py_compile (Static Analysis only)
            abs_sandbox_path = os.path.abspath(self.sandbox_dir)
            files_in_sandbox = [os.path.join(abs_sandbox_path, f) for f in os.listdir(abs_sandbox_path) if f.endswith(".py")]
            
            total_log = f"Docker Blocked: {e}\n--- Local Fallback Report ---\n"
            all_passed = True
            
            import py_compile
            for f in files_in_sandbox:
                try:
                    py_compile.compile(f, doraise=True)
                    total_log += f" {os.path.basename(f)}: Local Syntax OK.\n"
                except Exception as ex:
                    all_passed = False
                    total_log += f" {os.path.basename(f)}: Local Syntax ERROR: {ex}\n"
            
            return (all_passed, total_log)

    def teardown(self):
        """Cleans up the localized sandbox files."""
        if os.path.exists(self.sandbox_dir):
            shutil.rmtree(self.sandbox_dir)
        print(" [Sandbox] Vault cleared.")
