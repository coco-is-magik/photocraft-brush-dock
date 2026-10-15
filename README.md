# PhotoCraft stacked Brushes dock

## Contents

- `source/photocraft-0.7.0/`: all 1,474 upstream release files, with the approved
  local changes applied. Build artifacts and private application configuration are excluded.
- `patches/0100-stacked-brush-dock.patch`: 25 changed UI and translation files,
  relative to the packaged 0.7.0 archive. Includes brush and dock regression tests.
- `verification/report.txt`: archive/patch checksums and clean-application evidence.
- `package_patch.py`: packaging recipe for this exact release and local source tree;
  refuses changed archives, differing existing outputs, and repeated verification.

Source archive SHA-256:
`420bc64e3548579b1b255aed33be055be1688c3427f429dc5f1c28daf8639a2c`

Patch SHA-256:
`6a014fb6eade0136cffb210645dbeb7ce4e4af031513658fb74e863a520f3983`

## Install the user patch

Installation was NOT performed: this session has no passwordless administrator access.
Run these separately in an administrator-capable terminal:

```sh
sudo install -d -m 0755 /etc/portage/patches/media-gfx/photocraft
sudo install -m 0644 '/nas/contents/Projects/Programming Projects/photocraft-brush-dock/patches/0100-stacked-brush-dock.patch' /etc/portage/patches/media-gfx/photocraft/0100-stacked-brush-dock.patch
```

Confirm the installed checksum matches the value above:

```sh
sha256sum /etc/portage/patches/media-gfx/photocraft/0100-stacked-brush-dock.patch
```

To rebuild and install the currently approved release from source:

```sh
sudo emerge --ask --oneshot --usepkg=n =media-gfx/photocraft-0.7.0
```

This last command changes the installed application; it has not been run here.
Inspect Portage's patch output during preparation and then launch the installed
application to verify attachment, resizing, tab selection and restart persistence.

## Updates and recovery

The unversioned package directory is deliberate: Portage attempts this patch on
future source builds as well as 0.7.0. It does not patch prebuilt binary packages.
The file persists, but future upstream changes may require refreshing its hunks.
Do not treat compatibility with future releases as guaranteed. Check that the
patch is reported as applied when updating. More-specific package-version patch
directories can take precedence over a same-named patch.

To disable the customization, rename the installed file so it no longer ends in
`.patch` or `.diff`, then rebuild the package from source. The currently installed
binary remains unchanged until the rebuild. No user artwork or configuration needs
to be removed. Existing layouts default to floating; use **Attach to right sidebar**.

Gentoo reference: the `/etc/portage/patches` section of `portage(5)` and
the Gentoo Handbook's advanced Portage user-patch documentation.

## Verification

- Applied against pristine archived contents with `patch --fuzz=0`, dry-run and actual.
- All 25 resulting files match the approved local source byte-for-byte.
- Previously completed UI suite: 1,796 passed, zero failed, 10 ignored;
  desktop build and strict clippy logs reconfirmed successful, all exit codes zero.
- Development executable responds with `photocraft 0.7.0 (dev build)`.
- No Portage rebuild, installed-binary change or installed-patch verification performed.