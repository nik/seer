import asyncio
import json
import os
from typing import List
from dotenv import load_dotenv

from playwright.async_api import async_playwright
from tarsier.core import Tarsier
from tarsier.ocr import GoogleVisionOCRService
from llama_index.core.tools import FunctionTool, BaseTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.groq import Groq

load_dotenv()

class TarsierAgent:
    def __init__(self, llm_provider: str = "Groq"):
        self.flow_step = 0
        self.tarsier = None
        self.tag_to_xpath = {}
        self.page = None
        self.tarsier_agent = None
        self.llm_provider = llm_provider

    def initialize(self):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        credentials_path = os.path.join(project_root, "google_cloud_credentials.json")
        print(credentials_path)

        with open(credentials_path, "r") as f:
            credentials = json.load(f)

        ocr_service = GoogleVisionOCRService(credentials)
        self.tarsier = Tarsier(ocr_service)

        tools = self.get_tools()

        if self.llm_provider == "Anthropic":
            llm = Anthropic(
                model="claude-3-5-sonnet-20240620",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
        else:
            llm = Groq(
                model="llama-3.1-70b-versatile",
                api_key=os.getenv("GROQ_API_KEY"),
            )

        self.tarsier_agent = ReActAgent.from_tools(
            tools,
            llm=llm,
            verbose=True,
            max_iterations=30,
        )

    async def run(self, query: str):
        p = await async_playwright().__aenter__()
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            permissions=["clipboard-read", "clipboard-write"]
        )
        self.page = await context.new_page()
        await self.page.goto("https://todostaging.netlify.app/")
        await self.tarsier_agent.achat(query)

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
        increment_flow_step_tool = FunctionTool.from_defaults(
            fn=self.increment_flow_step, async_fn=self.increment_flow_step
        )
        return [
            read_page_tool,
            click_tool,
            type_text_tool,
            press_key_tool,
            count_elements_tool,
            screenshot_page_tool,
            open_tab_tool,
            increment_flow_step_tool,
        ]

    async def increment_flow_step(self):
        """
        Increment the flow step
        """
        self.flow_step += 1

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

    async def screenshot_page(self, filename: str, flow_step: int) -> str:
        """
        Take a screenshot of a page
        """
        screenshot, _ = await self.tarsier.page_to_image(
            self.page, tag_text_elements=False, keep_tags_showing=False, tagless=False
        )
        ui_flows_dir = "../workspace/ui_flows"
        os.makedirs(ui_flows_dir, exist_ok=True)

        screenshot_path = os.path.join(ui_flows_dir, f"{filename}_{flow_step}.png")
        with open(screenshot_path, "wb") as f:
            f.write(screenshot)
            print(f"Writing screenshot to {screenshot_path}")
        return f"{filename}_{flow_step}.png"

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
