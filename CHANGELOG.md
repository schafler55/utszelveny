# Változásnapló

Az ÚtSzelvény változásai, a legújabb elöl. A dátumok UTC szerint értendők.
A nagyobb funkciók saját ágon (branch) készültek teszt oldallal és teszt APK-val, és pull requestként (#) kerültek a `main` ágba;
a kisebb javítások közvetlenül a `main`-re kerültek.

## [0.16.4] – 2026-11-19
- Térképi címkék: a koppintás után a telefon kattintása már nem az új oldalra esik (ez néha visszacsukta a megnyitott kártyát vagy levette a kiemelést, vagy egy mezőre esett).

## [0.16.3] – 2026-11-19
- Keresés: sikeres keresés után az útszám- és szelvénymezők kiürülnek; mentés után a keresési eredmény kártyája eltűnik a Keresés oldalról (a keresés a mentett listában marad).

## [0.16.2] – 2026-11-19
- Mentett mérések és keresések: nagyobb, jobban olvasható útszámtáblák.
- Térkép: a megjelenített mentett méréseknek is van címkéje (név · hossz) a kezdőpontnál, mint a kereséseknek; a szakaszkereséseknél mindig látszik a címke.
- A térképi címkére koppintva megnyílik a mentett keresés / mérés kártyája kinyitva, kiemelve; a felső címkéknél a név nyit, a ✕ zár.

## [0.16.1] – 2026-11-19
- A mentett mérés / keresés kártyája lefelé nyílik ki, és záráskor felfelé húzódik vissza a kis kártyába.

## [0.16] – 2026-11-19 · [#14](https://github.com/schafler55/kozutszelveny/pull/14)
- Gyorsabb térkép mentett keresések, mérések és fényudvar mellett is: az álló réteg (utak, kiemelés, keresett szakaszok, mérési nyomvonalak, km-kövek) egy háttérvászonra rajzolódik, és követés / húzás közben csak eltolódik.
- Az utak úttípusonként egy útvonallal rajzolódnak, csak a képernyőn lévő részük; a fényudvar egyetlen áttetsző vonal.
- Útszámtáblák, pozíciónyíl, koppintásjelölő: elmosott árnyék helyett olcsó, eltolt árnyék.

## [0.15.1] – 2026-11-19
- Budapest kártya: „Fővárosi vagy kerületi helyi út, / Nem része az országos közúthálózatnak”.
- Mentett mérés: „GNSS mérés” (kötőjel nélkül).
- 4–5 jegyű útszámnál szélesebb, jobban olvasható tábla a mentett listákban.
- Mentett keresésnél is útszámtábla látszik; a mentett kártyák bárhol koppintva nyílnak.
- Névjegy: a copyright és a figyelmeztetés sorai külön sorban.

## [0.15] – 2026-11-19 · [#13](https://github.com/schafler55/kozutszelveny/pull/13)
- Budapest belterületén a fő kártya jelzi, hogy a fővárosi és kerületi utak nem részei az országos közúthálózatnak (a V0.14 csak a fejlesztési ágon létezett).
- Átkelési szakaszon a település neve (OpenStreetMap közigazgatási határok alapján), helységnévtábla a sebességkorlát mellett.
- Fotó: „‹település› belterület” a bélyegzőn átkelési szakaszon.
- Material 3 stílusú pozíciónyíl és koppintásjelölő a térképen.

## [0.13] – 2026-11-19 · [#12](https://github.com/schafler55/kozutszelveny/pull/12)
- Sima térképmozgás követéskor: a térkép és a nyíl a GNSS-frissítések között is folyamatosan halad.
- Lassú haladásnál és egyetlen kiugró irányértéknél nem fordul el a térkép.

## [0.12.3] – 2026-11-19
- Térkép: a Követés gomb ugyanakkora, mint a többi térképgomb.

## [0.12.2] – 2026-11-19
- CSV-export a mentett keresésekhez is; a CSV-gombok elrejthetők (Beállítások → Mérés / Keresés).

## [0.12.1] – 2026-11-19
- Mentett mérés: egy elválasztó vonal a részletek felett, mint a keresésnél.

## [0.12] – 2026-11-19
- A mentett mérések és a mentett keresések közös kártyát és viselkedést kaptak.

## [0.11.3] – 2026-11-19
- A WGS84 és az EOV koordináta külön sorban, sortörés nélkül.

## [0.11.2] – 2026-11-19
- Mérés: a mentett mérések listája nem ugrál, átnevezésnél nem záródik be a billentyűzet.

## [0.11.1] – 2026-11-19
- Általános: az alsó menü elrejtése görgetéskor kikapcsolható.

## [0.11] – 2026-11-19
- Gyorsabb fotózás: a képek sorban dolgozódnak fel, az exponáló gomb nem zár le.
- Választható mentési mappa az Android alkalmazásban (Képek, DCIM / ÚtSzelvény, DCIM / Camera vagy egyéni mappa).

## [0.10.3] – 2026-11-19
- Névjegy: az Android versionCode zárójelben a verziószám mögött.

## [0.10.2] – 2026-11-19
- Exponálás a hangerőgombokkal (és Bluetooth-os távkioldóval) az Android alkalmazásban.

## [0.10.1] – 2026-11-19
- A HUD beállítási lap mindig látható, az Általános HUD-kapcsoló megszűnt.

## [0.10] – 2026-11-19 · [#11](https://github.com/schafler55/kozutszelveny/pull/11)
- HUD mód: tükrözött, nagy kontrasztú kép, hogy a műszerfalra fektetett telefon a szélvédőn tükröződjön.
- Új HUD és Keresés beállítási lap; a beállítások fülei 4 × 2 rácsban.

## [0.9] – 2026-11-19 · [#10](https://github.com/schafler55/kozutszelveny/pull/10)
- Új Keresés fül: pont vagy szakasz keresése útszám és km+m alapján, jobb / bal pálya váltóval.
- Mentett keresések és mentett mérések egyenként kapcsolóval a térképen; gyorsabb rajzolásuk.

## [0.8.5] – 2026-11-18
- A „Vaku ki” ikon villáma egybefüggő vonal.

## [0.8.4] – 2026-11-18
- A híd-, állapot- és vakuikonok is lekerekített, Material 3 stílusúak.

## [0.8.3] – 2026-11-18
- Lekerekített Material 3 ikonok; a fejléc ikonja megnyitja a Névjegyet.

## [0.8.2] – 2026-11-18
- Kevésbé lekerekített kamerakeret; enyhébb, magasabb színátmenet a navigáció alatt.

## [0.8.1] – 2026-11-18 · [#9](https://github.com/schafler55/kozutszelveny/pull/9)
- Lebegő navigációs eszköztár animált feliratokkal és színátmenettel alatta.

## [0.8] – 2026-11-18 · [#8](https://github.com/schafler55/kozutszelveny/pull/8)
- Új Material 3 felület, választható világos téma, animált nyitóképernyő és animációk.
- Fotó: vaku gomb (Vaku ki / Vaku / Lámpa); a Vissza gomb lépésenként zár.

## [0.7.3] – 2026-11-18 · [#7](https://github.com/schafler55/kozutszelveny/pull/7)
- Térkép: az aktuális út kiemelése saját színben (Vastagabb / Fényudvar / Nincs).

## [0.7.2] – 2026-11-18
- „Térkép alapréteg” a „Háttértérkép” helyett.

## [0.7.1] – 2026-11-18
- Mérés: a km+m a kezdő / jelenlegi dobozban marad.

## [0.7] – 2026-11-18 · [#6](https://github.com/schafler55/kozutszelveny/pull/6)
- „GNSS” a „GPS” helyett minden feliratban; WGS84 az alapértelmezett, új koordináta-formátum.
- A használt és látható műholdak rendszerenként a GNSS-kártyán (Android).

## [0.6.3] – 2026-11-18
- Csípő-nagyításnál az ujjak közötti pont a helyén marad.

## [0.6.2] – 2026-11-18
- Alkalmazásikon és verziószám a fejlécben.

## [0.6.1] – 2026-11-18
- „Kézi útválasztás kikapcsolása” felirat; a NAP-megjegyzés rendesen elrejtve.

## [0.6] – 2026-11-18 · [#5](https://github.com/schafler55/kozutszelveny/pull/5)
- Új Fotó oldal: útszám, km+m, dátum és idő a kép tetején kétsoros sávban, égtáj és EXIF-pozíció.

## [0.5.1] – 2026-11-18 · [#4](https://github.com/schafler55/kozutszelveny/pull/4)
- A térképi mérés útvonala autópálya-csomópontokon át is működik.

## [0.5] – 2026-11-18 · [#3](https://github.com/schafler55/kozutszelveny/pull/3)
- Beállítások fülekkel, térkép-beállítások panel a térképen, mérés-beállítások.

## [0.4] – 2026-11-18 · [#2](https://github.com/schafler55/kozutszelveny/pull/2)
- Új Mérés oldal: GNSS-mérés szelvénnyel, több úton át szakaszokra bontva, mérés a térképen az úthálózat mentén.

## [0.3] – 2026-11-18 · [#1](https://github.com/schafler55/kozutszelveny/pull/1)
- Térkép-átdolgozás: műholdkép, menetirány szerinti forgatás, útszám-táblák a térképen.
- Minden fejlesztési ághoz teszt weboldal és teszt APK.

## [0.2] – 2026-11-18
- A verziószámozás újrakezdődött V0.2 Beta-tól (korábban V1.5.9), mert az alkalmazás még nem érte el az 1.0-t.

## Korábbi számozás (V1.x) – 2026-11-17 / 18
- **V1.5.9:** az alkalmazásikonban régi stílusú, csúcsos tetejű kilométerkő.
- **V1.5.8:** új név: ÚtSzelvény (korábban KözútSzelvény), végleges ikon.
- **V1.5.6 – V1.5.7:** új alkalmazásikon.
- **V1.5.5:** tisztább útnév a fő kártyán.
- **V1.5.4:** útszám a magyar útjelző tábla alakjában.
- **V1.5.3:** felüljárók mindkét pályán.
- **V1.5.2:** egyszerű hídikonok.
- **V1.5.1:** hidak az út alatt és felett, koppintható közeli utak.
- **V1.5:** tehergépjármű- és súlykorlátozások.
- **V1.4:** első feltöltés: útszám és km+m a NAP adataiból, sebességkorlát, hidak, kezelő; Android alkalmazás és APK-build.
