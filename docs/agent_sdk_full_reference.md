Certainly! Below is a comprehensive markdown document that serves as an in-depth reference for the OpenAI Agents SDK. This guide encompasses core concepts, practical examples, and best practices to assist developers in building, registering, and orchestrating AI agents effectively.

---

# OpenAI Agents SDK Documentation

## Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started](#2-getting-started)

   * [2.1 Prerequisites](#21-prerequisites)
   * [2.2 Installation](#22-installation)
   * [2.3 Authentication](#23-authentication)
3. [Core Concepts](#3-core-concepts)

   * [3.1 Agents](#31-agents)
   * [3.2 Tools](#32-tools)
   * [3.3 Handoffs](#33-handoffs)
   * [3.4 Guardrails](#34-guardrails)
   * [3.5 Runner](#35-runner)
   * [3.6 Tracing](#36-tracing)
4. [Building Agents](#4-building-agents)

   * [4.1 Basic Agent](#41-basic-agent)
   * [4.2 Agent with Tools](#42-agent-with-tools)
   * [4.3 Agent with Handoffs](#43-agent-with-handoffs)
   * [4.4 Agent with Guardrails](#44-agent-with-guardrails)
5. [Advanced Features](#5-advanced-features)

   * [5.1 Structured Outputs](#51-structured-outputs)
   * [5.2 Dynamic Instructions](#52-dynamic-instructions)
   * [5.3 Cloning Agents](#53-cloning-agents)
   * [5.4 Forcing Tool Use](#54-forcing-tool-use)
6. [Integration with External Models](#6-integration-with-external-models)
7. [Testing & Debugging](#7-testing--debugging)
8. [Best Practices](#8-best-practices)
9. [Resources](#9-resources)

---

## 1. Introduction

The OpenAI Agents SDK is a lightweight, Python-first framework designed to build agentic AI applications. It provides essential primitives like Agents, Tools, Handoffs, and Guardrails to create complex workflows with ease.([OpenAI GitHub][1])

---

## 2. Getting Started

### 2.1 Prerequisites

* Python ≥ 3.8
* pip package manager
* OpenAI API Key: Obtain from [OpenAI Platform](https://platform.openai.com/account/api-keys)

### 2.2 Installation

Install the OpenAI Agents SDK:

```bash
pip install openai-agents
```



### 2.3 Authentication

Set your OpenAI API key as an environment variable:([OpenAI GitHub][1])

```bash
export OPENAI_API_KEY="sk-XXXXXXXXXXXXXXXXXXXXXXXX"
```



For Windows PowerShell:

```powershell
$Env:OPENAI_API_KEY="sk-XXXXXXXXXXXXXXXXXXXXXXXX"
```



---

## 3. Core Concepts

### 3.1 Agents

Agents are LLMs configured with specific instructions and optional tools. They can process inputs, utilize tools, and produce outputs.

```python
from agents import Agent

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant."
)
```



### 3.2 Tools

Tools are functions that agents can use to perform specific tasks. They can be simple Python functions or integrations with external APIs.

```python
from agents import function_tool

@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."
```



### 3.3 Handoffs

Handoffs allow agents to delegate tasks to other agents, enabling the creation of complex workflows where specialized agents handle specific subtasks.([OpenAI GitHub][1])

```python
from agents import Agent

booking_agent = Agent(name="Booking Agent", instructions="Handle booking inquiries.")
refund_agent = Agent(name="Refund Agent", instructions="Handle refund inquiries.")

triage_agent = Agent(
    name="Triage Agent",
    instructions="Route inquiries to the appropriate agent.",
    handoffs=[booking_agent, refund_agent]
)
```



### 3.4 Guardrails

Guardrails are mechanisms to validate inputs and outputs of agents, ensuring they meet certain criteria.

```python
from agents import input_guardrail, GuardrailFunctionOutput

@input_guardrail
async def check_input(ctx, agent, input):
    if "forbidden" in input:
        return GuardrailFunctionOutput(tripwire_triggered=True)
    return GuardrailFunctionOutput(tripwire_triggered=False)
```



### 3.5 Runner

The Runner executes agents and manages workflows.

```python
from agents import Runner

result = Runner.run_sync(agent, "Hello, how can you assist me?")
print(result.final_output)
```



### 3.6 Tracing

Built-in tracing allows monitoring and debugging of agent workflows.([OpenAI GitHub][1])

```python
import os
os.environ["OPENAI_TRACE"] = "1"
```



---

## 4. Building Agents

### 4.1 Basic Agent

```python
from agents import Agent, Runner

agent = Agent(
    name="Basic Agent",
    instructions="Respond to greetings."
)

result = Runner.run_sync(agent, "Hello!")
print(result.final_output)
```



### 4.2 Agent with Tools

```python
from agents import Agent, Runner, function_tool

@function_tool
def add(a: int, b: int) -> int:
    return a + b

agent = Agent(
    name="Calculator Agent",
    instructions="Perform addition.",
    tools=[add]
)

result = Runner.run_sync(agent, "What is 2 plus 3?")
print(result.final_output)
```



### 4.3 Agent with Handoffs

```python
from agents import Agent, Runner

math_agent = Agent(name="Math Agent", instructions="Handle math questions.")
history_agent = Agent(name="History Agent", instructions="Handle history questions.")

triage_agent = Agent(
    name="Triage Agent",
    instructions="Route questions to the appropriate agent.",
    handoffs=[math_agent, history_agent]
)

result = Runner.run_sync(triage_agent, "Who was the first president of the USA?")
print(result.final_output)
```



### 4.4 Agent with Guardrails

```python
from agents import Agent, Runner, input_guardrail, GuardrailFunctionOutput

@input_guardrail
async def profanity_filter(ctx, agent, input):
    if "badword" in input:
        return GuardrailFunctionOutput(tripwire_triggered=True)
    return GuardrailFunctionOutput(tripwire_triggered=False)

agent = Agent(
    name="Polite Agent",
    instructions="Respond politely.",
    input_guardrails=[profanity_filter]
)

result = Runner.run_sync(agent, "Hello!")
print(result.final_output)
```



---

## 5. Advanced Features

### 5.1 Structured Outputs

Agents can return structured outputs using Pydantic models.([GitHub][2])

```python
from agents import Agent
from pydantic import BaseModel

class WeatherReport(BaseModel):
    temperature: float
    condition: str

agent = Agent(
    name="Weather Agent",
    instructions="Provide weather reports.",
    output_type=WeatherReport
)
```



### 5.2 Dynamic Instructions

Instructions can be dynamically generated based on context.([OpenAI GitHub][3])

```python
def dynamic_instructions(ctx, agent):
    return f"Assist user {ctx.context.user_id} with their queries."

agent = Agent(
    name="Dynamic Agent",
    instructions=dynamic_instructions
)
```



### 5.3 Cloning Agents

Agents can be cloned with modified properties.

```python
agent = Agent(name="Original Agent", instructions="Original instructions.")
cloned_agent = agent.clone(name="Cloned Agent", instructions="Modified instructions.")
```



### 5.4 Forcing Tool Use

Control tool usage with `tool_choice`.([OpenAI GitHub][3])

```python
agent = Agent(
    name="Tool Agent",
    instructions="Use the tool provided.",
    tools=[some_tool],
    model_settings={"tool_choice": "required"}
)
```



---

## 6. Integration with External Models

The SDK supports integration with non-OpenAI models via compatible APIs.([OpenAI GitHub][4])

```python
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel

client = AsyncOpenAI(base_url="https://api.externalmodel.com", api_key="your-api-key")

model = OpenAIChatCompletionsModel(
    model="external-model",
    openai_client=client
)

agent = Agent(
    name="External Model Agent",
    instructions="Use external model.",
    model=model
)
```



---

## 7. Testing & Debugging

* **Unit Testing**: Use `pytest` to write tests for agents and tools.
* **Mocking**: Mock external API calls during testing.
* **Tracing**: Enable tracing to monitor agent workflows.([OpenAI][5])

---

## 8. Best Practices

* **Prompt Engineering**: Craft clear and concise instructions.
* **Security**: Avoid hardcoding API keys; use environment variables.
* **Version Control**: Track changes using




Based on a thorough review of the latest OpenAI Agents SDK documentation and related resources, your existing markdown documentation covers the foundational aspects effectively. However, to enhance its comprehensiveness and utility, consider incorporating the following additional sections and details:

---

## 1. Agent Lifecycle and Execution Flow

Understanding the agent's execution lifecycle is crucial for effective debugging and optimization.([DEV Community][1])

### Agent Loop Overview

The agent loop operates as follows:([Medium][2])

1. **Input Submission**: The agent receives an input, which can be a string or a structured object.([Medium][2])

2. **LLM Invocation**: The agent processes the input using the configured language model.([Medium][2])

3. **Output Handling**:

   * **Final Output**: If the model returns a complete response, the loop terminates.
   * **Tool Calls**: If the model suggests using a tool, the agent invokes the specified tool and re-enters the loop with the tool's output.
   * **Handoff**: If the model delegates the task to another agent, control is transferred accordingly.([GitHub][3], [Medium][2])

This loop continues until a final output is produced or a maximum number of iterations is reached.([GitHub][3])

---

## 2. Context Management

The SDK allows passing a context object throughout the agent's execution, enabling shared state and dependency injection.

### Defining and Using Context

```python
from dataclasses import dataclass

@dataclass
class UserContext:
    user_id: str
    preferences: dict

# When running the agent
context = UserContext(user_id="12345", preferences={"language": "en"})
result = Runner.run_sync(agent, input_data, context=context)
```



This context is accessible within tools, guardrails, and agents, facilitating personalized and stateful interactions.

---

## 3. Tracing and Monitoring

The SDK includes built-in tracing capabilities for monitoring agent workflows.([DEV Community][1])

### Enabling Tracing

```python
import os
os.environ["OPENAI_TRACE"] = "1"
```



Traces can be visualized using compatible tools, providing insights into agent decisions, tool invocations, and handoffs.

---

## 4. Integration with External Tools and APIs

Agents can be equipped with tools that interface with external APIs or services.

### Example: Web Search Tool

```python
from agents import Agent, Runner, WebSearchTool

agent = Agent(
    name="Research Agent",
    instructions="Use web search to find information.",
    tools=[WebSearchTool()]
)

result = Runner.run_sync(agent, "What is the latest news on AI?")
print(result.final_output)
```



This enables agents to perform real-time data retrieval and processing.

---

## 5. Structured Outputs with Pydantic

Agents can return structured outputs by specifying a Pydantic model.

### Defining Structured Output

```python
from pydantic import BaseModel

class WeatherReport(BaseModel):
    temperature: float
    condition: str

agent = Agent(
    name="Weather Agent",
    instructions="Provide weather information.",
    output_type=WeatherReport
)
```



This facilitates validation and downstream processing of agent outputs.

---

## 6. Dynamic Instruction Generation

Instructions can be dynamically generated based on context or other runtime information.

### Implementing Dynamic Instructions

```python
def dynamic_instructions(context, agent):
    return f"Assist user {context.user_id} with their queries."

agent = Agent(
    name="Dynamic Agent",
    instructions=dynamic_instructions
)
```



This allows for personalized and context-aware agent behavior.

---

## 7. Guardrails for Input and Output Validation

Guardrails can be defined to validate inputs and outputs, ensuring compliance with desired criteria.

### Example: Input Guardrail

```python
from agents import input_guardrail, GuardrailFunctionOutput

@input_guardrail
async def check_input(ctx, agent, input_data):
    if "restricted" in input_data:
        return GuardrailFunctionOutput(tripwire_triggered=True)
    return GuardrailFunctionOutput(tripwire_triggered=False)
```



This mechanism enhances the robustness and safety of agent interactions.

---

## 8. Agent Cloning and Modification

Agents can be cloned and modified to create variations with different behaviors or configurations.

### Cloning an Agent

```python
original_agent = Agent(name="Original", instructions="Original instructions.")
cloned_agent = original_agent.clone(name="Clone", instructions="Modified instructions.")
```



This facilitates experimentation and reuse of agent configurations.

---

## 9. Forcing Tool Usage

You can control tool usage behavior by setting the `tool_choice` parameter in `model_settings`.

### Enforcing Tool Usage

```python
agent = Agent(
    name="Tool-Enforced Agent",
    instructions="Always use the provided tool.",
    tools=[some_tool],
    model_settings={"tool_choice": "required"}
)
```



This ensures that the agent utilizes specified tools as intended.

---

## 10. Integration with External Models

The SDK supports integration with external models that are compatible with OpenAI's API.

### Using an External Model

```python
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel

client = AsyncOpenAI(base_url="https://api.externalmodel.com", api_key="your-api-key")
model = OpenAIChatCompletionsModel(model="external-model", openai_client=client)

agent = Agent(
    name="External Model Agent",
    instructions="Use external model.",
    model=model
)
```



This allows leveraging different language models within the same agent framework.
