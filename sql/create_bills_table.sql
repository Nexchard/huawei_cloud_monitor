CREATE TABLE IF NOT EXISTS account_bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_name VARCHAR(100) NOT NULL,
    project_name VARCHAR(100) NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    cycle VARCHAR(7) NOT NULL,  -- 账单周期，格式：YYYY-MM
    batch_number VARCHAR(20) NOT NULL,  -- 数据批次号，格式：YYYYMMDDHHmmss
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_account_name (account_name),
    INDEX idx_project_name (project_name),
    INDEX idx_cycle (cycle),
    INDEX idx_batch_number (batch_number),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; 