-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 18, 2025 at 05:22 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `banting_barter_bank`
--

-- --------------------------------------------------------

--
-- Table structure for table `accounts`
--

CREATE TABLE `accounts` (
  `account_no` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `account_type` varchar(20) DEFAULT NULL CHECK (`account_type` in ('savings','checking')),
  `balance` decimal(15,2) DEFAULT 0.00,
  `interest_rate` decimal(15,2) DEFAULT 0.00 COMMENT 'Interest rate for savings accounts',
  `date_created` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `accounts`
--

INSERT INTO `accounts` (`account_no`, `user_id`, `account_type`, `balance`, `interest_rate`, `date_created`) VALUES
(20001, 1001, 'checking', 1250.75, 0.00, '2025-04-08 15:55:02'),
(20002, 1002, 'savings', 8450.25, 1.50, '2025-04-08 15:55:02'),
(20003, 1003, 'checking', 320.50, 0.00, '2025-04-08 15:55:02'),
(20004, 1004, 'savings', 12500.00, 2.00, '2025-04-08 15:55:02'),
(20005, 1005, 'checking', 750.00, 0.00, '2025-04-08 15:55:02'),
(20006, 1001, 'savings', 5000.00, 1.75, '2025-04-08 15:55:02'),
(20007, 1003, 'savings', 2500.00, 1.25, '2025-04-08 15:55:02');

-- --------------------------------------------------------

--
-- Table structure for table `loans`
--

CREATE TABLE `loans` (
  `loan_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `loan_amount` decimal(15,2) NOT NULL CHECK (`loan_amount` > 0),
  `interest_rate` decimal(15,2) NOT NULL,
  `loan_term` int(11) NOT NULL CHECK (`loan_term` > 0),
  `monthly_payment` decimal(15,2) NOT NULL,
  `status` varchar(20) DEFAULT 'active' CHECK (`status` in ('active','paid','defaulted')),
  `date_created` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `loans`
--

INSERT INTO `loans` (`loan_id`, `user_id`, `loan_amount`, `interest_rate`, `loan_term`, `monthly_payment`, `status`, `date_created`) VALUES
(3001, 1001, 10000.00, 5.00, 60, 188.71, 'active', '2025-04-08 15:57:52'),
(3002, 1003, 5000.00, 6.00, 36, 152.11, 'active', '2025-04-08 15:57:52'),
(3003, 1004, 20000.00, 4.50, 72, 316.72, 'active', '2025-04-08 15:57:52'),
(3004, 1002, 7500.00, 5.50, 48, 174.25, 'paid', '2025-04-08 15:57:52');

-- --------------------------------------------------------

--
-- Table structure for table `loan_payments`
--

CREATE TABLE `loan_payments` (
  `payment_id` int(11) NOT NULL,
  `loan_id` int(11) NOT NULL,
  `amount_paid` decimal(15,2) NOT NULL CHECK (`amount_paid` > 0),
  `payment_date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `loan_payments`
--

INSERT INTO `loan_payments` (`payment_id`, `loan_id`, `amount_paid`, `payment_date`) VALUES
(1, 3001, 188.71, '2025-04-08 15:57:59'),
(2, 3001, 188.71, '2025-04-08 15:57:59'),
(3, 3001, 188.71, '2025-04-08 15:57:59'),
(4, 3002, 152.11, '2025-04-08 15:57:59'),
(5, 3002, 152.11, '2025-04-08 15:57:59'),
(6, 3003, 316.72, '2025-04-08 15:57:59'),
(7, 3004, 174.25, '2025-04-08 15:57:59'),
(8, 3004, 174.25, '2025-04-08 15:57:59'),
(9, 3004, 174.25, '2025-04-08 15:57:59'),
(10, 3004, 174.25, '2025-04-08 15:57:59'),
(11, 3004, 174.25, '2025-04-08 15:57:59'),
(12, 3004, 174.25, '2025-04-08 15:57:59'),
(13, 3004, 174.25, '2025-04-08 15:57:59'),
(14, 3004, 174.25, '2025-04-08 15:57:59'),
(15, 3004, 174.25, '2025-04-08 15:57:59'),
(16, 3004, 174.25, '2025-04-08 15:57:59'),
(17, 3004, 174.25, '2025-04-08 15:57:59'),
(18, 3004, 174.25, '2025-04-08 15:57:59'),
(19, 3004, 174.25, '2025-04-08 15:57:59'),
(20, 3004, 174.25, '2025-04-08 15:57:59'),
(21, 3004, 174.25, '2025-04-08 15:57:59'),
(22, 3004, 174.25, '2025-04-08 15:57:59'),
(23, 3004, 174.25, '2025-04-08 15:57:59'),
(24, 3004, 174.25, '2025-04-08 15:57:59'),
(25, 3004, 174.25, '2025-04-08 15:57:59'),
(26, 3004, 174.25, '2025-04-08 15:57:59'),
(27, 3004, 174.25, '2025-04-08 15:57:59'),
(28, 3004, 174.25, '2025-04-08 15:57:59'),
(29, 3004, 174.25, '2025-04-08 15:57:59'),
(30, 3004, 174.25, '2025-04-08 15:57:59'),
(31, 3004, 174.25, '2025-04-08 15:57:59'),
(32, 3004, 174.25, '2025-04-08 15:57:59'),
(33, 3004, 174.25, '2025-04-08 15:57:59'),
(34, 3004, 174.25, '2025-04-08 15:57:59'),
(35, 3004, 174.25, '2025-04-08 15:57:59'),
(36, 3004, 174.25, '2025-04-08 15:57:59'),
(37, 3004, 174.25, '2025-04-08 15:57:59'),
(38, 3004, 174.25, '2025-04-08 15:57:59'),
(39, 3004, 174.25, '2025-04-08 15:57:59'),
(40, 3004, 174.25, '2025-04-08 15:57:59'),
(41, 3004, 174.25, '2025-04-08 15:57:59'),
(42, 3004, 174.25, '2025-04-08 15:57:59'),
(43, 3004, 174.25, '2025-04-08 15:57:59'),
(44, 3004, 174.25, '2025-04-08 15:57:59'),
(45, 3004, 174.25, '2025-04-08 15:57:59'),
(46, 3004, 174.25, '2025-04-08 15:57:59'),
(47, 3004, 174.25, '2025-04-08 15:57:59'),
(48, 3004, 174.25, '2025-04-08 15:57:59');

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `transaction_id` int(11) NOT NULL,
  `account_no` int(11) NOT NULL,
  `transaction_type` varchar(20) DEFAULT NULL CHECK (`transaction_type` in ('deposit','withdrawal','loan_payment')),
  `amount` decimal(15,2) NOT NULL CHECK (`amount` > 0),
  `transaction_date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `transactions`
--

INSERT INTO `transactions` (`transaction_id`, `account_no`, `transaction_type`, `amount`, `transaction_date`) VALUES
(12, 20001, 'deposit', 500.00, '2025-04-08 15:57:45'),
(13, 20001, 'withdrawal', 100.00, '2025-04-08 15:57:45'),
(14, 20002, 'deposit', 1000.00, '2025-04-08 15:57:45'),
(15, 20003, 'deposit', 200.00, '2025-04-08 15:57:45'),
(16, 20004, 'deposit', 5000.00, '2025-04-08 15:57:45'),
(17, 20005, 'deposit', 750.00, '2025-04-08 15:57:45'),
(18, 20006, 'deposit', 5000.00, '2025-04-08 15:57:45'),
(19, 20007, 'deposit', 2500.00, '2025-04-08 15:57:45'),
(20, 20001, 'deposit', 850.75, '2025-04-08 15:57:45'),
(21, 20002, 'deposit', 7450.25, '2025-04-08 15:57:45'),
(22, 20003, 'withdrawal', 79.50, '2025-04-08 15:57:45');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `address` text DEFAULT NULL,
  `date_created` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `first_name`, `last_name`, `email`, `phone`, `address`, `date_created`) VALUES
(1001, 'John', 'Smith', 'john.smith@email.com', '555-123-4567', '123 Main St, Anytown, USA', '2025-04-08 15:54:43'),
(1002, 'Emily', 'Johnson', 'emily.j@email.com', '555-234-5678', '456 Oak Ave, Somewhere, USA', '2025-04-08 15:54:43'),
(1003, 'Michael', 'Williams', 'michael.w@email.com', '555-345-6789', '789 Pine Rd, Nowhere, USA', '2025-04-08 15:54:43'),
(1004, 'Sarah', 'Brown', 'sarah.b@email.com', '555-456-7890', '321 Elm St, Anywhere, USA', '2025-04-08 15:54:43'),
(1005, 'David', 'Jones', 'david.j@email.com', '555-567-8901', '654 Maple Dr, Everywhere, USA', '2025-04-08 15:54:43');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `accounts`
--
ALTER TABLE `accounts`
  ADD PRIMARY KEY (`account_no`),
  ADD UNIQUE KEY `account_no` (`account_no`);

--
-- Indexes for table `loans`
--
ALTER TABLE `loans`
  ADD PRIMARY KEY (`loan_id`),
  ADD UNIQUE KEY `loan_id` (`loan_id`);

--
-- Indexes for table `loan_payments`
--
ALTER TABLE `loan_payments`
  ADD PRIMARY KEY (`payment_id`),
  ADD UNIQUE KEY `payment_id` (`payment_id`);

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`transaction_id`),
  ADD UNIQUE KEY `transaction_id` (`transaction_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `phone` (`phone`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `loans`
--
ALTER TABLE `loans`
  MODIFY `loan_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3005;

--
-- AUTO_INCREMENT for table `loan_payments`
--
ALTER TABLE `loan_payments`
  MODIFY `payment_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=49;

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `transaction_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `accounts`
--
ALTER TABLE `accounts`
  ADD CONSTRAINT `accounts_ibfk_1` FOREIGN KEY (`account_no`) REFERENCES `transactions` (`account_no`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Constraints for table `loans`
--
ALTER TABLE `loans`
  ADD CONSTRAINT `loans_ibfk_1` FOREIGN KEY (`loan_id`) REFERENCES `loan_payments` (`loan_id`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `accounts` (`user_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  ADD CONSTRAINT `users_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `loans` (`user_id`) ON DELETE CASCADE ON UPDATE NO ACTION;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
