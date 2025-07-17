#!/usr/bin/env python3
"""Quick start example for Claude Code SDK."""

import anyio

from claude_code_sdk import (
    AssistantMessage,
    ClaudeCodeOptions,
    ResultMessage,
    TextBlock,
    query,
)


async def basic_example():
    """Basic example - simple question."""
    print("=== Basic Example ===")
    print("[DEBUG] Starting query...")

    message_count = 0
    async for message in query(prompt="What is 2 + 2?"):
        message_count += 1
        print(f"[DEBUG] Received message #{message_count}: {type(message).__name__}")
        
        if isinstance(message, AssistantMessage):
            print(f"[DEBUG] AssistantMessage with {len(message.content)} blocks")
            for i, block in enumerate(message.content):
                print(f"[DEBUG] Block {i}: {type(block).__name__}")
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif isinstance(message, ResultMessage):
            print(f"[DEBUG] ResultMessage: cost=${message.total_cost_usd if message.total_cost_usd else 0}")
        else:
            print(f"[DEBUG] Other message type: {message}")
    
    print(f"[DEBUG] Query complete. Total messages: {message_count}")
    print()


async def with_options_example():
    """Example with custom options."""
    print("=== With Options Example ===")

    options = ClaudeCodeOptions(
        system_prompt="You are a helpful assistant that explains things simply.",
        max_turns=1,
    )

    async for message in query(
        prompt="Explain what Python is in one sentence.", options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
    print()


async def with_tools_example():
    """Example using tools."""
    print("=== With Tools Example ===")

    options = ClaudeCodeOptions(
        allowed_tools=["Read", "Write"],
        system_prompt="You are a helpful file assistant.",
    )

    async for message in query(
        prompt="Create a file called hello.txt with 'Hello, World!' in it",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif isinstance(message, ResultMessage) and message.total_cost_usd > 0:
            print(f"\nCost: ${message.total_cost_usd:.4f}")
    print()


async def main():
    """Run all examples."""
    await basic_example()
    await with_options_example()
    await with_tools_example()


if __name__ == "__main__":
    anyio.run(main)