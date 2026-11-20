# Pixel vendor compatibility / ColorOS 17

Maintain the current **coral hardware** as the source of truth:

- **GCam:** Google camera provider, Hexagon/Airbrush and supporting runtime libraries are paired to the Pixel camera stack. The existing Floral GCam plugin packages the application; this vendor tree provides the HAL.
- **3D Face Unlock:** Google IR Face HAL, Citadel Keymaster, calibration/secure hardware and persist data must remain intact. The ColorOS framework's biometric service may need new integration; a file-presence audit cannot establish operation.
- **Motion Sense:** CHRE/Oslo firmware, sensor HAL and factory calibration are Pixel-specific. SystemUI/Settings integration must be adapted to actual ColorOS component interfaces.
- **Telephony:** Retain Google's/qcom radio stack and test IMS with active Pakistan operators after the boot chain is stable. The OnePlus 7 Pro IMS shim is not a drop-in patch for coral.
- **Encryption:** Pixel file-based encryption must be preserved. A first-boot issue is not a reason to erase secure state without explicit diagnostics.

Do not place Google/OPPO/Qualcomm proprietary images in this GitHub repository. Donor archives are read from local build inputs only.
