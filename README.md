# Coinbase-Wallet-Desktop
Coinbase Desktop Wallet Alpha version
<img width="1536" height="1024" alt="f112455a-37df-4f4b-9468-113e35c6a457" src="https://github.com/user-attachments/assets/7e599b37-15e1-478d-9d66-c4084a955c2d" />

**The Professional-Grade Desktop Interface for Sovereign Asset Management.** 🔑

---

## 📖 Project Vision

Coinbase Desktop is a high-performance, native Windows application built in C++ to provide users with a secure, localized environment for managing digital assets. By moving beyond the browser, we offer enhanced security features, deeper hardware integration, and a dedicated workspace for the modern crypto ecosystem.

> **Current Status**: Public Alpha. This software is undergoing active development and community auditing.

---

## ✨ Comprehensive Feature Set

### 🛠️ Native Performance & Security
- **C++ Core Engine**: Engineered for low-latency and high-efficiency on Windows 10/11.
- **TPM Integration**: Leverages the Windows Trusted Platform Module (TPM) for hardware-level key protection.
- **Encrypted Local Vault**: Industry-standard AES-256 encryption for all locally stored metadata.

### 🔌 Hardware Wallet Ecosystem
- **Native Ledger Support**: Seamless HID communication with Ledger Nano S, X, and Stax.
- **Trezor Integration**: Full compatibility with Trezor One and Model T via Bridge or WebUSB.
- **Cold Storage Interaction**: Sign transactions offline while maintaining an intuitive desktop interface.

### 🔄 Ecosystem Synergy
- **Extension Bridge**: One-click migration tool to import keys, contacts, and settings from the Coinbase Wallet browser extension.
- **Direct Exchange Link**: Securely connect to your Coinbase Exchange account to view balances and initiate instant top-ups.
- **Universal Asset Support**: Manage thousands of tokens across multiple EVM-compatible chains and Layer 2s.

### 🍎 macOS Support (Node.js Environment)
- **Fast Deployment**: Install via `npm` or `yarn` for a seamless macOS experience.
- **Apple Silicon Optimized**: Native performance for M1/M2/M3 chips via Node.js runtime.
- **Keychain Integration**: Securely stores encrypted metadata using macOS Keychain.
---

## 💻 Technical Architecture & Requirements

### System Specifications
| **Operating System** | Windows 10 (Build 19041+) | Windows 11 | M
| **Processor** | Dual-core x64-based processor | Quad-core or higher |
| **Memory** | 4GB RAM | 8GB+ RAM |
| **Storage** | 200MB available space | SSD with 1GB+ for indexing |

### Build Dependencies
- **Compiler**: MSVC (Visual Studio 2022) with C++17 support or higher.
- **Build System**: CMake 3.22+.
- **Libraries**: OpenSSL 3.x, Boost 1.81, Qt 6.x (for GUI components).

---

## 📥 Deployment & Installation

### For End-Users
1. **Download**: Navigate to the [Releases](#) tab and download the latest `.msi` installer.
2. **Verification**: Verify the GPG signature of the installer to ensure binary integrity.
3. **Setup**: Follow the secure onboarding wizard to create a new vault or import an existing one.

### For Developers (Build from Source)
```powershell
# Clone the repository and its secure submodules
git clone --recursive [https://github.com/Kirubel125/Coinbase-Wallet-Desktop](https://github.com/Kirubel125/Coinbase-Wallet-Desktop)

# Enter project directory
cd desktop-wallet-cpp

# Configure and build
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --config Release
### 🍏 For macOS (via Node.js)
The macOS version utilizes our secure Node.js bridge to interact with the wallet core.

1. **Ensure Node.js is installed** (v18.x or higher recommended).
2. **Install the wallet package**:
   ```bash
npm install coinbase-desktop-sdk
npx coinbase-desktop-sdk
