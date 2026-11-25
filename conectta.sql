-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Tempo de geração: 25/11/2026 às 22:39
-- Versão do servidor: 10.4.32-MariaDB
-- Versão do PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Banco de dados: `conectta`
--

-- --------------------------------------------------------

--
-- Estrutura para tabela `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('882e15b6175d');

-- --------------------------------------------------------

--
-- Estrutura para tabela `app_meta`
--

CREATE TABLE `app_meta` (
  `key` varchar(80) NOT NULL,
  `value` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `app_meta`
--

INSERT INTO `app_meta` (`key`, `value`) VALUES
('seed_v1', '1');

-- --------------------------------------------------------

--
-- Estrutura para tabela `categories`
--

CREATE TABLE `categories` (
  `id` int(11) NOT NULL,
  `name` varchar(60) NOT NULL,
  `icon` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `categories`
--

INSERT INTO `categories` (`id`, `name`, `icon`) VALUES
(1, 'Elétrica', 'bolt'),
(2, 'Limpeza', 'sparkles'),
(3, 'Hidráulica', 'drop'),
(4, 'Pintura', 'paint'),
(5, 'Refrigeração', 'snow'),
(6, 'Montagem', 'chair');

-- --------------------------------------------------------

--
-- Estrutura para tabela `favorites`
--

CREATE TABLE `favorites` (
  `user_id` int(11) NOT NULL,
  `professional_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `messages`
--

CREATE TABLE `messages` (
  `id` int(11) NOT NULL,
  `request_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `body` text NOT NULL,
  `created_at` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `messages`
--

INSERT INTO `messages` (`id`, `request_id`, `sender_id`, `body`, `created_at`) VALUES
(1, 3, 1, 'Olá, Rafael! Você tem disponibilidade para conversar sobre a instalação?', '2026-11-09T12:01:00Z');

-- --------------------------------------------------------

--
-- Estrutura para tabela `professionals`
--

CREATE TABLE `professionals` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `profession` varchar(80) NOT NULL,
  `bio` text NOT NULL,
  `experience` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `professionals`
--

INSERT INTO `professionals` (`id`, `user_id`, `profession`, `bio`, `experience`) VALUES
(1, 2, 'Eletricista residencial', 'Cuidado em cada conexão. Instalações, manutenção e pequenos reparos elétricos em Serra Talhada.', 8),
(2, 4, 'Diarista e organização', 'Mais tempo para você, mais cuidado para sua casa. Limpeza residencial e organização de ambientes.', 5),
(3, 5, 'Encanador', 'Do vazamento ao chuveiro novo: soluções práticas para a hidráulica da sua casa.', 10),
(4, 6, 'Pintora residencial', 'Transformo ambientes com acabamento cuidadoso, cores e atenção aos detalhes.', 6),
(5, 7, 'Técnico em refrigeração', 'Seu conforto em boas mãos. Higienização e manutenção preventiva de ar-condicionado.', 7),
(6, 8, 'Montador de móveis', 'Seu espaço pronto para viver. Montagem e ajustes de móveis com cuidado e precisão.', 4);

-- --------------------------------------------------------

--
-- Estrutura para tabela `requests`
--

CREATE TABLE `requests` (
  `id` int(11) NOT NULL,
  `client_id` int(11) NOT NULL,
  `professional_id` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  `description` text NOT NULL,
  `neighborhood` varchar(60) NOT NULL,
  `preferred_date` varchar(10) NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` varchar(30) NOT NULL
) ;

--
-- Despejando dados para a tabela `requests`
--

INSERT INTO `requests` (`id`, `client_id`, `professional_id`, `service_id`, `description`, `neighborhood`, `preferred_date`, `status`, `created_at`) VALUES
(1, 1, 1, 1, 'Troca de duas tomadas da sala.', 'Centro', '2026-11-05', 'concluida', '2026-11-01T12:00:00Z'),
(2, 1, 2, 2, 'Limpeza do apartamento.', 'Centro', '2026-11-06', 'concluida', '2026-11-02T12:00:00Z'),
(3, 1, 1, 7, 'Gostaria de instalar um pendente na sala. Já tenho a luminária.', 'Centro', '2026-12-01', 'pendente', '2026-11-09T12:00:00Z');

-- --------------------------------------------------------

--
-- Estrutura para tabela `reviews`
--

CREATE TABLE `reviews` (
  `id` int(11) NOT NULL,
  `request_id` int(11) NOT NULL,
  `author_id` int(11) NOT NULL,
  `professional_id` int(11) NOT NULL,
  `rating` int(11) NOT NULL,
  `comment` text NOT NULL,
  `created_at` varchar(30) NOT NULL
) ;

--
-- Despejando dados para a tabela `reviews`
--

INSERT INTO `reviews` (`id`, `request_id`, `author_id`, `professional_id`, `rating`, `comment`, `created_at`) VALUES
(1, 1, 1, 1, 5, 'Atencioso, pontual e explicou tudo direitinho. Serviço muito bem feito!', '2026-11-05T15:00:00Z'),
(2, 2, 1, 2, 5, 'A casa ficou um capricho. Recomendo o cuidado e a organização!', '2026-11-06T15:00:00Z');

-- --------------------------------------------------------

--
-- Estrutura para tabela `services`
--

CREATE TABLE `services` (
  `id` int(11) NOT NULL,
  `professional_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `title` varchar(100) NOT NULL,
  `description` text NOT NULL,
  `price` float NOT NULL,
  `unit` varchar(30) NOT NULL,
  `active` int(11) NOT NULL
) ;

--
-- Despejando dados para a tabela `services`
--

INSERT INTO `services` (`id`, `professional_id`, `category_id`, `title`, `description`, `price`, `unit`, `active`) VALUES
(1, 1, 1, 'Instalação e reparos elétricos', 'Tomadas, interruptores, luminárias e pequenos reparos. Orçamento final após avaliação.', 80, 'serviço', 1),
(2, 2, 2, 'Limpeza e cuidado com seu lar', 'Limpeza residencial de ambientes. Materiais e duração combinados no orçamento.', 150, 'diária', 1),
(3, 3, 3, 'Reparos hidráulicos', 'Conserto de torneiras e vazamentos aparentes. Peças e materiais à parte.', 90, 'serviço', 1),
(4, 4, 4, 'Pintura de ambientes', 'Preparação e pintura de paredes internas. Valor de referência por metro quadrado.', 18, 'm²', 1),
(5, 5, 5, 'Higienização de ar-condicionado', 'Limpeza preventiva de split residencial. Avaliação do aparelho antes da execução.', 140, 'serviço', 1),
(6, 6, 6, 'Montagem de móveis', 'Montagem de mesas, estantes e móveis residenciais. Consulte orçamento para cada peça.', 100, 'móvel', 1),
(7, 1, 1, 'Instalação de luminárias', 'Instalação de luminárias e pendentes em ponto elétrico existente.', 60, 'unidade', 1),
(8, 2, 2, 'Organização de ambientes', 'Organização de armários e cômodos com soluções para sua rotina.', 100, 'serviço', 1);

-- --------------------------------------------------------

--
-- Estrutura para tabela `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(80) NOT NULL,
  `email` varchar(120) NOT NULL,
  `phone` varchar(30) NOT NULL,
  `role` varchar(20) NOT NULL,
  `neighborhood` varchar(60) NOT NULL,
  `demo` int(11) NOT NULL
) ;

--
-- Despejando dados para a tabela `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `phone`, `role`, `neighborhood`, `demo`) VALUES
(1, 'Marina Alves', 'marina@conectta.example', '', 'cliente', 'Centro', 1),
(2, 'Rafael Lima', 'rafael@conectta.example', '', 'profissional', 'São Cristóvão', 1),
(3, 'Gestor Conectta', 'gestor@conectta.example', '', 'admin', 'Centro', 1),
(4, 'Camila Santos', 'camila@conectta.example', '', 'profissional', 'AABB', 1),
(5, 'João Oliveira', 'joao@conectta.example', '', 'profissional', 'Bom Jesus', 1),
(6, 'Ana Beatriz', 'ana@conectta.example', '', 'profissional', 'Centro', 1),
(7, 'Lucas Ferreira', 'lucas@conectta.example', '', 'profissional', 'IPSEP', 1),
(8, 'Pedro Costa', 'pedro@conectta.example', '', 'profissional', 'Caxixola', 1);

-- --------------------------------------------------------

--
-- Estrutura para tabela `usuarios`
--

CREATE TABLE `usuarios` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `nome` varchar(120) NOT NULL,
  `email` varchar(190) NOT NULL,
  `telefone` varchar(30) DEFAULT NULL,
  `perfil` varchar(30) NOT NULL DEFAULT 'Usuário',
  `criado_em` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Índices para tabelas despejadas
--

--
-- Índices de tabela `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Índices de tabela `app_meta`
--
ALTER TABLE `app_meta`
  ADD PRIMARY KEY (`key`);

--
-- Índices de tabela `categories`
--
ALTER TABLE `categories`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Índices de tabela `favorites`
--
ALTER TABLE `favorites`
  ADD PRIMARY KEY (`user_id`,`professional_id`),
  ADD KEY `professional_id` (`professional_id`);

--
-- Índices de tabela `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `request_id` (`request_id`),
  ADD KEY `sender_id` (`sender_id`);

--
-- Índices de tabela `professionals`
--
ALTER TABLE `professionals`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Índices de tabela `requests`
--
ALTER TABLE `requests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `client_id` (`client_id`),
  ADD KEY `professional_id` (`professional_id`),
  ADD KEY `service_id` (`service_id`);

--
-- Índices de tabela `reviews`
--
ALTER TABLE `reviews`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `request_id` (`request_id`),
  ADD KEY `author_id` (`author_id`),
  ADD KEY `professional_id` (`professional_id`);

--
-- Índices de tabela `services`
--
ALTER TABLE `services`
  ADD PRIMARY KEY (`id`),
  ADD KEY `category_id` (`category_id`),
  ADD KEY `professional_id` (`professional_id`);

--
-- Índices de tabela `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Índices de tabela `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_usuarios_email` (`email`);

--
-- AUTO_INCREMENT para tabelas despejadas
--

--
-- AUTO_INCREMENT de tabela `categories`
--
ALTER TABLE `categories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de tabela `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de tabela `professionals`
--
ALTER TABLE `professionals`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de tabela `requests`
--
ALTER TABLE `requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `reviews`
--
ALTER TABLE `reviews`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `services`
--
ALTER TABLE `services`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Restrições para tabelas despejadas
--

--
-- Restrições para tabelas `favorites`
--
ALTER TABLE `favorites`
  ADD CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`professional_id`) REFERENCES `professionals` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `favorites_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Restrições para tabelas `messages`
--
ALTER TABLE `messages`
  ADD CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`request_id`) REFERENCES `requests` (`id`),
  ADD CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`);

--
-- Restrições para tabelas `professionals`
--
ALTER TABLE `professionals`
  ADD CONSTRAINT `professionals_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Restrições para tabelas `requests`
--
ALTER TABLE `requests`
  ADD CONSTRAINT `requests_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `requests_ibfk_2` FOREIGN KEY (`professional_id`) REFERENCES `professionals` (`id`),
  ADD CONSTRAINT `requests_ibfk_3` FOREIGN KEY (`service_id`) REFERENCES `services` (`id`);

--
-- Restrições para tabelas `reviews`
--
ALTER TABLE `reviews`
  ADD CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`professional_id`) REFERENCES `professionals` (`id`),
  ADD CONSTRAINT `reviews_ibfk_3` FOREIGN KEY (`request_id`) REFERENCES `requests` (`id`);

--
-- Restrições para tabelas `services`
--
ALTER TABLE `services`
  ADD CONSTRAINT `services_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`),
  ADD CONSTRAINT `services_ibfk_2` FOREIGN KEY (`professional_id`) REFERENCES `professionals` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
