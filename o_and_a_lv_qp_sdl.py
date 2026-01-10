"""
This script downloads exam papers and mark schemes from xtremepapers and papacambridge websites
for CAIE and Edexcel boards and organizes them into directories based on the
exam board and subject.
"""
import os
import time
import asyncio
from backend.scraper_service import ExamScraperService

service = ExamScraperService()

def get_exam_board():
    """Prompt user to choose the examination board."""
    while True:
        print("\nChoose the examination board:")
        print("1. Cambridge (CAIE) - Xtremepapers")
        print("2. Edexcel - Xtremepapers")
        print("3. Cambridge (CAIE) - Papacambridge")
        choice = input("Enter your choice (1, 2 or 3): ").strip()
        if choice == '1':
            return ('CAIE', 'xtremepapers')
        if choice == '2':
            return ('Edexcel', 'xtremepapers')
        if choice == '3':
            return ('CAIE', 'papacambridge')
        print("Invalid choice. Please enter 1, 2 or 3.")

def get_exam_level(exam_board):
    """Prompt user to choose the examination level based on the selected board."""
    while True:
        print("\nChoose the examination level:")
        if exam_board == 'CAIE':
            print("1. IGCSE")
            print("2. O Level")
            print("3. AS and A Level")
            choice = input("Enter your choice (1, 2, or 3): ").strip()
            level_map = {'1': 'IGCSE', '2': 'O Level', '3': 'AS and A Level'}
            if choice in level_map:
                return level_map[choice]
        else:  # Edexcel
            print("1. International GCSE")
            print("2. Advanced Level")
            choice = input("Enter your choice (1 or 2): ").strip()
            level_map = {'1': 'International GCSE', '2': 'Advanced Level'}
            if choice in level_map:
                return level_map[choice]
        print("Invalid choice. Please try again.")

def print_subjects_in_columns(subjects):
    """Print the available subjects in multiple columns."""
    terminal_width = os.get_terminal_size().columns
    max_width = max(len(f"{i}. {subject}") for i, subject in enumerate(subjects, 1))
    num_columns = max(1, terminal_width // (max_width + 2))
    subject_list = [f"{i}. {subject}" for i, subject in enumerate(subjects, 1)]
    for i in range(0, len(subject_list), num_columns):
        row = subject_list[i:i + num_columns]
        print("  ".join(item.ljust(max_width) for item in row))

def get_exam_info():
    """Get exam board, source and level information."""
    exam_board, source = get_exam_board()
    exam_level = get_exam_level(exam_board)

    if source == 'xtremepapers':
        subjects = service.get_xtremepapers_subjects(exam_board, exam_level)
    else:  # papacambridge
        subjects = service.get_papacambridge_subjects(exam_level)

    if not subjects:
        print("No subjects found. Exiting...")
        return None

    return {
        'exam_board': exam_board,
        'source': source,
        'exam_level': exam_level,
        'subjects': subjects
    }

async def download_pdf_to_dir(url, filename, subject_dir, exam_board):
    """Refactored download helper for CLI."""
    try:
        # We reuse the logic but save it to the desired directory structure
        temp_path = await service.download_paper(url, filename)
        subdir = service.categorize_pdf(filename, exam_board)
        dir_path = os.path.join(subject_dir, subdir)
        os.makedirs(dir_path, exist_ok=True)
        final_path = os.path.join(dir_path, filename)
        os.replace(temp_path, final_path)
        print(f"Downloaded: {filename}")
        return True
    except (IOError, OSError) as e:
        print(f"Error downloading {filename}: {e}")
        return False

async def download_selected_pdfs(subject, pdfs, subject_dir, exam_board):
    """Download PDFs for a selected subject."""
    successful_downloads = 0
    total_pdfs = len(pdfs)

    for filename, pdf_url in pdfs.items():
        if await download_pdf_to_dir(pdf_url, filename, subject_dir, exam_board):
            successful_downloads += 1
        time.sleep(0.5)

    print(f"\nCompleted {subject}: {successful_downloads} out of {total_pdfs} "
          f"files downloaded successfully")
    return successful_downloads

async def process_subjects(exam_info):
    """Process selected subjects and download papers."""
    if not exam_info:
        return

    exam_board = exam_info['exam_board']
    source = exam_info['source']
    exam_level = exam_info['exam_level']
    subjects = exam_info['subjects']

    print(f"\nAvailable subjects for {exam_board} {exam_level}:")
    print_subjects_in_columns(subjects)

    choices = input("\nEnter the numbers of the subjects you want to download (space-separated): ")
    try:
        selected_indices = [int(x.strip()) for x in choices.split()]
    except ValueError:
        print("Invalid input. Please enter numbers only.")
        return

    selected_subjects = list(subjects.keys())
    for index in selected_indices:
        if index < 1 or index > len(selected_subjects):
            print(f"Invalid subject number: {index}")
            continue

        subject = selected_subjects[index - 1]
        subject_url = subjects[subject]
        print(f"\nProcessing {subject}...")

        pdfs = service.get_pdfs(subject_url, exam_board, source)
        if not pdfs:
            print(f"No PDFs found for {subject}")
            continue

        subject_dir = os.path.join(
            exam_board,
            exam_level,
            subject.replace('/', '_').replace('&', 'and')
        )

        os.makedirs(subject_dir, exist_ok=True)
        await download_selected_pdfs(subject, pdfs, subject_dir, exam_board)

async def main_async():
    """Main async function to run the script."""
    exam_info = get_exam_info()
    await process_subjects(exam_info)

def main():
    """Entry point for the script."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        print("\nScript execution completed.")

if __name__ == "__main__":
    main()
