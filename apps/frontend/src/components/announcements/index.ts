export { AnnouncementDialog } from './announcement-dialog';
export { announcementRegistry, registerAnnouncement } from './registry';
export type { AnnouncementComponentProps } from './registry';
export { useAnnouncementStore } from '@/stores/announcement-store';
export type { AnnouncementData } from '@/stores/announcement-store';

// Import and register announcement components
import { MemoriesAnnouncement } from './components/memories-announcement';
import { registerAnnouncement } from './registry';

// Register components in the announcement registry
registerAnnouncement('memories', MemoriesAnnouncement);

// Export for direct usage if needed
export { MemoriesAnnouncement };
