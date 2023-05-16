"""Loader that uses Playwright to load a page, then uses unstructured to load the html.
"""
import logging
import sys
from typing import List, Optional

import asyncio
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader

logger = logging.getLogger(__name__)


class PlaywrightURLLoaderAsync(BaseLoader):
    """Loader that uses Playwright and to load a page and unstructured to load the html.
    This is useful for loading pages that require javascript to render.

    Attributes:
        urls (List[str]): List of URLs to load.
        continue_on_failure (bool): If True, continue loading other URLs on failure.
        headless (bool): If True, the browser will run in headless mode.
    """

    def __init__(
        self,
        urls: List[str],
        continue_on_failure: bool = True,
        headless: bool = True,
        remove_selectors: Optional[List[str]] = None,
    ):
        """Load a list of URLs using Playwright and unstructured."""
        try:
            import playwright  # noqa:F401
        except ImportError:
            raise ValueError(
                "playwright package not found, please install it with "
                "`pip install playwright`"
            )

        try:
            import unstructured  # noqa:F401
        except ImportError:
            raise ValueError(
                "unstructured package not found, please install it with "
                "`pip install unstructured`"
            )

        self.urls = urls
        self.continue_on_failure = continue_on_failure
        self.headless = headless
        self.remove_selectors = remove_selectors

    async def load_1(self) -> List[Document]:
        """Load the specified URLs using Playwright and create Document instances.

        Returns:
            List[Document]: A list of Document instances with loaded content.
        """
        from playwright.async_api import async_playwright
        from unstructured.partition.html import partition_html

        docs: List[Document] = list()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            for url in self.urls:
                try:
                    page = await browser.new_page()
                    await page.goto(url)

                    for selector in self.remove_selectors or []:
                        elements = page.locator(selector).all()
                        for element in elements:
                            if await element.is_visible():
                                element.evaluate("element => element.remove()")

                    page_source = await page.content()
                    elements = partition_html(text=page_source)
                    text = "\n\n".join([str(el) for el in elements])
                    metadata = {"source": url}
                    docs.append(Document(page_content=text, metadata=metadata))
                except Exception as e:
                    if self.continue_on_failure:
                        logger.error(
                            f"Error fetching or processing {url}, exception: {e}"
                        )
                    else:
                        raise e
            browser.close()
        return docs

    async def load(self) -> List[Document]:
        """Load the specified URLs using Playwright and create Document instances.

        Returns:
            List[Document]: A list of Document instances with loaded content.
        """
        from playwright.async_api import async_playwright

        docs: List[Document] = list()

        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=self.headless)
                tasks = [self.get_document(url, browser) for url in self.urls]
                docs = await asyncio.gather(*tasks)
            except Exception as e:
                raise e
            await browser.close()
            return docs   

    async def get_document(self, url, browser):
        from unstructured.partition.html import partition_html

        try:
            page = await browser.new_page()
            await page.goto(url)

            for selector in self.remove_selectors or []:
                elements = page.locator(selector).all()
                for element in elements:
                    if await element.is_visible():
                        element.evaluate("element => element.remove()")
            
            content = await page.content()
            elements = partition_html(text=content)
            text = "\n\n".join([str(el) for el in elements])
            metadata = {"source": url}
            await page.close()
            return Document(page_content=text, metadata=metadata)
        except Exception as e:
            if self.continue_on_failure:
                logger.error(
                    f"Error fetching or processing {url}, exception: {e}"
                )
            else:
                raise e

