#!/usr/bin/env python3
"""Browser smoke test of the web app (web/index.html); CI runs it on every push (.github/workflows/checks.yml).

    pip install playwright==1.63.0        # only the Python package: the installed Chrome is used, no download
    python3 tools/smoke_test.py [path to Chrome]

Drives the app the way a user does (taps and typing) in headless Chrome, with a fake GNSS position on road 7 and a
fake camera, and fails on any JavaScript error or missing text. It also checks things that broke before: taps on
the running-measurement buttons, the map without CanvasRenderingContext2D.roundRect (older phones), "GNSS off"
surviving a restart, the Firefox note's "Megértettem" button, a tap right after a flick (real touch events) and
the desktop layout (wide window with a mouse: map page, pointer readout, right-click menu). Requests to other servers (map tiles, GitHub) are
blocked, so the test never loads OpenStreetMap tiles.
"""
import asyncio
import http.server
import os
import socketserver
import sys
import threading
from functools import partial

from playwright.async_api import async_playwright

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CHROME = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CHROME", "/usr/bin/google-chrome")
ARGS = ["--no-sandbox", "--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream"]
FAILS, ERRORS = [], []


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), partial(Quiet, directory=ROOT))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}/web/index.html"


async def new_page(b, url, **ctx_opts):
    ctx = await b.new_context(viewport={"width": 412, "height": 915}, **ctx_opts)
    host = url.split("/web/")[0]
    await ctx.route("**/*", lambda r: r.continue_() if r.request.url.startswith(host) or r.request.url.startswith("data:")
                    or r.request.url.startswith("blob:") else r.abort())
    pg = await ctx.new_page()
    pg.set_default_timeout(6000)

    def on_console(m):
        t = m.text
        if m.type == "error" and "Failed to load resource" not in t:
            ERRORS.append("console error: " + t[:300])
        elif m.type == "warning" and t.startswith("Missing text"):
            ERRORS.append(t)
    pg.on("console", on_console)
    pg.on("pageerror", lambda e: ERRORS.append("page error: " + str(e)[:400]))
    return ctx, pg


async def step(name, coro):
    try:
        await coro
        print("ok    ", name, flush=True)
    except Exception as e:  # keep going, report at the end
        FAILS.append(f"{name}: {str(e).splitlines()[0][:300]}")
        print("FAIL  ", name, "–", str(e).splitlines()[0][:300], flush=True)


async def expect(cond, msg):
    if not cond:
        raise AssertionError(msg)


async def wait_js(pg, expr, timeout=6000):
    """Polls a JS expression until it is true (Playwright's own wait_for_function compiles code in the page, which
    the app's Content Security Policy does not allow – and should not)."""
    for _ in range(int(timeout / 100)):
        if await pg.evaluate(expr):
            return
        await pg.wait_for_timeout(100)
    raise AssertionError("timed out waiting for: " + expr[:120])


async def boot(pg, url):
    await pg.goto(url)
    await wait_js(pg, "typeof NSEG!=='undefined'&&NSEG>0", 20000)
    await pg.click("#frOk")


async def main_flow(b, url):
    ctx, pg = await new_page(b, url, permissions=["geolocation", "camera"],
                             geolocation={"latitude": 47.2, "longitude": 18.6, "accuracy": 5})
    await step("start, first-start notice", boot(pg, url))
    # put the fake GNSS position on road 7 at 46+275 (worked out with the app's own data)
    ll = await pg.evaluate("(()=>{const h=srchPoint(roadFind('7'),460275,0).hits[0];return [h.lat,h.lon]})()")
    await ctx.set_geolocation({"latitude": ll[0], "longitude": ll[1], "accuracy": 5})

    async def on_road():
        await wait_js(pg, "(()=>{const e=document.querySelector('#hero .ch');return !!e&&/^46\\+2\\d\\d$/.test(e.textContent)})()", 8000)
    await step("Pozíció shows road 7 at 46+2xx", on_road())

    async def pages():
        for n in ["nMap", "nSrch", "nMeas", "nFoto", "nPos"]:
            await pg.click("#" + n)
            await pg.wait_for_timeout(500)
    await step("every page", pages())

    async def settings():
        await pg.click("#gearBtn")
        for t in ["gen", "pos", "map", "srch", "meas", "foto", "hud", "info"]:
            await pg.click(f'#stabs button[data-t="{t}"]')
            await pg.wait_for_timeout(150)
        await pg.click("#closeSheet")
        await pg.wait_for_timeout(400)
    await step("every settings tab", settings())

    async def search():
        await pg.click("#nSrch")
        await pg.fill("#sRoad", "7")
        await pg.fill("#sK1", "46")
        await pg.fill("#sM1", "275")
        await pg.click("#sGo")
        await pg.wait_for_selector("#mapView.on")
        await expect("46+275" in await pg.inner_text("#mapInfo"), "the map bubble does not show 46+275")
        await pg.click('#mapInfo button[data-b="save"]')
        await pg.click("#nSrch")
        await expect(await pg.locator("#srchList .mitem").count() == 1, "the saved search is not in the list")
    await step("search 7 · 46+275, show on the map, save", search())

    async def coord_search():
        await pg.click('#srchSrc button[data-v="coord"]')
        await pg.fill("#sC1", f"{ll[0]+0.0002:.5f} {ll[1]+0.0002:.5f}")   # ~25 m beside road 7
        await pg.click("#sGo")
        try:
            await pg.wait_for_selector("#mapView.on")
        except Exception:
            raise AssertionError("no map after the search; message: " + await pg.inner_text("#sErr"))
        await pg.click("#nSrch")
        await pg.click('#srchSrc button[data-v="road"]')
    await step("coordinate search", coord_search())

    async def measurement():
        await pg.click("#nMeas")
        await pg.click("#mStart")
        # a phone sends a fix every second; the fake position only when it changes: move it a little
        await ctx.set_geolocation({"latitude": ll[0] + 0.00001, "longitude": ll[1], "accuracy": 5})
        await wait_js(pg, "!!document.getElementById('mPoint')&&!document.getElementById('mPoint').disabled", 8000)
        box = await pg.locator("#mPoint").bounding_box()
        x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        await pg.mouse.move(x, y)
        await pg.mouse.down()
        await pg.wait_for_timeout(1300)   # spans at least one redraw of the card (it used to swallow this tap)
        await pg.mouse.up()
        await pg.wait_for_timeout(300)
        await expect(await pg.locator("#measCtl .mpts .chip").count() == 1, "a long press on Pont added no point")
        for _ in range(3):
            box = await pg.locator("#mPoint").bounding_box()   # the button moves down as the point chips appear
            await pg.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
            await pg.mouse.down()
            await pg.wait_for_timeout(100)
            await pg.mouse.up()
            await pg.wait_for_timeout(450)
        await expect(await pg.locator("#measCtl .mpts .chip").count() == 4, "short taps on Pont were lost")
        await pg.click("#mStop")
        await pg.wait_for_selector("#mStart")
        await expect(await pg.locator("#measList .mitem").count() == 1, "the measurement is not in the saved list")
    await step("GNSS measurement: Pont (long press and taps), stop, saved", measurement())

    async def map_tools():
        await pg.click("#nMap")
        await pg.wait_for_timeout(400)
        await pg.click("#follow")
        box = await pg.locator("#map").bounding_box()
        cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2   # the map centre = your position, on road 7
        await pg.mouse.click(cx, cy)
        await pg.wait_for_timeout(300)
        n = await pg.evaluate("srchList.length")
        await pg.click('#mapInfo button[data-t="save"]')   # Mentés: saved, selected on the map, the map stays
        await expect(await pg.evaluate("mapOn&&srchList.length") == n + 1 and await pg.locator('#mapInfo button[data-b="det"]').count() == 1,
                     "Mentés on the tapped road did not leave the saved point selected on the map")
        await pg.click("#mmBtn")
        await pg.mouse.click(cx - 50, cy - 40)
        await pg.mouse.click(cx + 50, cy + 40)
        await pg.wait_for_timeout(600)
        await pg.click("#mmBtn")
        for b_ in ["zIn", "zOut", "rotBtn", "rotBtn", "baseBtn"]:
            await pg.click("#" + b_)
        await pg.mouse.move(cx, cy)
        await pg.mouse.wheel(0, -600)
        await pg.wait_for_timeout(400)
    await step("map: tap, measuring on the map, buttons, zoom", map_tools())

    async def hud():
        await pg.click("#gearBtn")
        await pg.click('#stabs button[data-t="hud"]')
        await pg.click("#hudStart")
        await pg.wait_for_selector("#hud.on")
        await pg.wait_for_timeout(500)
        await pg.keyboard.press("Escape")
        await wait_js(pg, "!document.getElementById('hud').classList.contains('on')")
    await step("HUD on and off", hud())

    async def photo():
        await pg.click("#nFoto")
        await wait_js(pg, "!document.getElementById('camShut').disabled", 10000)
        await pg.click("#camShut")
        await wait_js(pg, "camShots.length===1", 10000)   # stamped, encoded and in the session list
        await expect(await pg.evaluate("camShots[0].blob.size>20000&&camShots[0].tm.wk===true"),
                     "the photo was not encoded by the worker (blocked by the Content Security Policy?)")
        await pg.click("#camThumb")
        await pg.wait_for_selector("#camViewer.on")
        await pg.click("#cvClose")
        await pg.click("#nPos")
    await step("photo with the fake camera, viewer", photo())

    async def gnss_off_kept():
        await pg.click("#gearBtn")
        await pg.click('#stabs button[data-t="gen"]')
        off = await pg.evaluate("TX('settings.gnss_state_off')")
        await pg.click("#gpsToggle")
        await expect(await pg.inner_text("#gpsState") == off, "GNSS did not switch off")
        await pg.reload()
        await wait_js(pg, "typeof NSEG!=='undefined'&&NSEG>0", 20000)
        await pg.wait_for_timeout(1500)
        await expect(await pg.inner_text("#gpsState") == off, "GNSS was switched on again after the restart")
    await step("GNSS off is kept after a restart", gnss_off_kept())
    await ctx.close()


async def firefox_note(b, url):
    ua = "Mozilla/5.0 (Android 14; Mobile; rv:133.0) Gecko/133.0 Firefox/133.0"
    ctx, pg = await new_page(b, url, user_agent=ua)

    async def flow():
        await boot(pg, url)
        await pg.wait_for_selector("#protoAlert.on [data-note='ff-ok']")
        await pg.click("#protoAlert [data-note='ff-ok']")
        await expect(not await pg.locator("#protoAlert.on").count(), "the Firefox note did not close")
        await pg.reload()
        await wait_js(pg, "typeof NSEG!=='undefined'&&NSEG>0", 20000)
        await pg.wait_for_timeout(800)
        await expect(not await pg.locator("#protoAlert.on").count(), "the Firefox note came back after Megértettem")
    await step("Firefox note: Megértettem closes it for good", flow())
    await ctx.close()


async def narrow_menu(b, url):
    ctx, pg = await new_page(b, url)
    inside = """(()=>{const n=document.getElementById('navBar'),r=n.getBoundingClientRect();
      return [...n.querySelectorAll('button')].every(b=>{const q=b.getBoundingClientRect();return q.left>=r.left&&q.right<=r.right&&q.width>=36})})()"""

    async def flow():
        await boot(pg, url)
        for w, cls in [(412, ""), (360, "snug"), (320, "snug tight")]:
            await pg.set_viewport_size({"width": w, "height": 800})
            await wait_js(pg, f"document.getElementById('navBar').className.trim()==='{cls}'")
            for v in ["srch", "meas", "pos"]:
                await pg.evaluate(f"showView('{v}')")
                await pg.wait_for_timeout(500)
                await expect(await pg.evaluate(inside), f"{w} px wide screen, page {v}: a menu button is outside the menu")
        await pg.evaluate("document.documentElement.style.fontSize='200%';dispatchEvent(new Event('resize'))")
        await pg.set_viewport_size({"width": 412, "height": 800})
        await wait_js(pg, "document.getElementById('navBar').className.trim()==='snug'")
        await expect(await pg.evaluate(inside), "412 px wide screen with double text size: a menu button is outside the menu")
    await step("bottom menu fits narrow screens and big text", flow())
    await ctx.close()


async def old_browser_map(b, url):
    ctx, pg = await new_page(b, url)
    await ctx.add_init_script("delete CanvasRenderingContext2D.prototype.roundRect")

    async def flow():
        await boot(pg, url)
        await pg.wait_for_timeout(3000)   # bridge crossings are worked out ~2.5 s after the start
        await pg.click("#nMap")
        await pg.evaluate("""(()=>{const o=bridgePositions().find(o=>!o.K.side&&(brLimitK(o.b,'w')||brLimitK(o.b,'h')));
          S.mapBus=true;setFollow(false);mX=o.m.x;mY=o.m.y;mS=zToS(17);drawMap()})()""")
        await expect("Z17" in await pg.inner_text("#scalebar"), "the map did not finish drawing")
    await step("map at a restricted bridge without ctx.roundRect (older phones)", flow())
    await ctx.close()


async def tap_after_flick(b, url):
    """Real touch events: flick the map, tap a button 200 ms later. The browser used to swallow that tap (noFling)."""
    ctx, pg = await new_page(b, url, has_touch=True, is_mobile=True)
    cdp = await ctx.new_cdp_session(pg)

    async def touch(kind, *pt):
        await cdp.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": [{"x": pt[0], "y": pt[1]}] if pt else []})

    async def flow():
        await boot(pg, url)
        await pg.click("#nMap")
        await pg.wait_for_timeout(400)
        box = await pg.locator("#zOut").bounding_box()
        zoom = await pg.evaluate("mS")
        await touch("touchStart", 90, 400)
        for x in [130, 180, 230, 280, 330]:
            await touch("touchMove", x, 400)
            await pg.wait_for_timeout(12)
        await touch("touchEnd")
        await pg.wait_for_timeout(200)
        await touch("touchStart", box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        await pg.wait_for_timeout(40)
        await touch("touchEnd")
        await pg.wait_for_timeout(400)
        await expect(await pg.evaluate("mS") != zoom, "the tap on the zoom button right after a flick was lost")
    await step("touch: a tap right after a flick on the map arrives", flow())
    await ctx.close()


async def desktop(b, url):
    """Desktop browser (wide window, mouse): the map is the base page, no GNSS; pointer readout, click bubble,
    right-click menu, the Keresés / Mérés panel that is always open."""
    ctx, pg = await new_page(b, url)
    await pg.set_viewport_size({"width": 1440, "height": 900})

    async def flow():
        await boot(pg, url)
        await expect(await pg.evaluate("DESK&&mapOn&&watchId===null&&document.documentElement.dataset.view==='srch'"),
                     "not the desktop layout with the map and the Keresés panel (or GNSS was started)")
        # road 7 at 46+275 in the middle of the map
        await pg.evaluate("(()=>{const h=srchPoint(roadFind('7'),460275,0).hits[0],m=toM(h.lat,h.lon);mX=m.x;mY=m.y;mS=zToS(15);drawMap()})()")
        await pg.mouse.move(700, 450)
        await pg.mouse.move(720, 450)
        await wait_js(pg, "document.getElementById('deskStat').classList.contains('on')&&/46\\+2/.test(document.getElementById('deskStat').textContent)")
        await pg.mouse.click(720, 450)
        await wait_js(pg, "!!document.querySelector('#mapInfo .tapi')&&!document.getElementById('mapInfo').classList.contains('idle')")
        await pg.mouse.click(720, 450, button="right")
        await pg.wait_for_selector("#deskMenu.on")
        await pg.click('#deskMenu button[data-a="info"]')
        await pg.wait_for_selector("#infoPage.on")
        await pg.keyboard.press("Escape")
        await pg.click("#nMeas")
        await expect(await pg.evaluate("document.documentElement.dataset.view==='meas'&&mapOn"), "Mérés did not open in the panel")
        await pg.evaluate("showView('map')")
        await expect(await pg.evaluate("document.documentElement.dataset.view==='meas'"), "the panel did not stay open")
        await pg.click("#nSrch")
        await expect(await pg.evaluate("document.documentElement.dataset.view==='srch'"), "Keresés did not open in the panel")
    await step("desktop: map page, pointer readout, click, right-click menu, panel", flow())
    await ctx.close()


async def main():
    url = serve()
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, args=ARGS)
        await main_flow(b, url)
        await firefox_note(b, url)
        await narrow_menu(b, url)
        await old_browser_map(b, url)
        await tap_after_flick(b, url)
        await desktop(b, url)
        await b.close()
    for e in ERRORS:
        print("ERROR ", e)
    if FAILS or ERRORS:
        print(f"::error::smoke test: {len(FAILS)} failed step(s), {len(ERRORS)} JavaScript error(s)")
        sys.exit(1)
    print("smoke test passed")


asyncio.run(main())
