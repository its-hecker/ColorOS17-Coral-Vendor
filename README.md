# ColorOS 17 / coral vendor adapter

Maintainer: **Hecker**. The Pixel 4 XL's vendor blobs remain sourced from our pinned HeckerOS/PixelOS coral vendor tree. This repository contains **read-only compatibility audits** and will hold narrowly scoped ColorOS changes once the donor system has been inspected.

No binary blobs, radio partitions, proprietary firmware or flashable images are included here. Do not substitute OPPO/OnePlus vendor partitions: the camera, FaceAuth, Soli, Citadel and modem stacks are Pixel-specific.

Run `python3 tools/audit_vendor.py /path/to/heckeros-coral-vendor` on the source checkout. Results are evidence of source presence, **not** proof that ColorOS can load the HALs.
