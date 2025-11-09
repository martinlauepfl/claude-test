-- ============================================
-- 配额扣除原子操作函数
-- ============================================
-- 功能：安全地扣除用户配额，避免竞态条件
-- 使用：SELECT * FROM deduct_user_quota('user-id-here');
-- ============================================

CREATE OR REPLACE FUNCTION deduct_user_quota(user_id_param UUID)
RETURNS TABLE(
  success BOOLEAN,
  remaining_quota INTEGER,
  message TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER  -- 以函数拥有者权限运行，绕过RLS
AS $$
DECLARE
  current_quota INTEGER;
  new_quota INTEGER;
BEGIN
  -- 🔥 关键：使用 FOR UPDATE 锁定该行，防止并发修改
  -- 其他事务必须等待此事务完成才能访问这一行
  SELECT quota INTO current_quota
  FROM user_quotas
  WHERE user_id = user_id_param
  FOR UPDATE;

  -- 检查：配额记录是否存在
  IF current_quota IS NULL THEN
    RETURN QUERY SELECT
      FALSE::BOOLEAN,
      0::INTEGER,
      'Quota record not found'::TEXT;
    RETURN;
  END IF;

  -- 检查：配额是否足够
  IF current_quota <= 0 THEN
    RETURN QUERY SELECT
      FALSE::BOOLEAN,
      0::INTEGER,
      'Insufficient quota'::TEXT;
    RETURN;
  END IF;

  -- 扣除配额（原子操作）
  new_quota := current_quota - 1;

  UPDATE user_quotas
  SET
    quota = new_quota,
    updated_at = NOW()
  WHERE user_id = user_id_param;

  -- 返回成功结果
  RETURN QUERY SELECT
    TRUE::BOOLEAN,
    new_quota::INTEGER,
    'Quota deducted successfully'::TEXT;
END;
$$;

-- ============================================
-- 安全策略：允许认证用户调用此函数
-- ============================================
-- 注意：函数已设置 SECURITY DEFINER，
-- 但仍需要通过RLS确保用户只能扣除自己的配额

-- 授予使用权限（authenticated用户可以调用）
GRANT EXECUTE ON FUNCTION deduct_user_quota(UUID) TO authenticated;

-- ============================================
-- 测试示例（在Supabase SQL Editor中运行）
-- ============================================
-- 1. 查看当前配额
-- SELECT * FROM user_quotas WHERE user_id = 'your-user-id';

-- 2. 扣除配额
-- SELECT * FROM deduct_user_quota('your-user-id');

-- 3. 验证结果
-- SELECT * FROM user_quotas WHERE user_id = 'your-user-id';

-- ============================================
-- 如果需要删除此函数：
-- DROP FUNCTION IF EXISTS deduct_user_quota(UUID);
-- ============================================
