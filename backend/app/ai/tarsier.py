import asyncio
import json

from playwright.async_api import async_playwright

from tarsier.core import Tarsier
from tarsier.ocr import GoogleVisionOCRService

from llama_index.core.tools import FunctionTool, BaseTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.anthropic import Anthropic

from typing import List

class Tools:
    def __init__(self, tarsier, tag_to_xpath, page):
        self.tarsier = tarsier
        self.tag_to_xpath = tag_to_xpath
        self.page = page

    def get_tools(self) -> List[BaseTool]:
        read_page_tool = FunctionTool.from_defaults(
            fn=self.read_page, async_fn=self.read_page
        )
        click_tool = FunctionTool.from_defaults(fn=self.click, async_fn=self.click)
        type_text_tool = FunctionTool.from_defaults(
            fn=self.type_text, async_fn=self.type_text
        )
        press_key_tool = FunctionTool.from_defaults(
            fn=self.press_key, async_fn=self.press_key
        )
        count_elements_tool = FunctionTool.from_defaults(
            fn=self.count_elements, async_fn=self.count_elements
        )
        screenshot_page_tool = FunctionTool.from_defaults(
            fn=self.screenshot_page, async_fn=self.screenshot_page
        )
        open_tab_tool = FunctionTool.from_defaults(
            fn=self.open_tab, async_fn=self.open_tab
        )
        return [
            read_page_tool,
            click_tool,
            type_text_tool,
            press_key_tool,
            count_elements_tool,
            screenshot_page_tool,
            open_tab_tool,
        ]

    async def read_page(self) -> str:
        """
        Use to read the current state of the page
        """
        page_text, inner_tag_to_xpath = await self.tarsier.page_to_text(
            self.page, tag_text_elements=True, keep_tags_showing=True
        )
        self.tag_to_xpath.clear()
        self.tag_to_xpath.update(inner_tag_to_xpath)
        return page_text

    async def click(self, element_id: int) -> str:
        """
        Click on an element based on element_id and return the new page state
        """
        x_path = self.tag_to_xpath[element_id]

        element = self.page.locator(x_path)

        is_animated = await self.page.evaluate(
            """
            (selector) => {
                const element = document.evaluate(selector, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue
                if (!element) return false
                const styles = window.getComputedStyle(element)
                return styles.animation !== 'none' || styles.transition !== 'none'
            }
        """,
            x_path,
        )

        if is_animated:
            print(f"Element {element_id} is animated. Force clicking.")
            await element.click(force=True)
        else:
            print(f"Element {element_id} is stable. Normal clicking.")
            await element.click()

        await self.page.wait_for_timeout(2000)
        return await self.read_page()

    async def type_text(self, element_id: int, text: str) -> str:
        """
        Input text into a textbox based on element_id and return the new page state
        """
        x_path = self.tag_to_xpath[element_id]

        print(x_path)
        await self.page.locator(x_path).press_sequentially(text)
        return await self.read_page()

    async def press_key(self, key: str) -> str:
        """
        Press a key on the keyboard and return the new page state
        """
        await self.page.keyboard.press(key)
        await self.page.wait_for_timeout(2000)
        return await self.read_page()

    async def count_elements(self, element_ids: List[int]) -> int:
        """
        Count the number of elements on the page using a list of the element_ids
        """
        count = 0
        for element_id in element_ids:
            x_path = self.tag_to_xpath[element_id]
            count += await self.page.locator(x_path).count()
        return count

    async def screenshot_page(self) -> str:
        """
        Take a screenshot of the page and save it to a file
        """
        await self.page.screenshot(path="screenshot.png")
        return "screenshot.png"

    async def open_tab(self, url: str):
        """
        Open a new tab and return the new page state
        """
        clipboardText1 = await self.page.evaluate("navigator.clipboard.readText()")

        await self.page.goto(clipboardText1)
        return await self.read_page()

    async def debug_page(self):
        """
        Sleeps for 10 seconds
        """
        await self.page.wait_for_timeout(10000)


async def run_tarsier():
    with open("google_cloud_credentials.json", "r") as f:
        credentials = json.load(f)

    p = await async_playwright().__aenter__()
    browser = await p.chromium.launch(headless=True)
    context = await browser.new_context(
        permissions=["clipboard-read", "clipboard-write"]
    )
    page = await context.new_page()

    ocr_service = GoogleVisionOCRService(credentials)
    tarsier = Tarsier(ocr_service)
    tag_to_xpath = {}

    tools = Tools(tarsier, tag_to_xpath, page)
    tools = tools.get_tools()

    # llm = Anthropic(model="claude-3-haiku-20240307", api_key="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")
    llm = Anthropic(
        model="claude-3-5-sonnet-20240620",
        api_key="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",
    )
    tarsier_agent = ReActAgent.from_tools(
        tools,
        llm=llm,
        verbose=True,
        max_iterations=30,
        # system_prompt="You are a web interaction agent. Start first by using the read page tool to understand where you currently are. You will be passed in OCR text of a web page.",
    )

    await page.goto("http://localhost:5173")
    await tarsier_agent.achat()
