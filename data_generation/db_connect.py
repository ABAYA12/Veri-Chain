import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
urlSupaBaseTable = os.getenv("DIRECT_URL")

def connect_db():
    try:
        with psycopg2.connect(urlSupaBaseTable) as conn:
            with conn.cursor() as cur:
                
                # Define all SQL table creation statements
                query = """
                -- USER Table
                CREATE TABLE IF NOT EXISTS users (
                    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    public_key TEXT NOT NULL UNIQUE,
                    registration_date TIMESTAMP DEFAULT NOW(),
                    status TEXT CHECK (status IN ('active', 'suspended', 'deleted')) NOT NULL
                );

                -- IDENTITY Table
                CREATE TABLE IF NOT EXISTS identity (
                    identity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
                    ipfs_hash TEXT NOT NULL UNIQUE,
                    creation_date TIMESTAMP DEFAULT NOW(),
                    last_updated TIMESTAMP DEFAULT NOW(),
                    status TEXT CHECK (status IN ('pending', 'verified', 'revoked')) NOT NULL
                );

                -- ENTITY Table
                CREATE TABLE IF NOT EXISTS entity (
                    entity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name TEXT NOT NULL,
                    public_key TEXT NOT NULL UNIQUE,
                    entity_type TEXT CHECK (entity_type IN ('issuer', 'verifier', 'regulator')) NOT NULL,
                    registration_date TIMESTAMP DEFAULT NOW(),
                    status TEXT CHECK (status IN ('active', 'inactive')) NOT NULL
                );

                -- VERIFICATION Table
                CREATE TABLE IF NOT EXISTS verification (
                    verification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    identity_id UUID REFERENCES identity(identity_id) ON DELETE CASCADE,
                    verifier_entity_id UUID REFERENCES entity(entity_id) ON DELETE CASCADE,
                    request_date TIMESTAMP DEFAULT NOW(),
                    completion_date TIMESTAMP,
                    status TEXT CHECK (status IN ('pending', 'approved', 'rejected')) NOT NULL,
                    proof_reference TEXT UNIQUE
                );

                -- SMART_CONTRACT Table
                CREATE TABLE IF NOT EXISTS smart_contract (
                    contract_address TEXT PRIMARY KEY,
                    entity_id UUID REFERENCES entity(entity_id) ON DELETE CASCADE,
                    contract_type TEXT CHECK (contract_type IN ('identity', 'verification', 'transaction')) NOT NULL,
                    deployment_date TIMESTAMP DEFAULT NOW(),
                    version TEXT NOT NULL,
                    status TEXT CHECK (status IN ('active', 'deprecated')) NOT NULL
                );

                -- TRANSACTION Table
                CREATE TABLE IF NOT EXISTS transaction (
                    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    contract_address TEXT REFERENCES smart_contract(contract_address) ON DELETE CASCADE,
                    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
                    verification_id UUID REFERENCES verification(verification_id) ON DELETE CASCADE,
                    transaction_date TIMESTAMP DEFAULT NOW(),
                    transaction_type TEXT CHECK (transaction_type IN ('identity_registration', 'verification_request', 'credential_issue')) NOT NULL,
                    status TEXT CHECK (status IN ('pending', 'completed', 'failed')) NOT NULL
                );

                -- IPFS_STORAGE Table
                CREATE TABLE IF NOT EXISTS ipfs_storage (
                    content_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
                    ipfs_hash TEXT NOT NULL UNIQUE,
                    storage_date TIMESTAMP DEFAULT NOW(),
                    content_type TEXT CHECK (content_type IN ('identity', 'credential')) NOT NULL,
                    encryption_status TEXT CHECK (encryption_status IN ('encrypted', 'public')) NOT NULL
                );
                """

                # Execute the query
                cur.execute(query)
                conn.commit()

        print("✅ Successfully connected and tables created/verified!")
        return conn
    except Exception as e:
        print("❌ Database connection failed:", e)
        return None

if __name__ == "__main__":
    conn = connect_db()
    if conn:
        conn.close()
