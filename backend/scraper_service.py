import os
import re
import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple

class ExamScraperService:
    BASE_URL = 'https://papers.xtremepape.rs/'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    def get_xtremepapers_subjects(self, exam_board: str, exam_level: str) -> Dict[str, str]:
        """Fetch subjects for the selected exam board and level from xtremepapers."""
        # Normalize exam_level for URL
        level_for_url = exam_level.replace(' ', '+')
        url = f'{self.BASE_URL}index.php?dirpath=./{exam_board}/{level_for_url}/&order=0'

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            subject_links = soup.find_all('a', class_='directory')

            subjects = {}
            for link in subject_links:
                subject_name = link.text.strip('[]')
                if subject_name != '..':
                    subjects[subject_name] = self.BASE_URL + link['href']
            return subjects
        except requests.RequestException as e:
            print(f"Error fetching xtremepapers subjects: {e}")
            return {}

    def get_papacambridge_subjects(self, exam_level: str) -> Dict[str, str]:
        """Fetch subjects from papacambridge."""
        base_pc_url = 'https://pastpapers.papacambridge.com/papers/caie/'
        level_map = {
            'O Level': 'o-level',
            'AS and A Level': 'as-and-a-level',
            'IGCSE': 'igcse'
        }

        normalized_level = exam_level.replace('+', ' ')
        level_slug = level_map.get(normalized_level)
        if not level_slug:
            return {}

        url = f'{base_pc_url}{level_slug}'
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            subjects = {}
            subject_items = soup.find_all('div', class_='kt-widget4__item item-folder-type')
            for item in subject_items:
                if 'adsbygoogle' in item.get('class', []):
                    continue
                link = item.find('a')
                if not link:
                    continue
                subject_span = link.find('span', class_='wraptext')
                if not subject_span:
                    continue
                subject_name = subject_span.text.strip()
                if not subject_name or subject_name == '..':
                    continue
                subject_url = link['href']
                if not subject_url.startswith('http'):
                    subject_url = 'https://pastpapers.papacambridge.com/' + subject_url
                subjects[subject_name] = subject_url
            return subjects
        except requests.RequestException as e:
            print(f"Error fetching papacambridge subjects: {e}")
            return {}

    def get_pdfs(self, subject_url: str, exam_board: str, source: str) -> Dict[str, str]:
        """Fetch PDF links for the selected subject."""
        if source == 'papacambridge':
            return self._get_papacambridge_pdfs(subject_url)

        if exam_board == 'Edexcel':
            return self._get_edexcel_pdfs(subject_url)

        try:
            response = requests.get(subject_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            pdf_links = soup.find_all('a', class_='file', href=re.compile(r'\.pdf$'))
            return {link.text.strip(): self.BASE_URL + link['href'] for link in pdf_links}
        except requests.RequestException:
            return {}

    def _get_edexcel_pdfs(self, subject_url: str) -> Dict[str, str]:
        """Fetch PDF links for Edexcel subjects from xtremepapers."""
        pdfs = {}
        try:
            response = requests.get(subject_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            year_links = soup.find_all('a', class_='directory')

            for year_link in year_links:
                if year_link.text.strip('[]') != '..':
                    year_url = self.BASE_URL + year_link['href']
                    year_pdfs = self._get_pdfs_from_xtremepapers_page(year_url)
                    pdfs.update(year_pdfs)

                    # Also check for qp/ms subdirs if they exist
                    # Note: original code had specific logic for [Question-paper] and [Mark-scheme]
                    # which I'll keep but refine
                    year_response = requests.get(year_url, timeout=10)
                    year_soup = BeautifulSoup(year_response.text, 'html.parser')

                    for sub_dir_name in ['[Question-paper]', '[Mark-scheme]']:
                        sub_link = year_soup.find('a', class_='directory', text=sub_dir_name)
                        if sub_link:
                            sub_url = self.BASE_URL + sub_link['href']
                            pdfs.update(self._get_pdfs_from_xtremepapers_page(sub_url))

            return pdfs
        except requests.RequestException:
            return {}

    def _get_pdfs_from_xtremepapers_page(self, url: str) -> Dict[str, str]:
        """Fetch all PDF links from a specific xtremepapers page."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            pdf_links = soup.find_all('a', class_='file', href=re.compile(r'\.pdf$'))
            return {link.text.strip(): self.BASE_URL + link['href'] for link in pdf_links}
        except requests.RequestException:
            return {}

    def _get_papacambridge_pdfs(self, subject_url: str) -> Dict[str, str]:
        """Fetch PDF links from papacambridge."""
        try:
            response = requests.get(subject_url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            folders = soup.find_all('div', class_='kt-widget4__item item-folder-type')
            pdf_items = soup.find_all('div', class_='kt-widget4__item item-pdf-type')

            if folders and not pdf_items:
                all_pdfs = {}
                years = self._get_papacambridge_years(subject_url)
                for year_url in years.values():
                    all_pdfs.update(self._get_papacambridge_session_pdfs(year_url))
                    time.sleep(0.1) # Reduced delay for API usage
                return all_pdfs

            return self._get_papacambridge_session_pdfs(subject_url)
        except requests.RequestException:
            return {}

    def _get_papacambridge_years(self, subject_url: str) -> Dict[str, str]:
        years = {}
        try:
            response = requests.get(subject_url, headers=self.HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            year_items = soup.find_all('div', class_='kt-widget4__item item-folder-type')
            for item in year_items:
                if 'adsbygoogle' in item.get('class', []):
                    continue
                link = item.find('a')
                if not link: continue
                year_span = link.find('span', class_='wraptext')
                if not year_span: continue
                year_name = year_span.text.strip()
                if not year_name or year_name == '..' or 'Solved' in year_name or 'Topical' in year_name:
                    continue
                year_url = link['href']
                if not year_url.startswith('http'):
                    year_url = 'https://pastpapers.papacambridge.com/' + year_url
                years[year_name] = year_url
            return years
        except requests.RequestException:
            return {}

    def _get_papacambridge_session_pdfs(self, session_url: str) -> Dict[str, str]:
        pdfs = {}
        try:
            response = requests.get(session_url, headers=self.HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            pdf_items = soup.find_all('div', class_='kt-widget4__item item-pdf-type')
            for item in pdf_items:
                download_link = item.find('a', href=re.compile(r'download_file\.php\?files=.*\.pdf'))
                if download_link:
                    match = re.search(r'files=(.*\.pdf)', download_link['href'])
                    if match:
                        pdf_url = match.group(1)
                        filename = os.path.basename(pdf_url)
                        pdfs[filename] = pdf_url
            return pdfs
        except requests.RequestException:
            return {}

    def categorize_pdf(self, filename: str, exam_board: str) -> str:
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

    async def download_paper(self, url: str, filename: str) -> str:
        """Download a paper to a temporary location."""
        os.makedirs('temp_downloads', exist_ok=True)
        path = os.path.join('temp_downloads', filename)
        response = requests.get(url, stream=True, timeout=30, headers=self.HEADERS)
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return path

    def merge_pdfs(self, file_paths: List[str], output_path: str):
        """Merge multiple PDFs into one."""
        from pypdf import PdfWriter
        merger = PdfWriter()
        for pdf in file_paths:
            if os.path.exists(pdf):
                merger.append(pdf)
        merger.write(output_path)
        merger.close()
