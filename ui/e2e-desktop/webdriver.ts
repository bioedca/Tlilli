/**
 * A small W3C WebDriver client for the desktop smoke suite (PRD 34 §1, D-086).
 *
 * tauri-driver speaks W3C WebDriver and passes each command to the platform's driver
 * (WebKitWebDriver on Linux), which drives the app's webview. The suite needs a handful of
 * commands, so it sends them with `fetch` instead of depending on a WebDriver package.
 * Commands: https://www.w3.org/TR/webdriver2/#endpoints
 */

/** The key under which W3C WebDriver returns an element reference. */
const ELEMENT_KEY = "element-6066-11e4-a52e-4f735466cecf";

type Method = "GET" | "POST" | "DELETE";

/** A reference to an element in the app's page. */
export type Element = { readonly id: string };

async function command(
  url: string,
  method: Method,
  body?: object,
): Promise<unknown> {
  const init: RequestInit = { method };
  if (body !== undefined) {
    init.headers = { "Content-Type": "application/json" };
    init.body = JSON.stringify(body);
  }
  const response = await fetch(url, init);
  const { value } = (await response.json()) as { value: unknown };
  if (!response.ok) {
    const { error, message } = (value ?? {}) as {
      error?: string;
      message?: string;
    };
    throw new Error(
      `WebDriver ${method} ${url} answered ${response.status}: ${error ?? "no error code"}: ${message ?? ""}`,
    );
  }
  return value;
}

/** One session: tauri-driver starts the app for it and stops the app when it ends. */
export class Session {
  private constructor(private readonly url: string) {}

  /** Starts `application`, the path of the app's binary, through the driver at `server`. */
  static async start(server: string, application: string): Promise<Session> {
    const value = (await command(`${server}/session`, "POST", {
      capabilities: { alwaysMatch: { "tauri:options": { application } } },
    })) as { sessionId: string };
    return new Session(`${server}/session/${value.sessionId}`);
  }

  /** The document title of the app's window. */
  async title(): Promise<string> {
    return (await command(`${this.url}/title`, "GET")) as string;
  }

  /** The URL of the page in the app's window. */
  async location(): Promise<string> {
    return (await command(`${this.url}/url`, "GET")) as string;
  }

  /**
   * The first element matching the CSS `selector`, once there is one. The page renders after the
   * window opens, so the lookup repeats every 100 ms until `timeoutMs` has passed.
   */
  async waitFor(selector: string, timeoutMs = 10_000): Promise<Element> {
    const deadline = Date.now() + timeoutMs;
    for (;;) {
      const found = (await command(`${this.url}/elements`, "POST", {
        using: "css selector",
        value: selector,
      })) as Record<string, string>[];
      const id = found[0]?.[ELEMENT_KEY];
      if (id !== undefined) {
        return { id };
      }
      if (Date.now() > deadline) {
        throw new Error(`no element matches ${selector} after ${timeoutMs} ms`);
      }
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
  }

  /** The element's role as the accessibility tree computes it, such as `main`. */
  async role(element: Element): Promise<string> {
    return (await command(
      `${this.url}/element/${element.id}/computedrole`,
      "GET",
    )) as string;
  }

  /** The element's accessible name, such as the text of its `aria-labelledby` heading. */
  async label(element: Element): Promise<string> {
    return (await command(
      `${this.url}/element/${element.id}/computedlabel`,
      "GET",
    )) as string;
  }

  /** Ends the session, which closes the app. */
  async end(): Promise<void> {
    await command(this.url, "DELETE");
  }
}
