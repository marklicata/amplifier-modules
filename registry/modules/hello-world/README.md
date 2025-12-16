# Hello World Agent

The simplest possible Amplifier module - a minimal agent demonstrating the basic structure and patterns.

## Purpose

This embedded example module serves as:
- **Learning Resource**: See how a minimal agent is structured
- **Template**: Copy and modify for your own agents
- **Testing**: Verify your Amplifier installation

## Installation

```bash
amplifier module install hello-world
```

Since this is an embedded module, the source code is included directly in the registry!

## Usage

### Python API

```python
from hello_world import HelloAgent

# Create agent
agent = HelloAgent(config={"style": "friendly"})

# Generate greeting
message = agent.greet("Developer")
print(message)  # "Hello, Developer! Welcome to Amplifier."

# Run in Amplifier context
result = agent.run({"user_name": "Alice"})
print(result["greeting"])
```

### Configuration

```yaml
agent: hello-world
config:
  style: friendly  # Options: friendly, formal, casual
```

### Greeting Styles

**Friendly** (default):
```
Hello, Alice! Welcome to Amplifier.
```

**Formal**:
```
Greetings, Alice. Welcome to Amplifier.
```

**Casual**:
```
Hey Alice! Welcome to Amplifier!
```

## Source Code

The complete source is available at `src/hello_world.py` - only 60 lines of Python!

## Learning Points

This example demonstrates:
1. **Class-based agent structure**
2. **Configuration handling**
3. **Entry point pattern** (`hello_world:HelloAgent`)
4. **Context-based execution**
5. **Embedded module type**

## Next Steps

Once you understand this example:
1. Check out the `code-reviewer` agent for a more complex example
2. Read the [Amplifier Module Development Guide](https://docs.amplifier.dev/modules)
3. Create your own agent using this as a template

## License

MIT License - This is example code, use it however you like!
