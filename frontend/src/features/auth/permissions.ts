import { Role } from '../../api/types/schemas';

// Conceptual permissions for the frontend
export const Permission = {
  VIEW_DASHBOARD: 'VIEW_DASHBOARD',
  VIEW_INSPECTION: 'VIEW_INSPECTION',
  VIEW_HISTORY: 'VIEW_HISTORY',
  VIEW_ANALYTICS: 'VIEW_ANALYTICS',
  MANAGE_USERS: 'MANAGE_USERS',
} as const;
export type Permission = (typeof Permission)[keyof typeof Permission];

const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  [Role.ADMIN]: [
    Permission.VIEW_DASHBOARD,
    Permission.VIEW_INSPECTION,
    Permission.VIEW_HISTORY,
    Permission.VIEW_ANALYTICS,
    Permission.MANAGE_USERS,
  ],
  [Role.ENGINEER]: [
    Permission.VIEW_DASHBOARD,
    Permission.VIEW_INSPECTION,
    Permission.VIEW_HISTORY,
    Permission.VIEW_ANALYTICS,
  ],
  [Role.OPERATOR]: [
    Permission.VIEW_DASHBOARD,
    Permission.VIEW_INSPECTION,
    Permission.VIEW_HISTORY,
  ],
  [Role.VIEWER]: [
    Permission.VIEW_DASHBOARD,
    Permission.VIEW_HISTORY,
  ],
};

export const hasPermission = (role: Role, permission: Permission): boolean => {
  return ROLE_PERMISSIONS[role]?.includes(permission) ?? false;
};
