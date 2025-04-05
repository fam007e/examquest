# O and A Levels Exam Papers Downloader

This Python script allows users to download past papers for Cambridge (CAIE) and Edexcel examinations from multiple sources.

## Features

- Download past papers from multiple sources:
  - Xtremepapers (CAIE and Edexcel)
  - Papacambridge (CAIE)
- Choose between different examination levels:
  - CAIE: IGCSE, O Level, and AS/A Level
  - Edexcel: International GCSE and Advanced Level
- View available subjects for the chosen examination level
- Select multiple subjects for download
- Automatically categorizes papers by type (question papers, mark schemes, etc.)
- Smart retry mechanism for failed downloads
- User-friendly interface with columnar display of subjects

## Requirements

- Python 3.6 or higher
- Required libraries:
  ```
  requests
  beautifulsoup4
  ```

## Installation

There are multiple ways to install and use this tool:

### Method 1: Quick download and run

1. Ensure you have Python 3.6+ installed on your system.

2. Install the required libraries:

```bash
pip install requests beautifulsoup4
```

3. Download the script using curl:

```bash
curl -fsSL https://raw.githubusercontent.com/fam007e/OandALvl-exam-paper-downloader/refs/heads/main/o_and_a_lv_qp_sdl.py -o o_and_a_lv_qp_sdl.py
```

### Method 2: Clone repository and use requirements.txt

1. Clone the repository:

```bash
git clone https://github.com/fam007e/OandALvl-exam-paper-downloader.git
cd OandALvl-exam-paper-downloader
```

2. Install dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

### Method 3: Install as a Python package

1. Clone the repository:

```bash
git clone https://github.com/fam007e/OandALvl-exam-paper-downloader.git
cd OandALvl-exam-paper-downloader
```

2. Install the package:

```bash
pip install .
```

This will make the tool available as a command-line utility called `exam-downloader`.

## Usage

If you installed using Method 1 or 2:

```bash
python o_and_a_lv_qp_sdl.py
```

If you installed using Method 3:

```bash
exam-downloader
```

Then follow the on-screen prompts:
   - Choose the examination board (CAIE from Xtremepapers, Edexcel from Xtremepapers, or CAIE from Papacambridge)
   - Choose the examination level (varies by board)
   - Select the subjects you want to download papers for
   - Wait for the download to complete

The script will:
   - Fetch available subjects from the selected source
   - Display subjects in a user-friendly columnar format
   - Download selected papers with appropriate timeouts
   - Create organized folder structure for downloaded papers
   - Show download progress and summary statistics

The downloaded papers will be organized in folders by:
   - Examination board (CAIE/Edexcel)
   - Examination level (O Level, AS/A Level, etc.)
   - Subject
   - Paper type (`ms` for mark schemes, `qp` for question papers, and `misc` for other types)

## Technical Details

- Implements proper error handling and request timeouts
- Uses streaming downloads for better performance with large files
- Includes appropriate delays between requests to be respectful to the server
- Handles differences in website structures between Xtremepapers and Papacambridge
- Automatically categorizes papers based on filename patterns

## Note

Please be respectful of the websites and avoid overloading their servers with too many requests in a short time. The script includes small delays between requests to minimize server impact.

## Merging Papers

After downloading the papers, you can run the `pdfmerger.sh` script to merge the papers by type using `poppler` utility package `pdfunite`:

```bash
bash pdfmerger.sh
```

The script will:

- Find and merge the papers (question papers, mark schemes, etc.) for each paper type (e.g., `qp_1`, `qp_2`, etc.) into single PDFs.
- Save the merged PDFs in the `merged` directory.

## License

This project is open source and available under the [LICENSE](LICENSE).

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/fam007e/OandALvl-exam-paper-downloader/issues) if you want to contribute.