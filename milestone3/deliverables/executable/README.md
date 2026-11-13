# Milestone III Application Executable Deliverable

Per the official Milestone III requirements:
> *"Deliverables: 1. Application implementation / source code + executable"*

The application includes cross-platform one-click executable launchers:

### 1. Windows Executable Launcher
* **File:** [`milestone3/run.bat`](../../run.bat)
* **Execution:** Double-click or run from command prompt:
  ```cmd
  milestone3\run.bat
  ```
* **Features:**
  * Checks for remote MySQL `.env` configuration.
  * Manages an isolated Python virtual environment.
  * Automatically installs dependencies from `requirements.txt`.
  * Enforces the remote host verification guard (`verify_remote_host`).
  * Launches the default web browser directly to the dashboard.

### 2. Linux / macOS Executable Launcher
* **File:** [`milestone3/run.sh`](../../run.sh)
* **Execution:**
  ```bash
  chmod +x milestone3/run.sh
  ./milestone3/run.sh
  ```

### 3. CLI Direct Execution
For developers and evaluation scripts:
```bash
python -m milestone3.app.main
```
*(Append `--allow-local` only for offline local testing without internet access).*
