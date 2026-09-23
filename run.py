#!/usr/bin/env python3
"""One-command local launch for hackathon reviewers: python3 run.py."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def execute(command):
    subprocess.run([str(part) for part in command], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description="Подготовить и запустить локальный «Граф денег» одной командой.")
    parser.add_argument("--data", type=Path, default=ROOT / "FINANCE-CASE/data")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--check", action="store_true", help="собрать, пересчитать и проверить результат, затем завершить")
    parser.add_argument("--skip-install", action="store_true", help="использовать уже установленные зависимости без скачивания")
    args = parser.parse_args()
    if sys.version_info < (3, 12) or sys.version_info[:3] == (3, 14, 1):
        raise ValueError("Нужен Python 3.12 или новее, кроме версии 3.14.1.")
    if not 1 <= args.port <= 65535:
        raise ValueError("Порт должен быть числом от 1 до 65535.")
    data = args.data.resolve()
    missing = [name for name in ("nodes.parquet", "edges.parquet", "transactions.parquet") if not (data / name).is_file()]
    if missing:
        raise ValueError(f"Поместите исходные файлы организаторов в {data}. Не найдены: {', '.join(missing)}")
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    node = shutil.which("node")
    if npm is None or node is None:
        raise ValueError("Установите Node.js 22.12+ вместе с npm, затем повторите python3 run.py.")
    version = subprocess.check_output([node, "--version"], text=True).strip().lstrip("v").split(".")
    if tuple(map(int, version[:2])) < (22, 12):
        raise ValueError("Для сборки интерфейса нужен Node.js 22.12 или новее.")
    environment = ROOT / ".venv"
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.is_file():
        if args.skip_install:
            raise ValueError("Окружение .venv отсутствует. Запустите без --skip-install для подготовки.")
        print("1/4 · Подготовка локального Python-окружения", flush=True)
        execute([sys.executable, "-m", "venv", environment])
    dependency_check = (
        "from importlib.metadata import version; from pathlib import Path; "
        "requirements=[line.split('==') for line in Path('requirements.txt').read_text().splitlines() "
        "if line.strip() and not line.startswith('#')]; "
        "assert all(version(name)==expected for name,expected in requirements)"
    )
    installed = subprocess.run([str(python), "-c", dependency_check], cwd=ROOT, capture_output=True).returncode == 0
    if not installed:
        if args.skip_install:
            raise ValueError("Python-зависимости не готовы. Повторите без --skip-install.")
        execute([python, "-m", "pip", "install", "-r", ROOT / "requirements.txt"])
    frontend_ready = (ROOT / "frontend/node_modules").is_dir() and subprocess.run(
        [npm, "--prefix", str(ROOT / "frontend"), "ls", "--depth=0"], cwd=ROOT, capture_output=True
    ).returncode == 0
    if not frontend_ready:
        if args.skip_install:
            raise ValueError("Frontend-зависимости не готовы. Повторите без --skip-install.")
        execute([npm, "--prefix", ROOT / "frontend", "ci", "--no-audit", "--no-fund"])
    print("2/4 · Сборка локального интерфейса", flush=True)
    execute([npm, "--prefix", ROOT / "frontend", "run", "build"])
    print("3/4 · Расчёт ролей, временных признаков, маршрутов и сценариев", flush=True)
    execute([python, "-m", "solution", "--data", data, "--out", ROOT / "output"])
    if args.check:
        print("4/4 · Независимая проверка исходных данных и результата", flush=True)
        execute([python, ROOT / "scripts/verify_delivery.py", "--data", data, "--out", ROOT / "output"])
        execute([python, ROOT / "scripts/verify_temporal.py", "--data", data, "--out", ROOT / "output"])
        execute([python, ROOT / "scripts/verify_extensions.py", "--data", data, "--out", ROOT / "output"])
        print("Проверки расчёта и локальной выдачи пройдены. Браузерный сценарий — в README.", flush=True)
    else:
        print(f"4/4 · Откройте http://127.0.0.1:{args.port} · Остановка: Ctrl+C", flush=True)
        execute([python, "-m", "solution.server", "--data", ROOT / "output", "--ui", ROOT / "frontend/dist", "--port", args.port])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nЛокальный запуск остановлен.")
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"Не удалось запустить: {error}", file=sys.stderr)
        raise SystemExit(1)
