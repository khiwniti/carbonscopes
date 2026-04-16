/**
 * ╔══════════════════════════════════════════════════════════════════════╗
 * ║  CARBONSCOPE — Component Library Exports                            ║
 * ║  Dark Engineering Base + Emerald Green Accent                       ║
 * ║  EN 15978 Lifecycle-Aligned · Production-Ready                      ║
 * ╚══════════════════════════════════════════════════════════════════════╝
 */

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// DESIGN TOKENS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export { tokens, LIFECYCLE_STAGES } from '../tokens';
export type { Tokens, TokenKey, LifecycleStage } from '../tokens';

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// HOOKS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export { useInView } from './hooks/useInView';
export { useCountUp } from './hooks/useCountUp';

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// ATOMS (Base Components)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export { Badge } from './atoms/Badge';
export type { BadgeProps } from './atoms/Badge';

export { Button } from './atoms/Button';
export type { ButtonProps } from './atoms/Button';

export { Input } from './atoms/Input';
export type { InputProps } from './atoms/Input';

export { Divider } from './atoms/Divider';
export type { DividerProps } from './atoms/Divider';

export { Skeleton } from './atoms/Skeleton';
export type { SkeletonProps } from './atoms/Skeleton';

export { LifecycleStageTag } from './atoms/LifecycleStageTag';
export type { LifecycleStageTagProps } from './atoms/LifecycleStageTag';

export { SectionTitle } from './atoms/SectionTitle';
export type { SectionTitleProps } from './atoms/SectionTitle';

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// MOLECULES (Composite Components)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export { KPICard } from './molecules/KPICard';
export type { KPICardProps } from './molecules/KPICard';

export { LifecycleBarChart } from './molecules/LifecycleBarChart';
export type { LifecycleBarChartProps, LifecycleDataPoint } from './molecules/LifecycleBarChart';

export { EPDCard } from './molecules/EPDCard';
export type { EPDCardProps } from './molecules/EPDCard';

export { BenchmarkGauge } from './molecules/BenchmarkGauge';
export type { BenchmarkGaugeProps, BenchmarkBand } from './molecules/BenchmarkGauge';

export { MaterialComparisonRow } from './molecules/MaterialComparisonRow';
export type { MaterialComparisonRowProps, MaterialOption } from './molecules/MaterialComparisonRow';

export { ComplianceCard } from './molecules/ComplianceCard';
export type { ComplianceCardProps } from './molecules/ComplianceCard';

export { Tabs } from './molecules/Tabs';
export type { TabsProps, TabItem } from './molecules/Tabs';

export { AccordionItem } from './molecules/AccordionItem';
export type { AccordionItemProps } from './molecules/AccordionItem';

export { Toast } from './molecules/Toast';
export type { ToastProps } from './molecules/Toast';

export { StackedBarComparison } from './molecules/StackedBarComparison';
export type {
  StackedBarComparisonProps,
  ComparisonOption,
  ComparisonOptionData,
} from './molecules/StackedBarComparison';

export { ProjectSidebar } from './molecules/ProjectSidebar';
export type { ProjectSidebarProps } from './molecules/ProjectSidebar';
