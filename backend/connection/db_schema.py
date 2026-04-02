from backend.connection.db_connection import get_connection
 
 
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
 
   
    # ENUMS
 


 
    cursor.execute("""
    DO $$ BEGIN
        CREATE TYPE priority_level AS ENUM ('high', 'medium', 'low');
    EXCEPTION WHEN duplicate_object THEN NULL;
    END $$;
    """)
 
    cursor.execute("""
    DO $$ BEGIN
        CREATE TYPE request_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED', 'ISSUED');
    EXCEPTION WHEN duplicate_object THEN NULL;
    END $$;
    """)
 
    cursor.execute("""
    DO $$ BEGIN
        CREATE TYPE approval_status AS ENUM ('APPROVED', 'REJECTED', 'MODIFIED');
    EXCEPTION WHEN duplicate_object THEN NULL;
    END $$;
    """)
 
    cursor.execute("""
    DO $$ BEGIN
        CREATE TYPE transaction_type AS ENUM ('PURCHASE', 'ISSUE');
    EXCEPTION WHEN duplicate_object THEN NULL;
    END $$;
    """)
 
    # USERS
 
 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id              SERIAL PRIMARY KEY,
        name            VARCHAR(100) NOT NULL,
        email           VARCHAR(100) UNIQUE NOT NULL,
        role            VARCHAR(50)  NOT NULL,
        password_hash   VARCHAR(255) NOT NULL,
        contact         VARCHAR(50),
        is_active       BOOLEAN      DEFAULT TRUE,
        created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
    );
    """)
 
 
 
 
    # VENDORS
 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendors (
        id          SERIAL PRIMARY KEY,
        name        VARCHAR(100) NOT NULL,
        contact     VARCHAR(50),
        address     TEXT,
        is_active   BOOLEAN      DEFAULT TRUE,
        created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
    );
    """)
 
 

 
    # CATEGORIES
 
 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id          SERIAL PRIMARY KEY,
        name        VARCHAR(100) UNIQUE NOT NULL,
        is_active   BOOLEAN DEFAULT TRUE
    );
    """)
 
    # PRODUCTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id                  SERIAL PRIMARY KEY,
        name                VARCHAR(100) NOT NULL,
        category_id         INT          REFERENCES categories(id) ON DELETE SET NULL,
        unit                VARCHAR(20),
        shelf_life_days     INT          CHECK (shelf_life_days > 0),
        min_stock_level     INT          DEFAULT 0 CHECK (min_stock_level >= 0),
        brand_name          VARCHAR(50),
        is_active           BOOLEAN      DEFAULT TRUE,
        created_at          TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
    );
    """)
         # VENDOR PRODUCTS
 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendor_products (
        id          SERIAL PRIMARY KEY,
        vendor_id   INT            NOT NULL REFERENCES vendors(id)  ON DELETE CASCADE,
        product_id  INT            NOT NULL REFERENCES products(id) ON DELETE CASCADE,
        unit_cost   NUMERIC(10,2)           CHECK (unit_cost >= 0),
       
        is_active   BOOLEAN        DEFAULT TRUE,
        CONSTRAINT uq_vendor_product UNIQUE (vendor_id, product_id)
    );
    """)
 
   
 
    # INVENTOR.Y BATCHES
 
 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_batches (
        id                  SERIAL PRIMARY KEY,
        product_id          INT            NOT NULL REFERENCES products(id) ON DELETE CASCADE,
        vendor_id           INT                     REFERENCES vendors(id)  ON DELETE SET NULL,
        quantity            INT            NOT NULL CHECK (quantity > 0),
        quantity_available  INT            NOT NULL CHECK (quantity_available >= 0),
        unit_cost           NUMERIC(10,2)           CHECK (unit_cost >= 0),
        total_cost          NUMERIC(12,2)  GENERATED ALWAYS AS (quantity * unit_cost) STORED,
        purchase_date       DATE           DEFAULT CURRENT_DATE,
        expiry_date         DATE,
        created_at          TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT chk_available_lte_qty CHECK (quantity_available <= quantity)
    );
    """)
 
 
    # REQUESTS
 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id              SERIAL PRIMARY KEY,
        requested_by    INT            REFERENCES users(id) ON DELETE SET NULL,
        status          request_status DEFAULT 'PENDING',
        priority        priority_level DEFAULT 'medium',
        reason          TEXT,
        request_date    DATE           DEFAULT CURRENT_DATE,
        created_at      TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
    );
    """)
 
 
    # REQUEST ITEMS
 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS request_items (
        id                  SERIAL PRIMARY KEY,
        request_id          INT  NOT NULL REFERENCES requests(id)  ON DELETE CASCADE,
        product_id          INT  NOT NULL REFERENCES products(id)  ON DELETE RESTRICT,
        requested_quantity  INT  NOT NULL CHECK (requested_quantity > 0),
        approved_quantity   INT           CHECK (approved_quantity >= 0),
        fulfilled_quantity  INT  DEFAULT 0 CHECK (fulfilled_quantity >= 0)
    );
    """)
 
    # REQUEST APPROVALS
 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS request_approvals (
        id               SERIAL PRIMARY KEY,
        request_id       INT             NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
        approved_by      INT                      REFERENCES users(id)    ON DELETE SET NULL,
        approval_status  approval_status NOT NULL,
        remarks          TEXT,
        approval_date    TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
    );
    """)
 
    # STOCK TRANSACTIONS
 
 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_transactions (
        id                SERIAL PRIMARY KEY,
        batch_id          INT              NOT NULL REFERENCES inventory_batches(id) ON DELETE RESTRICT,
        product_id        INT              NOT NULL REFERENCES products(id)          ON DELETE RESTRICT,
        request_item_id   INT                       REFERENCES request_items(id)     ON DELETE SET NULL,
        transaction_type  transaction_type NOT NULL,
        quantity          INT              NOT NULL CHECK (quantity > 0),
        performed_by      INT                       REFERENCES users(id)             ON DELETE SET NULL,
        created_at        TIMESTAMP        DEFAULT CURRENT_TIMESTAMP
    );
    """)
 
 
    # AUDIT LOGS
 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id           SERIAL PRIMARY KEY,
        user_id      INT       REFERENCES users(id) ON DELETE SET NULL,
        action_type  VARCHAR(50),
        entity_name  VARCHAR(50),
        entity_id    INT,
        action_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        description  TEXT
    );
    """)
 
 
    # INDEXES
 
 
    indexes = [
     
        "CREATE INDEX IF NOT EXISTS idx_batch_product_fifo     ON inventory_batches(product_id, purchase_date ASC) WHERE quantity_available > 0;",
        "CREATE INDEX IF NOT EXISTS idx_batch_expiry           ON inventory_batches(expiry_date) WHERE expiry_date IS NOT NULL;",
        "CREATE INDEX IF NOT EXISTS idx_batch_vendor           ON inventory_batches(vendor_id);",
        "CREATE INDEX IF NOT EXISTS idx_product_category       ON products(category_id);",
        "CREATE INDEX IF NOT EXISTS idx_vendor_product_vendor  ON vendor_products(vendor_id);",
        "CREATE INDEX IF NOT EXISTS idx_vendor_product_product ON vendor_products(product_id);",
        "CREATE INDEX IF NOT EXISTS idx_req_pending            ON requests(id) WHERE status = 'PENDING';",
        "CREATE INDEX IF NOT EXISTS idx_req_status             ON requests(status);",
        "CREATE INDEX IF NOT EXISTS idx_req_requested_by       ON requests(requested_by);",
        "CREATE INDEX IF NOT EXISTS idx_req_item_request       ON request_items(request_id);",
        "CREATE INDEX IF NOT EXISTS idx_req_item_product       ON request_items(product_id);",
        "CREATE INDEX IF NOT EXISTS idx_req_approval_request   ON request_approvals(request_id);",
        "CREATE INDEX IF NOT EXISTS idx_tx_product             ON stock_transactions(product_id);",
        "CREATE INDEX IF NOT EXISTS idx_tx_batch               ON stock_transactions(batch_id);",
        "CREATE INDEX IF NOT EXISTS idx_tx_type                ON stock_transactions(transaction_type);",
        "CREATE INDEX IF NOT EXISTS idx_tx_req_item            ON stock_transactions(request_item_id);",
        "CREATE INDEX IF NOT EXISTS idx_tx_product_date        ON stock_transactions(product_id, created_at);",
        "CREATE INDEX IF NOT EXISTS idx_audit_user             ON audit_logs(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_audit_entity           ON audit_logs(entity_name, entity_id);",
    ]
 
    for idx in indexes:
        cursor.execute(idx)
 
    conn.commit()
    cursor.close()
    conn.close()
 
    print("All tables, ENUMs, and indexes created successfully!")
 
 
if __name__ == "__main__":
    create_tables()
 