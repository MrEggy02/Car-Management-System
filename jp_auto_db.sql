-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jun 25, 2026 at 08:38 PM
-- Server version: 8.4.3
-- PHP Version: 8.3.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `jp_auto_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `brands`
--

CREATE TABLE `brands` (
  `id` int NOT NULL,
  `name` varchar(100) NOT NULL COMMENT 'ຊື່ແບນລົດ (ເຊັ່ນ: Toyota, Honda, Isuzu, Ford)',
  `status` enum('active','inactive') DEFAULT 'active' COMMENT 'ສະຖານະ'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='ຂໍ້ມູນແບນລົດ';

--
-- Dumping data for table `brands`
--

INSERT INTO `brands` (`id`, `name`, `status`) VALUES
(1, 'Toyota', 'active'),
(2, 'Honda', 'active'),
(3, 'Isuzu', 'active'),
(4, 'Ford', 'active'),
(5, 'Mitsubishi', 'active'),
(6, 'Nissan', 'active'),
(7, 'Mazda', 'active'),
(8, 'Suzuki', 'active'),
(9, 'Hyundai', 'active'),
(10, 'Kia', 'active');

-- --------------------------------------------------------

--
-- Table structure for table `customers`
--

CREATE TABLE `customers` (
  `id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `address` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `customers`
--

INSERT INTO `customers` (`id`, `name`, `phone`, `address`, `created_at`) VALUES
(1, 'ສົມພອນ ແກ້ວມະນີ', '02012345678', 'ບ້ານດົງໂດກ, ເມືອງຈັນທະບູລີ, ນະຄອນຫຼວງວຽງຈັນ', '2026-04-27 07:47:07'),
(2, 'ບຸນມີ ສີຫາວົງ', '02098765432', 'ບ້ານສີເມືອງ, ເມືອງສີໂຄດຕະບອງ, ນະຄອນຫຼວງວຽງຈັນ', '2026-04-27 07:47:07'),
(3, 'ຄຳພອນ ຈັນທະວົງ', '02055551234', 'ບ້ານຫາດຊາຍ, ເມືອງໄຊເສດຖາ, ນະຄອນຫຼວງວຽງຈັນ', '2026-04-27 07:47:07'),
(4, 'Somchai Siphandone', '02011112222', 'House No. 123, Luang Prabang Road, Vientiane Capital', '2026-04-27 07:47:07'),
(5, 'ວິໄລວັນ ສຸກສະຫວັນ', '02033334444', 'ບ້ານໂພນໃສ, ເມືອງຈັນທະບູລີ, ນະຄອນຫຼວງວຽງຈັນ', '2026-04-27 07:47:07'),
(6, 'ທອງດີ ມະນີວົງ', '02077778888', 'ບ້ານດອນນົກຂຸ້ມ, ເມືອງສີສັດຕະນາກ, ນະຄອນຫຼວງວຽງຈັນ', '2026-04-27 07:47:07'),
(7, 'ສຸລີວັນ ພົມມະຫາໄຊ', '02099990000', 'ບ້ານສັນຕິພາບ, ເມືອງໄຊທານີ, ນະຄອນຫຼວງວຽງຈັນ', '2026-04-27 07:47:07'),
(8, 'Phet Sayavong', '02012340000', 'Unit 5, T2 Road, Vientiane Capital', '2026-04-27 07:47:07'),
(9, 'ດາວອນ ຈັນທະວົງສາ', '02045670000', 'ບ້ານສວນແກ້ວ, ເມືອງຫຼວງພະບາງ, ແຂວງຫຼວງພະບາງ', '2026-04-27 07:47:07'),
(10, 'ຄຳສຸກ ວົງພະຈັນ', '02088889999', 'ບ້ານທ່າເດື່ອ, ເມືອງປາກຊັນ, ແຂວງບໍລິຄໍາໄຊ', '2026-04-27 07:47:07'),
(11, 'ເອກະວິນ ດາລາວົງໄຊ', '020 91625415', 'Xiangkhouang', '2026-04-27 08:31:37'),
(20, 'ເອກະວິນ ດາລາວົງໄຊ', '02058641879', 'Xiangkhouang', '2026-04-27 08:33:41'),
(22, 'ເອກະວິນ ດາລາວົງໄຊ', '2058641879', 'Xiangkhouang', '2026-04-27 08:34:38'),
(24, 'Ekavin dalavong', '2098768797', 'Lkdsf', '2026-04-27 08:36:18'),
(31, 'ທະວັດໄຊ ອິນທາ', '0209187678', 'ຫ້ວຍຫົງ', '2026-04-27 08:48:37'),
(32, 'bank', '123', 'sva', '2026-06-05 05:35:46'),
(44, 'hg', '2099999999', 'vt', '2026-06-05 17:28:20'),
(47, 'ຈອນສັນ', '2029898811', 'ໂພນພະເນົາ', '2026-06-09 10:50:36'),
(48, 'ທ. ທອງມີ ໄຊມີສຸກ', '2091887716', 'ບ້ານ ສີເມືອງ ເມືອງ ສີສັດຕະນາກ ນະຄອນຫລວງວຽຈັນ', '2026-06-12 07:01:30'),
(49, 'ທ. ແສງປະເສີດ ໄຊຍະສິດ', '2091878718', 'ໂພນພະເນົາ', '2026-06-12 07:18:38'),
(51, 'ຢ', 'ຢ', 'ຢ', '2026-06-24 05:57:32');

-- --------------------------------------------------------

--
-- Table structure for table `employees`
--

CREATE TABLE `employees` (
  `id` int NOT NULL,
  `name` varchar(100) NOT NULL COMMENT 'ຊື່ພະນັກງານ',
  `phone` varchar(20) DEFAULT NULL COMMENT 'ເບີໂທ',
  `role` enum('admin','mechanic','cashier') DEFAULT 'admin' COMMENT 'ບົດບາດ',
  `status` enum('active','inactive') DEFAULT 'active' COMMENT 'ສະຖານະ',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'ວັນທີສ້າງ',
  `username` varchar(50) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `can_login` tinyint(1) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='ຂໍ້ມູນພະນັກງານ';

--
-- Dumping data for table `employees`
--

INSERT INTO `employees` (`id`, `name`, `phone`, `role`, `status`, `created_at`, `username`, `password`, `can_login`) VALUES
(1, 'ເຈົ້າຂອງຮ້ານ', '0200000001', 'admin', 'active', '2026-04-07 15:17:11', 'admin', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 1),
(2, 'ເອກະວິນ ດາລາວົງໄຊ ', '02091625415', 'mechanic', 'active', '2026-04-07 15:17:11', NULL, NULL, 0),
(3, 'ແສງສະຫວັນ ແສນຍາກອນ', '0205871980', 'cashier', 'active', '2026-04-07 15:17:11', 'user', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 1),
(4, 'ຊ່າງ ໜຶ່ງ', '020321654', 'mechanic', 'active', '2026-06-18 03:07:51', NULL, NULL, 0),
(5, '1', '1', 'admin', 'active', '2026-06-18 05:05:52', '111', 'f6e0a1e2ac41945a9aa7ff8a8aaa0cebc12a3bcc981a929ad5cf810a090e11ae', 1);

-- --------------------------------------------------------

--
-- Table structure for table `goods_receipts`
--

CREATE TABLE `goods_receipts` (
  `id` int NOT NULL,
  `receipt_no` varchar(50) NOT NULL COMMENT 'Receipt Number',
  `purchase_order_id` int NOT NULL COMMENT 'Reference PO (if any)',
  `supplier_id` int NOT NULL COMMENT 'Supplier',
  `reference_doc` varchar(100) DEFAULT NULL COMMENT 'Supplier document/invoice number',
  `receipt_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Date received',
  `total_amount` decimal(15,2) NOT NULL DEFAULT '0.00' COMMENT 'Total amount',
  `note` text COMMENT 'Notes',
  `status` enum('received','cancelled') NOT NULL DEFAULT 'received' COMMENT 'Status',
  `received_by` int NOT NULL COMMENT 'Employee who received it'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Goods receipt header';

--
-- Dumping data for table `goods_receipts`
--

INSERT INTO `goods_receipts` (`id`, `receipt_no`, `purchase_order_id`, `supplier_id`, `reference_doc`, `receipt_date`, `total_amount`, `note`, `status`, `received_by`) VALUES
(1, 'GR-2026-0001', 6, 11, NULL, '2026-06-19 06:52:31', 200000.00, NULL, 'received', 1),
(2, 'GR-2026-0002', 6, 11, NULL, '2026-06-19 06:52:32', 300000.00, NULL, 'received', 1),
(3, 'GR-2026-0003', 5, 11, NULL, '2026-06-19 08:41:26', 250000.00, NULL, 'received', 1),
(4, 'GR-2026-0004', 7, 11, NULL, '2026-06-19 09:57:02', 3000000.00, NULL, 'received', 1),
(5, 'GR-2026-0005', 9, 11, NULL, '2026-06-19 10:40:09', 67.00, NULL, 'received', 1),
(6, 'GR-2026-0006', 5, 11, NULL, '2026-06-22 08:58:44', 300000.00, NULL, 'received', 1),
(7, 'GR-2026-0007', 10, 11, NULL, '2026-06-24 16:48:50', 60000.00, NULL, 'received', 1);

-- --------------------------------------------------------

--
-- Table structure for table `goods_receipt_items`
--

CREATE TABLE `goods_receipt_items` (
  `id` int NOT NULL,
  `receipt_id` int NOT NULL COMMENT 'Goods receipt ID',
  `part_id` int NOT NULL COMMENT 'Received Part',
  `qty_received` int NOT NULL COMMENT 'Actual quantity received',
  `cost_price` decimal(15,2) NOT NULL COMMENT 'Cost price per unit',
  `total_price` decimal(15,2) NOT NULL COMMENT 'Total price'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Goods receipt items';

--
-- Dumping data for table `goods_receipt_items`
--

INSERT INTO `goods_receipt_items` (`id`, `receipt_id`, `part_id`, `qty_received`, `cost_price`, `total_price`) VALUES
(1, 1, 74, 4, 50000.00, 200000.00),
(2, 2, 74, 6, 50000.00, 300000.00),
(3, 3, 74, 5, 50000.00, 250000.00),
(4, 4, 70, 1, 3000000.00, 3000000.00),
(5, 5, 74, 1, 67.00, 67.00),
(6, 6, 74, 5, 60000.00, 300000.00),
(7, 7, 74, 1, 60000.00, 60000.00);

-- --------------------------------------------------------

--
-- Table structure for table `invoices`
--

CREATE TABLE `invoices` (
  `id` int NOT NULL,
  `job_order_id` int NOT NULL COMMENT 'ໃບຮັບລົດ',
  `total_amount` decimal(15,2) NOT NULL DEFAULT '0.00' COMMENT 'ຍອດລວມ',
  `total_discount` decimal(15,2) DEFAULT '0.00' COMMENT 'ສ່ວນຫຼຸດລວມ',
  `final_total` decimal(15,2) NOT NULL DEFAULT '0.00' COMMENT 'ຍອດສຸດທ້າຍ',
  `payment_method` enum('cash','transfer') NOT NULL,
  `paid_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'ວັນທີຈ່າຍ',
  `payment_status` enum('pending','paid') NOT NULL DEFAULT 'pending',
  `received_amount` decimal(15,2) DEFAULT '0.00' COMMENT 'ຮັບເງິນມາ',
  `change_amount` decimal(15,2) DEFAULT '0.00' COMMENT 'ທອນເງິນ',
  `created_by` int NOT NULL COMMENT 'ຜູ້ສ້າງໃບເກັບເງິນ'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='ຂໍ້ມູນໃບເກັບເງິນ';

--
-- Dumping data for table `invoices`
--

INSERT INTO `invoices` (`id`, `job_order_id`, `total_amount`, `total_discount`, `final_total`, `payment_method`, `paid_date`, `payment_status`, `received_amount`, `change_amount`, `created_by`) VALUES
(1, 2, 950000.00, 0.00, 950000.00, 'transfer', '2026-05-06 08:55:04', 'paid', 950000.00, 0.00, 1),
(2, 1, 15700000.00, 0.00, 15700000.00, 'cash', '2026-05-06 09:58:41', 'paid', 20000000.00, 4300000.00, 1),
(3, 5, 100000.00, 0.00, 100000.00, 'cash', '2026-06-05 06:06:47', 'paid', 100000.00, 0.00, 1),
(4, 6, 3100000.00, 0.00, 3100000.00, 'cash', '2026-06-12 04:39:11', 'paid', 3100000.00, 0.00, 1),
(5, 3, 0.00, 0.00, 0.00, 'cash', '2026-06-12 04:42:12', 'paid', 0.00, 0.00, 1),
(6, 8, 0.00, 0.00, 0.00, 'transfer', '2026-06-12 07:24:52', 'paid', 500000.00, 500000.00, 1),
(7, 16, 150000.00, 0.00, 150000.00, 'transfer', '2026-06-18 03:42:05', 'paid', 150000.00, 0.00, 1),
(8, 20, 1500400.00, 0.00, 1500400.00, 'cash', '2026-06-18 08:33:59', 'paid', 1500400.00, 0.00, 1),
(9, 13, 1150000.00, 0.00, 1150000.00, 'cash', '2026-06-18 09:09:09', 'paid', 1200000.00, 50000.00, 1),
(10, 19, 1000.00, 0.00, 1000.00, 'transfer', '2026-06-19 05:50:22', 'paid', 1000.00, 0.00, 1),
(11, 22, 16800100.00, 775000.00, 16025100.00, 'transfer', '2026-06-22 06:24:48', 'paid', 16025100.00, 0.00, 1),
(12, 21, 290000.00, 0.00, 290000.00, 'transfer', '2026-06-22 09:38:50', 'paid', 290000.00, 0.00, 1),
(13, 23, 2500000.00, 0.00, 2500000.00, 'cash', '2026-06-23 02:51:19', 'paid', 2500000.00, 0.00, 1),
(14, 17, 800.00, 0.00, 800.00, 'cash', '2026-06-23 02:51:27', 'paid', 800.00, 0.00, 1),
(15, 12, 4180000.00, 0.00, 4180000.00, 'cash', '2026-06-23 23:19:12', 'paid', 4180000.00, 0.00, 1),
(16, 11, 1640000.00, 0.00, 1640000.00, 'cash', '2026-06-24 03:20:12', 'paid', 1640000.00, 0.00, 1),
(17, 24, 15500400.00, 775000.00, 14725400.00, 'cash', NULL, 'pending', 0.00, 0.00, 1);

-- --------------------------------------------------------

--
-- Table structure for table `job_orders`
--

CREATE TABLE `job_orders` (
  `id` int NOT NULL,
  `job_no` varchar(20) NOT NULL,
  `customer_id` int NOT NULL,
  `vehicle_id` int NOT NULL,
  `receive_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `problem_description` text NOT NULL,
  `car_defects` text,
  `mileage` int DEFAULT '0',
  `fuel_level` varchar(50) DEFAULT '',
  `signed_receipt_image` varchar(255) DEFAULT NULL,
  `status` enum('pending','quoting','approved','repairing','finished','closed','cancelled') NOT NULL DEFAULT 'pending',
  `created_by` int NOT NULL,
  `closed_by` int DEFAULT NULL COMMENT 'ຜູ້ປິດງານ',
  `closed_at` timestamp NULL DEFAULT NULL COMMENT 'ວັນທີປິດ'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `job_orders`
--

INSERT INTO `job_orders` (`id`, `job_no`, `customer_id`, `vehicle_id`, `receive_date`, `problem_description`, `car_defects`, `mileage`, `fuel_level`, `signed_receipt_image`, `status`, `created_by`, `closed_by`, `closed_at`) VALUES
(1, 'JOB-2026-0001', 24, 18, '2026-04-29 16:10:34', 'ນ້ຳມັນເຄື່ອງ', NULL, 100, '1/4', NULL, 'finished', 1, NULL, NULL),
(2, 'JOB-2026-0002', 31, 17, '2026-04-29 16:13:51', 'ເກ', NULL, 1000, '1/2', NULL, 'finished', 1, NULL, NULL),
(3, 'JOB-2026-0003', 31, 17, '2026-05-01 16:37:30', 'ງ່ຽນ', NULL, 1000, '3/4', NULL, 'finished', 1, NULL, NULL),
(4, 'JOB-2026-0004', 31, 17, '2026-05-12 09:02:35', 'ກົງລົດເພ', NULL, 10000, 'full', NULL, 'finished', 1, NULL, NULL),
(5, 'JOB-2026-0005', 32, 19, '2026-06-05 05:39:31', 'ຢາກປ່ຽນນຳາໍມັນ', NULL, 1234, '3/4', NULL, 'finished', 1, NULL, NULL),
(6, 'JOB-2026-0006', 44, 23, '2026-06-11 08:23:37', 'ກົງແຕກ', NULL, 12000, 'full', NULL, 'finished', 1, NULL, NULL),
(7, 'JOB-2026-0007', 48, 28, '2026-06-12 07:13:30', 'ນ້ຳມັນເຄື່ອງຫມົດ', NULL, 9000, 'full', NULL, 'finished', 1, NULL, NULL),
(8, 'JOB-2026-0008', 49, 29, '2026-06-12 07:19:37', 'ນ້ຳມັນເຄື່ອງຫມົດ', NULL, 12000, '1/2', NULL, 'finished', 1, NULL, NULL),
(9, 'JOB-2026-0009', 47, 24, '2026-06-14 08:33:51', 'ຕັ່ງເປ່', NULL, 2000, 'full', NULL, 'finished', 1, NULL, NULL),
(10, 'JOB-2026-0010', 6, 7, '2026-06-14 08:46:08', 'ປະຕູເພ່', NULL, 1000, '3/4', NULL, 'finished', 1, NULL, NULL),
(11, 'JOB-2026-0011', 49, 29, '2026-06-14 09:53:18', 'ຢາງແຕກ', NULL, 2000, '1/4', NULL, 'closed', 1, 1, '2026-06-24 03:20:12'),
(12, 'JOB-2026-0012', 24, 18, '2026-06-14 17:55:36', 'kokoko', NULL, 999, '1/2', NULL, 'closed', 1, 1, '2026-06-23 23:19:12'),
(13, 'JOB-2026-0013', 32, 19, '2026-06-16 18:25:50', '23131213132', NULL, 1222222, '3/4', NULL, 'closed', 1, 1, '2026-06-18 09:09:09'),
(14, 'JOB-2026-0014', 32, 19, '2026-06-17 03:03:29', 'ກນດນກນກດາກດ', NULL, 121212121, '3/4', NULL, 'approved', 3, NULL, NULL),
(16, 'JOB-2026-0015', 32, 19, '2026-06-18 02:31:44', 'qeqwe', NULL, 1131313131, '3/4', NULL, 'closed', 1, 1, '2026-06-18 03:42:05'),
(17, 'JOB-2026-0016', 32, 19, '2026-06-18 04:19:18', '0', NULL, 0, 'full', NULL, 'closed', 1, 1, '2026-06-23 02:51:27'),
(19, 'JOB-2026-0017', 32, 19, '2026-06-18 05:06:57', 'ລົດສຽງດັງ', NULL, 100, 'full', NULL, 'closed', 1, 1, '2026-06-19 05:50:22'),
(20, 'JOB-2026-0018', 32, 19, '2026-06-18 05:36:54', '1000000', NULL, 141555, 'full', NULL, 'closed', 1, 1, '2026-06-18 08:33:59'),
(21, 'JOB-2026-0019', 32, 19, '2026-06-20 02:35:22', 'ລົດສຽງດັງ', NULL, 11122, '1/2', NULL, 'closed', 1, 1, '2026-06-22 09:38:50'),
(22, 'JOB-2026-0020', 32, 19, '2026-06-21 08:12:20', '1231313', NULL, 12313213, '', NULL, 'closed', 1, 1, '2026-06-22 06:24:48'),
(23, 'JOB-2026-0021', 32, 19, '2026-06-22 06:57:18', '212', NULL, 121, 'full', NULL, 'closed', 1, 1, '2026-06-23 02:51:19'),
(24, 'JOB-2026-0022', 32, 31, '2026-06-22 06:59:02', '122', NULL, 1212, 'full', NULL, 'finished', 1, NULL, NULL),
(25, 'JOB-2026-0023', 1, 1, '2026-06-24 00:52:49', 'ກວດເຊັກໄລຍະທາງ (Check mileage/maintenance)', 'ມີຮອຍບຸບຢູ່ກັນຊົນທ້າຍ (Dent on rear bumper)', 55000, '1/2', 'signed_7916f416f2f54d8d99f303c6d1859412.png', 'pending', 1, NULL, NULL),
(26, 'JOB-2026-0024', 32, 31, '2026-06-24 01:37:27', '321312312313', 'sdadwda', 1223, 'full', NULL, 'pending', 1, NULL, NULL),
(27, 'JOB-2026-0025', 32, 31, '2026-06-24 01:49:40', 'test image', '', 0, '', 'signed_8349ae64407f4b51a22384447d7ef2cc.png', 'pending', 1, NULL, NULL),
(28, 'JOB-2026-0026', 32, 31, '2026-06-24 01:51:07', 'test multipart', 'none', 0, 'full', 'signed_454f44c5c2fb42b48abb9eb49307e8c4.png', 'pending', 1, NULL, NULL),
(29, 'JOB-2026-0027', 32, 31, '2026-06-24 01:56:12', 'adsdad', 'sadsdad', 31313, 'full', NULL, 'pending', 1, NULL, NULL),
(30, 'JOB-2026-0028', 32, 31, '2026-06-24 02:00:37', '1', '1', 1, 'full', NULL, 'repairing', 1, NULL, NULL),
(31, 'JOB-2026-0029', 32, 31, '2026-06-24 02:10:01', '1', '1', 1, 'full', 'signed_dd08cd3dc13c4ae6a8b88c5a99b35532.png', 'finished', 1, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `parts`
--

CREATE TABLE `parts` (
  `id` int NOT NULL,
  `name` varchar(255) NOT NULL COMMENT 'ຊື່ອາໄຫຼ່',
  `cost_price` decimal(15,2) DEFAULT '0.00' COMMENT 'ລາຄາຕົ້ນທຶນ',
  `sell_price` decimal(15,2) DEFAULT '0.00' COMMENT 'ລາຄາຂາຍ',
  `stock_qty` int DEFAULT '0' COMMENT 'ຈຳນວນໃນສາງ',
  `min_stock` int DEFAULT '5' COMMENT 'ຈຳນວນຂັ້ນຕ່ຳ',
  `supplier_id` int DEFAULT NULL COMMENT 'ຜູ້ສະໜອງ',
  `category_id` int DEFAULT NULL,
  `unit_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='ຂໍ້ມູນອາໄຫຼ່';

--
-- Dumping data for table `parts`
--

INSERT INTO `parts` (`id`, `name`, `cost_price`, `sell_price`, `stock_qty`, `min_stock`, `supplier_id`, `category_id`, `unit_id`) VALUES
(9, 'ນ້ຳມັນເຄື່ອງດີເຊລ 10W-30 (6+1L)', 450000.00, 500000.00, 22, 3, 3, 7, 3),
(10, 'ໝໍ້ຕອງນ້ຳມັນເຄື່ອງ (Vigo/Revo)', 45000.00, 60000.00, 18, 5, 7, 7, 1),
(11, 'ໝໍ້ຕອງອາກາດ (D-Max 2020)', 120000.00, 140000.00, 8, 2, 2, 7, 1),
(12, 'ໝໍ້ຕອງນ້ຳມັນເຊື້ອໄຟ (Revo)', 180000.00, 200000.00, 10, 2, 3, 7, 1),
(13, 'ນ້ຳມັນເຄື່ອງ 5W30 Toyota', 120000.00, 150000.00, 25, 5, 3, 7, 1),
(14, 'ນ້ຳມັນເຄື່ອງ 10W40 Honda', 110000.00, 140000.00, 20, 5, 7, 7, 1),
(15, 'ກອງນ້ຳມັນເຄື່ອງ Toyota', 45000.00, 65000.00, 15, 3, 3, 7, 1),
(16, 'ກອງອາກາດ Isuzu D-Max', 70000.00, 95000.00, 12, 3, 2, 7, 1),
(17, 'ຜ້າເບກໜ້າ Honda Civic', 350000.00, 450000.00, 8, 2, 7, 7, 3),
(18, 'ຜ້າເບກຫຼັງ Toyota Vios', 300000.00, 400000.00, 9, 2, 3, 7, 3),
(19, 'ແບັດເຕີຣີ 12V 60Ah', 850000.00, 1050000.00, 6, 2, 11, 7, 1),
(20, 'ຫົວທຽນ NGK', 25000.00, 40000.00, 49, 10, 8, 7, 1),
(21, 'ສາຍພານເຄື່ອງ Toyota', 180000.00, 240000.00, 7, 2, 3, 7, 1),
(22, 'ກອງນ້ຳມັນເຊື້ອໄຟ Ford Ranger', 95000.00, 130000.00, 10, 3, 1, 7, 1),
(23, 'ໝໍ້ນ້ຳ Honda CRV', 1200000.00, 1450000.00, 4, 1, 7, 7, 1),
(24, 'ໄຟໜ້າ Toyota Hilux', 950000.00, 1200000.00, 3, 1, 3, 7, 1),
(25, 'ໄຟທ້າຍ Isuzu D-Max', 750000.00, 980000.00, 4, 1, 11, 7, 1),
(26, 'ຢາງລົດ 265/65R17', 2200000.00, 2600000.00, 12, 4, 10, 7, 1),
(27, 'ຈານເບກ Toyota Fortuner', 650000.00, 850000.00, 5, 2, 11, 7, 5),
(28, 'ປ້ຳນ້ຳ Toyota Vigo', 480000.00, 650000.00, 6, 2, 9, 7, 1),
(29, 'ຄອຍຫົວທຽນ Honda Jazz', 320000.00, 450000.00, 5, 2, 11, 7, 1),
(30, 'ຟິວ 15A', 5000.00, 10000.00, 100, 20, 9, 7, 1),
(31, 'ຫຼອດໄຟ H4', 35000.00, 55000.00, 30, 5, 11, 7, 1),
(32, 'ນ້ຳຢາຫຼໍ່ເຢັນ', 65000.00, 90000.00, 18, 5, 8, 7, 1),
(33, 'ນ້ຳມັນເບກ DOT4', 45000.00, 70000.00, 14, 4, 8, 7, 1),
(34, 'ຊຸດຄັດຊີ Toyota Revo', 1800000.00, 2200000.00, 3, 1, 3, 7, 3),
(35, 'ໂຊ້ກໜ້າ Mazda BT50', 750000.00, 950000.00, 4, 1, 6, 7, 5),
(36, 'ໂຊ້ກຫຼັງ Mazda BT50', 700000.00, 900000.00, 4, 1, 6, 7, 5),
(37, 'ລູກປືນລໍ້ໜ້າ Toyota', 150000.00, 220000.00, 10, 3, 3, 7, 1),
(38, 'ລູກໝາກພວງມາໄລ Honda', 120000.00, 180000.00, 9, 3, 7, 7, 1),
(39, 'ກະຈົກຂ້າງ Ford Ranger', 650000.00, 850000.00, 3, 1, 1, 7, 1),
(40, 'ກັນຊົນໜ້າ Toyota Vigo', 2200000.00, 2800000.00, 2, 1, 3, 7, 1),
(41, 'ພັດລົມໝໍ້ນ້ຳ Honda City', 550000.00, 750000.00, 5, 2, 7, 7, 1),
(42, 'ໄສ້ກອງແອ', 45000.00, 70000.00, 20, 5, 11, 7, 1),
(43, 'ປະເກັນຝາສູບ Toyota Altis', 280000.00, 380000.00, 6, 2, 3, 7, 3),
(44, 'ປະເກັນອ່າງນ້ຳມັນ Vigo', 85000.00, 120000.00, 10, 3, 3, 7, 1),
(45, 'ຊຸດສາຍຫົວທຽນ Honda Accord', 450000.00, 620000.00, 5, 2, 7, 7, 3),
(46, 'ໄດສະຕາດ Isuzu D-Max', 1800000.00, 2300000.00, 2, 1, 2, 7, 1),
(47, 'ໄດຊາດ Toyota Camry', 2200000.00, 2800000.00, 3, 1, 3, 7, 1),
(48, 'ຄອມແອ Ford Everest', 3500000.00, 4200000.00, 2, 1, 1, 7, 1),
(49, 'ວາວນ້ຳ Toyota Fortuner', 180000.00, 250000.00, 7, 2, 3, 7, 1),
(50, 'ສາຍແອ Honda CRV', 320000.00, 450000.00, 6, 2, 7, 7, 1),
(51, 'ມໍເຕີປັດນ້ຳຝົນ Mazda 3', 650000.00, 850000.00, 4, 1, 6, 7, 1),
(52, 'ຍາງແທ່ນເຄື່ອງ Toyota Revo', 280000.00, 380000.00, 8, 2, 3, 7, 1),
(53, 'ຍາງຫຸ້ມເພົາ Honda Civic', 95000.00, 140000.00, 15, 4, 7, 7, 1),
(54, 'ລູກປືນລໍ້ຫຼັງ Isuzu MU-X', 220000.00, 320000.00, 6, 2, 2, 7, 1),
(55, 'ສາຍຄັນເລັ່ງ Toyota Vigo', 120000.00, 180000.00, 9, 3, 3, 7, 1),
(56, 'ປ້ຳຕິກ Honda Jazz', 850000.00, 1100000.00, 4, 1, 7, 7, 3),
(57, 'ຊຸດໂສ້ໄທມິ່ງ Ford Ranger', 1450000.00, 1800000.00, 3, 1, 1, 7, 3),
(58, 'ກະບອກເບກໃຫຍ່ Toyota Vios', 650000.00, 850000.00, 5, 2, 3, 7, 1),
(59, 'ກະບອກຄັດຊີ Honda City', 480000.00, 650000.00, 5, 2, 7, 7, 1),
(60, 'ສະວິດໄຟເບກ', 45000.00, 75000.00, 20, 5, 9, 7, 1),
(61, 'ຊຸດລູກສູບ Toyota Altis', 2200000.00, 2800000.00, 2, 1, 3, 7, 3),
(62, 'ວາວໄອເສຍ Honda Civic', 180000.00, 250000.00, 8, 2, 7, 7, 1),
(63, 'ຫມໍ້ພັກນ້ຳ', 120000.00, 180000.00, 10, 3, 4, 7, 1),
(64, 'ມໍເຕີພັດລົມແອ', 850000.00, 1150000.00, 4, 1, 8, 7, 1),
(65, 'ປະເກັນປະຕູລົດ', 95000.00, 140000.00, 12, 3, 11, 7, 1),
(66, 'ຊຸດກຸນແຈລໍ້', 180000.00, 260000.00, 7, 2, 8, 7, 3),
(67, 'ສາຍພານແອ Toyota Camry', 220000.00, 320000.00, 5, 2, 3, 7, 1),
(68, 'ຝາຖັງນ້ຳ', 35000.00, 60000.00, 15, 5, 10, 7, 1),
(69, 'ຊຸດຄັນສົ່ງ Toyota Hilux', 1450000.00, 1900000.00, 2, 1, 3, 7, 3),
(70, 'ປ້ຳ ABS Honda Accord', 3000000.00, 5000000.00, 2, 1, 7, 7, 1),
(71, 'ສາຍດຶງຝາກະໂປງ', 85000.00, 120000.00, 10, 3, 11, 7, 1),
(72, 'ຄັນເກຍ Toyota Vios', 950000.00, 1300000.00, 2, 2, 3, 2, 2),
(74, '10000000', 60000.00, 100.00, 42, 5, 11, 2, 5);

-- --------------------------------------------------------

--
-- Table structure for table `parts_usage`
--

CREATE TABLE `parts_usage` (
  `id` int NOT NULL,
  `repair_id` int NOT NULL,
  `part_id` int NOT NULL,
  `qty` int DEFAULT '1',
  `cost_price` decimal(15,2) DEFAULT '0.00',
  `used_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `note` text COMMENT 'ເຫດຜົນເບີກ/ຫຼຸດ'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `parts_usage`
--

INSERT INTO `parts_usage` (`id`, `repair_id`, `part_id`, `qty`, `cost_price`, `used_at`, `note`) VALUES
(8, 5, 67, 1, 220000.00, '2026-06-12 04:17:59', NULL),
(9, 5, 68, 1, 35000.00, '2026-06-12 04:18:16', NULL),
(10, 7, 68, 1, 35000.00, '2026-06-12 07:23:25', NULL),
(11, 11, 68, 1, 35000.00, '2026-06-14 18:13:03', NULL),
(12, 14, 74, 1, 10.00, '2026-06-18 02:41:53', NULL),
(14, 18, 74, 1, 10.00, '2026-06-18 05:10:23', 'Pulled from quotation'),
(15, 18, 74, 1, 10.00, '2026-06-18 05:10:23', 'Pulled from quotation'),
(16, 18, 74, 1, 10.00, '2026-06-18 05:10:23', 'Pulled from quotation'),
(17, 18, 74, 1, 10.00, '2026-06-18 05:10:23', 'Pulled from quotation'),
(18, 18, 74, 1, 10.00, '2026-06-18 05:10:23', 'Pulled from quotation'),
(19, 18, 74, 1, 10.00, '2026-06-18 05:10:23', 'Pulled from quotation'),
(20, 18, 74, 1, 10.00, '2026-06-18 05:10:23', 'Pulled from quotation'),
(21, 18, 74, 1, 10.00, '2026-06-18 05:10:23', 'Pulled from quotation'),
(22, 18, 74, 1, 10.00, '2026-06-18 05:10:23', 'Pulled from quotation'),
(23, 18, 74, 1, 10.00, '2026-06-18 05:10:23', 'Pulled from quotation'),
(24, 19, 74, 4, 10.00, '2026-06-18 05:38:09', 'Pulled from quotation'),
(25, 19, 18, 1, 300000.00, '2026-06-18 05:38:21', NULL),
(26, 20, 20, 1, 25000.00, '2026-06-20 02:38:14', 'Pulled from quotation'),
(33, 24, 74, 1, 67.00, '2026-06-22 06:23:54', 'Pulled from quotation'),
(34, 24, 72, 1, 950000.00, '2026-06-22 06:23:54', 'Pulled from quotation'),
(35, 25, 74, 4, 60000.00, '2026-06-23 02:48:07', 'Pulled from quotation');

-- --------------------------------------------------------

--
-- Table structure for table `part_categories`
--

CREATE TABLE `part_categories` (
  `id` int NOT NULL,
  `name` varchar(100) NOT NULL COMMENT 'ຊື່ປະເພດ',
  `status` enum('active','inactive') DEFAULT 'active' COMMENT 'ສະຖານະ'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='ຂໍ້ມູນປະເພດອາໄຫຼ່';

--
-- Dumping data for table `part_categories`
--

INSERT INTO `part_categories` (`id`, `name`, `status`) VALUES
(1, 'ນ້ຳມັນເຄື່ອງ', 'active'),
(2, 'ນ້ຳມັນເກຍ', 'active'),
(3, 'ນ້ຳມັນເບກ', 'active'),
(4, 'ຢາງລົດ', 'active'),
(5, 'ຜ້າເບກ', 'active'),
(6, 'ໄຟຟ້າ', 'active'),
(7, 'ເຄື່ອງຈັກ', 'active'),
(8, 'ລະບົບຄວາມເຢັນ', 'active');

-- --------------------------------------------------------

--
-- Table structure for table `promotions`
--

CREATE TABLE `promotions` (
  `id` int NOT NULL,
  `name` varchar(255) NOT NULL COMMENT 'ຊື່ໂປໂມຊັນ',
  `discount_type` enum('percent','amount') NOT NULL COMMENT 'ປະເພດສ່ວນຫຼຸດ',
  `value` decimal(15,2) NOT NULL COMMENT 'ມູນຄ່າ',
  `min_amount` decimal(15,2) DEFAULT '0.00' COMMENT 'ມູນຄ່າຂັ້ນຕ່ຳ',
  `start_date` date DEFAULT NULL COMMENT 'ວັນເລີ່ມ',
  `end_date` date DEFAULT NULL COMMENT 'ວັນສິ້ນສຸດ',
  `status` enum('active','inactive') DEFAULT 'active' COMMENT 'ສະຖານະ'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='ຂໍ້ມູນໂປໂມຊັນ';

--
-- Dumping data for table `promotions`
--

INSERT INTO `promotions` (`id`, `name`, `discount_type`, `value`, `min_amount`, `start_date`, `end_date`, `status`) VALUES
(1, 'ສ່ວນຫຼຸດປີໃໝ່', 'percent', 10.00, 0.00, '2024-01-01', '2024-01-31', 'active'),
(2, 'ສ່ວນຫຼຸດສົ່ງທ້າຍປີ', 'amount', 50000.00, 200000.00, '2024-12-01', '2026-12-31', 'active'),
(3, 'ສ່ວນຫຼຸດພິເສດ', 'percent', 5.00, 0.00, '2024-06-01', '2026-07-20', 'active'),
(4, 'ຫຼຸດຄ່າຍ່າງ', 'amount', 50000.00, 0.00, '2026-06-15', '2026-06-30', 'active');

-- --------------------------------------------------------

--
-- Table structure for table `promotion_parts`
--

CREATE TABLE `promotion_parts` (
  `id` int NOT NULL,
  `promotion_id` int NOT NULL COMMENT 'ໂປໂມຊັນ',
  `part_id` int NOT NULL COMMENT 'ອາໄຫຼ່',
  `qty` int DEFAULT '1' COMMENT 'ຈຳນວນທີ່ຕ້ອງຊື້'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='ໂປໂມຊັນສຳລັບອາໄຫຼ່';

--
-- Dumping data for table `promotion_parts`
--

INSERT INTO `promotion_parts` (`id`, `promotion_id`, `part_id`, `qty`) VALUES
(2, 3, 16, 1),
(3, 2, 60, 1),
(9, 4, 64, 1);

-- --------------------------------------------------------

--
-- Table structure for table `promotion_services`
--

CREATE TABLE `promotion_services` (
  `id` int NOT NULL,
  `promotion_id` int NOT NULL COMMENT 'ໂປໂມຊັນ',
  `service_id` int NOT NULL COMMENT 'ບໍລິການ',
  `qty` int DEFAULT '1' COMMENT 'ຈຳນວນທີ່ແຖມ/ໃຫ້ຟຣີ'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='ໂປໂມຊັນສຳລັບບໍລິການ';

--
-- Dumping data for table `promotion_services`
--

INSERT INTO `promotion_services` (`id`, `promotion_id`, `service_id`, `qty`) VALUES
(1, 3, 24, 1);

-- --------------------------------------------------------

--
-- Table structure for table `purchase_items`
--

CREATE TABLE `purchase_items` (
  `id` int NOT NULL,
  `purchase_id` int NOT NULL,
  `part_id` int NOT NULL,
  `qty` int NOT NULL,
  `received_qty` int NOT NULL DEFAULT '0' COMMENT 'Quantity already received',
  `unit_cost` decimal(15,2) NOT NULL,
  `total_line` decimal(15,2) NOT NULL DEFAULT '0.00'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `purchase_items`
--

INSERT INTO `purchase_items` (`id`, `purchase_id`, `part_id`, `qty`, `received_qty`, `unit_cost`, `total_line`) VALUES
(1, 1, 12, 2, 0, 20000.00, 40000.00),
(5, 5, 74, 10, 10, 50000.00, 500000.00),
(6, 6, 74, 10, 10, 50000.00, 500000.00),
(7, 7, 70, 1, 1, 5000000.00, 5000000.00),
(8, 8, 70, 1, 0, 3000000.00, 3000000.00),
(9, 8, 62, 1, 0, 180000.00, 180000.00),
(10, 9, 74, 1, 1, 50000.00, 50000.00),
(11, 10, 74, 3, 1, 60000.00, 180000.00);

-- --------------------------------------------------------

--
-- Table structure for table `purchase_orders`
--

CREATE TABLE `purchase_orders` (
  `id` int NOT NULL,
  `po_no` varchar(50) NOT NULL,
  `supplier_id` int NOT NULL,
  `order_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `total_amount` decimal(15,2) NOT NULL DEFAULT '0.00',
  `status` enum('ordering','partial','completed','cancelled') NOT NULL DEFAULT 'ordering' COMMENT 'Status (ordering, partial, completed, cancelled)',
  `created_by` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `purchase_orders`
--

INSERT INTO `purchase_orders` (`id`, `po_no`, `supplier_id`, `order_date`, `total_amount`, `status`, `created_by`) VALUES
(1, 'PO-2026-0001', 10, '2026-05-06 12:12:33', 40000.00, 'completed', 1),
(2, 'PO-2026-0002', 7, '2026-05-10 08:25:49', 20000.00, 'completed', 1),
(3, 'PO-2026-0003', 3, '2026-05-10 09:47:07', 20000.00, 'completed', 1),
(4, 'PO-2026-0004', 3, '2026-06-17 02:12:24', 5000000.00, 'cancelled', 1),
(5, 'PO-2026-0005', 11, '2026-06-19 06:47:27', 500000.00, 'completed', 1),
(6, 'PO-2026-0006', 11, '2026-06-19 06:52:32', 500000.00, 'completed', 1),
(7, 'PO-2026-0007', 11, '2026-06-19 09:52:35', 5000000.00, 'completed', 1),
(8, 'PO-2026-0008', 11, '2026-06-19 10:28:58', 3180000.00, 'cancelled', 1),
(9, 'PO-2026-0009', 11, '2026-06-19 10:39:50', 50000.00, 'completed', 1),
(10, 'PO-2026-0010', 11, '2026-06-24 03:37:48', 180000.00, 'partial', 1);

-- --------------------------------------------------------

--
-- Table structure for table `quotations`
--

CREATE TABLE `quotations` (
  `id` int NOT NULL,
  `job_order_id` int NOT NULL,
  `promotion_id` int DEFAULT NULL,
  `sub_total` decimal(15,2) NOT NULL DEFAULT '0.00',
  `discount_amount` decimal(15,2) DEFAULT '0.00',
  `net_total` decimal(15,2) NOT NULL DEFAULT '0.00',
  `status` enum('draft','approved','rejected') NOT NULL DEFAULT 'draft',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `approved_by` int DEFAULT NULL COMMENT 'ຜູ້ອະນຸມັດ',
  `created_by` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `quotations`
--

INSERT INTO `quotations` (`id`, `job_order_id`, `promotion_id`, `sub_total`, `discount_amount`, `net_total`, `status`, `created_at`, `approved_by`, `created_by`) VALUES
(14, 2, NULL, 950000.00, 0.00, 950000.00, 'approved', '2026-05-01 08:53:56', NULL, 1),
(15, 3, NULL, 1940000.00, 0.00, 1940000.00, 'approved', '2026-05-01 16:38:39', NULL, 1),
(16, 1, NULL, 15700000.00, 0.00, 15700000.00, 'approved', '2026-05-06 09:56:48', NULL, 1),
(17, 5, NULL, 0.00, 0.00, 0.00, 'approved', '2026-06-05 05:44:43', NULL, 1),
(18, 6, NULL, 790000.00, 0.00, 790000.00, 'approved', '2026-06-11 18:11:44', NULL, 1),
(19, 7, NULL, 790000.00, 0.00, 790000.00, 'approved', '2026-06-12 07:14:23', NULL, 1),
(20, 8, NULL, 800000.00, 0.00, 800000.00, 'approved', '2026-06-12 07:22:12', NULL, 1),
(21, 9, NULL, 330000.00, 0.00, 330000.00, 'approved', '2026-06-14 08:38:55', NULL, 1),
(22, 10, NULL, 1620000.00, 0.00, 1620000.00, 'approved', '2026-06-14 08:46:28', NULL, 1),
(23, 11, NULL, 1640000.00, 0.00, 1640000.00, 'approved', '2026-06-14 09:53:37', NULL, 1),
(24, 12, NULL, 4180000.00, 0.00, 4180000.00, 'approved', '2026-06-14 17:56:01', NULL, 1),
(25, 13, NULL, 1150000.00, 0.00, 1150000.00, 'approved', '2026-06-16 18:38:23', NULL, 1),
(26, 14, NULL, 1150000.00, 0.00, 1150000.00, 'draft', '2026-06-17 08:38:39', NULL, 1),
(27, 14, 4, 1250000.00, 50000.00, 1200000.00, 'approved', '2026-06-17 17:13:42', NULL, 1),
(28, 14, NULL, 100.00, 0.00, 100.00, 'approved', '2026-06-17 17:35:16', NULL, 1),
(29, 4, NULL, 1000100.00, 0.00, 1000100.00, 'approved', '2026-06-17 17:50:44', 1, 1),
(30, 14, NULL, 100.00, 0.00, 100.00, 'approved', '2026-06-17 18:00:53', 1, 1),
(31, 16, NULL, 99999999.00, 0.00, 99999999.00, 'rejected', '2026-06-18 02:32:04', NULL, 1),
(32, 16, NULL, 150000.00, 0.00, 150000.00, 'approved', '2026-06-18 02:33:00', 1, 1),
(33, 17, NULL, 800.00, 0.00, 800.00, 'approved', '2026-06-18 04:19:40', 1, 1),
(35, 19, NULL, 1000.00, 0.00, 1000.00, 'approved', '2026-06-18 05:07:58', 1, 1),
(36, 20, NULL, 1500400.00, 0.00, 1500400.00, 'approved', '2026-06-18 05:37:34', 1, 1),
(37, 21, NULL, 290000.00, 0.00, 290000.00, 'approved', '2026-06-20 02:36:41', 1, 1),
(38, 22, 3, 16800100.00, 775000.00, 16025100.00, 'approved', '2026-06-21 08:12:32', 1, 1),
(39, 24, 3, 15500400.00, 775000.00, 14725400.00, 'approved', '2026-06-22 06:59:35', 1, 1),
(40, 23, NULL, 2500000.00, 0.00, 2500000.00, 'approved', '2026-06-23 02:47:52', 1, 1),
(41, 31, NULL, 150300.00, 0.00, 150300.00, 'approved', '2026-06-24 17:44:18', 1, 1),
(42, 30, NULL, 380000.00, 0.00, 380000.00, 'draft', '2026-06-25 11:28:56', NULL, 1),
(43, 30, NULL, 400.00, 0.00, 400.00, 'approved', '2026-06-25 17:22:17', 1, 1);

-- --------------------------------------------------------

--
-- Table structure for table `quotation_items`
--

CREATE TABLE `quotation_items` (
  `id` int NOT NULL,
  `quotation_id` int NOT NULL,
  `part_id` int DEFAULT NULL COMMENT 'ອາໄຫຼ່ (ຖ້າແມ່ນ part)',
  `service_id` int DEFAULT NULL COMMENT 'ບໍລິການ (ຖ້າແມ່ນ service)',
  `qty` int NOT NULL DEFAULT '1',
  `unit_price` decimal(15,2) NOT NULL DEFAULT '0.00',
  `total` decimal(15,2) NOT NULL DEFAULT '0.00',
  `discount_amount` decimal(15,2) NOT NULL DEFAULT '0.00',
  `custom_name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `quotation_items`
--

INSERT INTO `quotation_items` (`id`, `quotation_id`, `part_id`, `service_id`, `qty`, `unit_price`, `total`, `discount_amount`, `custom_name`) VALUES
(8, 14, 12, NULL, 1, 200000.00, 200000.00, 0.00, NULL),
(9, 14, NULL, 5, 1, 750000.00, 750000.00, 0.00, NULL),
(10, 15, 11, NULL, 1, 140000.00, 140000.00, 0.00, NULL),
(11, 15, NULL, 20, 1, 1800000.00, 1800000.00, 0.00, NULL),
(12, 16, 12, NULL, 1, 200000.00, 200000.00, 0.00, NULL),
(13, 16, NULL, 24, 1, 15500000.00, 15500000.00, 0.00, NULL),
(14, 17, 72, NULL, 1, 1300000.00, 1300000.00, 0.00, NULL),
(15, 17, 69, NULL, 1, 1900000.00, 1900000.00, 0.00, NULL),
(16, 17, 72, NULL, 1, 1300000.00, 1300000.00, 0.00, NULL),
(17, 17, 69, NULL, 1, 1900000.00, 1900000.00, 0.00, NULL),
(18, 17, 72, NULL, 1, 1300000.00, 1300000.00, 0.00, NULL),
(19, 17, 69, NULL, 1, 1900000.00, 1900000.00, 0.00, NULL),
(20, 17, 72, NULL, 1, 1300000.00, 1300000.00, 0.00, NULL),
(21, 17, 69, NULL, 1, 1900000.00, 1900000.00, 0.00, NULL),
(22, 18, 14, NULL, 1, 140000.00, 140000.00, 0.00, NULL),
(23, 18, NULL, 4, 1, 650000.00, 650000.00, 0.00, NULL),
(24, 19, 14, NULL, 1, 140000.00, 140000.00, 0.00, NULL),
(25, 19, NULL, 4, 1, 650000.00, 650000.00, 0.00, NULL),
(26, 20, NULL, 4, 1, 650000.00, 650000.00, 0.00, NULL),
(27, 20, 13, NULL, 1, 150000.00, 150000.00, 0.00, NULL),
(28, 21, 63, NULL, 1, 180000.00, 180000.00, 0.00, NULL),
(29, 21, NULL, 12, 1, 150000.00, 150000.00, 0.00, NULL),
(30, 22, 71, NULL, 1, 120000.00, 120000.00, 0.00, NULL),
(31, 22, NULL, 22, 1, 1500000.00, 1500000.00, 0.00, NULL),
(32, 23, 65, NULL, 1, 140000.00, 140000.00, 0.00, NULL),
(33, 23, NULL, 22, 1, 1500000.00, 1500000.00, 0.00, NULL),
(34, 24, 43, NULL, 1, 380000.00, 380000.00, 0.00, NULL),
(35, 24, NULL, 16, 1, 3800000.00, 3800000.00, 0.00, NULL),
(36, 25, 64, NULL, 1, 1150000.00, 1150000.00, 0.00, NULL),
(37, 26, 64, NULL, 1, 1150000.00, 1150000.00, 0.00, NULL),
(38, 27, NULL, NULL, 1, 100000.00, 100000.00, 0.00, 'ຄ່າແຮງການໃສ່ອາໄຫຼ'),
(39, 27, 64, NULL, 1, 1150000.00, 1150000.00, 50000.00, NULL),
(40, 28, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(41, 29, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(42, 29, NULL, NULL, 1, 1000000.00, 1000000.00, 0.00, '່'),
(43, 30, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(44, 31, NULL, NULL, 1, 99999999.00, 99999999.00, 0.00, 'test'),
(45, 32, NULL, NULL, 1, 150000.00, 150000.00, 0.00, 'test'),
(46, 33, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(47, 33, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(48, 33, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(49, 33, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(50, 33, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(51, 33, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(52, 33, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(53, 33, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(55, 35, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(56, 35, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(57, 35, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(58, 35, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(59, 35, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(60, 35, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(61, 35, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(62, 35, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(63, 35, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(64, 35, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(65, 36, 74, NULL, 4, 100.00, 400.00, 0.00, NULL),
(66, 36, NULL, 22, 1, 1500000.00, 1500000.00, 0.00, NULL),
(67, 37, NULL, NULL, 1, 250000.00, 250000.00, 0.00, 'ກວດສະພາບລົດ'),
(68, 37, 20, NULL, 1, 40000.00, 40000.00, 0.00, NULL),
(69, 38, 74, NULL, 1, 100.00, 100.00, 0.00, NULL),
(70, 38, 72, NULL, 1, 1300000.00, 1300000.00, 0.00, NULL),
(71, 38, NULL, 24, 1, 15500000.00, 15500000.00, 775000.00, NULL),
(72, 39, 74, NULL, 4, 100.00, 400.00, 0.00, NULL),
(73, 39, NULL, 24, 1, 15500000.00, 15500000.00, 775000.00, NULL),
(74, 40, NULL, NULL, 1, 2500000.00, 2500000.00, 0.00, 'ບໍ່ມີໃນບໍລິການ'),
(75, 41, 74, NULL, 3, 100.00, 300.00, 0.00, NULL),
(76, 41, NULL, 12, 1, 150000.00, 150000.00, 0.00, NULL),
(77, 42, 68, NULL, 1, 60000.00, 60000.00, 0.00, NULL),
(78, 42, 67, NULL, 1, 320000.00, 320000.00, 0.00, NULL),
(79, 43, 74, NULL, 4, 100.00, 400.00, 0.00, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `repair_orders`
--

CREATE TABLE `repair_orders` (
  `id` int NOT NULL,
  `job_order_id` int NOT NULL,
  `mechanic_id` int DEFAULT NULL,
  `start_date` timestamp NULL DEFAULT NULL,
  `end_date` timestamp NULL DEFAULT NULL,
  `status` enum('working','completed') DEFAULT 'working',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `repair_orders`
--

INSERT INTO `repair_orders` (`id`, `job_order_id`, `mechanic_id`, `start_date`, `end_date`, `status`, `created_at`) VALUES
(1, 1, 2, '2026-05-06 09:57:48', '2026-05-06 09:58:13', 'completed', '2026-05-04 10:11:24'),
(2, 3, 2, '2026-05-04 13:09:32', '2026-05-06 09:57:08', 'completed', '2026-05-04 12:25:24'),
(3, 2, 2, '2026-05-04 13:10:18', '2026-05-08 07:20:22', 'completed', '2026-05-04 13:10:18'),
(4, 5, 2, '2026-06-05 05:47:16', '2026-06-05 05:48:38', 'completed', '2026-06-05 05:47:15'),
(5, 6, 2, '2026-06-12 03:59:10', '2026-06-12 04:37:15', 'completed', '2026-06-12 03:54:32'),
(6, 7, 2, '2026-06-12 07:14:46', '2026-06-12 07:15:28', 'completed', '2026-06-12 07:14:46'),
(7, 8, 2, '2026-06-12 07:23:08', '2026-06-12 07:23:53', 'completed', '2026-06-12 07:23:07'),
(8, 9, 2, '2026-06-14 08:42:18', '2026-06-14 08:45:39', 'completed', '2026-06-14 08:42:17'),
(9, 10, 2, '2026-06-14 09:16:32', '2026-06-14 09:54:39', 'completed', '2026-06-14 09:16:32'),
(10, 11, 2, '2026-06-14 09:54:24', '2026-06-14 17:20:33', 'completed', '2026-06-14 09:54:24'),
(11, 12, 2, '2026-06-14 18:12:47', '2026-06-14 18:13:23', 'completed', '2026-06-14 18:12:46'),
(12, 13, 2, '2026-06-17 06:58:44', '2026-06-17 06:59:53', 'completed', '2026-06-17 06:58:44'),
(13, 14, 2, '2026-06-17 17:40:08', '2026-06-17 17:41:33', 'completed', '2026-06-17 17:40:07'),
(14, 4, 2, '2026-06-18 02:42:41', '2026-06-18 03:45:01', 'completed', '2026-06-18 02:30:30'),
(15, 16, 4, '2026-06-18 03:41:13', '2026-06-18 03:41:28', 'completed', '2026-06-18 03:41:13'),
(16, 17, 4, '2026-06-18 04:21:30', '2026-06-18 04:37:28', 'completed', '2026-06-18 04:21:30'),
(18, 19, 4, '2026-06-18 05:08:30', '2026-06-18 05:11:22', 'completed', '2026-06-18 05:08:30'),
(19, 20, 4, '2026-06-18 05:37:51', '2026-06-18 05:38:37', 'completed', '2026-06-18 05:37:50'),
(20, 21, 4, '2026-06-20 02:37:40', '2026-06-20 02:56:13', 'completed', '2026-06-20 02:37:40'),
(24, 22, 2, '2026-06-22 06:23:29', '2026-06-22 06:24:25', 'completed', '2026-06-22 06:23:28'),
(25, 24, 4, '2026-06-22 08:02:49', '2026-06-24 17:42:36', 'completed', '2026-06-22 08:02:49'),
(26, 23, 4, '2026-06-23 02:48:22', '2026-06-23 02:48:41', 'completed', '2026-06-23 02:48:21'),
(27, 31, 4, '2026-06-25 11:30:33', '2026-06-25 17:09:04', 'completed', '2026-06-25 11:30:32'),
(28, 30, 4, '2026-06-25 17:29:01', NULL, 'working', '2026-06-25 17:29:01');

-- --------------------------------------------------------

--
-- Table structure for table `services`
--

CREATE TABLE `services` (
  `id` int NOT NULL,
  `name` varchar(255) NOT NULL COMMENT 'ຊື່ບໍລິການ',
  `price` decimal(15,2) DEFAULT '0.00' COMMENT 'ລາຄາ',
  `description` text COMMENT 'ລາຍລະອຽດ',
  `estimated_time` int DEFAULT NULL COMMENT 'ເວລາປະມານ (ນາທີ)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='ຂໍ້ມູນລາຍການບໍລິການ';

--
-- Dumping data for table `services`
--

INSERT INTO `services` (`id`, `name`, `price`, `description`, `estimated_time`) VALUES
(1, 'ປ່ຽນໝໍ້ໄຟ', 120000.00, 'ບໍລິການປ່ຽນໝໍ້ໄຟໃໝ່ ພ້ອມກວດເຊັກໄດຊາດ', 60),
(2, 'ກວດເຊັກ ແລະ ເຕີມນ້ຳຢາແອ', 350000.00, 'ກວດເຊັກ ແລະ ເຕີມນ້ຳຢາແອໃຫ້ເຕັມ', 60),
(3, 'ລ້າງອັດສີດ ແລະ ເຄືອບເງົາ', 120000.00, 'ລ້າງພາຍນອກ, ດູດຝຸ່ນພາຍໃນ ແລະ ເຄືອບສີ', 120),
(4, 'ປ່ຽນນ້ຳມັນເຄື່ອງ', 650000.00, 'ປ່ຽນນ້ຳມັນເຄື່ອງຄົບຊຸດ ພ້ອມກວດເຊັກສະພາບທົ່ວໄປ', 60),
(5, 'ປ່ຽນຜ້າເບຼກໜ້າ', 750000.00, 'ປ່ຽນຜ້າເບຼກໃໝ່ (ຊຸດ 2 ລໍ້ໜ້າ)', 120),
(6, 'ລ້າງວາວ ແລະ ພອດໄອເສຍ ', 2200000.00, 'ລ້າງຄາບຂີ້ໝິ່ນ (Carbon Cleaning) ໃນເຄື່ອງຈັກ', 300),
(7, 'ລ້າງວາວ ແລະ ພອດໄອເສຍ ', 2200000.00, 'ລ້າງຄາບຂີ້ໝິ່ນ (Carbon Cleaning) ໃນເຄື່ອງຈັກ', 300),
(8, 'ປ່ຽນຜ້າເບຼກໃໝ່ (ຊຸດ 2 ລໍ້ຫຼັງ)', 650000.00, 'ປ່ຽນຜ້າເບຼກໃໝ່ (ຊຸດ 2 ລໍ້ຫຼັງ)', 120),
(9, 'ປ່ຽນນ້ຳມັນເກຍ', 850000.00, 'ປ່ຽນນ້ຳມັນເກຍອໍໂຕ້ (ATF)', 120),
(10, 'ປ່ຽນຫົວທຽນ', 400000.00, 'ປ່ຽນຫົວທຽນມາດຕະຖານ 4 ຫົວ', 60),
(11, 'ເຄືອບເງົາສີລົດ', 250000.00, 'ເຄືອບສີປ້ອງກັນ UV ແລະ ໃຫ້ຄວາມເງົາງາມ', 120),
(12, 'ລ້າງຫ້ອງເຄື່ອງ', 150000.00, 'ທຳຄວາມສະອາດຄາບນ້ຳມັນໃນຫ້ອງເຄື່ອງຈັກ', 60),
(13, 'ກວດເຊັກລະບົບຄອມພິວເຕີ', 200000.00, 'ໃຊ້ເຄື່ອງມື OBD2 ສະແກນຫາຈຸດບົກຜ່ອງ', 60),
(14, 'ຍົກເກຍ', 8500000.00, 'ສ້ອມແປງລະບົບເກຍອໍໂຕ້, ປ່ຽນຊຸດຄລັດ ແລະ ແຜ່ນສົມອງເກຍ', 1440),
(15, 'ສ້ອມແປງຊ່ວງລຸ່ມຊຸດໃຫຍ່', 5500000.00, 'ປ່ຽນບູດຢາງ, ລູກໝາກທຸກໂຕ ແລະ ໂຊັກອັບ 4 ໂຕ', 480),
(16, 'ປ່ຽນຊຸດຄລັດ(Clutch Set)', 3800000.00, 'ສຳລັບລົດເກຍກະປຸກ: ປ່ຽນແຜ່ນຄລັດ, ຫວີຄລັດ, ລູກປືນຄລັດ', 360),
(17, 'ລ້າງຖັງນ້ຳມັນເຊື້ອໄຟ', 1200000.00, 'ຖອດຖັງນ້ຳມັນມາລ້າງສິ່ງສົກກະປົກ ແລະ ປ່ຽນໄສ້ຕອງນ້ຳມັນ', 300),
(18, 'ປ່ຽນໝໍ້ນ້ຳ', 2500000.00, 'ປ່ຽນໝໍ້ນ້ຳໃໝ່ ພ້ອມໄລ່ນ້ຳໃນລະບົບທັງໝົດ', 240),
(19, 'ຕິດຕັ້ງກ້ອງຮອບຄັນ 360', 4500000.00, 'ຕິດຕັ້ງລະບົບກ້ອງ ແລະ ເດີນສາຍໄຟຮອບຄັນ', 360),
(20, 'ເພີ່ມກັນສະຫນິມ', 1800000.00, 'ພົ່ນນ້ຳຢາກັນສະຫນິມຊ່ວງລຸ່ມແບບເຕັມລະບົບ', 240),
(21, 'ປ່ຽນແລັກພວງມາໄລ', 7200000.00, 'ປ່ຽນຊຸດແລັກພວງມາໄລໃໝ່ ພ້ອມຕັ້ງສູນ', 300),
(22, 'ສ້ອມແປງລະບົບສາຍໄຟ', 1500000.00, 'ກວດເຊັກ ແລະ ໄລ່ສາຍໄຟທີ່ຂາດ ຫຼື ໄຟຊັອດ', 720),
(23, 'ສ້ອມແປງໄດຊາດ', 2800000.00, 'ປ່ຽນຖ່ານໄດຊາດ ຫຼື ປ່ຽນລູກໃໝ່', 180),
(24, 'ຜ່າຈັກ ', 15500000.00, 'ຖອດມ້າງເຄື່ອງຈັກເພື່ອປ່ຽນແຫວນ, ປະເກັນ ແລະ ລູກສູບໃໝ່', 2880);

-- --------------------------------------------------------

--
-- Table structure for table `shop`
--

CREATE TABLE `shop` (
  `id` int NOT NULL,
  `name` varchar(255) DEFAULT NULL COMMENT 'ຊື່ຮ້ານ',
  `address` text COMMENT 'ທີ່ຢູ່',
  `phone` varchar(50) DEFAULT NULL COMMENT 'ເບີໂທ'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='ຂໍ້ມູນຮ້ານ';

--
-- Dumping data for table `shop`
--

INSERT INTO `shop` (`id`, `name`, `address`, `phone`) VALUES
(1, 'ລູກຄ້າ ຕົວຢ່າງ (Demo Customer)', 'ນະຄອນຫຼວງວຽງຈັນ (Vientiane, Laos)', 'XXX-XXXX-XXXX');

-- --------------------------------------------------------

--
-- Table structure for table `stock_movement`
--

CREATE TABLE `stock_movement` (
  `id` int NOT NULL,
  `part_id` int DEFAULT NULL,
  `type` enum('IN','OUT') NOT NULL,
  `qty` int NOT NULL,
  `ref_type` enum('purchase','repair','adjust') NOT NULL,
  `ref_id` int DEFAULT NULL,
  `date` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `stock_movement`
--

INSERT INTO `stock_movement` (`id`, `part_id`, `type`, `qty`, `ref_type`, `ref_id`, `date`) VALUES
(3, 67, 'OUT', 1, 'repair', 5, '2026-06-12 04:17:59'),
(4, 68, 'OUT', 1, 'repair', 5, '2026-06-12 04:18:16'),
(5, 68, 'OUT', 1, 'repair', 7, '2026-06-12 07:23:25'),
(6, 68, 'OUT', 1, 'repair', 11, '2026-06-14 18:13:03'),
(7, 74, 'OUT', 1, 'repair', 14, '2026-06-18 02:41:53'),
(10, 74, 'OUT', 1, 'repair', 18, '2026-06-18 05:10:23'),
(11, 74, 'OUT', 1, 'repair', 18, '2026-06-18 05:10:23'),
(12, 74, 'OUT', 1, 'repair', 18, '2026-06-18 05:10:23'),
(13, 74, 'OUT', 1, 'repair', 18, '2026-06-18 05:10:23'),
(14, 74, 'OUT', 1, 'repair', 18, '2026-06-18 05:10:23'),
(15, 74, 'OUT', 1, 'repair', 18, '2026-06-18 05:10:23'),
(16, 74, 'OUT', 1, 'repair', 18, '2026-06-18 05:10:23'),
(17, 74, 'OUT', 1, 'repair', 18, '2026-06-18 05:10:23'),
(18, 74, 'OUT', 1, 'repair', 18, '2026-06-18 05:10:23'),
(19, 74, 'OUT', 1, 'repair', 18, '2026-06-18 05:10:23'),
(20, 74, 'OUT', 4, 'repair', 19, '2026-06-18 05:38:09'),
(21, 18, 'OUT', 1, 'repair', 19, '2026-06-18 05:38:21'),
(22, 74, 'IN', 4, 'purchase', 1, '2026-06-19 06:52:31'),
(23, 74, 'IN', 6, 'purchase', 2, '2026-06-19 06:52:32'),
(24, 74, 'IN', 5, 'purchase', 3, '2026-06-19 08:41:26'),
(25, 70, 'IN', 1, 'purchase', 4, '2026-06-19 09:57:02'),
(26, 74, 'IN', 1, 'purchase', 5, '2026-06-19 10:40:09'),
(27, 20, 'OUT', 1, 'repair', 20, '2026-06-20 02:38:14'),
(28, 16, 'OUT', 1, 'repair', 20, '2026-06-20 02:55:29'),
(29, 16, 'IN', 1, 'repair', 20, '2026-06-20 02:55:50'),
(30, 74, 'OUT', 1, 'repair', 21, '2026-06-21 09:11:17'),
(31, 72, 'OUT', 1, 'repair', 21, '2026-06-21 09:11:17'),
(32, 74, 'IN', 1, 'repair', 21, '2026-06-21 09:11:43'),
(33, 72, 'IN', 1, 'repair', 21, '2026-06-21 09:11:43'),
(34, 74, 'OUT', 1, 'repair', 22, '2026-06-21 09:12:14'),
(35, 72, 'OUT', 1, 'repair', 22, '2026-06-21 09:12:14'),
(36, 74, 'OUT', 1, 'repair', 22, '2026-06-21 09:12:19'),
(37, 74, 'IN', 1, 'repair', 22, '2026-06-21 09:13:09'),
(38, 72, 'IN', 1, 'repair', 22, '2026-06-21 09:13:09'),
(39, 74, 'IN', 1, 'repair', 22, '2026-06-21 09:13:09'),
(40, 74, 'OUT', 1, 'repair', 24, '2026-06-22 06:23:54'),
(41, 72, 'OUT', 1, 'repair', 24, '2026-06-22 06:23:54'),
(42, 74, 'IN', 5, 'purchase', 6, '2026-06-22 08:58:44'),
(43, 74, 'OUT', 4, 'repair', 25, '2026-06-23 02:48:07'),
(44, 74, 'IN', 1, 'purchase', 7, '2026-06-24 16:48:50');

-- --------------------------------------------------------

--
-- Table structure for table `suppliers`
--

CREATE TABLE `suppliers` (
  `id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `contact_person` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `address` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `suppliers`
--

INSERT INTO `suppliers` (`id`, `name`, `contact_person`, `phone`, `email`, `address`, `created_at`) VALUES
(1, 'Lao Ford City Vientiane', 'ຝ່າຍບໍລິການ', '020 76 666 690', 'laofordcity@rmagroup.net', 'ບ້ານວັດໄຕ, ຖະໜົນ ບສປ, ນະຄອນຫຼວງວຽງຈັນ', '2026-04-07 15:17:12'),
(2, 'Isuzu Lao Services', 'ຝ່າຍເຕັກນິກ', '021 316377', 'vilaysack@isuzulaoservices.la', 'ບ້ານໂພນໄຊ, ເມືອງໄຊເສດຖາ, ນະຄອນຫຼວງວຽງຈັນ', '2026-04-07 15:17:12'),
(3, 'Lao Toyota Service', 'ຝ່າຍບໍລິການ', '021 453040', '\rlaotoyotaservicelts@gmail.com', 'ບ້ານວັດນາກ, ຖະໜົນມິດພາບ ລາວ-ໄທ, ນະຄອນຫຼວງວຽງຈັນ', '2026-04-07 15:17:12'),
(4, 'Hyundai Laos (KPL)', 'ຝ່າຍຊ່ວຍເຫຼືອລູກຄ້າ', '021 454500', 'info@hyundailaos.com', 'ບ້ານນາໄຊ, ເມືອງໄຊເສດຖາ, ນະຄອນຫຼວງວຽງຈັນ', '2026-04-26 09:01:59'),
(5, 'Mitsubishi Motors Laos', 'ຝ່າຍບໍລິການ', '021 454000', 'service@mitsubishi-lao.com', 'ບ້ານໂພນສີນວນ, ເມືອງສີສັດຕະນາກ, ນະຄອນຫຼວງວຽງຈັນ', '2026-04-26 09:02:52'),
(6, 'Mazda Laos (K Lao)', 'ຝ່າຍຊ່ວຍເຫຼືອລູກຄ້າ', '021 453535', 'info@mazdalaos.com', 'ບ້ານນາໄຊ, ເມືອງໄຊເສດຖາ, ນະຄອນຫຼວງວຽງຈັນ', '2026-04-26 09:05:23'),
(7, 'Honda New Chip Xeng', 'ຝ່າຍສ້ອມແປງ', '021 213705', 'service@newchipxeng.com', 'ບ້ານສີຫອມ, ເມືອງຈັນທະບູລີ, ນະຄອນຫຼວງວຽງຈັນ', '2026-04-26 09:06:26'),
(8, 'Lattana ຮ້ານຂາຍອາໄຫຼ່ລົດໃຫຍ່ ລາຄາຖືກ ສາຂາ2', 'ພະນັກງານ', '020 78849592', 'lattana@2gmail.com', 'Laos, Vientiane Capital · Vientiane', '2026-04-30 17:56:10'),
(9, '\rJ-auto ຈຳຫນ່າຍເຄືອງຕົບແຕ່ງລົດໃຫຍ່ທຸກຊະນິດ', 'ຝ່າຍບໍລິການ', '\r020 59 926 677', 'jat2@gmail.com', 'Huayhong, Vientiane, Laos', '2026-04-30 17:58:02'),
(10, 'AutoClover ຂາຍເຄື່ອງແຕ່ງລົດໃຫຍ່ລາຄາຖືກ', 'ຝ່າຍບໍລິການ', '020 56787891', 'lungCK@gmail.com', 'ຢູ່ບ້ານ ດົງປະແຫຼບ ,ນະຄອນຫລວງວຽງຈັນ ', '2026-04-30 18:01:20'),
(11, 'ອານຸ ຂາຍສົ່ງອາໄຫຼ່ລົດໃຫຍ່', 'ພະນັກງານຂາຍ', '020 28551144', 'anu@autogmail.com', 'vientiane, Phonphanao , Laos', '2026-04-30 18:04:12');

-- --------------------------------------------------------

--
-- Table structure for table `units`
--

CREATE TABLE `units` (
  `id` int NOT NULL,
  `name` varchar(50) NOT NULL COMMENT 'ຊື່ຫົວໜ່ວຍ',
  `status` enum('active','inactive') DEFAULT 'active' COMMENT 'ສະຖານະ'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='ຂໍ້ມູນຫົວໜ່ວຍ';

--
-- Dumping data for table `units`
--

INSERT INTO `units` (`id`, `name`, `status`) VALUES
(1, 'ອັນ', 'active'),
(2, 'ຕຸກ', 'active'),
(3, 'ຊຸດ', 'active'),
(4, 'ແຜ່ນ', 'active'),
(5, 'ຄູ່', 'active'),
(6, 'ລິດ', 'active');

-- --------------------------------------------------------

--
-- Table structure for table `vehicles`
--

CREATE TABLE `vehicles` (
  `id` int NOT NULL,
  `customer_id` int DEFAULT NULL,
  `plate_number` varchar(50) NOT NULL,
  `model` varchar(100) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `color` varchar(50) DEFAULT NULL,
  `brand_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `vehicles`
--

INSERT INTO `vehicles` (`id`, `customer_id`, `plate_number`, `model`, `year`, `color`, `brand_id`) VALUES
(1, 1, 'ກຂ 1234', 'Fortuner', 2020, 'ຂາວ', NULL),
(2, 1, 'ຄງ 5678', 'CR-V', 2019, 'ດຳ', NULL),
(3, 2, 'ງຈ 9012', 'Triton', 2021, 'ເງິນ', NULL),
(4, 3, 'ຈສ 3456', 'Ranger', 2022, 'ແດງ', NULL),
(5, 4, 'ສຫ 7890', 'Vios', 2020, 'ຂາວ', NULL),
(6, 5, 'ຫຈ 1234', 'City', 2021, 'ຟ້າ', NULL),
(7, 6, 'ຈບ 5678', 'Santa Fe', 2020, 'ດຳ', NULL),
(8, 7, 'ບປ 9012', 'CX-5', 2021, 'ແດງ', NULL),
(9, 8, 'ປຜ 3456', 'Navara', 2022, 'ຂາວ', NULL),
(10, 9, 'ຜພ 7890', 'Hilux', 2019, 'ເງິນ', NULL),
(11, 10, 'ພຟ 2468', 'D-Max', 2020, 'ດຳ', NULL),
(12, 11, 'ຮຮ 7375', 'x1', 2019, 'black', NULL),
(14, 20, 'ຮຮ 7375', 'x1', 2019, 'black', NULL),
(15, 22, 'ຮຮ 7375', 'x1', 2019, 'black', NULL),
(17, 31, 'ກສ 2908', 'x1', 2019, 'white', NULL),
(18, 24, 'ກຮ 8999', 'x2', 2099, 'white', NULL),
(19, 32, 'VB 1234', 'etc', 2013, 'ດຳ', NULL),
(20, 44, 'ກກ 6666', 'v6', 2000, 'black', 10),
(21, NULL, 'ກພ 1234', 'yyy', 2222, 'black', 3),
(22, NULL, 'JHJH6', 'bbn', 7777, '9898', 9),
(23, 44, 'ກຂ 9999', 'x1', 2000, 'black', 3),
(24, 47, 'ມມ 9999', 'Rabtor', 2025, 'ຂາວ', 4),
(25, 47, 'ກຫ 7891', 'X1', 2022, 'black', 2),
(28, 48, 'ຮຮ 1560', 'M1', 2025, 'ຂາວ', 6),
(29, 49, 'ກນ 9909', 'M1', 2011, 'ຮຽນ', 3),
(31, 32, 'ກຄ 4543', 'ຫກັຫກ', 2021, 'ດຳ', 6);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `brands`
--
ALTER TABLE `brands`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `customers`
--
ALTER TABLE `customers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `phone` (`phone`);

--
-- Indexes for table `employees`
--
ALTER TABLE `employees`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `goods_receipts`
--
ALTER TABLE `goods_receipts`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `receipt_no` (`receipt_no`),
  ADD KEY `purchase_order_id` (`purchase_order_id`),
  ADD KEY `supplier_id` (`supplier_id`),
  ADD KEY `received_by` (`received_by`);

--
-- Indexes for table `goods_receipt_items`
--
ALTER TABLE `goods_receipt_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `receipt_id` (`receipt_id`),
  ADD KEY `part_id` (`part_id`);

--
-- Indexes for table `invoices`
--
ALTER TABLE `invoices`
  ADD PRIMARY KEY (`id`),
  ADD KEY `job_order_id` (`job_order_id`),
  ADD KEY `created_by` (`created_by`);

--
-- Indexes for table `job_orders`
--
ALTER TABLE `job_orders`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `job_no` (`job_no`),
  ADD KEY `vehicle_id` (`vehicle_id`),
  ADD KEY `idx_job_orders_status` (`status`),
  ADD KEY `idx_job_orders_customer` (`customer_id`),
  ADD KEY `idx_job_orders_date` (`receive_date`),
  ADD KEY `job_orders_ibfk_created_by` (`created_by`),
  ADD KEY `job_orders_ibfk_closed_by` (`closed_by`);

--
-- Indexes for table `parts`
--
ALTER TABLE `parts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `supplier_id` (`supplier_id`),
  ADD KEY `parts_ibfk_category` (`category_id`),
  ADD KEY `parts_ibfk_unit` (`unit_id`);

--
-- Indexes for table `parts_usage`
--
ALTER TABLE `parts_usage`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_parts_usage_repair` (`repair_id`),
  ADD KEY `idx_parts_usage_part` (`part_id`);

--
-- Indexes for table `part_categories`
--
ALTER TABLE `part_categories`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `promotions`
--
ALTER TABLE `promotions`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `promotion_parts`
--
ALTER TABLE `promotion_parts`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_promotion_part` (`promotion_id`,`part_id`),
  ADD KEY `part_id` (`part_id`);

--
-- Indexes for table `promotion_services`
--
ALTER TABLE `promotion_services`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_promotion_service` (`promotion_id`,`service_id`),
  ADD KEY `service_id` (`service_id`);

--
-- Indexes for table `purchase_items`
--
ALTER TABLE `purchase_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `purchase_id` (`purchase_id`),
  ADD KEY `part_id` (`part_id`);

--
-- Indexes for table `purchase_orders`
--
ALTER TABLE `purchase_orders`
  ADD PRIMARY KEY (`id`),
  ADD KEY `supplier_id` (`supplier_id`),
  ADD KEY `created_by` (`created_by`);

--
-- Indexes for table `quotations`
--
ALTER TABLE `quotations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_quotations_job_order` (`job_order_id`),
  ADD KEY `idx_quotations_status` (`status`),
  ADD KEY `fk_quotations_approved_by` (`approved_by`),
  ADD KEY `quotations_ibfk_promotion` (`promotion_id`),
  ADD KEY `created_by` (`created_by`);

--
-- Indexes for table `quotation_items`
--
ALTER TABLE `quotation_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_quotation_items_quotation` (`quotation_id`),
  ADD KEY `quotation_items_ibfk_2` (`part_id`),
  ADD KEY `quotation_items_ibfk_3` (`service_id`);

--
-- Indexes for table `repair_orders`
--
ALTER TABLE `repair_orders`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_repair_orders_job` (`job_order_id`),
  ADD KEY `idx_repair_orders_status` (`status`),
  ADD KEY `idx_repair_orders_mechanic` (`mechanic_id`);

--
-- Indexes for table `services`
--
ALTER TABLE `services`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `shop`
--
ALTER TABLE `shop`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `stock_movement`
--
ALTER TABLE `stock_movement`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_stock_movement_part` (`part_id`);

--
-- Indexes for table `suppliers`
--
ALTER TABLE `suppliers`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `units`
--
ALTER TABLE `units`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `vehicles`
--
ALTER TABLE `vehicles`
  ADD PRIMARY KEY (`id`),
  ADD KEY `customer_id` (`customer_id`),
  ADD KEY `vehicles_ibfk_brand` (`brand_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `brands`
--
ALTER TABLE `brands`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `customers`
--
ALTER TABLE `customers`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=52;

--
-- AUTO_INCREMENT for table `employees`
--
ALTER TABLE `employees`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `goods_receipts`
--
ALTER TABLE `goods_receipts`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `goods_receipt_items`
--
ALTER TABLE `goods_receipt_items`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `invoices`
--
ALTER TABLE `invoices`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `job_orders`
--
ALTER TABLE `job_orders`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT for table `parts`
--
ALTER TABLE `parts`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=75;

--
-- AUTO_INCREMENT for table `parts_usage`
--
ALTER TABLE `parts_usage`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;

--
-- AUTO_INCREMENT for table `part_categories`
--
ALTER TABLE `part_categories`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `promotions`
--
ALTER TABLE `promotions`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `promotion_parts`
--
ALTER TABLE `promotion_parts`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `promotion_services`
--
ALTER TABLE `promotion_services`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `purchase_items`
--
ALTER TABLE `purchase_items`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `purchase_orders`
--
ALTER TABLE `purchase_orders`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `quotations`
--
ALTER TABLE `quotations`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=44;

--
-- AUTO_INCREMENT for table `quotation_items`
--
ALTER TABLE `quotation_items`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=80;

--
-- AUTO_INCREMENT for table `repair_orders`
--
ALTER TABLE `repair_orders`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `services`
--
ALTER TABLE `services`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `shop`
--
ALTER TABLE `shop`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `stock_movement`
--
ALTER TABLE `stock_movement`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=45;

--
-- AUTO_INCREMENT for table `suppliers`
--
ALTER TABLE `suppliers`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `units`
--
ALTER TABLE `units`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `vehicles`
--
ALTER TABLE `vehicles`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `goods_receipts`
--
ALTER TABLE `goods_receipts`
  ADD CONSTRAINT `goods_receipts_ibfk_1` FOREIGN KEY (`purchase_order_id`) REFERENCES `purchase_orders` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `goods_receipts_ibfk_2` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `goods_receipts_ibfk_3` FOREIGN KEY (`received_by`) REFERENCES `employees` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `goods_receipt_items`
--
ALTER TABLE `goods_receipt_items`
  ADD CONSTRAINT `goods_receipt_items_ibfk_1` FOREIGN KEY (`receipt_id`) REFERENCES `goods_receipts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `goods_receipt_items_ibfk_2` FOREIGN KEY (`part_id`) REFERENCES `parts` (`id`);

--
-- Constraints for table `invoices`
--
ALTER TABLE `invoices`
  ADD CONSTRAINT `invoices_ibfk_1` FOREIGN KEY (`job_order_id`) REFERENCES `job_orders` (`id`);

--
-- Constraints for table `job_orders`
--
ALTER TABLE `job_orders`
  ADD CONSTRAINT `job_orders_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  ADD CONSTRAINT `job_orders_ibfk_2` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`),
  ADD CONSTRAINT `job_orders_ibfk_closed_by` FOREIGN KEY (`closed_by`) REFERENCES `employees` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `job_orders_ibfk_created_by` FOREIGN KEY (`created_by`) REFERENCES `employees` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `parts`
--
ALTER TABLE `parts`
  ADD CONSTRAINT `parts_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `parts_ibfk_category` FOREIGN KEY (`category_id`) REFERENCES `part_categories` (`id`),
  ADD CONSTRAINT `parts_ibfk_unit` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`);

--
-- Constraints for table `parts_usage`
--
ALTER TABLE `parts_usage`
  ADD CONSTRAINT `fk_parts_usage_part` FOREIGN KEY (`part_id`) REFERENCES `parts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `parts_usage_ibfk_1` FOREIGN KEY (`repair_id`) REFERENCES `repair_orders` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `promotion_parts`
--
ALTER TABLE `promotion_parts`
  ADD CONSTRAINT `promotion_parts_ibfk_1` FOREIGN KEY (`promotion_id`) REFERENCES `promotions` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `promotion_parts_ibfk_2` FOREIGN KEY (`part_id`) REFERENCES `parts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `promotion_services`
--
ALTER TABLE `promotion_services`
  ADD CONSTRAINT `promotion_services_ibfk_1` FOREIGN KEY (`promotion_id`) REFERENCES `promotions` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `promotion_services_ibfk_2` FOREIGN KEY (`service_id`) REFERENCES `services` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `purchase_items`
--
ALTER TABLE `purchase_items`
  ADD CONSTRAINT `purchase_items_ibfk_1` FOREIGN KEY (`purchase_id`) REFERENCES `purchase_orders` (`id`),
  ADD CONSTRAINT `purchase_items_ibfk_2` FOREIGN KEY (`part_id`) REFERENCES `parts` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `purchase_orders`
--
ALTER TABLE `purchase_orders`
  ADD CONSTRAINT `purchase_orders_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`),
  ADD CONSTRAINT `purchase_orders_ibfk_created_by` FOREIGN KEY (`created_by`) REFERENCES `employees` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `quotations`
--
ALTER TABLE `quotations`
  ADD CONSTRAINT `fk_quotations_approved_by` FOREIGN KEY (`approved_by`) REFERENCES `employees` (`id`),
  ADD CONSTRAINT `quotations_ibfk_1` FOREIGN KEY (`job_order_id`) REFERENCES `job_orders` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `quotations_ibfk_promotion` FOREIGN KEY (`promotion_id`) REFERENCES `promotions` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `quotation_items`
--
ALTER TABLE `quotation_items`
  ADD CONSTRAINT `quotation_items_ibfk_1` FOREIGN KEY (`quotation_id`) REFERENCES `quotations` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `quotation_items_ibfk_2` FOREIGN KEY (`part_id`) REFERENCES `parts` (`id`),
  ADD CONSTRAINT `quotation_items_ibfk_3` FOREIGN KEY (`service_id`) REFERENCES `services` (`id`);

--
-- Constraints for table `repair_orders`
--
ALTER TABLE `repair_orders`
  ADD CONSTRAINT `repair_orders_ibfk_1` FOREIGN KEY (`job_order_id`) REFERENCES `job_orders` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `repair_orders_ibfk_mechanic` FOREIGN KEY (`mechanic_id`) REFERENCES `employees` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `stock_movement`
--
ALTER TABLE `stock_movement`
  ADD CONSTRAINT `fk_stock_movement_part` FOREIGN KEY (`part_id`) REFERENCES `parts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `vehicles`
--
ALTER TABLE `vehicles`
  ADD CONSTRAINT `vehicles_ibfk_brand` FOREIGN KEY (`brand_id`) REFERENCES `brands` (`id`),
  ADD CONSTRAINT `vehicles_ibfk_customer` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
