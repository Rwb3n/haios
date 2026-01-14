
import os
import yaml
import logging
from haios_etl.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)

DB_PATH = os.environ.get("DB_PATH", "haios_memory.db")

def register_initial_agents():
    db = DatabaseManager(DB_PATH)
    db.setup() # Ensure schema is applied
    
    agents_dir = "docs/specs/agents"
    for filename in os.listdir(agents_dir):
        if filename.endswith(".yaml"):
            filepath = os.path.join(agents_dir, filename)
            with open(filepath, "r") as f:
                try:
                    agent_card = yaml.safe_load(f)
                    db.register_agent(agent_card)
                    print(f"Successfully registered: {agent_card['name']}")
                except Exception as e:
                    print(f"Failed to register {filename}: {e}")

if __name__ == "__main__":
    register_initial_agents()
