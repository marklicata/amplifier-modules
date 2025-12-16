"""
Hello World Agent - Minimal Amplifier Module Example

This is the simplest possible Amplifier agent, demonstrating
the basic structure and entry point pattern.
"""


class HelloAgent:
    """A simple greeting agent."""

    def __init__(self, config=None):
        """
        Initialize the Hello Agent.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.greeting_style = self.config.get("style", "friendly")

    def greet(self, name: str = "World") -> str:
        """
        Generate a greeting message.

        Args:
            name: Name to greet (default: "World")

        Returns:
            Greeting message string
        """
        if self.greeting_style == "formal":
            return f"Greetings, {name}. Welcome to Amplifier."
        elif self.greeting_style == "casual":
            return f"Hey {name}! Welcome to Amplifier!"
        else:  # friendly (default)
            return f"Hello, {name}! Welcome to Amplifier."

    def run(self, context):
        """
        Main agent execution method.

        Args:
            context: Amplifier execution context

        Returns:
            Greeting result
        """
        user_name = context.get("user_name", "World")
        greeting = self.greet(user_name)

        return {
            "greeting": greeting,
            "style": self.greeting_style,
            "success": True
        }


# Example usage
if __name__ == "__main__":
    agent = HelloAgent({"style": "friendly"})
    print(agent.greet("Developer"))
