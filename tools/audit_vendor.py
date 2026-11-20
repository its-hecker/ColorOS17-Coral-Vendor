#!/usr/bin/env python3
"""Check source blob availability; does not modify or copy proprietary data."""
import argparse
import json
from pathlib import Path

REQUIRED = {
    "camera_provider": "proprietary/vendor/bin/hw/android.hardware.camera.provider@2.7-service-google",
    "camera_hal": "proprietary/vendor/lib64/hw/camera.msmnile.so",
    "face_keymaster": "proprietary/vendor/bin/hw/android.hardware.keymaster@4.1-service.citadel",
    "face_airbrush": "proprietary/vendor/bin/hw/vendor.google.airbrush@1.0-service",
    "face_airbrush_lib": "proprietary/vendor/lib64/libairbrush-pixel.so",
    "soli_oslo_firmware": "proprietary/vendor/firmware/OsloSensorPackage.bin",
    "soli_config_firmware": "proprietary/vendor/firmware/OsloSensorConfig.bin",
    "chre_firmware": "proprietary/vendor/firmware/BufferConfigValCHRE.bin",
    "chre_config": "proprietary/vendor/etc/chre",
    "radio_service": "proprietary/vendor/bin/hw/qcrild",
    "main_vendor_blueprint": "Android.bp",
}


def audit(root):
    details = {key: {"path": value, "exists": (root / value).exists()}
               for key, value in REQUIRED.items()}
    return {"source": str(root.resolve()), "checks": details,
            "pass": all(item["exists"] for item in details.values()),
            "note": "Presence only; ABI, policy, licensing and runtime are unverified."}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("vendor_tree", type=Path)
    a = p.parse_args()
    report = audit(a.vendor_tree)
    print(json.dumps(report, indent=2))
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
