# Switch to Media Tab

This is a Zen browser extension that allows you to quickly switch to the tab that is currently playing audio. 

## Features

*   **Switch to Media Tab:** Automatically focuses the tab that is playing audio.
*   **Command-Line Control:** Use your terminal to switch to the media tab, list all tabs playing media, or switch to a specific tab by its ID.
*   **Toggle:** Switch back and forth between your current tab and the tab playing media.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/zen-media-toggle.git
    cd zen-media-toggle
    ```

2.  **Run the installation script:**
    ```bash
    ./install.sh
    ```
    The script will prompt you for your extension's ID. You can find this by going to `about:debugging` in Zen, clicking on "This Zen", and finding the "Switch to Media Tab" extension. The ID is the "Internal UUID".

3.  **Load the extension in Zen:**
    *   Open Zen and navigate to `about:debugging`.
    *   Click on "This Zen".
    *   Click on "Load Temporary Add-on...".
    *   Select the `manifest.json` file from the project directory.

## Usage

You can use the extension in two ways:

### 1. Browser Icon

Click on the extension's icon in the Zen toolbar to switch to the tab that is playing media.

### 2. Command Line

Use the `controller.py` script to control the extension from your terminal.

*   **Switch to the media tab:**
    ```bash
    ./controller.py switch
    ```

*   **Toggle between the current tab and the media tab:**
    ```bash
    ./controller.py toggle
    ```

*   **List all tabs playing media:**
    ```bash
    ./controller.py list
    ```
    This will output a list of tabs with their IDs and titles.

*   **Switch to a specific tab by its ID:**
    ```bash
    ./controller.py goto <tab_id>
    ```
    Replace `<tab_id>` with the ID of the tab you want to switch to.
