CREATE TABLE IF NOT EXISTS stored_cards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_name VARCHAR(100) NOT NULL,
    card_id VARCHAR(100) NOT NULL,
    card_name VARCHAR(255) NOT NULL,
    face_value DECIMAL(10,2) NOT NULL,
    balance DECIMAL(10,2) NOT NULL,
    effective_time DATETIME NOT NULL,
    expire_time DATETIME NOT NULL,
    batch_number VARCHAR(20) NOT NULL,  -- 数据批次号，格式：YYYYMMDDHHmmss
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_account_name (account_name),
    INDEX idx_card_id (card_id),
    INDEX idx_batch_number (batch_number),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; 