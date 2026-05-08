import os
import sys
import json
import hashlib
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
import shutil

DOCS_DIR = Path("docs")
FAISS_INDEX_DIR = Path("faiss_index")
REGISTRY_FILE = Path("file_registry.json")
LOG_FILE = Path("logs/update.log")
BUILD_SCRIPT = Path("build_index.py")

os.makedirs("logs", exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FAISSUpdater:
    def __init__(self):
        self.registry = self._load_registry()
        self.changed_files = []
        self.new_files = []
        self.deleted_files = []

    def _load_registry(self) -> Dict:
        if REGISTRY_FILE.exists():
            with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_registry(self):
        with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)

    def _get_file_hash(self, file_path: Path) -> str:
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _get_supported_files(self) -> List[Path]:
        extensions = {'.txt', '.pdf', '.docx', '.md', '.rst', '.html'}
        files = []
        for ext in extensions:
            files.extend(DOCS_DIR.glob(f"*{ext}"))
        return files

    def scan_for_changes(self) -> bool:
        current_files = self._get_supported_files()
        current_file_set = {str(f.relative_to(DOCS_DIR)) for f in current_files}
        old_file_set = set(self.registry.keys())

        for file_path in current_files:
            rel_path = str(file_path.relative_to(DOCS_DIR))
            current_hash = self._get_file_hash(file_path)

            if rel_path not in self.registry:
                self.new_files.append(rel_path)
                logger.info(f"Новый файл: {rel_path}")
            elif self.registry[rel_path] != current_hash:
                self.changed_files.append(rel_path)
                logger.info(f"Изменённый файл: {rel_path}")
            else:
                logger.debug(f"Без изменений: {rel_path}")

        # Удалённые файлы (были в реестре, но пропали из папки)
        self.deleted_files = list(old_file_set - current_file_set)
        for deleted in self.deleted_files:
            logger.info(f"Удалённый файл: {deleted}")

        has_changes = bool(self.new_files or self.changed_files or self.deleted_files)

        if not has_changes:
            logger.info("Нет изменений в документах. Индекс актуален.")
        else:
            logger.info(f"Статистика изменений: +{len(self.new_files)} новых, "
                        f"~{len(self.changed_files)} изменённых, "
                        f"-{len(self.deleted_files)} удалённых")

        return has_changes

    def backup_current_index(self) -> bool:
        if not FAISS_INDEX_DIR.exists():
            logger.info("Индекс не существует, резервная копия не требуется")
            return True

        backup_dir = Path(f"faiss_index_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        try:
            shutil.copytree(FAISS_INDEX_DIR, backup_dir)
            logger.info(f"Создана резервная копия индекса: {backup_dir}")
            return True
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
            return False

    def rebuild_index(self) -> bool:
        logger.info("Запуск build_index.py для обновления индекса...")

        try:
            result = subprocess.run(
                [sys.executable, str(BUILD_SCRIPT)],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                timeout=3600
            )

            if result.returncode == 0:
                logger.info("Индекс успешно обновлён")
                logger.debug(f"Вывод скрипта:\n{result.stdout}")
                return True
            else:
                logger.error(f"Ошибка при выполнении build_index.py (код {result.returncode})")
                logger.error(f"STDERR: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Таймаут: build_index.py выполнялся более 1 часа")
            return False
        except Exception as e:
            logger.error(f"Исключение при запуске build_index.py: {e}")
            return False

    def update_registry(self):
        current_files = self._get_supported_files()
        new_registry = {}

        for file_path in current_files:
            rel_path = str(file_path.relative_to(DOCS_DIR))
            new_registry[rel_path] = self._get_file_hash(file_path)

        self.registry = new_registry
        self._save_registry()
        logger.info(f"Реестр обновлён: {len(new_registry)} файлов")

    def get_index_stats(self) -> Dict:
        stats = {
            "index_exists": FAISS_INDEX_DIR.exists(),
            "index_size_mb": 0,
            "last_updated": None
        }

        if FAISS_INDEX_DIR.exists():
            total_size = sum(f.stat().st_size for f in FAISS_INDEX_DIR.rglob('*') if f.is_file())
            stats["index_size_mb"] = round(total_size / (1024 * 1024), 2)

        if LOG_FILE.exists():
            stats["last_updated"] = datetime.fromtimestamp(LOG_FILE.stat().st_mtime).isoformat()

        return stats

    def run(self) -> Dict:
        start_time = datetime.now()
        result = {
            "status": "success",
            "start_time": start_time.isoformat(),
            "end_time": None,
            "duration_seconds": 0,
            "new_files": [],
            "changed_files": [],
            "deleted_files": [],
            "error": None,
            "index_stats": {}
        }

        try:
            logger.info("=" * 60)
            logger.info(f"ЗАПУСК ОБНОВЛЕНИЯ БАЗЫ ЗНАНИЙ: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)

            if not self.scan_for_changes():
                result["status"] = "no_changes"
                result["index_stats"] = self.get_index_stats()
                return result

            result["new_files"] = self.new_files
            result["changed_files"] = self.changed_files
            result["deleted_files"] = self.deleted_files

            if not self.backup_current_index():
                logger.warning("Продолжаем без резервной копии")

            if not self.rebuild_index():
                result["status"] = "failed"
                result["error"] = "Ошибка при rebuild_index()"
                return result

            self.update_registry()

            result["index_stats"] = self.get_index_stats()

        except Exception as e:
            logger.exception(f"Критическая ошибка: {e}")
            result["status"] = "failed"
            result["error"] = str(e)

        finally:
            end_time = datetime.now()
            result["end_time"] = end_time.isoformat()
            result["duration_seconds"] = (end_time - start_time).total_seconds()

            logger.info("=" * 60)
            logger.info(f"ЗАВЕРШЕНИЕ: {result['status']}")
            logger.info(f"Длительность: {result['duration_seconds']:.2f} сек")
            logger.info(f"Размер индекса: {result['index_stats'].get('index_size_mb', 0)} MB")
            logger.info("=" * 60)

        return result


def main():
    updater = FAISSUpdater()
    result = updater.run()

    if result["status"] == "success":
        sys.exit(0)
    elif result["status"] == "no_changes":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
