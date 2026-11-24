#!/usr/bin/env bash
# Signs the unsigned APK built by the "build" job (android.yml) and writes the signed APK.
#   usage: sign-apk.sh <unsigned.apk> <signed output name>
#   key:   KS_B64 (the .p12 file in base64), KS_PASS (its password, also the key password), KS_ALIAS
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

# shows which certificate signed it (public information); an APK only installs over the app
# when this certificate is the same as the installed one's
"$bt/apksigner" verify --print-certs "$out" | grep -E '^Signer #1 certificate (DN|SHA-256 digest):'
echo "signed: $out"
