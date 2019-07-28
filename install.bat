REG ADD "HKEY_CURRENT_USER\SOFTWARE\Google\Chrome\NativeMessagingHosts\maoxian_web_clipper_native" /ve /t REG_SZ /d "%~dp0chrome_manifest.json" /f
REG ADD "HKEY_CURRENT_USER\SOFTWARE\Mozilla\NativeMessagingHosts\maoxian_web_clipper_native" /ve /t REG_SZ /d "%~dp0firefox_manifest.json" /f
