# Biztonság / Security

## Magyarul

Ha biztonsági hibát találsz az ÚtSzelvényben (a webalkalmazásban, az Android alkalmazásban, a https://utszelveny.hu weboldalon vagy a build folyamatban), **ne nyiss róla nyilvános issue-t**, hanem jelezd zártan:

- GitHubon: **Security → Report a vulnerability** (https://github.com/schafler55/utszelveny/security/advisories/new) – ezt csak a fejlesztő látja;
- vagy e-mailben: **visszajelzes@utszelveny.hu**.

Írd le, mit találtál, hogyan lehet előidézni, és melyik verzióban (Névjegy → Alkalmazás). Igyekszem néhány napon belül válaszolni; a javítás a következő stabil kiadásba kerül, és a változásnaplóban (CHANGELOG.md) is megjelenik. Ha szeretnéd, megnevezlek.

Javítást mindig a legutóbbi stabil kiadás kap (https://github.com/schafler55/utszelveny/releases/latest). Nem biztonsági hiba: a térképszolgáltatók (OpenStreetMap, Esri) és a GitHub működése, illetve az úthálózati adatok pontossága – ezeket a szokásos visszajelzésként küldd.

### Az APK eredetiségének ellenőrzése

A stabil kiadások APK fájljait (https://github.com/schafler55/utszelveny/releases) mindig ugyanaz a kulcs írja alá. Az aláíró tanúsítvány (C=HU, O=UtSzelveny, CN=Szaszi Daniel) SHA-256 ujjlenyomata:

`26063c1d3c66598dea90e4853756e4ad7ef6514dd6ebdbd6f03e34413d0b76e0`

Ellenőrzés számítógépen, az Android SDK `apksigner` eszközével: `apksigner verify --print-certs UtSzelveny-V1.4.0.apk` – a „certificate SHA-256 digest” sorban ennek az értéknek kell állnia. Ha más áll ott, az APK nem tőlem származik: ne telepítsd, és jelezd a fenti címen. A már telepített alkalmazást az Android is védi: más kulccsal aláírt APK-t nem enged rátelepíteni.

Az „ÚtSzelvény DEV” változatok (az `apk-latest` és a teszt APK-k) külön fejlesztői kulccsal készülnek; ujjlenyomatuk: `abd3fd7f83e9f2726afa4cc644a515997c3f35311222c42a1290519c9c4c4a88`.

## English

If you find a security problem in ÚtSzelvény (the web app, the Android app, the https://utszelveny.hu website or the build workflows), **please do not open a public issue**. Report it privately instead:

- on GitHub: **Security → Report a vulnerability** (https://github.com/schafler55/utszelveny/security/advisories/new) – only the maintainer sees it;
- or by e-mail: **visszajelzes@utszelveny.hu**.

Describe what you found, how to reproduce it and which version you use (Névjegy → Alkalmazás). I try to answer within a few days; the fix goes into the next stable release and is noted in CHANGELOG.md. You will be credited if you wish.

Only the latest stable release receives fixes (https://github.com/schafler55/utszelveny/releases/latest). Not security issues: the map tile providers (OpenStreetMap, Esri) and GitHub themselves, or the accuracy of the road data – please send those as normal feedback.

### Verifying the APK

The APK files of the stable releases (https://github.com/schafler55/utszelveny/releases) are always signed with the same key. SHA-256 fingerprint of the signing certificate (C=HU, O=UtSzelveny, CN=Szaszi Daniel):

`26063c1d3c66598dea90e4853756e4ad7ef6514dd6ebdbd6f03e34413d0b76e0`

To check it on a computer with `apksigner` from the Android SDK: `apksigner verify --print-certs UtSzelveny-V1.4.0.apk` – the "certificate SHA-256 digest" line must show this value. If it shows anything else, the APK is not from me: do not install it, and please report it at the address above. Android protects an installed app as well: it refuses an update signed with a different key.

"ÚtSzelvény DEV" builds (`apk-latest` and the test APKs) are signed with a separate development key; its fingerprint: `abd3fd7f83e9f2726afa4cc644a515997c3f35311222c42a1290519c9c4c4a88`.
