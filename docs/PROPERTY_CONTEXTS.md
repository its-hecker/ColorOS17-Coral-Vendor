# Guarded property context repair for ColorOS 17

The community OnePlus 7 Pro port reports first boot failures because ColorOS and the older vendor tree define the **same property + selector** with conflicting SELinux contexts. This implementation is a reviewable **candidate generator**, not a generic SELinux bypass.

Run only once donor and **assembled** Pixel vendor files have been extracted (the Git vendor source tree does not provide installed `vendor_property_contexts` by itself):

```bash
python3 tools/resolve_property_contexts.py \
  --donor-root /path/to/extracted/coloros \
  --vendor-root /path/to/extracted/pixel/vendor \
  --output /tmp/coral-coloros-propctx --strict
```

The script preserves Pixel vendor contexts. It produces changed **ColorOS product/system_ext** context files separately. Platform contexts are never automatically removed, and ambiguous vendor entries become blockers. A human/code-reviewed compatibility build must install the generated files, preserve labels, rebuild/signed images, and verify the property area with early init logs.

Not a bootable image or a claim that all SELinux policy conflicts are solved. Do **not** set global SELinux permissive or strip all policy rules based on these results.
