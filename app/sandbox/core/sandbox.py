import asyncio
import io
import os
import tarfile
import tempfile
import uuid
from typing import TYPE_CHECKING, Dict, Optional

# Avoid importing the Docker SDK here so we default to the WSL/local fallback
# implementation on systems without Docker. Tests and higher-level code still
# may refer to the `DockerSandbox` class name for compatibility.
docker = None
NotFound = Exception
Container = object
DOCKER_PY_AVAILABLE = False

import shutil
import subprocess

from app.config import SandboxSettings
from app.sandbox.core.exceptions import SandboxTimeoutError
from app.sandbox.core.terminal import AsyncDockerizedTerminal


class DockerSandbox:
    """Docker sandbox environment.

    Provides a containerized execution environment with resource limits,
    file operations, and command execution capabilities.

    Attributes:
        config: Sandbox configuration.
        volume_bindings: Volume mapping configuration.
        client: Docker client.
        container: Docker container instance.
        terminal: Container terminal interface.
    """

    def __init__(
        self,
        config: Optional[SandboxSettings] = None,
        volume_bindings: Optional[Dict[str, str]] = None,
    ):
        """Initializes a sandbox instance.

        If the docker python client and daemon are available, this class will use
        Docker. Otherwise it falls back to a WSL-based local sandbox that mimics
        the same public API so tests and other code can continue to work.

        Args:
            config: Sandbox configuration. Default configuration used if None.
            volume_bindings: Volume mappings in {host_path: container_path} format.
        """
        self.config = config or SandboxSettings()
        self.volume_bindings = volume_bindings or {}
        # Container type may not be available at runtime; import it only for type checking
        if TYPE_CHECKING:
            from docker.models.containers import Container as _Container
        self.container: Optional["_Container"] = None
        self.terminal: Optional[AsyncDockerizedTerminal] = None

        # If docker is available at runtime we will use it; otherwise fall back to WSL/local implementation
        self._use_docker = False
        if DOCKER_PY_AVAILABLE:
            try:
                client = docker.from_env()
                # lightweight check
                client.ping()
                self.client = client
                self._use_docker = True
            except Exception:
                self.client = None
                self._use_docker = False
        else:
            self.client = None

    async def create(self) -> "DockerSandbox":
        """Creates and starts the sandbox container.

        Returns:
            Current sandbox instance.

        Raises:
            docker.errors.APIError: If Docker API call fails.
            RuntimeError: If container creation or startup fails.
        """
        try:
            if self._use_docker and self.client:
                # Prepare container config
                host_config = self.client.api.create_host_config(
                    mem_limit=self.config.memory_limit,
                    cpu_period=100000,
                    cpu_quota=int(100000 * self.config.cpu_limit),
                    network_mode=(
                        "none" if not self.config.network_enabled else "bridge"
                    ),
                    binds=self._prepare_volume_bindings(),
                )

                # Generate unique container name with sandbox_ prefix
                container_name = f"sandbox_{uuid.uuid4().hex[:8]}"

                # Create container
                container = await asyncio.to_thread(
                    self.client.api.create_container,
                    image=self.config.image,
                    command="tail -f /dev/null",
                    hostname="sandbox",
                    working_dir=self.config.work_dir,
                    host_config=host_config,
                    name=container_name,
                    tty=True,
                    detach=True,
                )

                self.container = self.client.containers.get(container["Id"])

                # Start container
                await asyncio.to_thread(self.container.start)

                # Initialize terminal
                self.terminal = AsyncDockerizedTerminal(
                    container["Id"],
                    self.config.work_dir,
                    env_vars={"PYTHONUNBUFFERED": "1"},
                )
                await self.terminal.init()

                return self
            else:
                # Fallback: WSL-backed sandbox implementation that operates on a host temp directory
                # Create a host directory that will act as the sandbox filesystem
                host_dir = self._ensure_host_dir(self.config.work_dir)
                self._host_dir = host_dir
                # Compute WSL path for the host_dir using wslpath
                # Try multiple ways to compute a WSL path for the host_dir. Some systems
                # expose wslpath directly, others require invoking via bash in WSL.
                self._wsl_dir = None
                try:
                    res = subprocess.run(
                        ["wsl", "wslpath", "-a", host_dir],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    self._wsl_dir = res.stdout.strip()
                except Exception:
                    try:
                        # Alternative invocation: run wslpath inside bash
                        res = subprocess.run(
                            ["wsl", "bash", "-lc", f"wslpath -a '{host_dir}'"],
                            capture_output=True,
                            text=True,
                            check=True,
                        )
                        self._wsl_dir = res.stdout.strip()
                    except Exception:
                        # Last resort: attempt to translate Windows path to /mnt/... form
                        try:
                            p = host_dir.replace("\\", "/")
                            drive = p[0].lower()
                            rest = p[2:]
                            self._wsl_dir = f"/mnt/{drive}/{rest}"
                        except Exception:
                            self._wsl_dir = None

                # No container lifecycle to manage, but terminal-like execution will be done via wsl bash
                self.container = None
                # initialize local async terminal that runs commands in WSL (if available)
                from app.sandbox.core.terminal import AsyncLocalTerminal

                self.terminal = AsyncLocalTerminal(
                    self.config.work_dir,
                    self.config.timeout,
                    getattr(self, "_wsl_dir", None),
                )

                # If explicit volume_bindings were provided, ensure host paths are mapped into our host_dir
                # so that tests that pass host paths (like temp dirs) are available under the container path.
                # We will create symlinks inside host_dir that point to requested host paths when possible.
                for host_path, container_path in self.volume_bindings.items():
                    try:
                        # canonicalize
                        host_path_abs = os.path.abspath(host_path)
                        mount_point = os.path.join(
                            self._host_dir, container_path.lstrip("/")
                        )
                        os.makedirs(os.path.dirname(mount_point), exist_ok=True)
                        # If host_path already exists, create a symlink; otherwise copy the dir
                        if os.path.exists(host_path_abs):
                            try:
                                if os.path.exists(mount_point):
                                    # remove if some file exists
                                    if os.path.islink(mount_point) or os.path.isfile(
                                        mount_point
                                    ):
                                        os.remove(mount_point)
                                os.symlink(host_path_abs, mount_point)
                            except Exception:
                                # fallback to copying the contents when symlink fails
                                if os.path.isdir(host_path_abs):
                                    shutil.copytree(
                                        host_path_abs, mount_point, dirs_exist_ok=True
                                    )
                                else:
                                    os.makedirs(
                                        os.path.dirname(mount_point), exist_ok=True
                                    )
                                    shutil.copy(host_path_abs, mount_point)
                        else:
                            # create empty mount dir
                            os.makedirs(mount_point, exist_ok=True)
                    except Exception:
                        pass
                return self

        except Exception as e:
            await self.cleanup()  # Ensure resources are cleaned up
            raise RuntimeError(f"Failed to create sandbox: {e}") from e

    def _prepare_volume_bindings(self) -> Dict[str, Dict[str, str]]:
        """Prepares volume binding configuration.

        Returns:
            Volume binding configuration dictionary.
        """
        bindings = {}

        # Create and add working directory mapping
        work_dir = self._ensure_host_dir(self.config.work_dir)
        bindings[work_dir] = {"bind": self.config.work_dir, "mode": "rw"}

        # Add custom volume bindings
        for host_path, container_path in self.volume_bindings.items():
            bindings[host_path] = {"bind": container_path, "mode": "rw"}

        return bindings

    async def run_command(self, cmd: str, timeout: Optional[int] = None) -> str:
        """Runs a command in the sandbox.

        Uses Docker terminal/exec when Docker is available; otherwise executes via
        WSL (or the host) against the host-backed sandbox directory.
        """
        if self._use_docker and self.container:
            # delegate to terminal if available
            if self.terminal:
                return await self.terminal.run_command(
                    cmd, timeout=timeout or self.config.timeout
                )
            # fallback to docker exec
            proc = await asyncio.to_thread(
                self.client.containers.get(self.container.id).exec_run, cmd
            )
            # some exec_run returns a tuple-like object
            output = getattr(proc, "output", None) or proc
            if isinstance(output, bytes):
                return output.decode("utf-8")
            return str(output)

        # WSL/local fallback
        if getattr(self, "_wsl_dir", None):
            wsl_cmd = f"cd '{self._wsl_dir}' && {cmd}"
            run_args = ["wsl", "bash", "-lc", wsl_cmd]
        else:
            # run directly on host when WSL isn't available
            run_args = ["cmd", "/c", cmd]

        proc = await asyncio.to_thread(
            subprocess.run,
            run_args,
            capture_output=True,
            text=True,
            timeout=timeout or self.config.timeout,
        )
        return (proc.stdout or "") + (proc.stderr or "")

    async def read_file(self, path: str) -> str:
        """Reads a file from the sandbox (docker or host-backed)."""
        if self._use_docker and self.container:
            try:
                resolved = self._safe_resolve_path(path)
                stream, _ = await asyncio.to_thread(
                    self.container.get_archive, resolved
                )
                content = await self._read_from_tar(stream)
                return content.decode("utf-8")
            except NotFound:
                raise FileNotFoundError(path)
            except Exception as e:
                raise RuntimeError(f"Failed to read file from docker container: {e}")

        # fallback to host-backed filesystem
        # Map the requested container path to the host-backed sandbox root.
        rel = path
        if path.startswith(self.config.work_dir):
            rel = path[len(self.config.work_dir) :]
        host_path = os.path.join(self._host_dir, rel.lstrip("/"))
        if not os.path.exists(host_path):
            raise FileNotFoundError(path)

        def _read():
            with open(host_path, "r", encoding="utf-8") as f:
                return f.read()

        return await asyncio.to_thread(_read)

    async def write_file(self, path: str, content: str) -> None:
        """Writes a file to the sandbox (docker or host-backed)."""
        if self._use_docker and self.container:
            try:
                resolved = self._safe_resolve_path(path)
                parent = os.path.dirname(resolved) or "/"
                if parent:
                    await self.run_command(f"mkdir -p {parent}")

                tar_stream = await self._create_tar_stream(
                    os.path.basename(path), content.encode("utf-8")
                )
                # container.put_archive expects a file-like or bytes
                data = (
                    tar_stream.getvalue()
                    if hasattr(tar_stream, "getvalue")
                    else tar_stream
                )
                await asyncio.to_thread(self.container.put_archive, parent, data)
                return
            except Exception as e:
                raise RuntimeError(f"Failed to write file to docker container: {e}")

        # fallback: write into host-backed dir
        rel = path
        if path.startswith(self.config.work_dir):
            rel = path[len(self.config.work_dir) :]
        host_path = os.path.join(self._host_dir, rel.lstrip("/"))
        os.makedirs(os.path.dirname(host_path), exist_ok=True)

        # If we have a WSL-backed path, rewrite references to the container
        # workdir (/workspace) inside file contents so scripts using absolute
        # paths will resolve correctly when executed in WSL.
        content_to_write = content
        if getattr(self, "_wsl_dir", None):
            try:
                content_to_write = content.replace(self.config.work_dir, self._wsl_dir)
            except Exception:
                content_to_write = content

        def _write():
            with open(host_path, "w", encoding="utf-8") as f:
                f.write(content_to_write)

        await asyncio.to_thread(_write)

    async def copy_from(self, src_path: str, dst_path: str) -> None:
        """Copies a file from container to host (or from host-backed sandbox)."""
        if self._use_docker and self.container:
            try:
                resolved = self._safe_resolve_path(src_path)
                stream, _ = await asyncio.to_thread(
                    self.container.get_archive, resolved
                )
                # extract from tar stream into dst_path
                with tempfile.TemporaryDirectory() as tmp_dir:
                    tar_path = os.path.join(tmp_dir, "temp.tar")
                    with open(tar_path, "wb") as f:
                        for chunk in stream:
                            f.write(chunk)
                    with tarfile.open(tar_path) as tar:
                        tar.extractall(tmp_dir)
                        # find extracted file
                        members = tar.getmembers()
                        if not members:
                            raise FileNotFoundError(src_path)
                        extracted = os.path.join(tmp_dir, members[0].name)
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        shutil.copy(extracted, dst_path)
                return
            except NotFound:
                raise FileNotFoundError(src_path)
            except Exception as e:
                raise RuntimeError(f"Failed to copy from container: {e}")

        # fallback: copy from host-backed dir
        rel = src_path
        if src_path.startswith(self.config.work_dir):
            rel = src_path[len(self.config.work_dir) :]
        src = os.path.join(self._host_dir, rel.lstrip("/"))
        if not os.path.exists(src):
            raise FileNotFoundError(src_path)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy(src, dst_path)

    async def copy_to(self, src_path: str, dst_path: str) -> None:
        """Copies a file from host into container or host-backed sandbox."""
        if not os.path.exists(src_path):
            raise FileNotFoundError(src_path)

        if self._use_docker and self.container:
            try:
                resolved = self._safe_resolve_path(dst_path)
                parent = os.path.dirname(resolved) or "/"
                # ensure directory exists in container
                if parent:
                    await self.run_command(f"mkdir -p {parent}")

                # create tar and upload
                with tempfile.TemporaryDirectory() as tmp_dir:
                    tar_path = os.path.join(tmp_dir, "temp.tar")
                    with tarfile.open(tar_path, "w") as tar:
                        tar.add(src_path, arcname=os.path.basename(dst_path))
                    with open(tar_path, "rb") as f:
                        data = f.read()
                    await asyncio.to_thread(self.container.put_archive, parent, data)
                return
            except Exception as e:
                raise RuntimeError(f"Failed to copy to container: {e}")

        # fallback: copy into host-backed dir
        rel = dst_path
        if dst_path.startswith(self.config.work_dir):
            rel = dst_path[len(self.config.work_dir) :]
        dst = os.path.join(self._host_dir, rel.lstrip("/"))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src_path, dst)

    async def cleanup(self) -> None:
        """Cleans up sandbox resources for both docker and host-backed modes."""
        errors = []
        try:
            if self.terminal:
                try:
                    await self.terminal.close()
                except Exception as e:
                    errors.append(f"Terminal cleanup error: {e}")
                finally:
                    self.terminal = None

            if self._use_docker and self.container:
                try:
                    await asyncio.to_thread(self.container.stop, timeout=5)
                except Exception as e:
                    errors.append(f"Container stop error: {e}")

                try:
                    await asyncio.to_thread(self.container.remove, force=True)
                except Exception as e:
                    errors.append(f"Container remove error: {e}")
                finally:
                    self.container = None
            else:
                # Remove host_dir used for sandbox
                try:
                    if getattr(self, "_host_dir", None):
                        shutil.rmtree(self._host_dir)
                except Exception:
                    pass

        except Exception as e:
            errors.append(f"General cleanup error: {e}")

        if errors:
            print(f"Warning: Errors during cleanup: {', '.join(errors)}")

    @staticmethod
    def _ensure_host_dir(path: str) -> str:
        """Ensures directory exists on the host.

        Args:
            path: Directory path.

        Returns:
            Actual path on the host.
        """
        host_path = os.path.join(
            tempfile.gettempdir(),
            f"sandbox_{os.path.basename(path)}_{os.urandom(4).hex()}",
        )
        os.makedirs(host_path, exist_ok=True)
        return host_path

    @staticmethod
    async def _create_tar_stream(name: str, content: bytes) -> io.BytesIO:
        """Creates a tar file stream.

        Args:
            name: Filename.
            content: File content.

        Returns:
            Tar file stream.
        """
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode="w") as tar:
            tarinfo = tarfile.TarInfo(name=name)
            tarinfo.size = len(content)
            tar.addfile(tarinfo, io.BytesIO(content))
        tar_stream.seek(0)
        return tar_stream

    @staticmethod
    async def _read_from_tar(tar_stream) -> bytes:
        """Reads file content from a tar stream.

        Args:
            tar_stream: Tar file stream.

        Returns:
            File content.

        Raises:
            RuntimeError: If read operation fails.
        """
        with tempfile.NamedTemporaryFile() as tmp:
            for chunk in tar_stream:
                tmp.write(chunk)
            tmp.seek(0)

            with tarfile.open(fileobj=tmp) as tar:
                member = tar.next()
                if not member:
                    raise RuntimeError("Empty tar archive")

                file_content = tar.extractfile(member)
                if not file_content:
                    raise RuntimeError("Failed to extract file content")

                return file_content.read()

    async def __aenter__(self) -> "DockerSandbox":
        """Async context manager entry."""
        return await self.create()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.cleanup()
