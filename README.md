# Q-Flash Forge

**Q-Flash Forge** is a comprehensive tool developed for converting ROMs, fixing drivers, and managing partitions for **Oppo, OnePlus, and Realme** devices (supporting both Factory/Domestic and Export ROMs). It provides a user-friendly GUI for tasks that typically require complex command-line interactions.

## Features

- **ROM Conversion:** Convert sparse images (`.img`) to raw format and merge them into a `super.img`.
- **Archive Support:** **[NEW]** Native `.ZIP` ROM extraction. Directly select a ZIP file, and the tool will extract and verify it automatically.
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

1. **Select ROM Source:**
   - Click **"Browse Folder"** for an extracted ROM folder.
   - Or click **"Extract .ZIP"** to select a ROM archive.
2. **Choose Region:** Select the target region from the list (e.g., `IN`, `EU`, `VN`).
3. **Partition Check:** The tool verifies all required partition images exist.
4. **Create Super Image:** Click "CREATE SUPER IMAGE" to generate the merged file.
5. **Fix Drivers:** Use the "Drivers & Tools" section if relevant devices (9008/Fastboot) are not detected.

## Requirements

- Windows 10/11 (x64)
- [Python 3.8+](https://www.python.org/downloads/) (if running from source)
- `simg2img.exe`, `lpmake.exe` (Bundled in releases)

## Contact & Support

- **Developer:** Xuan Nguyen
- **Facebook:** [https://www.facebook.com/xuannguyen030923](https://www.facebook.com/xuannguyen030923)
- **Telegram:** [https://t.me/mitomtreem](https://t.me/mitomtreem)

## License

This project is open-source and available under the MIT License.

## Disclaimer

Use this tool at your own risk. The author is not responsible for any damage caused to your device.
