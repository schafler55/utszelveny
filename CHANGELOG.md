# Változásnapló

Az ÚtSzelvény változásai, a legújabb elöl. A dátumok UTC szerint értendők.
A nagyobb funkciók saját ágon (branch) készülnek teszt oldallal és teszt APK-val, és pull requestként (#) kerülnek a `main` ágba;
a kisebb javítások közvetlenül a `main`-re kerülnek.

**Verziószámok:** a V1.1.7-től a verziószám csak stabil kiadáskor nő. A legutóbbi kiadás óta a `main` ágra került
változások a „kiadatlan” szakaszba kerülnek, és a következő stabil kiadás ezeket együtt tartalmazza
(apró javítás: harmadik szám, pl. 1.1.8; új funkció: második szám, pl. 1.2.0). Korábban szinte minden módosítás
saját verziószámot kapott, ezért a régebbi bejegyzések aprók; a ténylegesen kiadott változatokat
„Stabil kiadás” jelöli.

## Kiadatlan
- **Térkép, nagyítási szint:** a bal felső méretarány buborékban a lépték előtt a nagyítási szint is látszik (pl. „Z16 | 50 m”); ugyanez a szám, amihez a hidak, a kilométerszelvények és a buszmegállók csúszkája viszonyít.
- **Buszmegállók a térképen az út mellett:** 15-ös nagyítástól a jel az út azon oldalán áll, ahol a megálló van (jobb / bal oldal a szelvényezés irányában), mint az OpenStreetMapen; az útközépi megállók az úton maradnak. 15 alatt az azonos nevű megálló két oldala egy jel az úton, 14 alatt pedig csak egy kis kék pont fehér alapon.
- **„ITT” felirat:** a hidak, a tehergépjármű-korlátozások, a buszmegállók és az azonosítópont távolságánál az „itt” helyett nagybetűs, félkövér „ITT”.
- **Új NAP adatok: egyirányú útpályák és autóbusz-megállóhelyek** (`tools/nap_egyiranyu_megallok.py`). A Szakasz adatai oldalon az Út részben új sor: „Forgalmi irány” (egyirányú a szelvényezés irányában / azzal szemben, vagy kétirányú); új „Autóbusz-megállóhelyek” rész az út 500 m-en belüli megállóival (név, oldal, szelvény, kiépítés; az azonos nevű megállók egy sorban). A térképen kis buszmegálló jelek; kapcsoló és nagyítási csúszka: Beállítások → Térkép → Rétegek (alapból ki, 16-os nagyítástól).
- **Térkép, széles képernyő:** böngészőben (760 px szélesség felett) a Térkép oldal kitölti az ablak teljes szélességét; a többi oldal továbbra is középen, telefonszélességben marad. Az alsó buborék és a térkép panelje középen, telefonszélességben marad.
- **Visszajelzés:** a Névjegy → Támogatás csoportban „kapcsolat” link a visszajelzes@utszelveny.hu címre (a levelezőalkalmazást nyitja meg); a kezdőlapon „Hibajelentés” gomb ugyanide.
- **Térkép:** menet közben (kb. 7 km/h felett, GNSS szerint) a térkép bal alsó sarkában kis sebességkorlát-tábla, átkelési szakaszon mellette a helységnévtábla; megálláskor 8 másodperc után eltűnik. Kapcsoló: Beállítások → Térkép → Nézet → „Sebességkorlát és helységnévtábla” (alapból be).
- **Térkép, címkék:** a kijelölt keresés vagy mérés címkéje feltűnőbb (nagyobb, a saját színével kitöltve, fehér kerettel), a szakasz vagy a nyomvonal vastagabb; a térkép más pontjára koppintva a kijelölés megszűnik (eddig megmaradt).
- **Címke a térképen:** új beállítás a Keresés és a Mérés fülön: a mentett keresések és mérések címkéje a térképen a nevük, vagy az útszám és a km+m (alapból: keresésnél útszám, mérésnél név, mint eddig).
- **GNSS mérés:** a mentett mérés részleteiben a „Legrosszabb pontosság” a mérésben felhasznált GNSS-pontok közül (az 50 m-nél pontatlanabb jeleket a mérés eddig is kihagyta).
- **Képernyő ébren tartása:** minden oldalon működik, amíg az alkalmazás nyitva van, a GNSS állapotától függetlenül; az Android alkalmazásban a kapcsoló ki is kapcsolja (eddig mindig ébren tartotta a kijelzőt).
- **Pozíció:** a sebességkorlát kártyán a sebesség buborék ugyanott áll, mint a fő kártyán a pontosság jelzése.
- **Fotó:** a „NINCS MENTVE” felirat a kép feldolgozása alatt is látszik, és halvány piros kitöltésű, piros keretes, lekerekített címke lett; a galéria ikon (és a kameraváltó gomb) középre került az exponáló gomb és a képernyő széle között.
- **Névjegy:** a Támogatás csoport az Alkalmazás alá került, a gomb felirata „Támogatás”; a frissítéseknél az ellenőrzés ideje évszámmal; az Adatok sorban a hidak száma is, a nagy számok ponttal tagolva (22.341 útszakasz); új adatvédelmi szöveg (Utcakép gomb).
- **Teszt oldalak és teszt APK-k:** angol útvonal, `utszelveny.hu/test/<ág>/` (eddig `teszt/<ág>/`), a teszt APK-k kiadása `apk-test-<ág>`, a fájlnév `UtSzelveny-test-…apk`.
- **Saját domain:** a weboldal új címe https://utszelveny.hu (a régi https://schafler55.github.io/utszelveny/ cím ide irányít át).
- **Kezdőlap:** új bemutató oldal a weboldal címén, nagy „ÚtSzelvény indítása” gombbal; a webalkalmazás az `app/` alá költözik.
  Az oldal háttere egy kitalált úthálózat (hidak, kereszteződések, kilométerszelvények, mint a térképen), görgetéskor lassabban mozog, mint az oldal.
  A régi címen telepített (kezdőképernyőre tett) webalkalmazás egyenesen az `app/` oldalt nyitja meg.

## [1.2.0] – 2026-11-22
Stabil kiadás; az 1.1.5–1.2.0 változásai együtt.
- **Névjegy:** az ÚtSzelvény logó a név, a © és a forráskód sora mellett, balra.
- **Firefox:** nem támogatott. Androidon a Firefox csak ritkán frissíti a helyadatot, ezért a szelvény nem követi folyamatosan a haladást; Firefoxban a Pozíció oldal tetején megjegyzés jelzi ezt, és a Chrome-ot vagy az Android alkalmazást javasolja (Androidon egy gombbal Chrome-ban nyitható meg).
- **Pozíció, műholdkeresés:** új műhold ikon, a jel a műhold testéből indul (eddig a napelemtábla végéről); a keresést jelző kör egyenletesen forog (eddig másodpercenként újraindult és ugrált), a forgó ív lekerekített végű, és forgás közben nő, majd rövidül.
- **Indítókép:** éles logó (eddig a kis fejléc-logó felnagyítva, ezért homályos volt); a töltést jelző csík feljebb, a név alá került, alatta „Betöltés…” felirattal.
- README: ajánlott böngészők.

## [1.1.4] – 2026-11-22
Stabil kiadás; az 1.1.2–1.1.4 változásai együtt.
- **Sebességkorlát kártya:** a GNSS szerinti sebesség a kártya jobb felső sarkába került, buborékban, mint a fő kártyán a jelerősség (a szám félkövér, a „km/h” nem). Túllépésnél a kártya címével együtt narancssárga, illetve piros lesz. A GNSS kártya alsó sorában csak a frissítés ideje maradt.
- **Térkép:** új kapcsoló a 0 km-es szelvényekhez (Beállítások → Térkép → Rétegek → „0 km-es szelvények elrejtése”, a kilométerszelvények nagyítás-csúszkája alatt); alapból rejtve vannak.
- **GNSS mérés:** a mérés ideje a bal felső sarokból a megtett út fölé került, középre.
- **Indítási tájékoztató:** új „Kilépés” gomb bal oldalt (a zöld „Elfogadom” jobb oldalt marad), ha valaki nem fogadja el a használat feltételeit; világos témában halvány piros háttérrel és piros kerettel. Az Android alkalmazás bezárul; a weboldal bezárja a lapot, ha a böngésző engedi, különben jelzi, hogy a lap bezárható. Semmi nem mentődik, a GNSS nem indul el, és a tájékoztató a következő indításkor újra megjelenik.
- Névjegy → Támogatás: kis szövegmódosítás („a munkámat és a további fejlesztést”, az ÚtSzelvény név félkövér).
- README: új Pozíció kép – 42 Báránd, M0 kézi útválasztással több út közül, 2514 Emőd híd- és tehergépjármű-korlátozással.

## [1.1.1] – 2026-11-22
Stabil kiadás.
- **Névjegy:** új „Támogatás” csoport rövid szöveggel és egy „Támogatás Revoluttal” gombbal (revolut.me/schafler55). A támogatás önkéntes, nem jár érte extra funkció. Az Adatvédelem szöveg megemlíti, hogy a gomb a Revolut oldalát nyitja meg.
- README: „Támogatás” szakasz; a GitHub oldalon „Sponsor” gomb (`.github/FUNDING.yml`).

## [1.1.0] – 2026-11-22 · [#20](https://github.com/schafler55/utszelveny/pull/20)
Stabil kiadás.
- **Frissítések:** indításkor az alkalmazás megnézi, megjelent-e új stabil verzió, és ha igen, egyszer megkérdezi: Frissítés / Később (Android: Kihagyom ezt a verziót is). A webalkalmazás a „Frissítés” gombra azonnal betölti az új verziót, a „Később” után a következő indításkor. Az Android alkalmazás megnyitja az új APK letöltését, amely a meglévőre telepíthető. A mentett adatok és a beállítások megmaradnak. Kapcsoló: Beállítások → Általános → Frissítések; kézi ellenőrzés és állapot a Névjegyben. Frissítés után egy rövid üzenet jelzi az új verziót.
- **Weboldal:** a https://schafler55.github.io/utszelveny/ cím mostantól a legutóbbi stabil kiadást mutatja (az APK-val azonos verzió), és egy új kiadás közzétételekor frissül. A `main` ág fejlesztői állapota a https://schafler55.github.io/utszelveny/dev/ címen érhető el, saját mentett adatokkal; a szövegek áttekintője is ide került (`dev/szovegek.html`).
- **Adatvédelem:** a Névjegy és a README megemlíti, hogy a frissítések keresésekor a GitHub látja az IP-címet.
- **Beállítások:** új elrendezés – minden fül csoportokba rendezve, zöld csoportcímekkel és kártyákkal; a „Kerékpárutak a térképen” a Térkép → Rétegek csoportba került; a fejlécben a logó, a név és a verzió a Névjegyet nyitja meg; egyforma csúszka-értékek; az „Indítási tájékoztató” gomb megszűnt (az első indításkor továbbra is megjelenik).
- **Új alapértékek:** téma Rendszer, aktuális út kiemelése Nincs, vonalvastagság ×1,5, kilométerszelvények a 15-ös nagyítástól, fotó koordináták Mindkettő, fotó minőség Gyors.
- **Fotó néző és törlés:** a fotók lapozhatók, mint egy galériában; a fájlnév és a gombok között színes buborék mutatja az állapotot: zöld „Mentve telefonra” vagy piros „Nincs még mentve” (felül csak a sorszám marad). A Fotó oldalon a galéria ikon közelebb került az exponáló gombhoz, és amíg van mentetlen fotó, piros „NINCS MENTVE” felirat látszik alatta. Törlés mindenhol egyformán: az első érintés pirosra váltja a gombot, a második 3 másodpercen belül töröl.
- **Sebességkorlát kártya:** ha a GNSS szerinti sebesség legalább 5 km/h-val a korlát fölött van, a kártya narancssárga, legalább 10 km/h-val fölötte piros lesz (ismeretlen haladási iránynál a két korlát közül a nagyobbhoz mérve)). Kapcsoló: Beállítások → Pozíció → Sebességkorlát → Túllépés jelzése színnel (alapból be).
- **Fotó néző:** lapozás után a gombok azonnal reagálnak: a már látott kép nem töltődik be újra, a következő kép a háttérben készül elő.
- **Indítási tájékoztató és Névjegy:** új licencmondat („Az alkalmazás GPL-3.0 licenc alapján, csak saját felelősségre használható!”, a második fele félkövér), egységes adatvédelmi szöveg (a tájékoztató a frissítések keresését is említi; az Android biztonsági mentésről szóló mondat kikerült), a vezetési figyelmeztetés a Névjegyben is félkövér. Mivel a tájékoztató szövege változott, frissítés után mindenkinek egyszer újra megjelenik.
- Szövegek: „Hidak / Kilométerszelvények megjelenítése a térképen”; a műholdkép rövidebb forrásmegjelölése a térképen (a Névjegyben marad a „Powered by Esri”).

## [1.0.3] – 2026-11-21
- Android: a CSV-exportok közvetlenül a Letöltések mappába kerülnek (nem a Letöltések / ÚtSzelvény almappába).
- Fotó beállítások: a „DCIM / Camera” mappa megszűnt; aki ezt választotta, annak a fotói ismét a Képek / ÚtSzelvény mappába kerülnek.

## [1.0.2] – 2026-11-21
- Szövegek: 38 felirat és magyarázat átfogalmazva, rövidítve (gondolatjelek helyett mondatok, felesleges részletek nélkül).
- Pozíció, GNSS kártya: a rendszer neve és a műholdszám között szóköz van („GPS 2/6”, „Galileo 8/9”).

## [1.0.1] – 2026-11-21
Stabil kiadás.
- Térkép: a kilométerszelvények és a km-számok ugyanattól a nagyítástól jelennek meg és tűnnek el. A Beállítások → Térkép oldalon a „Km-számok ettől a nagyítástól” csúszka megszűnt, a „Kilométerszelvények ettől a nagyítástól” csúszka állítja mindkettőt.

## [1.0] – 2026-11-21 · [#18](https://github.com/schafler55/utszelveny/pull/18)
Első stabil kiadás.
- **Indítási tájékoztató:** az első indításkor egy ablak jelenik meg (az adatok tájékoztató jellegűek, nem hitelesek; vezetés közben ne kezeld; helyadat-használat; GPL-3.0, garancia nélkül). A GNSS csak az „Elfogadom” után indul, így a helyengedély kérése a magyarázat után jön. A Névjegyben az „Indítási tájékoztató” gombbal újra megnézhető.
- **Adatvédelem:** új szakasz a Névjegyben és a README-ben: mi marad a készüléken, és mit látnak a térképszolgáltatók.
- **Térkép:** a műholdkép forrásmegjelölése „Powered by Esri · © Esri, Maxar, Earthstar Geographics, GIS User Community” (az Esri előírása szerint). Az Android alkalmazás a térképcsempék kérésekor azonosítja magát (`UtSzelveny/1.0` a projekt címével), ahogy az OpenStreetMap csempeszabályzata előírja.
- **Android:** az APK a V1.0-tól saját, titkos kulccsal aláírt kiadási (release) változat; a nyilvános debug kulcs kikerült a tárolóból. **A béta APK-t a V1.0 telepítése előtt el kell távolítani**, ezzel a mentett mérések és keresések is törlődnek, ezért előtte érdemes CSV-be menteni őket.
- **Kiadás:** egy `v*` címke (pl. `v1.0`) stabil GitHub kiadást készít az APK-val; a README letöltési linkje (`releases/latest`) erre mutat. Az `apk-latest` továbbra is a `main` ág legfrissebb állapota.
- Verzió mindenhol V1.0 (a „Beta” jelzés megszűnt), versionCode 100.

## [0.25.1] – 2026-11-21
- Térkép alapréteg választó (Beállítások → Térkép és a térkép panel): a négy előnézeti kép valódi térképrészlet ugyanarról a helyről (Báránd, 42-es főút és 4801-es út): Világos és Sötét az OpenStreetMap csempéiből, ugyanazzal a színszűrővel, mint a térkép; Műhold az Esri műholdképből; Ki csak az utakkal. Az utak a térkép színeivel (Műholdon sötét szegéllyel). A képek az alkalmazásba vannak építve (WebP, összesen ~48 KB, nagyjából annyi, mint a korábbi rajzok), offline is látszanak.
- README: új képernyőképek a V0.25-ből, a Pixel 7 Pro kijelzőjével megegyező méretben, valódi térkép-alapréteggel, és valódi, az alkalmazással készült fotók.

## [0.25] – 2026-11-21
- Fejlesztés: az alkalmazás összes szövege (címek, magyarázatok, gombfeliratok, üzenetek, hibaüzenetek, a fotó felirata, CSV-oszlopnevek, képernyőolvasó-címkék; 613 szöveg) egy helyre került: az `index.html` elején lévő szövegblokkba (`id="texts"`), képernyők szerint csoportosítva. A felület nem változott.
- Új oldal: **szovegek.html** – az összes szöveg képernyőnként, kereséssel; a szövegek ott átírhatók, a változások kimásolhatók vagy a módosított `index.html` letölthető.
- Tehergépjármű- és súlykorlátozó táblák a KRESZ táblák pontos másolataként (C-007, C-008, C-009, C-010, C-011, C-012, C-023, C-024; zóna: E-030): valósághű tehergépkocsi, pótkocsis szerelvény, tengely és narancs tábla; a szám egész része nagy, a tizedes és a „t” kisebb. A kerek táblák kerete a sebességkorlátozó tábláéval azonos.
- Csúszkák (Beállítások → Térkép és a térkép panel): csak a pöttyel állíthatók. A csúszka vonalára koppintás vagy onnan indított görgetés már nem változtatja meg az értéket, csak görget; a pötty érintési területe nagyobb lett.
- Ha a szövegblokk hibás (pl. hiányzó vessző), az alkalmazás akkor is elindul: a szövegek helyén a kulcsok látszanak, felül piros sor jelzi a hibát. A build (`tools/szovegek.py`) ellenőrzi a blokkot.

## [0.24] – 2026-11-21
- Keresés: új választó a Pont / Szakasz fölött: **Útszám / Koordináta**. Koordináta módban WGS84 („47.13285 19.41772”, vesszővel, É/K-val, fokkal, fok-perc(-mp) alakban is) vagy EOV („EOV 678089 198812”, „Y 678 089 X 198 812”) koordináta adható meg; a mező alatt látszik, mit ismert fel (a másik rendszerben is) és a legközelebbi út szelvénye a távolsággal. A „Saját” gomb a GNSS-pozíciót írja be. Szakasznál két koordináta: ha a két pont ugyanarra az útra esik, az út szakasza (mint az útszámos keresésnél); ha más-más útra, a térképi méréshez hasonlóan a legrövidebb útvonal az országos közúthálózaton, utanként a kezdő – záró szelvénnyel és hosszal („Több úton: 5, 52108”).
- A koordinátás keresések **limezöld** színűek a térképen (szakasz vonal, gombostű, a megadott pont célkereszttel és szaggatott vonallal az út pontjához), a mentett kártyán („Koordináta” / „Koord. szakasz”) és a buborékban; a részletekben a megadott koordináta és a távolság az úttól. CSV-ben a Megjegyzés oszlopban.
- Minden koordináta (GNSS kártya, térképi buborék, Adatok → Helyzet, utolsó ismert pozíció, mérések és keresések részletei) **hosszú nyomással vágólapra másolható**; értesítés: „WGS84 koordináta másolva” / „EOV koordináta másolva”. Csak a számok kerülnek a vágólapra (pl. „47.13285 19.41772”, „678089 198812”). Android: natív vágólap (`copyText`).
- Térkép: a kilométerszelvény nemcsak pont az úton, hanem egy rövid vonalka is az út mellé, a végén a km-számmal. Osztott pályán mindkét pálya kifelé mutat (egymástól el), osztatlan úton jobbra, kivéve ha 30 m-en belül egy másik út fut azon az oldalon.
- Új ikon a saját pozícióhoz: navigációs nyíl a térkép Követés gombján és a Keresés „Saját” gombján (zöld); a célkereszt csak a koordinátát jelöli (limezöld).
- Térkép: ahol egy országos út hídon halad át egy másik felett (pl. M1 az M7 felett), a híd felett haladó út a híd jelölése fölé rajzolódik; a keresett szakasz és a mérés vonala a hídon haladó úton a híd felett is látszik.
- Mérések színe: a GNSS mérés rózsaszín, a térképi mérés lila (a térképen, a kártyákon, a buborékban és a térképi mérés pontjain); a futó GNSS mérés továbbra is narancs.
- Fejlesztés: a kód megjegyzései angolul, az index.html elején angol szójegyzék a magyar szakkifejezésekhez (szelvény, pálya, átkelési szakasz…); a felület magyar marad.
- Beállítások → Térkép: „Kilométerszelvények a térképen” kapcsoló, „Kilométerszelvények ettől a nagyítástól” csúszka (11–18, alapból 14, mint eddig) és külön „Km-számok ettől a nagyítástól” csúszka (alapból 15); a km-szám csak ott látszik, ahol a szelvényjel is.

## [0.23.6] – 2026-11-20
- Tehergépjármű- és súlykorlátozások kártya (Pozíció oldal és Adatok) a hídkártyával azonos elrendezésben: balra a táblák (új, fehér szegélyes, keskeny számú kivitel, mint a sebességkártyán) és alattuk a távolság („120 m”, „itt”), jobbra korlátozásonként félkövér piros felirat az értékkel piros chipben (pl. „Össztömeg-korlátozás [7,5 t]”), alatta a kivétel, majd a szelvénytartomány („még 400 m”, ha benne vagy).
- A tehergépkocsi össztömeg-korlátozása röviden „Össztömeg-korlátozás” (a tábla mutatja, hogy tehergépkocsira vonatkozik).

## [0.23.5] – 2026-11-20
- Térkép alapréteg választó: valósághű előnézeti képek (kisváros utcákkal, házakkal, folyóval, erdővel és szántóval; a Világos és a Sötét kép ugyanazzal a színszűrővel készül, mint a valódi térképréteg, a Műhold légifotó-szerű). A „Szürke” réteg neve „Világos”.

## [0.23.4] – 2026-11-20
- Térképi buborék: a WGS84 és az EOV koordináta egy sorban; a kezelő (pl. MKIF) nem jelenik meg benne; a „Részletek” gomb neve „Adatok”.
- A hidak alapból már a 14-es nagyítástól látszanak a térképen (eddig 15; a csúszkán beállított érték megmarad).

## [0.23.3] – 2026-11-20
- Javítás: böngészőben az Utcakép gomb az ÚtSzelvény lapját is átvitte a Google Térképre; most csak új lapon nyílik meg, az ÚtSzelvény a helyén marad.
- Térképi buborék: rövidebb gombok, az ikon a felirat mellett; „Pont mentése” helyett „Mentés”.

## [0.23.2] – 2026-11-20
- Térkép: a koppintott pont buborékában új középső gomb, **Utcakép**: megnyitja a Google Utcaképet a pontnál, az út menetirányába nézve (bal pályán az ellenkező irányba). Az Android alkalmazásban a Google Térkép alkalmazásban, böngészőben új lapon nyílik meg. A három gomb ikonja a felirat fölé került, hogy kiférjenek.

## [0.23.1] – 2026-11-20
- Sebességkártya: kisebb helységnévtábla; a sebességkorlátozó táblának vékony fehér szegélye van (halvány körvonallal, hogy világos témán is látsszon), a számok keskenyebbek, mint az útszámtáblákon. A „KRESZ alapérték” / „Egyedi korlátozás” félkövér.
- Térkép, sötét alapréteg: a kerékpárutak a műholdképhez hasonló világos sárga színnel látszanak (eddig barna).
- Beállítások → Általános: új kapcsoló „Kerékpárutak a térképen”. Kikapcsolva a kerékpárutak és a rajtuk lévő hidak nem látszanak a térképen, és koppintással sem választhatók.
- Szakasz adatai → Forgalom: sorrend Egységjármű, Összes jármű, Nehéz motoros, Számlálóállomás.

## [0.23] – 2026-11-20
- Új NAP adat: Közúti azonosítópontok (17 114 pont – csomópontok, útvégek és más hálózati pontok hivatalos kóddal, pl. „C020001”). Beépítése: `tools/nap_azonositopontok.py`.
- Szakasz adatai: ha a koppintás egy azonosítópont közelében van, új „Azonosítópont” szakasz mutatja a kódot, a távolságot, és az ott találkozó összes utat útszám-táblával, mindegyiket a saját szelvényével (JOBB / BAL chippel osztott pályán) és nevével.

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
