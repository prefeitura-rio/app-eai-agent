import { Badge } from '@/components/ui/badge';
import { cn } from '@/app/utils/utils';

interface StatusBadgeProps {
  status: 0 | 1;
  className?: string;
}

export default function StatusBadge({ status, className }: StatusBadgeProps) {
  if (status === 1) {
    return (
      <Badge variant="default" className={cn("bg-green-600 hover:bg-green-700", className)}>
        Publicado
      </Badge>
    );
  }

  return (
    <Badge variant="secondary" className={cn("bg-yellow-600 hover:bg-yellow-700 text-white", className)}>
      Rascunho
    </Badge>
  );
}
