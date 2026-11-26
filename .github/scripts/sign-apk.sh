#!/usr/bin/env bash
# Signs the unsigned APK built by the "build" job (android.yml) and writes the signed APK.
#   usage: sign-apk.sh <unsigned.apk> <signed output name>
#   key:   KS_B64 (the .p12 file in base64), KS_PASS (its password, also the key password), KS_ALIAS
#   check: EXPECT_CERT = SHA-256 of the certificate that must have signed the APK (set in android.yml)
# The key file exists only while this script runs and is deleted at the end, even after an error.
set -euo pipefail

in="$1"
out="$2"

if [ -z "${KS_B64:-}" ] || [ -z "${KS_PASS:-}" ] || [ -z "${KS_ALIAS:-}" ]; then
  echo "::error::Signing key missing: ${KEY_HINT:-add the key secrets}"
  exit 1
fi

ks="$RUNNER_TEMP/sign.p12"
aligned="$RUNNER_TEMP/aligned.apk"
trap 'rm -f "$ks" "$aligned"' EXIT
echo "$KS_B64" | base64 -d > "$ks"

# newest Android build-tools on the GitHub runner (zipalign + apksigner)
bt=$(ls -d "${ANDROID_HOME:-$ANDROID_SDK_ROOT}"/build-tools/* | sort -V | tail -1)
echo "build-tools: $bt"

"$bt/zipalign" -f -p 4 "$in" "$aligned"
"$bt/apksigner" sign --ks "$ks" --ks-type PKCS12 --ks-key-alias "$KS_ALIAS" \
  --ks-pass env:KS_PASS --key-pass env:KS_PASS --out "$out" "$aligned"

# checks the signature (fails the job if it is not valid) and shows which certificate signed it (public
# information); an APK only installs over the app when this certificate is the same as the installed one's.
# The line format differs between build-tools versions ("Signer #1 …" / "Signer (minSdkVersion=…) …").
certs=$("$bt/apksigner" verify --print-certs "$out" 2>/dev/null)
echo "$certs" | grep -E 'certificate (DN|SHA-256 digest):' || echo "$certs"

# The key must be the one the installed apps were signed with: an APK signed with any other key cannot be installed
# over them. On a different (or unreadable) certificate the signed APK is deleted and the job fails, so the publish
# job never runs and nobody is offered that APK.
if [ -n "${EXPECT_CERT:-}" ]; then
  got=$(echo "$certs" | grep -oE 'certificate SHA-256 digest: [0-9a-fA-F]{64}' | awk '{print tolower($NF)}' | sort -u | xargs || true)
  if [ "$got" != "$EXPECT_CERT" ]; then
    rm -f "$out"
    echo "::error::Wrong signing key – nothing is published. Certificate of this APK: ${got:-not found}; expected: $EXPECT_CERT. Put the right key file into the secret (${KEY_HINT:-key secrets}) and run the job again."
    exit 1
  fi
  echo "signing certificate: the expected one ($EXPECT_CERT)"
fi
echo "signed: $out"
