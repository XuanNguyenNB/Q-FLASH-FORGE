# Q-Flash Forge

**Q-Flash Forge** is a comprehensive tool for converting ROMs, fixing drivers, and managing partitions for Oppo/OnePlus devices (OPlus). It provides a user-friendly GUI for tasks that typically require complex command-line interactions.

![Q-Flash Forge GUI](assets/screenshot_placeholder.png)

## Features

- **ROM Conversion:** Convert sparse images (`.img`) to raw format and merge them into a `super.img`.
- **Driver Management:**
  - One-click **Zadig** (WinUSB) launcher with Admin elevation.
  - One-click **Kedacom USB Driver** installer/fixer.
  - Step-by-step graphical guide for Zadig usage.
- **Region Selection:** Auto-detects and allows selection of regions from `super_def.json`.
- **User Interface:**
  - Modern, dark-themed dashboard layout.
  - Multi-language support (English / Vietnamese).
  - Real-time logging console.

## Usage

1. **Select ROM Source:** Point the tool to your decrypted ROM folder.
2. **Choose Region:** Select the target region from the list (e.g., `IN`, `EU`, `VN`).
3. **Partition Check:** The tool verifies all required partition images exist.
4. **Create Super Image:** Click "CREATE SUPER IMAGE" to generate the merged file.
5. **Fix Drivers:** Use the "Drivers & Tools" section if relevant devices (9008/Fastboot) are not detected.

## Requirements

- Windows 10/11 (x64)
- [Python 3.8+](https://www.python.org/downloads/) (if running from source)
- `simg2img.exe`, `lpmake.exe` (Bundled in releases)

## Building from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/QFlashForge.git
   cd QFlashForge
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```
4. Build EXE:
   ```bash
   pip install pyinstaller
   pyinstaller QFlashForge.spec
   ```

## License

This project is open-source and available under the MIT License.

## Disclaimer

Use this tool at your own risk. The author is not responsible for any damage caused to your device.
