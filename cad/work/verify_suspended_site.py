"""Browser QA for the added attachment page, its real meshes and preserved links."""
import argparse
import io
import json
from pathlib import Path
import struct
from urllib.parse import urljoin
import zipfile

from playwright.sync_api import sync_playwright, expect


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8765/")
    args = parser.parse_args()
    output = Path("/tmp/rocklabs-suspended-qa")
    output.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--enable-unsafe-swiftshader"])
        page = browser.new_page(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(urljoin(args.url, "index.html"))
        for label in ("(better)_trackpad", "(even better)_puck", "(corne + puck)_magnetic_dock"):
            expect(page.get_by_role("link", name=label, exact=True)).to_be_visible()
        page.get_by_role("link", name="(corne + puck)_suspended_attachment", exact=True).click()
        expect(page.get_by_role("heading", name="Along for the lift.")).to_be_visible()
        model = page.frame_locator("#model-view")
        expect(model.locator("#status")).to_have_attribute("data-loaded", "true", timeout=30000)
        expect(page.locator("#load-status")).to_be_empty()
        expect(page.locator("#print-size")).to_contain_text("183.5")
        page.screenshot(path=str(output / "desktop.png"), full_page=True)
        for label, mode in [("Attachment", "attachment"), ("Print plate", "print"),
                            ("Fit check", "coupon"), ("Suspended", "suspended")]:
            page.get_by_role("button", name=label, exact=True).click()
            expect(model.locator("#status")).to_have_text(f"Suspended puck — {mode}", timeout=30000)
            expect(model.locator("#status")).to_have_attribute("data-loaded", "true")
            expect(page.get_by_role("button", name=label, exact=True)).to_have_attribute("aria-pressed", "true")
            expect(page.locator("#load-status")).to_be_empty()
            page.locator(".viewer-card").screenshot(path=str(output / f"{mode}.png"))
            viewer_href = page.locator("#open-viewer").get_attribute("href")
            assert "embed=" not in viewer_href and mode in viewer_href
        print("PASS four real-mesh previews and standalone viewer links", flush=True)

        # Follow every local page resource, including collapsed links.
        for href in page.locator("a[href]").evaluate_all("links => links.map(a => a.getAttribute('href'))"):
            if href.startswith(("https:", "#")):
                continue
            assert page.request.get(urljoin(args.url, href)).ok, href
        for name in ("carrier", "upper_jaw", "retainer", "print_plate", "fit_coupon"):
            response = page.request.get(urljoin(args.url, f"models/corne_puck_suspended_{name}.stl"))
            assert response.ok
            data = response.body()
            assert len(data) == 84 + 50 * struct.unpack_from("<I", data, 80)[0]
        kit = page.request.get(urljoin(args.url, "models/corne_puck_suspended_print_kit.zip"))
        with zipfile.ZipFile(io.BytesIO(kit.body())) as archive:
            assert archive.testzip() is None
            assert len(archive.namelist()) == 12
            assert "README.md" in archive.namelist()
            report = json.loads(archive.read("dimensions.json"))
            assert report["checks"] and all(c["pass"] for c in report["checks"])
            assert report["derived"]["tilt_degrees_relative_to_keyboard"] == 15
        print("PASS downloads, STEP files, all resource links and complete print kit", flush=True)

        for width in (390, 320):
            page.set_viewport_size({"width": width, "height": 844})
            page.reload()
            expect(model.locator("#status")).to_have_attribute("data-loaded", "true", timeout=30000)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.get_by_role("button", name="Fit check", exact=True).click()
            expect(model.locator("#status")).to_have_text("Suspended puck — coupon", timeout=30000)
            if width == 390:
                page.screenshot(path=str(output / "mobile.png"), full_page=True)
        print("PASS 390 px and 320 px mobile layout and controls", flush=True)

        page.set_viewport_size({"width": 1440, "height": 1100})
        page.route("**/corne_puck_suspended_suspended_carrier.stl", lambda route: route.fulfill(status=404, body="Missing test mesh"))
        page.goto(urljoin(args.url, "suspended.html"))
        expect(model.locator("#status")).to_have_attribute("data-loaded", "error", timeout=30000)
        expect(page.locator("#load-status")).to_contain_text("Preview could not load")
        expect(page.get_by_role("link", name="AFTER CHECKING THE FIT Full attachment", exact=False)).to_be_visible()
        page.unroute("**/corne_puck_suspended_suspended_carrier.stl")
        page.goto(urljoin(args.url, "dock.html"))
        expect(page.get_by_role("heading", name="Closer to your keys.")).to_be_visible()
        expect(page.frame_locator("#model-view").locator("#status")).to_have_attribute("data-loaded", "true", timeout=30000)
        assert not errors, errors
        print(f"PASS missing-mesh feedback and original dock; no JS errors. Screenshots: {output}", flush=True)
        browser.close()


if __name__ == "__main__":
    main()
