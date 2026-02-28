"""
Create agent_config table
Run: python3 create_agent_table.py
"""
from app.database import engine
from app.models.agent_config import AgentConfig
from sqlalchemy import inspect

def main():
    # Check if table exists
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Existing tables: {', '.join(tables)}")
    
    if 'agent_config' not in tables:
        print('\nCreating agent_config table...')
        AgentConfig.__table__.create(engine)
        print('✅ agent_config table created successfully!')
    else:
        print('\n✅ agent_config table already exists')

if __name__ == "__main__":
    main()
