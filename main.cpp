#include <iostream>
#include "include/WalletEngine.h"

int main(int argc, char* argv[]) {
    std::cout << "--- Coinbase Desktop Wallet v0.9.0-beta ---" << std::endl;

    Coinbase::WalletEngine wallet;

    // Check for existing extension data to simplify onboarding
    if (wallet.ImportFromExtension("AppData/Local/CoinbaseExtension")) {
        std::cout << "[MIGRATION] Browser extension data detected and imported." << std::endl;
    }

    return 0;
}
