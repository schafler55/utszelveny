#!/usr/bin/env bash
# Signs the unsigned app bundle (.aab, the format Google Play takes) built by the "build" job (android.yml) with the
# same key as the APK, and checks the certificate like sign-apk.sh does.
#   usage: sign-aab.sh <unsigned.aab> <signed output name>
#   key:   KS_B64 (the .p12 file in base64), KS_PASS (its password, also the key password), KS_ALIAS
#   check: EXPECT_CERT = SHA-256 of the certificate that must have signed the bundle (set in android.yml)
# An app bundle is signed with jarsigner (apksigner only signs APKs). The key file exists only while this script
# runs and is deleted at the end, even after an error.
set -euo pipefail

in="$1"
out="$2"

if [ -z "${KS_B64:-}" ] || [ -z "${KS_PASS:-}" ] || [ -z "${KS_ALIAS:-}" ]; then
  echo "::error::Signing key missing: ${KEY_HINT:-add the key secrets}"
  exit 1
fi

ks="$RUNNER_TEMP/sign-aab.p12"
trap 'rm -f "$ks"' EXIT
echo "$KS_B64" | base64 -d > "$ks"

# the runner's JDK tools (jarsigner / keytool are not always on PATH)
jar=$(command -v jarsigner || echo "$JAVA_HOME/bin/jarsigner")
kt=$(command -v keytool || echo "$JAVA_HOME/bin/keytool")

cp "$in" "$out"
"$jar" -keystore "$ks" -storetype PKCS12 -storepass:env KS_PASS -keypass:env KS_PASS "$out" "$KS_ALIAS" > /dev/null
"$jar" -verify "$out" | grep -q 'jar verified' || { rm -f "$out"; echo "::error::The signed bundle does not verify"; exit 1; }

# same rule as for the APK: Google Play only accepts a bundle signed with the key it knows (the upload key), and this
# project uses the release key for that, so a bundle signed with any other key is deleted and the job fails
if [ -n "${EXPECT_CERT:-}" ]; then
  got=$("$kt" -printcert -jarfile "$out" | grep -m1 -E '^[[:space:]]*SHA256:' | sed -E 's/.*SHA256:[[:space:]]*//; s/://g' | tr 'A-F' 'a-f' || true)
  if [ "$got" != "$EXPECT_CERT" ]; then
    rm -f "$out"
    echo "::error::Wrong signing key – the bundle is not kept. Certificate of this bundle: ${got:-not found}; expected: $EXPECT_CERT."
    exit 1
  fi
  echo "signing certificate: the expected one ($EXPECT_CERT)"
fi
echo "signed: $out"
