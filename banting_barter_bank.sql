CREATE TABLE `Users` (
    `user_id` INTEGER NOT NULL UNIQUE,
    `first_name` VARCHAR(50) NOT NULL,
    `last_name` VARCHAR(50) NOT NULL,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `phone` VARCHAR(15) NOT NULL UNIQUE,
    `address` TEXT(150),
    `date_created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`user_id`)
);

CREATE TABLE `Accounts` (
    `account_no` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
    `user_id` INTEGER NOT NULL,
    `account_type` VARCHAR(20) CHECK (account_type IN ('savings', 'checking')),
    `balance` DECIMAL DEFAULT 0.00,
    `interest_rate` DECIMAL DEFAULT 0.00 COMMENT 'Interest rate for savings accounts',
    `date_created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`account_no`),
    FOREIGN KEY (`user_id`) REFERENCES `Users`(`user_id`) ON UPDATE NO ACTION ON DELETE CASCADE
);

CREATE TABLE `Transactions` (
    `transaction_id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
    `account_no` INTEGER NOT NULL,
    `transaction_type` VARCHAR(20) CHECK (transaction_type IN ('deposit', 'withdrawal', 'loan_payment')),
    `amount` DECIMAL NOT NULL CHECK (amount > 0),
    `transaction_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`transaction_id`),
    FOREIGN KEY (`account_no`) REFERENCES `Accounts`(`account_no`) ON UPDATE NO ACTION ON DELETE CASCADE
);

CREATE TABLE `Loans` (
    `loan_id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
    `user_id` INTEGER NOT NULL,
    `loan_amount` DECIMAL NOT NULL CHECK (loan_amount > 0),
    `interest_rate` DECIMAL NOT NULL,
    `loan_term` INTEGER NOT NULL CHECK (loan_term > 0),
    `monthly_payment` DECIMAL NOT NULL,
    `status` VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paid', 'defaulted')),
    `date_created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`loan_id`),
    FOREIGN KEY (`user_id`) REFERENCES `Users`(`user_id`) ON UPDATE NO ACTION ON DELETE CASCADE
);

CREATE TABLE `Loan_Payments` (
    `payment_id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
    `loan_id` INTEGER NOT NULL,
    `amount_paid` DECIMAL NOT NULL CHECK (amount_paid > 0),
    `payment_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`payment_id`),
    FOREIGN KEY (`loan_id`) REFERENCES `Loans`(`loan_id`) ON UPDATE NO ACTION ON DELETE CASCADE
);
