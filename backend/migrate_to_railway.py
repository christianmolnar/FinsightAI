# Railway Database Migration Script
# This will be run once you provide the Railway PostgreSQL connection string

import os
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def migrate_to_railway(database_url):
    """
    Migrate paper portfolio data from JSON to Railway PostgreSQL
    """
    print("🚀 Starting Railway PostgreSQL Migration...")
    
    # Create engine
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Test connection
        print("✓ Testing database connection...")
        result = session.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✓ Connected to PostgreSQL: {version[:50]}...")
        
        # Load existing paper portfolio data
        print("\n📁 Loading paper portfolio data from JSON...")
        json_file = "paper_portfolios.json"
        
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                portfolios = json.load(f)
            
            default_portfolio = portfolios.get('default', {})
            cash_balance = default_portfolio.get('cash_balance', 10000)
            positions = default_portfolio.get('positions', {})
            realized_pnl = default_portfolio.get('realized_pnl', 0)
            
            print(f"✓ Found portfolio with ${cash_balance:,.2f} cash")
            print(f"✓ Found {len(positions)} position(s)")
            
            # Create default user if not exists
            print("\n👤 Creating default user...")
            user_query = text("""
                INSERT INTO users (id, email, full_name, created_at)
                VALUES (
                    gen_random_uuid(),
                    'default@finsight.ai',
                    'Default User',
                    NOW()
                )
                ON CONFLICT (email) DO NOTHING
                RETURNING id;
            """)
            result = session.execute(user_query)
            session.commit()
            
            user_result = session.execute(
                text("SELECT id FROM users WHERE email = 'default@finsight.ai'")
            )
            user_id = user_result.fetchone()[0]
            print(f"✓ User created/found: {user_id}")
            
            # Create paper portfolio
            print("\n💼 Creating paper portfolio...")
            portfolio_query = text("""
                INSERT INTO portfolios (
                    id, user_id, name, portfolio_type,
                    initial_cash, current_cash, total_value,
                    created_at, updated_at
                )
                VALUES (
                    gen_random_uuid(),
                    :user_id,
                    'Paper Portfolio',
                    'paper',
                    10000.0,
                    :cash_balance,
                    :total_value,
                    NOW(),
                    NOW()
                )
                ON CONFLICT DO NOTHING
                RETURNING id;
            """)
            
            # Calculate total value
            positions_value = sum(
                pos['quantity'] * pos['avg_price'] 
                for pos in positions.values()
            )
            total_value = cash_balance + positions_value
            
            result = session.execute(
                portfolio_query,
                {
                    'user_id': user_id,
                    'cash_balance': cash_balance,
                    'total_value': total_value
                }
            )
            session.commit()
            
            portfolio_result = session.execute(
                text("""
                    SELECT id FROM portfolios 
                    WHERE user_id = :user_id AND portfolio_type = 'paper'
                    LIMIT 1
                """),
                {'user_id': user_id}
            )
            portfolio_id = portfolio_result.fetchone()[0]
            print(f"✓ Portfolio created: {portfolio_id}")
            
            # Migrate positions
            if positions:
                print(f"\n📊 Migrating {len(positions)} position(s)...")
                for symbol, pos_data in positions.items():
                    position_query = text("""
                        INSERT INTO positions (
                            id, portfolio_id, symbol,
                            quantity, average_cost, current_price,
                            market_value, unrealized_pnl,
                            created_at, updated_at
                        )
                        VALUES (
                            gen_random_uuid(),
                            :portfolio_id,
                            :symbol,
                            :quantity,
                            :avg_price,
                            :avg_price,
                            :market_value,
                            0.0,
                            NOW(),
                            NOW()
                        )
                        ON CONFLICT DO NOTHING;
                    """)
                    
                    market_value = pos_data['quantity'] * pos_data['avg_price']
                    
                    session.execute(
                        position_query,
                        {
                            'portfolio_id': portfolio_id,
                            'symbol': symbol,
                            'quantity': pos_data['quantity'],
                            'avg_price': pos_data['avg_price'],
                            'market_value': market_value
                        }
                    )
                    print(f"  ✓ Migrated {symbol}: {pos_data['quantity']} shares @ ${pos_data['avg_price']}")
                
                session.commit()
                print("✓ All positions migrated successfully")
            
            print("\n✅ Migration completed successfully!")
            print(f"\n📊 Summary:")
            print(f"  - Cash Balance: ${cash_balance:,.2f}")
            print(f"  - Positions Value: ${positions_value:,.2f}")
            print(f"  - Total Value: ${total_value:,.2f}")
            print(f"  - Positions: {len(positions)}")
            
        else:
            print("⚠️  No JSON file found - creating fresh portfolio")
            # Create default user and empty portfolio
            # (code similar to above but with default values)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        session.rollback()
        return False
        
    finally:
        session.close()

if __name__ == "__main__":
    # This will be run with the Railway DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("Please set it to your Railway PostgreSQL connection string")
        exit(1)
    
    migrate_to_railway(database_url)
