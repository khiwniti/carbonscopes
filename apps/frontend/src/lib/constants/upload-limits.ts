/**
 * Re-export from shared package for backward compatibility
 * @deprecated Import from '@/lib/shared' instead
 */
export {
  UPLOAD_LIMITS,
  ALLOWED_MIME_TYPES,
  ALLOWED_EXTENSIONS,
  EXTRACTABLE_EXTENSIONS,
  formatFileSize,
  isAllowedFile,
  isExtractableArchive,
} from '@/lib/shared';
