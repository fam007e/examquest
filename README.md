# O and A Levels Xtremepapers Downloader

This Python script allows users to download past papers for O Level and AS/A Level examinations from the Xtremepapers website.

## Features

- Choose between O Level and AS/A Level examinations
- View available subjects for the chosen examination level
- Select multiple subjects for download
- Automatically organizes downloaded papers into subject and paper type folders

## Requirements

- Python 3.6 or higher
- `requests` library
- `beautifulsoup4` library

## Installation

1. Ensure you have Python 3.6+ installed on your system.

2. Install the required libraries:

```bash
pip install requests beautifulsoup4
```

3. Download the script using curl:

```bash
curl -fsSL https://raw.githubusercontent.com/fam007e/OandALvl-exam-paper-downloader/refs/heads/main/o_and_a_lv_qp_sdl.py -o o_and_a_lv_qp_sdl.py
```

## Usage

1. Run the script:

```bash
python o_and_a_lv_qp_sdl.py
```

2. Follow the on-screen prompts:
   - Choose the examination level (O Level or AS/A Level)
   - Select the subjects you want to download papers for
   - Wait for the download to complete

3. The downloaded papers will be organized in folders by examination level, subject, and paper type (`ms` for mark schemes, `qp` for question papers, and `misc` for other types).

## Note

Please be respectful of the Xtremepapers website and avoid overloading their servers with too many requests in a short time.

## Merging Papers

After downloading the papers, you can run the `pdfmerger.sh` script to merge the papers by type using `poppler` utility package `pdfunite`:

```bash
bash pdfmerger.sh
```

The script will:

- Find and merge the papers (question papers, mark schemes, etc.) for each paper type (e.g., `qp_1`, `qp_2`, etc.) into single PDFs.
- Save the merged PDFs in the `merged` directory.
- Organize the downloaded papers into folders by examination level, subject, and paper type (`ms` for mark schemes, `qp` for question papers, and `misc` for other types).

## License

This project is open source and available under the [LICENSE](LICENSE).

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/fam007e/OandALvl-exam-paper-downloader/issues) if you want to contribute.

