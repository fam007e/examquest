"""
This script downloads exam papers and mark schemes from xtremepapers and papacambridge websites
for CAIE and Edexcel boards and organizes them into directories based on the
exam board and subject.
"""
import os
import re
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://papers.xtremepape.rs/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

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
            if choice == '1':
                return 'IGCSE'
            if choice == '2':
                return 'O+Level'
            if choice == '3':
                return 'AS+and+A+Level'
        else:  # Edexcel
            print("1. International GCSE")
            print("2. Advanced Level")
            choice = input("Enter your choice (1 or 2): ").strip()
            if choice == '1':
                return 'International+GCSE'
            if choice == '2':
                return 'Advanced+Level'
        print("Invalid choice. Please try again.")

def get_subjects(exam_board, exam_level):
    """Fetch subjects for the selected exam board and level from xtremepapers."""
    if exam_board == 'CAIE':
        url = f'{BASE_URL}index.php?dirpath=./CAIE/{exam_level}/&order=0'
    else:  # Edexcel
        url = f'{BASE_URL}index.php?dirpath=./Edexcel/{exam_level}/&order=0'

    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    subject_links = soup.find_all('a', class_='directory')

    subjects = {}
    for link in subject_links:
        subject_name = link.text.strip('[]')
        if subject_name != '..':  # Skip the parent directory link
            subjects[subject_name] = BASE_URL + link['href']
    return subjects

def get_papacambridge_subjects(exam_level):
    """Fetch subjects from papacambridge."""
    base_pc_url = 'https://pastpapers.papacambridge.com/papers/caie/'
    level_map = {
        'O+Level': 'o-level',
        'AS+and+A+Level': 'as-and-a-level',
        'IGCSE': 'igcse'
    }
    url = f'{base_pc_url}{level_map[exam_level]}'
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        subjects = {}
        # Find all subject divs
        subject_items = soup.find_all('div', class_='kt-widget4__item item-folder-type')
        for item in subject_items:
            # Skip advertisement divs
            if 'adsbygoogle' in item.get('class', []):
                continue
            link = item.find('a')
            if not link:
                continue
            # Get the subject name from the span with class 'wraptext'
            subject_span = link.find('span', class_='wraptext')
            if not subject_span:
                continue
            subject_name = subject_span.text.strip()
            # Skip empty or parent directory entries
            if not subject_name or subject_name == '..':
                continue
            # Get the href link
            subject_url = link['href']
            if not subject_url.startswith('http'):
                subject_url = 'https://pastpapers.papacambridge.com/' + subject_url
            subjects[subject_name] = subject_url
        return subjects
    except requests.RequestException as e:
        print(f"Error fetching subjects: {e}")
        return {}

def get_pdfs(subject_url, exam_board):
    """Fetch PDF links for the selected subject from xtremepapers."""
    response = requests.get(subject_url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    if exam_board == 'Edexcel':
        return get_edexcel_pdfs(subject_url)

    pdf_links = soup.find_all('a', class_='file', href=re.compile(r'\.pdf$'))
    return {link.text.strip(): BASE_URL + link['href'] for link in pdf_links}

def get_edexcel_pdfs(subject_url):
    """Fetch PDF links for Edexcel subjects from xtremepapers."""
    pdfs = {}
    response = requests.get(subject_url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    year_links = soup.find_all('a', class_='directory')

    for year_link in year_links:
        if year_link.text.strip('[]') != '..':
            year_url = BASE_URL + year_link['href']
            year_response = requests.get(year_url, timeout=10)
            year_soup = BeautifulSoup(year_response.text, 'html.parser')

            qp_link = year_soup.find('a', class_='directory', text='[Question-paper]')
            ms_link = year_soup.find('a', class_='directory', text='[Mark-scheme]')

            if qp_link:
                qp_url = BASE_URL + qp_link['href']
                qp_pdfs = get_pdfs_from_page(qp_url)
                pdfs.update(qp_pdfs)

            if ms_link:
                ms_url = BASE_URL + ms_link['href']
                ms_pdfs = get_pdfs_from_page(ms_url)
                pdfs.update(ms_pdfs)

    return pdfs

def get_pdfs_from_page(url):
    """Fetch all PDF links from a specific xtremepapers page."""
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    pdf_links = soup.find_all('a', class_='file', href=re.compile(r'\.pdf$'))
    return {link.text.strip(): BASE_URL + link['href'] for link in pdf_links}

def get_papacambridge_years(subject_url):
    """Fetch available exam sessions/years for a subject from papacambridge."""
    try:
        response = requests.get(subject_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        years = {}
        year_items = soup.find_all('div', class_='kt-widget4__item item-folder-type')
        for item in year_items:
            # Skip advertisement divs
            if 'adsbygoogle' in item.get('class', []):
                continue
            link = item.find('a')
            if not link:
                continue
            year_span = link.find('span', class_='wraptext')
            if not year_span:
                continue
            year_name = year_span.text.strip()
            # Skip special folders
            skip_conditions = [
                not year_name,
                year_name == '..',
                'Solved Past Papers' in year_name,
                'Topical Past Papers' in year_name
            ]
            if any(skip_conditions):
                continue
            year_url = link['href']
            if not year_url.startswith('http'):
                year_url = 'https://pastpapers.papacambridge.com/' + year_url
            years[year_name] = year_url
        return years
    except requests.RequestException as e:
        print(f"Error fetching years: {e}")
        return {}

def get_papacambridge_pdfs(subject_url):
    """Fetch PDF links from papacambridge."""
    try:
        # First check if this is a subject page or an exam session page
        response = requests.get(subject_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Check if this page has folders (years/sessions) or PDF files
        folders = soup.find_all('div', class_='kt-widget4__item item-folder-type')
        pdf_items = soup.find_all('div', class_='kt-widget4__item item-pdf-type')
        if folders and not pdf_items:
            # This is a subject page, get years and then pdfs for each year
            all_pdfs = {}
            years = get_papacambridge_years(subject_url)
            for year_name, year_url in years.items():
                print(f"Fetching papers for {year_name}...")
                year_pdfs = get_papacambridge_session_pdfs(year_url)
                all_pdfs.update(year_pdfs)
                time.sleep(0.5)  # Be nice to the server
            return all_pdfs
        # This is already a session page with PDFs
        return get_papacambridge_session_pdfs(subject_url)
    except requests.RequestException as e:
        print(f"Error processing subject: {e}")
        return {}

def get_papacambridge_session_pdfs(session_url):
    """Fetch PDF links from a specific papacambridge exam session page."""
    pdfs = {}
    try:
        response = requests.get(session_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all PDF items
        pdf_items = soup.find_all('div', class_='kt-widget4__item item-pdf-type')
        for item in pdf_items:
            # Find the download link
            download_link = item.find('a', href=re.compile(r'download_file\.php\?files=.*\.pdf'))
            if download_link:
                # Extract file URL from the download_file.php link
                match = re.search(r'files=(.*\.pdf)', download_link['href'])
                if match:
                    pdf_url = match.group(1)
                    # Extract the actual filename from the URL
                    filename = os.path.basename(pdf_url)
                    # Use the direct PDF URL, not the download_file.php URL
                    pdfs[filename] = pdf_url
        return pdfs
    except requests.RequestException as e:
        print(f"Error fetching PDFs from session: {e}")
        return {}

def download_pdf(url, filename, subject_dir, exam_board, source):
    """Download a PDF and save it in the appropriate directory."""
    try:
        if source == 'papacambridge':
            # For direct PDF URLs from papacambridge
            response = requests.get(url, headers=HEADERS, stream=True, timeout=10)
        else:
            response = requests.get(url, timeout=10)
        response.raise_for_status()
        subdir = categorize_pdf(filename, exam_board)
        dir_path = os.path.join(subject_dir, subdir)
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, filename)
        # Use streaming for better performance with large files
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        print(f"Downloaded: {filename}")
        return True
    except requests.RequestException as e:
        print(f"Error downloading {filename}: {e}")
        return False

def categorize_pdf(filename, exam_board):
    """Categorize the PDF as question paper, mark scheme, or miscellaneous."""
    filename_lower = filename.lower()
    if exam_board == 'CAIE':
        if '_ms_' in filename_lower or 'mark_scheme' in filename_lower:
            return 'ms'
        if '_qp_' in filename_lower or 'question_paper' in filename_lower:
            return 'qp'
        return 'misc'
    # Edexcel
    if 'question' in filename_lower:
        return 'qp'
    if 'mark' in filename_lower or 'ms' in filename_lower:
        return 'ms'
    return 'misc'

def print_subjects_in_columns(subjects):
    """Print the available subjects in multiple columns."""
    terminal_width = os.get_terminal_size().columns
    max_width = max(len(f"{i}. {subject}") for i, subject in enumerate(subjects, 1))
    num_columns = max(1, terminal_width // (max_width + 2))
    subject_list = [f"{i}. {subject}" for i, subject in enumerate(subjects, 1)]
    for i in range(0, len(subject_list), num_columns):
        row = subject_list[i:i + num_columns]
        print("  ".join(item.ljust(max_width) for item in row))

def main():
    """Main function to run the script."""
    # Split function to reduce local variables
    exam_info = get_exam_info()
    process_subjects(exam_info)

def get_exam_info():
    """Get exam board, source and level information."""
    exam_board, source = get_exam_board()
    exam_level = get_exam_level(exam_board)
    
    if source == 'xtremepapers':
        subjects = get_subjects(exam_board, exam_level)
    else:  # papacambridge
        subjects = get_papacambridge_subjects(exam_level)

    if not subjects:
        print("No subjects found. Exiting...")
        return None
    
    return {
        'exam_board': exam_board,
        'source': source,
        'exam_level': exam_level,
        'subjects': subjects
    }

def process_subjects(exam_info):
    """Process selected subjects and download papers."""
    if not exam_info:
        return
    
    exam_board = exam_info['exam_board']
    source = exam_info['source']
    exam_level = exam_info['exam_level']
    subjects = exam_info['subjects']
    
    print(f"\nAvailable subjects for {exam_board} {exam_level.replace('+', ' ')}:")
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

        if source == 'xtremepapers':
            pdfs = get_pdfs(subject_url, exam_board)
        else:  # papacambridge
            pdfs = get_papacambridge_pdfs(subject_url)
        
        if not pdfs:
            print(f"No PDFs found for {subject}")
            continue
        
        # For both sources, use the same structure
        subject_dir = os.path.join(
            exam_board,
            exam_level.replace('+', ' '),
            subject.replace('/', '_').replace('&', 'and')
        )
        
        os.makedirs(subject_dir, exist_ok=True)

        successful_downloads = 0
        total_pdfs = len(pdfs)
        
        for filename, pdf_url in pdfs.items():
            if download_pdf(pdf_url, filename, subject_dir, exam_board, source):
                successful_downloads += 1
            # Add a small delay to avoid overwhelming the server
            time.sleep(0.5)
        
        print(f"\nCompleted {subject}: {successful_downloads} out of {total_pdfs} "
              f"files downloaded successfully")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"\nAn unexpected error occurred: {e}")
