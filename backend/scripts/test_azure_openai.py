import asyncio

from app.integrations.llm.azure_openai import AzureOpenAIProvider


async def main():
    provider = AzureOpenAIProvider()
    result = await provider.generate(
        "Reply with exactly: Azure connection successful."
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())