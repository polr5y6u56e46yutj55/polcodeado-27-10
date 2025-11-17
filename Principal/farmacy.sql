-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 27-10-2025 a las 19:45:24
-- Versión del servidor: 10.4.24-MariaDB
-- Versión de PHP: 7.4.29

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `farmacy`
--
CREATE DATABASE IF NOT EXISTS `farmacy` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `farmacy`;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

DROP TABLE IF EXISTS `clientes`;
CREATE TABLE `clientes` (
  `ID` int(11) NOT NULL,
  `Nombre` varchar(80) DEFAULT NULL,
  `DNI` int(20) DEFAULT NULL,
  `Historial_compras` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `clientes`
--

INSERT INTO `clientes` (`ID`, `Nombre`, `DNI`, `Historial_compras`) VALUES
(1, 'Juan', 12345678, 'Cliente frecuente'),
(2, 'Ana', 87654321, 'Cliente eventual'),
(3, 'Luis', 11223344, 'Cliente frecuente');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empleados`
--

DROP TABLE IF EXISTS `empleados`;
CREATE TABLE `empleados` (
  `ID` int(11) NOT NULL,
  `Nombre__` varchar(80) DEFAULT NULL,
  `Rol` varchar(80) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `empleados`
--

INSERT INTO `empleados` (`ID`, `Nombre__`, `Rol`) VALUES
(1, 'María González', 'Farmacéutica'),
(2, 'Carlos López', 'Encargado de stock'),
(3, 'Lucía Fernández', 'Caja'),
(4, 'Diego Martínez', 'Repositor'),
(5, 'Ana Silva', 'Administración'),
(6, 'Javier Ruiz', 'Repartidor'),
(7, 'Sofía Díaz', 'Responsable técnico');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `medicamentos`
--

DROP TABLE IF EXISTS `medicamentos`;
CREATE TABLE `medicamentos` (
  `Id` int(11) NOT NULL,
  `Nombre_` varchar(255) DEFAULT NULL,
  `Categoria` varchar(80) DEFAULT NULL,
  `Precio` decimal(10,2) DEFAULT NULL,
  `Stock` int(255) DEFAULT NULL,
  `Codigo_Barras` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `medicamentos`
--

INSERT INTO `medicamentos` (`Id`, `Nombre_`, `Categoria`, `Precio`, `Stock`, `Codigo_Barras`) VALUES
(1, 'Paracetamol 500mg', 'Analgésico', '150.00', 50, '111111'),
(2, 'Ibuprofeno 400mg', 'Analgésico', '200.00', 8, '222222'),
(3, 'Amoxicilina 500mg', 'Antibiótico', '350.00', 5, '333333'),
(4, 'Loratadina 10mg', 'Antihistamínico', '120.00', 20, '444444'),
(5, 'Omeprazol 20mg', 'Antiácido', '180.00', 3, '555555');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ventas`
--

DROP TABLE IF EXISTS `ventas`;
CREATE TABLE `ventas` (
  `ID` int(11) NOT NULL,
  `Fecha` date DEFAULT NULL,
  `Cantidad` int(255) DEFAULT NULL,
  `id_Medicamentos` int(11) DEFAULT NULL,
  `id_Clientes` int(11) DEFAULT NULL,
  `id_Empleados` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `ventas`
--

INSERT INTO `ventas` (`ID`, `Fecha`, `Cantidad`, `id_Medicamentos`, `id_Clientes`, `id_Empleados`) VALUES
(1, '2025-08-01', 5, 1, 1, 1),
(2, '2025-08-02', 2, 2, 1, 3),
(3, '2025-08-03', 3, 3, 2, 1),
(4, '2025-08-04', 10, 1, 1, 2),
(5, '2025-08-05', 1, 5, 3, 4),
(6, '2025-08-05', 4, 2, 3, 3),
(7, '2025-08-05', 6, 4, 1, 5),
(8, '2025-08-07', 2, 3, 1, 1),
(9, '2025-08-07', 1, 3, 1, 2),
(10, '2025-08-08', 1, 2, 1, 3);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD PRIMARY KEY (`ID`);

--
-- Indices de la tabla `empleados`
--
ALTER TABLE `empleados`
  ADD PRIMARY KEY (`ID`);

--
-- Indices de la tabla `medicamentos`
--
ALTER TABLE `medicamentos`
  ADD PRIMARY KEY (`Id`),
  ADD UNIQUE KEY `Codigo_Barras` (`Codigo_Barras`);

--
-- Indices de la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `id_Medicamentos` (`id_Medicamentos`),
  ADD KEY `id_Clientes` (`id_Clientes`),
  ADD KEY `id_Empleados` (`id_Empleados`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `clientes`
--
ALTER TABLE `clientes`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `empleados`
--
ALTER TABLE `empleados`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `medicamentos`
--
ALTER TABLE `medicamentos`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `ventas`
--
ALTER TABLE `ventas`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD CONSTRAINT `ventas_ibfk_1` FOREIGN KEY (`id_Medicamentos`) REFERENCES `medicamentos` (`Id`),
  ADD CONSTRAINT `ventas_ibfk_2` FOREIGN KEY (`id_Clientes`) REFERENCES `clientes` (`ID`),
  ADD CONSTRAINT `ventas_ibfk_3` FOREIGN KEY (`id_Empleados`) REFERENCES `empleados` (`ID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
