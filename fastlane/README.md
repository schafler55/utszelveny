# Google Play áruházi adatok

Az ÚtSzelvény Google Play adatlapjának előkészített szövegei (a Google Play kiadás egyelőre nincs eldöntve), a Play (és az F-Droid) által is ismert „fastlane” mappaszerkezetben:

- `metadata/android/hu-HU/` – magyar (alapértelmezett nyelv), `metadata/android/en-US/` – angol
- `title.txt` (legfeljebb 30 karakter), `short_description.txt` (legfeljebb 80), `full_description.txt` (legfeljebb 4000)
- `changelogs/<versionCode>.txt` – az adott kiadás újdonságai (legfeljebb 500 karakter), pl. `1040000.txt` = V1.4.0

Egyelőre kézzel kerülnek a Play Console-ba (Áruházbeli jelenlét → Fő áruházi adatlap); az adatvédelmi tájékoztató címe:
https://utszelveny.hu/adatvedelem.html
