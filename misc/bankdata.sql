-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 28, 2025 at 03:08 AM
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
-- Database: `bankdata`
--

-- --------------------------------------------------------

--
-- Table structure for table `accounts`
--

CREATE TABLE `accounts` (
  `account_no` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `account_type` varchar(20) DEFAULT NULL CHECK (`account_type` in ('savings','checking')),
  `balance` decimal(15,2) NOT NULL DEFAULT 0.00,
  `interest_rate` decimal(10,0) DEFAULT 0 COMMENT 'Interest rate for savings accounts',
  `date_created` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `accounts`
--

INSERT INTO `accounts` (`account_no`, `user_id`, `account_type`, `balance`, `interest_rate`, `date_created`) VALUES
(20010, 2, 'checking', 100.00, 0, '2025-04-27 23:16:25'),
(20011, 3, 'checking', 204.88, 0, '2025-04-27 23:18:19'),
(20012, 3, 'savings', 190.00, 0, '2025-04-27 23:18:19');

-- --------------------------------------------------------

--
-- Table structure for table `loans`
--

CREATE TABLE `loans` (
  `loan_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `loan_amount` decimal(15,2) NOT NULL,
  `interest_rate` decimal(10,0) NOT NULL,
  `loan_term` int(11) NOT NULL CHECK (`loan_term` > 0),
  `monthly_payment` decimal(15,2) NOT NULL,
  `status` varchar(20) DEFAULT 'active' CHECK (`status` in ('active','paid','defaulted')),
  `date_created` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `loan_payments`
--

CREATE TABLE `loan_payments` (
  `payment_id` int(11) NOT NULL,
  `loan_id` int(11) NOT NULL,
  `amount_paid` decimal(15,2) NOT NULL,
  `payment_date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `transaction_id` int(11) NOT NULL,
  `account_no` int(11) NOT NULL,
  `transaction_type` varchar(20) DEFAULT NULL CHECK (`transaction_type` in ('deposit','withdrawal','loan_payment')),
  `amount` decimal(15,2) NOT NULL,
  `transaction_date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `transactions`
--

INSERT INTO `transactions` (`transaction_id`, `account_no`, `transaction_type`, `amount`, `transaction_date`) VALUES
(23, 20011, 'deposit', 2100.00, '2025-04-27 23:34:16'),
(24, 20011, 'withdrawal', -2100.00, '2025-04-27 23:36:52'),
(25, 20011, 'deposit', 210.00, '2025-04-27 23:43:00'),
(26, 20011, 'withdrawal', -5.00, '2025-04-27 23:43:15'),
(27, 20011, 'withdrawal', -0.12, '2025-04-27 23:43:20'),
(28, 20010, 'deposit', 100.00, '2025-04-28 01:02:20'),
(29, 20012, 'deposit', 210.00, '2025-04-28 01:03:59'),
(30, 20012, 'withdrawal', -20.00, '2025-04-28 01:04:04');

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
  `password` varchar(255) NOT NULL,
  `date_created` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `first_name`, `last_name`, `email`, `phone`, `address`, `password`, `date_created`) VALUES
(3, 'Jane', 'Doe', 'jane.doe@gmail.com', '3333333334', '4523 Nowhere', 'scrypt:32768:8:1$VXSxnqbrWIqHgYl5$fa7b815c08db7c1b3c37cdeda1799303797f9eb895a8b416609028660000b133f97e435d5deafa54fc8a61117133e2c36c6d23c716d35292b878f5f1a21b2525', '2025-04-27 23:18:19');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `accounts`
--
ALTER TABLE `accounts`
  ADD PRIMARY KEY (`account_no`),
  ADD UNIQUE KEY `account_no` (`account_no`),
  ADD KEY `fk_accounts_user` (`user_id`);

--
-- Indexes for table `loans`
--
ALTER TABLE `loans`
  ADD PRIMARY KEY (`loan_id`),
  ADD UNIQUE KEY `loan_id` (`loan_id`),
  ADD KEY `fk_loans_user` (`user_id`);

--
-- Indexes for table `loan_payments`
--
ALTER TABLE `loan_payments`
  ADD PRIMARY KEY (`payment_id`),
  ADD UNIQUE KEY `payment_id` (`payment_id`),
  ADD KEY `fk_loan_payments_loan` (`loan_id`);

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`transaction_id`),
  ADD UNIQUE KEY `transaction_id` (`transaction_id`),
  ADD KEY `fk_transactions_account` (`account_no`);

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
-- AUTO_INCREMENT for table `accounts`
--
ALTER TABLE `accounts`
  MODIFY `account_no` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20013;

--
-- AUTO_INCREMENT for table `loans`
--
ALTER TABLE `loans`
  MODIFY `loan_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3005;

--
-- AUTO_INCREMENT for table `loan_payments`
--
ALTER TABLE `loan_payments`
  MODIFY `payment_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=50;

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `transaction_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `accounts`
--
ALTER TABLE `accounts`
  ADD CONSTRAINT `fk_accounts_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `loans`
--
ALTER TABLE `loans`
  ADD CONSTRAINT `fk_loans_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `loan_payments`
--
ALTER TABLE `loan_payments`
  ADD CONSTRAINT `fk_loan_payments_loan` FOREIGN KEY (`loan_id`) REFERENCES `loans` (`loan_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `transactions`
--
ALTER TABLE `transactions`
  ADD CONSTRAINT `fk_transactions_account` FOREIGN KEY (`account_no`) REFERENCES `accounts` (`account_no`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
