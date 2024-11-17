import logging
import asyncio
import argparse
from collections import defaultdict
from aiopath import AsyncPath
import aioshutil

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def read_folder(source_folder: AsyncPath):
    try:
        files_by_extension = defaultdict(list)
        async for file in source_folder.iterdir():
            if await file.is_file():
                extension = file.suffix.lower()
                files_by_extension[extension].append(file)
            elif await file.is_dir():
                await read_folder(file)
        return files_by_extension
    except Exception as e:
        logger.error(f"Помилка при зчитуванні директорії {source_folder}: {e}")


async def copy_file(file: AsyncPath, output_folder: AsyncPath):
    if not await output_folder.exists():
        await output_folder.mkdir(parents=True, exist_ok=True)

    destination_folder = output_folder / file.suffix[1:]
    if not await destination_folder.exists():
        await destination_folder.mkdir(parents=True, exist_ok=True)

    try:
        destination = destination_folder / file.name
        await aioshutil.copy(file, destination)
        logger.info(f"Файл {file} скопійовано до {destination}")
    except Exception as e:
        logger.error(f"Помилка при копіюванні файлу {file}: {e}")


async def process_files(source_folder: AsyncPath, output_folder: AsyncPath):
    files_by_extension = await read_folder(source_folder)

    tasks = []
    for extension, files in files_by_extension.items():
        for file in files:
            tasks.append(copy_file(file, output_folder))

    await asyncio.gather(*tasks)


def main():
    parser = argparse.ArgumentParser(description="Сортування файлів за розширенням")
    parser.add_argument("source_folder", type=str, help="Шлях до вихідної папки")
    parser.add_argument("output_folder", type=str, help="Шлях до цільової папки")

    args = parser.parse_args()
    source_folder = AsyncPath(args.source_folder)
    output_folder = AsyncPath(args.output_folder)

    asyncio.run(process_files(source_folder, output_folder))


if __name__ == "__main__":
    main()
