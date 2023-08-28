-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 28, 2023 at 08:58 AM
-- Server version: 10.4.25-MariaDB
-- PHP Version: 8.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_facerecognition`
--

-- --------------------------------------------------------

--
-- Table structure for table `tb_users`
--

CREATE TABLE `tb_users` (
  `id_user` int(11) NOT NULL,
  `prefix` varchar(10) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `major` varchar(50) NOT NULL,
  `studentid` varchar(50) NOT NULL,
  `imageuser` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `tb_users`
--

INSERT INTO `tb_users` (`id_user`, `prefix`, `first_name`, `last_name`, `major`, `studentid`, `imageuser`) VALUES
(2, 'นาย', 'ธีรวัฒน์', 'พิณไชย', 'วศ.บ.วิศวกรรมคอมพิวเตอร์', '63543206064-1', '63543206064-1'),
(3, 'นาย', 'กิตติภณ', 'ชัยวรรณ', 'วศ.บ.วิศวกรรมคอมพิวเตอร์', '63543206052-6', '63543206052-6'),
(4, 'นาง', 'ภานุชนารถ', 'ฝั่นสุตา', 'วศ.บ.วิศวกรรมคอมพิวเตอร์', '63543206032-8', '63543206032-8'),
(5, 'นาย', 'ศวกร', 'ร่มโพธิ์เงิน', 'วศ.บ.วิศวกรรมคอมพิวเตอร์', '63543206074-0', '63543206074-0'),
(6, 'นาย', 'จิตตพงษ์', 'จงใจ', 'วศ.บ.วิศวกรรมคอมพิวเตอร์', '65543206007-8', '65543206007-8'),
(7, 'นาย', 'ชยธร', 'เอียดราช', 'วศ.บ.วิศวกรรมคอมพิวเตอร์', '65543206049-0', '65543206049-0'),
(8, 'นาย', 'ประพันธ์', 'แข็งขัน', 'วศ.บ.วิศวกรรมคอมพิวเตอร์', '65543206022-7', '65543206022-7'),
(9, 'นาย', 'ธนาวุฒิ', 'มนัสสา', 'วศ.บ.วิศวกรรมคอมพิวเตอร์', '65543206062-3', '65543206062-3'),
(10, 'นาย', 'ธีรเดช', 'ประเสริฐวงศ์พนา', 'วศ.บ.วิศวกรรมคอมพิวเตอร์', '65543206016-9', '65543206016-9'),
(11, 'นาย', 'พัทธนันท์', 'ใจช่วย', 'วศ.บ.วิศวกรรมคอมพิวเตอร์', '65543206026-8', '65543206026-8'),
(12, 'นาย', 'ธีระภัทร', 'ชมเชย', 'วศ.บ.วิศวกรรมคอมพิวเตอร์', '65543206019-3', '65543206019-3'),
(13, 'นาย', 'อังศุพันธ์', 'ทารวัน', 'วศ.บ.วิศวกรรมคอมพิวเตอร์', '63543206044-3', '63543206044-3'),
(14, 'นางสาว', 'กานต์สินี', 'ธรรมวงค์', '', '63543206004-7', '63543206004-7'),
(15, 'นางสาว', 'A', 'B', '-', '63543206789-1', '63543206789-1');

-- --------------------------------------------------------

--
-- Table structure for table `tb_user_logs`
--

CREATE TABLE `tb_user_logs` (
  `id_logs` int(50) NOT NULL,
  `studentid` varchar(50) NOT NULL,
  `report_date` date NOT NULL,
  `timestamp` time NOT NULL,
  `temperature` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `tb_user_logs`
--

INSERT INTO `tb_user_logs` (`id_logs`, `studentid`, `report_date`, `timestamp`, `temperature`) VALUES
(1, '63543206064-1', '2023-07-01', '16:15:44', 37.4),
(2, '63543206052-6', '2023-07-02', '22:15:44', 37.6),
(3, '63543206032-8', '2023-07-03', '21:17:15', 37.4),
(4, '63543206074-0', '2023-07-04', '22:15:44', 37.6),
(5, '65543206007-8', '2023-08-10', '16:05:19', 37.4),
(6, '65543206049-0', '2023-08-23', '20:06:19', 37.4),
(7, '65543206022-7', '2023-07-27', '32:06:19', 37.6),
(8, '65543206062-3', '2023-07-18', '31:28:12', 37.4),
(9, '65543206016-9', '2023-08-22', '47:28:12', 37.6);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tb_users`
--
ALTER TABLE `tb_users`
  ADD PRIMARY KEY (`id_user`);

--
-- Indexes for table `tb_user_logs`
--
ALTER TABLE `tb_user_logs`
  ADD PRIMARY KEY (`id_logs`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tb_users`
--
ALTER TABLE `tb_users`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `tb_user_logs`
--
ALTER TABLE `tb_user_logs`
  MODIFY `id_logs` int(50) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
