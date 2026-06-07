"""
Service for scraping exam papers from xtremepapers, papacambridge, and pastpapers.co.
Updated to use asynchronous requests with politeness techniques.
"""
import os
import json
import re
import asyncio
import random
import hashlib
from typing import Dict, List
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup
from pypdf import PdfWriter

class ExamScraperService:
    """Service to handle scraping operations for different exam boards and sources."""

    BASE_URL = 'https://papers.xtremepape.rs/'

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0'
    ]

    def __init__(self):
        # Limit concurrency to 5 requests at a time
        self.semaphore = asyncio.Semaphore(5)
        self._rand = random.SystemRandom()

    def _get_headers(self, url: str, referer: str = None) -> Dict[str, str]:
        """Return realistic headers to avoid bot detection."""
        parsed_url = urlparse(url)
        host = parsed_url.netloc

        if not referer:
            referer = 'https://www.google.com/'

        parsed_ref = urlparse(referer)

        # Determine Sec-Fetch-Site (same-origin, same-site, cross-site, none)
        host_parts = host.split('.')
        ref_parts = parsed_ref.netloc.split('.')

        base_domain = '.'.join(host_parts[-2:]) if len(host_parts) >= 2 else host
        ref_domain = '.'.join(ref_parts[-2:]) if len(ref_parts) >= 2 else parsed_ref.netloc

        if host == parsed_ref.netloc:
            fetch_site = 'same-origin'
        elif base_domain == ref_domain:
            fetch_site = 'same-site'
        elif not parsed_ref.netloc:
            fetch_site = 'none'
        else:
            fetch_site = 'cross-site'

        headers = {
            'User-Agent': self._rand.choice(self.USER_AGENTS),
            'Accept': (
                'text/html,application/xhtml+xml,application/xml;q=0.9,'
                'image/avif,image/webp,image/apng,*/*;q=0.8,'
                'application/signed-exchange;v=b3;q=0.7'
            ),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': referer,
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': fetch_site,
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        }

        # Add Sec-Ch-Ua headers for Chrome
        ua = headers['User-Agent']
        if 'Chrome' in ua:
            headers.update({
                'sec-ch-ua': '"Chromium";v="125", "Not.A/Brand";v="24", "Google Chrome";v="125"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': (
                    '"Windows"' if 'Windows' in ua else
                    '"macOS"' if 'Macintosh' in ua else '"Linux"'
                )
            })

        return headers

    def _get_safe_url(self, url: str) -> str:
        """Strictly validate and reconstruct the URL from trusted constants."""
        # Use a more flexible check for papacambridge to handle varied subdomains or paths
        trusted_map = {
            'papers.xtremepape.rs': 'https://papers.xtremepape.rs/',
            'pastpapers.papacambridge.com': 'https://pastpapers.papacambridge.com/',
            'papacambridge.com': 'https://papacambridge.com/',
            'pastpapers.co': 'https://pastpapers.co/'
        }

        parsed = urlparse(url)
        if parsed.netloc in trusted_map:
            # Reconstruct to ensure we use https and clean path
            base = trusted_map[parsed.netloc]
            path = parsed.path.lstrip('/')
            query = f"?{parsed.query}" if parsed.query else ""
            return f"{base.rstrip('/')}/{path}{query}"
        return ""

    def _is_trusted_url(self, url: str) -> bool:
        """Verify if the URL belongs to a trusted scraping domain strictly."""
        return bool(self._get_safe_url(url))

    def get_safe_path(self, filename: str) -> str:
        """Ensure the path is strictly within the temp_downloads directory."""
        # Force basename to prevent any directory traversal strings
        clean_name = os.path.basename(filename)
        base_dir = os.path.abspath('temp_downloads')
        os.makedirs(base_dir, exist_ok=True)

        target_path = os.path.abspath(os.path.join(base_dir, clean_name))

        # Check if the target path is still within base_dir exactly
        if os.path.commonpath([base_dir, target_path]) != base_dir:
            raise RuntimeError(f"Path traversal detected: {filename}")

        return target_path

    async def _fetch_html(self, session: aiohttp.ClientSession, url: str,
                          referer: str = None) -> str:
        """Wrapper for aiohttp GET requests with semaphore and jitter."""
        safe_url = self._get_safe_url(url)
        if not safe_url:
            print(f"Untrusted URL blocked: {url}")
            return ""

        async with self.semaphore:
            # Random jitter between 0.5 and 2.0 seconds for better human-like behavior
            await asyncio.sleep(self._rand.uniform(0.5, 2.0))

            try:
                # Use the URL's parent or base domain as referer if not provided
                if not referer:
                    referer = urljoin(url, '.')

                timeout = aiohttp.ClientTimeout(total=20)
                async with session.get(safe_url, headers=self._get_headers(safe_url, referer),
                                     timeout=timeout) as response:
                    if response.status == 200:
                        return await response.text()
                    if response.status == 403:
                        print(f"Access Denied (403) for {url}. Might be Cloudflare challenge.")
                        # Try a fallback with no referer at all or different domain
                        if referer != 'https://www.google.com/':
                            await asyncio.sleep(1)
                            headers = self._get_headers(safe_url, 'https://www.google.com/')
                            async with session.get(safe_url, headers=headers,
                                                 timeout=timeout) as retry_res:
                                if retry_res.status == 200:
                                    return await retry_res.text()

                    print(f"Failed to fetch {url}: Status {response.status}")
                    return ""
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                print(f"Request error for {url}: {e}")
                return ""

    async def get_xtremepapers_subjects(self, session: aiohttp.ClientSession,
                                        exam_board: str,
                                        exam_level: str) -> Dict[str, str]:
        """Fetch subjects for the selected exam board and level from xtremepapers."""
        level_for_url = exam_level.replace(' ', '+')
        url = f'{self.BASE_URL}index.php?dirpath=./{exam_board}/{level_for_url}/&order=0'

        html = await self._fetch_html(session, url)
        if not html:
            return {}

        soup = BeautifulSoup(html, 'html.parser')
        subject_links = soup.find_all('a', class_='directory')

        subjects = {}
        for link in subject_links:
            subject_name = link.text.strip('[]')
            if subject_name != '..':
                subjects[subject_name] = urljoin(self.BASE_URL, link['href'])
        return subjects

    async def get_papacambridge_subjects(self, session: aiohttp.ClientSession,
                                         exam_level: str) -> Dict[str, str]:
        """Fetch subjects from papacambridge."""
        level_map = {
            'O Level': 'o-level',
            'AS and A Level': 'as-and-a-level',
            'IGCSE': 'igcse'
        }

        normalized_level = exam_level.replace('+', ' ')
        level_slug = level_map.get(normalized_level)
        if not level_slug:
            return {}

        url = (
            f'https://pastpapers.papacambridge.com/papers/caie/{level_slug}'
        )
        html = await self._fetch_html(session, url, 'https://papacambridge.com/past-papers/')
        if not html:
            return {}

        soup = BeautifulSoup(html, 'html.parser')
        return self._parse_pc_subjects(soup, url)

    def _parse_pc_subjects(self, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        """Helper to parse subjects from papacambridge soup."""
        subjects = {}
        items = soup.find_all('div', class_='kt-widget4__item item-folder-type')
        for item in items:
            if 'adsbygoogle' in item.get('class', []):
                continue
            link = item.find('a')
            if not link:
                continue
            span = link.find('span', class_='wraptext')
            if not span:
                continue
            name = span.text.strip()
            if not name or name == '..':
                continue

            url = urljoin(base_url, link['href'])
            subjects[name] = url
        return subjects

    async def get_pdfs(self, session: aiohttp.ClientSession, subject_url: str,
                       exam_board: str, source: str) -> Dict[str, str]:
        """Fetch PDF links for the selected subject."""
        if source == 'papacambridge':
            return await self._get_papacambridge_pdfs(session, subject_url)

        if source == 'pastpapers_co':
            return await self._get_pastpapers_co_pdfs(session, subject_url)

        if exam_board == 'Edexcel':
            return await self._get_edexcel_pdfs(session, subject_url)

        html = await self._fetch_html(session, subject_url)
        if not html:
            return {}

        soup = BeautifulSoup(html, 'html.parser')
        pdf_links = soup.find_all('a', class_='file', href=re.compile(r'\.pdf$'))
        return {
            link.text.strip(): urljoin(self.BASE_URL, link['href'])
            for link in pdf_links
        }

    async def _get_edexcel_pdfs(self, session: aiohttp.ClientSession,
                                subject_url: str) -> Dict[str, str]:
        """Fetch PDF links for Edexcel subjects from xtremepapers."""
        html = await self._fetch_html(session, subject_url)
        if not html:
            return {}

        soup = BeautifulSoup(html, 'html.parser')
        year_links = soup.find_all('a', class_='directory')

        tasks = []
        for year_link in year_links:
            if year_link.text.strip('[]') != '..':
                year_url = urljoin(self.BASE_URL, year_link['href'])
                tasks.append(
                    self._get_edexcel_year_details(session, year_url)
                )

        results = await asyncio.gather(*tasks)

        all_pdfs = {}
        for r in results:
            all_pdfs.update(r)
        return all_pdfs

    async def _get_edexcel_year_details(self, session: aiohttp.ClientSession,
                                        year_url: str) -> Dict[str, str]:
        """Helper to fetch PDFs from an Edexcel year and its subdirectories."""
        pdfs = await self._get_pdfs_from_xtremepapers_page(session, year_url)

        # Check for qp/ms subdirs
        html = await self._fetch_html(session, year_url)
        if not html:
            return pdfs

        soup = BeautifulSoup(html, 'html.parser')
        sub_tasks = []
        for sub_dir_name in ['[Question-paper]', '[Mark-scheme]']:
            sub_link = soup.find('a', class_='directory', string=sub_dir_name)
            if sub_link:
                sub_url = urljoin(self.BASE_URL, sub_link['href'])
                sub_tasks.append(
                    self._get_pdfs_from_xtremepapers_page(session, sub_url)
                )

        if sub_tasks:
            sub_results = await asyncio.gather(*sub_tasks)
            for sr in sub_results:
                pdfs.update(sr)

        return pdfs

    async def _get_pdfs_from_xtremepapers_page(self, session: aiohttp.ClientSession,
                                               url: str) -> Dict[str, str]:
        """Fetch all PDF links from a specific xtremepapers page."""
        html = await self._fetch_html(session, url)
        if not html:
            return {}

        soup = BeautifulSoup(html, 'html.parser')
        pdf_links = soup.find_all('a', class_='file', href=re.compile(r'\.pdf$'))
        return {
            link.text.strip(): urljoin(self.BASE_URL, link['href'])
            for link in pdf_links
        }

    async def _get_papacambridge_pdfs(self, session: aiohttp.ClientSession,
                                      subject_url: str) -> Dict[str, str]:
        """Fetch PDF links from papacambridge."""
        html = await self._fetch_html(session, subject_url)
        if not html:
            return {}

        soup = BeautifulSoup(html, 'html.parser')
        folders = soup.find_all('div', class_='kt-widget4__item item-folder-type')
        pdf_items = soup.find_all('div', class_='kt-widget4__item item-pdf-type')

        if folders and not pdf_items:
            # Parallel fetch years
            years = self._get_papacambridge_years_internal(soup, subject_url)
            tasks = [
                self._get_papacambridge_session_pdfs(session, y_url)
                for y_url in years.values()
            ]
            results = await asyncio.gather(*tasks)

            all_pdfs = {}
            for res in results:
                all_pdfs.update(res)
            return all_pdfs

        return await self._get_papacambridge_session_pdfs(session, subject_url)

    def _get_papacambridge_years_internal(self, soup: BeautifulSoup,
                                          base_url: str) -> Dict[str, str]:
        """Internal helper to parse year links from local soup."""
        years = {}
        year_items = soup.find_all('div',
                                   class_='kt-widget4__item item-folder-type')
        for item in year_items:
            if 'adsbygoogle' in item.get('class', []):
                continue
            link = item.find('a')
            if not link:
                continue
            year_span = link.find('span', class_='wraptext')
            if not year_span:
                continue
            name = year_span.text.strip()
            is_invalid = not name or name == '..'
            is_special = 'Solved' in name or 'Topical' in name
            if is_invalid or is_special:
                continue

            year_url = urljoin(base_url, link['href'])
            years[name] = year_url
        return years

    async def _get_papacambridge_session_pdfs(self, session: aiohttp.ClientSession,
                                              session_url: str) -> Dict[str, str]:
        """Fetch PDF links from a Papacambridge session page."""
        html = await self._fetch_html(session, session_url)
        if not html:
            return {}

        soup = BeautifulSoup(html, 'html.parser')
        pdfs = {}
        pdf_items = soup.find_all('div', class_='kt-widget4__item item-pdf-type')
        for item in pdf_items:
            # Try finding download_file.php link first
            dl_pattern = r'download_file\.php\?files=.*\.pdf'
            download_link = item.find('a', href=re.compile(dl_pattern))

            pdf_url = ""
            if download_link:
                match = re.search(r'files=(.*\.pdf)', download_link['href'])
                if match:
                    pdf_url = match.group(1)
            else:
                # Look for direct PDF links
                direct_link = item.find('a', href=re.compile(r'\.pdf$'))
                if direct_link:
                    pdf_url = direct_link['href']

            if pdf_url:
                pdf_url = urljoin(session_url, pdf_url)
                filename = os.path.basename(pdf_url)
                pdfs[filename] = pdf_url
        return pdfs


    def categorize_pdf(self, filename: str, exam_board: str) -> str:
        """Categorize the PDF with specific paper numbers."""
        filename_lower = filename.lower()
        result = 'misc'

        if exam_board == 'CAIE':
            num_match = re.search(r'_(?:qp|ms)_(\d)', filename_lower)
            paper_num = num_match.group(1) if num_match else ""

            if '_ms_' in filename_lower or 'mark_scheme' in filename_lower:
                result = f'ms_{paper_num}' if paper_num else 'ms'
            elif '_qp_' in filename_lower or 'question_paper' in filename_lower:
                result = f'qp_{paper_num}' if paper_num else 'qp'

        elif exam_board == 'Edexcel':
            if re.search(r'Paper[ ]?1[PpRr]?', filename, re.IGNORECASE):
                result = 'qp_1'
            elif re.search(r'Paper[ ]?2[PpRr]?', filename, re.IGNORECASE):
                result = 'qp_2'
            elif 'question' in filename_lower:
                result = 'qp'
            elif 'mark' in filename_lower or 'ms' in filename_lower:
                result = 'ms'

        return result

    async def download_paper(self, session: aiohttp.ClientSession, url: str, filename: str) -> str:
        """Download a paper securely using a hash for the local path."""
        safe_url = self._get_safe_url(url)
        if not safe_url:
            raise RuntimeError(f"Untrusted URL blocked: {url}")

        # Opaque filename from URL hash to break path injection data flow
        url_hash = hashlib.sha256(safe_url.encode()).hexdigest()
        path = self.get_safe_path(f"{url_hash}.pdf")

        async with self.semaphore:
            timeout = aiohttp.ClientTimeout(total=60)
            async with session.get(safe_url, headers=self._get_headers(safe_url),
                                 timeout=timeout) as response:
                if response.status == 200:
                    with open(path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    return path

                raise RuntimeError(f"Failed to download {filename}: Status {response.status}")

    def merge_pdfs(self, file_paths: List[str], output_path: str):
        """Merge multiple PDFs into one securely."""
        # Ensure output path is safe
        safe_output_path = self.get_safe_path(os.path.basename(output_path))
        merger = PdfWriter()

        base_dir = os.path.abspath('temp_downloads')
        for pdf in file_paths:
            # Strong sanitization for CodeQL: only use basename
            safe_pdf_path = os.path.join(base_dir, os.path.basename(pdf))
            if os.path.exists(safe_pdf_path):
                merger.append(safe_pdf_path)

        with open(safe_output_path, 'wb') as f:
            merger.write(f)
        merger.close()

    async def get_pastpapers_co_subjects(self, session: aiohttp.ClientSession,
                                         exam_level: str) -> Dict[str, str]:
        """Fetch subjects from pastpapers.co."""
        level_map = {
            'O Level': 'o-level',
            'A Level': 'a-level',
            'IGCSE': 'igcse'
        }
        level_slug = level_map.get(exam_level, 'igcse')
        url = f'https://pastpapers.co/caie/{level_slug}'

        html = await self._fetch_html(session, url)
        if not html:
            return {}

        entries = self._extract_nextjs_data(html)
        subjects = {}
        for entry in entries:
            if entry.get('isDir'):
                name = entry.get('name')
                rel_path = entry.get('relPath')
                subjects[name] = f'https://pastpapers.co/caie/{rel_path}'
        return subjects

    async def _get_pastpapers_co_pdfs(self, session: aiohttp.ClientSession,
                                     subject_url: str) -> Dict[str, str]:
        """Recursively fetch PDF links from pastpapers.co folders."""
        html = await self._fetch_html(session, subject_url)
        if not html:
            return {}

        entries = self._extract_nextjs_data(html)
        pdfs = {}
        tasks = []

        for entry in entries:
            name = entry.get('name')
            rel_path = entry.get('relPath')
            if entry.get('isDir'):
                sub_url = f'https://pastpapers.co/caie/{rel_path}'
                tasks.append(self._get_pastpapers_co_pdfs(session, sub_url))
            elif name.lower().endswith('.pdf'):
                pdfs[name] = f'https://pastpapers.co/caie/{rel_path}'

        if tasks:
            results = await asyncio.gather(*tasks)
            for res in results:
                pdfs.update(res)

        return pdfs

    def _parse_entries_from_payload(self, clean_p: str) -> List[dict]:
        """Helper to extract entries array from a single clean payload string."""
        idx = clean_p.find('"entries":[')
        if idx == -1:
            return []
        start = idx + 10  # Index of the first '['

        # Simple state machine to find matching closing bracket while skipping string literals
        in_string = False
        escaped = False
        bracket_count = 0

        for i in range(start, len(clean_p)):
            char = clean_p[i]

            if escaped:
                escaped = False
                continue

            if char == '\\':
                escaped = True
                continue

            if char == '"':
                in_string = not in_string
                continue

            if not in_string:
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        json_str = clean_p[start : i + 1]
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            return []
        return []

    def _extract_nextjs_data(self, html: str) -> List[dict]:
        """Extract the entries array from Next.js self.__next_f.push payloads."""
        entries = []
        patterns = re.findall(
            r"self\.__next_f\.push\(\s*\[\s*\d+\s*,\s*(['\"])(.*?)\1\s*\]\s*\)",
            html,
            re.DOTALL,
        )
        for _, p in patterns:
            # Next.js escapes: \" -> " and \\ -> \
            clean_p = p.replace('\\"', '"').replace('\\\\', '\\').replace('\\n', '')

            if '"entries":[' in clean_p:
                try:
                    entries.extend(self._parse_entries_from_payload(clean_p))
                except (json.JSONDecodeError, ValueError):
                    continue
        return entries
