# Változásnapló

Az ÚtSzelvény változásai, a legújabb elöl. A dátumok UTC szerint értendők.
A nagyobb funkciók saját ágon (branch) készülnek teszt oldallal és teszt APK-val, és pull requestként (#) kerülnek a `main` ágba;
a kisebb javítások közvetlenül a `main`-re kerülnek.

**Verziószámok:** a V1.3.0 óta minden módosítás saját, négytagú verziószámot kap (V1.3.0.1, V1.3.0.2 …), így minden
letöltött alkalmazásról megállapítható, pontosan melyik változat. A harmadik szám csak külön döntésre változik
(pl. V1.3.1.0). A stabil kiadás a második számot növeli, és a neve háromtagú (pl. V1.4.0).
A még ki nem adott kis verziók ebben a naplóban külön szakaszokban állnak („kiadatlan”); a stabil kiadáskor egyetlen
szakaszba olvadnak össze, amely a kiadás összes változását felsorolja. A ténylegesen kiadott változatokat
„Stabil kiadás” jelöli. A V1.3.0 előtti bejegyzések utólag ugyanígy lettek összevonva: a közbenső kis verziók
(pl. 0.16.1–0.16.10) változásai a következő nagyobb verzió (pl. 0.17) szakaszában szerepelnek; a szakasz első sora
jelzi, mely változatokat tartalmazza.

## [1.3.1.2] – 2026-11-26 · kiadatlan
- **Térkép, átkelési szakaszok:** Z8-as és annál kisebb nagyításnál (ahogy a méretarány-sáv mutatja) a piros sáv nem jelenik meg, akkor sem, ha a kapcsoló be van kapcsolva; Z9-től látszik.
- **Névjegy → Frissítések:** az „Ellenőrizve:” és a dátum külön sorba került a „Naprakész” alá.

## [1.3.1.1] – 2026-11-26 · kiadatlan
- **Frissítéskeresés a fejlesztői változatban:** a https://utszelveny.hu/dev/ oldal és az „ÚtSzelvény DEV” APK mostantól ugyanúgy szól, ha új verzió érhető el, mint a stabil kiadás, csak a `main` ág új verzióit figyeli: a dev oldal a „Frissítés” gombra azonnal betölti az új változatot, a DEV alkalmazás megnyitja az új DEV APK letöltését (`apk-latest`), amely a meglévő DEV alkalmazásra települ. Az „Újdonságok” a `main` változásnaplóját nyitja meg. A DEV alkalmazás legfeljebb óránként kérdezi a GitHubot (a stabil naponta egyszer), a dev oldal minden indításkor a saját szerverét. Kapcsoló és kézi ellenőrzés ugyanott: Beállítások → Általános → Frissítések, Névjegy → Frissítések. A teszt ágak oldalain és teszt APK-iban továbbra sincs frissítéskeresés.
- A DEV alkalmazás csak ettől a változattól kezdve keres frissítést: a V1.3.1.1 DEV APK-t egyszer még kézzel kell telepíteni.

## [1.3.1.0] – 2026-11-26 · kiadatlan
- **Térkép, átkelési szakaszok:** új kapcsoló a Beállítások → Térkép → Utak csoportban, az „Utak vonalvastagsága” után: „Átkelési szakaszok a térképen”. Bekapcsolva a térkép halvány piros sávval jelöli az utak vonala alatt azokat a szakaszokat, ahol az út lakott területen halad át (NAP adat, ugyanaz, amelyből a sebességkorlát-kártya az átkelési szakaszt és a településtáblát mutatja). Kisebb nagyításnál a sáv fele olyan széles, hogy ne legyen túl feltűnő. A kerékpárutakon nincs jelölés. Alapból kikapcsolva; új adatot nem igényel, az alkalmazás mérete nem nő.

## [1.3.0.1] – 2026-11-26 · kiadatlan
- **Frissítés, „Újdonságok”:** az új verzióról szóló ablakban az „Újdonságok” hivatkozás mostantól a változásnaplót nyitja meg (az adott kiadás szerinti állapotában, így az új verzió változásai állnak legfelül), nem a GitHub kiadási oldalát. Azoknál lép életbe, akik már ezt a változatot használják: a V1.3.0 a következő stabil kiadásnál még a kiadási oldalt nyitja meg.
- **Verziószámok:** minden módosítás saját, négytagú verziószámot kap (részletek a napló elején). Az Android belső verziókódja (versionCode) mostantól verziótagonként két számjegy (V1.3.0.1 → 1030001; eddig tagonként egy, V1.3.0 → 1300), így egy tag 99-ig mehet. Az új kódok mind nagyobbak a korábbiaknál, a frissítés ugyanúgy települ. A `tools/verzio.py` a README verziósorát is ellenőrzi és átírja.

## [1.3.0] – 2026-11-26
Stabil kiadás; az 1.2.0 óta a `main` ágra került változások együtt (a `main` ágon eddig V1.2.1 és V1.2.2 néven).
- **Android build, az aláíró kulcs ellenőrzése:** aláírás után a build ellenőrzi, hogy az APK-t a várt tanúsítvány írta-e alá (stabil kiadásnál az eddigi stabil kiadásoké, DEV buildnél a DEV kulcsé). Eltérő kulcsnál a futás hibával leáll, és semmi nem kerül közzétételre, így nem jelenhet meg olyan stabil APK, amely nem telepíthető a már telepített alkalmazásra.
- **Alsó menü keskeny kijelzőn / nagy betűmérettel:** a menü eddig rögzített méretű volt (kb. 390 képpont széles kijelző kellett hozzá), ezért keskenyebb telefonon, illetve nagyra állított Android „Megjelenítési méret” vagy betűméret mellett az utolsó gomb (Fotó) részben vagy teljesen kilógott, és a Fotó oldalt nem lehetett megnyitni. Mostantól a menü mindig elfér: ha szűk a hely, először a gombok közti távolság csökken, ha így sem fér ki, a kiválasztott oldal neve nem jelenik meg, csak az ikonok. Széles kijelzőn (pl. Pixel 7 Pro) nincs változás.
- **Fotó, sebesség:** a kép JPEG-kódolása külön háttérszálon (worker) fut. Eddig a böngészőmotor az oldal „üresjáratára” várt vele, ami az Android alkalmazásban kiszámíthatatlanul jön: a fotó hol azonnal, hol csak másodpercek múlva készült el („Gyors” és „Legjobb” minőségnél is). A mentés külön sorban megy, így egy lassabb mentés nem tartja fel a következő fotó feldolgozását.
- **Keresés, alapértelmezett név:** osztott pályás úton a mentett keresés neve a pálya betűjelével végződik, zárójel nélkül: „M1 · 12+000 J” vagy „… B” (eddig „(jobb)” / „(bal)”). A korábban mentett, át nem nevezett keresések neve is átáll.
- **Térkép, koppintott pont mentése:** a koppintott útpont buborékjában a „Mentés” már nem vált át a Keresés oldalra: a pont a térképen marad, kiválasztva, a saját buborékjával (Elrejtés / Törlés / Részletek). A Keresés oldali kártyája a „Részletek” gombbal nyílik meg.
- **Koppintás gyors húzás után (képnézegető, térkép):** egy gyors lapozás vagy térképhúzás után az első koppintás (pl. a nézegető alsó gombjain vagy a térkép gombjain) akár egy másodpercig sem reagált: a böngésző a lendületes húzás „megállításának” vette, és elnyelte. Most azonnal reagál.
- **Fotó, képnézegető:** a nézegető és a bélyegkép a nagy fotók képernyő méretű másolatát mutatja (a mentett kép továbbra is a teljes felbontású), így lapozáskor nem a teljes, 12 megapixeles kép töltődik be.
- **Mérés, gombok:** mérés közben a „Pont rögzítése” és a „Leállítás” gomb nem nyel el koppintást. Eddig a kártya másodpercenként újrarajzolódott, és ha ez épp a koppintás közben történt, a koppintás elveszett (hosszabb nyomásnál mindig).
- **Pozíció, ⇄ útválasztó:** a közeli utak gombjai menet közben is biztosan reagálnak (a szelvény változásakor eddig újrarajzolódtak, és a koppintás elveszhetett).
- **Fotó:** 40 fotó felett sem vész el mentetlen kép: a listából csak a már mentett, legrégebbi fotók kerülnek ki. Ha a mentetlen fotók száma 40 fölé nő, az üzenet szól, hogy mentsd őket.
- **Mentés, megtelt tárhely:** ha a méréseket, kereséseket vagy beállításokat nem sikerül menteni (megtelt az alkalmazás tárhelye), piros üzenet jelez; eddig a hiba csendben elveszett, és újraindítás után hiányzott az adat.
- **Térkép, régebbi telefonok:** iOS 15-ön és régi Android WebView-ban a térkép nem áll le a korlátozott hidaknál és a buszmegállóknál (egy újabb rajzolófüggvény hiányzott ezekből a böngészőkből).
- **GNSS indításkor:** ha kikapcsolod a GNSS-t, a következő indításkor is kikapcsolva marad (eddig bekapcsolt, ha a helyadat engedélyezve volt). A letiltott helyadat már nem jegyződik meg kikapcsolásként: engedélyezése után a következő indításkor a GNSS magától elindul.
- **HUD, sebességtúllépés:** ugyanaz a jelzés, mint a Pozíció kártyán: 5 km/h túllépéstől narancssárga, 10 km/h-tól piros a sebesség, és a „Túllépés jelzése színnel” kapcsoló a HUD-ra is vonatkozik (eddig 3 km/h-tól, kapcsoló nélkül).
- **Firefox figyelmeztetés:** a „Megértettem” gombbal bezárható, és utána ebben a böngészőben nem jelenik meg újra.
- **Android, hozzávetőleges helyadat:** ha az alkalmazás csak hozzávetőleges helyet kap (Android 12-től választható), a Pozíció oldal tetején figyelmeztetés jelenik meg „Pontos hely engedélyezése” és „Megértettem” gombbal.
- **Szövegek:** az Android alkalmazás üzenetei (mentési hibák, mappaválasztó, megosztás) és néhány eddig a kódba írt szöveg (pl. „mp / perc / óra”, „offline”) is a szövegek blokkjába került, a szovegek.html-ben szerkeszthető.
- **Fejlesztés:** `tools/verzio.py` – a verziószám minden helyen egyezik-e (és egy paranccsal mindenhol átírható); a stabil kiadás címkéjét is ellenőrzi. Új „Checks” munkafolyamat minden feltöltéskor: szövegek, verziószámok és böngészős füstteszt (`tools/smoke_test.py`). Az APK-építés egy újabb feltöltésnél leállítja a még futó régit, és csak dokumentációt érintő feltöltésnél nem épül APK és weboldal. Takarítás: a régi térképbeállító panel és néhány nem használt függvény törölve, az SVG ikonok dupla attribútumai javítva, a buszmegálló-jelek gyorsabb rajzolása (ugyanúgy néznek ki).
- **Fotó, mentés helye (Android):** az alapértelmezett mappa mostantól a DCIM / ÚtSzelvény (a kamera mappája mellett), és ez áll a lista elején; a Képek / ÚtSzelvény a második, az egyéni mappa választása megmaradt. Aki már módosított valamit a beállításokban, annál a korábbi választás (Képek / ÚtSzelvény) marad, egy koppintással átállítható.
- **Térkép → Részletek → Vissza:** ha a térképi buborék „Részletek” gombja nyitja meg a Mérés vagy a Keresés oldalt, a Vissza (Android vissza gomb, böngésző vissza, Esc) a térképre visz vissza, nyitva hagyott buborékkal, nem a Pozíció oldalra.
- **Térkép, keresések:** kiválasztás nélkül a keresések csak a vonalukat (szakasz) vagy a tűjüket (pont) és a címkéjüket mutatják; a kezdő- és végpont (K, V), a másik pálya pontja, valamint a koordinátás keresés célkeresztje és szaggatott vonala az útig csak a kiválasztott keresésnél (a címkére koppintva, nyitott buborékkal) látszik.
- **Térkép, mentett mérések:** a pontok (K, P1, P2…, V) csak a kiválasztott (megnyitott buborékú) mérésnél és a folyamatban lévő mérésnél látszanak; a többi mentett mérésnél csak a színes vonal és a címke.
- **Adatfrissítés egy lépésben (`tools/adat/`):** az úthálózati adatokat (út- és szakaszadatok, szelvényezés, sebességkorlátozás, lakott területi szakaszok és településnevek, hidak, tehergépjármű-korlátozások, sávok, burkolat, forgalom, azonosítópontok, egyirányú útpályák, buszmegállók) mostantól egyetlen program állítja elő a NAP-ból letöltött 13 fájlból, ellenőrzésekkel (hiányos letöltés, ismeretlen kód vagy útszám, hirtelen adatvesztés esetén leáll) és összehasonlító jelentéssel; a korábbi három importáló program beleolvadt. Az első futás a jelenlegi adatokat állította elő újra (a NAP adatai november 16. óta nem változtak); 20 000 véletlen helyen próbálva 2 helyen tér el a szelvény (9 m és 3 m), 1 helyen a településnév; egy szelvényjel nélküli kerékpárúton (95001) a km-szelvény legfeljebb 43 m-rel máshová esik. **Névjegy:** az adatállapot napra pontosan, az adatokból („2026. november 24.”).
- **Térkép, saját sebesség:** menet közben a bal alsó sebességkorlát-tábla fölött egy kis körben a GNSS szerinti sebesség (csak a szám), a táblával egy függőleges vonalban, kissé a tábla mögé csúsztatva; 5 km/h túllépéstől narancssárga, 10 km/h-tól piros, mint a Pozíció oldal sebességkorlát kártyáján (Beállítások → Pozíció → Sebességkorlát kapcsoló). A Térkép → Nézet kapcsoló neve „Sebességkorlát, helységnévtábla, sebesség”.
- **Térkép, pont illesztése az útra:** koppintáskor és a térképi mérés pontjainál a pont az ujjad melletti legközelebbi útra kerül (kb. 40 képpontos körzetben, nagyítástól függetlenül), így nem kell pontosan az út vonalát eltalálni. Csak a térképen az adott nagyításon látható utak közül választ: kicsinyített térképen, ahol csak a főutak látszanak, a pont nem kerül egy közelebbi, de nem látható 4–5 számjegyű útra (ez kikapcsolt illesztésnél is így van). A jelölő, a koordináták, az Utcakép és a Szakasz adatai is az út pontját használják. Eddig közepes nagyításon csak néhány képpontra az úttól lehetett koppintani. Kapcsoló: Beállítások → Térkép → Koppintás → „Pont illesztése a legközelebbi útra” (alapból be; kikapcsolva a korábbi működés).
- **ÚtSzelvény DEV ikon:** a `main` ág és a teszt ágak APK-ja (ÚtSzelvény DEV) saját ikont kapott: piros keret, a KM tábla helyén „DEV” felirat, így a telefonon könnyű megkülönböztetni a rendes alkalmazástól (`android/app/src/dev/res/`). A stabil kiadás ikonja nem változik.
- **CSV export, ékezetek:** a Google Táblázatok (Sheets) Androidon eddig nyugat-európai kódolásúnak nézte a mentett CSV fájlt, ezért az ékezetes betűk elromlottak („NÃ©v”). A fájl elején mostantól egy láthatatlan jel is van, amiből a Táblázatok is felismeri az UTF-8 kódolást; az Excel ugyanúgy jól olvassa. A vágólapra másolt szövegben ezek a jelek nincsenek benne.
- **Biztonság (biztonsági audit, L3–L5, L7, I1–I3, I5):** a webalkalmazás tartalombiztonsági szabályt (Content Security Policy) kapott: az oldal csak a saját címéről, a két térképszerverről (OpenStreetMap, Esri) és a GitHub frissítéskereséséről tölthet be vagy kérdezhet le bármit, így egy esetleges jövőbeli hiba sem küldhetne el adatot máshová. A frissítéskeresés csak az ÚtSzelvény GitHub oldalára mutató linket fogad el. Az Android alkalmazás a helyadatot csak a saját oldalának adja (mint a kamerát), és egy megnyithatatlan link sem zárja be. A CSV exportban az =, +, -, @ jellel kezdődő neveket aposztróf előzi meg, hogy az Excel ne képletként futtassa (a számok, pl. „-12”, számok maradnak). A szövegszerkesztő (szovegek.html) a letöltött szövegblokkban nem hagy lezáró script címkét, ami elronthatná az alkalmazást. A teszt oldalak csak betűt, számot és . _ - jelet tartalmazó nevű ágakból készülnek. Új SECURITY.md (magyarul és angolul): hol lehet zártan jelezni biztonsági hibát.
- **Android, adatvédelem (biztonsági audit, L2):** az alkalmazás adatai (mentett mérések, keresések, beállítások) nem kerülnek bele a telefon Google biztonsági mentésébe, és telefoncserénél sem költöznek át az új készülékre (`android:allowBackup="false"`, `res/xml/data_extraction_rules.xml`), így az Adatvédelem szöveg („csak a készüléken tárolódnak”) az Android alkalmazásra is pontos. Telefoncsere vagy újratelepítés előtt a mérések CSV exporttal menthetők ki.
- **Android build, biztonság (biztonsági audit, M1):** a kiadási aláírókulcs csak a stabil kiadásokhoz (`V*` címke) kerül elő, egy külön, védett GitHub környezetből (`release`, a tulajdonos jóváhagyásával); a Gradle build és a külső GitHub Actions már nem látják a kulcsot (aláíratlan APK, külön aláíró lépés: `.github/scripts/sign-apk.sh`). A `main` ág (`apk-latest`) és a teszt ágak APK-ja mostantól külön alkalmazás, „ÚtSzelvény DEV” (`hu.szaszi.kozutszelveny.dev`): a rendes mellé települ, saját mentett adatokkal, frissítéskeresés nélkül, „DEV” / „TESZT” címkével, saját fejlesztői kulccsal aláírva. A GitHub Actions lépések a legújabb főverzióra frissítve és teljes commit SHA-ra rögzítve; a Dependabot havonta egy pull requestben javasolja a kisebb (nem főverziós) frissítésüket. A Gradle gyorsítótár a nyílt forráskódú („basic”) változat.
- **Keresés / Mérés beállítások:** a térképes felirat választójában „Útszám, szelvény” (eddig „Útszám, km+m”), a magyarázó szövegek is.
- **Átnevezés:** ha a mentett keresés vagy mérés új nevét üresen hagyod, visszakapja az alapértelmezett nevet: útszám és szelvény (pl. „6 · 162+030”, mérésnél „42 · 13+002 – 15+200”); az úthálózaton kívüli mérés megtartja a nevét.
- **Névjegy:** „Kapcsolat” nagy kezdőbetűvel. **Térkép beállítások:** a buszmegállók kapcsolója és csúszkája a Rétegek csoport végére került.
- **Kezdőlap, APK letöltés:** az „Android alkalmazás (APK) letöltése” link közvetlenül a legutóbbi stabil kiadás APK fájlját tölti le (eddig a kiadások oldalára vitt); minden új stabil kiadásnál magától frissül.
- **Térkép, nagyítási szint:** a bal felső méretarány buborékban a lépték előtt a nagyítási szint is látszik (pl. „Z16 | 50 m”); ugyanez a szám, amihez a hidak, a kilométerszelvények és a buszmegállók csúszkája viszonyít.
- **Buszmegállók a térképen az út mellett:** 15-ös nagyítástól a jel az út azon oldalán áll, ahol a megálló van (jobb / bal oldal a szelvényezés irányában), mint az OpenStreetMapen; az útközépi megállók az úton maradnak. 15 alatt az azonos nevű megálló két oldala egy jel az úton, 14 alatt pedig csak egy kis kék pont fehér alapon.
- **„ITT” felirat:** a hidak, a tehergépjármű-korlátozások, a buszmegállók és az azonosítópont távolságánál az „itt” helyett nagybetűs, félkövér „ITT”.
- **Új NAP adatok: egyirányú útpályák és autóbusz-megállóhelyek** (`tools/nap_egyiranyu_megallok.py`). A Szakasz adatai oldalon az Út részben új sor: „Forgalmi irány” (egyirányú a szelvényezés irányában / azzal szemben, vagy kétirányú); új „Autóbusz-megállóhelyek” rész az út 100 m-en belüli megállóival (név, oldal, szelvény, kiépítés; az azonos nevű megállók egy sorban, a távolság vagy „ITT” a név mellett). A térképen kis buszmegálló jelek; kapcsoló és nagyítási csúszka: Beállítások → Térkép → Rétegek (alapból ki, 16-os nagyítástól).
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
Stabil kiadás; az 1.1.1–1.2.0 változásai együtt (közbenső stabil kiadások: 1.1.1 és 1.1.4).
- **Névjegy:** az ÚtSzelvény logó a név, a © és a forráskód sora mellett, balra.
- **Firefox:** nem támogatott. Androidon a Firefox csak ritkán frissíti a helyadatot, ezért a szelvény nem követi folyamatosan a haladást; Firefoxban a Pozíció oldal tetején megjegyzés jelzi ezt, és a Chrome-ot vagy az Android alkalmazást javasolja (Androidon egy gombbal Chrome-ban nyitható meg).
- **Pozíció, műholdkeresés:** új műhold ikon, a jel a műhold testéből indul (eddig a napelemtábla végéről); a keresést jelző kör egyenletesen forog (eddig másodpercenként újraindult és ugrált), a forgó ív lekerekített végű, és forgás közben nő, majd rövidül.
- **Indítókép:** éles logó (eddig a kis fejléc-logó felnagyítva, ezért homályos volt); a töltést jelző csík feljebb, a név alá került, alatta „Betöltés…” felirattal.
- README: ajánlott böngészők.
- **Sebességkorlát kártya:** a GNSS szerinti sebesség a kártya jobb felső sarkába került, buborékban, mint a fő kártyán a jelerősség (a szám félkövér, a „km/h” nem). Túllépésnél a kártya címével együtt narancssárga, illetve piros lesz. A GNSS kártya alsó sorában csak a frissítés ideje maradt.
- **Térkép:** új kapcsoló a 0 km-es szelvényekhez (Beállítások → Térkép → Rétegek → „0 km-es szelvények elrejtése”, a kilométerszelvények nagyítás-csúszkája alatt); alapból rejtve vannak.
- **GNSS mérés:** a mérés ideje a bal felső sarokból a megtett út fölé került, középre.
- **Indítási tájékoztató:** új „Kilépés” gomb bal oldalt (a zöld „Elfogadom” jobb oldalt marad), ha valaki nem fogadja el a használat feltételeit; világos témában halvány piros háttérrel és piros kerettel. Az Android alkalmazás bezárul; a weboldal bezárja a lapot, ha a böngésző engedi, különben jelzi, hogy a lap bezárható. Semmi nem mentődik, a GNSS nem indul el, és a tájékoztató a következő indításkor újra megjelenik.
- Névjegy → Támogatás: kis szövegmódosítás („a munkámat és a további fejlesztést”, az ÚtSzelvény név félkövér).
- README: új Pozíció kép – 42 Báránd, M0 kézi útválasztással több út közül, 2514 Emőd híd- és tehergépjármű-korlátozással.
- **Névjegy:** új „Támogatás” csoport rövid szöveggel és egy „Támogatás Revoluttal” gombbal (revolut.me/schafler55). A támogatás önkéntes, nem jár érte extra funkció. Az Adatvédelem szöveg megemlíti, hogy a gomb a Revolut oldalát nyitja meg.
- README: „Támogatás” szakasz; a GitHub oldalon „Sponsor” gomb (`.github/FUNDING.yml`).

## [1.1.0] – 2026-11-22 · [#20](https://github.com/schafler55/utszelveny/pull/20)
Stabil kiadás; az 1.0.1–1.1.0 változásai együtt (közbenső stabil kiadás: 1.0.1).
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
- Android: a CSV-exportok közvetlenül a Letöltések mappába kerülnek (nem a Letöltések / ÚtSzelvény almappába).
- Fotó beállítások: a „DCIM / Camera” mappa megszűnt; aki ezt választotta, annak a fotói ismét a Képek / ÚtSzelvény mappába kerülnek.
- Szövegek: 38 felirat és magyarázat átfogalmazva, rövidítve (gondolatjelek helyett mondatok, felesleges részletek nélkül).
- Pozíció, GNSS kártya: a rendszer neve és a műholdszám között szóköz van („GPS 2/6”, „Galileo 8/9”).
- Térkép: a kilométerszelvények és a km-számok ugyanattól a nagyítástól jelennek meg és tűnnek el. A Beállítások → Térkép oldalon a „Km-számok ettől a nagyítástól” csúszka megszűnt, a „Kilométerszelvények ettől a nagyítástól” csúszka állítja mindkettőt.

## [1.0] – 2026-11-21 · [#18](https://github.com/schafler55/utszelveny/pull/18)
Első stabil kiadás; a 0.25.1 változásaival együtt.
- **Indítási tájékoztató:** az első indításkor egy ablak jelenik meg (az adatok tájékoztató jellegűek, nem hitelesek; vezetés közben ne kezeld; helyadat-használat; GPL-3.0, garancia nélkül). A GNSS csak az „Elfogadom” után indul, így a helyengedély kérése a magyarázat után jön. A Névjegyben az „Indítási tájékoztató” gombbal újra megnézhető.
- **Adatvédelem:** új szakasz a Névjegyben és a README-ben: mi marad a készüléken, és mit látnak a térképszolgáltatók.
- **Térkép:** a műholdkép forrásmegjelölése „Powered by Esri · © Esri, Maxar, Earthstar Geographics, GIS User Community” (az Esri előírása szerint). Az Android alkalmazás a térképcsempék kérésekor azonosítja magát (`UtSzelveny/1.0` a projekt címével), ahogy az OpenStreetMap csempeszabályzata előírja.
- **Android:** az APK a V1.0-tól saját, titkos kulccsal aláírt kiadási (release) változat; a nyilvános debug kulcs kikerült a tárolóból. **A béta APK-t a V1.0 telepítése előtt el kell távolítani**, ezzel a mentett mérések és keresések is törlődnek, ezért előtte érdemes CSV-be menteni őket.
- **Kiadás:** egy `v*` címke (pl. `v1.0`) stabil GitHub kiadást készít az APK-val; a README letöltési linkje (`releases/latest`) erre mutat. Az `apk-latest` továbbra is a `main` ág legfrissebb állapota.
- Verzió mindenhol V1.0 (a „Beta” jelzés megszűnt), versionCode 100.
- Térkép alapréteg választó (Beállítások → Térkép és a térkép panel): a négy előnézeti kép valódi térképrészlet ugyanarról a helyről (Báránd, 42-es főút és 4801-es út): Világos és Sötét az OpenStreetMap csempéiből, ugyanazzal a színszűrővel, mint a térkép; Műhold az Esri műholdképből; Ki csak az utakkal. Az utak a térkép színeivel (Műholdon sötét szegéllyel). A képek az alkalmazásba vannak építve (WebP, összesen ~48 KB, nagyjából annyi, mint a korábbi rajzok), offline is látszanak.
- README: új képernyőképek a V0.25-ből, a Pixel 7 Pro kijelzőjével megegyező méretben, valódi térkép-alapréteggel, és valódi, az alkalmazással készült fotók.

## [0.25] – 2026-11-21
- Fejlesztés: az alkalmazás összes szövege (címek, magyarázatok, gombfeliratok, üzenetek, hibaüzenetek, a fotó felirata, CSV-oszlopnevek, képernyőolvasó-címkék; 613 szöveg) egy helyre került: az `index.html` elején lévő szövegblokkba (`id="texts"`), képernyők szerint csoportosítva. A felület nem változott.
- Új oldal: **szovegek.html** – az összes szöveg képernyőnként, kereséssel; a szövegek ott átírhatók, a változások kimásolhatók vagy a módosított `index.html` letölthető.
- Tehergépjármű- és súlykorlátozó táblák a KRESZ táblák pontos másolataként (C-007, C-008, C-009, C-010, C-011, C-012, C-023, C-024; zóna: E-030): valósághű tehergépkocsi, pótkocsis szerelvény, tengely és narancs tábla; a szám egész része nagy, a tizedes és a „t” kisebb. A kerek táblák kerete a sebességkorlátozó tábláéval azonos.
- Csúszkák (Beállítások → Térkép és a térkép panel): csak a pöttyel állíthatók. A csúszka vonalára koppintás vagy onnan indított görgetés már nem változtatja meg az értéket, csak görget; a pötty érintési területe nagyobb lett.
- Ha a szövegblokk hibás (pl. hiányzó vessző), az alkalmazás akkor is elindul: a szövegek helyén a kulcsok látszanak, felül piros sor jelzi a hibát. A build (`tools/szovegek.py`) ellenőrzi a blokkot.

## [0.24] – 2026-11-21
A 0.23.1–0.23.6 közbenső változatok változásaival együtt.
- Keresés: új választó a Pont / Szakasz fölött: **Útszám / Koordináta**. Koordináta módban WGS84 („47.13285 19.41772”, vesszővel, É/K-val, fokkal, fok-perc(-mp) alakban is) vagy EOV („EOV 678089 198812”, „Y 678 089 X 198 812”) koordináta adható meg; a mező alatt látszik, mit ismert fel (a másik rendszerben is) és a legközelebbi út szelvénye a távolsággal. A „Saját” gomb a GNSS-pozíciót írja be. Szakasznál két koordináta: ha a két pont ugyanarra az útra esik, az út szakasza (mint az útszámos keresésnél); ha más-más útra, a térképi méréshez hasonlóan a legrövidebb útvonal az országos közúthálózaton, utanként a kezdő – záró szelvénnyel és hosszal („Több úton: 5, 52108”).
- A koordinátás keresések **limezöld** színűek a térképen (szakasz vonal, gombostű, a megadott pont célkereszttel és szaggatott vonallal az út pontjához), a mentett kártyán („Koordináta” / „Koord. szakasz”) és a buborékban; a részletekben a megadott koordináta és a távolság az úttól. CSV-ben a Megjegyzés oszlopban.
- Minden koordináta (GNSS kártya, térképi buborék, Adatok → Helyzet, utolsó ismert pozíció, mérések és keresések részletei) **hosszú nyomással vágólapra másolható**; értesítés: „WGS84 koordináta másolva” / „EOV koordináta másolva”. Csak a számok kerülnek a vágólapra (pl. „47.13285 19.41772”, „678089 198812”). Android: natív vágólap (`copyText`).
- Térkép: a kilométerszelvény nemcsak pont az úton, hanem egy rövid vonalka is az út mellé, a végén a km-számmal. Osztott pályán mindkét pálya kifelé mutat (egymástól el), osztatlan úton jobbra, kivéve ha 30 m-en belül egy másik út fut azon az oldalon.
- Új ikon a saját pozícióhoz: navigációs nyíl a térkép Követés gombján és a Keresés „Saját” gombján (zöld); a célkereszt csak a koordinátát jelöli (limezöld).
- Térkép: ahol egy országos út hídon halad át egy másik felett (pl. M1 az M7 felett), a híd felett haladó út a híd jelölése fölé rajzolódik; a keresett szakasz és a mérés vonala a hídon haladó úton a híd felett is látszik.
- Mérések színe: a GNSS mérés rózsaszín, a térképi mérés lila (a térképen, a kártyákon, a buborékban és a térképi mérés pontjain); a futó GNSS mérés továbbra is narancs.
- Fejlesztés: a kód megjegyzései angolul, az index.html elején angol szójegyzék a magyar szakkifejezésekhez (szelvény, pálya, átkelési szakasz…); a felület magyar marad.
- Beállítások → Térkép: „Kilométerszelvények a térképen” kapcsoló, „Kilométerszelvények ettől a nagyítástól” csúszka (11–18, alapból 14, mint eddig) és külön „Km-számok ettől a nagyítástól” csúszka (alapból 15); a km-szám csak ott látszik, ahol a szelvényjel is.
- Tehergépjármű- és súlykorlátozások kártya (Pozíció oldal és Adatok) a hídkártyával azonos elrendezésben: balra a táblák (új, fehér szegélyes, keskeny számú kivitel, mint a sebességkártyán) és alattuk a távolság („120 m”, „itt”), jobbra korlátozásonként félkövér piros felirat az értékkel piros chipben (pl. „Össztömeg-korlátozás [7,5 t]”), alatta a kivétel, majd a szelvénytartomány („még 400 m”, ha benne vagy).
- A tehergépkocsi össztömeg-korlátozása röviden „Össztömeg-korlátozás” (a tábla mutatja, hogy tehergépkocsira vonatkozik).
- Térkép alapréteg választó: valósághű előnézeti képek (kisváros utcákkal, házakkal, folyóval, erdővel és szántóval; a Világos és a Sötét kép ugyanazzal a színszűrővel készül, mint a valódi térképréteg, a Műhold légifotó-szerű). A „Szürke” réteg neve „Világos”.
- Térképi buborék: a WGS84 és az EOV koordináta egy sorban; a kezelő (pl. MKIF) nem jelenik meg benne; a „Részletek” gomb neve „Adatok”.
- A hidak alapból már a 14-es nagyítástól látszanak a térképen (eddig 15; a csúszkán beállított érték megmarad).
- Javítás: böngészőben az Utcakép gomb az ÚtSzelvény lapját is átvitte a Google Térképre; most csak új lapon nyílik meg, az ÚtSzelvény a helyén marad.
- Térképi buborék: rövidebb gombok, az ikon a felirat mellett; „Pont mentése” helyett „Mentés”.
- Térkép: a koppintott pont buborékában új középső gomb, **Utcakép**: megnyitja a Google Utcaképet a pontnál, az út menetirányába nézve (bal pályán az ellenkező irányba). Az Android alkalmazásban a Google Térkép alkalmazásban, böngészőben új lapon nyílik meg. A három gomb ikonja a felirat fölé került, hogy kiférjenek.
- Sebességkártya: kisebb helységnévtábla; a sebességkorlátozó táblának vékony fehér szegélye van (halvány körvonallal, hogy világos témán is látsszon), a számok keskenyebbek, mint az útszámtáblákon. A „KRESZ alapérték” / „Egyedi korlátozás” félkövér.
- Térkép, sötét alapréteg: a kerékpárutak a műholdképhez hasonló világos sárga színnel látszanak (eddig barna).
- Beállítások → Általános: új kapcsoló „Kerékpárutak a térképen”. Kikapcsolva a kerékpárutak és a rajtuk lévő hidak nem látszanak a térképen, és koppintással sem választhatók.
- Szakasz adatai → Forgalom: sorrend Egységjármű, Összes jármű, Nehéz motoros, Számlálóállomás.

## [0.23] – 2026-11-20
A 0.22.1–0.22.4 közbenső változatok változásaival együtt.
- Új NAP adat: Közúti azonosítópontok (17 114 pont – csomópontok, útvégek és más hálózati pontok hivatalos kóddal, pl. „C020001”). Beépítése: `tools/nap_azonositopontok.py`.
- Szakasz adatai: ha a koppintás egy azonosítópont közelében van, új „Azonosítópont” szakasz mutatja a kódot, a távolságot, és az ott találkozó összes utat útszám-táblával, mindegyiket a saját szelvényével (JOBB / BAL chippel osztott pályán) és nevével.
- Hidak kártya (Pozíció oldal) és a Részletek „Híd” szakasza egyforma soros elrendezést kapott: balra mindig a híd ikonja, alatta (a Pozíció oldalon) a távolság, pl. „150 m” vagy „itt”.
- Új, kéttónusú híd ikonok az alkalmazás színeivel: ugyanaz a híd, a zöld nyíl felfelé mutat a híd felett („Áthaladsz rajta”), lefelé a híd alatt („Alatta haladsz el”), mellette felfelé, ha a híd az út mellett van.
- A korlátozások félkövér piros szöveggel, soronként egy, az érték piros chipben (mint a JOBB / BAL), pl. „Össztömeg [40 t]”; a nagy táblaképek ebből a listából kikerültek.
- Ha egy út osztott pályás út (pl. autópálya) felett halad át, mindkét pálya megkapja a „Alatta haladsz el” hidat (eddig csak a hídhoz közelebbi pálya); a térképen a hídpálya mindkét pálya fölé ér.
- Térkép: a hidak hosszabbak, és méterben méreteződnek, így nagyításkor is megtartják hosszukat és arányukat.
- Beállítások → Térkép: csúszka, hogy melyik nagyítási szinttől látszanak a hidak (12–18, alapból 15).
- Térkép: a híd, amely alatt az út áthalad (pl. földúti híd az M44 felett), kitöltött hídpályaként jelenik meg az úton keresztben, a két pálya rekordja egy hídként; két országos út keresztezésénél a felső út alatt is hídpálya van, így látszik, mi halad felül.

## [0.22] – 2026-11-20
- Hidak a térképen nagyobb nagyításnál (térképi hídjel; kikapcsolható: Beállítások → Térkép). A korlátozott hidak sárgák a súly- vagy magasságkorláttal.
- Két országos út keresztezésénél az alkalmazás megkeresi, melyik út halad a hídon és melyik alatta (764 ilyen híd). A híd magasságkorlátja az alatta haladó úté: ott jelenik meg a térképen (↧), a Pozíció oldal hídkártyáján és a Részleteknél („Alatta haladsz el · M1 hídja”); a hídon haladók csak tájékoztatást kapnak („Alatta: 81106 …”).

## [0.21] – 2026-11-20
- Térkép: egy útra koppintva a buborékban két gomb: **Pont mentése** (a pont mentett keresés lesz, és megnyílik a Keresés oldalon) és **Részletek**.
- Új Szakasz adatai oldal: út (kategória, kezelő, megye, Mérnökség, pálya, szelvények), forgalmi sávok és burkolat, éves forgalom, sebességkorlát, belterület / külterület és település, a ponton lévő híd és az ott érvényes tehergépjármű-korlátozás, koordináták.

## [0.20] – 2026-11-20
A 0.19.1–0.19.5 közbenső változatok változásaival együtt.
- Új beépített NAP szakaszadatok az úthálózathoz: forgalmi sávok száma, burkolat típusa és szélessége, éves keresztmetszeti forgalom (2025). A felület még nem mutatja őket; egy későbbi verzióban a térképen koppintott szakasz részleteinél jelennek meg.
- Új eszköz: `tools/nap_szakaszadatok.py` – a NAP-ból letöltött fájlokból újra előállítja ezeket az adatokat.
- A GitHub-tároló új neve `schafler55/utszelveny`; a webalkalmazás címe https://schafler55.github.io/utszelveny/. A linkek (README, Névjegy, változásnapló) az új címre mutatnak. Az Android alkalmazás azonosítója nem változott, a frissítések ugyanúgy települnek.
- JOBB / BAL címkék függőlegesen a számok közepén (a keresési részletek nagy szelvénye mellett is).
- Mérések: a kezdet → vég nyíl vastagabb, nagyobb és a számok közepére igazítva (kártya, buborék, szakaszok).
- A Keresés oldal ugyanazzal az animációval nyílik meg, mint a Pozíció és a Mérés.
- Folyamatban lévő mérés: jobb felső sarokban a GNSS-pontosság jelzése (mint a Pozíció fő kártyáján), az eltelt idő a „Mérés folyamatban” alatt.
- Fotó: az elő- / hátlapi kamera váltó gomb kikapcsolva (a kód megmaradt).
- A félszélességű mezőkben „KEZDETE” a „KEZDET” helyett.
- Mentett térképi mérés: KEZDETE / VÉGE mezők; a pontok listájában zöld K, P1, P2 … és piros V jel, mint a térképen (a szakaszok is K→P1, P1→V).
- A kis JOBB / BAL címkék keskenyített felirattal: ugyanaz a félkövér betű 80%-os szélességre szűkítve, mint az útszámtáblákon (külön betűtípus nélkül). A Pozíció fő kártya címkéje nem változott.
- A kis JOBB / BAL címkék kisebbek, kitöltés nélkül, vékonyabb (1 px) zöld kerettel. A Pozíció fő kártya címkéje és a Keresés pályaválasztó gombja nem változott.
- JOBB / BAL címke: az alkalmazás zöld kiemelőszíne (halvány kitöltés, zöld keret), ugyanaz a betűtípus, mint mindenhol, a felirat függőlegesen középen. A beágyazott keskeny betűtípus és a hozzá tartozó forrásmegjelölés megszűnt.
- Egy betűcsalád az egész alkalmazásban (Roboto, ennek hiányában a rendszer betűtípusa): szövegek, szelvényszámok, térképi feliratok és táblák, fotóbélyegző – web és APK ugyanúgy.
- Mentett keresés részleteiből kikerült a „Pálya” sor (a JOBB / BAL a cím szelvénye mellett látszik).
- Mérés a térképen: mentés után a mérőeszköz alaphelyzetbe áll, alul a mentett mérés buborékja jelenik meg. A lerakott pontok és vonalak a mérések lila-rózsaszín színét kapják.
- Mérésnél JOBB / BAL címke, ha a mérés végig egy úton és ugyanazon a pályán van.

## [0.19] – 2026-11-20
A 0.18.1–0.18.2 közbenső változatok változásaival együtt.
- Jobb / bal pálya mindenhol egyformán: kis „JOBB” / „BAL” címke (halvány türkiz kitöltés, türkiz keret, keskeny félkövér betű) a km+m mellett – Pozíció fő kártya, térképi buborékok, mentett keresések, keresési részletek; a mérések Kezdet / Vége mezőiben a km alatti sorban. A Keresés pályaválasztó gombja ugyanilyen színű, „JOBB” / „BAL” felirattal.
- A címke betűtípusa beágyazott Roboto (legkeskenyebb szélesség, csak a szükséges betűk, ~5 KB), így minden telefonon ugyanúgy néz ki.
- Térkép: a rétegek gomb nem nyitja meg az alsó beállításpanelt, csak végiglépteti az alapréteget (Szürke → Sötét → Műhold → Ki), a választott réteg neve rövid ideig megjelenik. A többi térképbeállítás a Beállítások → Térkép fülön van.
- Az OpenStreetMap és az Esri forrásmegjelölése sima szöveg, nem link (a térképen és a Névjegyben).

## [0.18] – 2026-11-20
- Térkép: a mentett keresés és mérés „Térképen” gombja ugyanúgy működik – ráközelít, és alul egy közös buborékot mutat: név a keresés / mérés színében, útszámtábla + szelvény (szakasznál kezdet – vég, mérésnél kezdet → vég), az út neve vagy „Több úton: …”, hossz és dátum.
- A buborék gombjai: Elrejtés (ugyanaz a kapcsoló, mint a mentett listában), Törlés (megerősítéssel), Részletek (megnyitja a mentett kártyát kinyitva, kiemelve). Nem mentett keresés: Törlés és Mentés.
- A térkép tetején lévő címkék megszűntek; a térképi címkére koppintva is ez a buborék nyílik meg.

## [0.17] – 2026-11-20
A 0.16.1–0.16.10 közbenső változatok változásaival együtt.
- Világos téma: „Fehér kártyák” – fehér kártyák halványszürke háttéren, lágy árnyékkal; a mentett keresések és mérések mind külön fehér kártyák; sötétebb szövegek (címkék, dátumok, koordináták) a jobb olvashatóságért. Az Android állapot- és navigációs sáv színe is ehhez igazodik. A sötét téma nem változott.
- Térkép: az útszámtáblák helye nagyítás és húzás közben nem ugrál – a táblák az út mentén rögzített pontokon állnak, a már látható tábla a helyén marad (mérve kb. 8–12-szer kevesebb ugrás, eltűnés, felbukkanás).
- 4–5 jegyű útszámnál mindenhol szélesebb tábla (fő kártya, térképi buborékok, keresés, javaslatok), a szám ugyanakkora, mint a rövid útszámoknál.
- Térképi koppintás buborék: útszámtábla és szelvény egy sorban, alatta balra igazítva az út neve, a kezelő (pl. Magyar Közút Nonprofit Zrt.) és a két koordináta.
- Térkép: a koppintás utáni információs buborék útszámtáblával és szelvénnyel jelenik meg, mint a keresés eredménye; a WGS84 és az EOV koordináta külön sorban.
- GNSS kikapcsolásakor (Beállítások → Általános) a Pozíció fő kártyája „GNSS kikapcsolva” lesz (az utolsó ismert pozícióval), nem marad rajta az utolsó szelvény; a GNSS-kártyán „GNSS kikapcsolva a beállításokban” jelzés.
- Budapest kártya: „nem része az országos közúthálózatnak” kisbetűvel.
- A térkép felső címkéin az alkalmazás saját ikonjai (vonalzó, nagyító, bezárás) az emojik helyett; a mérés címkéje a térképi címkével azonos hosszt mutat.
- Térképi címkék: a koppintás után a telefon kattintása már nem az új oldalra esik (ez néha visszacsukta a megnyitott kártyát vagy levette a kiemelést, vagy egy mezőre esett).
- Keresés: sikeres keresés után az útszám- és szelvénymezők kiürülnek; mentés után a keresési eredmény kártyája eltűnik a Keresés oldalról (a keresés a mentett listában marad).
- Mentett mérések és keresések: nagyobb, jobban olvasható útszámtáblák.
- Térkép: a megjelenített mentett méréseknek is van címkéje (név · hossz) a kezdőpontnál, mint a kereséseknek; a szakaszkereséseknél mindig látszik a címke.
- A térképi címkére koppintva megnyílik a mentett keresés / mérés kártyája kinyitva, kiemelve; a felső címkéknél a név nyit, a ✕ zár.
- A mentett mérés / keresés kártyája lefelé nyílik ki, és záráskor felfelé húzódik vissza a kis kártyába.

## [0.16] – 2026-11-19 · [#14](https://github.com/schafler55/utszelveny/pull/14)
A 0.15.1 változat változásaival együtt.
- Gyorsabb térkép mentett keresések, mérések és fényudvar mellett is: az álló réteg (utak, kiemelés, keresett szakaszok, mérési nyomvonalak, km-kövek) egy háttérvászonra rajzolódik, és követés / húzás közben csak eltolódik.
- Az utak úttípusonként egy útvonallal rajzolódnak, csak a képernyőn lévő részük; a fényudvar egyetlen áttetsző vonal.
- Útszámtáblák, pozíciónyíl, koppintásjelölő: elmosott árnyék helyett olcsó, eltolt árnyék.
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
A 0.12.1–0.12.3 közbenső változatok változásaival együtt.
- Sima térképmozgás követéskor: a térkép és a nyíl a GNSS-frissítések között is folyamatosan halad.
- Lassú haladásnál és egyetlen kiugró irányértéknél nem fordul el a térkép.
- Térkép: a Követés gomb ugyanakkora, mint a többi térképgomb.
- CSV-export a mentett keresésekhez is; a CSV-gombok elrejthetők (Beállítások → Mérés / Keresés).
- Mentett mérés: egy elválasztó vonal a részletek felett, mint a keresésnél.

## [0.12] – 2026-11-19
A 0.11.1–0.11.3 közbenső változatok változásaival együtt.
- A mentett mérések és a mentett keresések közös kártyát és viselkedést kaptak.
- A WGS84 és az EOV koordináta külön sorban, sortörés nélkül.
- Mérés: a mentett mérések listája nem ugrál, átnevezésnél nem záródik be a billentyűzet.
- Általános: az alsó menü elrejtése görgetéskor kikapcsolható.

## [0.11] – 2026-11-19
A 0.10.1–0.10.3 közbenső változatok változásaival együtt.
- Gyorsabb fotózás: a képek sorban dolgozódnak fel, az exponáló gomb nem zár le.
- Választható mentési mappa az Android alkalmazásban (Képek, DCIM / ÚtSzelvény, DCIM / Camera vagy egyéni mappa).
- Névjegy: az Android versionCode zárójelben a verziószám mögött.
- Exponálás a hangerőgombokkal (és Bluetooth-os távkioldóval) az Android alkalmazásban.
- A HUD beállítási lap mindig látható, az Általános HUD-kapcsoló megszűnt.

## [0.10] – 2026-11-19 · [#11](https://github.com/schafler55/utszelveny/pull/11)
- HUD mód: tükrözött, nagy kontrasztú kép, hogy a műszerfalra fektetett telefon a szélvédőn tükröződjön.
- Új HUD és Keresés beállítási lap; a beállítások fülei 4 × 2 rácsban.

## [0.9] – 2026-11-19 · [#9](https://github.com/schafler55/utszelveny/pull/9), [#10](https://github.com/schafler55/utszelveny/pull/10)
A 0.8.1–0.8.5 közbenső változatok változásaival együtt.
- Új Keresés fül: pont vagy szakasz keresése útszám és km+m alapján, jobb / bal pálya váltóval.
- Mentett keresések és mentett mérések egyenként kapcsolóval a térképen; gyorsabb rajzolásuk.
- A „Vaku ki” ikon villáma egybefüggő vonal.
- A híd-, állapot- és vakuikonok is lekerekített, Material 3 stílusúak.
- Lekerekített Material 3 ikonok; a fejléc ikonja megnyitja a Névjegyet.
- Kevésbé lekerekített kamerakeret; enyhébb, magasabb színátmenet a navigáció alatt.
- Lebegő navigációs eszköztár animált feliratokkal és színátmenettel alatta.

## [0.8] – 2026-11-18 · [#7](https://github.com/schafler55/utszelveny/pull/7), [#8](https://github.com/schafler55/utszelveny/pull/8)
A 0.7.1–0.7.3 közbenső változatok változásaival együtt.
- Új Material 3 felület, választható világos téma, animált nyitóképernyő és animációk.
- Fotó: vaku gomb (Vaku ki / Vaku / Lámpa); a Vissza gomb lépésenként zár.
- Térkép: az aktuális út kiemelése saját színben (Vastagabb / Fényudvar / Nincs).
- „Térkép alapréteg” a „Háttértérkép” helyett.
- Mérés: a km+m a kezdő / jelenlegi dobozban marad.

## [0.7] – 2026-11-18 · [#6](https://github.com/schafler55/utszelveny/pull/6)
A 0.6.1–0.6.3 közbenső változatok változásaival együtt.
- „GNSS” a „GPS” helyett minden feliratban; WGS84 az alapértelmezett, új koordináta-formátum.
- A használt és látható műholdak rendszerenként a GNSS-kártyán (Android).
- Csípő-nagyításnál az ujjak közötti pont a helyén marad.
- Alkalmazásikon és verziószám a fejlécben.
- „Kézi útválasztás kikapcsolása” felirat; a NAP-megjegyzés rendesen elrejtve.

## [0.6] – 2026-11-18 · [#4](https://github.com/schafler55/utszelveny/pull/4), [#5](https://github.com/schafler55/utszelveny/pull/5)
A 0.5.1 változat változásaival együtt.
- Új Fotó oldal: útszám, km+m, dátum és idő a kép tetején kétsoros sávban, égtáj és EXIF-pozíció.
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
Az első két nap változatai az alkalmazásban még V1.4 – V1.5.9 Beta számot viseltek (a V1.5.7-ig KözútSzelvény néven);
a számozás a V0.2 Beta-val újrakezdődött. Hogy illeszkedjenek a mai számozás sorába, és ne lehessen összekeverni őket
a későbbi 1.x stabil kiadásokkal, ebben a naplóban egy 0-val az elejükön szerepelnek (V1.4 → 0.1.4, V1.5 → 0.1.5);
az eredeti verziószám a szakaszok első sorában áll.

## [0.1.5] – 2026-11-18
Eredeti verziószám: V1.5 – V1.5.9 Beta; e változatok változásai együtt (2026. november 17–18.).
- **Új név:** az alkalmazás neve ÚtSzelvény (korábban KözútSzelvény): a fejlécben, a böngésző címsorában, a webalkalmazás és az Android alkalmazás nevében, a README-ben és az APK fájlnevében (`UtSzelveny.apk`). Az Android csomagazonosító nem változott, így a frissítés a meglévő alkalmazásra települ, és a mentett beállítások megmaradnak.
- **Új alkalmazásikon:** kerek ikon sötét háttéren, zöld gyűrűvel: zöld „KM” útszámtábla, alatta jobbra kanyarodó út, az út szélén régi stílusú, felfelé keskenyedő, csúcsos tetejű kilométerkő „24” felirattal, halvány térképrács. Több lépésben készült el (először útszámtábla egy út fölött, majd a kanyar és a kilométerkő, végül a kő régi formája). Androidon adaptív és kerek ikon, a webalkalmazásnál 192 és 512 képpontos, valamint „maskable” ikon és favicon.
- **Fő kártya, útnév:** a szelvény alatt nincs „km” felirat. Az autópályák és autóutak nevében a „honnan – hová” rész külön, kisebb sorban, zárójelben áll (pl. „M30 autópálya” és alatta „(M3 - Tornyosnémeti)”); a csomóponti ágak nevében a „/x/” párok helyett „(x)” szerepel.
- **Útszámtábla:** az útszám a magyar útszámjelző tábla alakjában jelenik meg: egyenes oldalak, lapos V alakú alj, enyhén lekerekített sarkok, keskenyebb számok; az alsóbbrendű utak táblája ugyanilyen magas.
- **Hidak, osztott pályás utak:** a NAP hídadataiban az osztott pályás út feletti hidak csak az egyik pályán szerepelnek (513 a jobb, 5 a bal pályán). Mostantól a másik pályán is megjelennek, annál a szelvénynél, ahol az a híd alatt áthalad (a híd helyéből vetítve, 11–24 m-re), így mindkét irányban látszanak.
- **Hidak, ikonok:** három egyszerű, körvonalas ikon (áthaladsz rajta / áthaladsz alatta / az út mellett) a korábbi hat részletes piktogram helyett. A kerékpárutakon nyilvántartott gyaloghidak a kerékpárút saját hídjai, ezért az ott haladónak „Áthaladsz rajta” jelzéssel látszanak.
- **Hidak, rajta vagy alatta:** a hídlista megkülönbözteti azokat a hidakat, amelyeken áthaladsz, és azokat, amelyek alatt áthaladsz; korlátozás nélküli hídnál a híd típusát ikon jelzi (közúti híd, felüljáró, gyaloghíd, vadátjáró, közös vasúti híd). A „híd alatti” magasság- és szélességkorlátozás már nem jelenik meg a hídon haladónak; ahol a híd neve alapján országos közút halad alatta (5 eset), ott annál az útnál látszik.
- **Közeli utak:** a „közelben” címkék koppinthatók: a fő kijelzés átvált arra az útra, és egy címkével lehet visszatérni az automatikus útválasztáshoz.
- **Tehergépjármű- és súlykorlátozások:** új, kikapcsolható rész a NAP „Tehergépjárművekre vonatkozó korlátozások” adatcsomagjából (2808 rekord, 1881 összefüggő szakaszba vonva): az éppen érvényes korlátozások a hátralévő hosszal, a haladási irányban 3 km-en belül következők, KRESZ-szerű táblákkal és a kivételek szövegével.
- README: képernyőképek az alkalmazásból (valódi térképpel), az alkalmazásikon a cím fölött.

## [0.1.4] – 2026-11-17
Eredeti verziószám: V1.4 és V1.4.1 Beta. Az első feltöltés a GitHubra, KözútSzelvény néven.
- **Pozíció:** a telefon GPS-pozíciójából az aktuális út száma, neve és a szelvény (km+m), a NAP országos közúthálózati adataiból, internet nélkül. Címkék a pályáról, a közös szakaszról (ahol több út fut együtt) és a közeli utakról (útszám, szelvény, távolság). GPS nélkül „GPS kikapcsolva” kártya indítógombbal és az utolsó ismert pozícióval.
- **Sebességkorlát:** az érvényes sebességkorlát táblával, belterület / külterület jelzéssel (lakott területi átkelési szakasz vagy külsőségi szakasz); ahol nincs egyedi korlátozás, a KRESZ szerinti alapérték.
- **Hidak:** a közeli hidak és út feletti akadályok, súly- és magasságkorlátozással.
- **GPS és koordináták:** WGS84 és EOV koordináta (váltható), GPS-pontosság.
- **Kezelő:** az út kezelője és a megye.
- **Térkép:** az országos közúthálózat térképe internet nélkül, a saját pozícióval és követéssel; OpenStreetMap háttértérkép internetkapcsolattal (szürke, sötét vagy kikapcsolva); a térképre koppintva az adott pont útja és szelvénye.
- **Beállítások:** GPS indítása, képernyő ébren tartása, kerékpárutak kihagyása, háttértérkép, az utak vonalvastagsága, útnév mutatása; a sebességkorlát, a hidak, a GPS és koordináták, valamint a kezelő része külön ki- és bekapcsolható; kézi pozíció megadása WGS84 vagy EOV koordinátával (teszteléshez).
- **Telepíthető webalkalmazás** (PWA), amely az első betöltés után internet nélkül is működik; **Android alkalmazás** ugyanazzal az `index.html`-lel, az APK-t a GitHub minden `main` ágra kerülő feltöltéskor megépíti.
- Névjegy: hivatkozás a GitHub-forráskódra; licenc: GPL-3.0.
