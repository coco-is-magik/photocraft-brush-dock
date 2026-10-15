"""Package the approved local layout against the cached upstream release archive."""

import difflib
import hashlib
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile


ROOT = Path(__file__).resolve().parent
SOURCE = Path('/home/danbo/src/photocraft-0.7.0')
ARCHIVE = Path('/var/cache/distfiles/photocraft-0.7.0.tar.gz')
ARCHIVE_SHA256 = '420bc64e3548579b1b255aed33be055be1688c3427f429dc5f1c28daf8639a2c'
PATCH = ROOT / 'patches/0100-stacked-brush-dock.patch'
SNAPSHOT = ROOT / 'source/photocraft-0.7.0'
VERIFY = ROOT / 'verification/pristine'


def main():
    if hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() != ARCHIVE_SHA256:
        raise RuntimeError('Upstream archive checksum mismatch')
    if VERIFY.exists():
        raise RuntimeError('Verification already exists; refusing to overwrite evidence')

    changed = []
    snapshot = []
    with tarfile.open(ARCHIVE) as archive:
        for member in archive.getmembers():
            relative = PurePosixPath(member.name).relative_to('photocraft-0.7.0')
            if '..' in relative.parts or relative.is_absolute():
                raise RuntimeError(f'Unsafe archive path: {member.name}')
            if not member.isfile():
                if not member.isdir():
                    raise RuntimeError(f'Unexpected archive member: {member.name}')
                continue
            original = archive.extractfile(member).read()
            local = SOURCE.joinpath(*relative.parts)
            current = local.read_bytes()
            snapshot.append((relative, local, member.mode))
            if original != current:
                if not str(relative).startswith('crates/ui-egui/src/'):
                    raise RuntimeError(f'Unexpected change outside UI: {relative}')
                changed.append((relative, original, current))

    if not changed:
        raise RuntimeError('No source changes found')
    text = ''.join(
        ''.join(difflib.unified_diff(
            before.decode('utf-8').splitlines(keepends=True),
            after.decode('utf-8').splitlines(keepends=True),
            fromfile=f'a/{relative}', tofile=f'b/{relative}',
        ))
        for relative, before, after in changed
    )
    PATCH.parent.mkdir(parents=True, exist_ok=True)
    if PATCH.exists() and PATCH.read_text(encoding='utf-8') != text:
        raise RuntimeError('Existing patch differs; refusing to overwrite')
    PATCH.write_text(text, encoding='utf-8')
    for relative, local, mode in snapshot:
        destination = SNAPSHOT.joinpath(*relative.parts)
        if destination.exists():
            if destination.read_bytes() != local.read_bytes():
                raise RuntimeError(f'Existing snapshot differs: {relative}')
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(local, destination)
        destination.chmod(mode & 0o777)
    for relative, original, _ in changed:
        destination = VERIFY.joinpath(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(original)

    command = ['patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i', str(PATCH)]
    dry_run = subprocess.run(command + ['--dry-run'], cwd=VERIFY, capture_output=True, text=True, timeout=30, check=True)
    applied = subprocess.run(command, cwd=VERIFY, capture_output=True, text=True, timeout=30, check=True)
    for relative, _, expected in changed:
        if VERIFY.joinpath(*relative.parts).read_bytes() != expected:
            raise RuntimeError(f'Patched output differs from approved source: {relative}')
    report = (
        f'Upstream SHA-256: {ARCHIVE_SHA256}\n'
        f'Patch SHA-256: {hashlib.sha256(PATCH.read_bytes()).hexdigest()}\n'
        f'Source snapshot files: {len(snapshot)}\n'
        f'Changed files: {len(changed)}\n'
        'Dry-run and application: PASS, fuzz disabled\n'
        'All patched files match approved source byte-for-byte: PASS\n\n'
        + dry_run.stdout + applied.stdout
    )
    (ROOT / 'verification/report.txt').write_text(report, encoding='utf-8')
    print(report)


if __name__ == '__main__':
    main()