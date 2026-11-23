import { describe, expect, it } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync, readdirSync } from "node:fs";
import { resolve, join } from "node:path";

const root = resolve(import.meta.dirname, "../src");
const source = readFileSync(join(root, "styles/tokens.css"), "utf8");
function declarations(block: string) {
  return Object.fromEntries([...block.matchAll(/(--[\w-]+)\s*:\s*([^;]+);/g)].map((m) => [m[1], m[2].trim()]));
}
const light = declarations(source.split('[data-theme="dark"]')[0]);
const dark = { ...light, ...declarations(source.split('[data-theme="dark"]')[1]) };
function value(tokens: Record<string, string>, name: string, seen = new Set<string>()): string {
  if (seen.has(name)) throw new Error(`Cyclic token: ${name}`);
  seen.add(name);
  const result = tokens[name];
  if (!result) throw new Error(`Missing token: ${name}`);
  const alias = result.match(/^var\((--[\w-]+)\)$/);
  return alias ? value(tokens, alias[1], seen) : result;
}
function channels(color: string): number[] {
  if (/^#[0-9A-F]{6}$/i.test(color)) return [1, 3, 5].map((i) => parseInt(color.slice(i, i + 2), 16)).concat(1);
  const match = color.match(/^rgba?\((.+)\)$/);
  if (!match) throw new Error(`Unsupported color: ${color}`);
  const values = match[1].trim().split(/[\s,/]+/);
  return values.map((v, i) => v.endsWith("%") ? parseFloat(v) * (i === 3 ? 0.01 : 2.55) : Number(v)).concat(values.length === 3 ? [1] : []);
}
function composite(top: number[], bottom: number[]): number[] {
  return top.slice(0, 3).map((v, i) => v * top[3] + bottom[i] * (1 - top[3])).concat(1);
}
function luminance(rgb: number[]) {
  const c = rgb.slice(0, 3).map((v) => v / 255)
    .map((x) => x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4);
  return c[0] * 0.2126 + c[1] * 0.7152 + c[2] * 0.0722;
}
function contrast(a: string, b: string, under = "#0F1318") {
  const bg = composite(channels(b), channels(under));
  const [lo, hi] = [luminance(composite(channels(a), bg)), luminance(bg)].sort((x, y) => x - y);
  return (hi + 0.05) / (lo + 0.05);
}
for (const [theme, tokens] of Object.entries({ light, dark })) {
  describe(`${theme} semantic contrast`, () => {
    it("keeps readable text on all content surfaces", () => {
      for (const fg of ["--text-primary", "--text-secondary", "--text-muted"]) {
        for (const bg of ["--bg-canvas", "--bg-surface", "--bg-secondary", "--bg-warm", "--surface-muted", "--surface-soft", "--surface-highlight", ...(tokens["--elevated"] ? ["--elevated"] : [])]) {
          expect(contrast(value(tokens, fg), value(tokens, bg)), `${fg} / ${bg}`).toBeGreaterThanOrEqual(4.5);
        }
      }
    });
    it("keeps actions, selection and semantic labels readable", () => {
      const pairs = [
        ["--accent-ink", "--accent-light"], ["--accent-ink", "--bg-canvas"],
        ["--accent-ink", "--bg-secondary"], ["--accent-ink", "--surface-muted"], ["--accent-ink", "--surface-soft"],
        ["--selected-text", "--selected-bg"], ["--success", "--success-bg"],
        ["--warning", "--warning-bg"], ["--danger", "--danger-bg"], ["--info", "--info-bg"],
        ["--on-accent", "--accent"], ["--on-accent", "--accent-hover"], ["--on-accent", "--accent-active"],
        ["--on-danger", "--danger"], ["--on-danger", "--danger-hover"],
        ["--on-success", "--success"], ["--on-secondary", "--secondary"],
        ["--text-on-featured", "--surface-featured"], ["--text-featured-secondary", "--surface-featured"],
        ["--featured-accent", "--surface-featured"], ["--on-featured-button", "--featured-button-bg"],
        ["--on-featured-button", "--featured-button-hover"], ["--disabled-text", "--disabled-bg"],
        ["--nav-text", "--bg-sidebar"], ["--nav-muted", "--bg-sidebar"],
        ["--nav-text", "--nav-hover"], ["--nav-active", "--nav-selected"],
      ];
      for (const [fg, bg] of pairs) {
        for (const under of ["--bg-canvas", "--bg-surface", ...(tokens["--elevated"] ? ["--elevated"] : [])]) {
          expect(contrast(value(tokens, fg), value(tokens, bg), value(tokens, under)), `${fg} / ${bg} over ${under}`).toBeGreaterThanOrEqual(4.5);
        }
      }
    });
    it("distinguishes control edges, focus rings and data marks", () => {
      for (const fg of ["--border-strong", "--focus-color"]) {
        for (const bg of ["--bg-canvas", "--bg-surface", "--surface-muted", "--surface-soft", ...(tokens["--elevated"] ? ["--elevated"] : [])]) {
          expect(contrast(value(tokens, fg), value(tokens, bg)), `${fg} / ${bg}`).toBeGreaterThanOrEqual(3);
        }
      }
      for (const fg of ["--chart-1", "--chart-2", "--chart-3", "--chart-4", "--chart-positive", "--chart-caution", "--chart-negative"]) {
        expect(contrast(value(tokens, fg), value(tokens, "--chart-track")), fg).toBeGreaterThanOrEqual(3);
      }
    });
  });
}
it("keeps theme-specific action fills separate from readable foregrounds", () => {
  for (const tokens of [light, dark]) {
    for (const name of ["--featured-button-bg", "--progress-fill", "--nav-indicator"]) {
      expect(value(tokens, name), name).toBe(value(tokens, "--accent"));
    }
    expect(value(tokens, "--selected-text")).toBe(value(tokens, "--text-primary"));
    expect(value(tokens, "--nav-active")).toBe(value(tokens, "--text-primary"));
    expect(value(tokens, "--on-featured-button")).toBe(value(tokens, "--on-accent"));
  }
  expect(value(light, "--bg")).toBe("#FAF8F4");
  expect(value(dark, "--bg")).toBe("#0F1318");
  expect(value(light, "--accent")).toBe("#FFB020");
  expect(value(dark, "--accent")).toBe(value(light, "--accent"));
  expect(value(light, "--card")).toBe("#FFFDFA");
});
function files(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => entry.isDirectory() ? files(join(dir, entry.name)) : [join(dir, entry.name)]);
}
it("keeps literal presentation colors in the central token system", () => {
  for (const path of files(root).filter((p) => /\.(css|tsx)$/.test(p) && !p.endsWith("tokens.css"))) {
    const text = readFileSync(path, "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
    expect(text, path).not.toMatch(/#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(/);
  }
});
it("prevents low-contrast accent foregrounds, gradients and painted shadows in page styles", () => {
  for (const path of files(root).filter((p) => /\.(css|tsx)$/.test(p) && !p.endsWith("tokens.css"))) {
    const text = readFileSync(path, "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
    expect(text, path).not.toMatch(/(?<![\w-])color\s*:\s*var\(--accent(?:-hover|-active)?\)/);
    expect(text, path).not.toMatch(/(?:linear|radial|conic)-gradient\(/);
    for (const match of text.matchAll(/box-shadow\s*:\s*([^;]+);/g)) {
      expect(match[1].trim(), path).toBe(path.endsWith("dark.css") && match[1].includes("--shadow-floating") ? "var(--shadow-floating)" : "none");
    }
  }
});

it("preserves every frozen light-theme token", () => {
  expect(createHash("sha256").update(JSON.stringify(light)).digest("hex")).toBe("9b9337157aa19c57cac440f82b02145325a201df7bc8f3e867692f4e3d43825e");
});
it("keeps all additional component rules scoped to dark mode", () => {
  const css = readFileSync(join(root, "styles/dark.css"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
  for (const rule of css.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
    let depth = 0;
    let start = 0;
    const selectors: string[] = [];
    for (let i = 0; i < rule[1].length; i++) {
      if (rule[1][i] === "(") depth++;
      if (rule[1][i] === ")") depth--;
      if (rule[1][i] === "," && depth === 0) { selectors.push(rule[1].slice(start, i).trim()); start = i + 1; }
    }
    selectors.push(rule[1].slice(start).trim());
    for (const selector of selectors) expect(selector).toMatch(/^html\[data-theme="dark"\]/);
    if (rule[2].includes("--shadow-floating")) expect(rule[1].trim()).toBe('html[data-theme="dark"] :is(.pm-menu-dropdown, .pm-dialog)');
  }
});
it("uses translucent statuses and reserves amber tints for active controls", () => {
  for (const status of ["success", "warning", "danger", "info"]) {
    expect(channels(value(dark, `--${status}-bg`))[3]).toBeCloseTo(0.14);
    expect(channels(value(dark, `--${status}-border`))[3]).toBeCloseTo(0.30);
  }
  expect(value(dark, "--accent-light")).toBe(value(dark, "--elevated"));
  expect(channels(value(dark, "--selected-bg"))[3]).toBeCloseTo(0.12);
});
