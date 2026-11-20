# Változásnapló

Az ÚtSzelvény változásai, a legújabb elöl. A dátumok UTC szerint értendők.
A nagyobb funkciók saját ágon (branch) készültek teszt oldallal és teszt APK-val, és pull requestként (#) kerültek a `main` ágba;
a kisebb javítások közvetlenül a `main`-re kerültek.

## [0.22.4] – 2026-11-20
- Hidak kártya (Pozíció oldal) és a Részletek „Híd” szakasza egyforma soros elrendezést kapott: balra mindig a híd ikonja, alatta (a Pozíció oldalon) a távolság, pl. „150 m” vagy „itt”.
- Új, kéttónusú híd ikonok az alkalmazás színeivel: ugyanaz a híd, a zöld nyíl felfelé mutat a híd felett („Áthaladsz rajta”), lefelé a híd alatt („Alatta haladsz el”), mellette felfelé, ha a híd az út mellett van.
- A korlátozások félkövér piros szöveggel, soronként egy, az érték piros chipben (mint a JOBB / BAL), pl. „Össztömeg [40 t]”; a nagy táblaképek ebből a listából kikerültek.

## [0.22.3] – 2026-11-20
- Ha egy út osztott pályás út (pl. autópálya) felett halad át, mindkét pálya megkapja a „Alatta haladsz el” hidat (eddig csak a hídhoz közelebbi pálya); a térképen a hídpálya mindkét pálya fölé ér.

## [0.22.2] – 2026-11-20
- Térkép: a hidak hosszabbak, és méterben méreteződnek, így nagyításkor is megtartják hosszukat és arányukat.
- Beállítások → Térkép: csúszka, hogy melyik nagyítási szinttől látszanak a hidak (12–18, alapból 15).

## [0.22.1] – 2026-11-20
- Térkép: a híd, amely alatt az út áthalad (pl. földúti híd az M44 felett), kitöltött hídpályaként jelenik meg az úton keresztben, a két pálya rekordja egy hídként; két országos út keresztezésénél a felső út alatt is hídpálya van, így látszik, mi halad felül.

## [0.22] – 2026-11-20
- Hidak a térképen nagyobb nagyításnál (térképi hídjel; kikapcsolható: Beállítások → Térkép). A korlátozott hidak sárgák a súly- vagy magasságkorláttal.
- Két országos út keresztezésénél az alkalmazás megkeresi, melyik út halad a hídon és melyik alatta (764 ilyen híd). A híd magasságkorlátja az alatta haladó úté: ott jelenik meg a térképen (↧), a Pozíció oldal hídkártyáján és a Részleteknél („Alatta haladsz el · M1 hídja”); a hídon haladók csak tájékoztatást kapnak („Alatta: 81106 …”).

## [0.21] – 2026-11-20
- Térkép: egy útra koppintva a buborékban két gomb: **Pont mentése** (a pont mentett keresés lesz, és megnyílik a Keresés oldalon) és **Részletek**.
- Új Szakasz adatai oldal: út (kategória, kezelő, megye, Mérnökség, pálya, szelvények), forgalmi sávok és burkolat, éves forgalom, sebességkorlát, belterület / külterület és település, a ponton lévő híd és az ott érvényes tehergépjármű-korlátozás, koordináták.

## [0.20] – 2026-11-20
- Új beépített NAP szakaszadatok az úthálózathoz: forgalmi sávok száma, burkolat típusa és szélessége, éves keresztmetszeti forgalom (2025). A felület még nem mutatja őket; egy későbbi verzióban a térképen koppintott szakasz részleteinél jelennek meg.
- Új eszköz: `tools/nap_szakaszadatok.py` – a NAP-ból letöltött fájlokból újra előállítja ezeket az adatokat.

## [0.19.5] – 2026-11-20
- A GitHub-tároló új neve `schafler55/utszelveny`; a webalkalmazás címe https://schafler55.github.io/utszelveny/. A linkek (README, Névjegy, változásnapló) az új címre mutatnak. Az Android alkalmazás azonosítója nem változott, a frissítések ugyanúgy települnek.

## [0.19.4] – 2026-11-20
- JOBB / BAL címkék függőlegesen a számok közepén (a keresési részletek nagy szelvénye mellett is).
- Mérések: a kezdet → vég nyíl vastagabb, nagyobb és a számok közepére igazítva (kártya, buborék, szakaszok).
- A Keresés oldal ugyanazzal az animációval nyílik meg, mint a Pozíció és a Mérés.
- Folyamatban lévő mérés: jobb felső sarokban a GNSS-pontosság jelzése (mint a Pozíció fő kártyáján), az eltelt idő a „Mérés folyamatban” alatt.
- Fotó: az elő- / hátlapi kamera váltó gomb kikapcsolva (a kód megmaradt).
- A félszélességű mezőkben „KEZDETE” a „KEZDET” helyett.
- Mentett térképi mérés: KEZDETE / VÉGE mezők; a pontok listájában zöld K, P1, P2 … és piros V jel, mint a térképen (a szakaszok is K→P1, P1→V).

## [0.19.3] – 2026-11-20
- A kis JOBB / BAL címkék keskenyített felirattal: ugyanaz a félkövér betű 80%-os szélességre szűkítve, mint az útszámtáblákon (külön betűtípus nélkül). A Pozíció fő kártya címkéje nem változott.

## [0.19.2] – 2026-11-20
- A kis JOBB / BAL címkék kisebbek, kitöltés nélkül, vékonyabb (1 px) zöld kerettel. A Pozíció fő kártya címkéje és a Keresés pályaválasztó gombja nem változott.

## [0.19.1] – 2026-11-20
- JOBB / BAL címke: az alkalmazás zöld kiemelőszíne (halvány kitöltés, zöld keret), ugyanaz a betűtípus, mint mindenhol, a felirat függőlegesen középen. A beágyazott keskeny betűtípus és a hozzá tartozó forrásmegjelölés megszűnt.
- Egy betűcsalád az egész alkalmazásban (Roboto, ennek hiányában a rendszer betűtípusa): szövegek, szelvényszámok, térképi feliratok és táblák, fotóbélyegző – web és APK ugyanúgy.
- Mentett keresés részleteiből kikerült a „Pálya” sor (a JOBB / BAL a cím szelvénye mellett látszik).
- Mérés a térképen: mentés után a mérőeszköz alaphelyzetbe áll, alul a mentett mérés buborékja jelenik meg. A lerakott pontok és vonalak a mérések lila-rózsaszín színét kapják.
- Mérésnél JOBB / BAL címke, ha a mérés végig egy úton és ugyanazon a pályán van.

## [0.19] – 2026-11-20
- Jobb / bal pálya mindenhol egyformán: kis „JOBB” / „BAL” címke (halvány türkiz kitöltés, türkiz keret, keskeny félkövér betű) a km+m mellett – Pozíció fő kártya, térképi buborékok, mentett keresések, keresési részletek; a mérések Kezdet / Vége mezőiben a km alatti sorban. A Keresés pályaválasztó gombja ugyanilyen színű, „JOBB” / „BAL” felirattal.
- A címke betűtípusa beágyazott Roboto (legkeskenyebb szélesség, csak a szükséges betűk, ~5 KB), így minden telefonon ugyanúgy néz ki.

## [0.18.2] – 2026-11-20
- Térkép: a rétegek gomb nem nyitja meg az alsó beállításpanelt, csak végiglépteti az alapréteget (Szürke → Sötét → Műhold → Ki), a választott réteg neve rövid ideig megjelenik. A többi térképbeállítás a Beállítások → Térkép fülön van.

## [0.18.1] – 2026-11-20
- Az OpenStreetMap és az Esri forrásmegjelölése sima szöveg, nem link (a térképen és a Névjegyben).

## [0.18] – 2026-11-20
- Térkép: a mentett keresés és mérés „Térképen” gombja ugyanúgy működik – ráközelít, és alul egy közös buborékot mutat: név a keresés / mérés színében, útszámtábla + szelvény (szakasznál kezdet – vég, mérésnél kezdet → vég), az út neve vagy „Több úton: …”, hossz és dátum.
- A buborék gombjai: Elrejtés (ugyanaz a kapcsoló, mint a mentett listában), Törlés (megerősítéssel), Részletek (megnyitja a mentett kártyát kinyitva, kiemelve). Nem mentett keresés: Törlés és Mentés.
- A térkép tetején lévő címkék megszűntek; a térképi címkére koppintva is ez a buborék nyílik meg.

## [0.17] – 2026-11-20
- Világos téma: „Fehér kártyák” – fehér kártyák halványszürke háttéren, lágy árnyékkal; a mentett keresések és mérések mind külön fehér kártyák; sötétebb szövegek (címkék, dátumok, koordináták) a jobb olvashatóságért. Az Android állapot- és navigációs sáv színe is ehhez igazodik. A sötét téma nem változott.

## [0.16.10] – 2026-11-19
- Térkép: az útszámtáblák helye nagyítás és húzás közben nem ugrál – a táblák az út mentén rögzített pontokon állnak, a már látható tábla a helyén marad (mérve kb. 8–12-szer kevesebb ugrás, eltűnés, felbukkanás).

## [0.16.9] – 2026-11-19
- 4–5 jegyű útszámnál mindenhol szélesebb tábla (fő kártya, térképi buborékok, keresés, javaslatok), a szám ugyanakkora, mint a rövid útszámoknál.

## [0.16.8] – 2026-11-19
- Térképi koppintás buborék: útszámtábla és szelvény egy sorban, alatta balra igazítva az út neve, a kezelő (pl. Magyar Közút Nonprofit Zrt.) és a két koordináta.

## [0.16.7] – 2026-11-19
- Térkép: a koppintás utáni információs buborék útszámtáblával és szelvénnyel jelenik meg, mint a keresés eredménye; a WGS84 és az EOV koordináta külön sorban.

## [0.16.6] – 2026-11-19
- GNSS kikapcsolásakor (Beállítások → Általános) a Pozíció fő kártyája „GNSS kikapcsolva” lesz (az utolsó ismert pozícióval), nem marad rajta az utolsó szelvény; a GNSS-kártyán „GNSS kikapcsolva a beállításokban” jelzés.

## [0.16.5] – 2026-11-19
- Budapest kártya: „nem része az országos közúthálózatnak” kisbetűvel.
- A térkép felső címkéin az alkalmazás saját ikonjai (vonalzó, nagyító, bezárás) az emojik helyett; a mérés címkéje a térképi címkével azonos hosszt mutat.

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

## [0.16] – 2026-11-19 · [#14](https://github.com/schafler55/utszelveny/pull/14)
- Gyorsabb térkép mentett keresések, mérések és fényudvar mellett is: az álló réteg (utak, kiemelés, keresett szakaszok, mérési nyomvonalak, km-kövek) egy háttérvászonra rajzolódik, és követés / húzás közben csak eltolódik.
- Az utak úttípusonként egy útvonallal rajzolódnak, csak a képernyőn lévő részük; a fényudvar egyetlen áttetsző vonal.
- Útszámtáblák, pozíciónyíl, koppintásjelölő: elmosott árnyék helyett olcsó, eltolt árnyék.

## [0.15.1] – 2026-11-19
- Budapest kártya: „Fővárosi vagy kerületi helyi út, / Nem része az országos közúthálózatnak”.
- Mentett mérés: „GNSS mérés” (kötőjel nélkül).
- 4–5 jegyű útszámnál szélesebb, jobban olvasható tábla a mentett listákban.
- Mentett keresésnél is útszámtábla látszik; a mentett kártyák bárhol koppintva nyílnak.
- Névjegy: a copyright és a figyelmeztetés sorai külön sorban.

## [0.15] – 2026-11-19 · [#13](https://github.com/schafler55/utszelveny/pull/13)
- Budapest belterületén a fő kártya jelzi, hogy a fővárosi és kerületi utak nem részei az országos közúthálózatnak (a V0.14 csak a fejlesztési ágon létezett).
- Átkelési szakaszon a település neve (OpenStreetMap közigazgatási határok alapján), helységnévtábla a sebességkorlát mellett.
- Fotó: „‹település› belterület” a bélyegzőn átkelési szakaszon.
- Material 3 stílusú pozíciónyíl és koppintásjelölő a térképen.

## [0.13] – 2026-11-19 · [#12](https://github.com/schafler55/utszelveny/pull/12)
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

## [0.10] – 2026-11-19 · [#11](https://github.com/schafler55/utszelveny/pull/11)
- HUD mód: tükrözött, nagy kontrasztú kép, hogy a műszerfalra fektetett telefon a szélvédőn tükröződjön.
- Új HUD és Keresés beállítási lap; a beállítások fülei 4 × 2 rácsban.

## [0.9] – 2026-11-19 · [#10](https://github.com/schafler55/utszelveny/pull/10)
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

## [0.8.1] – 2026-11-18 · [#9](https://github.com/schafler55/utszelveny/pull/9)
- Lebegő navigációs eszköztár animált feliratokkal és színátmenettel alatta.

## [0.8] – 2026-11-18 · [#8](https://github.com/schafler55/utszelveny/pull/8)
- Új Material 3 felület, választható világos téma, animált nyitóképernyő és animációk.
- Fotó: vaku gomb (Vaku ki / Vaku / Lámpa); a Vissza gomb lépésenként zár.

## [0.7.3] – 2026-11-18 · [#7](https://github.com/schafler55/utszelveny/pull/7)
- Térkép: az aktuális út kiemelése saját színben (Vastagabb / Fényudvar / Nincs).

## [0.7.2] – 2026-11-18
- „Térkép alapréteg” a „Háttértérkép” helyett.

## [0.7.1] – 2026-11-18
- Mérés: a km+m a kezdő / jelenlegi dobozban marad.

## [0.7] – 2026-11-18 · [#6](https://github.com/schafler55/utszelveny/pull/6)
- „GNSS” a „GPS” helyett minden feliratban; WGS84 az alapértelmezett, új koordináta-formátum.
- A használt és látható műholdak rendszerenként a GNSS-kártyán (Android).

## [0.6.3] – 2026-11-18
- Csípő-nagyításnál az ujjak közötti pont a helyén marad.

## [0.6.2] – 2026-11-18
- Alkalmazásikon és verziószám a fejlécben.

## [0.6.1] – 2026-11-18
- „Kézi útválasztás kikapcsolása” felirat; a NAP-megjegyzés rendesen elrejtve.

## [0.6] – 2026-11-18 · [#5](https://github.com/schafler55/utszelveny/pull/5)
- Új Fotó oldal: útszám, km+m, dátum és idő a kép tetején kétsoros sávban, égtáj és EXIF-pozíció.

## [0.5.1] – 2026-11-18 · [#4](https://github.com/schafler55/utszelveny/pull/4)
- A térképi mérés útvonala autópálya-csomópontokon át is működik.

## [0.5] – 2026-11-18 · [#3](https://github.com/schafler55/utszelveny/pull/3)
- Beállítások fülekkel, térkép-beállítások panel a térképen, mérés-beállítások.

## [0.4] – 2026-11-18 · [#2](https://github.com/schafler55/utszelveny/pull/2)
- Új Mérés oldal: GNSS-mérés szelvénnyel, több úton át szakaszokra bontva, mérés a térképen az úthálózat mentén.

## [0.3] – 2026-11-18 · [#1](https://github.com/schafler55/utszelveny/pull/1)
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
