"""Browser checks for the real website; install playwright + chromium to run."""
import argparse
from pathlib import Path
import struct
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright, expect


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8765/")
    args = parser.parse_args()
    output = Path("/tmp/rocklabs-site-qa")
    output.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--enable-unsafe-swiftshader"])
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(urljoin(args.url, "index.html"))
        page.get_by_role("link", name="(corne + puck)_magnetic_dock").click()
        expect(page.get_by_role("heading", name="Closer to your keys.")).to_be_visible()
        model = page.frame_locator("#model-view")
        expect(model.locator("#status")).to_have_attribute("data-loaded", "true", timeout=30000)
        expect(page.locator("#load-status")).to_be_empty()
        expect(page.locator("#print-size")).to_contain_text("106.0")
        assert model.locator("canvas").count() == 1
        page.screenshot(path=str(output / "desktop.png"), full_page=True)
        for label, mode in [("Dock only", "dock"), ("Fit check", "coupon"), ("Assembly", "assembly")]:
            page.get_by_role("button", name=label, exact=True).click()
            expect(model.locator("#status")).to_have_text(f"Corne puck dock — {mode}", timeout=30000)
            expect(model.locator("#status")).to_have_attribute("data-loaded", "true")
            expect(page.get_by_role("button", name=label, exact=True)).to_have_attribute("aria-pressed", "true")
            if mode == "dock":
                page.locator(".viewer-card").screenshot(path=str(output / "dock-only.png"))
        print("PASS all three interactive previews load actual geometry")

        for name in ("print", "fit_coupon"):
            response = page.request.get(urljoin(args.url, f"models/corne_puck_dock_{name}.stl"))
            assert response.ok
            data = response.body()
            assert len(data) == 84 + 50 * struct.unpack_from("<I", data, 80)[0]
        for path in ("cad/outputs/corne_dock/corne_puck_dock_print.step", "cad/outputs/corne_dock/corne_puck_dock_assembly.step",
                     "cad/outputs/corne_dock/README.md", "cad/corne_dock.json", "cad/references/README.md"):
            assert page.request.get(urljoin(args.url, path)).ok, path
        report = page.request.get(urljoin(args.url, "models/corne_puck_dock_dimensions.json")).json()
        assert report["checks"] and all(row["pass"] for row in report["checks"])
        print("PASS printable downloads, STEP files, guides, and dimension report")

        page.set_viewport_size({"width": 390, "height": 844})
        page.reload()
        expect(model.locator("#status")).to_have_attribute("data-loaded", "true", timeout=30000)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.screenshot(path=str(output / "mobile.png"), full_page=True)
        page.get_by_role("button", name="Fit check", exact=True).click()
        expect(model.locator("#status")).to_have_text("Corne puck dock — coupon", timeout=30000)
        print("PASS mobile layout and model switching")

        page.goto(urljoin(args.url, "viewer.html?model=models/cirque_round_puck_v6_print_plate.stl%3Fv%3D5"))
        expect(page.locator("#status")).to_have_attribute("data-loaded", "true", timeout=30000)
        page.goto(urljoin(args.url, "viewer.html?model=models/corne_puck_dock_print.stl&model=missing-test-model.stl"))
        expect(page.locator("#status")).to_have_attribute("data-loaded", "error", timeout=30000)
        expect(page.locator("#status")).to_contain_text("missing-test-model.stl")
        assert page.locator("canvas").count() == 1
        print("PASS original puck viewer and partial-load error handling")
        assert not errors, errors
        print(f"PASS no JavaScript errors; screenshots: {output}")
        browser.close()


if __name__ == "__main__":
    main()
