-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 12, 2026 at 05:59 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `rodcafe_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `admin_id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`admin_id`, `username`, `password_hash`) VALUES
(1, 'admin', 'admin123');

-- --------------------------------------------------------

--
-- Table structure for table `customers`
--

CREATE TABLE `customers` (
  `customer_id` int(11) NOT NULL,
  `customerName` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customers`
--

INSERT INTO `customers` (`customer_id`, `customerName`) VALUES
(1, 'AJ'),
(2, 'MJ'),
(3, 'Rod'),
(4, 'Karlo'),
(5, 'NEIL'),
(6, 'JAWEL'),
(7, 'Jacob'),
(8, 'Maria'),
(9, 'Cousin'),
(10, 'Celine');

-- --------------------------------------------------------

--
-- Table structure for table `menu_items`
--

CREATE TABLE `menu_items` (
  `item_id` int(11) NOT NULL,
  `itemName` varchar(100) NOT NULL,
  `category` varchar(50) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `stock` int(11) NOT NULL DEFAULT 50
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `menu_items`
--

INSERT INTO `menu_items` (`item_id`, `itemName`, `category`, `price`, `stock`) VALUES
(100, 'Americano', 'Coffee', 130.00, 47),
(101, 'Latte', 'Coffee', 145.00, 47),
(102, 'Macchiato', 'Coffee', 150.00, 45),
(103, 'Cappuccino', 'Coffee', 150.00, 50),
(104, 'Matcha', 'Non-Coffee', 130.00, 47),
(105, 'Cookies-and-Cream', 'Non-Coffee', 140.00, 49),
(106, 'Strawberry', 'Non-Coffee', 140.00, 49),
(107, 'Brownies', 'Pastries', 90.00, 40),
(108, 'Banana-Bread', 'Pastries', 120.00, 48),
(109, 'Smores', 'Pastries', 90.00, 0),
(110, 'Crinkles', 'Pastries', 80.00, 50);

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `order_id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `serviceType` varchar(10) NOT NULL,
  `paymentOption` varchar(15) NOT NULL,
  `totalAmount` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`order_id`, `customer_id`, `serviceType`, `paymentOption`, `totalAmount`) VALUES
(5001, 1, 'Take-out', 'Card', 370.00),
(5002, 2, 'Dine-in', 'Cash', 555.00),
(5003, 3, 'Dine-in', 'Cash', 575.00),
(5004, 4, 'Dine-in', 'Cash', 130.00),
(5005, 5, 'Dine-in', 'Cash', 250.00),
(5006, 6, 'Dine-in', 'Cash', 130.00),
(5007, 7, 'Take-out', 'Card', 145.00),
(5008, 8, 'Take-out', 'Card', 130.00),
(5009, 9, 'Take-out', 'Card', 270.00),
(5010, 10, 'Take-out', 'Card', 280.00);

-- --------------------------------------------------------

--
-- Table structure for table `order_details`
--

CREATE TABLE `order_details` (
  `detail_id` int(11) NOT NULL,
  `order_id` int(11) DEFAULT NULL,
  `item_id` int(11) DEFAULT NULL,
  `quantity` int(11) NOT NULL,
  `customization` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `order_details`
--

INSERT INTO `order_details` (`detail_id`, `order_id`, `item_id`, `quantity`, `customization`) VALUES
(9000, 5001, 100, 1, 'Extra shots of Espresso'),
(9001, 5001, 102, 1, ''),
(9002, 5001, 107, 1, ''),
(9003, 5002, 101, 1, 'Oatside milk'),
(9004, 5002, 102, 1, 'Extra Caramel'),
(9005, 5002, 106, 1, ''),
(9006, 5002, 108, 1, ''),
(9007, 5003, 100, 1, 'Extra extra shots of espresso'),
(9008, 5003, 101, 1, ''),
(9009, 5003, 102, 2, ''),
(9010, 5004, 100, 1, ''),
(9011, 5005, 100, 1, ''),
(9012, 5005, 108, 1, ''),
(9013, 5006, 100, 1, ''),
(9014, 5007, 101, 1, ''),
(9015, 5008, 104, 1, ''),
(9016, 5009, 104, 1, ''),
(9017, 5009, 105, 1, ''),
(9018, 5010, 102, 1, ''),
(9019, 5010, 104, 1, '');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `customers`
--
ALTER TABLE `customers`
  ADD PRIMARY KEY (`customer_id`);

--
-- Indexes for table `menu_items`
--
ALTER TABLE `menu_items`
  ADD PRIMARY KEY (`item_id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`order_id`),
  ADD KEY `customer_id` (`customer_id`);

--
-- Indexes for table `order_details`
--
ALTER TABLE `order_details`
  ADD PRIMARY KEY (`detail_id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `item_id` (`item_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `customers`
--
ALTER TABLE `customers`
  MODIFY `customer_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `menu_items`
--
ALTER TABLE `menu_items`
  MODIFY `item_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=111;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `order_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5011;

--
-- AUTO_INCREMENT for table `order_details`
--
ALTER TABLE `order_details`
  MODIFY `detail_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9020;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`);

--
-- Constraints for table `order_details`
--
ALTER TABLE `order_details`
  ADD CONSTRAINT `order_details_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
  ADD CONSTRAINT `order_details_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `menu_items` (`item_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
