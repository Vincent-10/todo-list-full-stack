-- =====================================================
-- Todo-List 应用数据库设计
-- 模块：任务管理、分类/标签、搜索和过滤
-- 数据库：MySQL 8.0+
-- 创建时间：2026-04-07
-- =====================================================

-- -----------------------------------------------------
-- 数据库创建
-- -----------------------------------------------------
CREATE DATABASE IF NOT EXISTS `todolist` 
  DEFAULT CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

USE `todolist`;

-- =====================================================
-- 用户模块（基础支撑）
-- =====================================================

-- -----------------------------------------------------
-- 用户表
-- -----------------------------------------------------
CREATE TABLE `users` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名',
  `email` VARCHAR(100) NOT NULL COMMENT '邮箱',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
  `avatar_url` VARCHAR(500) DEFAULT NULL COMMENT '头像URL',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态：0-禁用，1-正常',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_email` (`email`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- =====================================================
-- 分类/标签模块
-- =====================================================

-- -----------------------------------------------------
-- 分类表（一级分类）
-- -----------------------------------------------------
CREATE TABLE `categories` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '分类ID',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '所属用户ID',
  `name` VARCHAR(50) NOT NULL COMMENT '分类名称',
  `color` VARCHAR(7) DEFAULT '#3B82F6' COMMENT '分类颜色（十六进制）',
  `icon` VARCHAR(50) DEFAULT NULL COMMENT '图标名称',
  `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序顺序',
  `is_default` TINYINT NOT NULL DEFAULT 0 COMMENT '是否默认分类：0-否，1-是',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_user_sort` (`user_id`, `sort_order`),
  CONSTRAINT `fk_categories_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务分类表';

-- -----------------------------------------------------
-- 标签表
-- -----------------------------------------------------
CREATE TABLE `tags` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '标签ID',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '所属用户ID',
  `name` VARCHAR(30) NOT NULL COMMENT '标签名称',
  `color` VARCHAR(7) DEFAULT '#10B981' COMMENT '标签颜色（十六进制）',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  UNIQUE KEY `uk_user_name` (`user_id`, `name`),
  CONSTRAINT `fk_tags_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务标签表';

-- =====================================================
-- 任务管理模块
-- =====================================================

-- -----------------------------------------------------
-- 任务表
-- -----------------------------------------------------
CREATE TABLE `tasks` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '任务ID',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '所属用户ID',
  `category_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '所属分类ID',
  `title` VARCHAR(200) NOT NULL COMMENT '任务标题',
  `description` TEXT DEFAULT NULL COMMENT '任务描述',
  `status` TINYINT NOT NULL DEFAULT 0 COMMENT '状态：0-待完成，1-进行中，2-已完成，3-已取消',
  `priority` TINYINT NOT NULL DEFAULT 1 COMMENT '优先级：0-无，1-低，2-中，3-高，4-紧急',
  `due_date` DATE DEFAULT NULL COMMENT '截止日期',
  `due_time` TIME DEFAULT NULL COMMENT '截止时间',
  `reminder_at` DATETIME DEFAULT NULL COMMENT '提醒时间',
  `completed_at` DATETIME DEFAULT NULL COMMENT '完成时间',
  `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序顺序',
  `is_starred` TINYINT NOT NULL DEFAULT 0 COMMENT '是否星标：0-否，1-是',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_category_id` (`category_id`),
  KEY `idx_user_status` (`user_id`, `status`),
  KEY `idx_user_priority` (`user_id`, `priority`),
  KEY `idx_user_due_date` (`user_id`, `due_date`),
  KEY `idx_user_starred` (`user_id`, `is_starred`),
  KEY `idx_user_created` (`user_id`, `created_at`),
  -- 全文索引，支持搜索功能
  FULLTEXT KEY `ft_title_desc` (`title`, `description`) WITH PARSER ngram,
  CONSTRAINT `fk_tasks_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_tasks_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务表';

-- -----------------------------------------------------
-- 任务-标签关联表（多对多）
-- -----------------------------------------------------
CREATE TABLE `task_tags` (
  `task_id` BIGINT UNSIGNED NOT NULL COMMENT '任务ID',
  `tag_id` BIGINT UNSIGNED NOT NULL COMMENT '标签ID',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`task_id`, `tag_id`),
  KEY `idx_tag_id` (`tag_id`),
  CONSTRAINT `fk_task_tags_task` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_task_tags_tag` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务-标签关联表';

-- =====================================================
-- 搜索和过滤支持（视图）
-- =====================================================

-- -----------------------------------------------------
-- 任务详情视图（包含分类和标签信息，方便查询）
-- -----------------------------------------------------
CREATE OR REPLACE VIEW `v_task_details` AS
SELECT 
  t.id,
  t.user_id,
  t.title,
  t.description,
  t.status,
  t.priority,
  t.due_date,
  t.due_time,
  t.reminder_at,
  t.completed_at,
  t.is_starred,
  t.sort_order,
  t.created_at,
  t.updated_at,
  c.id AS category_id,
  c.name AS category_name,
  c.color AS category_color,
  c.icon AS category_icon,
  -- 聚合标签为JSON数组
  (
    SELECT JSON_ARRAYAGG(
      JSON_OBJECT(
        'id', tg.id,
        'name', tg.name,
        'color', tg.color
      )
    )
    FROM task_tags tt
    JOIN tags tg ON tt.tag_id = tg.id
    WHERE tt.task_id = t.id
  ) AS tags
FROM tasks t
LEFT JOIN categories c ON t.category_id = c.id;

-- =====================================================
-- 初始化数据
-- =====================================================

-- 插入测试用户
INSERT INTO `users` (`username`, `email`, `password_hash`) VALUES
('demo', 'demo@example.com', '$2a$10$placeholder_hash_for_demo_user');

-- 插入默认分类
INSERT INTO `categories` (`user_id`, `name`, `color`, `icon`, `sort_order`, `is_default`) VALUES
(1, '收集箱', '#6B7280', 'inbox', 0, 1),
(1, '工作', '#3B82F6', 'briefcase', 1, 0),
(1, '生活', '#10B981', 'home', 2, 0),
(1, '学习', '#8B5CF6', 'book', 3, 0);

-- 插入默认标签
INSERT INTO `tags` (`user_id`, `name`, `color`) VALUES
(1, '重要', '#EF4444'),
(1, '紧急', '#F97316'),
(1, '待讨论', '#EAB308'),
(1, '长期', '#6366F1');

-- 插入示例任务
INSERT INTO `tasks` (`user_id`, `category_id`, `title`, `description`, `status`, `priority`, `due_date`) VALUES
(1, 2, '完成项目方案设计', '包括技术选型、架构设计、数据库设计等内容', 1, 3, DATE_ADD(CURDATE(), INTERVAL 3 DAY)),
(1, 2, '准备周会汇报材料', NULL, 0, 2, DATE_ADD(CURDATE(), INTERVAL 1 DAY)),
(1, 3, '购买生活用品', '牛奶、面包、水果', 0, 1, CURDATE()),
(1, 4, '学习 TypeScript 进阶', '泛型、装饰器、高级类型', 0, 2, DATE_ADD(CURDATE(), INTERVAL 7 DAY));

-- 关联示例任务和标签
INSERT INTO `task_tags` (`task_id`, `tag_id`) VALUES
(1, 1),  -- 完成项目方案设计 - 重要
(1, 2),  -- 完成项目方案设计 - 紧急
(2, 2),  -- 准备周会汇报材料 - 紧急
(4, 4);  -- 学习 TypeScript 进阶 - 长期
