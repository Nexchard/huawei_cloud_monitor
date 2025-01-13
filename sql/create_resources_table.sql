CREATE TABLE IF NOT EXISTS resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_name VARCHAR(100) NOT NULL,
    resource_name VARCHAR(255) NOT NULL,
    resource_id VARCHAR(100) NOT NULL,
    service_type VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    expire_time DATETIME NOT NULL,
    project_name VARCHAR(100),
    remaining_days INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_account_name (account_name),
    INDEX idx_resource_id (resource_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; 