export default function BerlinLoading() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
        <p className="text-muted-foreground">Loading Berlin page...</p>
        <p className="text-sm text-muted-foreground mt-2">This may take a moment</p>
      </div>
    </div>
  );
}
