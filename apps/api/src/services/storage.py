"""
Storage Service - manages dashboard YAML file storage.
MVP implementation uses local filesystem in /dashboards/ directory with JSON index.

Phase 6 Refactor: YAML as Single Source of Truth
- Removed all database operations
- YAML files are the ONLY source of dashboard definitions
- Lightweight JSON index for fast listing (no DB queries)

PDR Reference: §3 (Architecture Overview - YAML Storage), §4 (Data & Control Flows), §11 (Acceptance Criteria)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
import yaml

from src.core.exceptions import (
    DashboardAlreadyExistsException,
    DashboardNotFoundException,
    StorageException,
)
from src.models.yaml_schema import DashboardYAML

logger = structlog.get_logger(__name__)


class StorageService:
    """
    Service for storing and retrieving dashboard YAML files.

    Phase 6: YAML as Single Source of Truth
    - Files stored in /dashboards/ directory (simple filesystem)
    - Index stored in /dashboards/.index.json for fast listing
    - NO database operations - YAML files are the single source of truth
    - File path: /dashboards/{slug}.yaml
    - Version tracking via YAML metadata

    Future: Migrate to GCS with object versioning or Git repository.

    PDR §11 Acceptance: "Dashboard save writes YAML to storage and updates index"
    """

    def __init__(self, storage_root: Optional[Path] = None):
        """
        Initialize storage service.

        Args:
            storage_root: Root directory for dashboard files (defaults to /dashboards/)
        """
        self.storage_root = storage_root or Path("/dashboards")
        self.index_path = self.storage_root / ".index.json"

        # Ensure storage directory exists
        self._ensure_storage_directory()

    def _ensure_storage_directory(self) -> None:
        """Ensure storage root directory exists."""
        try:
            self.storage_root.mkdir(parents=True, exist_ok=True)
            logger.info(
                "storage_directory_initialized",
                path=str(self.storage_root),
            )
        except Exception as e:
            logger.error(
                "storage_directory_creation_failed",
                path=str(self.storage_root),
                error=str(e),
            )
            # Don't raise - this might be expected in some environments (e.g., Cloud Run with read-only FS)

    async def save_dashboard(
        self,
        dashboard_yaml: DashboardYAML,
        owner_email: str,
        overwrite: bool = False,
    ) -> DashboardYAML:
        """
        Save dashboard YAML to storage and update index.

        Args:
            dashboard_yaml: Validated dashboard YAML
            owner_email: Owner email address
            overwrite: Whether to overwrite existing dashboard

        Returns:
            DashboardYAML (with enriched metadata)

        Raises:
            DashboardAlreadyExistsException: If dashboard exists and overwrite=False
            StorageException: If file write fails
        """
        slug = dashboard_yaml.metadata.slug

        logger.info(
            "saving_dashboard",
            slug=slug,
            owner_email=owner_email,
            overwrite=overwrite,
        )

        # Check if dashboard exists
        file_path = self._get_file_path(slug)
        existing_yaml = None

        if file_path.exists():
            if not overwrite:
                raise DashboardAlreadyExistsException(slug=slug)
            # Load existing to preserve created_at
            try:
                existing_yaml = await self.load_dashboard_yaml(slug)
            except Exception:
                pass  # Ignore errors, will create new timestamps

        # Enrich metadata
        now = datetime.utcnow()
        dashboard_yaml.metadata.owner_email = owner_email
        dashboard_yaml.metadata.updated_at = now

        # Preserve created_at on updates, or set for new dashboards
        if existing_yaml and existing_yaml.metadata.created_at:
            dashboard_yaml.metadata.created_at = existing_yaml.metadata.created_at
        else:
            dashboard_yaml.metadata.created_at = now

        # Preserve access tracking on updates
        if existing_yaml:
            dashboard_yaml.metadata.access_count = existing_yaml.metadata.access_count
            dashboard_yaml.metadata.last_accessed = existing_yaml.metadata.last_accessed

        # Write YAML to file
        try:
            import aiofiles

            yaml_content = yaml.dump(
                dashboard_yaml.model_dump(mode="json", exclude_none=True),
                default_flow_style=False,
                sort_keys=False,
            )

            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(yaml_content)

            logger.info(
                "yaml_file_written",
                slug=slug,
                path=str(file_path),
                size_bytes=len(yaml_content),
            )

        except Exception as e:
            logger.error(
                "yaml_file_write_failed",
                slug=slug,
                path=str(file_path),
                error=str(e),
            )
            raise StorageException(
                message=f"Failed to write YAML file: {str(e)}",
                storage_path=str(file_path),
                operation="write",
                original_error=e,
            )

        # Update index
        await self._update_index(dashboard_yaml)

        logger.info("dashboard_saved", slug=slug)
        return dashboard_yaml

    async def load_dashboard_yaml(self, slug: str) -> DashboardYAML:
        """
        Load dashboard YAML from storage.

        Args:
            slug: Dashboard slug

        Returns:
            Parsed DashboardYAML

        Raises:
            DashboardNotFoundException: If dashboard not found
            StorageException: If file read or parse fails
        """
        logger.info("loading_dashboard_yaml", slug=slug)

        file_path = self._get_file_path(slug)

        if not file_path.exists():
            raise DashboardNotFoundException(slug=slug)

        # Read and parse YAML file
        try:
            import aiofiles

            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                yaml_content = await f.read()

            yaml_dict = yaml.safe_load(yaml_content)
            dashboard_yaml = DashboardYAML.model_validate(yaml_dict)

            logger.info(
                "dashboard_yaml_loaded",
                slug=slug,
                queries=len(dashboard_yaml.queries),
                charts=len(dashboard_yaml.layout),
            )

            return dashboard_yaml

        except FileNotFoundError:
            logger.error(
                "dashboard_file_not_found",
                slug=slug,
                path=str(file_path),
            )
            raise DashboardNotFoundException(slug=slug)

        except Exception as e:
            logger.error(
                "dashboard_yaml_load_failed",
                slug=slug,
                path=str(file_path),
                error=str(e),
            )
            raise StorageException(
                message=f"Failed to load dashboard YAML: {str(e)}",
                storage_path=str(file_path),
                operation="read",
                original_error=e,
            )

    async def delete_dashboard(self, slug: str) -> bool:
        """
        Delete dashboard from storage and index.

        Args:
            slug: Dashboard slug

        Returns:
            True if deleted, False if not found

        Raises:
            StorageException: If file deletion fails
        """
        logger.info("deleting_dashboard", slug=slug)

        file_path = self._get_file_path(slug)

        if not file_path.exists():
            logger.warning("dashboard_not_found_for_deletion", slug=slug)
            return False

        # Delete file
        try:
            import aiofiles.os

            await aiofiles.os.remove(str(file_path))
            logger.info("dashboard_file_deleted", slug=slug, path=str(file_path))

        except Exception as e:
            logger.error(
                "dashboard_file_deletion_failed",
                slug=slug,
                path=str(file_path),
                error=str(e),
            )
            raise StorageException(
                message=f"Failed to delete dashboard file: {str(e)}",
                storage_path=str(file_path),
                operation="delete",
                original_error=e,
            )

        # Remove from index
        await self._remove_from_index(slug)

        logger.info("dashboard_deleted", slug=slug)
        return True

    async def list_dashboards(
        self,
        page: int = 1,
        page_size: int = 20,
        view_type: Optional[str] = None,
        tag: Optional[str] = None,
        owner_email: Optional[str] = None,
    ) -> tuple[List[dict], int]:
        """
        List dashboards with pagination (from index).

        Args:
            page: Page number (1-indexed)
            page_size: Items per page
            view_type: Filter by view type
            tag: Filter by single tag
            owner_email: Filter by owner email

        Returns:
            Tuple of (dashboards list, total count)
        """
        logger.info("listing_dashboards", page=page, page_size=page_size)

        # Read index
        index = await self._read_index()
        dashboards = index.get("dashboards", [])

        # Apply filters in Python
        filtered = dashboards

        if owner_email:
            filtered = [d for d in filtered if d.get("owner_email") == owner_email]

        if view_type:
            filtered = [d for d in filtered if d.get("view_type") == view_type]

        if tag:
            filtered = [d for d in filtered if tag in d.get("tags", [])]

        # Sort by updated_at descending
        filtered.sort(key=lambda d: d.get("updated_at", ""), reverse=True)

        # Apply pagination
        total = len(filtered)
        offset = (page - 1) * page_size
        paginated = filtered[offset : offset + page_size]

        logger.info(
            "dashboards_listed",
            count=len(paginated),
            total=total,
            page=page,
            page_size=page_size,
        )

        return paginated, total

    async def record_access(self, slug: str) -> None:
        """
        Record dashboard access (increment counter, update timestamp).

        Args:
            slug: Dashboard slug
        """
        try:
            # Load YAML
            dashboard_yaml = await self.load_dashboard_yaml(slug)

            # Update access tracking
            dashboard_yaml.metadata.access_count += 1
            dashboard_yaml.metadata.last_accessed = datetime.utcnow()

            # Save back (preserving all other data)
            file_path = self._get_file_path(slug)
            import aiofiles

            yaml_content = yaml.dump(
                dashboard_yaml.model_dump(mode="json", exclude_none=True),
                default_flow_style=False,
                sort_keys=False,
            )

            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(yaml_content)

            # Update index
            await self._update_index(dashboard_yaml)

            logger.debug("dashboard_access_recorded", slug=slug)

        except Exception as e:
            # Don't fail the request if access tracking fails
            logger.warning("dashboard_access_tracking_failed", slug=slug, error=str(e))

    async def check_dashboard_exists(self, slug: str) -> bool:
        """
        Check if dashboard exists.

        Args:
            slug: Dashboard slug

        Returns:
            True if exists, False otherwise
        """
        file_path = self._get_file_path(slug)
        return file_path.exists()

    def _get_file_path(self, slug: str) -> Path:
        """
        Get file path for dashboard slug.

        Args:
            slug: Dashboard slug

        Returns:
            Path to YAML file
        """
        return self.storage_root / f"{slug}.yaml"

    async def _read_index(self) -> dict:
        """
        Read index from .index.json file.

        Returns:
            Index dictionary with dashboards list

        Raises:
            StorageException: If index read fails
        """
        if not self.index_path.exists():
            logger.warning("index_not_found_rebuilding")
            await self._rebuild_index()

        try:
            import aiofiles

            async with aiofiles.open(self.index_path, "r", encoding="utf-8") as f:
                content = await f.read()
                return json.loads(content)

        except Exception as e:
            logger.error("index_read_failed", error=str(e))
            # Return empty index on error
            return {"generated_at": datetime.utcnow().isoformat(), "dashboards": []}

    async def _update_index(self, dashboard_yaml: DashboardYAML) -> None:
        """
        Update index with dashboard metadata.

        Args:
            dashboard_yaml: Dashboard YAML to add/update in index
        """
        try:
            # Read current index
            index = await self._read_index()

            # Remove existing entry with same slug
            dashboards = [d for d in index.get("dashboards", []) if d.get("slug") != dashboard_yaml.metadata.slug]

            # Add new entry
            file_path = self._get_file_path(dashboard_yaml.metadata.slug)
            dashboards.append(
                {
                    "slug": dashboard_yaml.metadata.slug,
                    "name": dashboard_yaml.metadata.name,
                    "owner_email": dashboard_yaml.metadata.owner_email,
                    "view_type": dashboard_yaml.metadata.view_type.value,
                    "tags": dashboard_yaml.metadata.tags,
                    "created_at": dashboard_yaml.metadata.created_at.isoformat(),
                    "updated_at": dashboard_yaml.metadata.updated_at.isoformat(),
                    "access_count": dashboard_yaml.metadata.access_count,
                    "last_accessed": (
                        dashboard_yaml.metadata.last_accessed.isoformat()
                        if dashboard_yaml.metadata.last_accessed
                        else None
                    ),
                    "file_path": str(file_path),
                }
            )

            # Update index
            index["dashboards"] = dashboards
            index["generated_at"] = datetime.utcnow().isoformat()

            # Write back
            import aiofiles

            async with aiofiles.open(self.index_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(index, indent=2))

            logger.debug("index_updated", slug=dashboard_yaml.metadata.slug)

        except Exception as e:
            logger.error("index_update_failed", error=str(e))
            # Don't raise - index update failure shouldn't fail the save operation

    async def _remove_from_index(self, slug: str) -> None:
        """
        Remove dashboard from index.

        Args:
            slug: Dashboard slug to remove
        """
        try:
            # Read current index
            index = await self._read_index()

            # Filter out dashboard
            dashboards = [d for d in index.get("dashboards", []) if d.get("slug") != slug]

            # Update index
            index["dashboards"] = dashboards
            index["generated_at"] = datetime.utcnow().isoformat()

            # Write back
            import aiofiles

            async with aiofiles.open(self.index_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(index, indent=2))

            logger.debug("index_entry_removed", slug=slug)

        except Exception as e:
            logger.error("index_removal_failed", slug=slug, error=str(e))
            # Don't raise - index update failure shouldn't fail the delete operation

    async def _rebuild_index(self) -> None:
        """
        Rebuild index by scanning all YAML files in storage directory.
        """
        logger.info("rebuilding_index", storage_root=str(self.storage_root))

        dashboards = []

        try:
            # Scan all .yaml files
            for file_path in self.storage_root.glob("*.yaml"):
                if file_path.name == ".index.json":
                    continue

                try:
                    # Load YAML
                    import aiofiles

                    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                        yaml_content = await f.read()

                    yaml_dict = yaml.safe_load(yaml_content)
                    dashboard_yaml = DashboardYAML.model_validate(yaml_dict)

                    # Extract metadata
                    dashboards.append(
                        {
                            "slug": dashboard_yaml.metadata.slug,
                            "name": dashboard_yaml.metadata.name,
                            "owner_email": dashboard_yaml.metadata.owner_email,
                            "view_type": dashboard_yaml.metadata.view_type.value,
                            "tags": dashboard_yaml.metadata.tags,
                            "created_at": dashboard_yaml.metadata.created_at.isoformat(),
                            "updated_at": dashboard_yaml.metadata.updated_at.isoformat(),
                            "access_count": dashboard_yaml.metadata.access_count,
                            "last_accessed": (
                                dashboard_yaml.metadata.last_accessed.isoformat()
                                if dashboard_yaml.metadata.last_accessed
                                else None
                            ),
                            "file_path": str(file_path),
                        }
                    )

                except Exception as e:
                    logger.warning("index_rebuild_skip_file", file=str(file_path), error=str(e))
                    continue

            # Write index
            index = {"generated_at": datetime.utcnow().isoformat(), "dashboards": dashboards}

            import aiofiles

            async with aiofiles.open(self.index_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(index, indent=2))

            logger.info("index_rebuilt", dashboard_count=len(dashboards))

        except Exception as e:
            logger.error("index_rebuild_failed", error=str(e))
            raise StorageException(
                message=f"Failed to rebuild index: {str(e)}",
                storage_path=str(self.index_path),
                operation="rebuild",
                original_error=e,
            )

    async def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.

        Returns:
            Dict with storage stats
        """
        # Count files in storage directory
        file_count = 0
        total_size = 0

        if self.storage_root.exists():
            for file_path in self.storage_root.glob("*.yaml"):
                file_count += 1
                total_size += file_path.stat().st_size

        # Get index count
        index = await self._read_index()
        index_count = len(index.get("dashboards", []))

        return {
            "storage_root": str(self.storage_root),
            "file_count": file_count,
            "total_size_bytes": total_size,
            "index_entry_count": index_count,
            "storage_type": "filesystem",
        }
