-- Conectta Serra MySQL backup
-- Generated 2026-11-25T19:14:05
SET FOREIGN_KEY_CHECKS=0;
SET NAMES utf8mb4;
DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
INSERT INTO `alembic_version` (`version_num`) VALUES ('882e15b6175d');
DROP TABLE IF EXISTS `app_meta`;
CREATE TABLE `app_meta` (
  `key` varchar(80) NOT NULL,
  `value` text NOT NULL,
  PRIMARY KEY (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
INSERT INTO `app_meta` (`key`, `value`) VALUES ('seed_v1', '1');
DROP TABLE IF EXISTS `categories`;
CREATE TABLE `categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(60) NOT NULL,
  `icon` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
INSERT INTO `categories` (`id`, `name`, `icon`) VALUES (1, 'Elétrica', 'bolt');
INSERT INTO `categories` (`id`, `name`, `icon`) VALUES (2, 'Limpeza', 'sparkles');
INSERT INTO `categories` (`id`, `name`, `icon`) VALUES (3, 'Hidráulica', 'drop');
INSERT INTO `categories` (`id`, `name`, `icon`) VALUES (4, 'Pintura', 'paint');
INSERT INTO `categories` (`id`, `name`, `icon`) VALUES (5, 'Refrigeração', 'snow');
INSERT INTO `categories` (`id`, `name`, `icon`) VALUES (6, 'Montagem', 'chair');
DROP TABLE IF EXISTS `favorites`;
CREATE TABLE `favorites` (
  `user_id` int(11) NOT NULL,
  `professional_id` int(11) NOT NULL,
  PRIMARY KEY (`user_id`,`professional_id`),
  KEY `professional_id` (`professional_id`),
  CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`professional_id`) REFERENCES `professionals` (`id`) ON DELETE CASCADE,
  CONSTRAINT `favorites_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
DROP TABLE IF EXISTS `messages`;
CREATE TABLE `messages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `request_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `body` text NOT NULL,
  `created_at` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `request_id` (`request_id`),
  KEY `sender_id` (`sender_id`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`request_id`) REFERENCES `requests` (`id`),
  CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
INSERT INTO `messages` (`id`, `request_id`, `sender_id`, `body`, `created_at`) VALUES (1, 3, 1, 'Olá, Rafael! Você tem disponibilidade para conversar sobre a instalação?', '2026-11-09T12:01:00Z');
DROP TABLE IF EXISTS `professionals`;
CREATE TABLE `professionals` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `profession` varchar(80) NOT NULL,
  `bio` text NOT NULL,
  `experience` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `professionals_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
INSERT INTO `professionals` (`id`, `user_id`, `profession`, `bio`, `experience`) VALUES (1, 2, 'Eletricista residencial', 'Cuidado em cada conexão. Instalações, manutenção e pequenos reparos elétricos em Serra Talhada.', 8);
INSERT INTO `professionals` (`id`, `user_id`, `profession`, `bio`, `experience`) VALUES (2, 4, 'Diarista e organização', 'Mais tempo para você, mais cuidado para sua casa. Limpeza residencial e organização de ambientes.', 5);
INSERT INTO `professionals` (`id`, `user_id`, `profession`, `bio`, `experience`) VALUES (3, 5, 'Encanador', 'Do vazamento ao chuveiro novo: soluções práticas para a hidráulica da sua casa.', 10);
INSERT INTO `professionals` (`id`, `user_id`, `profession`, `bio`, `experience`) VALUES (4, 6, 'Pintora residencial', 'Transformo ambientes com acabamento cuidadoso, cores e atenção aos detalhes.', 6);
INSERT INTO `professionals` (`id`, `user_id`, `profession`, `bio`, `experience`) VALUES (5, 7, 'Técnico em refrigeração', 'Seu conforto em boas mãos. Higienização e manutenção preventiva de ar-condicionado.', 7);
INSERT INTO `professionals` (`id`, `user_id`, `profession`, `bio`, `experience`) VALUES (6, 8, 'Montador de móveis', 'Seu espaço pronto para viver. Montagem e ajustes de móveis com cuidado e precisão.', 4);
DROP TABLE IF EXISTS `requests`;
CREATE TABLE `requests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `client_id` int(11) NOT NULL,
  `professional_id` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  `description` text NOT NULL,
  `neighborhood` varchar(60) NOT NULL,
  `preferred_date` varchar(10) NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `client_id` (`client_id`),
  KEY `professional_id` (`professional_id`),
  KEY `service_id` (`service_id`),
  CONSTRAINT `requests_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `users` (`id`),
  CONSTRAINT `requests_ibfk_2` FOREIGN KEY (`professional_id`) REFERENCES `professionals` (`id`),
  CONSTRAINT `requests_ibfk_3` FOREIGN KEY (`service_id`) REFERENCES `services` (`id`),
  CONSTRAINT `CONSTRAINT_1` CHECK (`status` in ('pendente','aceita','concluida','cancelada'))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
INSERT INTO `requests` (`id`, `client_id`, `professional_id`, `service_id`, `description`, `neighborhood`, `preferred_date`, `status`, `created_at`) VALUES (1, 1, 1, 1, 'Troca de duas tomadas da sala.', 'Centro', '2026-11-05', 'concluida', '2026-11-01T12:00:00Z');
INSERT INTO `requests` (`id`, `client_id`, `professional_id`, `service_id`, `description`, `neighborhood`, `preferred_date`, `status`, `created_at`) VALUES (2, 1, 2, 2, 'Limpeza do apartamento.', 'Centro', '2026-11-06', 'concluida', '2026-11-02T12:00:00Z');
INSERT INTO `requests` (`id`, `client_id`, `professional_id`, `service_id`, `description`, `neighborhood`, `preferred_date`, `status`, `created_at`) VALUES (3, 1, 1, 7, 'Gostaria de instalar um pendente na sala. Já tenho a luminária.', 'Centro', '2026-12-01', 'pendente', '2026-11-09T12:00:00Z');
DROP TABLE IF EXISTS `reviews`;
CREATE TABLE `reviews` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `request_id` int(11) NOT NULL,
  `author_id` int(11) NOT NULL,
  `professional_id` int(11) NOT NULL,
  `rating` int(11) NOT NULL,
  `comment` text NOT NULL,
  `created_at` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `request_id` (`request_id`),
  KEY `author_id` (`author_id`),
  KEY `professional_id` (`professional_id`),
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`),
  CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`professional_id`) REFERENCES `professionals` (`id`),
  CONSTRAINT `reviews_ibfk_3` FOREIGN KEY (`request_id`) REFERENCES `requests` (`id`),
  CONSTRAINT `CONSTRAINT_1` CHECK (`rating` between 1 and 5)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
INSERT INTO `reviews` (`id`, `request_id`, `author_id`, `professional_id`, `rating`, `comment`, `created_at`) VALUES (1, 1, 1, 1, 5, 'Atencioso, pontual e explicou tudo direitinho. Serviço muito bem feito!', '2026-11-05T15:00:00Z');
INSERT INTO `reviews` (`id`, `request_id`, `author_id`, `professional_id`, `rating`, `comment`, `created_at`) VALUES (2, 2, 1, 2, 5, 'A casa ficou um capricho. Recomendo o cuidado e a organização!', '2026-11-06T15:00:00Z');
DROP TABLE IF EXISTS `services`;
CREATE TABLE `services` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `professional_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `title` varchar(100) NOT NULL,
  `description` text NOT NULL,
  `price` float NOT NULL,
  `unit` varchar(30) NOT NULL,
  `active` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  KEY `professional_id` (`professional_id`),
  CONSTRAINT `services_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`),
  CONSTRAINT `services_ibfk_2` FOREIGN KEY (`professional_id`) REFERENCES `professionals` (`id`),
  CONSTRAINT `CONSTRAINT_1` CHECK (`price` >= 0)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
INSERT INTO `services` (`id`, `professional_id`, `category_id`, `title`, `description`, `price`, `unit`, `active`) VALUES (1, 1, 1, 'Instalação e reparos elétricos', 'Tomadas, interruptores, luminárias e pequenos reparos. Orçamento final após avaliação.', 80.0, 'serviço', 1);
INSERT INTO `services` (`id`, `professional_id`, `category_id`, `title`, `description`, `price`, `unit`, `active`) VALUES (2, 2, 2, 'Limpeza e cuidado com seu lar', 'Limpeza residencial de ambientes. Materiais e duração combinados no orçamento.', 150.0, 'diária', 1);
INSERT INTO `services` (`id`, `professional_id`, `category_id`, `title`, `description`, `price`, `unit`, `active`) VALUES (3, 3, 3, 'Reparos hidráulicos', 'Conserto de torneiras e vazamentos aparentes. Peças e materiais à parte.', 90.0, 'serviço', 1);
INSERT INTO `services` (`id`, `professional_id`, `category_id`, `title`, `description`, `price`, `unit`, `active`) VALUES (4, 4, 4, 'Pintura de ambientes', 'Preparação e pintura de paredes internas. Valor de referência por metro quadrado.', 18.0, 'm²', 1);
INSERT INTO `services` (`id`, `professional_id`, `category_id`, `title`, `description`, `price`, `unit`, `active`) VALUES (5, 5, 5, 'Higienização de ar-condicionado', 'Limpeza preventiva de split residencial. Avaliação do aparelho antes da execução.', 140.0, 'serviço', 1);
INSERT INTO `services` (`id`, `professional_id`, `category_id`, `title`, `description`, `price`, `unit`, `active`) VALUES (6, 6, 6, 'Montagem de móveis', 'Montagem de mesas, estantes e móveis residenciais. Consulte orçamento para cada peça.', 100.0, 'móvel', 1);
INSERT INTO `services` (`id`, `professional_id`, `category_id`, `title`, `description`, `price`, `unit`, `active`) VALUES (7, 1, 1, 'Instalação de luminárias', 'Instalação de luminárias e pendentes em ponto elétrico existente.', 60.0, 'unidade', 1);
INSERT INTO `services` (`id`, `professional_id`, `category_id`, `title`, `description`, `price`, `unit`, `active`) VALUES (8, 2, 2, 'Organização de ambientes', 'Organização de armários e cômodos com soluções para sua rotina.', 100.0, 'serviço', 1);
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  `email` varchar(120) NOT NULL,
  `phone` varchar(30) NOT NULL,
  `role` varchar(20) NOT NULL,
  `neighborhood` varchar(60) NOT NULL,
  `demo` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `CONSTRAINT_1` CHECK (`role` in ('cliente','profissional','admin'))
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `role`, `neighborhood`, `demo`) VALUES (1, 'Marina Alves', 'marina@conectta.example', '', 'cliente', 'Centro', 1);
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `role`, `neighborhood`, `demo`) VALUES (2, 'Rafael Lima', 'rafael@conectta.example', '', 'profissional', 'São Cristóvão', 1);
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `role`, `neighborhood`, `demo`) VALUES (3, 'Gestor Conectta', 'gestor@conectta.example', '', 'admin', 'Centro', 1);
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `role`, `neighborhood`, `demo`) VALUES (4, 'Camila Santos', 'camila@conectta.example', '', 'profissional', 'AABB', 1);
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `role`, `neighborhood`, `demo`) VALUES (5, 'João Oliveira', 'joao@conectta.example', '', 'profissional', 'Bom Jesus', 1);
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `role`, `neighborhood`, `demo`) VALUES (6, 'Ana Beatriz', 'ana@conectta.example', '', 'profissional', 'Centro', 1);
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `role`, `neighborhood`, `demo`) VALUES (7, 'Lucas Ferreira', 'lucas@conectta.example', '', 'profissional', 'IPSEP', 1);
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `role`, `neighborhood`, `demo`) VALUES (8, 'Pedro Costa', 'pedro@conectta.example', '', 'profissional', 'Caxixola', 1);
DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE `usuarios` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `nome` varchar(120) NOT NULL,
  `email` varchar(190) NOT NULL,
  `telefone` varchar(30) DEFAULT NULL,
  `perfil` varchar(30) NOT NULL DEFAULT 'Usuário',
  `criado_em` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_usuarios_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
SET FOREIGN_KEY_CHECKS=1;
