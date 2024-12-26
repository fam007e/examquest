#!/bin/bash

# Function to install poppler-utils based on the Linux distribution
install_poppler() {
    echo "Attempting to install poppler-utils..."
    if [ -f /etc/os-release ]; then
        source /etc/os-release
        case $ID in
            ubuntu|debian)
                sudo apt update && sudo apt install -y poppler-utils
                ;;
            fedora)
                sudo dnf install -y poppler-utils
                ;;
            arch|manjaro)
                sudo pacman -Syu poppler
                ;;
            opensuse|suse)
                sudo zypper install -y poppler-tools
                ;;
            *)
                echo "Unsupported Linux distribution. Please install poppler-utils manually."
                exit 1
                ;;
        esac
    else
        echo "Could not detect Linux distribution. Please install poppler-utils manually."
        exit 1
    fi
}

# Ensure pdfunite is installed
if ! command -v pdfunite &> /dev/null; then
    echo "Error: pdfunite is not installed."
    install_poppler
    if ! command -v pdfunite &> /dev/null; then
        echo "Installation failed or pdfunite is still unavailable. Exiting."
        exit 1
    fi
fi

# Directory containing the PDF files
PDF_DIR="./"  # Change this if your PDFs are in another directory
MERGED_DIR="./merged"  # Directory to save merged PDFs

# Create output directory if it doesn't exist
mkdir -p "$MERGED_DIR"

# Merge papers by type (e.g., qp_1X)
for PAPER_TYPE in 1 2 3 4; do  # Add more paper types as needed
    # Find all PDFs matching the pattern *_qp_${PAPER_TYPE}*.pdf
    PAPER_FILES=$(find "$PDF_DIR" -type f -name "*_qp_${PAPER_TYPE}*.pdf" | sort)

    if [ -n "$PAPER_FILES" ]; then
        OUTPUT_FILE="${MERGED_DIR}/merged_paper_${PAPER_TYPE}.pdf"
        echo "Merging Paper $PAPER_TYPE into $OUTPUT_FILE..."

        # Use pdfunite to merge files
        pdfunite $PAPER_FILES "$OUTPUT_FILE"

        # Check if merge succeeded
        if [ $? -eq 0 ]; then
            echo "Successfully merged Paper $PAPER_TYPE into $OUTPUT_FILE."
        else
            echo "Failed to merge Paper $PAPER_TYPE. Please check your files."
        fi
    else
        echo "No files found for Paper $PAPER_TYPE."
    fi
done

echo "All merging completed. Merged files are in the $MERGED_DIR directory."
