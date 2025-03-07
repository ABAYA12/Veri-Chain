import psycopg2
from dotenv import load_dotenv
import os
from faker import Faker
import random
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()
urlSupaBaseTable = os.getenv("DIRECT_URL")

# Define 10 different locales
locales = ['en_US', 'fr_FR', 'de_DE', 'es_ES', 'it_IT', 'ja_JP', 'zh_CN', 'ru_RU', 'pt_PT', 'nl_NL']
# Create a Faker instance for each locale
fakers = {loc: Faker(loc) for loc in locales}

def get_random_faker():
    """Return a random Faker instance from our pool."""
    return random.choice(list(fakers.values()))

def connect_db():
    try:
        conn = psycopg2.connect(urlSupaBaseTable)
        cur = conn.cursor()
        # Create tables if they do not exist
        query = """
        # -- USER Table
        # CREATE TABLE IF NOT EXISTS users (
        #     user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        #     public_key TEXT NOT NULL UNIQUE,
        #     registration_date TIMESTAMP DEFAULT NOW(),
        #     status TEXT CHECK (status IN ('active', 'suspended', 'deleted')) NOT NULL
        # );

        # -- IDENTITY Table
        # CREATE TABLE IF NOT EXISTS identity (
        #     identity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        #     user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
        #     ipfs_hash TEXT NOT NULL UNIQUE,
        #     creation_date TIMESTAMP DEFAULT NOW(),
        #     last_updated TIMESTAMP DEFAULT NOW(),
        #     status TEXT CHECK (status IN ('pending', 'verified', 'revoked')) NOT NULL
        # );

        # -- ENTITY Table
        # CREATE TABLE IF NOT EXISTS entity (
        #     entity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        #     name TEXT NOT NULL,
        #     public_key TEXT NOT NULL UNIQUE,
        #     entity_type TEXT CHECK (entity_type IN ('issuer', 'verifier', 'regulator')) NOT NULL,
        #     registration_date TIMESTAMP DEFAULT NOW(),
        #     status TEXT CHECK (status IN ('active', 'inactive')) NOT NULL
        # );

        # -- VERIFICATION Table
        # CREATE TABLE IF NOT EXISTS verification (
        #     verification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        #     identity_id UUID REFERENCES identity(identity_id) ON DELETE CASCADE,
        #     verifier_entity_id UUID REFERENCES entity(entity_id) ON DELETE CASCADE,
        #     request_date TIMESTAMP DEFAULT NOW(),
        #     completion_date TIMESTAMP,
        #     status TEXT CHECK (status IN ('pending', 'approved', 'rejected')) NOT NULL,
        #     proof_reference TEXT UNIQUE
        # );

        # -- SMART_CONTRACT Table
        # CREATE TABLE IF NOT EXISTS smart_contract (
        #     contract_address TEXT PRIMARY KEY,
        #     entity_id UUID REFERENCES entity(entity_id) ON DELETE CASCADE,
        #     contract_type TEXT CHECK (contract_type IN ('identity', 'verification', 'transaction')) NOT NULL,
        #     deployment_date TIMESTAMP DEFAULT NOW(),
        #     version TEXT NOT NULL,
        #     status TEXT CHECK (status IN ('active', 'deprecated')) NOT NULL
        # );

        # -- TRANSACTION Table
        # CREATE TABLE IF NOT EXISTS transaction (
        #     transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        #     contract_address TEXT REFERENCES smart_contract(contract_address) ON DELETE CASCADE,
        #     user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
        #     verification_id UUID REFERENCES verification(verification_id) ON DELETE CASCADE,
        #     transaction_date TIMESTAMP DEFAULT NOW(),
        #     transaction_type TEXT CHECK (transaction_type IN ('identity_registration', 'verification_request', 'credential_issue')) NOT NULL,
        #     status TEXT CHECK (status IN ('pending', 'completed', 'failed')) NOT NULL
        # );

        # -- IPFS_STORAGE Table
        # CREATE TABLE IF NOT EXISTS ipfs_storage (
        #     content_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        #     user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
        #     ipfs_hash TEXT NOT NULL UNIQUE,
        #     storage_date TIMESTAMP DEFAULT NOW(),
        #     content_type TEXT CHECK (content_type IN ('identity', 'credential')) NOT NULL,
        #     encryption_status TEXT CHECK (encryption_status IN ('encrypted', 'public')) NOT NULL
        # );
        # """
        # cur.execute(query)
        # conn.commit()
        cur.close()
        print("✅ Successfully connected and tables created/verified!")
        return conn
    except Exception as e:
        print("❌ Database connection failed:", e)
        return None

def insert_users(conn, num_users=500):
    cur = conn.cursor()
    users = []
    statuses = ['active', 'suspended', 'deleted']
    for _ in range(num_users):
        fake = get_random_faker()
        # Generate a fake public key using a hex pattern
        public_key = fake.hexify(text="^^^^^^^^^^^^^^^^^^^^")
        status = random.choice(statuses)
        registration_date = fake.date_time_between(start_date='-1y', end_date='now')
        cur.execute(
            "INSERT INTO users (public_key, registration_date, status) VALUES (%s, %s, %s) RETURNING user_id",
            (public_key, registration_date, status)
        )
        user_id = cur.fetchone()[0]
        users.append(user_id)
    conn.commit()
    cur.close()
    return users

def insert_identities(conn, user_ids, num_identities=500):
    cur = conn.cursor()
    identities = []
    statuses = ['pending', 'verified', 'revoked']
    for _ in range(num_identities):
        fake = get_random_faker()
        user_id = random.choice(user_ids)
        ipfs_hash = fake.sha256()
        status = random.choice(statuses)
        creation_date = fake.date_time_between(start_date='-1y', end_date='now')
        # Ensure last_updated is after creation_date
        last_updated = creation_date + timedelta(days=random.randint(0, 365))
        cur.execute(
            "INSERT INTO identity (user_id, ipfs_hash, creation_date, last_updated, status) VALUES (%s, %s, %s, %s, %s) RETURNING identity_id",
            (user_id, ipfs_hash, creation_date, last_updated, status)
        )
        identity_id = cur.fetchone()[0]
        identities.append(identity_id)
    conn.commit()
    cur.close()
    return identities

def insert_entities(conn, num_entities=500):
    cur = conn.cursor()
    entities = []
    statuses = ['active', 'inactive']
    entity_types = ['issuer', 'verifier', 'regulator']
    for _ in range(num_entities):
        fake = get_random_faker()
        name = fake.company()
        public_key = fake.hexify(text="^^^^^^^^^^^^^^^^^^^^")
        entity_type = random.choice(entity_types)
        status = random.choice(statuses)
        registration_date = fake.date_time_between(start_date='-1y', end_date='now')
        cur.execute(
            "INSERT INTO entity (name, public_key, entity_type, registration_date, status) VALUES (%s, %s, %s, %s, %s) RETURNING entity_id",
            (name, public_key, entity_type, registration_date, status)
        )
        entity_id = cur.fetchone()[0]
        entities.append(entity_id)
    conn.commit()
    cur.close()
    return entities

def insert_verifications(conn, identity_ids, entity_ids, num_verifications=500):
    cur = conn.cursor()
    verifications = []
    statuses = ['pending', 'approved', 'rejected']
    for _ in range(num_verifications):
        fake = get_random_faker()
        identity_id = random.choice(identity_ids)
        verifier_entity_id = random.choice(entity_ids)
        request_date = fake.date_time_between(start_date='-1y', end_date='now')
        status = random.choice(statuses)
        # If approved or rejected, add a completion_date; leave as None if pending
        completion_date = (fake.date_time_between(start_date=request_date, end_date='now')
                           if status in ['approved', 'rejected'] else None)
        proof_reference = fake.hexify(text="^^^^^^^^^^^^^^^^^^^^")
        cur.execute(
            "INSERT INTO verification (identity_id, verifier_entity_id, request_date, completion_date, status, proof_reference) VALUES (%s, %s, %s, %s, %s, %s) RETURNING verification_id",
            (identity_id, verifier_entity_id, request_date, completion_date, status, proof_reference)
        )
        verification_id = cur.fetchone()[0]
        verifications.append(verification_id)
    conn.commit()
    cur.close()
    return verifications

def insert_smart_contracts(conn, entity_ids, num_contracts=500):
    cur = conn.cursor()
    contracts = []
    statuses = ['active', 'deprecated']
    contract_types = ['identity', 'verification', 'transaction']
    for _ in range(num_contracts):
        fake = get_random_faker()
        # Create a fake Ethereum-like address (0x followed by 40 hex digits)
        contract_address = "0x" + fake.hexify(text="^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        entity_id = random.choice(entity_ids)
        contract_type = random.choice(contract_types)
        deployment_date = fake.date_time_between(start_date='-1y', end_date='now')
        version = f"v{random.randint(1,5)}.{random.randint(0,9)}"
        status = random.choice(statuses)
        cur.execute(
            "INSERT INTO smart_contract (contract_address, entity_id, contract_type, deployment_date, version, status) VALUES (%s, %s, %s, %s, %s, %s) RETURNING contract_address",
            (contract_address, entity_id, contract_type, deployment_date, version, status)
        )
        contract_addr = cur.fetchone()[0]
        contracts.append(contract_addr)
    conn.commit()
    cur.close()
    return contracts

def insert_transactions(conn, user_ids, contracts, verification_ids, num_transactions=500):
    cur = conn.cursor()
    transactions = []
    statuses = ['pending', 'completed', 'failed']
    transaction_types = ['identity_registration', 'verification_request', 'credential_issue']
    for _ in range(num_transactions):
        fake = get_random_faker()
        contract_address = random.choice(contracts)
        user_id = random.choice(user_ids)
        verification_id = random.choice(verification_ids)
        transaction_date = fake.date_time_between(start_date='-1y', end_date='now')
        transaction_type = random.choice(transaction_types)
        status = random.choice(statuses)
        cur.execute(
            "INSERT INTO transaction (contract_address, user_id, verification_id, transaction_date, transaction_type, status) VALUES (%s, %s, %s, %s, %s, %s) RETURNING transaction_id",
            (contract_address, user_id, verification_id, transaction_date, transaction_type, status)
        )
        transaction_id = cur.fetchone()[0]
        transactions.append(transaction_id)
    conn.commit()
    cur.close()
    return transactions

def insert_ipfs_storage(conn, user_ids, num_storage=500):
    cur = conn.cursor()
    storage_ids = []
    content_types = ['identity', 'credential']
    encryption_statuses = ['encrypted', 'public']
    for _ in range(num_storage):
        fake = get_random_faker()
        user_id = random.choice(user_ids)
        ipfs_hash = fake.sha256()
        storage_date = fake.date_time_between(start_date='-1y', end_date='now')
        content_type = random.choice(content_types)
        encryption_status = random.choice(encryption_statuses)
        cur.execute(
            "INSERT INTO ipfs_storage (user_id, ipfs_hash, storage_date, content_type, encryption_status) VALUES (%s, %s, %s, %s, %s) RETURNING content_id",
            (user_id, ipfs_hash, storage_date, content_type, encryption_status)
        )
        content_id = cur.fetchone()[0]
        storage_ids.append(content_id)
    conn.commit()
    cur.close()
    return storage_ids

def main():
    conn = connect_db()
    if not conn:
        return
    try:
        # Insert fake data while respecting table relationships
        user_ids = insert_users(conn, num_users=500)
        identity_ids = insert_identities(conn, user_ids, num_identities=500)
        entity_ids = insert_entities(conn, num_entities=500)
        verification_ids = insert_verifications(conn, identity_ids, entity_ids, num_verifications=500)
        contract_addresses = insert_smart_contracts(conn, entity_ids, num_contracts=500)
        transaction_ids = insert_transactions(conn, user_ids, contract_addresses, verification_ids, num_transactions=500)
        storage_ids = insert_ipfs_storage(conn, user_ids, num_storage=500)
        print("✅ Fake data successfully inserted!")
    except Exception as e:
        print("❌ Error inserting fake data:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
