import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "property_contexts",
    Path(__file__).resolve().parents[1] / "tools/resolve_property_contexts.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


def write(root, path, text):
    file = root / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text)


class PropertyContextTests(unittest.TestCase):
    def prepare(self, donor, vendor):
        write(vendor, "etc/selinux/vendor_property_contexts",
              "persist.vendor.oslo u:object_r:vendor_oslo_prop:s0 exact string\n")
        write(donor, "system/etc/selinux/plat_property_contexts",
              "ro.build.version.sdk u:object_r:build_prop:s0 exact int\n")
        write(donor, "system_ext/etc/selinux/system_ext_property_contexts",
              "persist.vendor.oslo u:object_r:system_ext_oslo_prop:s0 exact string\n"
              "persist.vendor.other u:object_r:other_prop:s0 exact string\n")
        write(donor, "product/etc/selinux/product_property_contexts",
              "# all good\n")

    def test_candidate_removes_only_direct_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "donor"
            v = Path(tmp) / "vendor"
            self.prepare(d, v)
            r = p.reconcile(d, v)
            self.assertEqual(len(r["removed_candidates"]), 1)
            self.assertEqual(r["blocked"], [])
            kept = r["file_outputs"]["system_ext/etc/selinux/system_ext_property_contexts"]["content"]
            self.assertNotIn("persist.vendor.oslo", kept)
            self.assertIn("persist.vendor.other", kept)
            self.assertIn("ro.build.version.sdk", r["file_outputs"]["system/etc/selinux/plat_property_contexts"]["content"])

    def test_platform_conflict_is_never_auto_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            d, v = Path(tmp) / "donor", Path(tmp) / "vendor"
            self.prepare(d, v)
            write(d, "system/etc/selinux/plat_property_contexts",
                  "persist.vendor.oslo u:object_r:bad_plat_prop:s0 exact string\n")
            r = p.reconcile(d, v)
            self.assertEqual(len(r["blocked"]), 1)
            self.assertEqual(r["blocked"][0]["reason"], "platform conflict needs review")

    def test_missing_vendor_contexts_is_fatal(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                p.reconcile(Path(tmp) / "a", Path(tmp) / "b")

    def test_vendor_ambiguous_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            d, v = Path(tmp) / "donor", Path(tmp) / "vendor"
            self.prepare(d, v)
            write(v, "odm/etc/selinux/odm_property_contexts",
                  "persist.vendor.oslo u:object_r:other_vendor_prop:s0 exact string\n")
            r = p.reconcile(d, v)
            self.assertEqual(len(r["blocked"]), 1)
            self.assertEqual(len(r["removed_candidates"]), 0)


if __name__ == "__main__":
    unittest.main()
